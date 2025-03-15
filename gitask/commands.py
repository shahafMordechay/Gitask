import click

from gitask.config.config import Config
from gitask.config.config_utils import setup_autocomplete, interactive_setup
from gitask.pmt.pmt_factory import get_pmt
from gitask.pmt.project_management_tool import PMToolInterface
from gitask.utils import Utils
from gitask.vcs.vcs_factory import get_vcs
from gitask.vcs.version_control_tool import VCSInterface


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

    def move_to_to_do(self):
        """Move the current ticket to To Do status."""
        # Step 1: Get current ticket
        issue_key = self.utils.get_current_ticket()

        # Step 2: Update ticket status
        to_do_status = self.pmt.find_valid_status_transition(issue_key, self.config.to_do_statuses)
        self.pmt.update_ticket_status(issue_key, to_do_status)
        click.echo(f"'{to_do_status}' transition succeeded")

    def move_to_in_progress(self):
        """Move the current ticket to In Progress status."""
        # Step 1: Get current ticket
        issue_key = self.utils.get_current_ticket()

        # Step 2: Update ticket status
        in_progress_status = self.pmt.find_valid_status_transition(issue_key, self.config.in_progress_statuses)
        self.pmt.update_ticket_status(issue_key, in_progress_status)
        click.echo(f"'{in_progress_status}' transition succeeded")

    def move_to_in_review(self, title, reviewer, target_branch, pr_only_flag):
        """
        Move the current ticket to In Review status and create a pull request.

        :param title: The title of the pull request.
        :param reviewer: The username of the reviewer.
        :param target_branch: The target branch for the pull request.
        :param pr_only_flag: Flag to create only the pull request.
        """
        if not pr_only_flag:
            issue_key = self.utils.get_current_ticket()  # Step 1: Get current ticket
            user = self.pmt.get_user_by_username(reviewer)  # Step 2: Get reviewer user object

            # Step 3: Update git branch and reviewer
            git_branch_field = self.config.git_branch_field
            self.pmt.update_git_branch(issue_key, git_branch_field)

            reviewer_field = self.config.reviewer_field
            self.pmt.update_reviewer(issue_key, reviewer_field, user)

            # Step 4: Update ticket status
            in_review_status = self.pmt.find_valid_status_transition(issue_key, self.config.in_review_statuses)
            self.pmt.update_ticket_status(issue_key, in_review_status)
            click.echo(f"'{in_review_status}' transition succeeded.")

        # Step 5: Create MR
        pr_link = self.utils.create_pull_request(self.vcs, title, reviewer, target_branch=target_branch)
        click.echo(f"Successfully created merge request: {pr_link}")

    def move_to_done(self):
        """Move the current ticket to Done status."""
        # Step 1: Get current ticket
        issue_key = self.utils.get_current_ticket()

        # Step 2: Update ticket status
        done_status = self.pmt.find_valid_status_transition(issue_key, self.config.done_statuses)
        self.pmt.update_ticket_status(issue_key, done_status)
        click.echo(f"'{done_status}' transition succeeded.")
