from unittest.mock import patch, MagicMock

import pytest
from jira import JIRA, JIRAError

from gitask.pmt.jira_pmt import JiraPmt


@pytest.fixture(autouse=True)
def reset_jirapmt_singleton():
    JiraPmt._instance = None
    yield
    JiraPmt._instance = None


@pytest.fixture
def mock_config():
    with patch('gitask.pmt.jira_pmt.Config') as mock:
        config_instance = MagicMock()
        config_instance.pmt_url = 'https://test-jira.com'
        config_instance.pmt_token = 'test-token'
        mock.return_value = config_instance
        yield config_instance


@pytest.fixture
def mock_jira_client():
    with patch('gitask.pmt.jira_pmt.JIRA') as mock:
        client = MagicMock()
        mock.return_value = client
        yield client


class TestJiraPmt:
    @patch('gitask.pmt.jira_pmt.JIRA')
    def test_singleton_pattern(self, mock_jira_class, mock_config):
        """Test that JiraPmt follows the singleton pattern."""
        pmt1 = JiraPmt()
        pmt2 = JiraPmt()
        assert pmt1 is pmt2

    @patch('gitask.pmt.jira_pmt.JIRA')
    def test_init_jira_client(self, mock_jira_class, mock_config):
        """Test JIRA client initialization."""
        pmt = JiraPmt()
        mock_jira_class.assert_called_once_with(
            server=mock_config.pmt_url,
            token_auth=mock_config.pmt_token
        )
        assert pmt.api_url == f"{mock_config.pmt_url}/rest/api/2"
        assert pmt.token == mock_config.pmt_token

    @patch('gitask.pmt.jira_pmt.JIRA', side_effect=JIRAError("Connection failed"))
    def test_init_jira_client_error(self, mock_jira_class, mock_config):
        """Test handling of JIRA client initialization error."""
        with pytest.raises(SystemExit):
            JiraPmt()

    def test_update_ticket_status(self, mock_jira_client):
        """Test updating ticket status."""
        pmt = JiraPmt()
        pmt.update_ticket_status("TEST-123", "In Progress")
        mock_jira_client.transition_issue.assert_called_once_with("TEST-123", "In Progress")

    def test_update_ticket_status_error(self, mock_jira_client):
        """Test handling of ticket status update error."""
        mock_jira_client.transition_issue.side_effect = JIRAError("Invalid transition")
        pmt = JiraPmt()
        with pytest.raises(SystemExit):
            pmt.update_ticket_status("TEST-123", "Invalid Status")

    def test_find_valid_status_transition(self, mock_jira_client):
        """Test finding valid status transition."""
        mock_jira_client.transitions.return_value = [
            {"name": "To Do"},
            {"name": "In Progress"},
            {"name": "Done"}
        ]
        pmt = JiraPmt()
        status = pmt.find_valid_status_transition("TEST-123", ["In Progress", "Done"])
        assert status == "In Progress"
        mock_jira_client.transitions.assert_called_once_with("TEST-123")

    def test_find_valid_status_transition_no_valid(self, mock_jira_client):
        """Test finding valid status transition when none are valid."""
        mock_jira_client.transitions.return_value = [
            {"name": "To Do"},
            {"name": "In Progress"}
        ]
        mock_jira_client.issue.return_value.fields.status.name = "In Progress"
        pmt = JiraPmt()
        with pytest.raises(ValueError, match="Invalid status transition from current status 'In Progress' for issue 'TEST-123'"):
            pmt.find_valid_status_transition("TEST-123", ["Done"])

    def test_find_valid_status_transition_error(self, mock_jira_client):
        """Test handling of error when finding valid status transition."""
        mock_jira_client.transitions.side_effect = JIRAError("Failed to get transitions")
        pmt = JiraPmt()
        with pytest.raises(SystemExit):
            pmt.find_valid_status_transition("TEST-123", ["In Progress"])

    @patch('gitask.pmt.jira_pmt.JIRA')
    @patch('requests.get')
    def test_get_user_by_username(self, mock_requests_get, mock_jira_class, mock_config):
        mock_response = MagicMock()
        mock_response.json.return_value = [{"displayName": "Test User", "emailAddress": "test@example.com"}]
        mock_response.raise_for_status.return_value = None
        mock_requests_get.return_value = mock_response
        pmt = JiraPmt()
        user = pmt.get_user_by_username("testuser")
        assert user["displayName"] == "Test User"
        assert user["emailAddress"] == "test@example.com"

    @patch('gitask.pmt.jira_pmt.JIRA')
    @patch('requests.get')
    def test_get_user_by_username_not_found(self, mock_requests_get, mock_jira_class, mock_config):
        mock_response = MagicMock()
        mock_response.json.return_value = []
        mock_response.raise_for_status.return_value = None
        mock_requests_get.return_value = mock_response
        pmt = JiraPmt()
        with pytest.raises(ValueError, match="User 'testuser' not found"):
            pmt.get_user_by_username("testuser")

    @patch('gitask.pmt.jira_pmt.JIRA')
    @patch('gitask.pmt.jira_pmt.Utils.get_current_git_branch', return_value='feature/test')
    def test_update_git_branch(self, mock_get_branch, mock_jira_class, mock_config):
        pmt = JiraPmt()
        pmt.update_git_branch("TEST-123", "customfield_12345")
        mock_jira_class.return_value.issue.assert_called_once_with("TEST-123")
        mock_jira_class.return_value.issue.return_value.update.assert_called_once_with(
            fields={"customfield_12345": "feature/test"}
        )

    def test_update_reviewer(self, mock_jira_client):
        """Test updating reviewer field."""
        pmt = JiraPmt()
        user = {"displayName": "Test User", "emailAddress": "test@example.com"}
        pmt.update_reviewer("TEST-123", "customfield_12345", user)
        mock_jira_client.issue.assert_called_once_with("TEST-123")
        mock_jira_client.issue.return_value.update.assert_called_once_with(
            fields={"customfield_12345": user}
        ) 
