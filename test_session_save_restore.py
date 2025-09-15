#!/usr/bin/env python3.11
"""
Simple test script to verify session save/restore functionality.
"""

import asyncio
import os
import sys
import tempfile
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from automata.core.browser import BrowserManager
from automata.core.session_manager import SessionManager


async def test_session_save_restore():
    """Test session save/restore functionality."""
    print("Testing session save/restore functionality...")
    
    # Create a temporary directory for sessions
    with tempfile.TemporaryDirectory() as temp_dir:
        # Initialize browser manager and session manager
        browser_manager = BrowserManager(headless=True)
        session_manager = SessionManager(session_dir=temp_dir)
        
        try:
            # Start the browser
            await browser_manager.start()
            
            # Create a new page and navigate to a test URL
            page = await browser_manager.new_page("https://httpbin.org/cookies/set?test=value")
            
            # Set some localStorage and sessionStorage
            await page.evaluate("""() => {
                localStorage.setItem('test_local', 'local_value');
                sessionStorage.setItem('test_session', 'session_value');
            }""")
            
            # Save the session
            session_path = await session_manager.save_session(browser_manager, "test_session")
            print(f"Session saved to: {session_path}")
            
            # Verify session file exists
            assert Path(session_path).exists(), "Session file was not created"
            
            # Stop the browser
            await browser_manager.stop()
            
            # Start a new browser
            await browser_manager.start()
            
            # Create a new page (should be empty)
            page2 = await browser_manager.new_page("about:blank")
            
            # Verify cookies are not present
            cookies = await page2.context.cookies()
            assert len(cookies) == 0, f"Expected no cookies, got {len(cookies)}"
            
            # Load the session
            session_loaded = await session_manager.load_session(browser_manager, "test_session")
            print(f"Session loaded: {session_loaded}")
            assert session_loaded, "Failed to load session"
            
            # Create a new page and navigate to the same URL
            page3 = await browser_manager.new_page("https://httpbin.org/cookies")
            
            # Verify cookies are restored
            cookies = await page3.context.cookies()
            assert len(cookies) > 0, f"Expected cookies, got {len(cookies)}"
            
            # Verify localStorage and sessionStorage are restored
            local_value = await page3.evaluate("() => localStorage.getItem('test_local')")
            session_value = await page3.evaluate("() => sessionStorage.getItem('test_session')")
            
            assert local_value == "local_value", f"Expected 'local_value', got {local_value}"
            assert session_value == "session_value", f"Expected 'session_value', got {session_value}"
            
            # Stop the browser
            await browser_manager.stop()
            
            # List sessions
            sessions = await session_manager.list_sessions()
            print(f"Found {len(sessions)} sessions")
            assert len(sessions) > 0, "Expected at least one session"
            
            # Get session info
            session_info = await session_manager.get_session_info("test_session")
            assert session_info is not None, "Expected session info"
            print(f"Session info: {session_info}")
            
            # Delete session
            deleted = await session_manager.delete_session("test_session")
            assert deleted, "Failed to delete session"
            print("Session deleted successfully")
            
            # Verify session is deleted
            sessions = await session_manager.list_sessions()
            assert len(sessions) == 0, f"Expected no sessions, got {len(sessions)}"
            
            print("All tests passed!")
            
        except Exception as e:
            print(f"Test failed: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            # Make sure browser is stopped
            try:
                await browser_manager.stop()
            except:
                pass
    
    return True


async def test_session_encryption():
    """Test session encryption functionality."""
    print("\nTesting session encryption functionality...")
    
    # Create a temporary directory for sessions
    with tempfile.TemporaryDirectory() as temp_dir:
        # Initialize browser manager and session manager with encryption
        browser_manager = BrowserManager(headless=True)
        session_manager = SessionManager(session_dir=temp_dir, encryption_key="test_key")
        
        try:
            # Start the browser
            await browser_manager.start()
            
            # Create a new page and navigate to a test URL
            page = await browser_manager.new_page("https://httpbin.org/cookies/set?secret=value")
            
            # Save the session with encryption
            session_path = await session_manager.save_session(browser_manager, "encrypted_session")
            print(f"Encrypted session saved to: {session_path}")
            
            # Stop the browser
            await browser_manager.stop()
            
            # Try to load with wrong key
            wrong_session_manager = SessionManager(session_dir=temp_dir, encryption_key="wrong_key")
            await browser_manager.start()
            session_loaded = await wrong_session_manager.load_session(browser_manager, "encrypted_session")
            assert not session_loaded, "Session should not load with wrong key"
            await browser_manager.stop()
            
            # Load with correct key
            await browser_manager.start()
            session_loaded = await session_manager.load_session(browser_manager, "encrypted_session")
            assert session_loaded, "Failed to load encrypted session with correct key"
            
            # Verify data is loaded
            page = await browser_manager.new_page("https://httpbin.org/cookies")
            cookies = await page.context.cookies()
            assert len(cookies) > 0, f"Expected cookies, got {len(cookies)}"
            
            print("Encryption test passed!")
            
        except Exception as e:
            print(f"Encryption test failed: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            # Make sure browser is stopped
            try:
                await browser_manager.stop()
            except:
                pass
    
    return True


async def main():
    """Run all tests."""
    print("Running session save/restore tests...")
    
    success = True
    
    # Test basic session save/restore
    success &= await test_session_save_restore()
    
    # Test session encryption
    success &= await test_session_encryption()
    
    if success:
        print("\nAll tests passed!")
        return 0
    else:
        print("\nSome tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))