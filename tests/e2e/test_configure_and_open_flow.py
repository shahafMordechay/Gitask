import subprocess
import sys
import json
import pytest
import os

def test_configure_and_open_flow(tmp_path):
    config_path = tmp_path / "config.json"
    user_inputs = f"""{config_path}\nhttps://jira.company.com\npmt-token\nhttps://gitlab.company.com\ngit-token\nJira\nGitlab\ntest/repo\necho TEST-123\nTo Do,Backlog\nIn Progress\nIn Review\nDone\ncustomfield_12345\ncustomfield_67890\n\n\n\n\n\n\n\n\n\n\n\n"""
    # Run configure
    result = subprocess.run([
        'gitask', 'configure'
    ], input=user_inputs, capture_output=True, text=True, env={**os.environ, 'GITASK_CONFIG_PATH': str(config_path)})
    assert result.returncode == 0
    assert config_path.exists()
    # Run open (would need mocks for real PMT/VCS, here just check CLI runs)
    result2 = subprocess.run(['gitask', 'open'], capture_output=True, text=True, env={**os.environ, 'GITASK_CONFIG_PATH': str(config_path)})
    assert result2.returncode == 0
    # Optionally check output or config file content
    with open(config_path) as f:
        config = json.load(f)
    assert config['pmt-type'] == 'Jira'
    assert config['vcs-type'] == 'Gitlab'
    assert config['git-project'] == 'test/repo' 
