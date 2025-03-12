from abc import ABC, abstractmethod


class VCSInterface(ABC):
    """
    interface for version control systems.
    """

    @abstractmethod
    def create_pull_request(self, source_branch, target_branch, title, reviewer):
        """
        Create a pull request.

        :param source_branch: The source branch for the pull request.
        :param target_branch: The target branch for the pull request.
        :param title: The title of the pull request.
        :param reviewer: The reviewer for the pull request.
        :return: The created pull request link.
        """
        pass
