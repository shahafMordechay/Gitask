# Jira Workflow CLI

A command-line tool that simplifies ticket transitions by automating all necessary tasks associated with each stage.
The tool utilizes Git, using the current branch to update the relevant ticket and create merge requests when required.

## Features

- **`start-working`**: Moves the current Jira ticket to "In Progress" status.
- **`submit-to-review`**: Moves the current Jira ticket to "In Review" status, assigns a reviewer, and creates a merge request.

## Requirements

- Python 3.x
- Jira account and API access
- [Jira Python API](https://pypi.org/project/jira/)

## Installation

1. Clone this repository:

   ```bash
   git clone https://github.com/shahafMordechay/gira.git
   cd gira
2. Install the required Python dependencies:

   ```bash
   pip install -r requirements.txt
3. Install the package:

   ```bash
   pip install .
## Configuration

To use this tool, you need to set up a configuration file and certain environment variables.

### Environment Variables

1.	GIRA_AUTH_TOKEN: Your Jira API token. This token is used to authenticate requests to the Jira API. You can create a token from your Jira account settings.
2.	GIRA_URL: Your Jira base URL (e.g., https://yourcompany.atlassian.net).
3.	GIRA_CONFIG_PATH (optional): Define a custom path for the config file. If not set, it defaults to ~/gira_config.json.

### gira_config.json

The configuration file should be named gira_config.json and placed either in the home directory (~/gira_config.json) or in a custom directory if you define the GIRA_CONFIG_PATH environment variable.

Here’s a sample configuration file:
   ```json
   {
   "in-progress": "In Development",
   "in-review": "Pending Review",
   "reviewer-field": "customfield_12345",
   "create-mr": "/path/to/create-merge-request.sh",
   "current-ticket": "/path/to/get-current-ticket.sh"
   }
   ```

*	in-progress: Your Jira status name for tickets in progress.
* in-review: Your Jira status name for tickets in review.
*	reviewer-field: The custom field ID for the reviewer in Jira.
*	create-mr: Path to the script that creates a merge request.
*	current-ticket: The path to a script that returns the ID of the current Jira ticket you are working on.
	                If this field is not provided, the user will need to supply the ticket ID when executing the commands.                  

## Usage

Once the tool is installed and configured, you can use the following commands from your terminal:

### start-working

Transitions the current Jira ticket to the “In Progress” status:
  ```bash
  start-working [TICKET_ID]
  ```

### submit-to-review

Transitions the current Jira ticket to “In Review”, updates the reviewer field, and creates a merge request:
  ```bash
  submit-to-review --target-branch <branch-name> --reviewer <reviewer-username>  [TICKET_ID]
  ```
Example:
  ```bash
  submit-to-review --target-branch feature-branch --reviewer johndoe TASK-1234
  ```

## Development

If you are contributing to this project or making local modifications:
  1.	After making changes, reinstall the package locally: **`pip install .`**
  2.	Run tests to ensure everything works as expected.

## License

This project is licensed under the MIT License. See the LICENSE file for more information.
