#!/usr/bin/env python3.11
"""
Script to get detailed information about the email button on the Freepik login page.
"""

import asyncio
import json
from src.automata.tools.browser_explorer import BrowserExplorer

async def test_freepik_email_button():
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
        
        # Get detailed information about the email button
        email_button = await explorer.current_page.query_selector("button:has-text('Continue with email')")
        
        if email_button:
            # Get all attributes
            attributes = await email_button.evaluate("el => { const attrs = {}; for (let i = 0; i < el.attributes.length; i++) { attrs[el.attributes[i].name] = el.attributes[i].value; } return attrs; }")
            
            # Get inner HTML
            inner_html = await email_button.evaluate("el => el.innerHTML")
            
            # Get outer HTML
            outer_html = await email_button.evaluate("el => el.outerHTML")
            
            # Get computed styles
            styles = await email_button.evaluate("el => { const styles = {}; const computed = getComputedStyle(el); for (let i = 0; i < computed.length; i++) { styles[computed[i]] = computed.getPropertyValue(computed[i]); } return styles; }")
            
            # Get position and size
            bounding_box = await email_button.bounding_box()
            
            button_info = {
                "tag": "button",
                "text": "Continue with email",
                "attributes": attributes,
                "inner_html": inner_html,
                "outer_html": outer_html,
                "styles": styles,
                "bounding_box": bounding_box
            }
            
            # Save button info to a file
            with open("freepik_email_button_info.json", "w") as f:
                json.dump(button_info, f, indent=2)
            
            print("Email button information saved to freepik_email_button_info.json")
            print(f"Attributes: {attributes}")
        else:
            print("Email button not found")
        
    finally:
        # Stop the browser
        await explorer.stop()

if __name__ == "__main__":
    asyncio.run(test_freepik_email_button())
