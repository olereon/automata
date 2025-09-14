"""
Interactive utilities for prompting user input.
"""

from typing import Optional, List, Any
from ..core.logger import get_logger

logger = get_logger(__name__)


def prompt_user(prompt: str, optional: bool = False) -> str:
    """
    Prompt the user for input.
    
    Args:
        prompt: The prompt to display
        optional: Whether the input is optional
        
    Returns:
        User input string
    """
    try:
        if optional:
            prompt += " (optional): "
        else:
            prompt += ": "
            
        return input(prompt).strip()
    
    except Exception as e:
        logger.error(f"Error prompting user: {e}")
        raise


def prompt_choice(prompt: str, choices: List[str]) -> str:
    """
    Prompt the user to choose from a list of options.
    
    Args:
        prompt: The prompt to display
        choices: List of choices
        
    Returns:
        Selected choice
    """
    try:
        print(f"\n{prompt}")
        for i, choice in enumerate(choices, 1):
            print(f"{i}. {choice}")
        
        while True:
            try:
                selection = input(f"Enter choice (1-{len(choices)}): ").strip()
                index = int(selection) - 1
                
                if 0 <= index < len(choices):
                    return choices[index]
                else:
                    print(f"Invalid choice. Please enter a number between 1 and {len(choices)}.")
            
            except ValueError:
                print("Invalid input. Please enter a number.")
    
    except Exception as e:
        logger.error(f"Error prompting choice: {e}")
        raise


def prompt_yes_no(prompt: str) -> bool:
    """
    Prompt the user for a yes/no response.
    
    Args:
        prompt: The prompt to display
        
    Returns:
        True for yes, False for no
    """
    try:
        while True:
            response = input(f"{prompt} (y/n): ").strip().lower()
            
            if response in ['y', 'yes']:
                return True
            elif response in ['n', 'no']:
                return False
            else:
                print("Please enter 'y' or 'n'.")
    
    except Exception as e:
        logger.error(f"Error prompting yes/no: {e}")
        raise