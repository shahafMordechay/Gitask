import functools

import click

from gitask.config.config import Config
from gitask.config.config_utils import setup_autocomplete, interactive_setup
from gitask.pmt.pmt_factory import get_pmt
from gitask.pmt.project_management_tool import PMToolInterface
from gitask.utils import Utils
from gitask.vcs.vcs_factory import get_vcs
from gitask.vcs.version_control_tool import VCSInterface


def with_hooks(action_name):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            utils = Utils()
            config = Config()
            hooks = config.hooks

            # Pass the command parameters (args and kwargs) to the hook scripts
            command_params = {}
            if args:
                command_params['args'] = list(args)
            if kwargs:
                command_params.update(kwargs)

            if action_name in hooks and 'pre' in hooks[action_name]:
                utils.run_hook_script(hooks[action_name]['pre'], command_params)

            result = func(*args, **kwargs)

            if action_name in hooks and 'post' in hooks[action_name]:
                utils.run_hook_script(hooks[action_name]['post'], command_params)

            return result
        return wrapper
    return decorator

class Commands:
    """
    Commands class to handle all the main commands.
    """

    def __init__(self):
        self.config = Config()
        self.utils = Utils()
        self.pmt: PMToolInterface = get_pmt()
        self.vcs: VCSInterface = get_vcs()


    @staticmethod
    def configure(auto_complete):
        """
        Configure Gitask with the necessary settings.

        This function handles the configuration of Gitask.
        If the `auto_complete` flag is set, it will only set up autocompletion.
        Otherwise, it will run the interactive setup to configure all relevant data for Gitask.

        :param auto_complete: Flag to indicate if only autocompletion should be set up.
        """
        if auto_complete:
            setup_autocomplete()
            return

        interactive_setup()

    @with_hooks('open')
    def move_to_to_do(self):
        """Move the current ticket to To Do status."""
        # Step 1: Get current ticket
        issue_key = self.utils.get_current_ticket()

        # Step 2: Update ticket status
        to_do_status = self.pmt.find_valid_status_transition(issue_key, self.config.to_do_statuses)
        self.pmt.update_ticket_status(issue_key, to_do_status)
        click.echo(f"'{to_do_status}' transition succeeded")

    @with_hooks('start-working')
    def move_to_in_progress(self):
        """Move the current ticket to In Progress status."""

        # Validate that the in progress status is configured
        if self.config.in_progress_status is None or self.config.in_progress_statuses.length == 0:
            raise ValueError("No in progress statuses configured")

        # Step 1: Get current ticket
        issue_key = self.utils.get_current_ticket()

        # Step 2: Update ticket status
        in_progress_status = self.pmt.find_valid_status_transition(issue_key, self.config.in_progress_statuses)
        self.pmt.update_ticket_status(issue_key, in_progress_status)
        click.echo(f"'{in_progress_status}' transition succeeded")

    @with_hooks('submit-to-review')
    def move_to_in_review(self, title, reviewer, target_branch, pr_only_flag):
        """
        Move the current ticket to In Review status and create a pull request.

        :param title: The title of the pull request.
        :param reviewer: The username of the reviewer.
        :param target_branch: The target branch for the pull request.
        :param pr_only_flag: Flag to create only the pull request.
        """
        if not pr_only_flag:
            # Validate that the in review status is configured
            if self.config.in_review_statuses is None or self.config.in_review_statuses.length == 0:
                raise ValueError("No in review statuses configured")
        
            issue_key = self.utils.get_current_ticket()  # Step 1: Get current ticket
            user = self.pmt.get_user_by_username(reviewer)  # Step 2: Get reviewer user object

            # Step 3: Update git branch and reviewer
            if self.config.git_branch_field is not None and self.config.git_branch_field.length > 0:
                self.pmt.update_git_branch(issue_key, self.config.git_branch_field)
                
            if self.config.reviewer_field is not None and self.config.reviewer_field.length > 0:
                self.pmt.update_reviewer(issue_key, self.config.reviewer_field, user)

            # Step 4: Update ticket status
            in_review_status = self.pmt.find_valid_status_transition(issue_key, self.config.in_review_statuses)
            self.pmt.update_ticket_status(issue_key, in_review_status)
            click.echo(f"'{in_review_status}' transition succeeded.")

        # Step 5: Create MR
        self.utils.create_pull_request(self.vcs, title, reviewer, target_branch=target_branch)

    @with_hooks('done')
    def move_to_done(self):
        """Move the current ticket to Done status."""
        # Step 1: Get current ticket
        issue_key = self.utils.get_current_ticket()

        # Step 2: Update ticket status
        done_status = self.pmt.find_valid_status_transition(issue_key, self.config.done_statuses)
        self.pmt.update_ticket_status(issue_key, done_status)
        click.echo(f"'{done_status}' transition succeeded.")
