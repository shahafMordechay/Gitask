import sys

import click
from github import Github, GithubException

from gitask.config.config import Config
from gitask.vcs.version_control_tool import VCSInterface


def handle_github_errors(func):
    """
    Decorator to handle GitHub errors and print meaningful error messages.

    :param func: The function to wrap.
    :return: The wrapped function.
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except GithubException as e:
            # e.data can be a dict or a string (when mocked)
            message = None
            if hasattr(e, 'data'):
                if isinstance(e.data, dict):
                    message = e.data.get('message', str(e))
                else:
                    message = str(e.data)
            else:
                message = str(e)
            click.echo(f"GitHub Error: {message}")
            sys.exit(1)

    return wrapper


class GithubVcs(VCSInterface):
    """
    GithubVcs class implements the VCSInterface for GitHub.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GithubVcs, cls).__new__(cls)
            cls._instance.__init_github_client()
        return cls._instance

    @handle_github_errors
    def __init_github_client(self):
        config = Config()
        self.github_client = Github(config.git_token)
        self.github_repo = self.github_client.get_repo(config.git_proj)

    @handle_github_errors
    def __get_user_by_name(self, name):
        """
        Get a GitHub user by their username.

        :param name: The username to search for
        :return: The GitHub user object
        :raises: ValueError if no user found
        """
        try:
            user = self.github_client.get_user(name)
            return user
        except GithubException as e:
            # 404 means not found, others are generic errors
            if hasattr(e, 'status') and e.status == 404:
                raise ValueError(f"No GitHub user found matching '{name}'")
            raise ValueError(f"Failed to get user by name: {name}")

    @handle_github_errors
    def __get_current_user(self):
        """Get the current GitHub user."""
        return self.github_client.get_user()

    @handle_github_errors
    def create_pull_request(self, source_branch, target_branch, title, reviewer):
        """
        Create a pull request in GitHub.

        :param source_branch: The source branch for the pull request.
        :param target_branch: The target branch for the pull request.
        :param title: The title of the pull request.
        :param reviewer: The reviewer for the pull request.
        :return: The created pull request link.
        """
        # Check if PR already exists
        existing_prs = self.github_repo.get_pulls(state='open', head=source_branch)
        if existing_prs.totalCount > 0:
            pr_url = existing_prs[0].html_url
            click.echo(pr_url)
            raise GithubException(422, {"message": "Pull request already exists"})

        # Create new PR
        pr = self.github_repo.create_pull(
            title=title,
            head=source_branch,
            base=target_branch
        )

        # Set assignee and reviewer
        try:
            pr.add_to_assignees(self.__get_current_user().login)
            reviewer_user = self.__get_user_by_name(reviewer)
            pr.create_review_request(reviewers=[reviewer_user.login])
        except GithubException as e:
            click.echo(pr.html_url)
            raise e

        return pr.html_url
