from gitask.config import Config
from gitask.pmt.jira_pmt import JiraPmt


def get_pmt():
    pmt_type = Config().pmt_type

    if pmt_type == "jira":
        return JiraPmt()
    raise ValueError(f"Unsupported PMT type: {pmt_type}")