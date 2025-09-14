"""
Error handling and recovery mechanisms for web automation.
"""

import asyncio
import traceback
from typing import Optional, Dict, Any, Callable, List, Union
from enum import Enum
import logging
from functools import wraps
from playwright.async_api import Page, Error as PlaywrightError

logger = logging.getLogger(__name__)


class AutomationError(Exception):
    """Base exception for automation errors."""
    pass


class ElementNotFoundError(AutomationError):
    """Raised when an element cannot be found."""
    pass


class TimeoutError(AutomationError):
    """Raised when an operation times out."""
    pass


class NavigationError(AutomationError):
    """Raised when navigation fails."""
    pass


class AuthenticationError(AutomationError):
    """Raised when authentication fails."""
    pass


class WorkflowError(AutomationError):
    """Raised when a workflow execution fails."""
    pass


class RecoveryStrategy(Enum):
    """Enumeration of recovery strategies."""
    RETRY = "retry"
    REFRESH = "refresh"
    NAVIGATE_BACK = "navigate_back"
    WAIT_AND_RETRY = "wait_and_retry"
    ALTERNATIVE_SELECTOR = "alternative_selector"
    CUSTOM = "custom"


class ErrorHandler:
    """Handles errors and implements recovery strategies."""

    def __init__(self, max_retries: int = 3, retry_delay: int = 1000):
        """
        Initialize the error handler.

        Args:
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in milliseconds
        """
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.recovery_strategies = {
            RecoveryStrategy.RETRY: self._retry_strategy,
            RecoveryStrategy.REFRESH: self._refresh_strategy,
            RecoveryStrategy.NAVIGATE_BACK: self._navigate_back_strategy,
            RecoveryStrategy.WAIT_AND_RETRY: self._wait_and_retry_strategy,
            RecoveryStrategy.ALTERNATIVE_SELECTOR: self._alternative_selector_strategy,
        }

    def add_recovery_strategy(self, strategy: RecoveryStrategy, handler: Callable) -> None:
        """
        Add a custom recovery strategy.

        Args:
            strategy: The recovery strategy type
            handler: The handler function
        """
        self.recovery_strategies[strategy] = handler

    async def handle_error(
        self,
        error: Exception,
        page: Page,
        context: Optional[Dict[str, Any]] = None,
        strategies: Optional[List[RecoveryStrategy]] = None
    ) -> bool:
        """
        Handle an error with recovery strategies.

        Args:
            error: The exception that occurred
            page: The Playwright Page object
            context: Additional context for error handling
            strategies: List of recovery strategies to try

        Returns:
            True if recovery was successful, False otherwise
        """
        context = context or {}
        strategies = strategies or [
            RecoveryStrategy.WAIT_AND_RETRY,
            RecoveryStrategy.RETRY,
            RecoveryStrategy.REFRESH,
        ]

        logger.error(f"Error occurred: {error}")
        logger.debug(f"Error traceback: {traceback.format_exc()}")

        for strategy in strategies:
            try:
                logger.info(f"Attempting recovery strategy: {strategy.value}")
                handler = self.recovery_strategies.get(strategy)
                if handler:
                    result = await handler(error, page, context)
                    if result:
                        logger.info(f"Recovery successful with strategy: {strategy.value}")
                        return True
            except Exception as recovery_error:
                logger.error(f"Recovery strategy {strategy.value} failed: {recovery_error}")

        logger.error("All recovery strategies failed")
        return False

    async def _retry_strategy(
        self,
        error: Exception,
        page: Page,
        context: Dict[str, Any]
    ) -> bool:
        """
        Retry strategy implementation.

        Args:
            error: The exception that occurred
            page: The Playwright Page object
            context: Additional context for error handling

        Returns:
            True if recovery was successful, False otherwise
        """
        retry_count = context.get("retry_count", 0)
        if retry_count >= self.max_retries:
            return False

        # Get the original function and arguments from context
        func = context.get("function")
        args = context.get("args", [])
        kwargs = context.get("kwargs", {})

        if not func:
            return False

        # Update retry count
        context["retry_count"] = retry_count + 1

        # Wait before retrying
        await asyncio.sleep(self.retry_delay / 1000)

        # Retry the function
        try:
            result = await func(*args, **kwargs)
            context["result"] = result
            return True
        except Exception as e:
            logger.debug(f"Retry {retry_count + 1} failed: {e}")
            return False

    async def _refresh_strategy(
        self,
        error: Exception,
        page: Page,
        context: Dict[str, Any]
    ) -> bool:
        """
        Refresh strategy implementation.

        Args:
            error: The exception that occurred
            page: The Playwright Page object
            context: Additional context for error handling

        Returns:
            True if recovery was successful, False otherwise
        """
        try:
            # Refresh the page
            await page.reload(wait_until="networkidle")
            
            # Get the original function and arguments from context
            func = context.get("function")
            args = context.get("args", [])
            kwargs = context.get("kwargs", {})

            if func:
                result = await func(*args, **kwargs)
                context["result"] = result
                return True
            
            return True
        except Exception as e:
            logger.debug(f"Refresh strategy failed: {e}")
            return False

    async def _navigate_back_strategy(
        self,
        error: Exception,
        page: Page,
        context: Dict[str, Any]
    ) -> bool:
        """
        Navigate back strategy implementation.

        Args:
            error: The exception that occurred
            page: The Playwright Page object
            context: Additional context for error handling

        Returns:
            True if recovery was successful, False otherwise
        """
        try:
            # Navigate back and then forward again
            await page.go_back(wait_until="networkidle")
            await page.go_forward(wait_until="networkidle")
            
            # Get the original function and arguments from context
            func = context.get("function")
            args = context.get("args", [])
            kwargs = context.get("kwargs", {})

            if func:
                result = await func(*args, **kwargs)
                context["result"] = result
                return True
            
            return True
        except Exception as e:
            logger.debug(f"Navigate back strategy failed: {e}")
            return False

    async def _wait_and_retry_strategy(
        self,
        error: Exception,
        page: Page,
        context: Dict[str, Any]
    ) -> bool:
        """
        Wait and retry strategy implementation.

        Args:
            error: The exception that occurred
            page: The Playwright Page object
            context: Additional context for error handling

        Returns:
            True if recovery was successful, False otherwise
        """
        try:
            # Wait longer than the standard retry delay
            await asyncio.sleep((self.retry_delay * 2) / 1000)
            
            # Get the original function and arguments from context
            func = context.get("function")
            args = context.get("args", [])
            kwargs = context.get("kwargs", {})

            if func:
                result = await func(*args, **kwargs)
                context["result"] = result
                return True
            
            return True
        except Exception as e:
            logger.debug(f"Wait and retry strategy failed: {e}")
            return False

    async def _alternative_selector_strategy(
        self,
        error: Exception,
        page: Page,
        context: Dict[str, Any]
    ) -> bool:
        """
        Alternative selector strategy implementation.

        Args:
            error: The exception that occurred
            page: The Playwright Page object
            context: Additional context for error handling

        Returns:
            True if recovery was successful, False otherwise
        """
        try:
            # Get the original selector and function from context
            original_selector = context.get("selector")
            alternative_selectors = context.get("alternative_selectors", [])
            func = context.get("function")
            args = context.get("args", [])
            kwargs = context.get("kwargs", {})

            if not original_selector or not alternative_selectors or not func:
                return False

            # Try each alternative selector
            for selector in alternative_selectors:
                try:
                    # Replace the selector in the arguments
                    if args and isinstance(args[0], str):
                        args[0] = selector
                    elif "selector" in kwargs:
                        kwargs["selector"] = selector

                    # Try the function with the alternative selector
                    result = await func(*args, **kwargs)
                    context["result"] = result
                    context["used_selector"] = selector
                    return True
                except Exception as e:
                    logger.debug(f"Alternative selector {selector} failed: {e}")
                    continue

            return False
        except Exception as e:
            logger.debug(f"Alternative selector strategy failed: {e}")
            return False


def with_error_handling(
    strategies: Optional[List[RecoveryStrategy]] = None,
    max_retries: int = 3,
    retry_delay: int = 1000,
    raise_on_failure: bool = True,
    custom_handler: Optional[Callable] = None
):
    """
    Decorator for adding error handling to async functions.

    Args:
        strategies: List of recovery strategies to try
        max_retries: Maximum number of retry attempts
        retry_delay: Delay between retries in milliseconds
        raise_on_failure: Whether to raise the exception after failed recovery
        custom_handler: Custom error handler function

    Returns:
        Decorator function
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Create error handler
            handler = ErrorHandler(max_retries=max_retries, retry_delay=retry_delay)

            # Prepare context
            context = {
                "function": func,
                "args": args,
                "kwargs": kwargs,
                "retry_count": 0,
            }

            # Add selector to context if it's a selector-based function
            if args and isinstance(args[0], str):
                context["selector"] = args[0]
            elif "selector" in kwargs:
                context["selector"] = kwargs["selector"]

            # Add alternative selectors if provided
            if "alternative_selectors" in kwargs:
                context["alternative_selectors"] = kwargs["alternative_selectors"]

            try:
                # Try the original function
                result = await func(*args, **kwargs)
                return result
            except Exception as error:
                # Try custom handler if provided
                if custom_handler:
                    try:
                        custom_result = await custom_handler(error, *args, **kwargs)
                        if custom_result is not None:
                            return custom_result
                    except Exception as handler_error:
                        logger.error(f"Custom error handler failed: {handler_error}")

                # Try recovery strategies
                recovery_success = await handler.handle_error(
                    error, args[0] if args and hasattr(args[0], "evaluate") else None,
                    context, strategies
                )

                if recovery_success:
                    return context.get("result")
                elif raise_on_failure:
                    raise error
                else:
                    return None

        return wrapper
    return decorator


class CircuitBreaker:
    """Circuit breaker pattern for handling repeated failures."""

    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60000):
        """
        Initialize the circuit breaker.

        Args:
            failure_threshold: Number of failures before opening the circuit
            recovery_timeout: Timeout in milliseconds before attempting recovery
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = 0
        self.state = "closed"  # closed, open, half-open

    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Call a function with circuit breaker protection.

        Args:
            func: Function to call
            *args: Function arguments
            **kwargs: Function keyword arguments

        Returns:
            Result of the function call

        Raises:
            The original exception if the circuit is open
        """
        import time

        if self.state == "open":
            # Check if recovery timeout has elapsed
            if (time.time() * 1000 - self.last_failure_time) > self.recovery_timeout:
                self.state = "half-open"
                logger.info("Circuit breaker transitioning to half-open state")
            else:
                raise AutomationError("Circuit breaker is open")

        try:
            result = await func(*args, **kwargs)
            
            # Reset on success
            if self.state == "half-open":
                self.state = "closed"
                self.failure_count = 0
                logger.info("Circuit breaker reset to closed state")
            
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time() * 1000
            
            if self.failure_count >= self.failure_threshold:
                self.state = "open"
                logger.warning(f"Circuit breaker opened after {self.failure_count} failures")
            
            raise e
