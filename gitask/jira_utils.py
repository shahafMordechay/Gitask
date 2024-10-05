import requests
from jira import JIRA

from gitask.config import Config
from gitask.utils import Utils


class JiraUtils:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(JiraUtils, cls).__new__(cls)
            cls._instance.__init_jira_client()
        return cls._instance

    def __init_jira_client(self):
        config = Config()
        self.jira_client = JIRA(server=config.pmt_url, token_auth=config.pmt_token)
        self.api_url = f"{config.pmt_url}/rest/api/2"
        self.token = config.pmt_token

    def update_ticket_status(self, issue_key, status):
        self.jira_client.transition_issue(issue_key, status)

    def get_user_by_username(self, username):
        params = {"username": username}

        users = self.__jira_get_request(params)
        if not users:
            raise ValueError(f"User '{username}' not found")

        return users[0]

    def update_git_branch(self, issue_key, git_branch_field):
        self.jira_client.issue(issue_key).update(fields={git_branch_field: Utils.get_current_git_branch()})

    def update_reviewer(self, issue_key, reviewer_field_id, user):
        self.jira_client.issue(issue_key).update(fields={reviewer_field_id: user})

    def __jira_get_request(self, params=None):
        url = f"{self.api_url}/user/search"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

        if params is None:
            response = requests.get(url, headers=headers)
        else:
            response = requests.get(url, headers=headers, params=params)

        response.raise_for_status()

        return response.json()
