import functools
import subprocess

import click

from gitask.commands import Commands


def handle_exceptions(func):
    """Decorator to handle exceptions and print user-friendly error messages."""
    @functools.wraps(func) # To preserve Click's metadata
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except subprocess.CalledProcessError as e:
            click.echo(f"Subprocess Error: {str(e)}", err=True)
        except Exception as e:
            click.echo(str(e), err=True)
    return wrapper


@click.command(name='configure')
@click.option('--auto-complete', is_flag=True, required=False,  help='Setup gitask autocompletion.')
@handle_exceptions
def configure(auto_complete):
    """Configure Gitask with the necessary settings."""
    Commands.configure(auto_complete)


@click.command(name='open')
@handle_exceptions
def reopen():
    """Move the current ticket to To Do status."""
    Commands().move_to_to_do()


@click.command(name='start-working', short_help='Move the current ticket to In Progress status.')
@handle_exceptions
def start_working():
    """Move the current ticket to In Progress status."""
    Commands().move_to_in_progress()


@click.command(name='submit-to-review', short_help='Submit the current ticket to In Review and create a pull request.')
@click.option('-t', '--title', default='',  help='Title of the pull request.')
@click.option('-r', '--reviewer', required=True, help='Username of the reviewer.')
@click.option('-b', '--branch', required=False, help='Target branch for pull request.')
@click.option('--pr-only', '--pull-request-only', is_flag=True, required=False, help='Create only the pull request.')
@handle_exceptions
def submit_to_review(title, reviewer, branch, pr_only):
    """Submit the current ticket to In Review and create a pull request."""
    Commands().move_to_in_review(title, reviewer, branch, pr_only)


@click.command(name='done')
@handle_exceptions
def done():
    """Move the current ticket to Done status."""
    Commands().move_to_done()


@click.group(context_settings={"max_content_width": 120})
def cli():
    # enable the use of subcommands
    pass


cli.add_command(configure)
cli.add_command(reopen)
cli.add_command(start_working)
cli.add_command(submit_to_review)
cli.add_command(done)

if __name__ == '__main__':
    cli()
