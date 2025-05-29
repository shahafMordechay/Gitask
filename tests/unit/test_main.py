import pytest
from unittest.mock import patch, MagicMock
import sys
import click
from click.testing import CliRunner

import gitask.main as main_mod

@pytest.fixture(autouse=True)
def patch_sys_exit():
    with patch('sys.exit', side_effect=SystemExit) as mock_exit:
        yield mock_exit


def test_handle_exceptions_decorator_debug(monkeypatch):
    @main_mod.handle_exceptions
    def raise_error():
        raise ValueError("fail")
    ctx = click.Context(main_mod.cli, obj={'DEBUG': True})
    monkeypatch.setattr(click, 'get_current_context', lambda silent=True: ctx)
    with pytest.raises(ValueError):
        raise_error()


def test_handle_exceptions_decorator_no_debug(monkeypatch):
    @main_mod.handle_exceptions
    def raise_error():
        raise ValueError("fail")
    ctx = click.Context(main_mod.cli, obj={'DEBUG': False})
    monkeypatch.setattr(click, 'get_current_context', lambda silent=True: ctx)
    with pytest.raises(SystemExit):
        raise_error()


def test_configure_command():
    with patch.object(main_mod.Commands, 'configure') as mock_configure:
        runner = CliRunner()
        result = runner.invoke(main_mod.configure, ['--auto-complete'])
        assert result.exit_code == 0
        mock_configure.assert_called_once_with(True)


def test_reopen_command():
    mock_instance = MagicMock()
    with patch('gitask.main.Commands', return_value=mock_instance):
        runner = CliRunner()
        result = runner.invoke(main_mod.reopen)
        assert result.exit_code == 0
        mock_instance.move_to_to_do.assert_called_once()


def test_start_working_command():
    mock_instance = MagicMock()
    with patch('gitask.main.Commands', return_value=mock_instance):
        runner = CliRunner()
        result = runner.invoke(main_mod.start_working)
        assert result.exit_code == 0
        mock_instance.move_to_in_progress.assert_called_once()


def test_submit_to_review_command():
    mock_instance = MagicMock()
    with patch('gitask.main.Commands', return_value=mock_instance):
        runner = CliRunner()
        result = runner.invoke(main_mod.submit_to_review, ['-t', 'PR Title', '-r', 'reviewer', '-b', 'dev', '--pr-only'])
        assert result.exit_code == 0
        mock_instance.move_to_in_review.assert_called_once_with('PR Title', 'reviewer', 'dev', True)


def test_done_command():
    mock_instance = MagicMock()
    with patch('gitask.main.Commands', return_value=mock_instance):
        runner = CliRunner()
        result = runner.invoke(main_mod.done)
        assert result.exit_code == 0
        mock_instance.move_to_done.assert_called_once()


def test_cli_debug_flag():
    # Add a dummy command to print debug value
    @main_mod.cli.command('debug-ctx')
    @click.pass_context
    def debug_ctx(ctx):
        click.echo(str(ctx.obj['DEBUG']))
    runner = CliRunner()
    result = runner.invoke(main_mod.cli, ['--debug', 'debug-ctx'])
    assert result.exit_code == 0
    assert 'True' in result.output


def test_cli_command_registration():
    commands = {cmd.name for cmd in main_mod.cli.commands.values()}
    assert {'configure', 'open', 'start-working', 'submit-to-review', 'done'} <= commands 
