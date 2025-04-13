from gitask.config.config import Config
from gitask.vcs.gitlab_vcs import GitlabVcs
from gitask.vcs.github_vcs import GithubVcs


def get_vcs():
    vcs_type = Config().vcs_type.lower()

    if vcs_type == "gitlab":
        return GitlabVcs()
    elif vcs_type == "github":
        return GithubVcs()
    raise ValueError(f"Unsupported VCS type: {vcs_type}")
