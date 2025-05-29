import os
import json
import tempfile
import pytest
from gitask.utils import save_json_to_file, split_and_strip
import subprocess
from unittest.mock import patch, MagicMock

from gitask.utils import Utils
from gitask.config.config import Config


@pytest.fixture
def mock_config():
    with patch('gitask.utils.Config') as mock:
        config_instance = MagicMock()
        config_instance.current_ticket_script = "echo TEST-123"
        mock.return_value = config_instance
        yield config_instance


@pytest.fixture
def utils():
    return Utils()


class TestUtils:
    def test_singleton_pattern(self):
        """Test that Utils follows the singleton pattern."""
        utils1 = Utils()
        utils2 = Utils()
        assert utils1 is utils2

    @patch('subprocess.check_output')
    def test_get_current_git_branch(self, mock_check_output):
        """Test getting the current git branch."""
        mock_check_output.return_value = b"feature/test-branch"
        utils = Utils()
        branch = utils.get_current_git_branch()
        assert branch == "feature/test-branch"
        mock_check_output.assert_called_once_with("git rev-parse --abbrev-ref HEAD", shell=True)

    @patch('subprocess.check_output')
    def test_get_current_ticket(self, mock_check_output, mock_config):
        """Test getting the current ticket using the configured script."""
        mock_check_output.return_value = b"TEST-123"
        utils = Utils()
        ticket = utils.get_current_ticket()
        assert ticket == "TEST-123"
        mock_check_output.assert_called_once_with(mock_config.current_ticket_script, shell=True)

    def test_get_current_ticket_no_script(self, mock_config):
        """Test that get_current_ticket raises an error when no script is configured."""
        mock_config.current_ticket_script = None
        utils = Utils()
        with pytest.raises(ValueError, match="No current ticket script defined in the configuration."):
            utils.get_current_ticket()

    @patch('subprocess.check_output')
    def test_get_current_ticket_script_error(self, mock_check_output, mock_config):
        """Test handling of script execution errors."""
        mock_check_output.side_effect = subprocess.CalledProcessError(1, "echo")
        utils = Utils()
        with pytest.raises(subprocess.CalledProcessError):
            utils.get_current_ticket()

    @patch('click.echo')
    def test_create_pull_request(self, mock_echo):
        """Test creating a pull request."""
        utils = Utils()
        mock_vcs = MagicMock()
        mock_vcs.create_pull_request.return_value = "https://github.com/user/repo/pull/123"
        
        pr_link = utils.create_pull_request(
            vcs_object=mock_vcs,
            title="Test PR",
            reviewer="testuser",
            cur_branch="feature/test",
            target_branch="main"
        )
        
        assert pr_link == "https://github.com/user/repo/pull/123"
        mock_vcs.create_pull_request.assert_called_once_with(
            "feature/test",
            "main",
            "Test PR",
            "testuser"
        )
        mock_echo.assert_called_once_with("Successfully created pull request: https://github.com/user/repo/pull/123")

    @patch('click.echo')
    def test_create_pull_request_default_title(self, mock_echo):
        """Test creating a pull request with default title."""
        utils = Utils()
        mock_vcs = MagicMock()
        mock_vcs.create_pull_request.return_value = "https://github.com/user/repo/pull/123"
        
        with patch.object(utils, 'get_current_git_branch', return_value="feature/test"):
            pr_link = utils.create_pull_request(
                vcs_object=mock_vcs,
                title="",
                reviewer="testuser",
                target_branch="main"
            )
        
        assert pr_link == "https://github.com/user/repo/pull/123"
        mock_vcs.create_pull_request.assert_called_once_with(
            "feature/test",
            "main",
            "Merge feature/test into main",
            "testuser"
        )

def test_save_json_to_file():
    data = {"a": 1, "b": 2}
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = os.path.join(tmpdir, "config.json")
        save_json_to_file(file_path, data)
        with open(file_path) as f:
            loaded = json.load(f)
        assert loaded == data

def test_split_and_strip():
    assert split_and_strip("a, b, c") == ["a", "b", "c"]
    assert split_and_strip("  x ,y , z ") == ["x", "y", "z"]
    assert split_and_strip("") == [""]
    assert split_and_strip("one|two|three", sep="|") == ["one", "two", "three"] 
