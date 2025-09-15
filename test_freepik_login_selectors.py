#!/usr/bin/env python3.11
"""
Script to test the Freepik login page and identify the correct selectors.
"""

import asyncio
import json
from src.automata.tools.browser_explorer import BrowserExplorer

async def test_freepik_login():
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
        
        # Take a screenshot
        await explorer.take_screenshot("freepik_login_page.png")
        
        # Find all interactive elements on the login page
        elements = await explorer.find_interactive_elements()
        
        # Print the elements
        print(f"Found {len(elements)} interactive elements on the login page:")
        
        # Look for email-related elements
        email_elements = []
        for element in elements:
            text = element.get('text', '').lower()
            if 'email' in text or 'continue' in text:
                email_elements.append(element)
        
        print(f"\nFound {len(email_elements)} potential email-related elements:")
        for i, element in enumerate(email_elements):
            print(f"\n{i+1}. {element['tag']}: {element['text'][:100]}...")
            print("   Selectors:")
            for sel_type, sel_value in element['selectors'].items():
                print(f"     {sel_type}: {sel_value}")
        
        # Save email elements to a file
        with open("freepik_login_email_elements.json", "w") as f:
            json.dump(email_elements, f, indent=2)
        
        print("\nEmail elements saved to freepik_login_email_elements.json")
        
    finally:
        # Stop the browser
        await explorer.stop()

if __name__ == "__main__":
    asyncio.run(test_freepik_login())
