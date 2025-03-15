import json
import os


class Config:
    CONFIG_FILE = "GITASK_CONFIG_PATH"
    DEFAULT_CONFIG_FILE = "~/.config/gitask/config.json"
    PMT_TOKEN_ENV_VAR = "GITASK_PMT_TOKEN"
    PMT_URL_ENV_VAR = "GITASK_PMT_URL"
    GIT_TOKEN_ENV_VAR = "GITASK_GIT_TOKEN"
    GIT_URL_ENV_VAR = "GITASK_GIT_URL"
    PMT_TYPE_PROP_NAME = "pmt-type"
    VCS_TYPE_PROP_NAME = "vcs-type"
    GIT_PROJECT_PROP_NAME = "git-project"
    TO_DO_PROP_NAME = "to-do"
    IN_PROGRESS_PROP_NAME = "in-progress"
    IN_REVIEW_PROP_NAME = "in-review"
    DONE_PROP_NAME = "done"
    REVIEWER_FIELD_PROP_NAME = "reviewer-field"
    GIT_BRANCH_FIELD_PROP_NAME = "git-branch-field"
    CURRENT_TICKET_PROP_NAME = "current-ticket"


    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance.__load_config()
        return cls._instance

    def __load_config(self):
        """Load configuration from the config file or environment variables."""
        config_path = os.getenv(Config.CONFIG_FILE, os.path.expanduser(Config.DEFAULT_CONFIG_FILE))

        try:
            with open(config_path, 'r') as config_file:
                self.config_data = json.load(config_file)
        except FileNotFoundError:
            print(f"Error: Configuration file not found at {config_path}")
            self.config_data = {}  # Set to an empty dict to avoid attribute errors
        except json.JSONDecodeError:
            print("Error: Configuration file is not a valid JSON.")
            self.config_data = {}

    @property
    def pmt_token(self):
        return os.getenv(Config.PMT_TOKEN_ENV_VAR)

    @property
    def pmt_url(self):
        return os.getenv(Config.PMT_URL_ENV_VAR)

    @property
    def pmt_type(self):
        return self.config_data.get(Config.PMT_TYPE_PROP_NAME)

    @property
    def vcs_type(self):
        return self.config_data.get(Config.VCS_TYPE_PROP_NAME)

    @property
    def git_token(self):
        return os.getenv(Config.GIT_TOKEN_ENV_VAR)

    @property
    def git_url(self):
        return os.getenv(Config.GIT_URL_ENV_VAR)

    @property
    def git_proj(self):
        return self.config_data.get(Config.GIT_PROJECT_PROP_NAME)

    @property
    def to_do_statuses(self):
        return self.config_data.get(Config.TO_DO_PROP_NAME)

    @property
    def in_progress_statuses(self):
        return self.config_data.get(Config.IN_PROGRESS_PROP_NAME)

    @property
    def in_review_statuses(self):
        return self.config_data.get(Config.IN_REVIEW_PROP_NAME)

    @property
    def done_statuses(self):
        return self.config_data.get(Config.DONE_PROP_NAME)

    @property
    def reviewer_field(self):
        return self.config_data.get(Config.REVIEWER_FIELD_PROP_NAME)

    @property
    def git_branch_field(self):
        return self.config_data.get(Config.GIT_BRANCH_FIELD_PROP_NAME)

    @property
    def current_ticket_script(self):
        return self.config_data.get(Config.CURRENT_TICKET_PROP_NAME)
