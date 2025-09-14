"""
File I/O utilities for reading/writing external data.
"""

import json
import csv
import os
import yaml
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, Any, Optional, List, Union, Tuple
import logging

from ..core.errors import AutomationError
from ..core.logger import get_logger

logger = get_logger(__name__)


class FileIO:
    """File I/O utilities for reading and writing external data."""

    def __init__(self):
        """Initialize the FileIO utility."""
        pass

    def read_json(self, file_path: str) -> Dict[str, Any]:
        """
        Read JSON data from a file.

        Args:
            file_path: Path to the JSON file

        Returns:
            Dictionary with JSON data

        Raises:
            AutomationError: If the file cannot be read or parsed
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            logger.info(f"JSON data loaded from: {file_path}")
            return data
        
        except FileNotFoundError:
            raise AutomationError(f"File not found: {file_path}")
        except json.JSONDecodeError as e:
            raise AutomationError(f"Invalid JSON in file {file_path}: {e}")
        except Exception as e:
            raise AutomationError(f"Error reading JSON file {file_path}: {e}")

    def write_json(self, data: Dict[str, Any], file_path: str, indent: int = 2) -> None:
        """
        Write JSON data to a file.

        Args:
            data: Dictionary with JSON data
            file_path: Path to the JSON file
            indent: JSON indentation level

        Raises:
            AutomationError: If the file cannot be written
        """
        try:
            # Create directory if it doesn't exist
            directory = Path(file_path).parent
            directory.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=indent, ensure_ascii=False)
            
            logger.info(f"JSON data saved to: {file_path}")
        
        except Exception as e:
            raise AutomationError(f"Error writing JSON file {file_path}: {e}")

    def read_csv(self, file_path: str, delimiter: str = ",", has_header: bool = True) -> List[Dict[str, str]]:
        """
        Read CSV data from a file.

        Args:
            file_path: Path to the CSV file
            delimiter: CSV delimiter
            has_header: Whether the CSV file has a header row

        Returns:
            List of dictionaries with CSV data

        Raises:
            AutomationError: If the file cannot be read or parsed
        """
        try:
            data = []
            
            with open(file_path, "r", encoding="utf-8") as f:
                reader = csv.reader(f, delimiter=delimiter)
                
                # Read header if present
                if has_header:
                    header = next(reader)
                else:
                    # Generate header if not present
                    first_row = next(reader)
                    header = [f"column_{i}" for i in range(len(first_row))]
                    data.append(dict(zip(header, first_row)))
                
                # Read data rows
                for row in reader:
                    data.append(dict(zip(header, row)))
            
            logger.info(f"CSV data loaded from: {file_path}")
            return data
        
        except FileNotFoundError:
            raise AutomationError(f"File not found: {file_path}")
        except Exception as e:
            raise AutomationError(f"Error reading CSV file {file_path}: {e}")

    def write_csv(self, data: List[Dict[str, str]], file_path: str, delimiter: str = ",", 
                header: Optional[List[str]] = None) -> None:
        """
        Write CSV data to a file.

        Args:
            data: List of dictionaries with CSV data
            file_path: Path to the CSV file
            delimiter: CSV delimiter
            header: List of header column names (optional)

        Raises:
            AutomationError: If the file cannot be written
        """
        try:
            # Create directory if it doesn't exist
            directory = Path(file_path).parent
            directory.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f, delimiter=delimiter)
                
                # Write header
                if header:
                    writer.writerow(header)
                elif data:
                    writer.writerow(data[0].keys())
                
                # Write data rows
                for row in data:
                    writer.writerow(row.values())
            
            logger.info(f"CSV data saved to: {file_path}")
        
        except Exception as e:
            raise AutomationError(f"Error writing CSV file {file_path}: {e}")

    def read_yaml(self, file_path: str) -> Dict[str, Any]:
        """
        Read YAML data from a file.

        Args:
            file_path: Path to the YAML file

        Returns:
            Dictionary with YAML data

        Raises:
            AutomationError: If the file cannot be read or parsed
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            
            logger.info(f"YAML data loaded from: {file_path}")
            return data
        
        except FileNotFoundError:
            raise AutomationError(f"File not found: {file_path}")
        except yaml.YAMLError as e:
            raise AutomationError(f"Invalid YAML in file {file_path}: {e}")
        except Exception as e:
            raise AutomationError(f"Error reading YAML file {file_path}: {e}")

    def write_yaml(self, data: Dict[str, Any], file_path: str) -> None:
        """
        Write YAML data to a file.

        Args:
            data: Dictionary with YAML data
            file_path: Path to the YAML file

        Raises:
            AutomationError: If the file cannot be written
        """
        try:
            # Create directory if it doesn't exist
            directory = Path(file_path).parent
            directory.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, "w", encoding="utf-8") as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
            
            logger.info(f"YAML data saved to: {file_path}")
        
        except Exception as e:
            raise AutomationError(f"Error writing YAML file {file_path}: {e}")

    def read_xml(self, file_path: str) -> ET.Element:
        """
        Read XML data from a file.

        Args:
            file_path: Path to the XML file

        Returns:
            XML Element object

        Raises:
            AutomationError: If the file cannot be read or parsed
        """
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            logger.info(f"XML data loaded from: {file_path}")
            return root
        
        except FileNotFoundError:
            raise AutomationError(f"File not found: {file_path}")
        except ET.ParseError as e:
            raise AutomationError(f"Invalid XML in file {file_path}: {e}")
        except Exception as e:
            raise AutomationError(f"Error reading XML file {file_path}: {e}")

    def write_xml(self, element: ET.Element, file_path: str) -> None:
        """
        Write XML data to a file.

        Args:
            element: XML Element object
            file_path: Path to the XML file

        Raises:
            AutomationError: If the file cannot be written
        """
        try:
            # Create directory if it doesn't exist
            directory = Path(file_path).parent
            directory.mkdir(parents=True, exist_ok=True)
            
            tree = ET.ElementTree(element)
            tree.write(file_path, encoding="utf-8", xml_declaration=True)
            
            logger.info(f"XML data saved to: {file_path}")
        
        except Exception as e:
            raise AutomationError(f"Error writing XML file {file_path}: {e}")

    def read_text(self, file_path: str) -> str:
        """
        Read text data from a file.

        Args:
            file_path: Path to the text file

        Returns:
            Text content

        Raises:
            AutomationError: If the file cannot be read
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
            
            logger.info(f"Text data loaded from: {file_path}")
            return text
        
        except FileNotFoundError:
            raise AutomationError(f"File not found: {file_path}")
        except Exception as e:
            raise AutomationError(f"Error reading text file {file_path}: {e}")

    def write_text(self, text: str, file_path: str) -> None:
        """
        Write text data to a file.

        Args:
            text: Text content
            file_path: Path to the text file

        Raises:
            AutomationError: If the file cannot be written
        """
        try:
            # Create directory if it doesn't exist
            directory = Path(file_path).parent
            directory.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(text)
            
            logger.info(f"Text data saved to: {file_path}")
        
        except Exception as e:
            raise AutomationError(f"Error writing text file {file_path}: {e}")

    def read_lines(self, file_path: str) -> List[str]:
        """
        Read lines from a text file.

        Args:
            file_path: Path to the text file

        Returns:
            List of lines

        Raises:
            AutomationError: If the file cannot be read
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = [line.strip() for line in f.readlines()]
            
            logger.info(f"Lines loaded from: {file_path}")
            return lines
        
        except FileNotFoundError:
            raise AutomationError(f"File not found: {file_path}")
        except Exception as e:
            raise AutomationError(f"Error reading lines from file {file_path}: {e}")

    def write_lines(self, lines: List[str], file_path: str) -> None:
        """
        Write lines to a text file.

        Args:
            lines: List of lines
            file_path: Path to the text file

        Raises:
            AutomationError: If the file cannot be written
        """
        try:
            # Create directory if it doesn't exist
            directory = Path(file_path).parent
            directory.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
            
            logger.info(f"Lines saved to: {file_path}")
        
        except Exception as e:
            raise AutomationError(f"Error writing lines to file {file_path}: {e}")

    def file_exists(self, file_path: str) -> bool:
        """
        Check if a file exists.

        Args:
            file_path: Path to the file

        Returns:
            True if the file exists, False otherwise
        """
        return os.path.exists(file_path)

    def delete_file(self, file_path: str) -> bool:
        """
        Delete a file.

        Args:
            file_path: Path to the file

        Returns:
            True if the file was deleted, False otherwise
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"File deleted: {file_path}")
                return True
            else:
                logger.warning(f"File not found: {file_path}")
                return False
        
        except Exception as e:
            logger.error(f"Error deleting file {file_path}: {e}")
            return False

    def copy_file(self, source_path: str, destination_path: str) -> bool:
        """
        Copy a file.

        Args:
            source_path: Path to the source file
            destination_path: Path to the destination file

        Returns:
            True if the file was copied, False otherwise
        """
        try:
            # Create directory if it doesn't exist
            directory = Path(destination_path).parent
            directory.mkdir(parents=True, exist_ok=True)
            
            with open(source_path, "rb") as src, open(destination_path, "wb") as dst:
                dst.write(src.read())
            
            logger.info(f"File copied from {source_path} to {destination_path}")
            return True
        
        except Exception as e:
            logger.error(f"Error copying file from {source_path} to {destination_path}: {e}")
            return False

    def move_file(self, source_path: str, destination_path: str) -> bool:
        """
        Move a file.

        Args:
            source_path: Path to the source file
            destination_path: Path to the destination file

        Returns:
            True if the file was moved, False otherwise
        """
        try:
            # Create directory if it doesn't exist
            directory = Path(destination_path).parent
            directory.mkdir(parents=True, exist_ok=True)
            
            os.rename(source_path, destination_path)
            
            logger.info(f"File moved from {source_path} to {destination_path}")
            return True
        
        except Exception as e:
            logger.error(f"Error moving file from {source_path} to {destination_path}: {e}")
            return False

    def get_file_size(self, file_path: str) -> int:
        """
        Get the size of a file in bytes.

        Args:
            file_path: Path to the file

        Returns:
            File size in bytes

        Raises:
            AutomationError: If the file cannot be accessed
        """
        try:
            return os.path.getsize(file_path)
        
        except Exception as e:
            raise AutomationError(f"Error getting file size for {file_path}: {e}")

    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """
        Get information about a file.

        Args:
            file_path: Path to the file

        Returns:
            Dictionary with file information

        Raises:
            AutomationError: If the file cannot be accessed
        """
        try:
            stat = os.stat(file_path)
            
            return {
                "path": file_path,
                "size": stat.st_size,
                "modified": stat.st_mtime,
                "created": stat.st_ctime,
                "is_file": os.path.isfile(file_path),
                "is_dir": os.path.isdir(file_path),
                "exists": os.path.exists(file_path)
            }
        
        except Exception as e:
            raise AutomationError(f"Error getting file info for {file_path}: {e}")

    def list_files(self, directory: str, pattern: Optional[str] = None, recursive: bool = False) -> List[str]:
        """
        List files in a directory.

        Args:
            directory: Path to the directory
            pattern: File pattern to match (optional)
            recursive: Whether to list files recursively

        Returns:
            List of file paths

        Raises:
            AutomationError: If the directory cannot be accessed
        """
        try:
            if not os.path.isdir(directory):
                raise AutomationError(f"Not a directory: {directory}")
            
            if recursive:
                if pattern:
                    return [str(p) for p in Path(directory).rglob(pattern)]
                else:
                    return [str(p) for p in Path(directory).rglob("*") if p.is_file()]
            else:
                if pattern:
                    return [str(p) for p in Path(directory).glob(pattern)]
                else:
                    return [str(p) for p in Path(directory).glob("*") if p.is_file()]
        
        except Exception as e:
            raise AutomationError(f"Error listing files in directory {directory}: {e}")

    def create_directory(self, directory: str) -> bool:
        """
        Create a directory.

        Args:
            directory: Path to the directory

        Returns:
            True if the directory was created, False otherwise
        """
        try:
            Path(directory).mkdir(parents=True, exist_ok=True)
            logger.info(f"Directory created: {directory}")
            return True
        
        except Exception as e:
            logger.error(f"Error creating directory {directory}: {e}")
            return False

    def delete_directory(self, directory: str, recursive: bool = False) -> bool:
        """
        Delete a directory.

        Args:
            directory: Path to the directory
            recursive: Whether to delete the directory recursively

        Returns:
            True if the directory was deleted, False otherwise
        """
        try:
            if recursive:
                import shutil
                shutil.rmtree(directory)
            else:
                os.rmdir(directory)
            
            logger.info(f"Directory deleted: {directory}")
            return True
        
        except Exception as e:
            logger.error(f"Error deleting directory {directory}: {e}")
            return False

    def get_file_extension(self, file_path: str) -> str:
        """
        Get the extension of a file.

        Args:
            file_path: Path to the file

        Returns:
            File extension (without the dot)
        """
        return Path(file_path).suffix.lower().lstrip(".")

    def change_file_extension(self, file_path: str, new_extension: str) -> str:
        """
        Change the extension of a file.

        Args:
            file_path: Path to the file
            new_extension: New extension (without the dot)

        Returns:
            New file path with the changed extension
        """
        path = Path(file_path)
        return str(path.with_suffix(f".{new_extension}"))
