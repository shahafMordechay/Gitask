import json
import os
import subprocess
from unittest.mock import patch, MagicMock

import pytest

from gitask.utils import Utils, save_json_to_file, split_and_strip


@pytest.fixture
def mock_config():
    with patch('gitask.utils.Config') as mock:
        config = MagicMock()
        config.pmt_url = "https://jira.example.com"
        config.pmt_token = "pmt-token"
        config.git_url = "https://gitlab.example.com"
        config.git_token = "git-token"
        config.current_ticket_script = "echo TEST-123"
        mock.return_value = config
        yield config


@pytest.fixture
def utils_instance(mock_config):
    return Utils()


def test_save_json_to_file(tmp_path):
    file_path = tmp_path / "test.json"
    data = {"test": "data"}
    save_json_to_file(file_path, data)
    assert file_path.exists()
    with open(file_path) as f:
        assert json.load(f) == data


def test_get_current_git_branch(utils_instance):
    with patch('subprocess.check_output') as mock:
        mock.return_value = b"feature/test-branch"
        assert utils_instance.get_current_git_branch() == "feature/test-branch"
        mock.assert_called_once_with("git rev-parse --abbrev-ref HEAD", shell=True)


def test_get_current_ticket(utils_instance):
    with patch('subprocess.check_output') as mock:
        mock.return_value = b"TEST-123"
        assert utils_instance.get_current_ticket() == "TEST-123"
        mock.assert_called_once_with("echo TEST-123", shell=True)


def test_get_current_ticket_no_script(utils_instance, mock_config):
    mock_config.current_ticket_script = None
    with pytest.raises(ValueError, match="No current ticket script defined"):
        utils_instance.get_current_ticket()


def test_create_pull_request(utils_instance):
    mock_vcs = MagicMock()
    mock_vcs.create_pull_request.return_value = "https://gitlab.example.com/merge/1"
    
    with patch.object(utils_instance, 'get_current_git_branch', return_value="feature/test"):
        pr_link = utils_instance.create_pull_request(
            mock_vcs,
            "Test PR",
            "reviewer",
            target_branch="main"
        )
        
        assert pr_link == "https://gitlab.example.com/merge/1"
        mock_vcs.create_pull_request.assert_called_once_with(
            "feature/test",
            "main",
            "Test PR",
            "reviewer"
        )


def test_create_pull_request_empty_title(utils_instance):
    mock_vcs = MagicMock()
    mock_vcs.create_pull_request.return_value = "https://gitlab.example.com/merge/1"
    
    with patch.object(utils_instance, 'get_current_git_branch', return_value="feature/test"):
        pr_link = utils_instance.create_pull_request(
            mock_vcs,
            "",
            "reviewer",
            target_branch="main"
        )
        
        assert pr_link == "https://gitlab.example.com/merge/1"
        mock_vcs.create_pull_request.assert_called_once_with(
            "feature/test",
            "main",
            "Merge feature/test into main",
            "reviewer"
        )


def test_run_hook_script_python(utils_instance, tmp_path):
    import sys
    script_path = tmp_path / "test.py"
    script_path.write_text("print('test')")
    script_path.chmod(0o755)
    
    with patch('subprocess.check_output') as mock_check_output, \
         patch('subprocess.run') as mock_run:
        mock_check_output.return_value = b"TEST-123"
        utils_instance.run_hook_script(str(script_path), {"param": "value"})
        
        mock_check_output.assert_called_once_with("echo TEST-123", shell=True)
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert args[0] == sys.executable or args[0] == "python"
        assert args[1] == str(script_path)
        assert "--pmt-url=https://jira.example.com" in args
        assert "--pmt-token=pmt-token" in args
        assert "--git-url=https://gitlab.example.com" in args
        assert "--git-token=git-token" in args
        assert "--issue-key=TEST-123" in args
        assert "--command-params=" in args[-1]


def test_run_hook_script_shell(utils_instance, tmp_path):
    script_path = tmp_path / "test.sh"
    script_path.write_text("echo 'test'")
    script_path.chmod(0o755)
    
    with patch('subprocess.check_output') as mock_check_output, \
         patch('subprocess.run') as mock_run:
        mock_check_output.return_value = b"TEST-123"
        utils_instance.run_hook_script(str(script_path), None)
        
        mock_check_output.assert_called_once_with("echo TEST-123", shell=True)
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert args[0] == "bash"
        assert args[1] == str(script_path)
        assert "--pmt-url=https://jira.example.com" in args
        assert "--pmt-token=pmt-token" in args
        assert "--git-url=https://gitlab.example.com" in args
        assert "--git-token=git-token" in args
        assert "--issue-key=TEST-123" in args


def test_run_hook_script_not_found(utils_instance):
    with pytest.raises(FileNotFoundError):
        utils_instance.run_hook_script("nonexistent.py", None)


def test_run_hook_script_unsupported_type(utils_instance, tmp_path):
    script_path = tmp_path / "test.txt"
    script_path.write_text("test")
    
    with pytest.raises(ValueError, match="Unsupported hook script type"):
        utils_instance.run_hook_script(str(script_path), None)


def test_run_hook_script_permission_error(utils_instance, tmp_path):
    script_path = tmp_path / "test.sh"
    script_path.write_text("echo 'test'")
    
    with patch('subprocess.check_output') as mock_check_output, \
         patch('subprocess.run', side_effect=PermissionError("Permission denied")):
        mock_check_output.return_value = b"TEST-123"
        with pytest.raises(RuntimeError, match="Failed to execute hook script"):
            utils_instance.run_hook_script(str(script_path), None)


def test_split_and_strip():
    assert split_and_strip("a, b, c") == ["a", "b", "c"]
    assert split_and_strip("a|b|c", sep="|") == ["a", "b", "c"]
    assert split_and_strip("  a  ,  b  ,  c  ") == ["a", "b", "c"]
    assert split_and_strip("") == [""] 
