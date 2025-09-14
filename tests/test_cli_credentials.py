"""
Tests for the CLI credentials parameter.
"""

import json
import os
import tempfile
from unittest.mock import patch, MagicMock, AsyncMock

import pytest
from click.testing import CliRunner

from src.automata.cli.main import cli


@pytest.fixture
def valid_credentials_file():
    """Create a valid credentials file for testing."""
    credentials_data = {
        "credentials": {
            "username": "testuser",
            "password": "testpass123",
            "email": "testuser@example.com"
        },
        "config": {
            "base_url": "https://api.example.com",
            "timeout": 30
        },
        "custom_fields": {
            "user_id": "12345",
            "preferences": {
                "theme": "dark"
            }
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(credentials_data, f, indent=2)
        return f.name


@pytest.fixture
def minimal_credentials_file():
    """Create a minimal credentials file for testing."""
    credentials_data = {
        "credentials": {
            "username": "testuser",
            "password": "testpass123"
        },
        "config": {}
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(credentials_data, f, indent=2)
        return f.name


@pytest.fixture
def invalid_json_file():
    """Create an invalid JSON file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        f.write('{"invalid": json}')
        return f.name


@pytest.fixture
def sample_workflow_file():
    """Create a sample workflow file for testing."""
    workflow_data = {
        "name": "Test Workflow",
        "version": "1.0.0",
        "description": "A test workflow",
        "variables": {
            "url": "https://example.com",
            "username": "${username}",
            "password": "${password}"
        },
        "steps": [
            {
                "name": "Navigate to page",
                "action": "navigate",
                "value": "${url}"
            },
            {
                "name": "Login",
                "action": "type",
                "selector": "#username",
                "value": "${username}"
            },
            {
                "name": "Enter password",
                "action": "type",
                "selector": "#password",
                "value": "${password}"
            },
            {
                "name": "Submit",
                "action": "click",
                "selector": "#submit"
            }
        ]
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(workflow_data, f, indent=2)
        return f.name


@pytest.fixture
def mock_auth_config():
    """Create a mock authentication config."""
    mock_config = MagicMock()
    mock_config.authenticate = AsyncMock(return_value={
        "success": True,
        "session_data": {
            "credentials": {
                "username": "testuser",
                "password": "testpass123",
                "email": "testuser@example.com"
            },
            "config": {
                "base_url": "https://api.example.com",
                "timeout": 30
            },
            "custom_fields": {
                "user_id": "12345",
                "preferences": {
                    "theme": "dark"
                }
            }
        }
    })
    return mock_config


@pytest.fixture
def mock_workflow_engine():
    """Create a mock workflow execution engine."""
    mock_engine = MagicMock()
    mock_engine.variable_manager = MagicMock()
    mock_engine.execute_workflow = AsyncMock(return_value=[
        {"status": "completed", "step_name": "Navigate to page"},
        {"status": "completed", "step_name": "Login"},
        {"status": "completed", "step_name": "Enter password"},
        {"status": "completed", "step_name": "Submit"}
    ])
    return mock_engine


@pytest.fixture
def mock_workflow_builder():
    """Create a mock workflow builder."""
    mock_builder = MagicMock()
    mock_builder.load_workflow.return_value = {
        "name": "Test Workflow",
        "version": "1.0.0",
        "description": "A test workflow",
        "variables": {
            "url": "https://example.com",
            "username": "${username}",
            "password": "${password}"
        },
        "steps": [
            {
                "name": "Navigate to page",
                "action": "navigate",
                "value": "${url}"
            },
            {
                "name": "Login",
                "action": "type",
                "selector": "#username",
                "value": "${username}"
            },
            {
                "name": "Enter password",
                "action": "type",
                "selector": "#password",
                "value": "${password}"
            },
            {
                "name": "Submit",
                "action": "click",
                "selector": "#submit"
            }
        ]
    }
    return mock_builder


class TestCliCredentials:
    """Test cases for the CLI credentials parameter."""

    @pytest.mark.unit
    @pytest.mark.cli
    @pytest.mark.auth
    def test_workflow_execute_with_valid_credentials(self, valid_credentials_file, sample_workflow_file, 
                                                   mock_auth_config, mock_workflow_engine, mock_workflow_builder):
        """Test that workflow execute succeeds with valid credentials."""
        runner = CliRunner()
        
        with patch('src.automata.auth.config.AuthenticationConfig', return_value=mock_auth_config), \
             patch('src.automata.cli.main.WorkflowExecutionEngine', return_value=mock_workflow_engine), \
             patch('src.automata.cli.main.WorkflowBuilder', return_value=mock_workflow_builder):
            
            result = runner.invoke(cli, [
                'workflow', 'execute', 
                sample_workflow_file,
                '--credentials', valid_credentials_file
            ])
            
            assert result.exit_code == 0
            assert "Credentials loaded from:" in result.output
            assert "Workflow executed successfully with 4 steps" in result.output
            
            # Verify that authentication was called with correct parameters
            mock_auth_config.authenticate.assert_called_once_with(
                method="credentials_json",
                path=valid_credentials_file
            )
            
            # Verify that credentials were injected into variable manager
            assert mock_workflow_engine.variable_manager.bulk_set_variables.call_count == 3
            mock_workflow_engine.variable_manager.bulk_set_variables.assert_any_call({
                "username": "testuser",
                "password": "testpass123",
                "email": "testuser@example.com"
            })
            mock_workflow_engine.variable_manager.bulk_set_variables.assert_any_call({
                "base_url": "https://api.example.com",
                "timeout": 30
            })
            mock_workflow_engine.variable_manager.bulk_set_variables.assert_any_call({
                "user_id": "12345",
                "preferences": {
                    "theme": "dark"
                }
            })

    @pytest.mark.unit
    @pytest.mark.cli
    @pytest.mark.auth
    def test_workflow_execute_with_minimal_credentials(self, minimal_credentials_file, sample_workflow_file,
                                                      mock_auth_config, mock_workflow_engine, mock_workflow_builder):
        """Test that workflow execute succeeds with minimal credentials."""
        runner = CliRunner()
        
        with patch('src.automata.auth.config.AuthenticationConfig', return_value=mock_auth_config), \
             patch('src.automata.cli.main.WorkflowExecutionEngine', return_value=mock_workflow_engine), \
             patch('src.automata.cli.main.WorkflowBuilder', return_value=mock_workflow_builder):
            
            result = runner.invoke(cli, [
                'workflow', 'execute', 
                sample_workflow_file,
                '--credentials', minimal_credentials_file
            ])
            
            assert result.exit_code == 0
            assert "Credentials loaded from:" in result.output
            assert "Workflow executed successfully with 4 steps" in result.output

    @pytest.mark.unit
    @pytest.mark.cli
    @pytest.mark.auth
    def test_workflow_execute_without_credentials(self, sample_workflow_file, mock_workflow_engine, mock_workflow_builder):
        """Test that workflow execute succeeds without credentials."""
        runner = CliRunner()
        
        with patch('src.automata.cli.main.WorkflowExecutionEngine', return_value=mock_workflow_engine), \
             patch('src.automata.cli.main.WorkflowBuilder', return_value=mock_workflow_builder):
            
            result = runner.invoke(cli, [
                'workflow', 'execute', 
                sample_workflow_file
            ])
            
            assert result.exit_code == 0
            assert "Credentials loaded from:" not in result.output
            assert "Workflow executed successfully with 4 steps" in result.output

    @pytest.mark.unit
    @pytest.mark.cli
    @pytest.mark.auth
    def test_workflow_execute_with_authentication_failure(self, valid_credentials_file, sample_workflow_file,
                                                          mock_auth_config, mock_workflow_engine, mock_workflow_builder):
        """Test that workflow execute fails when authentication fails."""
        # Configure mock to return authentication failure
        mock_auth_config.authenticate.return_value = {
            "success": False,
            "error": "Invalid credentials"
        }
        
        runner = CliRunner()
        
        with patch('src.automata.auth.config.AuthenticationConfig', return_value=mock_auth_config), \
             patch('src.automata.cli.main.WorkflowExecutionEngine', return_value=mock_workflow_engine), \
             patch('src.automata.cli.main.WorkflowBuilder', return_value=mock_workflow_builder):
            
            result = runner.invoke(cli, [
                'workflow', 'execute', 
                sample_workflow_file,
                '--credentials', valid_credentials_file
            ])
            
            assert result.exit_code == 1
            assert "Error loading credentials: Invalid credentials" in result.output
            
            # Verify that authentication was called
            mock_auth_config.authenticate.assert_called_once_with(
                method="credentials_json",
                path=valid_credentials_file
            )
            
            # Verify that workflow execution was not called
            mock_workflow_engine.execute_workflow.assert_not_called()

    @pytest.mark.unit
    @pytest.mark.cli
    @pytest.mark.auth
    def test_workflow_execute_with_nonexistent_credentials_file(self, sample_workflow_file, mock_workflow_engine, mock_workflow_builder):
        """Test that workflow execute fails with a non-existent credentials file."""
        runner = CliRunner()
        
        with patch('src.automata.cli.main.WorkflowExecutionEngine', return_value=mock_workflow_engine), \
             patch('src.automata.cli.main.WorkflowBuilder', return_value=mock_workflow_builder):
            
            result = runner.invoke(cli, [
                'workflow', 'execute', 
                sample_workflow_file,
                '--credentials', '/nonexistent/credentials.json'
            ])
            
            # Click returns exit code 2 when a file path doesn't exist
            assert result.exit_code == 2
            assert "does not exist" in result.output

    @pytest.mark.unit
    @pytest.mark.cli
    @pytest.mark.auth
    def test_workflow_execute_with_invalid_credentials_file(self, invalid_json_file, sample_workflow_file,
                                                           mock_auth_config, mock_workflow_engine, mock_workflow_builder):
        """Test that workflow execute fails with an invalid credentials file."""
        # Configure mock to return authentication failure
        mock_auth_config.authenticate.return_value = {
            "success": False,
            "error": "Failed to load credentials from JSON file"
        }
        
        runner = CliRunner()
        
        with patch('src.automata.auth.config.AuthenticationConfig', return_value=mock_auth_config), \
             patch('src.automata.cli.main.WorkflowExecutionEngine', return_value=mock_workflow_engine), \
             patch('src.automata.cli.main.WorkflowBuilder', return_value=mock_workflow_builder):
            
            result = runner.invoke(cli, [
                'workflow', 'execute', 
                sample_workflow_file,
                '--credentials', invalid_json_file
            ])
            
            assert result.exit_code == 1
            assert "Error loading credentials: Failed to load credentials from JSON file" in result.output

    @pytest.mark.unit
    @pytest.mark.cli
    @pytest.mark.auth
    def test_workflow_execute_with_workflow_execution_failure(self, valid_credentials_file, sample_workflow_file,
                                                             mock_auth_config, mock_workflow_engine, mock_workflow_builder):
        """Test that workflow execute handles workflow execution failure."""
        # Configure mock to return workflow execution failure
        mock_workflow_engine.execute_workflow.return_value = [
            {"status": "completed", "step_name": "Navigate to page"},
            {"status": "failed", "step_name": "Login", "error": "Element not found"},
            {"status": "skipped", "step_name": "Enter password"},
            {"status": "skipped", "step_name": "Submit"}
        ]
        
        runner = CliRunner()
        
        with patch('src.automata.auth.config.AuthenticationConfig', return_value=mock_auth_config), \
             patch('src.automata.cli.main.WorkflowExecutionEngine', return_value=mock_workflow_engine), \
             patch('src.automata.cli.main.WorkflowBuilder', return_value=mock_workflow_builder):
            
            result = runner.invoke(cli, [
                'workflow', 'execute', 
                sample_workflow_file,
                '--credentials', valid_credentials_file
            ])
            
            assert result.exit_code == 0
            assert "Credentials loaded from:" in result.output
            assert "Workflow executed successfully with 4 steps" in result.output
            assert "Completed: 1, Failed: 1, Skipped: 2" in result.output
            assert "- Login: Element not found" in result.output

    @pytest.mark.unit
    @pytest.mark.cli
    @pytest.mark.auth
    def test_workflow_execute_with_exception(self, valid_credentials_file, sample_workflow_file,
                                            mock_auth_config, mock_workflow_engine, mock_workflow_builder):
        """Test that workflow execute handles exceptions during workflow execution."""
        # Configure mock to raise an exception
        mock_workflow_engine.execute_workflow.side_effect = Exception("Workflow execution error")
        
        runner = CliRunner()
        
        with patch('src.automata.auth.config.AuthenticationConfig', return_value=mock_auth_config), \
             patch('src.automata.cli.main.WorkflowExecutionEngine', return_value=mock_workflow_engine), \
             patch('src.automata.cli.main.WorkflowBuilder', return_value=mock_workflow_builder):
            
            result = runner.invoke(cli, [
                'workflow', 'execute', 
                sample_workflow_file,
                '--credentials', valid_credentials_file
            ])
            
            assert result.exit_code == 1
            assert "Error executing workflow: Workflow execution error" in result.output

    @pytest.mark.unit
    @pytest.mark.cli
    @pytest.mark.auth
    def test_workflow_execute_with_verbose_flag(self, valid_credentials_file, sample_workflow_file,
                                               mock_auth_config, mock_workflow_engine, mock_workflow_builder):
        """Test that workflow execute works with the verbose flag."""
        runner = CliRunner()
        
        with patch('src.automata.auth.config.AuthenticationConfig', return_value=mock_auth_config), \
             patch('src.automata.cli.main.WorkflowExecutionEngine', return_value=mock_workflow_engine), \
             patch('src.automata.cli.main.WorkflowBuilder', return_value=mock_workflow_builder):
            
            result = runner.invoke(cli, [
                '--verbose',
                'workflow', 'execute', 
                sample_workflow_file,
                '--credentials', valid_credentials_file
            ])
            
            assert result.exit_code == 0
            assert "Credentials loaded from:" in result.output
            assert "Workflow executed successfully with 4 steps" in result.output

    @pytest.mark.unit
    @pytest.mark.cli
    @pytest.mark.auth
    def test_workflow_execute_with_config_flag(self, valid_credentials_file, sample_workflow_file,
                                              mock_auth_config, mock_workflow_engine, mock_workflow_builder):
        """Test that workflow execute works with the config flag."""
        runner = CliRunner()
        
        with patch('src.automata.auth.config.AuthenticationConfig', return_value=mock_auth_config), \
             patch('src.automata.cli.main.WorkflowExecutionEngine', return_value=mock_workflow_engine), \
             patch('src.automata.cli.main.WorkflowBuilder', return_value=mock_workflow_builder):
            
            result = runner.invoke(cli, [
                '--config', '/path/to/config.json',
                'workflow', 'execute', 
                sample_workflow_file,
                '--credentials', valid_credentials_file
            ])
            
            assert result.exit_code == 0
            assert "Credentials loaded from:" in result.output
            assert "Workflow executed successfully with 4 steps" in result.output
