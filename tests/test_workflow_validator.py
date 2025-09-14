"""
Unit tests for the workflow validator component.
"""

import pytest
from src.automata.workflow.validator import WorkflowValidator
from src.automata.workflow.schema import WorkflowSchema
from src.automata.core.errors import AutomationError


@pytest.mark.unit
class TestWorkflowValidator:
    """Test cases for WorkflowValidator."""

    def test_init(self):
        """Test WorkflowValidator initialization."""
        schema = WorkflowSchema()
        validator = WorkflowValidator(schema)
        assert validator is not None
        assert validator.schema is schema
        assert validator.errors == []
        assert validator.warnings == []

    def test_validate_workflow_valid(self):
        """Test validating a valid workflow."""
        schema = WorkflowSchema()
        validator = WorkflowValidator(schema)
        
        # Valid workflow
        workflow = {
            "name": "Test Workflow",
            "version": "1.0.0",
            "description": "A test workflow",
            "variables": {},
            "steps": [
                {
                    "name": "Step 1",
                    "action": "navigate",
                    "value": "https://example.com"
                }
            ]
        }
        
        # Test
        is_valid = validator.validate_workflow(workflow)
        
        # Verify
        assert is_valid is True
        assert validator.errors == []

    def test_validate_workflow_missing_name(self):
        """Test validating a workflow with missing name."""
        schema = WorkflowSchema()
        validator = WorkflowValidator(schema)
        
        # Invalid workflow (missing name)
        workflow = {
            "version": "1.0.0",
            "description": "A test workflow",
            "variables": {},
            "steps": [
                {
                    "name": "Step 1",
                    "action": "navigate",
                    "value": "https://example.com"
                }
            ]
        }
        
        # Test
        is_valid = validator.validate_workflow(workflow)
        
        # Verify
        assert is_valid is False
        assert len(validator.errors) > 0
        assert any("name" in error for error in validator.errors)

    def test_validate_workflow_missing_version(self):
        """Test validating a workflow with missing version."""
        schema = WorkflowSchema()
        validator = WorkflowValidator(schema)
        
        # Invalid workflow (missing version)
        workflow = {
            "name": "Test Workflow",
            "description": "A test workflow",
            "variables": {},
            "steps": [
                {
                    "name": "Step 1",
                    "action": "navigate",
                    "value": "https://example.com"
                }
            ]
        }
        
        # Test
        is_valid = validator.validate_workflow(workflow)
        
        # Verify
        assert is_valid is False
        assert len(validator.errors) > 0
        assert any("version" in error for error in validator.errors)

    def test_validate_workflow_missing_steps(self):
        """Test validating a workflow with missing steps."""
        schema = WorkflowSchema()
        validator = WorkflowValidator(schema)
        
        # Invalid workflow (missing steps)
        workflow = {
            "name": "Test Workflow",
            "version": "1.0.0",
            "description": "A test workflow",
            "variables": {}
        }
        
        # Test
        is_valid = validator.validate_workflow(workflow)
        
        # Verify
        assert is_valid is False
        assert len(validator.errors) > 0
        assert any("steps" in error for error in validator.errors)

    def test_validate_workflow_empty_steps(self):
        """Test validating a workflow with empty steps."""
        schema = WorkflowSchema()
        validator = WorkflowValidator(schema)
        
        # Invalid workflow (empty steps)
        workflow = {
            "name": "Test Workflow",
            "version": "1.0.0",
            "description": "A test workflow",
            "variables": {},
            "steps": []
        }
        
        # Test
        is_valid = validator.validate_workflow(workflow)
        
        # Verify
        assert is_valid is False
        assert len(validator.errors) > 0
        assert any("steps" in error for error in validator.errors)

    def test_validate_workflow_invalid_step(self):
        """Test validating a workflow with invalid step."""
        schema = WorkflowSchema()
        validator = WorkflowValidator(schema)
        
        # Invalid workflow (invalid step)
        workflow = {
            "name": "Test Workflow",
            "version": "1.0.0",
            "description": "A test workflow",
            "variables": {},
            "steps": [
                {
                    "name": "Step 1",
                    "value": "https://example.com"
                    # Missing action
                }
            ]
        }
        
        # Test
        is_valid = validator.validate_workflow(workflow)
        
        # Verify
        assert is_valid is False
        assert len(validator.errors) > 0
        assert any("action" in error for error in validator.errors)

    def test_validate_workflow_invalid_action(self):
        """Test validating a workflow with invalid action."""
        schema = WorkflowSchema()
        validator = WorkflowValidator(schema)
        
        # Invalid workflow (invalid action)
        workflow = {
            "name": "Test Workflow",
            "version": "1.0.0",
            "description": "A test workflow",
            "variables": {},
            "steps": [
                {
                    "name": "Step 1",
                    "action": "invalid_action",
                    "value": "https://example.com"
                }
            ]
        }
        
        # Test
        is_valid = validator.validate_workflow(workflow)
        
        # Verify
        assert is_valid is False
        assert len(validator.errors) > 0
        assert any("invalid_action" in error for error in validator.errors)

    def test_validate_workflow_file_valid(self, sample_workflow_file):
        """Test validating a valid workflow file."""
        schema = WorkflowSchema()
        validator = WorkflowValidator(schema)
        
        # Test
        is_valid = validator.validate_workflow_file(sample_workflow_file)
        
        # Verify
        assert is_valid is True
        assert validator.errors == []

    def test_validate_workflow_file_invalid(self, temp_dir):
        """Test validating an invalid workflow file."""
        schema = WorkflowSchema()
        validator = WorkflowValidator(schema)
        
        # Create invalid workflow file
        import json
        import os
        invalid_workflow = {
            "version": "1.0.0",
            "description": "A test workflow",
            "variables": {},
            "steps": []
            # Missing name
        }
        
        workflow_file = os.path.join(temp_dir, "invalid_workflow.json")
        with open(workflow_file, "w") as f:
            json.dump(invalid_workflow, f)
        
        # Test
        is_valid = validator.validate_workflow_file(workflow_file)
        
        # Verify
        assert is_valid is False
        assert len(validator.errors) > 0

    def test_validate_workflow_file_nonexistent(self):
        """Test validating a nonexistent workflow file."""
        schema = WorkflowSchema()
        validator = WorkflowValidator(schema)
        
        # Test
        with pytest.raises(AutomationError, match="Workflow file not found"):
            validator.validate_workflow_file("nonexistent_file.json")

    def test_has_errors(self):
        """Test has_errors method."""
        schema = WorkflowSchema()
        validator = WorkflowValidator(schema)
        
        # Initially no errors
        assert validator.has_errors() is False
        
        # Add an error
        validator.errors.append("Test error")
        
        # Now has errors
        assert validator.has_errors() is True

    def test_has_warnings(self):
        """Test has_warnings method."""
        schema = WorkflowSchema()
        validator = WorkflowValidator(schema)
        
        # Initially no warnings
        assert validator.has_warnings() is False
        
        # Add a warning
        validator.warnings.append("Test warning")
        
        # Now has warnings
        assert validator.has_warnings() is True

    def test_print_errors(self, capsys):
        """Test print_errors method."""
        schema = WorkflowSchema()
        validator = WorkflowValidator(schema)
        
        # Add errors
        validator.errors = ["Error 1", "Error 2"]
        
        # Print errors
        validator.print_errors()
        
        # Verify output
        captured = capsys.readouterr()
        assert "Error 1" in captured.out
        assert "Error 2" in captured.out

    def test_print_warnings(self, capsys):
        """Test print_warnings method."""
        schema = WorkflowSchema()
        validator = WorkflowValidator(schema)
        
        # Add warnings
        validator.warnings = ["Warning 1", "Warning 2"]
        
        # Print warnings
        validator.print_warnings()
        
        # Verify output
        captured = capsys.readouterr()
        assert "Warning 1" in captured.out
        assert "Warning 2" in captured.out

    def test_clear_errors(self):
        """Test clear_errors method."""
        schema = WorkflowSchema()
        validator = WorkflowValidator(schema)
        
        # Add errors
        validator.errors = ["Error 1", "Error 2"]
        validator.warnings = ["Warning 1", "Warning 2"]
        
        # Clear errors
        validator.clear_errors()
        
        # Verify
        assert validator.errors == []
        assert validator.warnings == []

    def test_strict_validation(self):
        """Test strict validation mode."""
        schema = WorkflowSchema()
        validator = WorkflowValidator(schema)
        
        # Valid workflow
        workflow = {
            "name": "Test Workflow",
            "version": "1.0.0",
            "description": "A test workflow",
            "variables": {},
            "steps": [
                {
                    "name": "Step 1",
                    "action": "navigate",
                    "value": "https://example.com"
                }
            ]
        }
        
        # Test with strict validation
        is_valid = validator.validate_workflow(workflow, strict=True)
        
        # Verify
        assert is_valid is True
        assert validator.errors == []
