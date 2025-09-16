"""
Connection error handling utilities for MCP Bridge.
"""

import asyncio
import time
import traceback
from enum import Enum
from typing import Dict, Any, Optional, Callable, List, Union
from urllib.parse import urlparse

import aiohttp
import websockets

from ..core.logger import get_logger
from .errors import CircuitBreaker

logger = get_logger(__name__)


class ConnectionErrorType(Enum):
    """Enumeration of connection error types."""
    NETWORK_ERROR = "network_error"
    TIMEOUT_ERROR = "timeout_error"
    AUTHENTICATION_ERROR = "authentication_error"
    PROTOCOL_ERROR = "protocol_error"
    SERVER_ERROR = "server_error"
    CONFIGURATION_ERROR = "configuration_error"
    UNKNOWN_ERROR = "unknown_error"


class ConnectionErrorContext:
    """Context information for connection errors."""
    
    def __init__(
        self,
        error_type: ConnectionErrorType,
        error_message: str,
        server_url: str,
        timestamp: float = None,
        original_exception: Exception = None,
        additional_info: Dict[str, Any] = None
    ):
        """
        Initialize connection error context.
        
        Args:
            error_type: Type of the connection error
            error_message: Error message
            server_url: Server URL that failed to connect
            timestamp: Timestamp when the error occurred
            original_exception: Original exception that caused the error
            additional_info: Additional information about the error
        """
        self.error_type = error_type
        self.error_message = error_message
        self.server_url = server_url
        self.timestamp = timestamp or time.time()
        self.original_exception = original_exception
        self.additional_info = additional_info or {}
        
        # Extract host and port from URL
        parsed_url = urlparse(server_url)
        self.host = parsed_url.hostname
        self.port = parsed_url.port
        self.scheme = parsed_url.scheme
        
        # Add connection attempt count
        self.connection_attempts = 0
        self.last_attempt_time = None
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert error context to dictionary."""
        return {
            "error_type": self.error_type.value,
            "error_message": self.error_message,
            "server_url": self.server_url,
            "host": self.host,
            "port": self.port,
            "scheme": self.scheme,
            "timestamp": self.timestamp,
            "connection_attempts": self.connection_attempts,
            "last_attempt_time": self.last_attempt_time,
            "additional_info": self.additional_info
        }
    
    def increment_attempts(self) -> None:
        """Increment connection attempt count and update last attempt time."""
        self.connection_attempts += 1
        self.last_attempt_time = time.time()


class ConnectionErrorHandler:
    """Handles connection errors with retry logic and circuit breaker pattern."""
    
    def __init__(
        self,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        backoff_factor: float = 2.0,
        circuit_breaker_threshold: int = 5,
        circuit_breaker_timeout: float = 60.0
    ):
        """
        Initialize connection error handler.
        
        Args:
            max_retries: Maximum number of retry attempts
            retry_delay: Initial delay between retries in seconds
            backoff_factor: Factor for exponential backoff
            circuit_breaker_threshold: Number of failures before opening circuit
            circuit_breaker_timeout: Timeout in seconds before attempting recovery
        """
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.backoff_factor = backoff_factor
        
        # Create circuit breakers for different servers
        self.circuit_breakers = {}
        self.circuit_breaker_threshold = circuit_breaker_threshold
        self.circuit_breaker_timeout = circuit_breaker_timeout
        
        # Track connection errors
        self.error_history = []
        
    def get_circuit_breaker(self, server_url: str) -> CircuitBreaker:
        """
        Get or create a circuit breaker for a server URL.
        
        Args:
            server_url: Server URL
            
        Returns:
            Circuit breaker instance
        """
        if server_url not in self.circuit_breakers:
            self.circuit_breakers[server_url] = CircuitBreaker(
                failure_threshold=self.circuit_breaker_threshold,
                recovery_timeout=int(self.circuit_breaker_timeout * 1000)  # Convert to milliseconds
            )
        return self.circuit_breakers[server_url]
    
    def classify_error(self, error: Exception, server_url: str) -> ConnectionErrorContext:
        """
        Classify a connection error and create error context.
        
        Args:
            error: The exception that occurred
            server_url: Server URL that failed to connect
            
        Returns:
            Connection error context
        """
        error_type = ConnectionErrorType.UNKNOWN_ERROR
        error_message = str(error)
        
        # Classify error based on exception type and message
        if isinstance(error, (aiohttp.ClientError, aiohttp.ClientConnectionError)):
            error_type = ConnectionErrorType.NETWORK_ERROR
            error_message = f"Network error connecting to {server_url}: {error}"
        elif isinstance(error, (asyncio.TimeoutError, aiohttp.ClientTimeout, aiohttp.ServerTimeoutError)):
            error_type = ConnectionErrorType.TIMEOUT_ERROR
            error_message = f"Timeout connecting to {server_url}: {error}"
        elif hasattr(websockets, 'exceptions') and isinstance(error, websockets.exceptions.InvalidStatusCode):
            if error.status_code in (401, 403):
                error_type = ConnectionErrorType.AUTHENTICATION_ERROR
                error_message = f"Authentication failed for {server_url}: {error}"
            else:
                error_type = ConnectionErrorType.SERVER_ERROR
                error_message = f"Server error {error.status_code} for {server_url}: {error}"
        elif hasattr(websockets, 'exceptions') and hasattr(websockets.exceptions, 'ConnectionClosed') and isinstance(error, websockets.exceptions.ConnectionClosed):
            error_type = ConnectionErrorType.NETWORK_ERROR
            error_message = f"Connection closed for {server_url}: {error}"
        elif hasattr(websockets, 'exceptions') and hasattr(websockets.exceptions, 'ConnectionClosedError') and isinstance(error, websockets.exceptions.ConnectionClosedError):
            error_type = ConnectionErrorType.NETWORK_ERROR
            error_message = f"Connection closed for {server_url}: {error}"
        elif hasattr(websockets, 'exceptions') and hasattr(websockets.exceptions, 'ConnectionClosedOK') and isinstance(error, websockets.exceptions.ConnectionClosedOK):
            error_type = ConnectionErrorType.NETWORK_ERROR
            error_message = f"Connection closed for {server_url}: {error}"
        elif hasattr(websockets, 'exceptions') and hasattr(websockets.exceptions, 'InvalidURI') and isinstance(error, websockets.exceptions.InvalidURI):
            error_type = ConnectionErrorType.CONFIGURATION_ERROR
            error_message = f"Invalid configuration for {server_url}: {error}"
        elif hasattr(websockets, 'exceptions') and hasattr(websockets.exceptions, 'InvalidHandshake') and isinstance(error, websockets.exceptions.InvalidHandshake):
            error_type = ConnectionErrorType.CONFIGURATION_ERROR
            error_message = f"Invalid configuration for {server_url}: {error}"
        elif "protocol" in str(error).lower():
            error_type = ConnectionErrorType.PROTOCOL_ERROR
            error_message = f"Protocol error with {server_url}: {error}"
        
        # Create error context
        context = ConnectionErrorContext(
            error_type=error_type,
            error_message=error_message,
            server_url=server_url,
            original_exception=error,
            additional_info={
                "exception_type": type(error).__name__,
                "traceback": traceback.format_exc()
            }
        )
        
        # Add to error history
        self.error_history.append(context)
        
        # Keep only the last 100 errors
        if len(self.error_history) > 100:
            self.error_history = self.error_history[-100:]
        
        return context
    
    async def handle_connection_error(
        self,
        error: Exception,
        server_url: str,
        connection_func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """
        Handle a connection error with retry logic and circuit breaker.
        
        Args:
            error: The exception that occurred
            server_url: Server URL that failed to connect
            connection_func: Function to call for connection
            *args: Arguments to pass to the connection function
            **kwargs: Keyword arguments to pass to the connection function
            
        Returns:
            Result of the connection function if successful
            
        Raises:
            The original exception if all retry attempts fail
        """
        # Classify the error
        context = self.classify_error(error, server_url)
        
        # Get circuit breaker for this server
        circuit_breaker = self.get_circuit_breaker(server_url)
        
        # Check if circuit breaker is open
        try:
            return await circuit_breaker.call(connection_func, *args, **kwargs)
        except Exception as e:
            # Circuit breaker is open or call failed
            logger.warning(f"Circuit breaker open for {server_url}: {e}")
            
            # Try to recover with retries
            return await self._retry_connection(
                context, connection_func, *args, **kwargs
            )
    
    async def _retry_connection(
        self,
        context: ConnectionErrorContext,
        connection_func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """
        Retry a connection with exponential backoff.
        
        Args:
            context: Connection error context
            connection_func: Function to call for connection
            *args: Arguments to pass to the connection function
            **kwargs: Keyword arguments to pass to the connection function
            
        Returns:
            Result of the connection function if successful
            
        Raises:
            The original exception if all retry attempts fail
        """
        logger.info(f"Attempting to reconnect to {context.server_url} "
                   f"(attempt {context.connection_attempts + 1}/{self.max_retries})")
        
        # Increment attempt count
        context.increment_attempts()
        
        # Calculate delay with exponential backoff
        delay = self.retry_delay * (self.backoff_factor ** (context.connection_attempts - 1))
        
        # Wait before retrying
        if delay > 0:
            logger.info(f"Waiting {delay:.2f} seconds before retrying")
            await asyncio.sleep(delay)
        
        # Try to connect
        try:
            result = await connection_func(*args, **kwargs)
            
            # Reset circuit breaker on successful connection
            circuit_breaker = self.get_circuit_breaker(context.server_url)
            circuit_breaker.state = "closed"
            circuit_breaker.failure_count = 0
            
            logger.info(f"Successfully reconnected to {context.server_url} "
                      f"after {context.connection_attempts} attempts")
            
            return result
            
        except Exception as e:
            # Connection failed again
            logger.error(f"Reconnection attempt {context.connection_attempts} "
                        f"failed for {context.server_url}: {e}")
            
            # Check if we should retry
            if context.connection_attempts < self.max_retries:
                # Update error context before retrying
                context.increment_attempts()
                
                # Retry again
                return await self._retry_connection(
                    context, connection_func, *args, **kwargs
                )
            else:
                # All retry attempts failed
                logger.error(f"All reconnection attempts failed for {context.server_url}")
                
                # Create detailed error message
                error_message = (
                    f"Failed to connect to {context.server_url} after "
                    f"{context.connection_attempts} attempts. "
                    f"Last error: {e}. "
                    f"Error type: {context.error_type.value}. "
                    f"Please check the server status and network connection."
                )
                
                # Raise a new exception with detailed information
                raise ConnectionError(error_message) from e


class ConnectionError(Exception):
    """Exception raised when connection fails after retries."""
    
    def __init__(self, message: str, context: Optional[ConnectionErrorContext] = None):
        """
        Initialize connection error.
        
        Args:
            message: Error message
            context: Connection error context
        """
        super().__init__(message)
        self.context = context
        
    def __str__(self) -> str:
        """Return string representation of the error."""
        if self.context:
            return f"{super().__str__()} (Error type: {self.context.error_type.value})"
        return super().__str__()