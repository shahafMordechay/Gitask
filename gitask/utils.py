import json
import os
import subprocess

from gitask.config.config import Config


def save_json_to_file(file_path, data):
    """Save the configuration JSON data to the config file."""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)


class Utils:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Utils, cls).__new__(cls)
            cls._instance.__init__()
        return cls._instance


    def __init__(self):
        self.config = Config()


    @staticmethod
    def get_current_git_branch():
        """Get the current git branch name."""
        return subprocess.check_output("git rev-parse --abbrev-ref HEAD", shell=True).strip().decode('utf-8')


    def get_current_ticket(self):
        """Get the current ticket using the configured script."""
        current_ticket_script = self.config.current_ticket_script

        if current_ticket_script is None:
            raise ValueError("No current ticket script defined in the configuration.")

        return subprocess.check_output(current_ticket_script, shell=True).strip().decode('utf-8')


    def create_pull_request(self, vcs_object, title, reviewer, cur_branch=None, target_branch="master"):
        """
        Create a pull request.

        :param vcs_object: The version control system object.
        :param title: The pull request title.
        :param reviewer: The reviewer for the pull request.
        :param cur_branch: The current branch name.
        :param target_branch: The target branch name.
        :return The pull request link.
        """
        if cur_branch is None:
            cur_branch = self.get_current_git_branch()

        if title == "":
            title = f"Merge {cur_branch} into {target_branch}"

        return vcs_object.create_pull_request(cur_branch, target_branch, title, reviewer)
