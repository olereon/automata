#!/usr/bin/env python3.11
"""
Script to get detailed information about the login button on the Freepik login page.
"""

import asyncio
import json
from src.automata.tools.browser_explorer import BrowserExplorer

async def test_freepik_login_button():
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
        
        # Enter email
        await explorer.current_page.fill("xpath=//div/label/input[@name='email']", "test@example.com")
        
        # Enter password
        await explorer.current_page.fill("xpath=//div/label/input[@name='password']", "testpassword")
        
        # Take a screenshot
        await explorer.take_screenshot("freepik_login_form.png")
        
        # Find all interactive elements on the login form
        elements = await explorer.find_interactive_elements()
        
        # Look for login-related elements
        login_elements = []
        for element in elements:
            text = element.get('text', '').lower()
            if 'login' in text or 'sign' in text or 'submit' in text or 'log in' in text:
                login_elements.append(element)
        
        print(f"\nFound {len(login_elements)} potential login-related elements:")
        for i, element in enumerate(login_elements):
            print(f"\n{i+1}. {element['tag']}: {element['text'][:100]}...")
            print("   Selectors:")
            for sel_type, sel_value in element['selectors'].items():
                print(f"     {sel_type}: {sel_value}")
        
        # Save login elements to a file
        with open("freepik_login_elements.json", "w") as f:
            json.dump(login_elements, f, indent=2)
        
        print("\nLogin elements saved to freepik_login_elements.json")
        
        # Get detailed information about the submit button
        submit_button = await explorer.current_page.query_selector("button[type='submit']")
        
        if submit_button:
            # Get all attributes
            attributes = await submit_button.evaluate("el => { const attrs = {}; for (let i = 0; i < el.attributes.length; i++) { attrs[el.attributes[i].name] = el.attributes[i].value; } return attrs; }")
            
            # Get inner HTML
            inner_html = await submit_button.evaluate("el => el.innerHTML")
            
            # Get outer HTML
            outer_html = await submit_button.evaluate("el => el.outerHTML")
            
            # Check if button is disabled
            is_disabled = await submit_button.is_disabled()
            
            button_info = {
                "tag": "button",
                "attributes": attributes,
                "inner_html": inner_html,
                "outer_html": outer_html,
                "is_disabled": is_disabled
            }
            
            # Save button info to a file
            with open("freepik_submit_button_info.json", "w") as f:
                json.dump(button_info, f, indent=2)
            
            print("\nSubmit button information saved to freepik_submit_button_info.json")
            print(f"Is disabled: {is_disabled}")
            print(f"Attributes: {attributes}")
        else:
            print("\nSubmit button not found")
        
    finally:
        # Stop the browser
        await explorer.stop()

if __name__ == "__main__":
    asyncio.run(test_freepik_login_button())
