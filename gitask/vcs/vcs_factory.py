from gitask.config.config import Config
from gitask.vcs.gitlab_vcs import GitlabVcs


def get_vcs():
    vcs_type = Config().vcs_type.lower()

    if vcs_type == "gitlab":
        return GitlabVcs()
    raise ValueError(f"Unsupported VCS type: {vcs_type}")