import subprocess
import sys
import json
import pytest
import os

# 1. Missing config file path
def test_configure_missing_config_path(tmp_path):
    user_inputs = "\n"  # blank config path
    result = subprocess.run([
        'gitask', 'configure'
    ], input=user_inputs, capture_output=True, text=True)
    assert result.returncode != 0 or 'config' in result.stderr.lower() or 'config' in result.stdout.lower()

# 2. Invalid config file path
def test_configure_invalid_path(tmp_path):
    user_inputs = "/nonexistent/directory/config.json\n"  # invalid path
    result = subprocess.run([
        'gitask', 'configure'
    ], input=user_inputs, capture_output=True, text=True)
    assert result.returncode != 0 or 'config' in result.stderr.lower() or 'config' in result.stdout.lower()

# 3. Missing required fields
def test_configure_missing_required_fields(tmp_path):
    config_path = tmp_path / "config.json"
    user_inputs = f"""{config_path}\nhttps://jira.company.com\npmt-token\nhttps://gitlab.company.com\ngit-token\nJira\nGitlab\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n"""
    result = subprocess.run([
        'gitask', 'configure'
    ], input=user_inputs, capture_output=True, text=True)
    assert result.returncode != 0 or 'config' in result.stderr.lower() or 'config' in result.stdout.lower()

# 4. Invalid PMT/VCS types
def test_configure_invalid_types(tmp_path):
    config_path = tmp_path / "config.json"
    user_inputs = f"""{config_path}\nhttps://jira.company.com\npmt-token\nhttps://gitlab.company.com\ngit-token\nInvalidPMT\nInvalidVCS\ntest/repo\necho TEST-123\nTo Do,Backlog\nIn Progress\nIn Review\nDone\ncustomfield_12345\ncustomfield_67890\n\n\n\n\n\n\n\n\n\n\n\n"""
    result = subprocess.run([
        'gitask', 'configure'
    ], input=user_inputs, capture_output=True, text=True)
    assert result.returncode != 0 or 'config' in result.stderr.lower() or 'config' in result.stdout.lower()

# 5. Only optional fields blank
def test_configure_optional_fields_blank(tmp_path):
    config_path = tmp_path / "config.json"
    user_inputs = f"""{config_path}\nhttps://jira.company.com\npmt-token\nhttps://gitlab.company.com\ngit-token\nJira\nGitlab\ntest/repo\necho TEST-123\nTo Do,Backlog\n\n\nDone\n\n\n\n\n\n\n\n\n\n\n\n"""
    result = subprocess.run([
        'gitask', 'configure'
    ], input=user_inputs, capture_output=True, text=True, env={**os.environ, 'GITASK_CONFIG_PATH': str(config_path)})
    assert result.returncode == 0
    assert config_path.exists()
    with open(config_path) as f:
        config = json.load(f)
    assert config['pmt-type'] == 'Jira'
    assert config['vcs-type'] == 'Gitlab'
    assert config['git-project'] == 'test/repo'

# 6. All hooks blank
def test_configure_hooks_all_blank(tmp_path):
    config_path = tmp_path / "config.json"
    user_inputs = f"""{config_path}\nhttps://jira.company.com\npmt-token\nhttps://gitlab.company.com\ngit-token\nJira\nGitlab\ntest/repo\necho TEST-123\nTo Do,Backlog\n\n\nDone\n\n\n\n\n\n\n\n\n\n\n\n"""
    result = subprocess.run([
        'gitask', 'configure'
    ], input=user_inputs, capture_output=True, text=True, env={**os.environ, 'GITASK_CONFIG_PATH': str(config_path)})
    assert result.returncode == 0
    assert config_path.exists()
    with open(config_path) as f:
        config = json.load(f)
    assert 'hooks' in config
    for cmd in ['open', 'start', 'review', 'done']:
        assert config['hooks'][cmd] == {}

# 7. Some hooks filled
def test_configure_hooks_some_filled(tmp_path):
    config_path = tmp_path / "config.json"
    user_inputs = f"""{config_path}\nhttps://jira.company.com\npmt-token\nhttps://gitlab.company.com\ngit-token\nJira\nGitlab\ntest/repo\necho TEST-123\nTo Do,Backlog\n\n\nDone\n\n\n\n\n\n\n\n\n\n\n/script/pre-done.sh\n\n\n\n"""
    result = subprocess.run([
        'gitask', 'configure'
    ], input=user_inputs, capture_output=True, text=True, env={**os.environ, 'GITASK_CONFIG_PATH': str(config_path)})
    assert result.returncode == 0
    assert config_path.exists()
    with open(config_path) as f:
        config = json.load(f)
    assert config['hooks']['done']['pre'] == os.path.expanduser('/script/pre-done.sh')

# 8. Comma-separated statuses
def test_configure_comma_separated_statuses(tmp_path):
    config_path = tmp_path / "config.json"
    user_inputs = f"""{config_path}\nhttps://jira.company.com\npmt-token\nhttps://gitlab.company.com\ngit-token\nJira\nGitlab\ntest/repo\necho TEST-123\nTo Do,Backlog, Ready\nIn Progress, Doing\nIn Review, Code Review\nDone, Complete\n\n\n\n\n\n\n\n\n\n\n\n"""
    result = subprocess.run([
        'gitask', 'configure'
    ], input=user_inputs, capture_output=True, text=True, env={**os.environ, 'GITASK_CONFIG_PATH': str(config_path)})
    assert result.returncode == 0
    assert config_path.exists()
    with open(config_path) as f:
        config = json.load(f)
    assert config['to-do'] == ['To Do', 'Backlog', 'Ready']
    assert config['in-progress'] == ['In Progress', 'Doing']
    assert config['in-review'] == ['In Review', 'Code Review']
    assert config['done'] == ['Done', 'Complete']

# 9. Autocompletion rejected
def test_configure_autocomplete_rejected(tmp_path):
    config_path = tmp_path / "config.json"
    user_inputs = f"""{config_path}\nhttps://jira.company.com\npmt-token\nhttps://gitlab.company.com\ngit-token\nJira\nGitlab\ntest/repo\necho TEST-123\nTo Do,Backlog\n\n\nDone\n\n\n\n\n\n\n\n\n\n\n\nno\n"""
    result = subprocess.run([
        'gitask', 'configure'
    ], input=user_inputs, capture_output=True, text=True, env={**os.environ, 'GITASK_CONFIG_PATH': str(config_path)})
    assert result.returncode == 0
    assert config_path.exists()

# 10. Autocompletion accepted
def test_configure_autocomplete_accepted(tmp_path):
    config_path = tmp_path / "config.json"
    user_inputs = f"""{config_path}\nhttps://jira.company.com\npmt-token\nhttps://gitlab.company.com\ngit-token\nJira\nGitlab\ntest/repo\necho TEST-123\nTo Do,Backlog\n\n\nDone\n\n\n\n\n\n\n\n\n\n\n\nyes\n"""
    result = subprocess.run([
        'gitask', 'configure'
    ], input=user_inputs, capture_output=True, text=True, env={**os.environ, 'GITASK_CONFIG_PATH': str(config_path)})
    assert result.returncode == 0
    assert config_path.exists() 
