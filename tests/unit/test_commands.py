import pytest
from unittest.mock import patch, MagicMock

from gitask.commands import Commands, with_hooks
from gitask.pmt.pmt_factory import get_pmt


@pytest.fixture
def mock_config():
    with patch('gitask.commands.Config') as mock:
        config = MagicMock()
        config.to_do_statuses = ["To Do"]
        config.in_progress_statuses = ["In Progress"]
        config.in_review_statuses = ["In Review"]
        config.done_statuses = ["Done"]
        config.git_branch_field = "git_branch"
        config.reviewer_field = "reviewer"
        config.hooks = {}
        mock.return_value = config
        yield config


@pytest.fixture
def mock_utils():
    with patch('gitask.commands.Utils') as mock:
        utils = MagicMock()
        utils.get_current_ticket.return_value = "TEST-123"
        mock.return_value = utils
        yield utils


@pytest.fixture
def mock_pmt():
    with patch('gitask.commands.get_pmt') as mock:
        pmt = MagicMock()
        pmt.find_valid_status_transition.return_value = "To Do"
        pmt.get_user_by_username.return_value = {"id": "123", "name": "Test User"}
        mock.return_value = pmt
        yield pmt


@pytest.fixture
def mock_vcs():
    with patch('gitask.commands.get_vcs') as mock:
        vcs = MagicMock()
        mock.return_value = vcs
        yield vcs


@pytest.fixture
def commands_instance(mock_config, mock_utils, mock_pmt, mock_vcs):
    return Commands()


def test_configure_autocomplete():
    with patch('gitask.commands.setup_autocomplete') as mock_setup:
        Commands.configure(auto_complete=True)
        mock_setup.assert_called_once()


def test_configure_interactive():
    with patch('gitask.commands.interactive_setup') as mock_setup:
        Commands.configure(auto_complete=False)
        mock_setup.assert_called_once()


def test_move_to_to_do(commands_instance, mock_utils, mock_pmt):
    commands_instance.move_to_to_do()
    
    mock_utils.get_current_ticket.assert_called_once()
    mock_pmt.find_valid_status_transition.assert_called_once_with("TEST-123", ["To Do"])
    mock_pmt.update_ticket_status.assert_called_once_with("TEST-123", "To Do")


def test_move_to_in_progress(commands_instance, mock_utils, mock_pmt):
    commands_instance.move_to_in_progress()
    
    mock_utils.get_current_ticket.assert_called_once()
    mock_pmt.find_valid_status_transition.assert_called_once_with("TEST-123", ["In Progress"])
    mock_pmt.update_ticket_status.assert_called_once_with("TEST-123", "To Do")


def test_move_to_in_review(commands_instance, mock_utils, mock_pmt, mock_vcs):
    commands_instance.move_to_in_review("Test PR", "reviewer", "main", False)
    
    mock_utils.get_current_ticket.assert_called_once()
    mock_pmt.get_user_by_username.assert_called_once_with("reviewer")
    mock_pmt.update_git_branch.assert_called_once_with("TEST-123", "git_branch")
    mock_pmt.update_reviewer.assert_called_once_with("TEST-123", "reviewer", {"id": "123", "name": "Test User"})
    mock_pmt.find_valid_status_transition.assert_called_once_with("TEST-123", ["In Review"])
    mock_pmt.update_ticket_status.assert_called_once_with("TEST-123", "To Do")
    mock_utils.create_pull_request.assert_called_once_with(mock_vcs, "Test PR", "reviewer", target_branch="main")


def test_move_to_in_review_pr_only(commands_instance, mock_utils, mock_vcs):
    commands_instance.move_to_in_review("Test PR", "reviewer", "main", True)
    
    mock_utils.get_current_ticket.assert_not_called()
    mock_utils.create_pull_request.assert_called_once_with(mock_vcs, "Test PR", "reviewer", target_branch="main")


def test_move_to_done(commands_instance, mock_utils, mock_pmt):
    commands_instance.move_to_done()
    
    mock_utils.get_current_ticket.assert_called_once()
    mock_pmt.find_valid_status_transition.assert_called_once_with("TEST-123", ["Done"])
    mock_pmt.update_ticket_status.assert_called_once_with("TEST-123", "To Do")


def test_with_hooks_decorator():
    @with_hooks('test_action')
    def test_func(*args, **kwargs):
        return "test result"
    
    with patch('gitask.commands.Utils') as mock_utils, \
         patch('gitask.commands.Config') as mock_config:
        utils = MagicMock()
        config = MagicMock()
        config.hooks = {
            'test_action': {
                'pre': 'pre_script.sh',
                'post': 'post_script.sh'
            }
        }
        mock_utils.return_value = utils
        mock_config.return_value = config
        
        result = test_func('arg1', kwarg1='value1')
        
        assert result == "test result"
        assert utils.run_hook_script.call_count == 2
        utils.run_hook_script.assert_any_call('pre_script.sh', {'args': ['arg1'], 'kwarg1': 'value1'})
        utils.run_hook_script.assert_any_call('post_script.sh', {'args': ['arg1'], 'kwarg1': 'value1'}) 
