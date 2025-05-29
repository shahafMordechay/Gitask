from unittest.mock import patch, MagicMock

import pytest
from github import GithubException

from gitask.vcs.github_vcs import GithubVcs


@pytest.fixture(autouse=True)
def reset_githubvcs_singleton():
    GithubVcs._instance = None
    yield
    GithubVcs._instance = None

@patch('gitask.vcs.github_vcs.Github')
@patch('gitask.vcs.github_vcs.Config')
class TestGithubVcs:
    def test_singleton_pattern(self, mock_config_class, mock_github_class):
        """Test that GithubVcs follows the singleton pattern."""
        mock_config = MagicMock()
        mock_config.git_token = 'test-token'
        mock_config.git_proj = 'test/repo'
        mock_config_class.return_value = mock_config
        vcs1 = GithubVcs()
        vcs2 = GithubVcs()
        assert vcs1 is vcs2

    def test_init_github_client(self, mock_config_class, mock_github_class):
        """Test GitHub client initialization."""
        mock_config = MagicMock()
        mock_config.git_token = 'test-token'
        mock_config.git_proj = 'test/repo'
        mock_config_class.return_value = mock_config
        vcs = GithubVcs()
        mock_github_class.assert_called_once_with('test-token')
        mock_github_class.return_value.get_repo.assert_called_once_with('test/repo')

    def test_init_github_client_error(self, mock_config_class, mock_github_class):
        """Test handling of GitHub client initialization error."""
        mock_config = MagicMock()
        mock_config.git_token = 'test-token'
        mock_config.git_proj = 'test/repo'
        mock_config_class.return_value = mock_config
        mock_github_class.side_effect = GithubException(404, "Not found")
        with pytest.raises(SystemExit):
            GithubVcs()

    def test_get_user_by_name_exact_match(self, mock_config_class, mock_github_class):
        """Test getting user by name with exact match."""
        mock_config = MagicMock()
        mock_config.git_token = 'test-token'
        mock_config.git_proj = 'test/repo'
        mock_config_class.return_value = mock_config
        mock_user = MagicMock()
        mock_github_class.return_value.get_user.return_value = mock_user
        vcs = GithubVcs()
        user = vcs._GithubVcs__get_user_by_name("testuser")
        assert user == mock_user
        mock_github_class.return_value.get_user.assert_called_once_with("testuser")

    def test_get_user_by_name_not_found(self, mock_config_class, mock_github_class):
        """Test getting user by name when user is not found."""
        mock_config = MagicMock()
        mock_config.git_token = 'test-token'
        mock_config.git_proj = 'test/repo'
        mock_config_class.return_value = mock_config
        mock_github_class.return_value.get_user.side_effect = GithubException(404, "Not found")
        vcs = GithubVcs()
        with pytest.raises(ValueError, match="No GitHub user found matching 'testuser'"):
            vcs._GithubVcs__get_user_by_name("testuser")

    def test_get_user_by_name_error(self, mock_config_class, mock_github_class):
        """Test handling of error when getting user by name."""
        mock_config = MagicMock()
        mock_config.git_token = 'test-token'
        mock_config.git_proj = 'test/repo'
        mock_config_class.return_value = mock_config
        mock_github_class.return_value.get_user.side_effect = GithubException(500, "Server error")
        vcs = GithubVcs()
        with pytest.raises(ValueError, match="Failed to get user by name: testuser"):
            vcs._GithubVcs__get_user_by_name("testuser")

    def test_get_current_user(self, mock_config_class, mock_github_class):
        """Test getting current user."""
        mock_config = MagicMock()
        mock_config.git_token = 'test-token'
        mock_config.git_proj = 'test/repo'
        mock_config_class.return_value = mock_config
        mock_user = MagicMock()
        mock_github_class.return_value.get_user.return_value = mock_user
        vcs = GithubVcs()
        user = vcs._GithubVcs__get_current_user()
        assert user == mock_user
        mock_github_class.return_value.get_user.assert_called_once()

    def test_create_pull_request(self, mock_config_class, mock_github_class):
        """Test creating a pull request."""
        mock_config = MagicMock()
        mock_config.git_token = 'test-token'
        mock_config.git_proj = 'test-repo'
        mock_config_class.return_value = mock_config
        mock_pr = MagicMock()
        mock_pr.html_url = "https://github.com/test/repo/pull/123"
        mock_github_class.return_value.get_repo.return_value.create_pull.return_value = mock_pr
        mock_pulls = MagicMock()
        mock_pulls.totalCount = 0
        mock_github_class.return_value.get_repo.return_value.get_pulls.return_value = mock_pulls
        vcs = GithubVcs()
        pr_link = vcs.create_pull_request(
            source_branch="feature/test",
            target_branch="main",
            title="Test PR",
            reviewer="testuser"
        )
        assert pr_link == "https://github.com/test/repo/pull/123"
        mock_github_class.return_value.get_repo.return_value.create_pull.assert_called_once_with(
            title="Test PR",
            head="feature/test",
            base="main"
        )

    def test_create_pull_request_error(self, mock_config_class, mock_github_class):
        """Test handling of error when creating pull request."""
        mock_config = MagicMock()
        mock_config.git_token = 'test-token'
        mock_config.git_proj = 'test-repo'
        mock_config_class.return_value = mock_config
        mock_github_class.return_value.get_repo.return_value.create_pull.side_effect = GithubException(400, "Bad request")
        mock_pulls = MagicMock()
        mock_pulls.totalCount = 0
        mock_github_class.return_value.get_repo.return_value.get_pulls.return_value = mock_pulls
        vcs = GithubVcs()
        with pytest.raises(SystemExit):
            vcs.create_pull_request(
                source_branch="feature/test",
                target_branch="main",
                title="Test PR",
                reviewer="testuser"
            ) 
