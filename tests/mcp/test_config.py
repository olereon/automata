"""
Unit tests for MCP configuration.
"""

import json
import os
import tempfile
import pytest
from unittest.mock import patch, mock_open, MagicMock

from automata.mcp.config import MCPConfiguration


class TestMCPConfiguration:
    """Test cases for MCPConfiguration class."""

    def test_default_config(self):
        """Test that default configuration is loaded correctly."""
        config = MCPConfiguration()
        
        assert config.get_server_url() == "http://localhost:8080"
        assert config.get_timeout() == 30000
        assert config.get_retry_attempts() == 3
        assert config.get_retry_delay() == 1000
        assert config.is_bridge_extension_enabled() is True
        assert config.get_bridge_extension_port() == 9222
        assert config.is_session_sync_enabled() is True
        assert config.get_session_encryption_key() is None
        assert config.prefer_mcp_authentication() is False
        assert config.fallback_to_automata_authentication() is True

    def test_config_from_file(self):
        """Test that configuration is loaded from file correctly."""
        file_config = {
            "mcp": {
                "server_url": "http://example.com:9000",
                "timeout": 60000,
                "retry_attempts": 5,
                "retry_delay": 2000,
                "bridge_extension": {
                    "enabled": False,
                    "port": 9333
                },
                "session": {
                    "sync_enabled": False,
                    "encryption_key": "test-key"
                },
                "authentication": {
                    "prefer_mcp": True,
                    "fallback_to_automata": False
                }
            }
        }

        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            json.dump(file_config, f)
            temp_path = f.name

        try:
            config = MCPConfiguration(config_path=temp_path)

            assert config.get_server_url() == "http://example.com:9000"
            assert config.get_timeout() == 60000
            assert config.get_retry_attempts() == 5
            assert config.get_retry_delay() == 2000
            assert config.is_bridge_extension_enabled() is False
            assert config.get_bridge_extension_port() == 9333
            assert config.is_session_sync_enabled() is False
            assert config.get_session_encryption_key() == "test-key"
            assert config.prefer_mcp_authentication() is True
            assert config.fallback_to_automata_authentication() is False
        finally:
            os.unlink(temp_path)

    def test_config_from_environment(self):
        """Test that configuration is loaded from environment variables correctly."""
        with patch.dict(os.environ, {
            "MCP_SERVER_URL": "http://env-example.com:8000",
            "MCP_TIMEOUT": "45000",
            "MCP_RETRY_ATTEMPTS": "4",
            "MCP_RETRY_DELAY": "1500",
            "MCP_BRIDGE_PORT": "9444",
            "MCP_SESSION_ENCRYPTION_KEY": "env-key",
            "MCP_PREFER_MCP_AUTH": "true",
            "MCP_FALLBACK_TO_AUTOMATA_AUTH": "false"
        }):
            config = MCPConfiguration()

            assert config.get_server_url() == "http://env-example.com:8000"
            assert config.get_timeout() == 45000
            assert config.get_retry_attempts() == 4
            assert config.get_retry_delay() == 1500
            assert config.get_bridge_extension_port() == 9444
            assert config.get_session_encryption_key() == "env-key"
            assert config.prefer_mcp_authentication() is True
            assert config.fallback_to_automata_authentication() is False

    def test_config_validation_invalid_server_url(self):
        """Test that invalid server URL raises ValueError."""
        config = MCPConfiguration()
        with pytest.raises(ValueError, match="MCP server URL must be a non-empty string"):
            config._validate_config({
                "mcp": {
                    "server_url": None,
                    "timeout": 30000
                }
            })

    def test_config_validation_empty_server_url(self):
        """Test that empty server URL raises ValueError."""
        # Create a temporary file with invalid configuration
        invalid_config = {
            "mcp": {
                "server_url": "",
                "timeout": 30000,
                "retry_attempts": 3,
                "retry_delay": 1000
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            json.dump(invalid_config, f)
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError, match="MCP server URL must be a non-empty string"):
                MCPConfiguration(config_path=temp_path)
        finally:
            os.unlink(temp_path)

    def test_config_validation_invalid_timeout(self):
        """Test that invalid timeout raises ValueError."""
        # Create a temporary file with invalid configuration
        invalid_config = {
            "mcp": {
                "server_url": "http://localhost:8080",
                "timeout": -1,
                "retry_attempts": 3,
                "retry_delay": 1000
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            json.dump(invalid_config, f)
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError, match="MCP timeout must be a positive integer"):
                MCPConfiguration(config_path=temp_path)
        finally:
            os.unlink(temp_path)

    def test_config_validation_invalid_retry_attempts(self):
        """Test that invalid retry attempts raises ValueError."""
        # Create a temporary file with invalid configuration
        invalid_config = {
            "mcp": {
                "server_url": "http://localhost:8080",
                "timeout": 30000,
                "retry_attempts": -1,
                "retry_delay": 1000
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            json.dump(invalid_config, f)
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError, match="MCP retry attempts must be a non-negative integer"):
                MCPConfiguration(config_path=temp_path)
        finally:
            os.unlink(temp_path)

    def test_config_validation_invalid_retry_delay(self):
        """Test that invalid retry delay raises ValueError."""
        # Create a temporary file with invalid configuration
        invalid_config = {
            "mcp": {
                "server_url": "http://localhost:8080",
                "timeout": 30000,
                "retry_attempts": 3,
                "retry_delay": -1
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            json.dump(invalid_config, f)
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError, match="MCP retry delay must be a non-negative integer"):
                MCPConfiguration(config_path=temp_path)
        finally:
            os.unlink(temp_path)

    def test_config_validation_invalid_bridge_port(self):
        """Test that invalid bridge extension port raises ValueError."""
        # Create a temporary file with invalid configuration
        invalid_config = {
            "mcp": {
                "server_url": "http://localhost:8080",
                "timeout": 30000,
                "retry_attempts": 3,
                "retry_delay": 1000,
                "bridge_extension": {
                    "port": 0
                }
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            json.dump(invalid_config, f)
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError, match="MCP bridge extension port must be a valid port number"):
                MCPConfiguration(config_path=temp_path)
        finally:
            os.unlink(temp_path)

    def test_config_validation_invalid_bridge_port_too_high(self):
        """Test that too high bridge extension port raises ValueError."""
        # Create a temporary file with invalid configuration
        invalid_config = {
            "mcp": {
                "server_url": "http://localhost:8080",
                "timeout": 30000,
                "retry_attempts": 3,
                "retry_delay": 1000,
                "bridge_extension": {
                    "port": 70000
                }
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            json.dump(invalid_config, f)
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError, match="MCP bridge extension port must be a valid port number"):
                MCPConfiguration(config_path=temp_path)
        finally:
            os.unlink(temp_path)

    def test_config_validation_invalid_session_sync(self):
        """Test that invalid session sync setting raises ValueError."""
        # Create a temporary file with invalid configuration
        invalid_config = {
            "mcp": {
                "server_url": "http://localhost:8080",
                "timeout": 30000,
                "retry_attempts": 3,
                "retry_delay": 1000,
                "session": {
                    "sync_enabled": "not_a_boolean"
                }
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            json.dump(invalid_config, f)
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError, match="MCP session sync_enabled must be a boolean"):
                MCPConfiguration(config_path=temp_path)
        finally:
            os.unlink(temp_path)

    def test_config_validation_invalid_prefer_mcp(self):
        """Test that invalid prefer_mcp setting raises ValueError."""
        # Create a temporary file with invalid configuration
        invalid_config = {
            "mcp": {
                "server_url": "http://localhost:8080",
                "timeout": 30000,
                "retry_attempts": 3,
                "retry_delay": 1000,
                "authentication": {
                    "prefer_mcp": "not_a_boolean"
                }
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            json.dump(invalid_config, f)
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError, match="MCP authentication prefer_mcp must be a boolean"):
                MCPConfiguration(config_path=temp_path)
        finally:
            os.unlink(temp_path)

    def test_config_validation_invalid_fallback(self):
        """Test that invalid fallback setting raises ValueError."""
        # Create a temporary file with invalid configuration
        invalid_config = {
            "mcp": {
                "server_url": "http://localhost:8080",
                "timeout": 30000,
                "retry_attempts": 3,
                "retry_delay": 1000,
                "authentication": {
                    "fallback_to_automata": "not_a_boolean"
                }
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            json.dump(invalid_config, f)
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError, match="MCP authentication fallback_to_automata must be a boolean"):
                MCPConfiguration(config_path=temp_path)
        finally:
            os.unlink(temp_path)

    def test_save_config(self):
        """Test that configuration is saved correctly."""
        config = MCPConfiguration()

        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            temp_path = f.name

        try:
            config.save_config(temp_path)

            with open(temp_path, "r") as f:
                saved_config = json.load(f)

            assert saved_config["mcp"]["server_url"] == "http://localhost:8080"
            assert saved_config["mcp"]["timeout"] == 30000
        finally:
            os.unlink(temp_path)

    def test_get_config(self):
        """Test that get_config returns the full configuration."""
        config = MCPConfiguration()
        full_config = config.get_config()

        assert "mcp" in full_config
        assert full_config["mcp"]["server_url"] == "http://localhost:8080"
        assert full_config["mcp"]["timeout"] == 30000

    def test_invalid_environment_timeout(self):
        """Test that invalid timeout environment variable uses default."""
        with patch.dict(os.environ, {"MCP_TIMEOUT": "not_a_number"}):
            config = MCPConfiguration()
            # Should use default value
            assert config.get_timeout() == 30000

    def test_invalid_environment_retry_attempts(self):
        """Test that invalid retry_attempts environment variable uses default."""
        with patch.dict(os.environ, {"MCP_RETRY_ATTEMPTS": "not_a_number"}):
            config = MCPConfiguration()
            # Should use default value
            assert config.get_retry_attempts() == 3

    def test_invalid_environment_retry_delay(self):
        """Test that invalid retry_delay environment variable uses default."""
        with patch.dict(os.environ, {"MCP_RETRY_DELAY": "not_a_number"}):
            config = MCPConfiguration()
            # Should use default value
            assert config.get_retry_delay() == 1000

    def test_invalid_environment_bridge_port(self):
        """Test that invalid bridge_port environment variable uses default."""
        with patch.dict(os.environ, {"MCP_BRIDGE_PORT": "not_a_number"}):
            config = MCPConfiguration()
            # Should use default value
            assert config.get_bridge_extension_port() == 9222