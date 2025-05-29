import subprocess
import sys
import json
import os
import pytest
import tempfile
import stat

# Helper to write a dummy config file
def write_config(config_path, overrides=None):
    config = {
        'pmt-type': 'Jira',
        'vcs-type': 'Gitlab',
        'git-project': 'test/repo',
        'current-ticket': 'echo TEST-123',
        'to-do': ['To Do', 'Backlog'],
        'done': ['Done'],
        'in-progress': ['In Progress'],
        'in-review': ['In Review'],
        'hooks': {cmd: {} for cmd in ['open', 'start', 'review', 'done']}
    }
    if overrides:
        config.update(overrides)
    with open(config_path, 'w') as f:
        json.dump(config, f)

# 1. File system permission errors
def test_config_permission_error(tmp_path, monkeypatch):
    config_path = tmp_path / 'config.json'
    write_config(config_path)
    # Make the file read-only
    os.chmod(config_path, stat.S_IREAD)
    monkeypatch.setenv('GITASK_CONFIG_PATH', str(config_path))
    # Try to overwrite config (simulate by running configure)
    user_inputs = f"""{config_path}\nhttps://jira.company.com\npmt-token\nhttps://gitlab.company.com\ngit-token\nJira\nGitlab\ntest/repo\necho TEST-123\nTo Do,Backlog\nIn Progress\nIn Review\nDone\ncustomfield_12345\ncustomfield_67890\n\n\n\n\n\n\n\n\n\n\n\n"""
    result = subprocess.run([
        'gitask', 'config', 'init'
    ], input=user_inputs, capture_output=True, text=True)
    os.chmod(config_path, stat.S_IWRITE)  # Clean up for Windows
    assert result.returncode != 0
    assert 'Permission denied' in result.stderr or 'Permission denied' in result.stdout

# 2. Malformed environment variable (invalid path)
def test_config_invalid_env_path(tmp_path, monkeypatch):
    # Set env var to a directory
    monkeypatch.setenv('GITASK_CONFIG_PATH', str(tmp_path))
    result = subprocess.run([
        'gitask', 'open'
    ], capture_output=True, text=True)
    assert result.returncode != 0
    assert f"Error: Configuration file not found at {tmp_path}" in result.stdout or result.stderr

# 3. Corrupted/invalid config file
def test_config_invalid_json(tmp_path, monkeypatch):
    config_path = tmp_path / 'config.json'
    with open(config_path, 'w') as f:
        f.write('{invalid json')
    monkeypatch.setenv('GITASK_CONFIG_PATH', str(config_path))
    result = subprocess.run([
        'gitask', 'open'
    ], capture_output=True, text=True)
    assert result.returncode != 0
    assert f"Error: Failed to parse config file {config_path}." in result.stdout or result.stderr

# 4. Unsupported shell for autocompletion
def test_unsupported_shell_for_autocomplete(monkeypatch):
    monkeypatch.setenv('SHELL', '/bin/tcsh')
    result = subprocess.run([
        'gitask', 'configure', '--auto-complete'
    ], capture_output=True, text=True)
    assert result.returncode != 0
    assert 'not supported' in result.stdout or 'not supported' in result.stderr

# 5. Network/service unavailability
def test_network_unavailable(tmp_path, monkeypatch):
    config_path = tmp_path / 'config.json'
    # Use an invalid PMT URL
    write_config(config_path)
    monkeypatch.setenv('GITASK_CONFIG_PATH', str(config_path))
    monkeypatch.setenv('GITASK_PMT_URL', 'http://localhost:9999')
    # This will fail if the CLI tries to connect to the PMT
    result = subprocess.run([
        'gitask', 'open'
    ], capture_output=True, text=True, timeout=10)
    assert result.returncode != 0
    assert 'Unable to connect' in result.stdout or 'Unable to connect' in result.stderr or 'Connection refused' in result.stdout or 'Connection refused' in result.stderr

# 6. CLI invoked from non-project directory
def test_cli_outside_git_repo(tmp_path, monkeypatch):
    config_path = tmp_path / 'config.json'
    write_config(config_path)
    monkeypatch.setenv('GITASK_CONFIG_PATH', str(config_path))
    cwd = os.getcwd()
    try:
        os.chdir(tmp_path)
        result = subprocess.run([
            'gitask', 'open'
        ], capture_output=True, text=True)
    finally:
        os.chdir(cwd)
    assert result.returncode != 0
    assert 'git repository' in result.stdout or 'git repository' in result.stderr or 'not a git repo' in result.stdout or 'not a git repo' in result.stderr

# 7. Invalid reviewer/branch/status names
def test_invalid_reviewer_branch_status(tmp_path, monkeypatch):
    config_path = tmp_path / 'config.json'
    # Use invalid reviewer and status names
    write_config(config_path, overrides={'in-review': [''], 'done': [''], 'to-do': [''], 'in-progress': [''], 'git-project': '', 'current-ticket': ''})
    monkeypatch.setenv('GITASK_CONFIG_PATH', str(config_path))
    result = subprocess.run([
        'gitask', 'submit-to-review', '-r', '', '-b', ''
    ], capture_output=True, text=True)
    assert result.returncode != 0
    assert 'cannot be empty' in result.stdout or 'cannot be empty' in result.stderr or 'invalid' in result.stdout or 'invalid' in result.stderr 
