import json
import sys
import requests
from jira import JIRA, JIRAError

from gitask.config import Config
from gitask.utils import Utils


def handle_jira_errors(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except JIRAError as e:
            try:
                response_json = e.response.json()  # Parse JSON response
                error_messages = response_json.get("errorMessages", [])
                errors = response_json.get("errors", {})

                if error_messages:
                    print("\n".join(error_messages))

                if errors:
                    for field, message in errors.items():
                        print(f"{field}: {message}")

                sys.exit(1)
            except (json.JSONDecodeError, TypeError, AttributeError):
                pass

            print(e.text)
            sys.exit(1)

    return wrapper


class JiraUtils:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(JiraUtils, cls).__new__(cls)
            cls._instance.__init_jira_client()
        return cls._instance

    @handle_jira_errors
    def __init_jira_client(self):
        config = Config()
        self.jira_client = JIRA(server=config.pmt_url, token_auth=config.pmt_token)
        self.api_url = f"{config.pmt_url}/rest/api/2"
        self.token = config.pmt_token

    @handle_jira_errors
    def update_ticket_status(self, issue_key, status):
        self.jira_client.transition_issue(issue_key, status)

    @handle_jira_errors
    def get_user_by_username(self, username):
        params = {"username": username}

        users = self.__jira_get_request(params)
        if not users:
            raise ValueError(f"User '{username}' not found")

        return users[0]

    @handle_jira_errors
    def update_git_branch(self, issue_key, git_branch_field):
        self.jira_client.issue(issue_key).update(fields={git_branch_field: Utils.get_current_git_branch()})

    @handle_jira_errors
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
