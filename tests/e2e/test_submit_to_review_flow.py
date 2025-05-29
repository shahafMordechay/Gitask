import subprocess
import sys
import json
import pytest

def test_submit_to_review_flow(tmp_path):
    config_path = tmp_path / "config.json"
    user_inputs = f"""{config_path}\nhttps://jira.company.com\npmt-token\nhttps://gitlab.company.com\ngit-token\nJira\nGitlab\ntest/repo\necho TEST-123\nTo Do,Backlog\nIn Progress\nIn Review\nDone\ncustomfield_12345\ncustomfield_67890\n\n\n\n\n\n\n\n\n\n\n\n"""
    # Run configure
    result = subprocess.run([
        sys.executable, '-m', 'gitask', 'config', 'init'
    ], input=user_inputs, capture_output=True, text=True)
    assert result.returncode == 0
    assert config_path.exists()
    # Run start-working
    result2 = subprocess.run([sys.executable, '-m', 'gitask', 'start-working'], capture_output=True, text=True)
    assert result2.returncode == 0
    # Run submit-to-review (would need mocks for real PMT/VCS, here just check CLI runs)
    result3 = subprocess.run([
        sys.executable, '-m', 'gitask', 'submit-to-review', '-r', 'reviewer', '-b', 'main'
    ], capture_output=True, text=True)
    assert result3.returncode == 0
    # Optionally check output or config file content
    with open(config_path) as f:
        config = json.load(f)
    assert config['pmt-type'] == 'Jira'
    assert config['vcs-type'] == 'Gitlab'
    assert config['git-project'] == 'test/repo' 
