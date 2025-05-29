import pytest
from unittest.mock import patch, MagicMock
from gitask.pmt.jira_pmt import JiraPmt, handle_jira_errors
from jira import JIRAError

@pytest.fixture(autouse=True)
def reset_jira_singleton():
    JiraPmt._instance = None
    yield
    JiraPmt._instance = None

def test_singleton(monkeypatch):
    with patch('gitask.pmt.jira_pmt.JIRA') as mock_jira:
        with patch('gitask.pmt.jira_pmt.Config') as mock_config:
            mock_config.return_value.pmt_url = 'url'
            mock_config.return_value.pmt_token = 'token'
            j1 = JiraPmt()
            j2 = JiraPmt()
            assert j1 is j2
            mock_jira.assert_called_once()

def test_update_ticket_status(monkeypatch):
    mock_jira_client = MagicMock()
    with patch('gitask.pmt.jira_pmt.JIRA', return_value=mock_jira_client):
        with patch('gitask.pmt.jira_pmt.Config') as mock_config:
            mock_config.return_value.pmt_url = 'url'
            mock_config.return_value.pmt_token = 'token'
            jira = JiraPmt()
            jira.update_ticket_status('ISSUE-1', 'In Progress')
            mock_jira_client.transition_issue.assert_called_once_with('ISSUE-1', 'In Progress')

def test_find_valid_status_transition(monkeypatch):
    mock_jira_client = MagicMock()
    mock_jira_client.transitions.return_value = [
        {'name': 'To Do'}, {'name': 'In Progress'}
    ]
    mock_jira_client.issue().fields.status.name = 'To Do'
    with patch('gitask.pmt.jira_pmt.JIRA', return_value=mock_jira_client):
        with patch('gitask.pmt.jira_pmt.Config') as mock_config:
            mock_config.return_value.pmt_url = 'url'
            mock_config.return_value.pmt_token = 'token'
            jira = JiraPmt()
            assert jira.find_valid_status_transition('ISSUE-1', ['In Progress']) == 'In Progress'
            # No valid transition
            mock_jira_client.transitions.return_value = []
            with pytest.raises(ValueError):
                jira.find_valid_status_transition('ISSUE-1', ['Done'])

def test_get_user_by_username(monkeypatch):
    mock_jira_client = MagicMock()
    with patch('gitask.pmt.jira_pmt.JIRA', return_value=mock_jira_client):
        with patch('gitask.pmt.jira_pmt.Config') as mock_config:
            mock_config.return_value.pmt_url = 'url'
            mock_config.return_value.pmt_token = 'token'
            jira = JiraPmt()
            with patch.object(jira, '_JiraPmt__jira_get_request', return_value=[{'name': 'user'}]):
                user = jira.get_user_by_username('user')
                assert user == {'name': 'user'}
            with patch.object(jira, '_JiraPmt__jira_get_request', return_value=[]):
                with pytest.raises(ValueError):
                    jira.get_user_by_username('user')

def test_update_git_branch(monkeypatch):
    mock_jira_client = MagicMock()
    with patch('gitask.pmt.jira_pmt.JIRA', return_value=mock_jira_client):
        with patch('gitask.pmt.jira_pmt.Config') as mock_config:
            mock_config.return_value.pmt_url = 'url'
            mock_config.return_value.pmt_token = 'token'
            jira = JiraPmt()
            with patch('gitask.pmt.jira_pmt.Utils.get_current_git_branch', return_value='branch'): 
                jira.update_git_branch('ISSUE-1', 'field')
                mock_jira_client.issue().update.assert_called_once()

def test_update_reviewer(monkeypatch):
    mock_jira_client = MagicMock()
    with patch('gitask.pmt.jira_pmt.JIRA', return_value=mock_jira_client):
        with patch('gitask.pmt.jira_pmt.Config') as mock_config:
            mock_config.return_value.pmt_url = 'url'
            mock_config.return_value.pmt_token = 'token'
            jira = JiraPmt()
            jira.update_reviewer('ISSUE-1', 'field', {'id': 1})
            mock_jira_client.issue().update.assert_called_once()

def test_jira_get_request(monkeypatch):
    mock_response = MagicMock()
    mock_response.json.return_value = {'result': 1}
    mock_response.raise_for_status.return_value = None
    with patch('gitask.pmt.jira_pmt.requests.get', return_value=mock_response) as mock_get:
        with patch('gitask.pmt.jira_pmt.JIRA'):
            with patch('gitask.pmt.jira_pmt.Config') as mock_config:
                mock_config.return_value.pmt_url = 'url'
                mock_config.return_value.pmt_token = 'token'
                jira = JiraPmt()
                jira.api_url = 'http://api'
                jira.token = 'tok'
                result = jira._JiraPmt__jira_get_request('resource', params={'a': 1})
                assert result == {'result': 1}
                mock_get.assert_called_once()

def test_handle_jira_errors_decorator():
    @handle_jira_errors
    def raise_jira_error():
        err = JIRAError("fail")
        err.response = type('obj', (), {'json': lambda: {'errorMessages': ['err'], 'errors': {}}})()
        err.text = 'fail'
        raise err
    with patch('sys.exit') as mock_exit:
        raise_jira_error()
        mock_exit.assert_called() 
