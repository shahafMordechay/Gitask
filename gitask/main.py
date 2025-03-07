import subprocess
import click

from gitask.jira_tool import JiraTool
from gitask.project_management_tool import PMToolInterface

# Create an instance of PMDao to handle the main logic
pm_tool: PMToolInterface = JiraTool()


@click.command()
def start_working():
    """Move the current ticket to In Progress."""
    pm_tool.move_to_in_progress()


@click.command()
@click.option('--branch', required=False, help='Target branch for merge request.')
@click.option('--reviewer', required=True, help='Username of the reviewer.')
def submit_to_review(branch, reviewer):
    """Submit the current ticket to In Review and create a merge request."""
    pm_tool.move_to_in_review(branch, reviewer)


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
