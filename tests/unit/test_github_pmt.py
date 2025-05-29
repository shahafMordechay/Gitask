from unittest.mock import patch, MagicMock

import pytest
from github import GithubException

from gitask.pmt.github_pmt import GitHubPmt


@patch('gitask.pmt.github_pmt.Github')
@patch('gitask.pmt.github_pmt.Config')
class TestGitHubPmt:
    def test_init(self, mock_config_class, mock_github_class):
        """Test GitHub client initialization."""
        mock_config = MagicMock()
        mock_config.pmt_token = 'test-token'
        mock_config.git_proj = 'test/repo'
        mock_config_class.return_value = mock_config
        pmt = GitHubPmt()
        mock_github_class.assert_called_once_with('test-token')
        mock_github_class.return_value.get_repo.assert_called_once_with('test/repo')

    def test_get_user_by_username_not_supported(self, mock_config_class, mock_github_class):
        """Test that get_user_by_username is not supported."""
        mock_config = MagicMock()
        mock_config.pmt_token = 'test-token'
        mock_config.git_proj = 'test/repo'
        mock_config_class.return_value = mock_config
        pmt = GitHubPmt()
        with pytest.raises(NotImplementedError, match="This action is not supported for GitHub"):
            pmt.get_user_by_username("testuser")

    def test_update_ticket_status(self, mock_config_class, mock_github_class):
        """Test updating issue state."""
        mock_config = MagicMock()
        mock_config.pmt_token = 'test-token'
        mock_config.git_proj = 'test/repo'
        mock_config_class.return_value = mock_config
        mock_issue = MagicMock()
        mock_github_class.return_value.get_repo.return_value.get_issue.return_value = mock_issue
        pmt = GitHubPmt()
        pmt.update_ticket_status("123", "closed")
        mock_github_class.return_value.get_repo.return_value.get_issue.assert_called_once_with(123)
        mock_issue.edit.assert_called_once_with(state="closed")

    def test_update_git_branch_not_supported(self, mock_config_class, mock_github_class):
        """Test that update_git_branch is not supported."""
        mock_config = MagicMock()
        mock_config.pmt_token = 'test-token'
        mock_config.git_proj = 'test/repo'
        mock_config_class.return_value = mock_config
        pmt = GitHubPmt()
        with pytest.raises(NotImplementedError, match="This action is not supported for GitHub"):
            pmt.update_git_branch("123", "branch_field")

    def test_update_reviewer_not_supported(self, mock_config_class, mock_github_class):
        """Test that update_reviewer is not supported."""
        mock_config = MagicMock()
        mock_config.pmt_token = 'test-token'
        mock_config.git_proj = 'test/repo'
        mock_config_class.return_value = mock_config
        pmt = GitHubPmt()
        with pytest.raises(NotImplementedError, match="This action is not supported for GitHub"):
            pmt.update_reviewer("123", "reviewer_field", {})

    def test_find_valid_status_transition_open_to_closed(self, mock_config_class, mock_github_class):
        """Test finding valid status transition from open to closed."""
        mock_config = MagicMock()
        mock_config.pmt_token = 'test-token'
        mock_config.git_proj = 'test/repo'
        mock_config_class.return_value = mock_config
        mock_issue = MagicMock()
        mock_issue.state = "open"
        mock_github_class.return_value.get_repo.return_value.get_issue.return_value = mock_issue
        pmt = GitHubPmt()
        status = pmt.find_valid_status_transition("123", ["closed"])
        assert status == "closed"
        mock_github_class.return_value.get_repo.return_value.get_issue.assert_called_once_with(123)

    def test_find_valid_status_transition_closed_to_open(self, mock_config_class, mock_github_class):
        """Test finding valid status transition from closed to open."""
        mock_config = MagicMock()
        mock_config.pmt_token = 'test-token'
        mock_config.git_proj = 'test/repo'
        mock_config_class.return_value = mock_config
        mock_issue = MagicMock()
        mock_issue.state = "closed"
        mock_github_class.return_value.get_repo.return_value.get_issue.return_value = mock_issue
        pmt = GitHubPmt()
        status = pmt.find_valid_status_transition("123", ["open"])
        assert status == "open"
        mock_github_class.return_value.get_repo.return_value.get_issue.assert_called_once_with(123)

    def test_find_valid_status_transition_invalid(self, mock_config_class, mock_github_class):
        """Test finding valid status transition when none are valid."""
        mock_config = MagicMock()
        mock_config.pmt_token = 'test-token'
        mock_config.git_proj = 'test/repo'
        mock_config_class.return_value = mock_config
        mock_issue = MagicMock()
        mock_issue.state = "open"
        mock_github_class.return_value.get_repo.return_value.get_issue.return_value = mock_issue
        pmt = GitHubPmt()
        with pytest.raises(ValueError, match="Invalid status transition from current status 'open' for issue '123'"):
            pmt.find_valid_status_transition("123", ["open"])

    def test_get_issue_status(self, mock_config_class, mock_github_class):
        """Test getting current issue state."""
        mock_config = MagicMock()
        mock_config.pmt_token = 'test-token'
        mock_config.git_proj = 'test/repo'
        mock_config_class.return_value = mock_config
        mock_issue = MagicMock()
        mock_issue.state = "open"
        mock_github_class.return_value.get_repo.return_value.get_issue.return_value = mock_issue
        pmt = GitHubPmt()
        status = pmt.get_issue_status("123")
        assert status == "open"
        mock_github_class.return_value.get_repo.return_value.get_issue.assert_called_once_with(123) 
