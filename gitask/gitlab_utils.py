import sys

import gitlab

from gitask.config import Config
from gitask.version_control_tool import VCSInterface


def handle_gitlab_errors(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except gitlab.exceptions.GitlabError as e:
            error_message = e.error_message
            if len(error_message) == 1:
                error_message = error_message[0]

            print(error_message)
            sys.exit(1)

    return wrapper


class GitlabUtils(VCSInterface):
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GitlabUtils, cls).__new__(cls)
            cls._instance.__init_gitlab_client()
        return cls._instance

    @handle_gitlab_errors
    def __init_gitlab_client(self):
        config = Config()
        self.gitlab_client = gitlab.Gitlab(config.git_url, private_token=config.git_token)
        self.gitlab_project = self.gitlab_client.projects.get(config.git_proj)

    @handle_gitlab_errors
    def get_user_id_by_name(self, name):
        users = self.gitlab_client.users.list(search=name)
        if users:
            return users[0].id
        else:
            raise ValueError(f"User with name '{name}' not found.")


    @handle_gitlab_errors
    def create_merge_request(self, source_branch, target_branch, title, reviewer):
        mr_data = {
            'source_branch': source_branch,
            'target_branch': target_branch,
            'title': title,
            'reviewer_ids': [self.get_user_id_by_name(reviewer)]
        }
        self.gitlab_project.mergerequests.create(mr_data)
