import subprocess

def test_cli_help():
    result = subprocess.run(['gitask', '--help'], capture_output=True, text=True)
    assert result.returncode == 0
    assert 'Usage:' in result.stdout 
