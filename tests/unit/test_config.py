import os
import json
import pytest
from unittest.mock import patch, mock_open
from gitask.config.config import Config

@pytest.fixture(autouse=True)
def reset_config_singleton():
    Config._instance = None
    yield
    Config._instance = None

def make_config_data(**overrides):
    data = {
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
        'hooks': {'open': {'pre': '/pre.sh'}}
    }
    data.update(overrides)
    return data

def test_singleton_pattern(tmp_path):
    config_path = tmp_path / "config.json"
    data = make_config_data()
    config_path.write_text(json.dumps(data))
    with patch.dict(os.environ, {Config.CONFIG_FILE: str(config_path)}):
        c1 = Config()
        c2 = Config()
        assert c1 is c2

def test_load_config_file_not_found(tmp_path):
    config_path = tmp_path / "notfound.json"
    with patch.dict(os.environ, {Config.CONFIG_FILE: str(config_path)}):
        with pytest.raises(FileNotFoundError, match=f"Configuration file not found at {config_path}"):
            Config()

def test_load_config_invalid_json(tmp_path):
    config_path = tmp_path / "bad.json"
    config_path.write_text("not json")
    with patch.dict(os.environ, {Config.CONFIG_FILE: str(config_path)}):
        with pytest.raises(ValueError, match=f"Failed to parse config file {config_path}."):
            Config()

def test_missing_required_fields(tmp_path):
    config_path = tmp_path / "missing.json"
    data = make_config_data()
    del data['pmt-type']
    config_path.write_text(json.dumps(data))
    with patch.dict(os.environ, {Config.CONFIG_FILE: str(config_path)}):
        with pytest.raises(ValueError, match="Missing required fields: pmt-type"):
            Config()

def test_property_access(tmp_path):
    config_path = tmp_path / "config.json"
    data = make_config_data()
    config_path.write_text(json.dumps(data))
    env = {
        Config.CONFIG_FILE: str(config_path),
        Config.PMT_TOKEN_ENV_VAR: 'tok',
        Config.PMT_URL_ENV_VAR: 'url',
        Config.GIT_TOKEN_ENV_VAR: 'gtok',
        Config.GIT_URL_ENV_VAR: 'gurl',
    }
    with patch.dict(os.environ, env):
        c = Config()
        assert c.pmt_token == 'tok'
        assert c.pmt_url == 'url'
        assert c.git_token == 'gtok'
        assert c.git_url == 'gurl'
        assert c.pmt_type == data['pmt-type']
        assert c.vcs_type == data['vcs-type']
        assert c.git_proj == data['git-project']
        assert c.to_do_statuses == data['to-do']
        assert c.in_progress_statuses == data['in-progress']
        assert c.in_review_statuses == data['in-review']
        assert c.done_statuses == data['done']
        assert c.reviewer_field == data['reviewer-field']
        assert c.git_branch_field == data['git-branch-field']
        assert c.current_ticket_script == data['current-ticket']
        assert c.hooks == data['hooks']

def test_hooks_default_empty_dict(tmp_path):
    config_path = tmp_path / "config.json"
    data = make_config_data()
    del data['hooks']
    config_path.write_text(json.dumps(data))
    with patch.dict(os.environ, {Config.CONFIG_FILE: str(config_path)}):
        c = Config()
        assert c.hooks == {} 
