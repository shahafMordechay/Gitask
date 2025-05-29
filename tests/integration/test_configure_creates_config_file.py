import subprocess
import json
import sys
import pytest

def test_configure_creates_config_file(tmp_path):
    config_path = tmp_path / "config.json"
    user_inputs = f"""{config_path}\nhttps://jira.company.com\npmt-token\nhttps://gitlab.company.com\ngit-token\nJira\nGitlab\ntest/repo\necho TEST-123\nTo Do,Backlog\nIn Progress\nIn Review\nDone\ncustomfield_12345\ncustomfield_67890\n\n\n\n\n\n\n\n\n\n\n\n"""
    result = subprocess.run([
        sys.executable, '-m', 'gitask', 'configure'
    ], input=user_inputs, capture_output=True, text=True)
    assert result.returncode == 0
    assert config_path.exists()
    with open(config_path) as f:
        config = json.load(f)
    assert config['pmt-type'] == 'Jira'
    assert config['vcs-type'] == 'Gitlab'
    assert config['git-project'] == 'test/repo' 
