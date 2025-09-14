"""
Tests for the JSON credentials authentication provider.
"""

import asyncio
import json
import os
import stat
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock, AsyncMock

import pytest

from src.automata.auth.credentials_json import CredentialsJsonAuthProvider, CredentialsJsonWebAuthenticator
from src.automata.auth.base import AuthResult, AuthMethod


@pytest.fixture
def auth_provider():
    """Create a credentials JSON authentication provider for testing."""
    return CredentialsJsonAuthProvider()


@pytest.fixture
def web_authenticator():
    """Create a credentials JSON web authenticator for testing."""
    mock_engine = MagicMock()
    return CredentialsJsonWebAuthenticator(mock_engine)


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
def missing_credentials_file():
    """Create a credentials file missing the credentials section."""
    credentials_data = {
        "config": {
            "base_url": "https://api.example.com"
        },
        "custom_fields": {
            "user_id": "12345"
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(credentials_data, f, indent=2)
        return f.name


@pytest.fixture
def missing_config_file():
    """Create a credentials file missing the config section."""
    credentials_data = {
        "credentials": {
            "username": "testuser",
            "password": "testpass123"
        },
        "custom_fields": {
            "user_id": "12345"
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(credentials_data, f, indent=2)
        return f.name


@pytest.fixture
def readable_permissions_file(valid_credentials_file):
    """Create a credentials file with readable permissions."""
    # Set file permissions to be readable by others
    os.chmod(valid_credentials_file, stat.S_IRUSR | stat.S_IWUSR | stat.S_IROTH)
    return valid_credentials_file


@pytest.fixture
def git_directory_file():
    """Create a credentials file in a git directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a .git directory
        git_dir = Path(temp_dir) / ".git"
        git_dir.mkdir()
        
        # Create credentials file
        credentials_file = Path(temp_dir) / "credentials.json"
        credentials_data = {
            "credentials": {
                "username": "testuser",
                "password": "testpass123"
            },
            "config": {}
        }
        
        with open(credentials_file, 'w') as f:
            json.dump(credentials_data, f, indent=2)
        
        return str(credentials_file)


class TestCredentialsJsonAuthProvider:
    """Test cases for the CredentialsJsonAuthProvider class."""

    @pytest.mark.asyncio
    @pytest.mark.unit
    @pytest.mark.auth
    async def test_is_available_with_valid_file(self, auth_provider, valid_credentials_file):
        """Test that is_available returns True for a valid credentials file."""
        result = await auth_provider.is_available(path=valid_credentials_file)
        assert result is True

    @pytest.mark.asyncio
    @pytest.mark.unit
    @pytest.mark.auth
    async def test_is_available_with_no_path(self, auth_provider):
        """Test that is_available returns False when no path is provided."""
        result = await auth_provider.is_available()
        assert result is False

    @pytest.mark.asyncio
    @pytest.mark.unit
    @pytest.mark.auth
    async def test_is_available_with_nonexistent_file(self, auth_provider):
        """Test that is_available returns False for a non-existent file."""
        result = await auth_provider.is_available(path="/nonexistent/file.json")
        assert result is False

    @pytest.mark.asyncio
    @pytest.mark.unit
    @pytest.mark.auth
    async def test_is_available_with_invalid_permissions(self, auth_provider, readable_permissions_file):
        """Test that is_available returns False for a file with invalid permissions."""
        result = await auth_provider.is_available(path=readable_permissions_file)
        assert result is False

    @pytest.mark.asyncio
    @pytest.mark.unit
    @pytest.mark.auth
    async def test_is_available_with_git_directory(self, auth_provider, git_directory_file):
        """Test that is_available returns False for a file in a git directory."""
        result = await auth_provider.is_available(path=git_directory_file)
        assert result is False

    @pytest.mark.asyncio
    @pytest.mark.unit
    @pytest.mark.auth
    async def test_authenticate_with_valid_file(self, auth_provider, valid_credentials_file):
        """Test that authenticate succeeds with a valid credentials file."""
        result = await auth_provider.authenticate(path=valid_credentials_file)
        
        assert result.success is True
        assert "Authenticated using JSON credentials file" in result.message
        assert result.data["credentials_file"] == valid_credentials_file
        assert result.data["credentials"]["username"] == "***"
        assert result.data["credentials"]["password"] == "***"
        assert result.session_data["credentials"]["username"] == "testuser"
        assert result.session_data["credentials"]["password"] == "testpass123"
        assert result.session_data["auth_method"] == AuthMethod.CREDENTIALS_JSON.value

    @pytest.mark.asyncio
    @pytest.mark.unit
    @pytest.mark.auth
    async def test_authenticate_with_minimal_file(self, auth_provider, minimal_credentials_file):
        """Test that authenticate succeeds with a minimal credentials file."""
        result = await auth_provider.authenticate(path=minimal_credentials_file)
        
        assert result.success is True
        assert result.session_data["credentials"]["username"] == "testuser"
        assert result.session_data["credentials"]["password"] == "testpass123"

    @pytest.mark.asyncio
    @pytest.mark.unit
    @pytest.mark.auth
    async def test_authenticate_with_no_path(self, auth_provider):
        """Test that authenticate fails when no path is provided."""
        result = await auth_provider.authenticate()
        
        assert result.success is False
        assert "No JSON credentials file path provided" in result.message

    @pytest.mark.asyncio
    @pytest.mark.unit
    @pytest.mark.auth
    async def test_authenticate_with_invalid_json(self, auth_provider, invalid_json_file):
        """Test that authenticate fails with invalid JSON."""
        result = await auth_provider.authenticate(path=invalid_json_file)
        
        assert result.success is False
        assert "Failed to load credentials from JSON file" in result.message

    @pytest.mark.asyncio
    @pytest.mark.unit
    @pytest.mark.auth
    async def test_authenticate_with_missing_credentials(self, auth_provider, missing_credentials_file):
        """Test that authenticate fails when credentials section is missing."""
        result = await auth_provider.authenticate(path=missing_credentials_file)
        
        assert result.success is False
        assert "Invalid credentials format" in result.message

    @pytest.mark.asyncio
    @pytest.mark.unit
    @pytest.mark.auth
    async def test_authenticate_with_missing_config(self, auth_provider, missing_config_file):
        """Test that authenticate fails when config section is missing."""
        result = await auth_provider.authenticate(path=missing_config_file)
        
        assert result.success is False
        assert "Invalid credentials format" in result.message

    @pytest.mark.unit
    @pytest.mark.auth
    def test_get_credentials(self, auth_provider):
        """Test that get_credentials extracts credentials from session data."""
        session_data = {
            "credentials": {
                "username": "testuser",
                "password": "testpass123"
            },
            "config": {
                "base_url": "https://api.example.com"
            }
        }
        
        credentials = auth_provider.get_credentials(session_data)
        assert credentials == {
            "username": "testuser",
            "password": "testpass123"
        }

    @pytest.mark.unit
    @pytest.mark.auth
    def test_get_config(self, auth_provider):
        """Test that get_config extracts config from session data."""
        session_data = {
            "credentials": {
                "username": "testuser",
                "password": "testpass123"
            },
            "config": {
                "base_url": "https://api.example.com"
            }
        }
        
        config = auth_provider.get_config(session_data)
        assert config == {
            "base_url": "https://api.example.com"
        }

    @pytest.mark.unit
    @pytest.mark.auth
    def test_get_custom_fields(self, auth_provider):
        """Test that get_custom_fields extracts custom fields from session data."""
        session_data = {
            "credentials": {
                "username": "testuser",
                "password": "testpass123"
            },
            "config": {},
            "custom_fields": {
                "user_id": "12345",
                "preferences": {
                    "theme": "dark"
                }
            }
        }
        
        custom_fields = auth_provider.get_custom_fields(session_data)
        assert custom_fields == {
            "user_id": "12345",
            "preferences": {
                "theme": "dark"
            }
        }

    @pytest.mark.unit
    @pytest.mark.auth
    def test_validate_credentials_format_with_valid_data(self, auth_provider):
        """Test that _validate_credentials_format returns None for valid data."""
        data = {
            "credentials": {
                "username": "testuser",
                "password": "testpass123"
            },
            "config": {}
        }
        
        error = auth_provider._validate_credentials_format(data)
        assert error is None

    @pytest.mark.unit
    @pytest.mark.auth
    def test_validate_credentials_format_with_non_dict(self, auth_provider):
        """Test that _validate_credentials_format returns error for non-dict data."""
        data = "not a dict"
        
        error = auth_provider._validate_credentials_format(data)
        assert error == "Credentials data must be a dictionary"

    @pytest.mark.unit
    @pytest.mark.auth
    def test_validate_credentials_format_with_missing_credentials(self, auth_provider):
        """Test that _validate_credentials_format returns error when credentials section is missing."""
        data = {
            "config": {}
        }
        
        error = auth_provider._validate_credentials_format(data)
        assert error == "Missing required section: credentials"

    @pytest.mark.unit
    @pytest.mark.auth
    def test_validate_credentials_format_with_missing_config(self, auth_provider):
        """Test that _validate_credentials_format returns error when config section is missing."""
        data = {
            "credentials": {}
        }
        
        error = auth_provider._validate_credentials_format(data)
        assert error == "Missing required section: config"

    @pytest.mark.unit
    @pytest.mark.auth
    def test_validate_credentials_format_with_invalid_credentials(self, auth_provider):
        """Test that _validate_credentials_format returns error when credentials section is not a dict."""
        data = {
            "credentials": "not a dict",
            "config": {}
        }
        
        error = auth_provider._validate_credentials_format(data)
        assert error == "Credentials section must be a dictionary"

    @pytest.mark.unit
    @pytest.mark.auth
    def test_validate_credentials_format_with_invalid_config(self, auth_provider):
        """Test that _validate_credentials_format returns error when config section is not a dict."""
        data = {
            "credentials": {},
            "config": "not a dict"
        }
        
        error = auth_provider._validate_credentials_format(data)
        assert error == "Config section must be a dictionary"

    @pytest.mark.unit
    @pytest.mark.auth
    def test_validate_credentials_format_with_invalid_custom_fields(self, auth_provider):
        """Test that _validate_credentials_format returns error when custom_fields section is not a dict."""
        data = {
            "credentials": {},
            "config": {},
            "custom_fields": "not a dict"
        }
        
        error = auth_provider._validate_credentials_format(data)
        assert error == "Custom fields section must be a dictionary"

    @pytest.mark.unit
    @pytest.mark.auth
    def test_load_json_credentials_with_valid_file(self, auth_provider, valid_credentials_file):
        """Test that _load_json_credentials loads data from a valid file."""
        data = auth_provider._load_json_credentials(Path(valid_credentials_file))
        
        assert data is not None
        assert data["credentials"]["username"] == "testuser"
        assert data["config"]["base_url"] == "https://api.example.com"

    @pytest.mark.unit
    @pytest.mark.auth
    def test_load_json_credentials_with_invalid_file(self, auth_provider, invalid_json_file):
        """Test that _load_json_credentials returns None for an invalid file."""
        data = auth_provider._load_json_credentials(Path(invalid_json_file))
        assert data is None

    @pytest.mark.unit
    @pytest.mark.auth
    def test_load_json_credentials_with_nonexistent_file(self, auth_provider):
        """Test that _load_json_credentials returns None for a non-existent file."""
        data = auth_provider._load_json_credentials(Path("/nonexistent/file.json"))
        assert data is None


class TestCredentialsJsonWebAuthenticator:
    """Test cases for the CredentialsJsonWebAuthenticator class."""

    @pytest.mark.asyncio
    @pytest.mark.unit
    @pytest.mark.auth
    async def test_authenticate_with_valid_credentials(self, web_authenticator, valid_credentials_file):
        """Test that web authentication succeeds with valid credentials."""
        # Mock the web authentication methods
        web_authenticator.navigate_to_login = AsyncMock()
        web_authenticator.fill_login_form = AsyncMock()
        web_authenticator.wait_for_login_completion = AsyncMock(return_value=True)
        
        result = await web_authenticator.authenticate(
            login_url="https://example.com/login",
            username_selector="#username",
            password_selector="#password",
            path=valid_credentials_file
        )
        
        assert result.success is True
        assert "Web authentication successful for user: testuser" in result.message
        web_authenticator.navigate_to_login.assert_called_once_with("https://example.com/login")
        web_authenticator.fill_login_form.assert_called_once_with(
            username_selector="#username",
            username="testuser",
            password_selector="#password",
            password="testpass123",
            submit_selector=None
        )

    @pytest.mark.asyncio
    @pytest.mark.unit
    @pytest.mark.auth
    async def test_authenticate_with_login_failure(self, web_authenticator, valid_credentials_file):
        """Test that web authentication fails when login fails."""
        # Mock the web authentication methods
        web_authenticator.navigate_to_login = AsyncMock()
        web_authenticator.fill_login_form = AsyncMock()
        web_authenticator.wait_for_login_completion = AsyncMock(return_value=False)
        
        result = await web_authenticator.authenticate(
            login_url="https://example.com/login",
            username_selector="#username",
            password_selector="#password",
            path=valid_credentials_file
        )
        
        assert result.success is False
        assert "Web authentication failed using JSON credentials" in result.message

    @pytest.mark.asyncio
    @pytest.mark.unit
    @pytest.mark.auth
    async def test_authenticate_with_missing_username(self, web_authenticator, minimal_credentials_file):
        """Test that web authentication fails when username is missing."""
        # Create credentials file without username
        credentials_data = {
            "credentials": {
                "password": "testpass123"
            },
            "config": {}
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(credentials_data, f, indent=2)
            credentials_file = f.name
        
        try:
            result = await web_authenticator.authenticate(
                login_url="https://example.com/login",
                username_selector="#username",
                password_selector="#password",
                path=credentials_file
            )
            
            assert result.success is False
            assert "Username not found in JSON credentials file" in result.message
        finally:
            os.unlink(credentials_file)

    @pytest.mark.asyncio
    @pytest.mark.unit
    @pytest.mark.auth
    async def test_authenticate_with_missing_password(self, web_authenticator, minimal_credentials_file):
        """Test that web authentication fails when password is missing."""
        # Create credentials file without password
        credentials_data = {
            "credentials": {
                "username": "testuser"
            },
            "config": {}
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(credentials_data, f, indent=2)
            credentials_file = f.name
        
        try:
            result = await web_authenticator.authenticate(
                login_url="https://example.com/login",
                username_selector="#username",
                password_selector="#password",
                path=credentials_file
            )
            
            assert result.success is False
            assert "Password not found in JSON credentials file" in result.message
        finally:
            os.unlink(credentials_file)

    @pytest.mark.asyncio
    @pytest.mark.unit
    @pytest.mark.auth
    async def test_authenticate_with_submit_selector(self, web_authenticator, valid_credentials_file):
        """Test that web authentication uses submit selector when provided."""
        # Mock the web authentication methods
        web_authenticator.navigate_to_login = AsyncMock()
        web_authenticator.fill_login_form = AsyncMock()
        web_authenticator.wait_for_login_completion = AsyncMock(return_value=True)
        
        result = await web_authenticator.authenticate(
            login_url="https://example.com/login",
            username_selector="#username",
            password_selector="#password",
            submit_selector="#submit",
            path=valid_credentials_file
        )
        
        assert result.success is True
        web_authenticator.fill_login_form.assert_called_once_with(
            username_selector="#username",
            username="testuser",
            password_selector="#password",
            password="testpass123",
            submit_selector="#submit"
        )
