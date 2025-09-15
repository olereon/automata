#!/usr/bin/env python3.11
"""
Script to test the Freepik website and identify the correct selectors.
"""

import asyncio
import json
from src.automata.tools.browser_explorer import BrowserExplorer

async def test_freepik():
    # Create browser explorer in visible mode
    explorer = BrowserExplorer(headless=False)
    
    try:
        # Start the browser
        await explorer.start()
        
        # Navigate to Freepik
        await explorer.navigate("https://www.freepik.com/")
        
        # Find all interactive elements
        elements = await explorer.find_interactive_elements()
        
        # Print the elements
        print(f"Found {len(elements)} interactive elements:")
        for i, element in enumerate(elements):
            print(f"\n{i+1}. {element['tag']}: {element['text'][:50]}...")
            print("   Selectors:")
            for sel_type, sel_value in element['selectors'].items():
                print(f"     {sel_type}: {sel_value}")
        
        # Save elements to a file for analysis
        with open("freepik_elements.json", "w") as f:
            json.dump(elements, f, indent=2)
        
        print("\nElements saved to freepik_elements.json")
        
        # Take a screenshot
        await explorer.take_screenshot("freepik_homepage.png")
        
        # Look for sign-in related elements
        sign_in_elements = []
        for element in elements:
            text = element.get('text', '').lower()
            if 'sign' in text or 'login' in text or 'account' in text or 'profile' in text:
                sign_in_elements.append(element)
        
        print(f"\nFound {len(sign_in_elements)} potential sign-in related elements:")
        for i, element in enumerate(sign_in_elements):
            print(f"\n{i+1}. {element['tag']}: {element['text'][:50]}...")
            print("   Selectors:")
            for sel_type, sel_value in element['selectors'].items():
                print(f"     {sel_type}: {sel_value}")
        
        # Save sign-in elements to a file
        with open("freepik_signin_elements.json", "w") as f:
            json.dump(sign_in_elements, f, indent=2)
        
        print("\nSign-in elements saved to freepik_signin_elements.json")
        
    finally:
        # Stop the browser
        await explorer.stop()

if __name__ == "__main__":
    asyncio.run(test_freepik())
