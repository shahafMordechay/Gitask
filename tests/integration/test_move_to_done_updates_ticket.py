import sys
import pytest
from unittest.mock import patch, MagicMock
import subprocess

def test_move_to_done_updates_ticket(tmp_path):
    """Test that moving a ticket to Done updates the ticket correctly."""
    with patch('gitask.commands.Config') as mock_config_class, \
         patch('gitask.commands.Utils') as mock_utils_class, \
         patch('gitask.commands.get_pmt') as mock_get_pmt:
        
        # Setup mocks
        mock_config = MagicMock()
        mock_config.done_statuses = ['Done']
        mock_config_class.return_value = mock_config
        
        mock_utils = MagicMock()
        mock_utils.get_current_ticket.return_value = 'TICKET-4'
        mock_utils_class.return_value = mock_utils
        
        mock_pmt = MagicMock()
        mock_pmt.find_valid_status_transition.return_value = 'Done'
        mock_get_pmt.return_value = mock_pmt

        # Run the command
        result = subprocess.run([
            sys.executable, '-m', 'gitask', 'done'
        ], capture_output=True, text=True)

        # Verify the command executed successfully
        assert result.returncode == 0

        # Verify the mocks were called correctly
        mock_utils.get_current_ticket.assert_called_once()
        mock_pmt.find_valid_status_transition.assert_called_once_with('TICKET-4', 'Done')
        mock_pmt.update_ticket_status.assert_called_once_with('TICKET-4', 'Done') 
