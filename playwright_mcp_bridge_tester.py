"""
Comprehensive tester for Playwright MCP Bridge extension connection implementation.
"""

import asyncio
import json
import time
import uuid
from pathlib import Path
from typing import Dict, Any, List, Optional, Union, Tuple

# Add the src directory to the path
import sys
sys.path.insert(0, 'src')

from automata.mcp.bridge_extension_client import MCPBridgeExtensionClient
from automata.mcp.bridge_extension_security import MCPBridgeExtensionSecurity
from automata.mcp.bridge import MCPBridgeConnector
from automata.core.mcp_bridge import MCPBridgeConnector as CoreMCPBridgeConnector
from automata.mcp.config import MCPConfiguration
from automata.core.logger import get_logger

logger = get_logger(__name__)

class PlaywrightMCPBridgeExtensionTester:
    """
    Comprehensive tester for Playwright MCP Bridge extension connection implementation.
    """
    
    def __init__(self, config_file: str = None):
        """
        Initialize the tester.
        
        Args:
            config_file: Path to configuration file
        """
        self.config_file = config_file
        self.config = None
        self.client = None
        self.core_connector = None
        self.bridge_connector = None
        self.test_results = {}
        self.performance_metrics = {}
        
    async def setup(self):
        """Set up the test environment."""
        logger.info("Setting up test environment")
        
        # Load configuration
        if self.config_file:
            self.config = MCPConfiguration.load_from_file(self.config_file)
        else:
            self.config = MCPConfiguration.load_default()
        
        # Initialize clients
        self.client = MCPBridgeExtensionClient(
            websocket_url=self.config.get_bridge_extension_websocket_url(),
            timeout=self.config.get_timeout(),
            retry_attempts=self.config.get_retry_attempts(),
            retry_delay=self.config.get_retry_delay(),
            enable_security=True
        )
        
        self.core_connector = CoreMCPBridgeConnector(config=self.config)
        self.bridge_connector = MCPBridgeConnector(config=self.config)
        
        logger.info("Test environment setup complete")
        
    async def teardown(self):
        """Clean up after tests."""
        logger.info("Tearing down test environment")
        
        # Disconnect clients
        if self.client and await self.client.is_connected():
            await self.client.disconnect()
            
        if self.core_connector and await self.core_connector.is_connected():
            await self.core_connector.disconnect()
            
        if self.bridge_connector and self.bridge_connector.connected:
            await self.bridge_connector.disconnect()
        
        logger.info("Test environment teardown complete")
        
    async def run_all_tests(self):
        """Run all tests."""
        logger.info("Starting all tests")
        
        start_time = time.time()
        
        # Test connection establishment and authentication
        await self.test_connection_establishment()
        
        # Test tab management operations
        await self.test_tab_management()
        
        # Test navigation functionality
        await self.test_navigation()
        
        # Test cookie and LocalStorage management
        await self.test_cookie_storage_management()
        
        # Test screenshot functionality
        await self.test_screenshot_functionality()
        
        # Test connection handling during browser events
        await self.test_connection_handling_during_events()
        
        # Test reconnection logic
        await self.test_reconnection_logic()
        
        # Test cross-platform compatibility
        await self.test_cross_platform_compatibility()
        
        end_time = time.time()
        self.performance_metrics["total_test_time"] = end_time - start_time
        
        logger.info("All tests completed")
        
    async def test_connection_establishment(self):
        """Test connection establishment and authentication."""
        logger.info("Testing connection establishment and authentication")
        
        test_name = "connection_establishment"
        self.test_results[test_name] = {
            "success": False,
            "details": [],
            "errors": []
        }
        
        try:
            # Test basic connection
            start_time = time.time()
            await self.client.connect()
            connection_time = time.time() - start_time
            self.performance_metrics["connection_time"] = connection_time
            
            if not await self.client.is_connected():
                raise Exception("Failed to establish connection")
            
            self.test_results[test_name]["details"].append(f"Connection established in {connection_time:.2f} seconds")
            
            # Test capabilities retrieval
            capabilities = await self.client.get_capabilities()
            self.test_results[test_name]["details"].append(f"Capabilities retrieved: {list(capabilities.keys())}")
            
            # Test core connector connection
            start_time = time.time()
            core_connected = await self.core_connector.connect(test_mode=True)
            core_connection_time = time.time() - start_time
            self.performance_metrics["core_connection_time"] = core_connection_time
            
            if not core_connected:
                raise Exception("Failed to establish core connector connection")
            
            self.test_results[test_name]["details"].append(f"Core connector connection established in {core_connection_time:.2f} seconds")
            
            # Test bridge connector connection
            start_time = time.time()
            bridge_connected = await self.bridge_connector.connect(test_mode=True)
            bridge_connection_time = time.time() - start_time
            self.performance_metrics["bridge_connection_time"] = bridge_connection_time
            
            if not bridge_connected:
                raise Exception("Failed to establish bridge connector connection")
            
            self.test_results[test_name]["details"].append(f"Bridge connector connection established in {bridge_connection_time:.2f} seconds")
            
            self.test_results[test_name]["success"] = True
            
        except Exception as e:
            logger.error(f"Connection establishment test failed: {e}")
            self.test_results[test_name]["errors"].append(str(e))
        
        finally:
            # Disconnect if connected
            if await self.client.is_connected():
                await self.client.disconnect()
            if await self.core_connector.is_connected():
                await self.core_connector.disconnect()
            if self.bridge_connector.connected:
                await self.bridge_connector.disconnect()
    
    async def test_tab_management(self):
        """Test tab management operations."""
        logger.info("Testing tab management operations")
        
        test_name = "tab_management"
        self.test_results[test_name] = {
            "success": False,
            "details": [],
            "errors": []
        }
        
        try:
            # Connect
            await self.client.connect()
            
            # Test list tabs
            start_time = time.time()
            tabs = await self.client.list_tabs()
            list_tabs_time = time.time() - start_time
            self.performance_metrics["list_tabs_time"] = list_tabs_time
            
            self.test_results[test_name]["details"].append(f"Listed {len(tabs)} tabs in {list_tabs_time:.2f} seconds")
            
            # Test create tab
            if len(tabs) > 0:
                initial_tab_count = len(tabs)
            else:
                initial_tab_count = 0
                
            start_time = time.time()
            new_tab = await self.client.create_tab("https://example.com")
            create_tab_time = time.time() - start_time
            self.performance_metrics["create_tab_time"] = create_tab_time
            
            self.test_results[test_name]["details"].append(f"Created new tab in {create_tab_time:.2f} seconds")
            
            # Refresh tabs
            tabs = await self.client.list_tabs()
            if len(tabs) != initial_tab_count + 1:
                raise Exception(f"Expected {initial_tab_count + 1} tabs, got {len(tabs)}")
            
            # Test select tab
            new_tab_id = new_tab.get("tabId")
            if new_tab_id:
                start_time = time.time()
                await self.client.select_tab(new_tab_id)
                select_tab_time = time.time() - start_time
                self.performance_metrics["select_tab_time"] = select_tab_time
                
                self.test_results[test_name]["details"].append(f"Selected tab in {select_tab_time:.2f} seconds")
                
                current_tab = await self.client.get_current_tab()
                if current_tab != new_tab_id:
                    raise Exception(f"Expected tab {new_tab_id} to be selected, got {current_tab}")
            
            # Test reload tab
            if new_tab_id:
                start_time = time.time()
                await self.client.reload_tab(new_tab_id)
                reload_tab_time = time.time() - start_time
                self.performance_metrics["reload_tab_time"] = reload_tab_time
                
                self.test_results[test_name]["details"].append(f"Reloaded tab in {reload_tab_time:.2f} seconds")
            
            # Test close tab
            if new_tab_id:
                start_time = time.time()
                await self.client.close_tab(new_tab_id)
                close_tab_time = time.time() - start_time
                self.performance_metrics["close_tab_time"] = close_tab_time
                
                self.test_results[test_name]["details"].append(f"Closed tab in {close_tab_time:.2f} seconds")
                
                # Refresh tabs
                tabs = await self.client.list_tabs()
                if len(tabs) != initial_tab_count:
                    raise Exception(f"Expected {initial_tab_count} tabs after close, got {len(tabs)}")
            
            self.test_results[test_name]["success"] = True
            
        except Exception as e:
            logger.error(f"Tab management test failed: {e}")
            self.test_results[test_name]["errors"].append(str(e))
        
        finally:
            # Disconnect if connected
            if await self.client.is_connected():
                await self.client.disconnect()
    
    async def test_navigation(self):
        """Test navigation functionality."""
        logger.info("Testing navigation functionality")
        
        test_name = "navigation"
        self.test_results[test_name] = {
            "success": False,
            "details": [],
            "errors": []
        }
        
        try:
            # Connect
            await self.client.connect()
            
            # Create a tab for navigation
            new_tab = await self.client.create_tab()
            tab_id = new_tab.get("tabId")
            
            if tab_id:
                # Select the tab
                await self.client.select_tab(tab_id)
                
                # Test navigate to URL
                start_time = time.time()
                result = await self.client.navigate_to("https://example.com")
                navigate_time = time.time() - start_time
                self.performance_metrics["navigate_time"] = navigate_time
                
                self.test_results[test_name]["details"].append(f"Navigated to example.com in {navigate_time:.2f} seconds")
                
                # Test navigate back (shouldn't work since we just navigated)
                start_time = time.time()
                result = await self.client.navigate_back()
                back_time = time.time() - start_time
                self.performance_metrics["back_time"] = back_time
                
                self.test_results[test_name]["details"].append(f"Navigated back in {back_time:.2f} seconds")
                
                # Test navigate forward (shouldn't work since we just went back)
                start_time = time.time()
                result = await self.client.navigate_forward()
                forward_time = time.time() - start_time
                self.performance_metrics["forward_time"] = forward_time
                
                self.test_results[test_name]["details"].append(f"Navigated forward in {forward_time:.2f} seconds")
                
                # Navigate to another page to test back/forward properly
                await self.client.navigate_to("https://example.org")
                await self.client.navigate_to("https://example.net")
                
                # Navigate back
                start_time = time.time()
                result = await self.client.navigate_back()
                back_time = time.time() - start_time
                self.performance_metrics["back_time_2"] = back_time
                
                self.test_results[test_name]["details"].append(f"Navigated back to example.org in {back_time:.2f} seconds")
                
                # Navigate forward
                start_time = time.time()
                result = await self.client.navigate_forward()
                forward_time = time.time() - start_time
                self.performance_metrics["forward_time_2"] = forward_time
                
                self.test_results[test_name]["details"].append(f"Navigated forward to example.net in {forward_time:.2f} seconds")
                
                # Close the tab
                await self.client.close_tab(tab_id)
            
            self.test_results[test_name]["success"] = True
            
        except Exception as e:
            logger.error(f"Navigation test failed: {e}")
            self.test_results[test_name]["errors"].append(str(e))
        
        finally:
            # Disconnect if connected
            if await self.client.is_connected():
                await self.client.disconnect()
    
    async def test_cookie_storage_management(self):
        """Test cookie and LocalStorage management operations."""
        logger.info("Testing cookie and LocalStorage management")
        
        test_name = "cookie_storage_management"
        self.test_results[test_name] = {
            "success": False,
            "details": [],
            "errors": []
        }
        
        try:
            # Connect
            await self.client.connect()
            
            # Create a tab for testing
            new_tab = await self.client.create_tab("https://example.com")
            tab_id = new_tab.get("tabId")
            
            if tab_id:
                # Select the tab
                await self.client.select_tab(tab_id)
                
                # Test get cookies
                start_time = time.time()
                cookies = await self.client.get_cookies()
                get_cookies_time = time.time() - start_time
                self.performance_metrics["get_cookies_time"] = get_cookies_time
                
                self.test_results[test_name]["details"].append(f"Got {len(cookies)} cookies in {get_cookies_time:.2f} seconds")
                
                # Test set cookies
                test_cookies = [
                    {
                        "name": "test_cookie",
                        "value": "test_value",
                        "domain": "example.com",
                        "path": "/",
                        "expires": -1,
                        "secure": False,
                        "httpOnly": False
                    }
                ]
                
                start_time = time.time()
                result = await self.client.set_cookies(test_cookies)
                set_cookies_time = time.time() - start_time
                self.performance_metrics["set_cookies_time"] = set_cookies_time
                
                self.test_results[test_name]["details"].append(f"Set cookies in {set_cookies_time:.2f} seconds")
                
                # Verify cookies were set
                cookies = await self.client.get_cookies()
                test_cookie_found = any(c.get("name") == "test_cookie" for c in cookies)
                if not test_cookie_found:
                    raise Exception("Test cookie was not set")
                
                # Test clear cookies
                start_time = time.time()
                result = await self.client.clear_cookies()
                clear_cookies_time = time.time() - start_time
                self.performance_metrics["clear_cookies_time"] = clear_cookies_time
                
                self.test_results[test_name]["details"].append(f"Cleared cookies in {clear_cookies_time:.2f} seconds")
                
                # Verify cookies were cleared
                cookies = await self.client.get_cookies()
                test_cookie_found = any(c.get("name") == "test_cookie" for c in cookies)
                if test_cookie_found:
                    raise Exception("Test cookie was not cleared")
                
                # Test LocalStorage operations
                # Test get LocalStorage
                start_time = time.time()
                storage = await self.client.get_local_storage()
                get_storage_time = time.time() - start_time
                self.performance_metrics["get_local_storage_time"] = get_storage_time
                
                self.test_results[test_name]["details"].append(f"Got LocalStorage with {len(storage)} items in {get_storage_time:.2f} seconds")
                
                # Test set LocalStorage
                test_data = {
                    "test_key": "test_value",
                    "another_key": "another_value"
                }
                
                start_time = time.time()
                result = await self.client.set_local_storage(test_data)
                set_storage_time = time.time() - start_time
                self.performance_metrics["set_local_storage_time"] = set_storage_time
                
                self.test_results[test_name]["details"].append(f"Set LocalStorage in {set_storage_time:.2f} seconds")
                
                # Verify LocalStorage was set
                storage = await self.client.get_local_storage()
                if storage.get("test_key") != "test_value" or storage.get("another_key") != "another_value":
                    raise Exception("LocalStorage was not set correctly")
                
                # Test clear LocalStorage
                start_time = time.time()
                result = await self.client.clear_local_storage()
                clear_storage_time = time.time() - start_time
                self.performance_metrics["clear_local_storage_time"] = clear_storage_time
                
                self.test_results[test_name]["details"].append(f"Cleared LocalStorage in {clear_storage_time:.2f} seconds")
                
                # Verify LocalStorage was cleared
                storage = await self.client.get_local_storage()
                if storage.get("test_key") or storage.get("another_key"):
                    raise Exception("LocalStorage was not cleared")
                
                # Close the tab
                await self.client.close_tab(tab_id)
            
            self.test_results[test_name]["success"] = True
            
        except Exception as e:
            logger.error(f"Cookie and LocalStorage management test failed: {e}")
            self.test_results[test_name]["errors"].append(str(e))
        
        finally:
            # Disconnect if connected
            if await self.client.is_connected():
                await self.client.disconnect()
    
    async def test_screenshot_functionality(self):
        """Test screenshot functionality."""
        logger.info("Testing screenshot functionality")
        
        test_name = "screenshot_functionality"
        self.test_results[test_name] = {
            "success": False,
            "details": [],
            "errors": []
        }
        
        try:
            # Connect
            await self.client.connect()
            
            # Create a tab for testing
            new_tab = await self.client.create_tab("https://example.com")
            tab_id = new_tab.get("tabId")
            
            if tab_id:
                # Select the tab
                await self.client.select_tab(tab_id)
                
                # Test take screenshot with default options
                start_time = time.time()
                screenshot = await self.client.take_screenshot()
                screenshot_time = time.time() - start_time
                self.performance_metrics["screenshot_time"] = screenshot_time
                
                self.test_results[test_name]["details"].append(f"Took screenshot in {screenshot_time:.2f} seconds")
                
                if not screenshot or len(screenshot) == 0:
                    raise Exception("Screenshot is empty")
                
                # Test take screenshot with JPEG format
                start_time = time.time()
                screenshot = await self.client.take_screenshot(format="jpeg", quality=90)
                screenshot_jpeg_time = time.time() - start_time
                self.performance_metrics["screenshot_jpeg_time"] = screenshot_jpeg_time
                
                self.test_results[test_name]["details"].append(f"Took JPEG screenshot in {screenshot_jpeg_time:.2f} seconds")
                
                if not screenshot or len(screenshot) == 0:
                    raise Exception("JPEG screenshot is empty")
                
                # Test take screenshot with full page option
                start_time = time.time()
                screenshot = await self.client.take_screenshot(full_page=True)
                screenshot_full_time = time.time() - start_time
                self.performance_metrics["screenshot_full_time"] = screenshot_full_time
                
                self.test_results[test_name]["details"].append(f"Took full page screenshot in {screenshot_full_time:.2f} seconds")
                
                if not screenshot or len(screenshot) == 0:
                    raise Exception("Full page screenshot is empty")
                
                # Test take screenshot with clip option
                clip = {
                    "x": 0,
                    "y": 0,
                    "width": 800,
                    "height": 600
                }
                
                start_time = time.time()
                screenshot = await self.client.take_screenshot(clip=clip)
                screenshot_clip_time = time.time() - start_time
                self.performance_metrics["screenshot_clip_time"] = screenshot_clip_time
                
                self.test_results[test_name]["details"].append(f"Took clipped screenshot in {screenshot_clip_time:.2f} seconds")
                
                if not screenshot or len(screenshot) == 0:
                    raise Exception("Clipped screenshot is empty")
                
                # Close the tab
                await self.client.close_tab(tab_id)
            
            self.test_results[test_name]["success"] = True
            
        except Exception as e:
            logger.error(f"Screenshot functionality test failed: {e}")
            self.test_results[test_name]["errors"].append(str(e))
        
        finally:
            # Disconnect if connected
            if await self.client.is_connected():
                await self.client.disconnect()
    
    async def test_connection_handling_during_events(self):
        """Test connection handling during browser events."""
        logger.info("Testing connection handling during browser events")
        
        test_name = "connection_handling_during_events"
        self.test_results[test_name] = {
            "success": False,
            "details": [],
            "errors": []
        }
        
        try:
            # Connect
            await self.client.connect()
            
            # Create multiple tabs
            tabs = []
            for i in range(3):
                tab = await self.client.create_tab(f"https://example{i+1}.com")
                tabs.append(tab.get("tabId"))
            
            # Test switching between tabs
            for tab_id in tabs:
                start_time = time.time()
                await self.client.select_tab(tab_id)
                switch_time = time.time() - start_time
                self.performance_metrics[f"switch_tab_{tab_id}_time"] = switch_time
                
                self.test_results[test_name]["details"].append(f"Switched to tab {tab_id} in {switch_time:.2f} seconds")
                
                # Verify the tab is selected
                current_tab = await self.client.get_current_tab()
                if current_tab != tab_id:
                    raise Exception(f"Expected tab {tab_id} to be selected, got {current_tab}")
            
            # Test navigating in different tabs
            for i, tab_id in enumerate(tabs):
                await self.client.select_tab(tab_id)
                
                start_time = time.time()
                await self.client.navigate_to(f"https://example{i+1}.org")
                navigate_time = time.time() - start_time
                self.performance_metrics[f"navigate_tab_{tab_id}_time"] = navigate_time
                
                self.test_results[test_name]["details"].append(f"Navigated tab {tab_id} in {navigate_time:.2f} seconds")
            
            # Test closing tabs while connected
            for tab_id in tabs:
                start_time = time.time()
                await self.client.close_tab(tab_id)
                close_time = time.time() - start_time
                self.performance_metrics[f"close_tab_{tab_id}_time"] = close_time
                
                self.test_results[test_name]["details"].append(f"Closed tab {tab_id} in {close_time:.2f} seconds")
            
            # Verify all tabs are closed
            remaining_tabs = await self.client.list_tabs()
            if len(remaining_tabs) != 0:
                raise Exception(f"Expected 0 tabs, got {len(remaining_tabs)}")
            
            self.test_results[test_name]["success"] = True
            
        except Exception as e:
            logger.error(f"Connection handling during events test failed: {e}")
            self.test_results[test_name]["errors"].append(str(e))
        
        finally:
            # Disconnect if connected
            if await self.client.is_connected():
                await self.client.disconnect()
    
    async def test_reconnection_logic(self):
        """Test reconnection logic after connection loss."""
        logger.info("Testing reconnection logic")
        
        test_name = "reconnection_logic"
        self.test_results[test_name] = {
            "success": False,
            "details": [],
            "errors": []
        }
        
        try:
            # Connect
            await self.client.connect()
            
            # Create a tab
            new_tab = await self.client.create_tab("https://example.com")
            tab_id = new_tab.get("tabId")
            
            # Select the tab
            await self.client.select_tab(tab_id)
            
            # Simulate connection loss by disconnecting
            await self.client.disconnect()
            
            # Test reconnection
            start_time = time.time()
            await self.client.connect()
            reconnect_time = time.time() - start_time
            self.performance_metrics["reconnect_time"] = reconnect_time
            
            self.test_results[test_name]["details"].append(f"Reconnected in {reconnect_time:.2f} seconds")
            
            # Verify the connection is restored
            if not await self.client.is_connected():
                raise Exception("Reconnection failed")
            
            # Verify we can still perform operations
            tabs = await self.client.list_tabs()
            self.test_results[test_name]["details"].append(f"Listed {len(tabs)} tabs after reconnection")
            
            # Close the tab
            await self.client.close_tab(tab_id)
            
            self.test_results[test_name]["success"] = True
            
        except Exception as e:
            logger.error(f"Reconnection logic test failed: {e}")
            self.test_results[test_name]["errors"].append(str(e))
        
        finally:
            # Disconnect if connected
            if await self.client.is_connected():
                await self.client.disconnect()
    
    async def test_cross_platform_compatibility(self):
        """Test cross-platform compatibility."""
        logger.info("Testing cross-platform compatibility")
        
        test_name = "cross_platform_compatibility"
        self.test_results[test_name] = {
            "success": False,
            "details": [],
            "errors": []
        }
        
        try:
            # Get platform information
            import platform
            system = platform.system()
            version = platform.version()
            architecture = platform.machine()
            
            self.test_results[test_name]["details"].append(f"Platform: {system} {version} {architecture}")
            
            # Test platform-specific configuration
            if self.client._security:
                platform_config = self.client._security.get_platform_config()
                self.test_results[test_name]["details"].append(f"Platform config: {platform_config}")
            
            # Test connection with platform-specific settings
            await self.client.connect()
            
            # Test basic operations
            tabs = await self.client.list_tabs()
            self.test_results[test_name]["details"].append(f"Listed {len(tabs)} tabs on {system}")
            
            # Create a tab
            new_tab = await self.client.create_tab("https://example.com")
            tab_id = new_tab.get("tabId")
            
            # Select the tab
            await self.client.select_tab(tab_id)
            
            # Take a screenshot
            screenshot = await self.client.take_screenshot()
            if not screenshot or len(screenshot) == 0:
                raise Exception(f"Screenshot is empty on {system}")
            
            self.test_results[test_name]["details"].append(f"Successfully took screenshot on {system}")
            
            # Close the tab
            await self.client.close_tab(tab_id)
            
            self.test_results[test_name]["success"] = True
            
        except Exception as e:
            logger.error(f"Cross-platform compatibility test failed: {e}")
            self.test_results[test_name]["errors"].append(str(e))
        
        finally:
            # Disconnect if connected
            if await self.client.is_connected():
                await self.client.disconnect()
    
    def generate_test_report(self):
        """Generate a comprehensive test report."""
        logger.info("Generating test report")
        
        import platform
        
        report = {
            "test_environment": {
                "platform": platform.system(),
                "platform_version": platform.version(),
                "architecture": platform.machine(),
                "python_version": platform.python_version(),
                "config_file": self.config_file
            },
            "test_results": self.test_results,
            "performance_metrics": self.performance_metrics,
            "summary": {
                "total_tests": len(self.test_results),
                "passed_tests": sum(1 for result in self.test_results.values() if result["success"]),
                "failed_tests": sum(1 for result in self.test_results.values() if not result["success"])
            }
        }
        
        # Calculate overall success rate
        total_tests = report["summary"]["total_tests"]
        passed_tests = report["summary"]["passed_tests"]
        if total_tests > 0:
            success_rate = (passed_tests / total_tests) * 100
            report["summary"]["success_rate"] = f"{success_rate:.2f}%"
        else:
            report["summary"]["success_rate"] = "0%"
        
        # Save report to file
        report_file = f"playwright_mcp_bridge_test_report_{int(time.time())}.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Test report saved to {report_file}")
        
        # Print summary
        print("\n=== Test Summary ===")
        print(f"Total Tests: {total_tests}")
        print(f"Passed Tests: {passed_tests}")
        print(f"Failed Tests: {report['summary']['failed_tests']}")
        print(f"Success Rate: {report['summary']['success_rate']}")
        print(f"Report File: {report_file}")
        
        # Print failed tests
        failed_tests = [name for name, result in self.test_results.items() if not result["success"]]
        if failed_tests:
            print("\n=== Failed Tests ===")
            for test_name in failed_tests:
                print(f"- {test_name}")
                for error in self.test_results[test_name]["errors"]:
                    print(f"  Error: {error}")
        
        return report

async def main():
    """Main function to run the tests."""
    tester = PlaywrightMCPBridgeExtensionTester()
    
    try:
        await tester.setup()
        await tester.run_all_tests()
        report = tester.generate_test_report()
        return report
    except Exception as e:
        logger.error(f"Test execution failed: {e}")
        raise
    finally:
        await tester.teardown()

if __name__ == "__main__":
    asyncio.run(main())
