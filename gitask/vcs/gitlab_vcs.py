import json
import sys

import click
import gitlab

from gitask.config.config import Config
from gitask.vcs.version_control_tool import VCSInterface


def handle_gitlab_errors(func):
    """
    Decorator to handle GitLab errors and print meaningful error messages.

    :param func: The function to wrap.
    :return: The wrapped function.
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except gitlab.exceptions.GitlabError as e:
            error_message = e.error_message
            if len(error_message) == 1:
                error_message = error_message[0]

            click.echo(error_message)
            sys.exit(1)

    return wrapper


class GitlabVcs(VCSInterface):
    """
    GitlabVcs class implements the VCSInterface for GitLab.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GitlabVcs, cls).__new__(cls)
            cls._instance.__init_gitlab_client()
        return cls._instance


    @handle_gitlab_errors
    def __init_gitlab_client(self):
        config = Config()
        self.gitlab_client = gitlab.Gitlab(config.git_url, private_token=config.git_token)
        self.gitlab_project = self.gitlab_client.projects.get(config.git_proj)


    @handle_gitlab_errors
    def __get_user_id_by_name(self, name):
        users = self.gitlab_client.users.list(search=name)
        if users:
            return users[0].id
        else:
            raise ValueError(f"User with name '{name}' not found.")


    @handle_gitlab_errors
    def create_pull_request(self, source_branch, target_branch, title, reviewer):
        """
        Create a merge request in GitLab.

        :param source_branch: The source branch for the merge request.
        :param target_branch: The target branch for the merge request.
        :param title: The title of the merge request.
        :param reviewer: The reviewer for the merge request.
        :return: The created merge request link.
        """
        mr_data = {
            'source_branch': source_branch,
            'target_branch': target_branch,
            'title': title,
            'reviewer_ids': [self.__get_user_id_by_name(reviewer)]
        }

        try:
            merge_request = self.gitlab_project.mergerequests.create(mr_data)
        except gitlab.exceptions.GitlabError as e:
            try:
                mrs = self.gitlab_project.mergerequests.list(source_branch=source_branch, state="opened")
                click.echo(mrs[0].web_url)
                raise e
            except (json.JSONDecodeError, TypeError):
                raise e

        return merge_request.web_url
