import pytest
from unittest.mock import MagicMock, patch, PropertyMock
import gitlab
import json
import click
import os

from gitask.vcs.gitlab_vcs import GitlabVcs, handle_gitlab_errors
from gitask.config.config import Config

REQUIRED_CONFIG = {
    'git_url': 'https://gitlab.com',
    'git_token': 'test_token',
    'git_proj': 'test/project',
    'pmt-type': 'jira',
    'vcs-type': 'gitlab',
    'git-project': 'test/project',
    'current-ticket': 'TICKET-1',
    'to-do': 'To Do',
    'done': 'Done',
}

@pytest.fixture(autouse=True)
def patch_config_and_reset_singleton():
    Config._instance = None
    GitlabVcs._instance = None
    with patch.object(Config, '_Config__load_config', return_value=None):
        # Create the singleton instance and set required fields
        config = Config()
        config.config_data = REQUIRED_CONFIG.copy()
        yield

@pytest.fixture(autouse=True)
def mock_gitlab_client():
    with patch('gitask.vcs.gitlab_vcs.gitlab.Gitlab') as mock:
        client = MagicMock()
        mock.return_value = client
        yield client

@pytest.fixture
def mock_gitlab_project(mock_gitlab_client):
    project = MagicMock()
    mock_gitlab_client.projects.get.return_value = project
    return project

def test_handle_gitlab_errors_decorator():
    @handle_gitlab_errors
    def test_func():
        raise gitlab.exceptions.GitlabError("Test error")

    with pytest.raises(SystemExit):
        test_func()


def test_handle_gitlab_errors_with_list_error_message():
    @handle_gitlab_errors
    def test_func():
        error = gitlab.exceptions.GitlabError("Test error")
        error.error_message = ["Single error message"]
        raise error

    with pytest.raises(SystemExit):
        test_func()


def test_gitlab_vcs_singleton():
    vcs1 = GitlabVcs()
    vcs2 = GitlabVcs()
    assert vcs1 is vcs2


def test_init_gitlab_client(mock_gitlab_client, mock_gitlab_project):
    vcs = GitlabVcs()
    mock_gitlab_client.auth.assert_called_once()
    mock_gitlab_client.projects.get.assert_called_once_with('test/project')


def test_get_user_id_by_name(mock_gitlab_client):
    vcs = GitlabVcs()
    mock_user = MagicMock()
    mock_user.id = 123
    mock_gitlab_client.users.list.return_value = [mock_user]
    
    user_id = vcs._GitlabVcs__get_user_id_by_name("test_user")
    assert user_id == 123
    mock_gitlab_client.users.list.assert_called_once_with(search="test_user")


def test_get_user_id_by_name_not_found(mock_gitlab_client):
    vcs = GitlabVcs()
    mock_gitlab_client.users.list.return_value = []
    
    with pytest.raises(ValueError, match="User with name 'test_user' not found"):
        vcs._GitlabVcs__get_user_id_by_name("test_user")


def test_get_current_user_id(mock_gitlab_client):
    vcs = GitlabVcs()
    mock_gitlab_client.user.id = 456
    
    user_id = vcs._GitlabVcs__get_current_user_id()
    assert user_id == 456


def test_create_pull_request_success(mock_gitlab_client, mock_gitlab_project):
    vcs = GitlabVcs()
    mock_gitlab_client.user.id = 456
    mock_user = MagicMock()
    mock_user.id = 123
    mock_gitlab_client.users.list.return_value = [mock_user]
    
    mock_mr = MagicMock()
    mock_mr.web_url = "https://gitlab.com/test/project/-/merge_requests/1"
    mock_gitlab_project.mergerequests.create.return_value = mock_mr
    
    mr_url = vcs.create_pull_request(
        source_branch="feature",
        target_branch="main",
        title="Test MR",
        reviewer="test_user"
    )
    
    assert mr_url == "https://gitlab.com/test/project/-/merge_requests/1"
    mock_gitlab_project.mergerequests.create.assert_called_once_with({
        'source_branch': 'feature',
        'target_branch': 'main',
        'title': 'Test MR',
        'reviewer_ids': [123],
        'assignee_id': 456
    })


def test_create_pull_request_existing_mr(mock_gitlab_project):
    vcs = GitlabVcs()
    vcs.gitlab_client.user.id = 456
    mock_user = MagicMock()
    mock_user.id = 123
    vcs.gitlab_client.users.list.return_value = [mock_user]
    
    # Mock existing MR
    mock_existing_mr = MagicMock()
    mock_existing_mr.web_url = "https://gitlab.com/test/project/-/merge_requests/1"
    mock_gitlab_project.mergerequests.list.return_value = [mock_existing_mr]
    
    # Make create() raise an error
    mock_gitlab_project.mergerequests.create.side_effect = gitlab.exceptions.GitlabError("MR already exists")
    
    with pytest.raises(SystemExit):
        vcs.create_pull_request(
            source_branch="feature",
            target_branch="main",
            title="Test MR",
            reviewer="test_user"
        )
    
    mock_gitlab_project.mergerequests.list.assert_called_once_with(
        source_branch="feature",
        state="opened"
    ) 
