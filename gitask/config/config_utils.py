import os
import sys

import click

from gitask.config.config import Config
from gitask.utils import save_json_to_file

GITASK_ENV_PATH = os.path.expanduser("~/.config/gitask/gitask_env")
SHELL_CONFIG_FILES = {
    "bash": "~/.bashrc",
    "zsh": "~/.zshrc",
    "fish": "~/.config/fish/config.fish",
}

def interactive_setup():
    """
    Interactive setup to configure all relevant data for Gitask.

    This setup will guide the user through configuring Gitask, including setting environment variables,
    creating a config file, and setting up autocompletion.
    """
    click.echo("\n✨ Welcome to Gitask Setup! ✨")
    click.echo("This setup will generate a configuration file and configure environment variables.\n")

    env_vars = {}

    # Config file path
    config_file_path = click.prompt("📂 Enter the config file path", default=Config.DEFAULT_CONFIG_FILE)
    config_file_path = os.path.expanduser(config_file_path)
    env_vars[Config.CONFIG_FILE] = config_file_path

    # Environment variables
    click.echo("\n🔧 Setting up environment variables:")
    env_vars[Config.PMT_URL_ENV_VAR] = click.prompt("  🔹 Project management tool URL (e.g., https://jira.company.com)")
    env_vars[Config.PMT_TOKEN_ENV_VAR] = click.prompt("  🔹 Project management tool API token")
    env_vars[Config.GIT_URL_ENV_VAR] = click.prompt("  🔹 Git server URL (e.g., https://gitlab.company.com)")
    env_vars[Config.GIT_TOKEN_ENV_VAR] = click.prompt("  🔹 Git personal access token")

    # Config file setup
    click.echo("\n⚙️ Configuring Gitask settings:")
    config = {}
    config[Config.PMT_TYPE_PROP_NAME] = click.prompt("  🔹 Project management tool type (Jira)")
    config[Config.VCS_TYPE_PROP_NAME] = click.prompt("  🔹 Version control system type (Gitlab)")
    config[Config.GIT_PROJECT_PROP_NAME] = click.prompt("  🔹 Git project name or namespace (e.g., user/repository or group/project)")
    config[Config.CURRENT_TICKET_PROP_NAME] = click.prompt("  🔹 Script to get the current issue (e.g., /scripts/get_current_issue.sh)")
    config[Config.TO_DO_PROP_NAME] = click.prompt("  🔹 To-Do statuses (comma-separated, e.g., To do,Backlog)").split(",")
    config[Config.TO_DO_PROP_NAME] = [status.strip() for status in config.get(Config.TO_DO_PROP_NAME)]
    config[Config.IN_PROGRESS_PROP_NAME] = click.prompt("  🔹 In-Progress statuses (comma-separated, e.g., In Progress,Doing)").split(",")
    config[Config.IN_PROGRESS_PROP_NAME] = [status.strip() for status in config.get(Config.IN_PROGRESS_PROP_NAME)]
    config[Config.IN_REVIEW_PROP_NAME] = click.prompt("  🔹 In-Review statuses (comma-separated, e.g., In Review,Code Review)").split(",")
    config[Config.IN_REVIEW_PROP_NAME] = [status.strip() for status in config.get(Config.IN_REVIEW_PROP_NAME)]
    config[Config.DONE_PROP_NAME] = click.prompt("  🔹 Done statuses (comma-separated, e.g., Done,Complete)").split(",")
    config[Config.DONE_PROP_NAME] = [status.strip() for status in config.get(Config.DONE_PROP_NAME)]
    config[Config.GIT_BRANCH_FIELD_PROP_NAME] = click.prompt("  🔹 Git branch metadata field in the Project management tool (e.g., customfield_12345)")
    config[Config.REVIEWER_FIELD_PROP_NAME] = click.prompt("  🔹 Reviewer metadata field in the Project management tool (e.g., customfield_12345)")

    # Save configuration and environment variables
    _set_env_variables(env_vars)
    save_json_to_file(config_file_path, config)
    click.echo("\n✅ Configuration saved!")

    # Autocompletion setup
    setup_autocomplete()

    shell_config = os.path.expanduser(SHELL_CONFIG_FILES[get_shell_type()])
    click.secho("\n🎯 Setup complete!", fg="green", bold=True)
    click.secho("\n❗ IMPORTANT: To start using Gitask, restart your terminal or run:", fg="yellow", bold=True)
    click.secho(f"   source {shell_config}\n", fg="yellow", bold=True)

def setup_autocomplete():
    """
    Set up autocompletion for the Gitask CLI.

    This function detects the user's shell and adds the necessary autocompletion
    command to the shell's configuration file. It supports bash, zsh, and fish shells.
    """
    autocomplete_command_by_shell = {
        "bash": 'eval "$(_GITASK_COMPLETE=bash_source gitask)"',
        "zsh": 'eval "$(_GITASK_COMPLETE=zsh_source gitask)"',
        "fish": '_GITASK_COMPLETE=fish_source gitask | source',
    }

    shell = get_shell_type()
    autocomplete_command = autocomplete_command_by_shell[shell]

    click.echo("\n🔹 Gitask CLI supports autocompletion!")
    click.echo("   To enable autocompletion permanently, we need to update your shell configuration file.")
    click.echo("   This will add the following line to your shell profile:")
    click.echo(f"      {autocomplete_command}")

    if not click.confirm("\n⚡ Would you like to enable autocompletion?"):
        click.echo("\n❌ Autocompletion was NOT enabled.")
        click.echo("ℹ️  You can enable autocompletion later by running: `gitask configure --auto-complete`")
        click.echo("   or by adding the following line to your shell profile:")
        click.echo(f"      {autocomplete_command}")
        return

    shell_config = os.path.expanduser(SHELL_CONFIG_FILES[shell])
    with open(shell_config, "r+") as f:
        content = f.read()
        if autocomplete_command not in content:
            f.write(f"\n{autocomplete_command}\n")

    click.echo("\n✅ Autocompletion enabled!")

def _set_env_variables(env_vars):
    """Save environment variables to the Gitask env file and update the shell profile."""
    env_file_path = os.path.expanduser(GITASK_ENV_PATH)
    os.makedirs(os.path.dirname(env_file_path), exist_ok=True)

    # Write environment variables to gitask_env
    with open(env_file_path, "w") as f:
        for key, value in env_vars.items():
            f.write(f'export {key}="{value.strip()}"\n')

    # Ensure the file is sourced in .bashrc/.zshrc/.profile
    shell = get_shell_type()
    shell_path = os.path.expanduser(SHELL_CONFIG_FILES[shell])
    with open(shell_path, "r+") as f:
        content = f.read()
        if f"source {env_file_path}" not in content:
            f.write(f'\n# Load Gitask environment variables\nsource {env_file_path}\n')

def get_shell_type():
    shell = os.getenv("SHELL", "")

    if "bash" in shell:
        return "bash"
    elif "zsh" in shell:
        return "zsh"
    elif "fish" in shell:
        return "fish"
    else:
        sys.exit(1)
