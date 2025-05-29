import os
import pytest
from unittest.mock import patch, mock_open, MagicMock
import click

from gitask.config.config_utils import (
    interactive_setup,
    setup_autocomplete,
    _set_env_variables,
    _get_shell_type,
    GITASK_ENV_PATH,
    SHELL_CONFIG_FILES
)

@pytest.fixture
def mock_click_prompt():
    with patch('click.prompt') as mock_prompt:
        yield mock_prompt

@pytest.fixture
def mock_click_echo():
    with patch('click.echo') as mock_echo:
        yield mock_echo

@pytest.fixture
def mock_click_confirm():
    with patch('click.confirm') as mock_confirm:
        yield mock_confirm

@pytest.fixture
def mock_os_makedirs():
    with patch('os.makedirs') as mock_makedirs:
        yield mock_makedirs

@pytest.fixture
def mock_save_json():
    with patch('gitask.config.config_utils.save_json_to_file') as mock_save:
        yield mock_save

def test_get_shell_type():
    # Test bash
    with patch.dict(os.environ, {'SHELL': '/bin/bash'}):
        assert _get_shell_type() == 'bash'
    
    # Test zsh
    with patch.dict(os.environ, {'SHELL': '/bin/zsh'}):
        assert _get_shell_type() == 'zsh'
    
    # Test fish
    with patch.dict(os.environ, {'SHELL': '/usr/bin/fish'}):
        assert _get_shell_type() == 'fish'
    
    # Test unknown shell
    with patch.dict(os.environ, {'SHELL': '/bin/unknown'}):
        with pytest.raises(SystemExit):
            _get_shell_type()

def test_set_env_variables(mock_os_makedirs):
    env_vars = {
        'TEST_VAR1': 'value1',
        'TEST_VAR2': 'value2'
    }
    
    # Mock file operations
    mock_env_file = mock_open()
    mock_shell_file = mock_open(read_data='')
    
    with patch('builtins.open', mock_env_file) as mock_file, \
         patch('os.path.expanduser', return_value='/test/path'), \
         patch('gitask.config.config_utils._get_shell_type', return_value='bash'):
        _set_env_variables(env_vars)
        
        # Check if makedirs was called
        mock_os_makedirs.assert_called_once()
        
        # Check if env file was written correctly
        mock_file.assert_any_call('/test/path', 'w')
        write_calls = mock_file().write.call_args_list
        assert any('export TEST_VAR1="value1"' in str(call) for call in write_calls)
        assert any('export TEST_VAR2="value2"' in str(call) for call in write_calls)
        
        # Check if shell config was updated
        mock_file.assert_any_call('/test/path', 'r+')
        assert any('source /test/path' in str(call) for call in write_calls)

def test_setup_autocomplete_bash(mock_click_echo, mock_click_confirm):
    # Mock shell type
    with patch('gitask.config.config_utils._get_shell_type', return_value='bash'), \
         patch('builtins.open', mock_open(read_data='')):
        
        # Test when user confirms
        mock_click_confirm.return_value = True
        setup_autocomplete()
        
        # Verify the correct command was suggested
        mock_click_echo.assert_any_call('   To enable autocompletion permanently, we need to update your shell configuration file.')
        
        # Test when user declines
        mock_click_confirm.return_value = False
        setup_autocomplete()
        mock_click_echo.assert_any_call('\n❌ Autocompletion was NOT enabled.')

def test_interactive_setup(mock_click_prompt, mock_click_echo, mock_save_json, mock_os_makedirs):
    # Mock all user inputs
    mock_click_prompt.side_effect = [
        '~/.config/gitask/config.json',  # config file path
        'https://jira.company.com',      # PMT URL
        'pmt_token',                     # PMT token
        'https://gitlab.company.com',    # Git URL
        'git_token',                     # Git token
        'Jira',                          # PMT type
        'Gitlab',                        # VCS type
        'test/project',                  # Git project
        '/scripts/get_issue.sh',         # Current ticket script
        'To Do,Backlog',                 # To-Do statuses
        'In Progress',                   # In-Progress statuses
        'In Review',                     # In-Review statuses
        'Done',                          # Done statuses
        'customfield_12345',             # Git branch field
        'customfield_67890',             # Reviewer field
        '',                              # Pre-open hook
        '',                              # Post-open hook
        '',                              # Pre-start hook
        '',                              # Post-start hook
        '',                              # Pre-review hook
        '',                              # Post-review hook
        '',                              # Pre-done hook
        ''                               # Post-done hook
    ]
    
    # Mock file operations
    with patch('builtins.open', mock_open()), \
         patch('os.path.expanduser', return_value='/test/path'), \
         patch('gitask.config.config_utils.setup_autocomplete') as mock_setup_autocomplete, \
         patch('gitask.config.config_utils._set_env_variables') as mock_set_env, \
         patch('gitask.config.config_utils._get_shell_type', return_value='bash'), \
         patch('os.path.dirname', return_value='/test/config/dir'):
        
        interactive_setup()
        
        # Verify config was saved
        mock_save_json.assert_called_once()
        
        # Verify autocomplete was set up
        mock_setup_autocomplete.assert_called_once()
        
        # Verify environment variables were set
        mock_set_env.assert_called_once()
        
        # Verify directory was created
        mock_os_makedirs.assert_called_with('/test/config/dir', exist_ok=True)

def test_interactive_setup_with_hooks(mock_click_prompt, mock_click_echo, mock_save_json):
    # Mock user inputs including hook scripts
    mock_click_prompt.side_effect = [
        '~/.config/gitask/config.json',  # config file path
        'https://jira.company.com',      # PMT URL
        'pmt_token',                     # PMT token
        'https://gitlab.company.com',    # Git URL
        'git_token',                     # Git token
        'Jira',                          # PMT type
        'Gitlab',                        # VCS type
        'test/project',                  # Git project
        '/scripts/get_issue.sh',         # Current ticket script
        'To Do,Backlog',                 # To-Do statuses
        'In Progress',                   # In-Progress statuses
        'In Review',                     # In-Review statuses
        'Done',                          # Done statuses
        'customfield_12345',             # Git branch field
        'customfield_67890',             # Reviewer field
        '/scripts/pre_open.sh',          # Pre-open hook
        '/scripts/post_open.sh',         # Post-open hook
        '',                              # Pre-start hook
        '',                              # Post-start hook
        '',                              # Pre-review hook
        '',                              # Post-review hook
        '',                              # Pre-done hook
        ''                               # Post-done hook
    ]
    
    with patch('builtins.open', mock_open()), \
         patch('os.path.expanduser', return_value='/test/path'), \
         patch('gitask.config.config_utils.setup_autocomplete'), \
         patch('gitask.config.config_utils._set_env_variables'), \
         patch('gitask.config.config_utils._get_shell_type', return_value='bash'), \
         patch('os.path.dirname', return_value='/test/config/dir'), \
         patch('os.makedirs'):
        
        interactive_setup()
        
        # Verify config was saved with hooks
        mock_save_json.assert_called_once()
        saved_config = mock_save_json.call_args[0][1]
        assert 'hooks' in saved_config
        assert saved_config['hooks']['open']['pre'] == '/test/path'
        assert saved_config['hooks']['open']['post'] == '/test/path' 
