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
def test_done_happy_path(tmp_path, monkeypatch):
    config_path = tmp_path / 'config.json'
    write_config(config_path)
    monkeypatch.setenv('GITASK_CONFIG_PATH', str(config_path))
    result = subprocess.run([
        'gitask', 'done'
    ], capture_output=True, text=True)
    assert result.returncode == 0

# 2. Missing config file
def test_done_missing_config_file(tmp_path, monkeypatch):
    config_path = tmp_path / 'config.json'
    monkeypatch.setenv('GITASK_CONFIG_PATH', str(config_path))
    result = subprocess.run([
        'gitask', 'done'
    ], capture_output=True, text=True)
    assert result.returncode != 0 or 'config' in result.stderr.lower() or 'config' in result.stdout.lower()

# 3. Missing required config field
def test_done_missing_required_field(tmp_path, monkeypatch):
    config_path = tmp_path / 'config.json'
    write_config(config_path, overrides={'current-ticket': None})
    monkeypatch.setenv('GITASK_CONFIG_PATH', str(config_path))
    result = subprocess.run([
        'gitask', 'done'
    ], capture_output=True, text=True)
    assert result.returncode != 0 or 'current' in result.stderr.lower() or 'current' in result.stdout.lower()

# 4. No current ticket
def test_done_no_current_ticket(tmp_path, monkeypatch):
    config_path = tmp_path / 'config.json'
    write_config(config_path, overrides={'current-ticket': 'echo ""'})
    monkeypatch.setenv('GITASK_CONFIG_PATH', str(config_path))
    result = subprocess.run([
        'gitask', 'done'
    ], capture_output=True, text=True)
    assert result.returncode != 0 or 'ticket' in result.stderr.lower() or 'ticket' in result.stdout.lower()

# 5. PMT error (simulate by using an invalid status)
def test_done_pmt_error(tmp_path, monkeypatch):
    config_path = tmp_path / 'config.json'
    write_config(config_path, overrides={'done': ['INVALID_STATUS']})
    monkeypatch.setenv('GITASK_CONFIG_PATH', str(config_path))
    result = subprocess.run([
        'gitask', 'done'
    ], capture_output=True, text=True)
    assert result.returncode != 0 or 'error' in result.stderr.lower() or 'error' in result.stdout.lower()

# 6. Already in target status
def test_done_already_in_target_status(tmp_path, monkeypatch):
    config_path = tmp_path / 'config.json'
    write_config(config_path)
    monkeypatch.setenv('GITASK_CONFIG_PATH', str(config_path))
    result = subprocess.run([
        'gitask', 'done'
    ], capture_output=True, text=True)
    assert result.returncode == 0 or 'already' in result.stdout.lower() or 'already' in result.stderr.lower()

# 7. Corrupted/invalid config file
def test_done_corrupted_config_file(tmp_path, monkeypatch):
    config_path = tmp_path / 'config.json'
    with open(config_path, 'w') as f:
        f.write('{invalid json')
    monkeypatch.setenv('GITASK_CONFIG_PATH', str(config_path))
    result = subprocess.run([
        'gitask', 'done'
    ], capture_output=True, text=True)
    assert result.returncode != 0 or 'json' in result.stderr.lower() or 'json' in result.stdout.lower() or 'decode' in result.stderr.lower() or 'decode' in result.stdout.lower()

# 8. GITASK_CONFIG_PATH not set
def test_done_env_var_not_set(tmp_path, monkeypatch):
    monkeypatch.delenv('GITASK_CONFIG_PATH', raising=False)
    result = subprocess.run([
        'gitask', 'done'
    ], capture_output=True, text=True)
    assert result.returncode != 0 or 'config' in result.stderr.lower() or 'config' in result.stdout.lower()

# 9. CLI with unexpected arguments
def test_done_unexpected_argument(tmp_path, monkeypatch):
    config_path = tmp_path / 'config.json'
    write_config(config_path)
    monkeypatch.setenv('GITASK_CONFIG_PATH', str(config_path))
    result = subprocess.run([
        'gitask', 'done', '--unknown-flag'
    ], capture_output=True, text=True)
    assert result.returncode != 0 or 'usage' in result.stderr.lower() or 'usage' in result.stdout.lower() or 'unknown' in result.stderr.lower() or 'unknown' in result.stdout.lower()

# 10. Multiple tickets/unexpected script output
def test_done_multiple_tickets_script(tmp_path, monkeypatch):
    config_path = tmp_path / 'config.json'
    write_config(config_path, overrides={'current-ticket': 'echo "TICKET-1 TICKET-2"'})
    monkeypatch.setenv('GITASK_CONFIG_PATH', str(config_path))
    result = subprocess.run([
        'gitask', 'done'
    ], capture_output=True, text=True)
    assert result.returncode != 0 or 'multiple' in result.stderr.lower() or 'multiple' in result.stdout.lower() or 'ticket' in result.stderr.lower() or 'ticket' in result.stdout.lower() 
