"""
Logging and debugging capabilities for web automation.
"""

import logging
import os
import sys
from datetime import datetime
from typing import Optional, Dict, Any, List, Union
from pathlib import Path
import json
from rich.console import Console
from rich.logging import RichHandler
from rich.traceback import install
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.tree import Tree
import asyncio

# Install rich traceback handler
install(show_locals=True)


class AutomationLogger:
    """Enhanced logger for web automation with debugging capabilities."""

    def __init__(
        self,
        name: str = "automata",
        level: int = logging.INFO,
        log_dir: Optional[str] = None,
        enable_console: bool = True,
        enable_file: bool = True,
        enable_screenshots: bool = True,
        enable_html: bool = True
    ):
        """
        Initialize the automation logger.

        Args:
            name: Logger name
            level: Logging level
            log_dir: Directory to store log files
            enable_console: Whether to enable console logging
            enable_file: Whether to enable file logging
            enable_screenshots: Whether to enable screenshot logging
            enable_html: Whether to enable HTML report generation
        """
        self.name = name
        self.level = level
        self.enable_console = enable_console
        self.enable_file = enable_file
        self.enable_screenshots = enable_screenshots
        self.enable_html = enable_html
        
        # Create logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Set up console handler with rich
        if enable_console:
            console = Console(stderr=True)
            console_handler = RichHandler(
                console=console,
                rich_tracebacks=True,
                tracebacks_show_locals=True
            )
            console_handler.setLevel(level)
            console_formatter = logging.Formatter(
                "%(message)s",
                datefmt="[%X]"
            )
            console_handler.setFormatter(console_formatter)
            self.logger.addHandler(console_handler)
        
        # Set up log directory
        if log_dir:
            self.log_dir = Path(log_dir)
        else:
            self.log_dir = Path.cwd() / "logs"
        
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Set up file handler
        if enable_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_file = self.log_dir / f"{name}_{timestamp}.log"
            
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(level)
            file_formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)
        
        # Set up screenshot directory
        if enable_screenshots:
            self.screenshot_dir = self.log_dir / "screenshots"
            self.screenshot_dir.mkdir(parents=True, exist_ok=True)
        
        # Set up HTML report directory
        if enable_html:
            self.html_dir = self.log_dir / "html"
            self.html_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize console for rich output
        self.console = Console()
        
        # Initialize step tracking
        self.steps = []
        self.current_step = None
        
        # Initialize progress tracking
        self.progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        )
        
        # Debug data storage
        self.debug_data = {}

    def debug(self, message: str, **kwargs) -> None:
        """Log a debug message."""
        self.logger.debug(message, **kwargs)

    def info(self, message: str, **kwargs) -> None:
        """Log an info message."""
        self.logger.info(message, **kwargs)

    def warning(self, message: str, **kwargs) -> None:
        """Log a warning message."""
        self.logger.warning(message, **kwargs)

    def error(self, message: str, **kwargs) -> None:
        """Log an error message."""
        self.logger.error(message, **kwargs)

    def critical(self, message: str, **kwargs) -> None:
        """Log a critical message."""
        self.logger.critical(message, **kwargs)

    def exception(self, message: str, **kwargs) -> None:
        """Log an exception with traceback."""
        self.logger.exception(message, **kwargs)

    def start_step(self, name: str, description: str = "") -> Dict[str, Any]:
        """
        Start a new step in the automation process.

        Args:
            name: Step name
            description: Step description

        Returns:
            Step dictionary
        """
        step = {
            "name": name,
            "description": description,
            "start_time": datetime.now(),
            "status": "running",
            "screenshots": [],
            "logs": [],
            "debug_data": {}
        }
        
        self.steps.append(step)
        self.current_step = step
        
        self.info(f"Starting step: {name}")
        if description:
            self.info(f"Description: {description}")
        
        return step

    def end_step(self, status: str = "completed", message: str = "") -> None:
        """
        End the current step.

        Args:
            status: Step status ('completed', 'failed', 'skipped')
            message: Optional message about the step
        """
        if not self.current_step:
            return
        
        self.current_step["end_time"] = datetime.now()
        self.current_step["status"] = status
        self.current_step["duration"] = (
            self.current_step["end_time"] - self.current_step["start_time"]
        ).total_seconds()
        
        if message:
            self.current_step["message"] = message
        
        self.info(f"Step {self.current_step['name']} {status}")
        if message:
            self.info(f"Details: {message}")
        
        self.current_step = None

    def log_screenshot(self, page, name: Optional[str] = None) -> str:
        """
        Take a screenshot and log it.

        Args:
            page: Playwright Page object
            name: Screenshot name (auto-generated if not provided)

        Returns:
            Path to the screenshot file
        """
        if not self.enable_screenshots:
            return ""
        
        if not name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            name = f"screenshot_{timestamp}"
        
        # Ensure .png extension
        if not name.endswith(".png"):
            name += ".png"
        
        screenshot_path = self.screenshot_dir / name
        
        try:
            # Take screenshot
            page.screenshot(path=str(screenshot_path))
            
            # Log screenshot
            self.info(f"Screenshot saved: {screenshot_path}")
            
            # Add to current step if available
            if self.current_step:
                self.current_step["screenshots"].append(str(screenshot_path))
            
            return str(screenshot_path)
        except Exception as e:
            self.error(f"Failed to take screenshot: {e}")
            return ""

    def log_debug_data(self, key: str, value: Any) -> None:
        """
        Store debug data.

        Args:
            key: Data key
            value: Data value
        """
        self.debug_data[key] = value
        
        # Add to current step if available
        if self.current_step:
            self.current_step["debug_data"][key] = value

    def log_page_info(self, page) -> None:
        """
        Log information about the current page.

        Args:
            page: Playwright Page object
        """
        try:
            url = page.url
            title = page.title()
            
            self.info(f"Current page: {title}")
            self.info(f"URL: {url}")
            
            # Store as debug data
            self.log_debug_data("page_url", url)
            self.log_debug_data("page_title", title)
        except Exception as e:
            self.error(f"Failed to get page info: {e}")

    def log_element_info(self, element, name: str = "element") -> None:
        """
        Log information about an element.

        Args:
            element: Playwright ElementHandle
            name: Element name for logging
        """
        try:
            # Get element properties
            tag_name = element.evaluate("el => el.tagName.toLowerCase()")
            text_content = element.text_content() or ""
            is_visible = element.is_visible()
            
            # Get attributes
            attributes = element.evaluate("""el => {
                const attrs = {};
                for (const attr of el.attributes) {
                    attrs[attr.name] = attr.value;
                }
                return attrs;
            }""")
            
            self.info(f"Element '{name}':")
            self.info(f"  Tag: {tag_name}")
            self.info(f"  Visible: {is_visible}")
            self.info(f"  Text: {text_content[:100]}{'...' if len(text_content) > 100 else ''}")
            
            if attributes:
                self.info(f"  Attributes: {json.dumps(attributes, indent=2)}")
            
            # Store as debug data
            element_info = {
                "tag_name": tag_name,
                "text_content": text_content,
                "is_visible": is_visible,
                "attributes": attributes
            }
            self.log_debug_data(f"element_{name}", element_info)
        except Exception as e:
            self.error(f"Failed to get element info: {e}")

    def start_progress(self, description: str) -> None:
        """
        Start a progress indicator.

        Args:
            description: Progress description
        """
        self.progress.start()
        self.progress.add_task(description, total=None)

    def stop_progress(self) -> None:
        """Stop the progress indicator."""
        self.progress.stop()

    def update_progress(self, description: str) -> None:
        """
        Update the progress description.

        Args:
            description: New progress description
        """
        if self.progress.tasks:
            self.progress.update(self.progress.tasks[0].id, description=description)

    def print_summary(self) -> None:
        """Print a summary of the automation session."""
        if not self.steps:
            return
        
        # Create summary table
        table = Table(title="Automation Session Summary")
        table.add_column("Step", style="cyan", no_wrap=True)
        table.add_column("Status", style="magenta")
        table.add_column("Duration", style="green")
        table.add_column("Description", style="yellow")
        
        for step in self.steps:
            status_style = "green" if step["status"] == "completed" else "red"
            duration = f"{step.get('duration', 0):.2f}s"
            
            table.add_row(
                step["name"],
                f"[{status_style}]{step['status']}[/{status_style}]",
                duration,
                step.get("description", "")
            )
        
        self.console.print(table)
        
        # Print step details if there are failures
        failed_steps = [step for step in self.steps if step["status"] == "failed"]
        if failed_steps:
            self.console.print("\n[bold red]Failed Steps:[/bold red]")
            
            for step in failed_steps:
                self.console.print(f"[bold]• {step['name']}[/bold]")
                if step.get("message"):
                    self.console.print(f"  {step['message']}")
                
                if step.get("screenshots"):
                    self.console.print("  Screenshots:")
                    for screenshot in step["screenshots"]:
                        self.console.print(f"    - {screenshot}")

    def generate_html_report(self) -> str:
        """
        Generate an HTML report of the automation session.

        Returns:
            Path to the HTML report file
        """
        if not self.enable_html or not self.steps:
            return ""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.html_dir / f"report_{timestamp}.html"
        
        # Create HTML content
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Automation Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    margin: 0;
                    padding: 20px;
                    color: #333;
                }}
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                }}
                h1, h2, h3 {{
                    color: #2c3e50;
                }}
                .step {{
                    border: 1px solid #ddd;
                    border-radius: 5px;
                    padding: 15px;
                    margin-bottom: 20px;
                }}
                .step-header {{
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 10px;
                }}
                .step-name {{
                    font-weight: bold;
                    font-size: 1.2em;
                }}
                .step-status {{
                    padding: 5px 10px;
                    border-radius: 3px;
                    color: white;
                    font-weight: bold;
                }}
                .status-completed {{
                    background-color: #27ae60;
                }}
                .status-failed {{
                    background-color: #e74c3c;
                }}
                .status-skipped {{
                    background-color: #f39c12;
                }}
                .step-details {{
                    margin-top: 10px;
                }}
                .screenshot {{
                    max-width: 100%;
                    border: 1px solid #ddd;
                    border-radius: 3px;
                    margin: 10px 0;
                }}
                .debug-data {{
                    background-color: #f8f9fa;
                    border: 1px solid #ddd;
                    border-radius: 3px;
                    padding: 10px;
                    margin: 10px 0;
                    font-family: monospace;
                    white-space: pre-wrap;
                }}
                .logs {{
                    background-color: #f8f9fa;
                    border: 1px solid #ddd;
                    border-radius: 3px;
                    padding: 10px;
                    margin: 10px 0;
                    font-family: monospace;
                    white-space: pre-wrap;
                    max-height: 200px;
                    overflow-y: auto;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Automation Report</h1>
                <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        """
        
        # Add steps
        for step in self.steps:
            status_class = f"status-{step['status']}"
            
            html_content += f"""
                <div class="step">
                    <div class="step-header">
                        <div class="step-name">{step['name']}</div>
                        <div class="step-status {status_class}">{step['status'].upper()}</div>
                    </div>
                    <div class="step-details">
                        <p><strong>Duration:</strong> {step.get('duration', 0):.2f} seconds</p>
            """
            
            if step.get("description"):
                html_content += f"<p><strong>Description:</strong> {step['description']}</p>"
            
            if step.get("message"):
                html_content += f"<p><strong>Message:</strong> {step['message']}</p>"
            
            # Add screenshots
            if step.get("screenshots"):
                html_content += "<h3>Screenshots</h3>"
                for screenshot in step["screenshots"]:
                    # Convert absolute path to relative if it's within the log directory
                    screenshot_path = screenshot
                    if self.log_dir in Path(screenshot).parents:
                        screenshot_path = f"../{Path(screenshot).relative_to(self.log_dir.parent)}"
                    
                    html_content += f'<img src="{screenshot_path}" alt="Screenshot" class="screenshot">'
            
            # Add debug data
            if step.get("debug_data"):
                html_content += "<h3>Debug Data</h3>"
                html_content += f'<div class="debug-data">{json.dumps(step["debug_data"], indent=2)}</div>'
            
            html_content += "</div></div>"
        
        html_content += """
            </div>
        </body>
        </html>
        """
        
        # Write HTML file
        try:
            with open(report_file, "w", encoding="utf-8") as f:
                f.write(html_content)
            
            self.info(f"HTML report generated: {report_file}")
            return str(report_file)
        except Exception as e:
            self.error(f"Failed to generate HTML report: {e}")
            return ""

    def save_debug_data(self, filename: Optional[str] = None) -> str:
        """
        Save debug data to a JSON file.

        Args:
            filename: Output filename (auto-generated if not provided)

        Returns:
            Path to the debug data file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"debug_data_{timestamp}.json"
        
        # Ensure .json extension
        if not filename.endswith(".json"):
            filename += ".json"
        
        debug_file = self.log_dir / filename
        
        try:
            with open(debug_file, "w", encoding="utf-8") as f:
                json.dump(self.debug_data, f, indent=2, default=str)
            
            self.info(f"Debug data saved: {debug_file}")
            return str(debug_file)
        except Exception as e:
            self.error(f"Failed to save debug data: {e}")
            return ""


# Global logger instance
_logger_instance = None


def get_logger(
    name: str = "automata",
    level: int = logging.INFO,
    log_dir: Optional[str] = None,
    enable_console: bool = True,
    enable_file: bool = True,
    enable_screenshots: bool = True,
    enable_html: bool = True
) -> AutomationLogger:
    """
    Get or create the global logger instance.

    Args:
        name: Logger name
        level: Logging level
        log_dir: Directory to store log files
        enable_console: Whether to enable console logging
        enable_file: Whether to enable file logging
        enable_screenshots: Whether to enable screenshot logging
        enable_html: Whether to enable HTML report generation

    Returns:
        AutomationLogger instance
    """
    global _logger_instance
    
    if _logger_instance is None:
        _logger_instance = AutomationLogger(
            name=name,
            level=level,
            log_dir=log_dir,
            enable_console=enable_console,
            enable_file=enable_file,
            enable_screenshots=enable_screenshots,
            enable_html=enable_html
        )
    
    return _logger_instance


def set_logger(logger: AutomationLogger) -> None:
    """
    Set the global logger instance.

    Args:
        logger: AutomationLogger instance to set as global
    """
    global _logger_instance
    _logger_instance = logger
