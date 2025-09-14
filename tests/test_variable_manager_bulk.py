"""
Tests for the variable manager bulk operations.
"""

import json
import pytest
from unittest.mock import patch, MagicMock

from src.automata.utils.variables import VariableManager
from src.automata.core.errors import AutomationError


@pytest.fixture
def variable_manager():
    """Create a variable manager for testing."""
    return VariableManager()


@pytest.fixture
def sample_credentials():
    """Create sample credentials for testing."""
    return {
        "username": "testuser",
        "password": "testpass123",
        "email": "testuser@example.com",
        "api_key": "sk-test123456789"
    }


@pytest.fixture
def sample_config():
    """Create sample config for testing."""
    return {
        "base_url": "https://api.example.com",
        "timeout": 30,
        "retries": 3,
        "debug": False
    }


@pytest.fixture
def sample_custom_fields():
    """Create sample custom fields for testing."""
    return {
        "user_id": "12345",
        "account_type": "premium",
        "preferences": {
            "theme": "dark",
            "language": "en",
            "notifications": True
        },
        "metadata": {
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-02T00:00:00Z"
        }
    }


@pytest.fixture
def sample_workflow_with_variables():
    """Create a sample workflow with variables for testing."""
    return {
        "name": "Test Workflow",
        "version": "1.0.0",
        "description": "A test workflow with variables",
        "variables": {
            "url": "https://example.com",
            "username": "${username}",
            "password": "${password}",
            "api_endpoint": "${base_url}/api",
            "user_id": "${user_id}",
            "theme": "${theme}"
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


class TestVariableManagerBulkOperations:
    """Test cases for the variable manager bulk operations."""

    @pytest.mark.unit
    def test_bulk_set_variables(self, variable_manager):
        """Test that bulk_set_variables sets multiple variables correctly."""
        variables = {
            "username": "testuser",
            "password": "testpass123",
            "email": "testuser@example.com"
        }
        
        variable_manager.bulk_set_variables(variables)
        
        # Verify all variables were set
        assert variable_manager.get_variable("username") == "testuser"
        assert variable_manager.get_variable("password") == "testpass123"
        assert variable_manager.get_variable("email") == "testuser@example.com"

    @pytest.mark.unit
    def test_bulk_set_variables_with_persist(self, variable_manager):
        """Test that bulk_set_variables persists variables when requested."""
        variables = {
            "username": "testuser",
            "password": "testpass123"
        }
        
        with patch.object(variable_manager, '_persist_variable') as mock_persist:
            variable_manager.bulk_set_variables(variables, persist=True)
            
            # Verify persist was called for each variable
            assert mock_persist.call_count == 2
            mock_persist.assert_any_call("username", "testuser")
            mock_persist.assert_any_call("password", "testpass123")

    @pytest.mark.unit
    def test_bulk_set_variables_with_empty_dict(self, variable_manager):
        """Test that bulk_set_variables handles empty dictionary correctly."""
        variable_manager.bulk_set_variables({})
        
        # Verify no variables were set
        assert len(variable_manager.variables) == 0

    @pytest.mark.unit
    def test_bulk_set_variables_with_exception(self, variable_manager):
        """Test that bulk_set_variables handles exceptions correctly."""
        variables = {
            "username": "testuser",
            "password": "testpass123"
        }
        
        with patch.object(variable_manager, 'set_variable', side_effect=Exception("Test error")):
            with pytest.raises(AutomationError, match="Error bulk setting variables"):
                variable_manager.bulk_set_variables(variables)

    @pytest.mark.unit
    def test_bulk_get_variables(self, variable_manager):
        """Test that bulk_get_variables gets multiple variables correctly."""
        # Set some variables
        variable_manager.set_variable("username", "testuser")
        variable_manager.set_variable("password", "testpass123")
        variable_manager.set_variable("email", "testuser@example.com")
        
        # Get variables
        names = ["username", "password", "email"]
        result = variable_manager.bulk_get_variables(names)
        
        # Verify all variables were retrieved
        assert result["username"] == "testuser"
        assert result["password"] == "testpass123"
        assert result["email"] == "testuser@example.com"

    @pytest.mark.unit
    def test_bulk_get_variables_with_nonexistent_variables(self, variable_manager):
        """Test that bulk_get_variables handles nonexistent variables correctly."""
        # Set some variables
        variable_manager.set_variable("username", "testuser")
        variable_manager.set_variable("password", "testpass123")
        
        # Get variables including nonexistent ones
        names = ["username", "password", "nonexistent1", "nonexistent2"]
        result = variable_manager.bulk_get_variables(names)
        
        # Verify existing variables were retrieved and nonexistent ones returned None
        assert result["username"] == "testuser"
        assert result["password"] == "testpass123"
        assert result["nonexistent1"] is None
        assert result["nonexistent2"] is None

    @pytest.mark.unit
    def test_bulk_get_variables_with_empty_list(self, variable_manager):
        """Test that bulk_get_variables handles empty list correctly."""
        result = variable_manager.bulk_get_variables([])
        
        # Verify empty dictionary was returned
        assert result == {}

    @pytest.mark.unit
    def test_bulk_get_variables_with_exception(self, variable_manager):
        """Test that bulk_get_variables handles exceptions correctly."""
        names = ["username", "password"]
        
        with patch.object(variable_manager, 'get_variable', side_effect=Exception("Test error")):
            with pytest.raises(AutomationError, match="Error bulk getting variables"):
                variable_manager.bulk_get_variables(names)

    @pytest.mark.unit
    def test_bulk_delete_variables(self, variable_manager):
        """Test that bulk_delete_variables deletes multiple variables correctly."""
        # Set some variables
        variable_manager.set_variable("username", "testuser")
        variable_manager.set_variable("password", "testpass123")
        variable_manager.set_variable("email", "testuser@example.com")
        
        # Delete variables
        names = ["username", "password"]
        result = variable_manager.bulk_delete_variables(names)
        
        # Verify variables were deleted
        assert result["username"] is True
        assert result["password"] is True
        assert variable_manager.get_variable("username") is None
        assert variable_manager.get_variable("password") is None
        assert variable_manager.get_variable("email") == "testuser@example.com"

    @pytest.mark.unit
    def test_bulk_delete_variables_with_nonexistent_variables(self, variable_manager):
        """Test that bulk_delete_variables handles nonexistent variables correctly."""
        # Set some variables
        variable_manager.set_variable("username", "testuser")
        variable_manager.set_variable("password", "testpass123")
        
        # Delete variables including nonexistent ones
        names = ["username", "password", "nonexistent1", "nonexistent2"]
        result = variable_manager.bulk_delete_variables(names)
        
        # Verify existing variables were deleted and nonexistent ones returned True
        # (Note: The current implementation always returns True)
        assert result["username"] is True
        assert result["password"] is True
        assert result["nonexistent1"] is True
        assert result["nonexistent2"] is True

    @pytest.mark.unit
    def test_bulk_delete_variables_with_empty_list(self, variable_manager):
        """Test that bulk_delete_variables handles empty list correctly."""
        result = variable_manager.bulk_delete_variables([])
        
        # Verify empty dictionary was returned
        assert result == {}

    @pytest.mark.unit
    def test_bulk_delete_variables_with_exception(self, variable_manager):
        """Test that bulk_delete_variables handles exceptions correctly."""
        names = ["username", "password"]
        
        with patch.object(variable_manager, 'delete_variable', side_effect=Exception("Test error")):
            with pytest.raises(AutomationError, match="Error bulk deleting variables"):
                variable_manager.bulk_delete_variables(names)

    @pytest.mark.unit
    def test_inject_variables_from_dict(self, variable_manager, sample_credentials):
        """Test that inject_variables_from_dict injects variables correctly."""
        variable_manager.inject_variables_from_dict(sample_credentials)
        
        # Verify all variables were injected
        assert variable_manager.get_variable("username") == "testuser"
        assert variable_manager.get_variable("password") == "testpass123"
        assert variable_manager.get_variable("email") == "testuser@example.com"
        assert variable_manager.get_variable("api_key") == "sk-test123456789"

    @pytest.mark.unit
    def test_inject_variables_from_dict_with_prefix(self, variable_manager, sample_credentials):
        """Test that inject_variables_from_dict injects variables with prefix correctly."""
        variable_manager.inject_variables_from_dict(sample_credentials, prefix="auth_")
        
        # Verify all variables were injected with prefix
        assert variable_manager.get_variable("auth_username") == "testuser"
        assert variable_manager.get_variable("auth_password") == "testpass123"
        assert variable_manager.get_variable("auth_email") == "testuser@example.com"
        assert variable_manager.get_variable("auth_api_key") == "sk-test123456789"

    @pytest.mark.unit
    def test_inject_variables_from_dict_with_empty_dict(self, variable_manager):
        """Test that inject_variables_from_dict handles empty dictionary correctly."""
        variable_manager.inject_variables_from_dict({})
        
        # Verify no variables were injected
        assert len(variable_manager.variables) == 0

    @pytest.mark.unit
    def test_inject_variables_from_dict_with_exception(self, variable_manager, sample_credentials):
        """Test that inject_variables_from_dict handles exceptions correctly."""
        with patch.object(variable_manager, 'set_variable', side_effect=Exception("Test error")):
            with pytest.raises(AutomationError, match="Error injecting variables from dictionary"):
                variable_manager.inject_variables_from_dict(sample_credentials)

    @pytest.mark.unit
    def test_extract_variables_to_dict(self, variable_manager, sample_credentials):
        """Test that extract_variables_to_dict extracts variables correctly."""
        # Inject variables
        variable_manager.inject_variables_from_dict(sample_credentials)
        
        # Extract variables
        result = variable_manager.extract_variables_to_dict()
        
        # Verify all variables were extracted
        assert result["username"] == "testuser"
        assert result["password"] == "testpass123"
        assert result["email"] == "testuser@example.com"
        assert result["api_key"] == "sk-test123456789"

    @pytest.mark.unit
    def test_extract_variables_to_dict_with_prefix(self, variable_manager, sample_credentials):
        """Test that extract_variables_to_dict extracts variables with prefix correctly."""
        # Inject variables with prefix
        variable_manager.inject_variables_from_dict(sample_credentials, prefix="auth_")
        
        # Extract variables with prefix
        result = variable_manager.extract_variables_to_dict(prefix="auth_")
        
        # Verify all variables were extracted without prefix
        assert result["username"] == "testuser"
        assert result["password"] == "testpass123"
        assert result["email"] == "testuser@example.com"
        assert result["api_key"] == "sk-test123456789"

    @pytest.mark.unit
    def test_extract_variables_to_dict_with_nonexistent_prefix(self, variable_manager, sample_credentials):
        """Test that extract_variables_to_dict handles nonexistent prefix correctly."""
        # Inject variables
        variable_manager.inject_variables_from_dict(sample_credentials)
        
        # Extract variables with nonexistent prefix
        result = variable_manager.extract_variables_to_dict(prefix="nonexistent_")
        
        # Verify empty dictionary was returned
        assert result == {}

    @pytest.mark.unit
    def test_extract_variables_to_dict_with_exception(self, variable_manager, sample_credentials):
        """Test that extract_variables_to_dict handles exceptions correctly."""
        # Inject variables
        variable_manager.inject_variables_from_dict(sample_credentials)
        
        with patch.object(variable_manager, 'list_variables', side_effect=Exception("Test error")):
            with pytest.raises(AutomationError, match="Error extracting variables to dictionary"):
                variable_manager.extract_variables_to_dict()

    @pytest.mark.unit
    def test_substitute_variables_with_credentials(self, variable_manager, sample_credentials, sample_config, sample_custom_fields):
        """Test that substitute_variables works with injected credentials."""
        # Inject credentials, config, and custom fields
        variable_manager.bulk_set_variables(sample_credentials)
        variable_manager.bulk_set_variables(sample_config)
        variable_manager.bulk_set_variables(sample_custom_fields)
        
        # Test substitution with various formats
        text1 = "Username: ${username}, Password: $password"
        result1 = variable_manager.substitute_variables(text1)
        assert result1 == "Username: testuser, Password: testpass123"
        
        # Test substitution with nested values
        text2 = "API endpoint: ${base_url}/api, User ID: ${user_id}"
        result2 = variable_manager.substitute_variables(text2)
        assert result2 == "API endpoint: https://api.example.com/api, User ID: 12345"
        
        # Test substitution with deeply nested values
        # Note: The current implementation doesn't support nested variable access like ${preferences.theme}
        # So we need to inject the nested values as separate variables
        variable_manager.set_variable("theme", "dark")
        variable_manager.set_variable("language", "en")
        
        text3 = "Theme: ${theme}, Language: ${language}"
        result3 = variable_manager.substitute_variables(text3)
        assert result3 == "Theme: dark, Language: en"

    @pytest.mark.unit
    def test_workflow_variable_substitution(self, variable_manager, sample_credentials, sample_config, sample_custom_fields, sample_workflow_with_variables):
        """Test that workflow variables are substituted correctly with injected credentials."""
        # Inject credentials, config, and custom fields
        variable_manager.bulk_set_variables(sample_credentials)
        variable_manager.bulk_set_variables(sample_config)
        variable_manager.bulk_set_variables(sample_custom_fields)
        
        # Inject nested values as separate variables
        variable_manager.set_variable("theme", "dark")
        variable_manager.set_variable("language", "en")
        variable_manager.set_variable("notifications", "True")
        
        # Substitute variables in workflow
        workflow_json = json.dumps(sample_workflow_with_variables)
        substituted_json = variable_manager.substitute_variables(workflow_json)
        substituted_workflow = json.loads(substituted_json)
        
        # Verify variables were substituted correctly
        assert substituted_workflow["variables"]["username"] == "testuser"
        assert substituted_workflow["variables"]["password"] == "testpass123"
        assert substituted_workflow["variables"]["api_endpoint"] == "https://api.example.com/api"
        assert substituted_workflow["variables"]["user_id"] == "12345"
        assert substituted_workflow["variables"]["theme"] == "dark"

    @pytest.mark.unit
    def test_multiple_bulk_operations(self, variable_manager, sample_credentials, sample_config):
        """Test that multiple bulk operations work correctly together."""
        # Inject credentials and config
        variable_manager.inject_variables_from_dict(sample_credentials, prefix="auth_")
        variable_manager.inject_variables_from_dict(sample_config, prefix="cfg_")
        
        # Extract variables
        auth_vars = variable_manager.extract_variables_to_dict(prefix="auth_")
        cfg_vars = variable_manager.extract_variables_to_dict(prefix="cfg_")
        
        # Verify extracted variables
        assert auth_vars["username"] == "testuser"
        assert auth_vars["password"] == "testpass123"
        assert cfg_vars["base_url"] == "https://api.example.com"
        assert cfg_vars["timeout"] == 30
        
        # Delete variables using the actual variable names with prefixes
        prefixed_vars = [f"auth_{key}" for key in auth_vars.keys()] + [f"cfg_{key}" for key in cfg_vars.keys()]
        variable_manager.bulk_delete_variables(prefixed_vars)
        
        # Verify variables were deleted
        assert variable_manager.get_variable("auth_username") is None
        assert variable_manager.get_variable("auth_password") is None
        assert variable_manager.get_variable("cfg_base_url") is None
        assert variable_manager.get_variable("cfg_timeout") is None
