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


@click.command(name='start-working')
@handle_exceptions
def start_working():
    """Move the current ticket to In Progress."""
    Commands().move_to_in_progress()


@click.command(name='submit-to-review')
@click.option('--title', default='',  help='Title of the pull request.')
@click.option('--reviewer', required=True, help='Username of the reviewer.')
@click.option('--branch', required=False, help='Target branch for pull request.')
@handle_exceptions
def submit_to_review(title, reviewer, branch):
    """Submit the current ticket to In Review and create a pull request."""
    Commands().move_to_in_review(title, reviewer, branch)


@click.group(context_settings={"max_content_width": 120})
def cli():
    # enable the use of subcommands
    pass


cli.add_command(start_working)
cli.add_command(submit_to_review)

if __name__ == '__main__':
    cli()
