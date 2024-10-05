import subprocess

from gitask.config import Config
from gitask.gitlab_utils import GitlabUtils
from gitask.version_control_tool import VCSInterface


class Utils:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Utils, cls).__new__(cls)
            cls._instance.__init__()
            cls._instance.__init_version_control_tool()
        return cls._instance


    def __init__(self):
        self.config = Config()


    def __init_version_control_tool(self):
        if self.config.git_repo_type == "gitlab":
            self.vcs: VCSInterface = GitlabUtils()
        else:
            raise ValueError("Unsupported version control tool")


    def get_current_ticket(self):
        current_ticket_script = self.config.current_ticket_script

        if current_ticket_script is None:
            raise ValueError("No current ticket script defined in the configuration.")

        return subprocess.check_output(current_ticket_script, shell=True).strip().decode('utf-8')


    @staticmethod
    def get_current_git_branch():
        return subprocess.check_output("git rev-parse --abbrev-ref HEAD", shell=True).strip().decode('utf-8')


    def create_merge_request(self, reviewer, cur_branch=None, target_branch="master", message=""):
        if cur_branch is None:
            cur_branch = self.get_current_git_branch()

        if message == "":
            message = f"Merge {cur_branch} into {target_branch}"

        return self.vcs.create_merge_request(cur_branch, target_branch, message, reviewer)
