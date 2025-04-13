from typing import List

from github import Github

from gitask.pmt.project_management_tool import PMToolInterface
from gitask.config.config import Config


class GitHubPmt(PMToolInterface):
    def __init__(self):
        self.config = Config()
        self.github = Github(self.config.pmt_token)
        self.repo = self.github.get_repo(self.config.git_proj)

    def get_user_by_username(self, username: str) -> dict:
        """Not supported for GitHub."""
        raise NotImplementedError("This action is not supported for GitHub")

    def update_ticket_status(self, issue_key: str, status: str) -> None:
        """Update issue state (open/closed)."""
        issue = self.repo.get_issue(int(issue_key))
        issue.edit(state=status)

    def update_git_branch(self, issue_key: str, git_branch_field: str) -> None:
        """Not supported for GitHub."""
        raise NotImplementedError("This action is not supported for GitHub")

    def update_reviewer(self, issue_key: str, reviewer_field: str, user: dict) -> None:
        """Not supported for GitHub."""
        raise NotImplementedError("This action is not supported for GitHub")

    def find_valid_status_transition(self, issue_key: str, target_statuses: List[str]) -> str:
        """Find a valid status transition based on current issue state."""
        issue = self.repo.get_issue(int(issue_key))
        if "closed" in target_statuses and issue.state == "open":
            return "closed"
        elif "open" in target_statuses and issue.state == "closed":
            return "open"
        else:
            raise ValueError(f"Invalid status transition from current status '{issue.state}' for issue '{issue_key}'")

    def get_issue_status(self, issue_key: str) -> str:
        """Get current issue state."""
        issue = self.repo.get_issue(int(issue_key))
        return issue.state 
