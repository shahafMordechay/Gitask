import json
import os
from unittest.mock import patch, mock_open

import pytest

from gitask.config.config import Config


@pytest.fixture(autouse=True)
def reset_config_singleton():
    Config._instance = None
    yield
    Config._instance = None


@pytest.fixture
def mock_env_vars():
    """Fixture to set up mock environment variables."""
    env_vars = {
        'GITASK_CONFIG_PATH': '/test/config.json',
        'GITASK_PMT_TOKEN': 'test-pmt-token',
        'GITASK_PMT_URL': 'https://test-pmt.com',
        'GITASK_GIT_TOKEN': 'test-git-token',
        'GITASK_GIT_URL': 'https://test-git.com'
    }
    with patch.dict(os.environ, env_vars):
        yield env_vars


@pytest.fixture
def mock_config_file():
    """Fixture to provide mock config file content."""
    return {
        'pmt-type': 'Jira',
        'vcs-type': 'GitHub',
        'git-project': 'test/repo',
        'to-do': ['To Do', 'Backlog'],
        'in-progress': ['In Progress'],
        'in-review': ['In Review'],
        'done': ['Done'],
        'reviewer-field': 'customfield_12345',
        'git-branch-field': 'customfield_67890',
        'current-ticket': 'echo TEST-123',
        'hooks': {
            'open': {'pre': '/path/to/pre-open.sh'},
            'done': {'post': '/path/to/post-done.sh'}
        }
    }


class TestConfig:
    def test_singleton_pattern(self):
        """Test that Config follows the singleton pattern."""
        config1 = Config()
        config2 = Config()
        assert config1 is config2

    def test_load_config_file_not_found(self):
        """Test behavior when config file doesn't exist."""
        with patch('os.getenv', return_value='/nonexistent/path'):
            with patch('builtins.open', side_effect=FileNotFoundError):
                config = Config()
                assert config.config_data == {}

    def test_load_config_invalid_json(self):
        """Test behavior when config file contains invalid JSON."""
        mock_file = mock_open(read_data='invalid json')
        with patch('builtins.open', mock_file):
            config = Config()
            assert config.config_data == {}

    def test_load_config_success(self, mock_config_file):
        """Test successful loading of config file."""
        mock_file = mock_open(read_data=json.dumps(mock_config_file))
        with patch('builtins.open', mock_file):
            config = Config()
            assert config.config_data == mock_config_file

    def test_environment_variables(self, mock_env_vars):
        """Test accessing environment variables."""
        config = Config()
        assert config.pmt_token == mock_env_vars['GITASK_PMT_TOKEN']
        assert config.pmt_url == mock_env_vars['GITASK_PMT_URL']
        assert config.git_token == mock_env_vars['GITASK_GIT_TOKEN']
        assert config.git_url == mock_env_vars['GITASK_GIT_URL']

    def test_config_properties(self, mock_config_file):
        """Test accessing config file properties."""
        mock_file = mock_open(read_data=json.dumps(mock_config_file))
        with patch('builtins.open', mock_file):
            config = Config()
            assert config.pmt_type == mock_config_file['pmt-type']
            assert config.vcs_type == mock_config_file['vcs-type']
            assert config.git_proj == mock_config_file['git-project']
            assert config.to_do_statuses == mock_config_file['to-do']
            assert config.in_progress_statuses == mock_config_file['in-progress']
            assert config.in_review_statuses == mock_config_file['in-review']
            assert config.done_statuses == mock_config_file['done']
            assert config.reviewer_field == mock_config_file['reviewer-field']
            assert config.git_branch_field == mock_config_file['git-branch-field']
            assert config.current_ticket_script == mock_config_file['current-ticket']
            assert config.hooks == mock_config_file['hooks']

    def test_missing_optional_properties(self):
        """Test behavior when optional properties are missing."""
        mock_file = mock_open(read_data=json.dumps({}))
        with patch('builtins.open', mock_file):
            config = Config()
            assert config.in_progress_statuses is None
            assert config.in_review_statuses is None
            assert config.reviewer_field is None
            assert config.git_branch_field is None
            assert config.hooks == {} 
