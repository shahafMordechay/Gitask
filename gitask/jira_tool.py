from gitask.config import Config
from gitask.jira_utils import JiraUtils
from gitask.project_management_tool import PMToolInterface
from gitask.utils import Utils


class JiraTool(PMToolInterface):
    def __init__(self):
        self.jira_utils = JiraUtils()
        self.config = Config()
        self.utils = Utils()

    def move_to_in_progress(self):
        # Step 1: Get current ticket
        issue_key = self.utils.get_current_ticket()

        # Step 2: Update ticket status
        in_progress_status = self.config.in_progress_status
        self.jira_utils.update_ticket_status(issue_key, in_progress_status)

    def move_to_in_review(self, target_branch, reviewer):
        issue_key = self.utils.get_current_ticket()  # Step 1: Get current ticket
        user = self.jira_utils.get_user_by_username(reviewer)  # Step 2: Get reviewer user object

        # Step 3: Update git branch and reviewer
        git_branch_field = self.config.git_branch_field
        self.jira_utils.update_git_branch(issue_key, git_branch_field)

        reviewer_field = self.config.reviewer_field
        self.jira_utils.update_reviewer(issue_key, reviewer_field, user)

        # Step 4: Update ticket status
        in_review_status = self.config.in_review_status
        self.jira_utils.update_ticket_status(issue_key, in_review_status)

        # Step 5: Create MR
        self.utils.create_merge_request(reviewer, target_branch=target_branch)
