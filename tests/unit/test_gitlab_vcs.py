from unittest.mock import patch, MagicMock

import pytest
import gitlab
from gitlab.exceptions import GitlabError

from gitask.vcs.gitlab_vcs import GitlabVcs


@pytest.fixture(autouse=True)
def reset_gitlabvcs_singleton():
    GitlabVcs._instance = None
    yield
    GitlabVcs._instance = None


@patch('gitask.vcs.gitlab_vcs.gitlab.Gitlab')
@patch('gitask.vcs.gitlab_vcs.Config')
class TestGitlabVcs:
    def test_init_gitlab_client(self, mock_config_class, mock_gitlab_class):
        """Test GitLab client initialization."""
        mock_config = MagicMock()
        mock_config.git_token = 'test-token'
        mock_config.git_url = 'https://test-gitlab.com'
        mock_config.git_proj = 'test/repo'
        mock_config_class.return_value = mock_config
        
        mock_gitlab = MagicMock()
        mock_gitlab.auth.return_value = None
        mock_gitlab.projects.get.return_value = MagicMock()
        mock_gitlab.user.id = 123
        mock_gitlab_class.return_value = mock_gitlab
        
        vcs = GitlabVcs()
        mock_gitlab_class.assert_called_once_with(
            mock_config.git_url,
            private_token=mock_config.git_token
        )
        mock_gitlab.auth.assert_called_once()
        mock_gitlab.projects.get.assert_called_once_with(mock_config.git_proj)

    def test_init_gitlab_client_error(self, mock_config_class, mock_gitlab_class):
        """Test handling of GitLab client initialization error."""
        mock_config = MagicMock()
        mock_config.git_token = 'test-token'
        mock_config.git_url = 'https://test-gitlab.com'
        mock_config.git_proj = 'test/repo'
        mock_config_class.return_value = mock_config
        
        mock_gitlab_class.side_effect = GitlabError("Connection failed")
        with pytest.raises(SystemExit):
            GitlabVcs()

    def test_get_user_id_by_name(self, mock_config_class, mock_gitlab_class):
        """Test getting user ID by name."""
        mock_config = MagicMock()
        mock_config.git_token = 'test-token'
        mock_config.git_url = 'https://test-gitlab.com'
        mock_config.git_proj = 'test/repo'
        mock_config_class.return_value = mock_config
        
        mock_gitlab = MagicMock()
        mock_gitlab.user.id = 123
        mock_gitlab.users.list.return_value = [MagicMock(id=123)]
        mock_gitlab_class.return_value = mock_gitlab
        
        vcs = GitlabVcs()
        user_id = vcs._GitlabVcs__get_user_id_by_name("testuser")
        assert user_id == 123
        mock_gitlab.users.list.assert_called_once_with(search="testuser")

    def test_get_user_id_by_name_not_found(self, mock_config_class, mock_gitlab_class):
        """Test getting user ID when user is not found."""
        mock_config = MagicMock()
        mock_config.git_token = 'test-token'
        mock_config.git_url = 'https://test-gitlab.com'
        mock_config.git_proj = 'test/repo'
        mock_config_class.return_value = mock_config
        
        mock_gitlab = MagicMock()
        mock_gitlab.user.id = 123
        mock_gitlab.users.list.return_value = []
        mock_gitlab_class.return_value = mock_gitlab
        
        vcs = GitlabVcs()
        with pytest.raises(ValueError, match="User with name 'testuser' not found."):
            vcs._GitlabVcs__get_user_id_by_name("testuser")

    def test_get_current_user_id(self, mock_config_class, mock_gitlab_class):
        """Test getting current user ID."""
        mock_config = MagicMock()
        mock_config.git_token = 'test-token'
        mock_config.git_url = 'https://test-gitlab.com'
        mock_config.git_proj = 'test/repo'
        mock_config_class.return_value = mock_config
        
        mock_gitlab = MagicMock()
        mock_gitlab.user.id = 123
        mock_gitlab_class.return_value = mock_gitlab
        
        vcs = GitlabVcs()
        user_id = vcs._GitlabVcs__get_current_user_id()
        assert user_id == 123

    def test_create_pull_request(self, mock_config_class, mock_gitlab_class):
        """Test creating a merge request."""
        mock_config = MagicMock()
        mock_config.git_token = 'test-token'
        mock_config.git_url = 'https://test-gitlab.com'
        mock_config.git_proj = 'test/repo'
        mock_config_class.return_value = mock_config
        
        mock_gitlab = MagicMock()
        mock_gitlab.user.id = 123
        mock_gitlab.users.list.return_value = [MagicMock(id=123)]
        mock_project = MagicMock()
        mock_mr = MagicMock()
        mock_mr.web_url = "https://gitlab.com/test/repo/merge_requests/123"
        mock_project.mergerequests.create.return_value = mock_mr
        mock_gitlab.projects.get.return_value = mock_project
        mock_gitlab_class.return_value = mock_gitlab
        
        vcs = GitlabVcs()
        mr_link = vcs.create_pull_request(
            source_branch="feature/test",
            target_branch="main",
            title="Test MR",
            reviewer="testuser"
        )
        assert mr_link == "https://gitlab.com/test/repo/merge_requests/123"
        mock_project.mergerequests.create.assert_called_once()

    def test_create_pull_request_error(self, mock_config_class, mock_gitlab_class):
        """Test handling of error when creating merge request."""
        mock_config = MagicMock()
        mock_config.git_token = 'test-token'
        mock_config.git_url = 'https://test-gitlab.com'
        mock_config.git_proj = 'test/repo'
        mock_config_class.return_value = mock_config
        
        mock_gitlab = MagicMock()
        mock_gitlab.user.id = 123
        mock_gitlab.users.list.return_value = [MagicMock(id=123)]
        mock_project = MagicMock()
        mock_project.mergerequests.create.side_effect = GitlabError("Failed to create MR")
        mock_gitlab.projects.get.return_value = mock_project
        mock_gitlab_class.return_value = mock_gitlab
        
        vcs = GitlabVcs()
        with pytest.raises(SystemExit):
            vcs.create_pull_request(
                source_branch="feature/test",
                target_branch="main",
                title="Test MR",
                reviewer="testuser"
            )
