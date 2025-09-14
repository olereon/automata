"""
HTML/XPath parser tool for extracting element information.
"""

import asyncio
import json
from typing import Dict, Any, Optional, List, Union, Tuple
from pathlib import Path
from playwright.async_api import Page, ElementHandle
from lxml import html, etree
import re

from ..core.errors import AutomationError
from ..core.logger import get_logger

logger = get_logger(__name__)


class HTMLParser:
    """HTML parser for extracting element information."""

    def __init__(self):
        """Initialize the HTML parser."""
        self.namespaces = {
            "xhtml": "http://www.w3.org/1999/xhtml",
            "svg": "http://www.w3.org/2000/svg"
        }

    async def parse_page(self, page: Page) -> Dict[str, Any]:
        """
        Parse the current page and extract element information.

        Args:
            page: Playwright Page object

        Returns:
            Dictionary with parsed page information
        """
        logger.info("Parsing page HTML")
        
        try:
            # Get page HTML
            html_content = await page.content()
            
            # Parse HTML
            parsed_html = html.fromstring(html_content)
            
            # Extract page information
            page_info = {
                "url": page.url,
                "title": await page.title(),
                "elements": self._extract_elements(parsed_html),
                "forms": self._extract_forms(parsed_html),
                "links": self._extract_links(parsed_html),
                "images": self._extract_images(parsed_html),
                "tables": self._extract_tables(parsed_html)
            }
            
            logger.info(f"Page parsed successfully: {page.url}")
            return page_info
        
        except Exception as e:
            logger.error(f"Error parsing page: {e}")
            raise AutomationError(f"Error parsing page: {e}")

    def _extract_elements(self, parsed_html: html.HtmlElement) -> List[Dict[str, Any]]:
        """
        Extract interactive elements from parsed HTML.

        Args:
            parsed_html: Parsed HTML element

        Returns:
            List of element information
        """
        elements = []
        
        # Define interactive element selectors
        selectors = [
            "//button",
            "//input[@type='button' or @type='submit' or @type='reset']",
            "//a[@href]",
            "//select",
            "//textarea",
            "//input[@type='text' or @type='password' or @type='email' or @type='search' or @type='tel' or @type='url']",
            "//input[@type='checkbox' or @type='radio']",
            "//label",
            "//div[@role='button' or @role='link' or @role='textbox' or @role='combobox' or @role='listbox']"
        ]
        
        for selector in selectors:
            try:
                found_elements = parsed_html.xpath(selector, namespaces=self.namespaces)
                
                for element in found_elements:
                    element_info = self._extract_element_info(element)
                    if element_info:
                        elements.append(element_info)
            
            except Exception as e:
                logger.warning(f"Error extracting elements with selector {selector}: {e}")
        
        return elements

    def _extract_element_info(self, element: html.HtmlElement) -> Optional[Dict[str, Any]]:
        """
        Extract information from a single HTML element.

        Args:
            element: HTML element

        Returns:
            Element information dictionary or None
        """
        try:
            # Get element tag
            tag = element.tag
            
            # Get element attributes
            attributes = dict(element.attrib)
            
            # Get element text
            text = element.text_content().strip() if element.text_content() else ""
            
            # Get element XPath
            xpath = self._generate_xpath(element)
            
            # Get element CSS selector
            css_selector = self._generate_css_selector(element)
            
            # Create element info
            element_info = {
                "tag": tag,
                "attributes": attributes,
                "text": text,
                "xpath": xpath,
                "css_selector": css_selector
            }
            
            # Add additional information based on element type
            if tag == "a":
                element_info["href"] = attributes.get("href", "")
            elif tag == "img":
                element_info["src"] = attributes.get("src", "")
                element_info["alt"] = attributes.get("alt", "")
            elif tag == "input":
                element_info["type"] = attributes.get("type", "")
                element_info["name"] = attributes.get("name", "")
                element_info["value"] = attributes.get("value", "")
                element_info["placeholder"] = attributes.get("placeholder", "")
            elif tag == "button":
                element_info["type"] = attributes.get("type", "")
                element_info["name"] = attributes.get("name", "")
            elif tag == "select":
                element_info["name"] = attributes.get("name", "")
                element_info["options"] = self._extract_select_options(element)
            
            return element_info
        
        except Exception as e:
            logger.warning(f"Error extracting element info: {e}")
            return None

    def _extract_select_options(self, select_element: html.HtmlElement) -> List[Dict[str, Any]]:
        """
        Extract options from a select element.

        Args:
            select_element: Select HTML element

        Returns:
            List of option information
        """
        options = []
        
        try:
            option_elements = select_element.xpath("./option")
            
            for option in option_elements:
                option_info = {
                    "value": option.get("value", ""),
                    "text": option.text_content().strip() if option.text_content() else "",
                    "selected": option.get("selected") is not None
                }
                options.append(option_info)
        
        except Exception as e:
            logger.warning(f"Error extracting select options: {e}")
        
        return options

    def _extract_forms(self, parsed_html: html.HtmlElement) -> List[Dict[str, Any]]:
        """
        Extract form information from parsed HTML.

        Args:
            parsed_html: Parsed HTML element

        Returns:
            List of form information
        """
        forms = []
        
        try:
            form_elements = parsed_html.xpath("//form")
            
            for form in form_elements:
                form_info = {
                    "action": form.get("action", ""),
                    "method": form.get("method", "get"),
                    "id": form.get("id", ""),
                    "name": form.get("name", ""),
                    "fields": self._extract_form_fields(form)
                }
                forms.append(form_info)
        
        except Exception as e:
            logger.warning(f"Error extracting forms: {e}")
        
        return forms

    def _extract_form_fields(self, form_element: html.HtmlElement) -> List[Dict[str, Any]]:
        """
        Extract form fields from a form element.

        Args:
            form_element: Form HTML element

        Returns:
            List of form field information
        """
        fields = []
        
        try:
            # Find all input, select, textarea, and button elements in the form
            field_selectors = [
                ".//input",
                ".//select",
                ".//textarea",
                ".//button"
            ]
            
            for selector in field_selectors:
                field_elements = form_element.xpath(selector)
                
                for field in field_elements:
                    field_info = self._extract_element_info(field)
                    if field_info:
                        fields.append(field_info)
        
        except Exception as e:
            logger.warning(f"Error extracting form fields: {e}")
        
        return fields

    def _extract_links(self, parsed_html: html.HtmlElement) -> List[Dict[str, Any]]:
        """
        Extract link information from parsed HTML.

        Args:
            parsed_html: Parsed HTML element

        Returns:
            List of link information
        """
        links = []
        
        try:
            link_elements = parsed_html.xpath("//a[@href]")
            
            for link in link_elements:
                link_info = {
                    "href": link.get("href", ""),
                    "text": link.text_content().strip() if link.text_content() else "",
                    "title": link.get("title", ""),
                    "target": link.get("target", ""),
                    "xpath": self._generate_xpath(link),
                    "css_selector": self._generate_css_selector(link)
                }
                links.append(link_info)
        
        except Exception as e:
            logger.warning(f"Error extracting links: {e}")
        
        return links

    def _extract_images(self, parsed_html: html.HtmlElement) -> List[Dict[str, Any]]:
        """
        Extract image information from parsed HTML.

        Args:
            parsed_html: Parsed HTML element

        Returns:
            List of image information
        """
        images = []
        
        try:
            img_elements = parsed_html.xpath("//img[@src]")
            
            for img in img_elements:
                img_info = {
                    "src": img.get("src", ""),
                    "alt": img.get("alt", ""),
                    "title": img.get("title", ""),
                    "width": img.get("width", ""),
                    "height": img.get("height", ""),
                    "xpath": self._generate_xpath(img),
                    "css_selector": self._generate_css_selector(img)
                }
                images.append(img_info)
        
        except Exception as e:
            logger.warning(f"Error extracting images: {e}")
        
        return images

    def _extract_tables(self, parsed_html: html.HtmlElement) -> List[Dict[str, Any]]:
        """
        Extract table information from parsed HTML.

        Args:
            parsed_html: Parsed HTML element

        Returns:
            List of table information
        """
        tables = []
        
        try:
            table_elements = parsed_html.xpath("//table")
            
            for table in table_elements:
                table_info = {
                    "id": table.get("id", ""),
                    "class": table.get("class", ""),
                    "rows": self._extract_table_rows(table),
                    "xpath": self._generate_xpath(table),
                    "css_selector": self._generate_css_selector(table)
                }
                tables.append(table_info)
        
        except Exception as e:
            logger.warning(f"Error extracting tables: {e}")
        
        return tables

    def _extract_table_rows(self, table_element: html.HtmlElement) -> List[Dict[str, Any]]:
        """
        Extract table rows from a table element.

        Args:
            table_element: Table HTML element

        Returns:
            List of table row information
        """
        rows = []
        
        try:
            # Find all tr elements in the table
            row_elements = table_element.xpath(".//tr")
            
            for row in row_elements:
                row_info = {
                    "type": "header" if row.xpath("./th") else "data",
                    "cells": self._extract_table_cells(row)
                }
                rows.append(row_info)
        
        except Exception as e:
            logger.warning(f"Error extracting table rows: {e}")
        
        return rows

    def _extract_table_cells(self, row_element: html.HtmlElement) -> List[Dict[str, Any]]:
        """
        Extract table cells from a table row element.

        Args:
            row_element: Table row HTML element

        Returns:
            List of table cell information
        """
        cells = []
        
        try:
            # Find all th and td elements in the row
            cell_elements = row_element.xpath("./th | ./td")
            
            for cell in cell_elements:
                cell_info = {
                    "type": "header" if cell.tag == "th" else "data",
                    "text": cell.text_content().strip() if cell.text_content() else "",
                    "colspan": cell.get("colspan", "1"),
                    "rowspan": cell.get("rowspan", "1")
                }
                cells.append(cell_info)
        
        except Exception as e:
            logger.warning(f"Error extracting table cells: {e}")
        
        return cells

    def _generate_xpath(self, element: html.HtmlElement) -> str:
        """
        Generate a unique XPath for an element.

        Args:
            element: HTML element

        Returns:
            XPath string
        """
        try:
            # Use the built-in getpath method to generate XPath
            path = element.getroottree().getpath(element)
            
            # Convert to a more readable format
            if path.startswith("/html"):
                return path
            else:
                # If it's a relative path, make it absolute
                return f"/html{path}"
        
        except Exception as e:
            logger.warning(f"Error generating XPath: {e}")
            return ""

    def _generate_css_selector(self, element: html.HtmlElement) -> str:
        """
        Generate a CSS selector for an element.

        Args:
            element: HTML element

        Returns:
            CSS selector string
        """
        try:
            # Start with the tag name
            selector = element.tag
            
            # Add ID if present
            element_id = element.get("id")
            if element_id:
                selector += f"#{element_id}"
            
            # Add classes if present
            element_class = element.get("class")
            if element_class:
                classes = element_class.split()
                for cls in classes:
                    selector += f".{cls}"
            
            # Add attributes to make it more specific
            attributes = ["name", "type", "value", "placeholder", "title", "alt", "href", "src"]
            for attr in attributes:
                attr_value = element.get(attr)
                if attr_value:
                    selector += f'[{attr}="{attr_value}"]'
                    break  # Just add one attribute to keep it simple
            
            return selector
        
        except Exception as e:
            logger.warning(f"Error generating CSS selector: {e}")
            return element.tag

    async def save_parsed_page(self, page_info: Dict[str, Any], output_path: str) -> None:
        """
        Save parsed page information to a file.

        Args:
            page_info: Parsed page information
            output_path: Path to save the file
        """
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(page_info, f, indent=2, default=str)
            
            logger.info(f"Parsed page saved to: {output_path}")
        
        except Exception as e:
            logger.error(f"Error saving parsed page: {e}")
            raise AutomationError(f"Error saving parsed page: {e}")

    async def load_parsed_page(self, input_path: str) -> Dict[str, Any]:
        """
        Load parsed page information from a file.

        Args:
            input_path: Path to the file

        Returns:
            Parsed page information
        """
        try:
            with open(input_path, "r", encoding="utf-8") as f:
                page_info = json.load(f)
            
            logger.info(f"Parsed page loaded from: {input_path}")
            return page_info
        
        except Exception as e:
            logger.error(f"Error loading parsed page: {e}")
            raise AutomationError(f"Error loading parsed page: {e}")

    def find_elements_by_text(self, page_info: Dict[str, Any], text: str, exact_match: bool = False) -> List[Dict[str, Any]]:
        """
        Find elements by their text content.

        Args:
            page_info: Parsed page information
            text: Text to search for
            exact_match: Whether to match text exactly

        Returns:
            List of matching elements
        """
        matching_elements = []
        
        try:
            # Search in all elements
            for element in page_info.get("elements", []):
                element_text = element.get("text", "")
                
                if exact_match:
                    if element_text == text:
                        matching_elements.append(element)
                else:
                    if text.lower() in element_text.lower():
                        matching_elements.append(element)
            
            # Search in links
            for link in page_info.get("links", []):
                link_text = link.get("text", "")
                
                if exact_match:
                    if link_text == text:
                        matching_elements.append(link)
                else:
                    if text.lower() in link_text.lower():
                        matching_elements.append(link)
            
            logger.info(f"Found {len(matching_elements)} elements matching text: {text}")
            return matching_elements
        
        except Exception as e:
            logger.error(f"Error finding elements by text: {e}")
            return []

    def find_elements_by_attribute(self, page_info: Dict[str, Any], attribute: str, value: str) -> List[Dict[str, Any]]:
        """
        Find elements by attribute value.

        Args:
            page_info: Parsed page information
            attribute: Attribute name
            value: Attribute value

        Returns:
            List of matching elements
        """
        matching_elements = []
        
        try:
            # Search in all elements
            for element in page_info.get("elements", []):
                attributes = element.get("attributes", {})
                
                if attribute in attributes and attributes[attribute] == value:
                    matching_elements.append(element)
            
            # Search in links
            for link in page_info.get("links", []):
                if attribute == "href" and link.get("href") == value:
                    matching_elements.append(link)
                elif attribute in link and link[attribute] == value:
                    matching_elements.append(link)
            
            # Search in images
            for img in page_info.get("images", []):
                if attribute == "src" and img.get("src") == value:
                    matching_elements.append(img)
                elif attribute == "alt" and img.get("alt") == value:
                    matching_elements.append(img)
                elif attribute in img and img[attribute] == value:
                    matching_elements.append(img)
            
            logger.info(f"Found {len(matching_elements)} elements with {attribute}={value}")
            return matching_elements
        
        except Exception as e:
            logger.error(f"Error finding elements by attribute: {e}")
            return []

    def find_elements_by_tag(self, page_info: Dict[str, Any], tag: str) -> List[Dict[str, Any]]:
        """
        Find elements by tag name.

        Args:
            page_info: Parsed page information
            tag: Tag name

        Returns:
            List of matching elements
        """
        matching_elements = []
        
        try:
            # Search in all elements
            for element in page_info.get("elements", []):
                if element.get("tag") == tag:
                    matching_elements.append(element)
            
            # Search in links
            if tag == "a":
                matching_elements.extend(page_info.get("links", []))
            
            # Search in images
            if tag == "img":
                matching_elements.extend(page_info.get("images", []))
            
            logger.info(f"Found {len(matching_elements)} elements with tag: {tag}")
            return matching_elements
        
        except Exception as e:
            logger.error(f"Error finding elements by tag: {e}")
            return []

    def parse_file(self, file_path: str) -> Dict[str, Any]:
        """
        Parse HTML from a file and extract element information.

        Args:
            file_path: Path to the HTML file

        Returns:
            Dictionary with parsed page information
        """
        logger.info(f"Parsing HTML file: {file_path}")
        
        try:
            # Read HTML file
            with open(file_path, "r", encoding="utf-8") as f:
                html_content = f.read()
            
            # Parse HTML
            parsed_html = html.fromstring(html_content)
            
            # Extract page information
            page_info = {
                "url": f"file://{file_path}",
                "title": self._extract_title(parsed_html),
                "elements": self._extract_elements(parsed_html),
                "forms": self._extract_forms(parsed_html),
                "links": self._extract_links(parsed_html),
                "images": self._extract_images(parsed_html),
                "tables": self._extract_tables(parsed_html)
            }
            
            logger.info(f"HTML file parsed successfully: {file_path}")
            return page_info
        
        except Exception as e:
            logger.error(f"Error parsing HTML file: {e}")
            raise AutomationError(f"Error parsing HTML file: {e}")

    def _extract_title(self, parsed_html: html.HtmlElement) -> str:
        """
        Extract title from parsed HTML.

        Args:
            parsed_html: Parsed HTML element

        Returns:
            Title string
        """
        try:
            title_elements = parsed_html.xpath("//title")
            if title_elements:
                return title_elements[0].text_content().strip() if title_elements[0].text_content() else ""
            return ""
        except Exception as e:
            logger.warning(f"Error extracting title: {e}")
            return ""

    async def click_element(self, page: Page, selector: str) -> None:
        """
        Click on an element.

        Args:
            page: Playwright Page object
            selector: CSS selector or XPath for the element
        """
        try:
            # Check if selector is XPath
            if selector.startswith("xpath="):
                xpath = selector[6:]  # Remove "xpath=" prefix
                element = await page.wait_for_selector(xpath, state="visible")
                await element.click()
            else:
                # Treat as CSS selector
                element = await page.wait_for_selector(selector, state="visible")
                await element.click()
            
            logger.info(f"Clicked element with selector: {selector}")
        
        except Exception as e:
            logger.error(f"Error clicking element with selector {selector}: {e}")
            raise AutomationError(f"Error clicking element with selector {selector}: {e}")

    async def type_text(self, page: Page, selector: str, text: str) -> None:
        """
        Type text into an input field.

        Args:
            page: Playwright Page object
            selector: CSS selector or XPath for the element
            text: Text to type
        """
        try:
            # Check if selector is XPath
            if selector.startswith("xpath="):
                xpath = selector[6:]  # Remove "xpath=" prefix
                element = await page.wait_for_selector(xpath, state="visible")
                await element.fill(text)
            else:
                # Treat as CSS selector
                element = await page.wait_for_selector(selector, state="visible")
                await element.fill(text)
            
            logger.info(f"Typed text into element with selector: {selector}")
        
        except Exception as e:
            logger.error(f"Error typing text into element with selector {selector}: {e}")
            raise AutomationError(f"Error typing text into element with selector {selector}: {e}")

    async def hover_element(self, page: Page, selector: str) -> None:
        """
        Hover over an element.

        Args:
            page: Playwright Page object
            selector: CSS selector or XPath for the element
        """
        try:
            # Check if selector is XPath
            if selector.startswith("xpath="):
                xpath = selector[6:]  # Remove "xpath=" prefix
                element = await page.wait_for_selector(xpath, state="visible")
                await element.hover()
            else:
                # Treat as CSS selector
                element = await page.wait_for_selector(selector, state="visible")
                await element.hover()
            
            logger.info(f"Hovered over element with selector: {selector}")
        
        except Exception as e:
            logger.error(f"Error hovering over element with selector {selector}: {e}")
            raise AutomationError(f"Error hovering over element with selector {selector}: {e}")

    async def get_text(self, page: Page, selector: str) -> str:
        """
        Get text content of an element.

        Args:
            page: Playwright Page object
            selector: CSS selector or XPath for the element

        Returns:
            Text content of the element
        """
        try:
            # Check if selector is XPath
            if selector.startswith("xpath="):
                xpath = selector[6:]  # Remove "xpath=" prefix
                element = await page.wait_for_selector(xpath, state="visible")
                text = await element.text_content()
            else:
                # Treat as CSS selector
                element = await page.wait_for_selector(selector, state="visible")
                text = await element.text_content()
            
            logger.info(f"Got text from element with selector: {selector}")
            return text or ""
        
        except Exception as e:
            logger.error(f"Error getting text from element with selector {selector}: {e}")
            raise AutomationError(f"Error getting text from element with selector {selector}: {e}")

    async def get_attribute(self, page: Page, selector: str, attribute: str) -> str:
        """
        Get attribute value of an element.

        Args:
            page: Playwright Page object
            selector: CSS selector or XPath for the element
            attribute: Name of the attribute

        Returns:
            Attribute value of the element
        """
        try:
            # Check if selector is XPath
            if selector.startswith("xpath="):
                xpath = selector[6:]  # Remove "xpath=" prefix
                element = await page.wait_for_selector(xpath, state="visible")
                attr_value = await element.get_attribute(attribute)
            else:
                # Treat as CSS selector
                element = await page.wait_for_selector(selector, state="visible")
                attr_value = await element.get_attribute(attribute)
            
            logger.info(f"Got attribute '{attribute}' from element with selector: {selector}")
            return attr_value or ""
        
        except Exception as e:
            logger.error(f"Error getting attribute '{attribute}' from element with selector {selector}: {e}")
            raise AutomationError(f"Error getting attribute '{attribute}' from element with selector {selector}: {e}")

    async def extract_data(self, page: Page, selector: str, config: Dict[str, Any]) -> Any:
        """
        Extract data from elements matching a selector.

        Args:
            page: Playwright Page object
            selector: CSS selector or XPath for the elements
            config: Configuration for data extraction

        Returns:
            Extracted data
        """
        try:
            # Get elements matching selector
            if selector.startswith("xpath="):
                xpath = selector[6:]  # Remove "xpath=" prefix
                elements = await page.query_selector_all(xpath)
            else:
                # Treat as CSS selector
                elements = await page.query_selector_all(selector)
            
            # Extract data based on config
            extract_type = config.get("type", "text")
            result = []
            
            for element in elements:
                if extract_type == "text":
                    text = await element.text_content()
                    result.append(text or "")
                elif extract_type == "attribute":
                    attr_name = config.get("attribute", "")
                    attr_value = await element.get_attribute(attr_name)
                    result.append(attr_value or "")
                elif extract_type == "html":
                    html_content = await element.inner_html()
                    result.append(html_content or "")
            
            # If only one element was expected and config specifies single, return just that item
            if config.get("single", False) and len(result) > 0:
                return result[0]
            
            logger.info(f"Extracted {len(result)} items with selector: {selector}")
            return result
        
        except Exception as e:
            logger.error(f"Error extracting data with selector {selector}: {e}")
            raise AutomationError(f"Error extracting data with selector {selector}: {e}")
