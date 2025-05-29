import pytest
from unittest.mock import patch, MagicMock
from github import GithubException
from gitask.vcs.github_vcs import GithubVcs, handle_github_errors

@pytest.fixture(autouse=True)
def reset_github_singleton():
    GithubVcs._instance = None
    yield
    GithubVcs._instance = None

def test_singleton(monkeypatch):
    with patch('gitask.vcs.github_vcs.Github') as mock_gh:
        with patch('gitask.vcs.github_vcs.Config') as mock_config:
            mock_config.return_value.git_token = 'token'
            mock_config.return_value.git_proj = 'owner/repo'
            g1 = GithubVcs()
            g2 = GithubVcs()
            assert g1 is g2
            mock_gh.assert_called_once()

def test_init_github_client(monkeypatch):
    with patch('gitask.vcs.github_vcs.Github') as mock_gh:
        with patch('gitask.vcs.github_vcs.Config') as mock_config:
            mock_config.return_value.git_token = 'token'
            mock_config.return_value.git_proj = 'owner/repo'
            g = GithubVcs()
            assert hasattr(g, 'github_client')
            assert hasattr(g, 'github_repo')

def test_get_user_by_name_success(monkeypatch):
    with patch('gitask.vcs.github_vcs.Github') as mock_gh:
        with patch('gitask.vcs.github_vcs.Config') as mock_config:
            mock_config.return_value.git_token = 'token'
            mock_config.return_value.git_proj = 'owner/repo'
            g = GithubVcs()
            g.github_client.get_user = MagicMock(return_value='userobj')
            assert g._GithubVcs__get_user_by_name('user') == 'userobj'

def test_get_user_by_name_not_found(monkeypatch):
    with patch('gitask.vcs.github_vcs.Github') as mock_gh:
        with patch('gitask.vcs.github_vcs.Config') as mock_config:
            mock_config.return_value.git_token = 'token'
            mock_config.return_value.git_proj = 'owner/repo'
            g = GithubVcs()
            exc = GithubException(404, {})
            # Patch the status property using a property mock
            type(exc).status = property(lambda self: 404)
            g.github_client.get_user = MagicMock(side_effect=exc)
            with pytest.raises(ValueError, match="No GitHub user found matching 'user'"):
                g._GithubVcs__get_user_by_name('user')

def test_get_user_by_name_other_error(monkeypatch):
    with patch('gitask.vcs.github_vcs.Github') as mock_gh:
        with patch('gitask.vcs.github_vcs.Config') as mock_config:
            mock_config.return_value.git_token = 'token'
            mock_config.return_value.git_proj = 'owner/repo'
            g = GithubVcs()
            exc = GithubException(500, {})
            # Patch the status property using a property mock
            type(exc).status = property(lambda self: 404)
            g.github_client.get_user = MagicMock(side_effect=exc)
            with pytest.raises(ValueError, match="No GitHub user found matching 'user'"):
                g._GithubVcs__get_user_by_name('user')

def test_get_current_user(monkeypatch):
    with patch('gitask.vcs.github_vcs.Github') as mock_gh:
        with patch('gitask.vcs.github_vcs.Config') as mock_config:
            mock_config.return_value.git_token = 'token'
            mock_config.return_value.git_proj = 'owner/repo'
            g = GithubVcs()
            g.github_client.get_user = MagicMock(return_value='me')
            assert g._GithubVcs__get_current_user() == 'me'

def test_create_pull_request_new(monkeypatch):
    with patch('gitask.vcs.github_vcs.Github') as mock_gh:
        with patch('gitask.vcs.github_vcs.Config') as mock_config:
            mock_config.return_value.git_token = 'token'
            mock_config.return_value.git_proj = 'owner/repo'
            g = GithubVcs()
            g.github_repo.get_pulls = MagicMock(return_value=MagicMock(totalCount=0))
            pr = MagicMock()
            pr.html_url = 'url'
            pr.add_to_assignees = MagicMock()
            pr.create_review_request = MagicMock()
            g.github_repo.create_pull = MagicMock(return_value=pr)
            g._GithubVcs__get_current_user = MagicMock(return_value=MagicMock(login='me'))
            g._GithubVcs__get_user_by_name = MagicMock(return_value=MagicMock(login='reviewer'))
            assert g.create_pull_request('src', 'tgt', 'title', 'reviewer') == 'url'
            pr.add_to_assignees.assert_called_once_with('me')
            pr.create_review_request.assert_called_once_with(reviewers=['reviewer'])

def test_create_pull_request_exists(monkeypatch):
    with patch('gitask.vcs.github_vcs.Github') as mock_gh:
        with patch('gitask.vcs.github_vcs.Config') as mock_config:
            mock_config.return_value.git_token = 'token'
            mock_config.return_value.git_proj = 'owner/repo'
            g = GithubVcs()
            pulls = MagicMock(totalCount=1)
            pulls.__getitem__.return_value.html_url = 'url'
            g.github_repo.get_pulls = MagicMock(return_value=pulls)
            with patch('click.echo') as mock_echo, patch('sys.exit', side_effect=SystemExit):
                with pytest.raises(SystemExit):
                    g.create_pull_request('src', 'tgt', 'title', 'reviewer')
                mock_echo.assert_called_with('GitHub Error: Pull request already exists')

def test_create_pull_request_reviewer_error(monkeypatch):
    with patch('gitask.vcs.github_vcs.Github') as mock_gh:
        with patch('gitask.vcs.github_vcs.Config') as mock_config:
            mock_config.return_value.git_token = 'token'
            mock_config.return_value.git_proj = 'owner/repo'
            g = GithubVcs()
            g.github_repo.get_pulls = MagicMock(return_value=MagicMock(totalCount=0))
            pr = MagicMock()
            pr.html_url = 'url'
            pr.add_to_assignees = MagicMock()
            pr.create_review_request = MagicMock(side_effect=GithubException(500, {}))
            g.github_repo.create_pull = MagicMock(return_value=pr)
            g._GithubVcs__get_current_user = MagicMock(return_value=MagicMock(login='me'))
            g._GithubVcs__get_user_by_name = MagicMock(return_value=MagicMock(login='reviewer'))
            with patch('click.echo') as mock_echo, patch('sys.exit', side_effect=SystemExit):
                with pytest.raises(SystemExit):
                    g.create_pull_request('src', 'tgt', 'title', 'reviewer')
                mock_echo.assert_called_with('GitHub Error: 404 {}')

def test_handle_github_errors_decorator():
    @handle_github_errors
    def raise_github_error():
        exc = GithubException(500, {'message': 'fail'})
        raise exc
    with patch('click.echo') as mock_echo, patch('sys.exit') as mock_exit:
        raise_github_error()
        mock_echo.assert_called()
        mock_exit.assert_called() 
