import pytest
from unittest.mock import patch, MagicMock
from gitask.pmt.pmt_factory import get_pmt
from gitask.pmt.jira_pmt import JiraPmt
from gitask.pmt.github_pmt import GitHubPmt

def test_get_pmt_jira():
    with patch('gitask.pmt.pmt_factory.Config') as mock_config, \
         patch('gitask.pmt.pmt_factory.JiraPmt') as mock_jira:
        mock_config.return_value.pmt_type = 'Jira'
        result = get_pmt()
        mock_jira.assert_called_once()
        assert result == mock_jira()

def test_get_pmt_github():
    with patch('gitask.pmt.pmt_factory.Config') as mock_config, \
         patch('gitask.pmt.pmt_factory.GitHubPmt') as mock_gh:
        mock_config.return_value.pmt_type = 'GitHub'
        result = get_pmt()
        mock_gh.assert_called_once()
        assert result == mock_gh()

def test_get_pmt_invalid():
    with patch('gitask.pmt.pmt_factory.Config') as mock_config:
        mock_config.return_value.pmt_type = 'Trello'
        with pytest.raises(ValueError, match='Unsupported PMT type: trello'):
            get_pmt() 
