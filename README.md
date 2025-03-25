# Gitask

## Overview

Gitask is a CLI tool that automates issue transition workflows, integrating with version control systems (VCS). It utilizes a user-defined script to extract the relevant issue ID, and ensures seamless task management with minimal manual intervention.


## Features

- **Seamless Issue Transitions**: Automatically move issues between statuses ('To Do' to 'In Progress,' 'In Review,' ‘Done') without manually specifying the issue ID.

- **Automated Workflow Actions**: Handles related actions such as updating issue metadata, assigning reviewers, and creating pull requests to streamline your workflow.

- **Smart Autocompletion**: Supports shell completion for faster command usage.

- **Interactive Configuration**: Set up Gitask with a guided interactive process to configure all necessary settings.


## Installation

```bash
pip install gitask
```

If installation fails try to use a virtual environment:

```bash
python3 -m venv gitask-env
source gitask-env/bin/activate
pip install gitask
```


## Configuration

Gitask uses a combination of environment variables and a JSON configuration file for maximum flexibility and security.

### Environment Variables
| **Variable**         | **Description**                                                     |
|----------------------|---------------------------------------------------------------------|
| `GITASK_CONFIG_PATH` | Path to the configuration file. Defaults to `~/.gitask_config.json` |
| `GITASK_PMT_TOKEN`   | Authentication token for your project management tool               |
| `GITASK_PMT_URL`     | Base URL for your project management tool                           |
| `GITASK_GIT_TOKEN`   | Authentication token for your version control system                |
| `GITASK_GIT_URL`     | Base URL for your version control system                            |

### Configuration File
The configuration file is a JSON file that specifies the integration details for the project management tool and the version control system.

```json
{
  "pmt-type": "jira",
  "vcs-type": "gitlab",
  "git-project": "group/project",
  "current-ticket": "/workspace/my-scripts/get_issue_id.sh",
  "to-do": [
    "Open"
  ],
  "in-progress": [
    "Start working",
    "Back to work"
  ],
  "in-review": [
    "To review"
  ],
  "done": [
    "Resolve"
  ],
  "git-branch-field": "customfield_10001",
  "reviewer-field": "customfield_10101"
}
```

| **Field**          | **Description**                                                                                                                       |
|--------------------|---------------------------------------------------------------------------------------------------------------------------------------|
| `pmt-type`         | Specifies the project management tool being used (e.g., "Jira", "Clickup", "Trello")                                                  |
| `vcs-type`         | Specifies the version control system being used (e.g., "GitLab", "GitHub", "Bitbucket")                                               |
| `git-project`      | The path to the project in your VCS (e.g., "group/project" in GitLab or "owner/repo" in GitHub)                                       |
| `current-ticket`   | Path to the script that extracts the current issue ID from your working environment (see [Issue ID Extraction](#issue-iD-extraction)) |
| `to-do`            | An array of status transition names that lead to your corresponding “To Do” status                                                    |
| `in-progress`      | An array of status transition names that lead to your corresponding “In Progress” status                                              |
| `in-review`        | An array of status transition names that lead to your corresponding “In Review” status                                                |
| `done`             | An array of status transition names that lead to your corresponding “Done” status                                                     |
| `git-branch-field` | The custom issue field ID for storing the git branch name in your PMT (required only if it’s a custom field)                          |
| `reviewer-field`   | The custom issue field ID for storing the reviewer username in your PMT (required only if it’s a custom field)                        |

### Interactive Setup
For a guided configuration experience, use the built-in interactive setup: `gitask configure`.
This process will:
1. Guide you through setting up PMT and VCS connections.
2. Configure custom fields.
3. Define issue ID extraction script.
4. Create the JSON configuration file.
5. Enable shell autocompletion (optional).


## Usage

### Open a Ticket

&ensp; Moves the ticket to "To Do" status.

&ensp; `gitask open`
<br>

### Start Working on an Issue

&ensp; Moves it to "In Progress".

&ensp; `gitask start-working`
<br>

### Submit  for Review

&ensp; Moves it to "In Review".

&ensp; Updates the issue’s “git branch” and “reviewer” fields.

&ensp; Creates a pull request.

&ensp;  `gitask submit-to-review`
<br>

### Mark Issue as Done

&ensp; Marks the issue as “Done".

&ensp; `gitask done`
<br>

### Interactive Configuration

&ensp; Guides you through setting up Gitask step by step.

&ensp; `gitask configure`
<br>

## Supported Integrations

### Project Management Tools

- Jira

### Version Control Systems

- GitLab


## Issue ID Extraction

The current-ticket script should:
1. Output the issue ID according to the current git branch.
   - It can be extracted from the branch name, commit message, or any other relevant source.
2. Have executable permissions.

### Example

```bash
#!/bin/bash
# Extract JIRA issue ID from current Git branch
BRANCH_NAME=$(git rev-parse --abbrev-ref HEAD)
ISSUE=$(echo "$BRANCH_NAME" | grep -o "COMPANY-[0-9]\{5\}")
echo $ISSUE
```

## Troubleshooting

#### 1. ERROR: No matching distribution found for python-gitlab>=5.6.0
   If you encounter this error, run the following command to install the required package:
   ```bash
   pip install --upgrade python-gitlab --index-url https://pypi.org/simple/
   ```
   If you’re working within a virtual environment, ensure that it is activated before running the above command.
   <br>

#### 2. Shell fails to recognize gitask command
   If your shell does not recognize the gitask command after installation, it’s likely because the virtual environment’s bin directory is not in your PATH.<br>
   To fix this, add the path to your virtual environment’s bin directory in your shell profile (e.g., .bashrc, .zshrc):
   ```bash
   export PATH="/path/to/your/virtualenv/bin:$PATH"
   ```
   After making this change, restart your terminal or run `source ~/.zshrc` (or equivalent) to apply the update.


## License

This project is licensed under the MIT License - see the [LICENSE file](https://github.com/shahafMordechay/Gitask/blob/main/LICENSE) for details.


## Contributing

Contributions are welcome! Feel free to submit pull requests or open issues.
1. Fork the repository 
2. Create your feature branch (`git checkout -b username/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin username/amazing-feature`)
5. Open a Pull Request


## Support

For issues, open a GitHub issue or reach out via discussions.
