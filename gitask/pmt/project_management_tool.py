from abc import ABC, abstractmethod


class PMToolInterface(ABC):
    """
    Interface for project management tools.
    """

    @abstractmethod
    def update_ticket_status(self, issue_key, status):
        """
        Update the status of a ticket.

        :param issue_key: The key of the issue to update.
        :param status: The new status to set.
        """
        pass

    @abstractmethod
    def find_valid_status_transition(self, issue_key, statuses):
        """
        Check if any of the provided statuses can be applied as a valid transition for the given issue.

        :param issue_key: The key of the issue to check.
        :param statuses: A list of statuses to evaluate.
        :return: The first valid status if a transition is possible.
                 Raises an exception if no valid transition is found.
        """
        pass

    @abstractmethod
    def get_user_by_username(self, username):
        """
        Get a user object by their username.

        :param username: The username of the user to retrieve.
        :return: The user object.
        """
        pass

    @abstractmethod
    def update_git_branch(self, issue_key, git_branch_field):
        """
        Update the git branch field of a ticket.

        :param issue_key: The key of the issue to update.
        :param git_branch_field: The field to update with the current git branch.
        """
        pass

    @abstractmethod
    def update_reviewer(self, issue_key, reviewer_field, user_object):
        """
        Update the reviewer field of a ticket.

        :param issue_key: The key of the issue to update.
        :param reviewer_field: The field to update with the reviewer.
        :param user_object: The user object of the reviewer.
        """
        pass
