#!/usr/bin/env python3.11
"""
Test script to directly load credentials from JSON file and execute workflow.
"""

import asyncio
import json
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from automata.core.browser import BrowserManager
from automata.workflow import WorkflowBuilder, WorkflowExecutionEngine
from automata.core.logger import get_logger

logger = get_logger(__name__)

async def main():
    try:
        # Load credentials directly from JSON file
        credentials_path = "credentials/credentials.json"
        
        print(f"CREDENTIAL_DEBUG: Loading credentials from: {credentials_path}")
        
        with open(credentials_path, "r", encoding="utf-8") as f:
            credentials_data = json.load(f)
        
        print(f"CREDENTIAL_DEBUG: Credentials data: {credentials_data}")
        
        # Initialize workflow execution engine with visible browser
        engine = WorkflowExecutionEngine(browser_manager=BrowserManager(headless=False))
        
        # Inject credentials into variable manager
        print(f"CREDENTIAL_DEBUG: Injecting credentials into variable manager")
        engine.variable_manager.bulk_set_variables(credentials_data)
        
        # List all variables after injection
        all_vars = engine.variable_manager.list_variables()
        print(f"CREDENTIAL_DEBUG: All variables after credential injection: {all_vars}")
        
        # Load workflow
        builder = WorkflowBuilder()
        workflow = builder.load_workflow("workflows/freep_login.json")
        
        # Execute workflow
        print("Executing workflow...")
        results = await engine.execute_workflow(workflow)
        
        # Print results
        print(f"Workflow executed successfully with {len(results)} steps")
        
        # Print execution summary
        completed = sum(1 for r in results if r.get("status") == "completed")
        failed = sum(1 for r in results if r.get("status") == "failed")
        skipped = sum(1 for r in results if r.get("status") == "skipped")
        
        print(f"Completed: {completed}, Failed: {failed}, Skipped: {skipped}")
        
        # Print failed steps if any
        if failed > 0:
            print("\nFailed steps:")
            for result in results:
                if result.get("status") == "failed":
                    print(f"  - {result.get('step_name')}: {result.get('error')}")
        
        return 0
    
    except Exception as e:
        print(f"Error executing workflow: {e}")
        return 1

if __name__ == '__main__':
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
