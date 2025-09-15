#!/usr/bin/env python3.11
"""
Script to test the form validation on the Freepik login page.
"""

import asyncio
import json
from src.automata.tools.browser_explorer import BrowserExplorer

async def test_freepik_form_validation():
    # Create browser explorer in visible mode
    explorer = BrowserExplorer(headless=False)
    
    try:
        # Start the browser
        await explorer.start()
        
        # Navigate to Freepik
        await explorer.navigate("https://www.freepik.com/")
        
        # Click sign-in button
        await explorer.current_page.click("xpath=//a[@data-cy='signin-button']")
        
        # Wait for login page to load
        await explorer.current_page.wait_for_load_state("networkidle")
        
        # Click Continue with email button
        await explorer.current_page.click("css=.main-button.button.button--outline.button--with-icon >> text=Continue with email")
        
        # Wait for email form to load
        await explorer.current_page.wait_for_selector("xpath=//div/label/input[@name='email']")
        
        # Get the submit button
        submit_button = await explorer.current_page.query_selector("css=#submit")
        
        # Check initial state
        is_disabled = await submit_button.is_disabled()
        print(f"Initial button state - Is disabled: {is_disabled}")
        
        # Enter email
        await explorer.current_page.fill("xpath=//div/label/input[@name='email']", "test@example.com")
        
        # Check state after entering email
        is_disabled = await submit_button.is_disabled()
        print(f"After entering email - Is disabled: {is_disabled}")
        
        # Enter password
        await explorer.current_page.fill("xpath=//div/label/input[@name='password']", "testpassword")
        
        # Check state after entering password
        is_disabled = await submit_button.is_disabled()
        print(f"After entering password - Is disabled: {is_disabled}")
        
        # Trigger input events to ensure validation
        await explorer.current_page.evaluate("() => { document.querySelector('input[name=\"email\"]').dispatchEvent(new Event('input', { bubbles: true })); }")
        await explorer.current_page.evaluate("() => { document.querySelector('input[name=\"password\"]').dispatchEvent(new Event('input', { bubbles: true })); }")
        
        # Wait a moment for validation
        await asyncio.sleep(1)
        
        # Check final state
        is_disabled = await submit_button.is_disabled()
        print(f"After triggering events - Is disabled: {is_disabled}")
        
        # Get email and password field values
        email_value = await explorer.current_page.evaluate("() => document.querySelector('input[name=\"email\"]').value")
        password_value = await explorer.current_page.evaluate("() => document.querySelector('input[name=\"password\"]').value")
        
        print(f"Email field value: '{email_value}'")
        print(f"Password field value: '{password_value}'")
        
        # Check if there are any validation error messages
        error_elements = await explorer.current_page.query_selector_all(".error, .form-error, [class*='error'], [class*='invalid']")
        print(f"Found {len(error_elements)} error elements")
        
        for i, error in enumerate(error_elements):
            error_text = await error.text_content()
            print(f"Error {i+1}: {error_text}")
        
        # Take a screenshot
        await explorer.take_screenshot("freepik_form_validation.png")
        
        # Try clicking the login button with JavaScript
        try:
            await explorer.current_page.evaluate("() => document.querySelector('#submit').click()")
            print("Successfully clicked login button with JavaScript")
        except Exception as e:
            print(f"Error clicking login button with JavaScript: {e}")
        
    finally:
        # Stop the browser
        await explorer.stop()

if __name__ == "__main__":
    asyncio.run(test_freepik_form_validation())
