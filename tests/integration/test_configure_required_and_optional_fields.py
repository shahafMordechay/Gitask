import subprocess
import sys
import json
import pytest
from unittest.mock import patch, mock_open

# 1. Happy path: all fields filled
def test_configure_all_fields(tmp_path):
    config_path = tmp_path / "config.json"
    user_inputs = f"""{config_path}\nhttps://jira.company.com\npmt-token\nhttps://gitlab.company.com\ngit-token\nJira\nGitlab\ntest/repo\necho TEST-123\nTo Do,Backlog\nIn Progress\nIn Review\nDone\ncustomfield_12345\ncustomfield_67890\n/script/pre-open.sh\n/script/post-open.sh\n/script/pre-start.sh\n/script/post-start.sh\n/script/pre-review.sh\n/script/post-review.sh\n/script/pre-done.sh\n/script/post-done.sh\n"""
    with patch('builtins.open', mock_open()):
        with patch('os.makedirs'):
            with patch('gitask.config.config_utils.setup_autocomplete'):
                result = subprocess.run([
                    sys.executable, '-m', 'gitask', 'configure'
                ], input=user_inputs, capture_output=True, text=True)
    assert result.returncode == 0
    # Would check config file content if not mocked

# 2. Only required fields
def test_configure_required_fields_only(tmp_path):
    config_path = tmp_path / "config.json"
    user_inputs = f"""{config_path}\nhttps://jira.company.com\npmt-token\nhttps://gitlab.company.com\ngit-token\nJira\nGitlab\ntest/repo\necho TEST-123\nTo Do,Backlog\n\n\nDone\n\n\n\n\n\n\n\n\n\n\n\n"""
    with patch('builtins.open', mock_open()):
        with patch('os.makedirs'):
            with patch('gitask.config.config_utils.setup_autocomplete'):
                result = subprocess.run([
                    sys.executable, '-m', 'gitask', 'configure'
                ], input=user_inputs, capture_output=True, text=True)
    assert result.returncode == 0

# 3. Missing required fields
def test_configure_missing_required_fields(tmp_path):
    config_path = tmp_path / "config.json"
    user_inputs = f"""{config_path}\nhttps://jira.company.com\npmt-token\nhttps://gitlab.company.com\ngit-token\nJira\nGitlab\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n"""
    with patch('builtins.open', mock_open()):
        with patch('os.makedirs'):
            with patch('gitask.config.config_utils.setup_autocomplete'):
                result = subprocess.run([
                    sys.executable, '-m', 'gitask', 'configure'
                ], input=user_inputs, capture_output=True, text=True)
    assert result.returncode != 0

# 4. Invalid PMT/VCS types
def test_configure_invalid_types(tmp_path):
    config_path = tmp_path / "config.json"
    user_inputs = f"""{config_path}\nhttps://jira.company.com\npmt-token\nhttps://gitlab.company.com\ngit-token\nInvalidPMT\nInvalidVCS\ntest/repo\necho TEST-123\nTo Do,Backlog\nIn Progress\nIn Review\nDone\ncustomfield_12345\ncustomfield_67890\n\n\n\n\n\n\n\n\n\n\n\n"""
    with patch('builtins.open', mock_open()):
        with patch('os.makedirs'):
            with patch('gitask.config.config_utils.setup_autocomplete'):
                result = subprocess.run([
                    sys.executable, '-m', 'gitask', 'configure'
                ], input=user_inputs, capture_output=True, text=True)
    assert result.returncode != 0

# 5. Comma-separated statuses
def test_configure_comma_separated_statuses(tmp_path):
    config_path = tmp_path / "config.json"
    user_inputs = f"""{config_path}\nhttps://jira.company.com\npmt-token\nhttps://gitlab.company.com\ngit-token\nJira\nGitlab\ntest/repo\necho TEST-123\nTo Do,Backlog, Ready\nIn Progress, Doing\nIn Review, Code Review\nDone, Complete\n\n\n\n\n\n\n\n\n\n\n\n"""
    with patch('builtins.open', mock_open()):
        with patch('os.makedirs'):
            with patch('gitask.config.config_utils.setup_autocomplete'):
                result = subprocess.run([
                    sys.executable, '-m', 'gitask', 'configure'
                ], input=user_inputs, capture_output=True, text=True)
    assert result.returncode == 0

# 6. Hooks: all blank
def test_configure_hooks_all_blank(tmp_path):
    config_path = tmp_path / "config.json"
    user_inputs = f"""{config_path}\nhttps://jira.company.com\npmt-token\nhttps://gitlab.company.com\ngit-token\nJira\nGitlab\ntest/repo\necho TEST-123\nTo Do,Backlog\n\n\nDone\n\n\n\n\n\n\n\n\n\n\n\n"""
    with patch('builtins.open', mock_open()):
        with patch('os.makedirs'):
            with patch('gitask.config.config_utils.setup_autocomplete'):
                result = subprocess.run([
                    sys.executable, '-m', 'gitask', 'configure'
                ], input=user_inputs, capture_output=True, text=True)
    assert result.returncode == 0

# 7. Hooks: some filled
def test_configure_hooks_some_filled(tmp_path):
    config_path = tmp_path / "config.json"
    user_inputs = f"""{config_path}\nhttps://jira.company.com\npmt-token\nhttps://gitlab.company.com\ngit-token\nJira\nGitlab\ntest/repo\necho TEST-123\nTo Do,Backlog\n\n\nDone\n\n\n\n\n\n\n\n\n\n\n/script/pre-done.sh\n\n\n\n"""
    with patch('builtins.open', mock_open()):
        with patch('os.makedirs'):
            with patch('gitask.config.config_utils.setup_autocomplete'):
                result = subprocess.run([
                    sys.executable, '-m', 'gitask', 'configure'
                ], input=user_inputs, capture_output=True, text=True)
    assert result.returncode == 0 
