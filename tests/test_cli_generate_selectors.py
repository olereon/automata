"""
Unit tests for the CLI generate-selectors command with fragment functionality.
"""

import json
import os
import tempfile
import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner
from src.automata.cli.main import cli


@pytest.mark.unit
@pytest.mark.cli
@pytest.mark.helper
class TestCliGenerateSelectors:
    """Test cases for CLI generate-selectors command with fragment functionality."""

    def test_generate_selectors_with_html_fragment(self):
        """Test generate-selectors command with --html-fragment parameter."""
        runner = CliRunner()
        
        fragment = """<div class="container">
    <button id="submit-btn">Submit</button>
    <input type="text" name="username" placeholder="Username">
    <a href="/home">Home</a>
</div>"""
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = os.path.join(temp_dir, "selectors.json")
            
            result = runner.invoke(cli, [
                'helper', 'generate-selectors',
                '--html-fragment', fragment,
                '--targeting-mode', 'all',
                '--output', output_file
            ])
            
            assert result.exit_code == 0
            assert "Selectors generated and saved to:" in result.output
            
            # Check output file
            assert os.path.exists(output_file)
            with open(output_file, 'r') as f:
                selectors = json.load(f)
            
            assert len(selectors) > 0
            assert "element_0" in selectors

    def test_generate_selectors_with_fragment_file(self):
        """Test generate-selectors command with --fragment-file parameter."""
        runner = CliRunner()
        
        fragment = """<div class="container">
    <button id="submit-btn">Submit</button>
    <input type="text" name="username" placeholder="Username">
    <a href="/home">Home</a>
</div>"""
        
        with tempfile.TemporaryDirectory() as temp_dir:
            fragment_file = os.path.join(temp_dir, "fragment.html")
            output_file = os.path.join(temp_dir, "selectors.json")
            
            with open(fragment_file, 'w') as f:
                f.write(fragment)
            
            result = runner.invoke(cli, [
                'helper', 'generate-selectors',
                '--fragment-file', fragment_file,
                '--targeting-mode', 'all',
                '--output', output_file
            ])
            
            assert result.exit_code == 0
            assert "Selectors generated and saved to:" in result.output
            
            # Check output file
            assert os.path.exists(output_file)
            with open(output_file, 'r') as f:
                selectors = json.load(f)
            
            assert len(selectors) > 0
            assert "element_0" in selectors

    def test_generate_selectors_with_stdin(self):
        """Test generate-selectors command with --stdin flag."""
        runner = CliRunner()
        
        fragment = """<div class="container">
    <button id="submit-btn">Submit</button>
    <input type="text" name="username" placeholder="Username">
    <a href="/home">Home</a>
</div>"""
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = os.path.join(temp_dir, "selectors.json")
            
            result = runner.invoke(cli, [
                'helper', 'generate-selectors',
                '--stdin',
                '--targeting-mode', 'all',
                '--output', output_file
            ], input=fragment)
            
            assert result.exit_code == 0
            assert "Selectors generated and saved to:" in result.output
            
            # Check output file
            assert os.path.exists(output_file)
            with open(output_file, 'r') as f:
                selectors = json.load(f)
            
            assert len(selectors) > 0
            assert "element_0" in selectors

    def test_generate_selectors_with_selector_targeting_mode(self):
        """Test generate-selectors command with selector targeting mode."""
        runner = CliRunner()
        
        fragment = """<div class="container">
    <button id="submit-btn">Submit</button>
    <input type="text" name="username" placeholder="Username">
    <a href="/home">Home</a>
</div>"""
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = os.path.join(temp_dir, "selectors.json")
            
            result = runner.invoke(cli, [
                'helper', 'generate-selectors',
                '--html-fragment', fragment,
                '--targeting-mode', 'selector',
                '--custom-selector', 'button',
                '--selector-type', 'css',
                '--output', output_file
            ])
            
            assert result.exit_code == 0
            assert "Selectors generated and saved to:" in result.output
            
            # Check output file
            assert os.path.exists(output_file)
            with open(output_file, 'r') as f:
                selectors = json.load(f)
            
            assert len(selectors) == 1
            assert "element_0" in selectors
            assert selectors["element_0"]["element_tag"] == "button"

    def test_generate_selectors_with_auto_targeting_mode(self):
        """Test generate-selectors command with auto targeting mode."""
        runner = CliRunner()
        
        fragment = """<div class="container">
    <button id="submit-btn">Submit</button>
    <input type="text" name="username" placeholder="Username">
    <a href="/home">Home</a>
    <span>Just text</span>
</div>"""
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = os.path.join(temp_dir, "selectors.json")
            
            result = runner.invoke(cli, [
                'helper', 'generate-selectors',
                '--html-fragment', fragment,
                '--targeting-mode', 'auto',
                '--output', output_file
            ])
            
            assert result.exit_code == 0
            assert "Selectors generated and saved to:" in result.output
            
            # Check output file
            assert os.path.exists(output_file)
            with open(output_file, 'r') as f:
                selectors = json.load(f)
            
            # Should find important elements (button, input, a) but not plain span
            assert len(selectors) >= 3
            
            # Check that important elements are included
            element_tags = [result["element_tag"] for result in selectors.values()]
            assert "button" in element_tags
            assert "input" in element_tags
            assert "a" in element_tags

    def test_generate_selectors_with_backward_compatibility(self):
        """Test generate-selectors command with backward compatibility."""
        runner = CliRunner()
        
        complete_html = """<!DOCTYPE html>
<html>
<head>
    <title>Test Page</title>
</head>
<body>
    <div class="container">
        <button id="submit-btn">Submit</button>
        <input type="text" name="username" placeholder="Username">
    </div>
</body>
</html>"""
        
        with tempfile.TemporaryDirectory() as temp_dir:
            html_file = os.path.join(temp_dir, "page.html")
            output_file = os.path.join(temp_dir, "selectors.json")
            
            with open(html_file, 'w') as f:
                f.write(complete_html)
            
            # Test with file parameter (legacy mode)
            result = runner.invoke(cli, [
                'helper', 'generate-selectors',
                '--file', html_file,
                '--output', output_file
            ])
            
            assert result.exit_code == 0
            assert "Selectors generated and saved to:" in result.output
            
            # Check output file
            assert os.path.exists(output_file)
            with open(output_file, 'r') as f:
                selectors = json.load(f)
            
            assert len(selectors) > 0
            assert "element_0" in selectors

    def test_generate_selectors_with_custom_selector_legacy_mode(self):
        """Test generate-selectors command with custom selector in legacy mode."""
        runner = CliRunner()
        
        complete_html = """<!DOCTYPE html>
<html>
<head>
    <title>Test Page</title>
</head>
<body>
    <div class="container">
        <button id="submit-btn">Submit</button>
        <input type="text" name="username" placeholder="Username">
    </div>
</body>
</html>"""
        
        with tempfile.TemporaryDirectory() as temp_dir:
            html_file = os.path.join(temp_dir, "page.html")
            output_file = os.path.join(temp_dir, "selectors.json")
            
            with open(html_file, 'w') as f:
                f.write(complete_html)
            
            # Test with file and custom selector (legacy mode)
            result = runner.invoke(cli, [
                'helper', 'generate-selectors',
                '--file', html_file,
                '--custom-selector', '#submit-btn',
                '--selector-type', 'css',
                '--output', output_file
            ])
            
            assert result.exit_code == 0
            assert "Selectors generated and saved to:" in result.output
            
            # Check output file
            assert os.path.exists(output_file)
            with open(output_file, 'r') as f:
                selectors = json.load(f)
            
            assert len(selectors) == 1
            assert "element_0" in selectors
            assert selectors["element_0"]["element_tag"] == "button"

    def test_generate_selectors_with_no_input_source(self):
        """Test generate-selectors command with no input source."""
        runner = CliRunner()
        
        result = runner.invoke(cli, [
            'helper', 'generate-selectors'
        ])
        
        assert result.exit_code == 1
        assert "Error: No input source specified" in result.output

    def test_generate_selectors_with_nonexistent_fragment_file(self):
        """Test generate-selectors command with nonexistent fragment file."""
        runner = CliRunner()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = os.path.join(temp_dir, "selectors.json")
            
            result = runner.invoke(cli, [
                'helper', 'generate-selectors',
                '--fragment-file', 'nonexistent.html',
                '--output', output_file
            ])
            
            assert result.exit_code == 1
            assert "Error generating selectors" in result.output

    def test_generate_selectors_with_empty_fragment_file(self):
        """Test generate-selectors command with empty fragment file."""
        runner = CliRunner()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            fragment_file = os.path.join(temp_dir, "fragment.html")
            output_file = os.path.join(temp_dir, "selectors.json")
            
            with open(fragment_file, 'w') as f:
                f.write("")
            
            result = runner.invoke(cli, [
                'helper', 'generate-selectors',
                '--fragment-file', fragment_file,
                '--output', output_file
            ])
            
            assert result.exit_code == 1
            assert "Error generating selectors" in result.output

    def test_generate_selectors_with_empty_html_fragment(self):
        """Test generate-selectors command with empty HTML fragment."""
        runner = CliRunner()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = os.path.join(temp_dir, "selectors.json")
            
            result = runner.invoke(cli, [
                'helper', 'generate-selectors',
                '--html-fragment', '',
                '--output', output_file
            ])
            
            assert result.exit_code == 1
            assert "Error generating selectors" in result.output

    def test_generate_selectors_with_invalid_targeting_mode(self):
        """Test generate-selectors command with invalid targeting mode."""
        runner = CliRunner()
        
        fragment = "<div>Content</div>"
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = os.path.join(temp_dir, "selectors.json")
            
            result = runner.invoke(cli, [
                'helper', 'generate-selectors',
                '--html-fragment', fragment,
                '--targeting-mode', 'invalid',
                '--output', output_file
            ])
            
            assert result.exit_code == 1
            assert "Error generating selectors" in result.output

    def test_generate_selectors_with_selector_mode_but_no_custom_selector(self):
        """Test generate-selectors command with selector mode but no custom selector."""
        runner = CliRunner()
        
        fragment = "<div>Content</div>"
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = os.path.join(temp_dir, "selectors.json")
            
            result = runner.invoke(cli, [
                'helper', 'generate-selectors',
                '--html-fragment', fragment,
                '--targeting-mode', 'selector',
                '--output', output_file
            ])
            
            assert result.exit_code == 1
            assert "Error generating selectors" in result.output

    def test_generate_selectors_with_invalid_selector_type(self):
        """Test generate-selectors command with invalid selector type."""
        runner = CliRunner()
        
        fragment = "<div>Content</div>"
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = os.path.join(temp_dir, "selectors.json")
            
            result = runner.invoke(cli, [
                'helper', 'generate-selectors',
                '--html-fragment', fragment,
                '--targeting-mode', 'selector',
                '--custom-selector', 'div',
                '--selector-type', 'invalid',
                '--output', output_file
            ])
            
            assert result.exit_code == 1
            assert "Error generating selectors" in result.output

    def test_generate_selectors_with_no_stdin_input(self):
        """Test generate-selectors command with --stdin flag but no input."""
        runner = CliRunner()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = os.path.join(temp_dir, "selectors.json")
            
            result = runner.invoke(cli, [
                'helper', 'generate-selectors',
                '--stdin',
                '--output', output_file
            ])
            
            assert result.exit_code == 1
            assert "Error generating selectors" in result.output

    def test_generate_selectors_with_default_output_filename(self):
        """Test generate-selectors command with default output filename."""
        runner = CliRunner()
        
        fragment = "<div>Content</div>"
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Change to temp directory
            with runner.isolated_filesystem(temp_dir):
                result = runner.invoke(cli, [
                    'helper', 'generate-selectors',
                    '--html-fragment', fragment,
                    '--targeting-mode', 'all'
                ])
                
                assert result.exit_code == 0
                assert "Selectors generated and saved to:" in result.output
                
                # Check that default output file was created
                assert os.path.exists("selectors.json")
                with open("selectors.json", 'r') as f:
                    selectors = json.load(f)
                
                assert len(selectors) > 0
                assert "element_0" in selectors

    def test_generate_selectors_with_fragment_file_default_output_filename(self):
        """Test generate-selectors command with fragment file and default output filename."""
        runner = CliRunner()
        
        fragment = "<div>Content</div>"
        
        with tempfile.TemporaryDirectory() as temp_dir:
            fragment_file = os.path.join(temp_dir, "fragment.html")
            
            with open(fragment_file, 'w') as f:
                f.write(fragment)
            
            # Change to temp directory
            with runner.isolated_filesystem(temp_dir):
                result = runner.invoke(cli, [
                    'helper', 'generate-selectors',
                    '--fragment-file', fragment_file,
                    '--targeting-mode', 'all'
                ])
                
                assert result.exit_code == 0
                assert "Selectors generated and saved to:" in result.output
                
                # Check that default output file was created
                assert os.path.exists("fragment_selectors.json")
                with open("fragment_selectors.json", 'r') as f:
                    selectors = json.load(f)
                
                assert len(selectors) > 0
                assert "element_0" in selectors

    def test_generate_selectors_with_no_selectors_generated(self):
        """Test generate-selectors command when no selectors are generated."""
        runner = CliRunner()
        
        fragment = "<!-- Just a comment, no elements -->"
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = os.path.join(temp_dir, "selectors.json")
            
            result = runner.invoke(cli, [
                'helper', 'generate-selectors',
                '--html-fragment', fragment,
                '--targeting-mode', 'all',
                '--output', output_file
            ])
            
            assert result.exit_code == 0
            assert "No selectors generated" in result.output

    def test_generate_selectors_with_complex_html_fragment(self):
        """Test generate-selectors command with complex HTML fragment."""
        runner = CliRunner()
        
        fragment = """<div class="container" id="main">
    <header class="header">
        <nav class="navigation">
            <ul class="nav-list">
                <li class="nav-item"><a href="#home" class="nav-link">Home</a></li>
                <li class="nav-item"><a href="#about" class="nav-link">About</a></li>
                <li class="nav-item"><a href="#contact" class="nav-link">Contact</a></li>
            </ul>
        </nav>
    </header>
    <main class="content">
        <section class="hero">
            <h1 class="title">Welcome to Our Site</h1>
            <p class="subtitle">This is a hero section</p>
            <button class="cta-button" id="get-started">Get Started</button>
        </section>
        <section class="features">
            <div class="feature">
                <h2 class="feature-title">Feature 1</h2>
                <p class="feature-description">Description of feature 1</p>
            </div>
            <div class="feature">
                <h2 class="feature-title">Feature 2</h2>
                <p class="feature-description">Description of feature 2</p>
            </div>
        </section>
    </main>
    <footer class="footer">
        <p class="copyright">&copy; 2023 Our Site</p>
    </footer>
</div>"""
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = os.path.join(temp_dir, "selectors.json")
            
            result = runner.invoke(cli, [
                'helper', 'generate-selectors',
                '--html-fragment', fragment,
                '--targeting-mode', 'all',
                '--output', output_file
            ])
            
            assert result.exit_code == 0
            assert "Selectors generated and saved to:" in result.output
            
            # Check output file
            assert os.path.exists(output_file)
            with open(output_file, 'r') as f:
                selectors = json.load(f)
            
            # Should generate selectors for many elements
            assert len(selectors) > 10
            
            # Check that important elements are included
            element_tags = [result["element_tag"] for result in selectors.values()]
            assert "div" in element_tags
            assert "a" in element_tags
            assert "button" in element_tags
            assert "h1" in element_tags
            assert "h2" in element_tags
            assert "p" in element_tags
