
"""
Interactive browser exploration tool for web automation.
"""

import asyncio
import json
import logging
import os
from pathlib import Path
from typing import Optional, Dict, Any, List
from playwright.async_api import Page, ElementHandle, Locator
from click import echo, style, prompt, confirm

from ..core.browser import BrowserManager
from ..auth.session import SessionAuthProvider, CookieManager
from ..core.logger import get_logger

logger = get_logger(__name__)


class BrowserExplorer:
    """Interactive browser exploration tool with session management."""

    def __init__(self, headless: bool = False):
        """
        Initialize the browser explorer.

        Args:
            headless: Whether to run browser in headless mode
        """
        self.browser_manager = BrowserManager(headless=headless)
        self.session_auth = SessionAuthProvider()
        self.cookie_manager = CookieManager()
        self.current_page: Optional[Page] = None
        self.session_id: Optional[str] = None

    async def start(self) -> None:
        """Start the browser explorer."""
        await self.browser_manager.start()
        echo(style("Browser started successfully!", fg="green"))

    async def stop(self) -> None:
        """Stop the browser explorer."""
        await self.browser_manager.stop()
        echo(style("Browser stopped successfully!", fg="green"))

    async def navigate(self, url: str) -> None:
        """
        Navigate to a URL.

        Args:
            url: URL to navigate to
        """
        if not self.browser_manager.current_page:
            self.current_page = await self.browser_manager.new_page(url)
        else:
            await self.current_page.goto(url)
        echo(style(f"Navigated to: {url}", fg="blue"))

    async def save_session(self, session_id: str, username: Optional[str] = None) -> str:
        """
        Save the current browser session.

        Args:
            session_id: ID for the session
            username: Username associated with the session

        Returns:
            Path to the saved session file
        """
        if not self.browser_manager.context:
            raise RuntimeError("Browser not started or no context available")

        session_path = await self.session_auth.save_session(
            session_id=session_id,
            context=self.browser_manager.context,
            username=username
        )
        self.session_id = session_id
        echo(style(f"Session saved with ID: {session_id}", fg="green"))
        return session_path

    async def load_session(self, session_id: str) -> bool:
        """
        Load a saved browser session.

        Args:
            session_id: ID of the session to load

        Returns:
            True if successful, False otherwise
        """
        if not self.browser_manager.context:
            raise RuntimeError("Browser not started or no context available")

        result = await self.session_auth.authenticate(
            session_id=session_id,
            context=self.browser_manager.context
        )
        
        if result.success:
            self.session_id = session_id
            echo(style(f"Session loaded with ID: {session_id}", fg="green"))
            return True
        else:
            echo(style(f"Failed to load session: {result.message}", fg="red"))
            return False

    async def delete_session(self, session_id: str) -> bool:
        """
        Delete a saved session.

        Args:
            session_id: ID of the session to delete

        Returns:
            True if successful, False otherwise
        """
        success = await self.session_auth.delete_session(session_id)
        if success:
            echo(style(f"Session deleted with ID: {session_id}", fg="green"))
            if self.session_id == session_id:
                self.session_id = None
        else:
            echo(style(f"Failed to delete session: {session_id}", fg="red"))
        return success

    async def list_sessions(self) -> List[Dict[str, Any]]:
        """
        List all available sessions.

        Returns:
            List of session information
        """
        sessions = await self.session_auth.list_sessions()
        echo(style(f"Found {len(sessions)} sessions:", fg="blue"))
        for session in sessions:
            status = "Expired" if session.get("is_expired", False) else "Active"
            echo(f"  - {session['session_id']}: {session.get('username', 'N/A')} ({status})")
        return sessions

    async def get_element_info(self, selector: str) -> Dict[str, Any]:
        """
        Get information about an element.

        Args:
            selector: CSS selector for the element

        Returns:
            Element information
        """
        if not self.current_page:
            raise RuntimeError("No page available")

        try:
            element = await self.current_page.query_selector(selector)
            if not element:
                return {"error": "Element not found"}

            # Get basic element properties
            tag_name = await element.evaluate("el => el.tagName.toLowerCase()")
            text_content = await element.evaluate("el => el.textContent")
            inner_html = await element.evaluate("el => el.innerHTML")
            outer_html = await element.evaluate("el => el.outerHTML")

            # Get attributes
            attributes = await element.evaluate("el => { const attrs = {}; for (let i = 0; i < el.attributes.length; i++) { attrs[el.attributes[i].name] = el.attributes[i].value; } return attrs; }")

            # Get computed styles
            styles = await element.evaluate("el => { const styles = {}; const computed = getComputedStyle(el); for (let i = 0; i < computed.length; i++) { styles[computed[i]] = computed.getPropertyValue(computed[i]); } return styles; }")

            # Get position and size
            bounding_box = await element.bounding_box()

            return {
                "selector": selector,
                "tag_name": tag_name,
                "text_content": text_content,
                "inner_html": inner_html,
                "outer_html": outer_html,
                "attributes": attributes,
                "styles": styles,
                "bounding_box": bounding_box
            }
        except Exception as e:
            return {"error": str(e)}

    async def generate_selectors(self, element_handle: ElementHandle) -> Dict[str, str]:
        """
        Generate multiple types of selectors for an element.

        Args:
            element_handle: Playwright element handle

        Returns:
            Dictionary with different selector types
        """
        selectors = {}

        # Get tag name
        tag_name = await element_handle.evaluate("el => el.tagName.toLowerCase()")

        # Get ID
        element_id = await element_handle.get_attribute("id")
        if element_id:
            selectors["id"] = f"#{element_id}"

        # Get classes
        classes = await element_handle.get_attribute("class")
        if classes:
            class_list = classes.split()
            if class_list:
                selectors["class"] = "." + ".".join(class_list)

        # Generate XPath
        try:
            xpath = await element_handle.evaluate("el => { const node = el; let path = ''; while (node && node.nodeType === Node.ELEMENT_NODE) { let index = 0; let sibling = node.previousSibling; while (sibling) { if (sibling.nodeType === Node.ELEMENT_NODE && sibling.tagName === node.tagName) { index++; } sibling = sibling.previousSibling; } const tagName = node.tagName.toLowerCase(); const pathIndex = index > 0 ? `[${index + 1}]` : ''; path = '/' + tagName + pathIndex + path; node = node.parentNode; } return path; }")
            selectors["xpath"] = xpath
        except:
            pass

        # Generate attributes-based selector
        attributes = await element_handle.evaluate("el => { const attrs = {}; for (let i = 0; i < el.attributes.length; i++) { attrs[el.attributes[i].name] = el.attributes[i].value; } return attrs; }")
        if attributes:
            attr_selectors = []
            for attr, value in attributes.items():
                if attr not in ["class", "id"]:
                    attr_selectors.append(f"[{attr}='{value}']")
            if attr_selectors:
                selectors["attributes"] = tag_name + "".join(attr_selectors)

        return selectors

    async def find_interactive_elements(self) -> List[Dict[str, Any]]:
        """
        Find all interactive elements on the page.

        Returns:
            List of interactive elements with their selectors
        """
        if not self.current_page:
            raise RuntimeError("No page available")

        elements = []

        # Find all clickable elements
        clickable_selectors = [
            "button",
            "input[type='button']",
            "input[type='submit']",
            "input[type='reset']",
            "a[href]",
            "[role='button']",
            "[onclick]",
            ".btn",
            ".button"
        ]

        for selector in clickable_selectors:
            try:
                element_handles = await self.current_page.query_selector_all(selector)
                for handle in element_handles:
                    selectors = await self.generate_selectors(handle)
                    text_content = await handle.evaluate("el => el.textContent")
                    
                    element_info = {
                        "tag": await handle.evaluate("el => el.tagName.toLowerCase()"),
                        "text": text_content,
                        "selectors": selectors
                    }
                    
                    # Get bounding box for position info
                    try:
                        bbox = await handle.bounding_box()
                        if bbox:
                            element_info["position"] = {
                                "x": bbox["x"],
                                "y": bbox["y"],
                                "width": bbox["width"],
                                "height": bbox["height"]
                            }
                    except:
                        pass
                    
                    elements.append(element_info)
            except Exception as e:
                logger.warning(f"Error finding elements with selector '{selector}': {e}")

        return elements

    async def highlight_element(self, selector: str, duration: int = 3000) -> None:
        """
        Highlight an element on the page.

        Args:
            selector: CSS selector for the element
            duration: Duration to highlight in milliseconds
        """
        if not self.current_page:
            raise RuntimeError("No page available")

        try:
            element = await self.current_page.query_selector(selector)
            if element:
                await element.evaluate("""
                    (element, duration) => {
                        const originalStyle = element.style.cssText;
                        element.style.cssText += 'outline: 2px solid red; outline-offset: 2px; background-color: rgba(255, 0, 0, 0.2);';
                        setTimeout(() => {
                            element.style.cssText = originalStyle;
                        }, duration);
                    }
                """, duration)
                echo(style(f"Element highlighted for {duration}ms", fg="blue"))
            else:
                echo(style("Element not found", fg="red"))
        except Exception as e:
            echo(style(f"Error highlighting element: {e}", fg="red"))

    async def take_screenshot(self, path: Optional[str] = None) -> str:
        """
        Take a screenshot of the current page.

        Args:
            path: Path to save the screenshot

        Returns:
            Path to the saved screenshot
        """
        if not self.current_page:
            raise RuntimeError("No page available")

        if not path:
            path = f"screenshot_{int(asyncio.get_event_loop().time())}.png"

        await self.current_page.screenshot(path=path)
        echo(style(f"Screenshot saved to: {path}", fg="green"))
        return path

    async def run_interactive(self) -> None:
        """Run the interactive browser explorer."""
        echo(style("=== Interactive Browser Explorer ===", fg="blue"))
        echo("Available commands:")
        echo("  navigate <url>     - Navigate to a URL")
        echo("  find              - Find all interactive elements")
        echo("  info <selector>   - Get information about an element")
        echo("  highlight <sel>   - Highlight an element")
        echo("  screenshot        - Take a screenshot")
        echo("  save <id> [user]  - Save current session")
        echo("  load <id>         - Load a saved session")
        echo("  delete <id>       - Delete a session")
        echo("  list              - List all sessions")
        echo("  help              - Show this help")
        echo("  quit              - Exit the explorer")

        while True:
            try:
                command = prompt("\n> ").strip()
                if not command:
                    continue

                parts = command.split()
                cmd = parts[0].lower()
                args = parts[1:]

                if cmd == "quit":
                    echo(style("Exiting browser explorer...", fg="yellow"))
                    break

                elif cmd == "help":
                    echo("Available commands:")
                    echo("  navigate <url>     - Navigate to a URL")
                    echo("  find              - Find all interactive elements")
                    echo("  info <selector>   - Get information about an element")
                    echo("  highlight <sel>   - Highlight an element")
                    echo("  screenshot        - Take a screenshot")
                    echo("  save <id> [user]  - Save current session")
                    echo("  load <id>         - Load a saved session")
                    echo("  delete <id>       - Delete a session")
                    echo("  list              - List all sessions")
                    echo("  help              - Show this help")
                    echo("  quit              - Exit the explorer")

                elif cmd == "navigate":
                    if len(args) != 1:
                        echo(style("Usage: navigate <url>", fg="red"))
                        continue
                    await self.navigate(args[0])

                elif cmd == "find":
                    elements = await self.find_interactive_elements()
                    echo(style(f"Found {len(elements)} interactive elements:", fg="blue"))
                    for i, element in enumerate(elements):
                        echo(f"\n{i+1}. {element['tag']}: {element['text'][:50]}...")
                        echo("   Selectors:")
                        for sel_type, sel_value in element['selectors'].items():
                            echo(f"     {sel_type}: {sel_value}")
                        if 'position' in element:
                            pos = element['position']
                            echo(f"     Position: x={pos['x']}, y={pos['y']}, size={pos['width']}x{pos['height']}")

                elif cmd == "info":
                    if len(args) != 1:
                        echo(style("Usage: info <selector>", fg="red"))
                        continue
                    info = await self.get_element_info(args[0])
                    if "error" in info:
                        echo(style(f"Error: {info['error']}", fg="red"))
                    else:
                        echo(style("Element information:", fg="blue"))
                        echo(f"  Tag: {info['tag_name']}")
                        echo(f"  Text: {info['text_content'][:100]}...")
                        echo("  Attributes:")
                        for attr, value in info['attributes'].items():
                            echo(f"    {attr}: {value}")
                        if info['bounding_box']:
                            bbox = info['bounding_box']
                            echo(f"  Position: x={bbox['x']}, y={bbox['y']}, size={bbox['width']}x{bbox['height']}")

                elif cmd == "highlight":
                    if len(args) != 1:
                        echo(style("Usage: highlight <selector>", fg="red"))
                        continue
                    await self.highlight_element(args[0])

                elif cmd == "screenshot":
                    await self.take_screenshot()

                elif cmd == "save":
                    if not args:
                        echo(style("Usage: save <session_id> [username]", fg="red"))
                        continue
                    session_id = args[0]
                    username = args[1] if len(args) > 1 else None
                    await self.save_session(session_id, username)

                elif cmd == "load":
                    if len(args) != 1:
                        echo(style("Usage: load <session_id>", fg="red"))
                        continue
                    await self.load_session(args[0])

                elif cmd == "delete":
                    if len(args) != 1:
                        echo(style("Usage: delete <session_id>", fg="red"))
                        continue
                    await self.delete_session(args[0])

                elif cmd == "list":
                    await self.list_sessions()

                else:
                    echo(style(f"Unknown command: {cmd}", fg="red"))
                    echo("Type 'help' for available commands")

            except KeyboardInterrupt:
                echo(style("\nExiting browser explorer...", fg="yellow"))
                break
            except Exception as e:
                echo(style(f"Error: {e}", fg="red"))