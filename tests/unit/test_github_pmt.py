import pytest
from unittest.mock import patch, MagicMock
from gitask.pmt.github_pmt import GitHubPmt

@pytest.fixture
def mock_config():
    with patch('gitask.pmt.github_pmt.Config') as mock:
        config = MagicMock()
        config.pmt_token = 'token'
        config.git_proj = 'owner/repo'
        mock.return_value = config
        yield config

@pytest.fixture
def mock_github():
    with patch('gitask.pmt.github_pmt.Github') as mock:
        mock_issue = MagicMock()
        mock_issue.state = 'open'
        mock_repo = MagicMock()
        mock_repo.get_issue.return_value = mock_issue
        mock_github = MagicMock()
        mock_github.get_repo.return_value = mock_repo
        mock.return_value = mock_github
        yield mock_github, mock_repo, mock_issue

def test_not_supported_methods(mock_config, mock_github):
    pmt = GitHubPmt()
    with pytest.raises(NotImplementedError, match="This action is not supported for GitHub"):
        pmt.get_user_by_username('user')
    
    # These methods should return None without raising an error
    assert pmt.update_git_branch('1', 'field') is None
    assert pmt.update_reviewer('1', 'field', {'id': 1}) is None

def test_update_ticket_status(mock_config, mock_github):
    mock_github, mock_repo, mock_issue = mock_github
    pmt = GitHubPmt()
    pmt.update_ticket_status('1', 'closed')
    mock_repo.get_issue.assert_called_once_with(1)
    mock_issue.edit.assert_called_once_with(state='closed')

def test_find_valid_status_transition_closed(mock_config, mock_github):
    mock_github, mock_repo, mock_issue = mock_github
    pmt = GitHubPmt()
    mock_issue.state = 'open'
    assert pmt.find_valid_status_transition('1', ['closed']) == 'closed'

def test_find_valid_status_transition_open(mock_config, mock_github):
    mock_github, mock_repo, mock_issue = mock_github
    pmt = GitHubPmt()
    mock_issue.state = 'closed'
    assert pmt.find_valid_status_transition('1', ['open']) == 'open'

def test_find_valid_status_transition_invalid(mock_config, mock_github):
    mock_github, mock_repo, mock_issue = mock_github
    pmt = GitHubPmt()
    mock_issue.state = 'open'
    with pytest.raises(ValueError, match="Invalid status transition from current status 'open' for issue '1'"):
        pmt.find_valid_status_transition('1', ['open'])

def test_get_issue_status(mock_config, mock_github):
    mock_github, mock_repo, mock_issue = mock_github
    pmt = GitHubPmt()
    mock_issue.state = 'closed'
    assert pmt.get_issue_status('1') == 'closed' 
