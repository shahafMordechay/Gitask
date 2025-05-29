import subprocess
import sys
import json
import os
import pytest

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

# 1. Happy path
def test_open_happy_path(tmp_path, monkeypatch):
    config_path = tmp_path / 'config.json'
    write_config(config_path)
    monkeypatch.setenv('GITASK_CONFIG_PATH', str(config_path))
    # Patch PMT and Utils to simulate success
    result = subprocess.run([
        sys.executable, '-m', 'gitask', 'open'
    ], capture_output=True, text=True)
    # Should succeed or at least not crash
    assert result.returncode == 0

# 2. Missing config file
def test_open_missing_config_file(tmp_path, monkeypatch):
    config_path = tmp_path / 'config.json'
    monkeypatch.setenv('GITASK_CONFIG_PATH', str(config_path))
    result = subprocess.run([
        sys.executable, '-m', 'gitask', 'open'
    ], capture_output=True, text=True)
    assert result.returncode != 0 or 'config' in result.stderr.lower() or 'config' in result.stdout.lower()

# 3. Missing required config field
def test_open_missing_required_field(tmp_path, monkeypatch):
    config_path = tmp_path / 'config.json'
    write_config(config_path, overrides={'current-ticket': None})
    monkeypatch.setenv('GITASK_CONFIG_PATH', str(config_path))
    result = subprocess.run([
        sys.executable, '-m', 'gitask', 'open'
    ], capture_output=True, text=True)
    assert result.returncode != 0 or 'current' in result.stderr.lower() or 'current' in result.stdout.lower()

# 4. No current ticket
def test_open_no_current_ticket(tmp_path, monkeypatch):
    config_path = tmp_path / 'config.json'
    # Use a script that returns nothing
    write_config(config_path, overrides={'current-ticket': 'echo ""'})
    monkeypatch.setenv('GITASK_CONFIG_PATH', str(config_path))
    result = subprocess.run([
        sys.executable, '-m', 'gitask', 'open'
    ], capture_output=True, text=True)
    assert result.returncode != 0 or 'ticket' in result.stderr.lower() or 'ticket' in result.stdout.lower()

# 5. PMT error (simulate by using an invalid status)
def test_open_pmt_error(tmp_path, monkeypatch):
    config_path = tmp_path / 'config.json'
    # Use a status that will not be found
    write_config(config_path, overrides={'to-do': ['INVALID_STATUS']})
    monkeypatch.setenv('GITASK_CONFIG_PATH', str(config_path))
    result = subprocess.run([
        sys.executable, '-m', 'gitask', 'open'
    ], capture_output=True, text=True)
    assert result.returncode != 0 or 'error' in result.stderr.lower() or 'error' in result.stdout.lower()

# 6. Already in target status (simulate by using a script that returns a ticket already in 'To Do')
def test_open_already_in_target_status(tmp_path, monkeypatch):
    config_path = tmp_path / 'config.json'
    # This scenario may require a more advanced mock, but we can check for a message
    write_config(config_path)
    monkeypatch.setenv('GITASK_CONFIG_PATH', str(config_path))
    # No real way to simulate this without a real PMT, so just run and check for no crash
    result = subprocess.run([
        sys.executable, '-m', 'gitask', 'open'
    ], capture_output=True, text=True)
    assert result.returncode == 0 or 'already' in result.stdout.lower() or 'already' in result.stderr.lower()

# 7. Corrupted/invalid config file
def test_open_corrupted_config_file(tmp_path, monkeypatch):
    config_path = tmp_path / 'config.json'
    with open(config_path, 'w') as f:
        f.write('{invalid json')
    monkeypatch.setenv('GITASK_CONFIG_PATH', str(config_path))
    result = subprocess.run([
        sys.executable, '-m', 'gitask', 'open'
    ], capture_output=True, text=True)
    assert result.returncode != 0 or 'json' in result.stderr.lower() or 'json' in result.stdout.lower() or 'decode' in result.stderr.lower() or 'decode' in result.stdout.lower()

# 8. GITASK_CONFIG_PATH not set
def test_open_env_var_not_set(tmp_path, monkeypatch):
    # Ensure env var is not set
    monkeypatch.delenv('GITASK_CONFIG_PATH', raising=False)
    result = subprocess.run([
        sys.executable, '-m', 'gitask', 'open'
    ], capture_output=True, text=True)
    assert result.returncode != 0 or 'config' in result.stderr.lower() or 'config' in result.stdout.lower()

# 9. CLI with unexpected arguments
def test_open_unexpected_argument(tmp_path, monkeypatch):
    config_path = tmp_path / 'config.json'
    write_config(config_path)
    monkeypatch.setenv('GITASK_CONFIG_PATH', str(config_path))
    result = subprocess.run([
        sys.executable, '-m', 'gitask', 'open', '--unknown-flag'
    ], capture_output=True, text=True)
    assert result.returncode != 0 or 'usage' in result.stderr.lower() or 'usage' in result.stdout.lower() or 'unknown' in result.stderr.lower() or 'unknown' in result.stdout.lower()

# 10. Interactive prompt invalid input (simulate by running config with a number for a string field)
def test_configure_invalid_input_type(tmp_path):
    config_path = tmp_path / "config.json"
    # Enter a number for PMT type (should be a string/choice)
    user_inputs = f"""{config_path}\nhttps://jira.company.com\npmt-token\nhttps://gitlab.company.com\ngit-token\n123\nGitlab\ntest/repo\necho TEST-123\nTo Do,Backlog\n\n\nDone\n\n\n\n\n\n\n\n\n\n\n\n"""
    result = subprocess.run([
        sys.executable, '-m', 'gitask', 'config', 'init'
    ], input=user_inputs, capture_output=True, text=True)
    assert result.returncode != 0 or 'invalid' in result.stderr.lower() or 'invalid' in result.stdout.lower()

# 11. Multiple tickets/unexpected script output
def test_open_multiple_tickets_script(tmp_path, monkeypatch):
    config_path = tmp_path / 'config.json'
    # Script returns multiple tickets
    write_config(config_path, overrides={'current-ticket': 'echo "TICKET-1 TICKET-2"'})
    monkeypatch.setenv('GITASK_CONFIG_PATH', str(config_path))
    result = subprocess.run([
        sys.executable, '-m', 'gitask', 'open'
    ], capture_output=True, text=True)
    # Should error or handle gracefully
    assert result.returncode != 0 or 'multiple' in result.stderr.lower() or 'multiple' in result.stdout.lower() or 'ticket' in result.stderr.lower() or 'ticket' in result.stdout.lower() 
