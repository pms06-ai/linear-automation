import os
import sys
import pytest
from unittest.mock import patch, MagicMock
import importlib.util


def load_module_from_path(name, path):
    """Load a module from a specific file path"""
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


# Get the base path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TestDailyJournal:
    """Tests for the daily journal function"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Load the module for each test"""
        module_path = os.path.join(BASE_DIR, 'functions', 'daily-journal', 'main.py')
        self.module = load_module_from_path('daily_journal_main', module_path)
    
    def test_missing_api_key(self):
        """Test that missing API key returns error"""
        with patch.dict(os.environ, {}, clear=True):
            result, status = self.module.create_daily_journal(None)
            assert status == 500
            assert "LINEAR_API_KEY" in result.get("error", "")
    
    def test_successful_issue_creation(self):
        """Test successful issue creation"""
        mock_response = MagicMock()
        mock_response.json.side_effect = [
            {"data": {"teams": {"nodes": [{"id": "team-123", "name": "Test Team"}]}}},
            {"data": {"issueCreate": {"success": True, "issue": {"id": "issue-123", "identifier": "TT-1", "title": "Trading Journal - 2024-01-01"}}}}
        ]
        mock_response.raise_for_status = MagicMock()
        
        with patch.dict(os.environ, {"LINEAR_API_KEY": "test-key"}):
            with patch.object(self.module.requests, 'post', return_value=mock_response):
                result, status = self.module.create_daily_journal(None)
                assert status == 200
                assert result.get("success") is True
                assert "issue" in result
    
    def test_no_teams_found(self):
        """Test when no teams are found"""
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": {"teams": {"nodes": []}}}
        mock_response.raise_for_status = MagicMock()
        
        with patch.dict(os.environ, {"LINEAR_API_KEY": "test-key"}):
            with patch.object(self.module.requests, 'post', return_value=mock_response):
                result, status = self.module.create_daily_journal(None)
                assert status == 404
                assert "No teams found" in result.get("error", "")
    
    def test_request_exception_on_teams(self):
        """Test handling of request exception when fetching teams"""
        with patch.dict(os.environ, {"LINEAR_API_KEY": "test-key"}):
            with patch.object(self.module.requests, 'post', side_effect=self.module.requests.exceptions.RequestException("Network error")):
                result, status = self.module.create_daily_journal(None)
                assert status == 500
                assert "Failed to fetch teams" in result.get("error", "")


class TestBqMonitor:
    """Tests for the BigQuery monitor function"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Load the module for each test"""
        module_path = os.path.join(BASE_DIR, 'functions', 'bq-monitor', 'main.py')
        self.module = load_module_from_path('bq_monitor_main', module_path)
    
    def test_missing_api_key(self):
        """Test that missing API key returns error"""
        with patch.dict(os.environ, {}, clear=True):
            result, status = self.module.check_bigquery_jobs(None)
            assert status == 500
            assert "LINEAR_API_KEY" in result.get("error", "")
    
    def test_missing_project_id(self):
        """Test that missing project ID returns error"""
        with patch.dict(os.environ, {"LINEAR_API_KEY": "test-key"}, clear=True):
            result, status = self.module.check_bigquery_jobs(None)
            assert status == 500
            assert "GCP_PROJECT_ID" in result.get("error", "")
    
    def test_successful_monitoring(self):
        """Test successful monitoring check"""
        with patch.dict(os.environ, {"LINEAR_API_KEY": "test-key", "GCP_PROJECT_ID": "test-project"}):
            result, status = self.module.check_bigquery_jobs(None)
            assert status == 200
            assert result.get("success") is True
            assert "test-project" in result.get("message", "")
