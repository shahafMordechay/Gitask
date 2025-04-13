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
            click.echo(f"GitHub Error: {e.data.get('message', str(e))}")
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
        # First try exact username match
        try:
            user = self.github_client.get_user(name)
            return user
        except GithubException.UnknownObjectException:
            raise ValueError(f"No GitHub user found matching '{name}'")
        except GithubException:
            raise ValueError(f"Failed to get user by name: {name}")

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
        try:
            # Check if PR already exists
            existing_prs = self.github_repo.get_pulls(state='open', head=source_branch)
            if existing_prs.totalCount > 0:
                click.echo(existing_prs[0].html_url)
                raise GithubException(422, {"message": "Pull request already exists"})

            # Create new PR
            pr = self.github_repo.create_pull(
                title=title,
                body="",  # Optional: Add description
                head=source_branch,
                base=target_branch
            )

            # Add reviewer
            reviewer_user = self.__get_user_by_name(reviewer)
            pr.create_review_request(reviewers=[reviewer_user.login])

            return pr.html_url

        except GithubException as e:
            if e.status == 422 and "pull request already exists" in str(e).lower():
                existing_prs = self.github_repo.get_pulls(state='open', head=source_branch)
                if existing_prs.totalCount > 0:
                    click.echo(existing_prs[0].html_url)
            raise e
