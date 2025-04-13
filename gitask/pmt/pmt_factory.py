from gitask.config.config import Config
from gitask.pmt.github_pmt import GitHubPmt
from gitask.pmt.jira_pmt import JiraPmt
from gitask.pmt.project_management_tool import PMToolInterface


def get_pmt() -> PMToolInterface:
    """
    Get the appropriate PMT implementation based on the configuration.
    :return: The PMT implementation.
    """
    pmt_type = Config().pmt_type.lower()
    
    if pmt_type == "jira":
        return JiraPmt()
    elif pmt_type == "github":
        return GitHubPmt()
    else:
        raise ValueError(f"Unsupported PMT type: {pmt_type}")
