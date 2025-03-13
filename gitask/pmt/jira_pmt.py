import json
import sys

import requests
from jira import JIRA, JIRAError

from gitask.config.config import Config
from gitask.pmt.project_management_tool import PMToolInterface
from gitask.utils import Utils


def handle_jira_errors(func):
    """
    Decorator to handle JIRA errors and print meaningful error messages.

    :param func: The function to wrap.
    :return: The wrapped function.
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except JIRAError as e:
            try:
                # Print the error messages and errors from the response JSON
                response_json = e.response.json()
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

            # print the error text if the error messages and errors attributes are not present
            print(e.text)
            sys.exit(1)

    return wrapper


class JiraPmt(PMToolInterface):
    """
    JiraPmt class implements the PMToolInterface for JIRA.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(JiraPmt, cls).__new__(cls)
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
        """
        Update the status of a JIRA ticket.

        :param issue_key: The key of the issue to update.
        :param status: The new status to set.
        """
        self.jira_client.transition_issue(issue_key, status)

    @handle_jira_errors
    def find_valid_status_transition(self, issue_key, statuses):
        """
        Check if any of the provided statuses can be applied as a valid transition for the given issue.

        :param issue_key: The key of the issue to check.
        :param statuses: A list of statuses to evaluate.
        :return: The first valid status if a transition is possible.
                 Raises an exception if no valid transition is found.
        """
        transitions = self.jira_client.transitions(issue_key)
        valid_transitions = [transition["name"] for transition in transitions if transition["name"] in statuses]

        if not valid_transitions:
            # noinspection PyUnresolvedReferences
            current_status = self.jira_client.issue(issue_key).fields.status.name
            raise ValueError(f"Invalid status transition from current status '{current_status}' for issue '{issue_key}'")

        return valid_transitions[0]

    @handle_jira_errors
    def get_user_by_username(self, username):
        """
        Get a JIRA user object by their username.

        :param username: The username of the user to retrieve.
        :return: The user object.
        """
        params = {"username": username}
        users = self.__jira_get_request(params)
        if not users:
            raise ValueError(f"User '{username}' not found")

        return users[0]

    @handle_jira_errors
    def update_git_branch(self, issue_key, git_branch_field):
        """
        Update the git branch field of a JIRA ticket.

        :param issue_key: The key of the issue to update.
        :param git_branch_field: The field to update with the current git branch.
        """
        self.jira_client.issue(issue_key).update(fields={git_branch_field: Utils.get_current_git_branch()})

    @handle_jira_errors
    def update_reviewer(self, issue_key, reviewer_field_id, user):
        """
        Update the reviewer field of a JIRA ticket.

        :param issue_key: The key of the issue to update.
        :param reviewer_field_id: The field to update with the reviewer.
        :param user: The user object of the reviewer.
        """
        self.jira_client.issue(issue_key).update(fields={reviewer_field_id: user})

    def __jira_get_request(self, params=None):
        """
        Make a GET request to the JIRA API.

        :param params: The query parameters for the request.
        :return: The JSON response from the API.
        """
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
