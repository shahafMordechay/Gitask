import subprocess
from email.policy import default

import click

from gitask.commands import Commands


@click.command()
def start_working():
    """Move the current ticket to In Progress."""
    Commands().move_to_in_progress()


@click.command()
@click.option('--title', default='',  help='Title of the pull request.')
@click.option('--reviewer', required=True, help='Username of the reviewer.')
@click.option('--branch', required=False, help='Target branch for pull request.')
def submit_to_review(title, reviewer, branch):
    """Submit the current ticket to In Review and create a pull request."""
    Commands().move_to_in_review(title, reviewer, branch)


@click.group()
def cli():
    # enable the use of subcommands
    pass


cli.add_command(start_working)
cli.add_command(submit_to_review)

if __name__ == '__main__':
    try:
        cli()
    except ValueError as ve:
        click.echo(f"Configuration Error: {str(ve)}", err=True)
    except subprocess.CalledProcessError as e:
        click.echo(f"Subprocess Error: {str(e)}", err=True)
    except Exception as e:
        click.echo(f"An unexpected error occurred: {str(e)}", err=True)
