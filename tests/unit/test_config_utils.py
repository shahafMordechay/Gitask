import os
import json
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
    """Fixture to mock click.prompt responses."""
    with patch('click.prompt') as mock:
        # Default responses for interactive setup
        mock.side_effect = [
            "~/.config/gitask/config.json",  # config file path
            "https://jira.company.com",      # PMT URL
            "pmt-token",                     # PMT token
            "https://gitlab.company.com",    # Git URL
            "git-token",                     # Git token
            "Jira",                          # PMT type
            "Gitlab",                        # VCS type
            "test/repo",                     # Git project
            "echo TEST-123",                 # Current ticket script
            "To Do,Backlog",                 # To-Do statuses
            "In Progress",                   # In-Progress statuses
            "In Review",                     # In-Review statuses
            "Done",                          # Done statuses
            "customfield_12345",             # Git branch field
            "customfield_67890",             # Reviewer field
            "",                              # Pre-open script
            "",                              # Post-open script
            "",                              # Pre-start script
            "",                              # Post-start script
            "",                              # Pre-review script
            "",                              # Post-review script
            "",                              # Pre-done script
            ""                               # Post-done script
        ]
        yield mock


@pytest.fixture
def mock_click_confirm():
    """Fixture to mock click.confirm responses."""
    with patch('click.confirm') as mock:
        mock.return_value = True
        yield mock


@pytest.fixture
def mock_shell_config():
    """Fixture to mock shell configuration file."""
    with patch('builtins.open', mock_open(read_data="")) as mock:
        yield mock


class TestConfigUtils:
    def test_interactive_setup(self, mock_click_prompt, mock_click_confirm, mock_shell_config):
        """Test interactive setup process."""
        with patch('gitask.config.config_utils.save_json_to_file') as mock_save:
            with patch('gitask.config.config_utils._set_env_variables') as mock_set_env:
                with patch('gitask.config.config_utils.setup_autocomplete') as mock_setup_auto:
                    interactive_setup()

                    # Verify config file was saved with correct data
                    mock_save.assert_called_once()
                    config_data = mock_save.call_args[0][1]
                    assert config_data['pmt-type'] == 'Jira'
                    assert config_data['vcs-type'] == 'Gitlab'
                    assert config_data['git-project'] == 'test/repo'
                    assert config_data['current-ticket'] == 'echo TEST-123'
                    assert config_data['to-do'] == ['To Do', 'Backlog']
                    assert config_data['in-progress'] == ['In Progress']
                    assert config_data['in-review'] == ['In Review']
                    assert config_data['done'] == ['Done']
                    assert config_data['git-branch-field'] == 'customfield_12345'
                    assert config_data['reviewer-field'] == 'customfield_67890'

                    # Verify environment variables were set
                    mock_set_env.assert_called_once()
                    env_vars = mock_set_env.call_args[0][0]
                    assert env_vars['GITASK_CONFIG_PATH'] == os.path.expanduser("~/.config/gitask/config.json")
                    assert env_vars['GITASK_PMT_URL'] == 'https://jira.company.com'
                    assert env_vars['GITASK_PMT_TOKEN'] == 'pmt-token'
                    assert env_vars['GITASK_GIT_URL'] == 'https://gitlab.company.com'
                    assert env_vars['GITASK_GIT_TOKEN'] == 'git-token'

                    # Verify autocompletion was set up
                    mock_setup_auto.assert_called_once()

    def test_set_env_variables(self):
        """Test setting environment variables."""
        env_vars = {
            'GITASK_CONFIG_PATH': '/test/config.json',
            'GITASK_PMT_TOKEN': 'test-token'
        }

        mock_file = mock_open()
        with patch('builtins.open', mock_file) as mock_open_file:
            with patch('os.makedirs') as mock_makedirs:
                _set_env_variables(env_vars)

                # Verify env file was created with correct content
                mock_open_file.assert_called()
                mock_file().write.assert_called()
                write_calls = mock_file().write.call_args_list
                assert any('export GITASK_CONFIG_PATH="/test/config.json"' in call[0][0] for call in write_calls)
                assert any('export GITASK_PMT_TOKEN="test-token"' in call[0][0] for call in write_calls)

    def test_setup_autocomplete(self):
        """Test setting up autocompletion."""
        mock_file = mock_open()
        with patch('builtins.open', mock_file) as mock_open_file:
            with patch('gitask.config.config_utils._get_shell_type', return_value='bash'):
                with patch('click.confirm', return_value=True):
                    setup_autocomplete()

                    # Verify shell config was updated with autocompletion command
                    mock_open_file.assert_called()
                    mock_file().write.assert_called()
                    write_calls = mock_file().write.call_args_list
                    assert any('eval "$(_GITASK_COMPLETE=bash_source gitask)"' in call[0][0] for call in write_calls)

    def test_get_shell_type(self):
        """Test shell type detection."""
        with patch('os.getenv', return_value='/bin/bash'):
            assert _get_shell_type() == 'bash'

        with patch('os.getenv', return_value='/bin/zsh'):
            assert _get_shell_type() == 'zsh'

        with patch('os.getenv', return_value='/usr/bin/fish'):
            assert _get_shell_type() == 'fish'

        with patch('os.getenv', return_value='/bin/tcsh'):
            with pytest.raises(SystemExit):
                _get_shell_type() 
