import sys
import pytest
from unittest.mock import patch, MagicMock
import subprocess

def test_move_to_in_review_creates_pr_and_updates_ticket(tmp_path):
    """Test that moving a ticket to In Review creates a PR and updates the ticket."""
    with patch('gitask.commands.Config') as mock_config_class, \
         patch('gitask.commands.Utils') as mock_utils_class, \
         patch('gitask.commands.get_pmt') as mock_get_pmt, \
         patch('gitask.commands.get_vcs') as mock_get_vcs:
        
        # Setup mocks
        mock_config = MagicMock()
        mock_config.in_review_statuses = ['In Review']
        mock_config.git_branch_field = 'branch_field'
        mock_config.reviewer_field = 'reviewer_field'
        mock_config_class.return_value = mock_config
        
        mock_utils = MagicMock()
        mock_utils.get_current_ticket.return_value = 'TICKET-3'
        mock_utils_class.return_value = mock_utils
        
        mock_pmt = MagicMock()
        mock_pmt.find_valid_status_transition.return_value = 'In Review'
        mock_pmt.get_user_by_username.return_value = {'username': 'reviewer'}
        mock_get_pmt.return_value = mock_pmt
        
        mock_vcs = MagicMock()
        mock_vcs.create_pull_request.return_value = {'url': 'https://github.com/pr/1'}
        mock_get_vcs.return_value = mock_vcs

        # Run the command
        result = subprocess.run([
            sys.executable, '-m', 'gitask', 'submit-to-review', '-r', 'reviewer', '-b', 'main'
        ], capture_output=True, text=True)

        # Verify the command executed successfully
        assert result.returncode == 0

        # Verify the mocks were called correctly
        mock_utils.get_current_ticket.assert_called_once()
        mock_pmt.find_valid_status_transition.assert_called_once_with('TICKET-3', 'In Review')
        mock_pmt.get_user_by_username.assert_called_once_with('reviewer')
        mock_vcs.create_pull_request.assert_called_once()
        mock_pmt.update_ticket_status.assert_called_once_with('TICKET-3', 'In Review')
        mock_pmt.update_ticket_fields.assert_called_once() 
