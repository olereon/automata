"""
Selector generator tool that converts HTML to robust selectors.
"""

import re
from typing import Dict, Any, Optional, List, Union, Tuple
from lxml import html, etree
from ..core.errors import AutomationError
from ..core.logger import get_logger

logger = get_logger(__name__)


class SelectorGenerator:
    """Generates robust selectors from HTML elements."""

    def __init__(self):
        """Initialize the selector generator."""
        self.attribute_priority = [
            "id", "name", "data-testid", "data-test", "data-cy", "data-qa",
            "title", "alt", "placeholder", "type", "value", "href", "src"
        ]

    def generate_selectors(self, html_content: str, element_info: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate multiple types of selectors for an element.

        Args:
            html_content: HTML content of the page
            element_info: Element information containing xpath or css_selector

        Returns:
            Dictionary with different types of selectors
        """
        try:
            # Parse HTML
            parsed_html = html.fromstring(html_content)
            
            # Find the element
            element = None
            if "xpath" in element_info and element_info["xpath"]:
                element = parsed_html.xpath(element_info["xpath"])
                if element:
                    element = element[0]
            
            if not element and "css_selector" in element_info and element_info["css_selector"]:
                element = parsed_html.cssselect(element_info["css_selector"])
                if element:
                    element = element[0]
            
            if not element:
                logger.error("Element not found in HTML content")
                return {}
            
            # Generate different types of selectors
            selectors = {
                "xpath": self._generate_xpath(element),
                "css": self._generate_css_selector(element),
                "id": self._generate_id_selector(element),
                "name": self._generate_name_selector(element),
                "text": self._generate_text_selector(element),
                "attribute": self._generate_attribute_selector(element),
                "combined": self._generate_combined_selector(element)
            }
            
            # Filter out empty selectors
            selectors = {k: v for k, v in selectors.items() if v}
            
            logger.info(f"Generated {len(selectors)} selectors for element")
            return selectors
        
        except Exception as e:
            logger.error(f"Error generating selectors: {e}")
            return {}

    def _generate_xpath(self, element: html.HtmlElement) -> str:
        """
        Generate a robust XPath for an element.

        Args:
            element: HTML element

        Returns:
            XPath string
        """
        try:
            # Start with the element itself
            path = []
            current = element
            
            # Traverse up the DOM tree
            while current is not None:
                # Get element tag
                tag = current.tag
                
                # Get position among siblings
                siblings = current.xpath(f"./preceding-sibling::{tag}")
                position = len(siblings) + 1
                
                # Build path segment
                if position == 1 and len(current.xpath(f"./following-sibling::{tag}")) == 0:
                    # No siblings with the same tag
                    path_segment = tag
                else:
                    # Has siblings with the same tag, include position
                    path_segment = f"{tag}[{position}]"
                
                # Add to path
                path.insert(0, path_segment)
                
                # Move to parent
                current = current.getparent()
                
                # Stop at body or html
                if current is not None and current.tag in ["body", "html"]:
                    break
            
            # Join path segments
            xpath = "/" + "/".join(path)
            
            # Try to make it more specific with attributes
            specific_xpath = self._make_xpath_more_specific(element, xpath)
            
            return specific_xpath
        
        except Exception as e:
            logger.warning(f"Error generating XPath: {e}")
            return ""

    def _make_xpath_more_specific(self, element: html.HtmlElement, xpath: str) -> str:
        """
        Make an XPath more specific by adding attributes.

        Args:
            element: HTML element
            xpath: Original XPath

        Returns:
            More specific XPath
        """
        try:
            # Check if element has an ID
            element_id = element.get("id")
            if element_id:
                # Replace the last segment with ID selector
                last_segment = xpath.split("/")[-1]
                tag = last_segment.split("[")[0]
                return xpath.replace(last_segment, f"{tag}[@id='{element_id}']")
            
            # Check for other prioritized attributes
            for attr in self.attribute_priority[1:]:  # Skip ID as we already checked it
                attr_value = element.get(attr)
                if attr_value:
                    # Replace the last segment with attribute selector
                    last_segment = xpath.split("/")[-1]
                    tag = last_segment.split("[")[0]
                    return xpath.replace(last_segment, f"{tag}[@{attr}='{attr_value}']")
            
            # Check for unique class combination
            element_class = element.get("class")
            if element_class:
                classes = element_class.split()
                if len(classes) >= 2:  # Use at least 2 classes for specificity
                    class_selector = " and ".join([f"contains(@class, '{cls}')" for cls in classes])
                    last_segment = xpath.split("/")[-1]
                    tag = last_segment.split("[")[0]
                    return xpath.replace(last_segment, f"{tag}[{class_selector}]")
            
            return xpath
        
        except Exception as e:
            logger.warning(f"Error making XPath more specific: {e}")
            return xpath

    def _generate_css_selector(self, element: html.HtmlElement) -> str:
        """
        Generate a robust CSS selector for an element.

        Args:
            element: HTML element

        Returns:
            CSS selector string
        """
        try:
            # Start with the element tag
            selector = element.tag
            
            # Add ID if present
            element_id = element.get("id")
            if element_id:
                return f"{selector}#{element_id}"
            
            # Add classes if present
            element_class = element.get("class")
            if element_class:
                classes = element_class.split()
                selector += "." + ".".join(classes)
            
            # Add attributes to make it more specific
            for attr in self.attribute_priority:
                if attr == "id":
                    continue  # Already handled
                if attr == "class":
                    continue  # Already handled
                
                attr_value = element.get(attr)
                if attr_value:
                    selector += f'[{attr}="{attr_value}"]'
                    break  # Just add one attribute to keep it simple
            
            # If still not specific enough, add nth-child
            parent = element.getparent()
            if parent is not None:
                siblings = parent.xpath(f"./{element.tag}")
                if len(siblings) > 1:
                    index = siblings.index(element) + 1
                    selector += f":nth-child({index})"
            
            return selector
        
        except Exception as e:
            logger.warning(f"Error generating CSS selector: {e}")
            return element.tag

    def _generate_id_selector(self, element: html.HtmlElement) -> str:
        """
        Generate an ID-based selector for an element.

        Args:
            element: HTML element

        Returns:
            ID selector string or empty string if no ID
        """
        try:
            element_id = element.get("id")
            if element_id:
                return f"#{element_id}"
            return ""
        
        except Exception as e:
            logger.warning(f"Error generating ID selector: {e}")
            return ""

    def _generate_name_selector(self, element: html.HtmlElement) -> str:
        """
        Generate a name-based selector for an element.

        Args:
            element: HTML element

        Returns:
            Name selector string or empty string if no name
        """
        try:
            element_name = element.get("name")
            if element_name:
                return f"[name='{element_name}']"
            return ""
        
        except Exception as e:
            logger.warning(f"Error generating name selector: {e}")
            return ""

    def _generate_text_selector(self, element: html.HtmlElement) -> str:
        """
        Generate a text-based selector for an element.

        Args:
            element: HTML element

        Returns:
            Text selector string or empty string if no text
        """
        try:
            text = element.text_content().strip()
            if text:
                # Escape quotes in text
                escaped_text = text.replace("'", "\\'")
                return f":contains('{escaped_text}')"
            return ""
        
        except Exception as e:
            logger.warning(f"Error generating text selector: {e}")
            return ""

    def _generate_attribute_selector(self, element: html.HtmlElement) -> str:
        """
        Generate an attribute-based selector for an element.

        Args:
            element: HTML element

        Returns:
            Attribute selector string or empty string if no suitable attributes
        """
        try:
            # Try prioritized attributes
            for attr in self.attribute_priority:
                if attr == "id":
                    continue  # Already handled by ID selector
                if attr == "name":
                    continue  # Already handled by name selector
                
                attr_value = element.get(attr)
                if attr_value:
                    return f'[{attr}="{attr_value}"]'
            
            return ""
        
        except Exception as e:
            logger.warning(f"Error generating attribute selector: {e}")
            return ""

    def _generate_combined_selector(self, element: html.HtmlElement) -> str:
        """
        Generate a combined selector using multiple attributes.

        Args:
            element: HTML element

        Returns:
            Combined selector string
        """
        try:
            # Start with tag
            selector = element.tag
            
            # Add ID if present
            element_id = element.get("id")
            if element_id:
                selector += f"#{element_id}"
            
            # Add classes if present
            element_class = element.get("class")
            if element_class:
                classes = element_class.split()
                selector += "." + ".".join(classes)
            
            # Add multiple attributes for robustness
            added_attrs = 0
            for attr in self.attribute_priority:
                if attr == "id" or attr == "class":
                    continue  # Already handled
                
                attr_value = element.get(attr)
                if attr_value and added_attrs < 2:  # Limit to 2 additional attributes
                    selector += f'[{attr}="{attr_value}"]'
                    added_attrs += 1
            
            return selector
        
        except Exception as e:
            logger.warning(f"Error generating combined selector: {e}")
            return element.tag

    def rank_selectors(self, selectors: Dict[str, str]) -> List[Tuple[str, str, int]]:
        """
        Rank selectors by robustness.

        Args:
            selectors: Dictionary of selector types and values

        Returns:
            List of tuples (selector_type, selector_value, score) sorted by score (higher is better)
        """
        try:
            ranked_selectors = []
            
            for selector_type, selector_value in selectors.items():
                score = self._score_selector(selector_type, selector_value)
                ranked_selectors.append((selector_type, selector_value, score))
            
            # Sort by score (descending)
            ranked_selectors.sort(key=lambda x: x[2], reverse=True)
            
            return ranked_selectors
        
        except Exception as e:
            logger.error(f"Error ranking selectors: {e}")
            return []

    def _score_selector(self, selector_type: str, selector_value: str) -> int:
        """
        Score a selector based on its robustness.

        Args:
            selector_type: Type of selector
            selector_value: Selector value

        Returns:
            Score (higher is better)
        """
        try:
            score = 0
            
            # Base score by selector type
            if selector_type == "id":
                score = 100  # ID selectors are the most robust
            elif selector_type == "combined":
                score = 90
            elif selector_type == "xpath":
                score = 80
            elif selector_type == "css":
                score = 70
            elif selector_type == "name":
                score = 60
            elif selector_type == "attribute":
                score = 50
            elif selector_type == "text":
                score = 40  # Text selectors are less robust
            else:
                score = 30
            
            # Adjust score based on selector characteristics
            if selector_value:
                # ID selector
                if "#" in selector_value:
                    score += 20
                
                # Multiple classes
                class_count = selector_value.count(".")
                if class_count >= 2:
                    score += 10
                
                # Multiple attributes
                attr_count = selector_value.count("[")
                if attr_count >= 2:
                    score += 10
                
                # XPath with predicates
                if selector_type == "xpath" and "@" in selector_value:
                    score += 15
                
                # Penalize for text-based selectors
                if ":contains" in selector_value:
                    score -= 20
                
                # Penalize for positional selectors
                if ":nth-child" in selector_value or "[position()" in selector_value:
                    score -= 10
            
            return max(0, score)  # Ensure score is not negative
        
        except Exception as e:
            logger.warning(f"Error scoring selector: {e}")
            return 0

    def get_best_selector(self, selectors: Dict[str, str]) -> Tuple[str, str]:
        """
        Get the best selector from a dictionary of selectors.

        Args:
            selectors: Dictionary of selector types and values

        Returns:
            Tuple of (selector_type, selector_value)
        """
        try:
            ranked_selectors = self.rank_selectors(selectors)
            
            if ranked_selectors:
                return ranked_selectors[0][0], ranked_selectors[0][1]
            else:
                return "", ""
        
        except Exception as e:
            logger.error(f"Error getting best selector: {e}")
            return "", ""

    def validate_selector(self, html_content: str, selector: str, selector_type: str = "css") -> bool:
        """
        Validate a selector against HTML content.

        Args:
            html_content: HTML content
            selector: Selector to validate
            selector_type: Type of selector (css or xpath)

        Returns:
            True if selector is valid, False otherwise
        """
        try:
            # Parse HTML
            parsed_html = html.fromstring(html_content)
            
            # Try to find element with selector
            if selector_type == "css":
                elements = parsed_html.cssselect(selector)
            elif selector_type == "xpath":
                elements = parsed_html.xpath(selector)
            else:
                logger.error(f"Unsupported selector type: {selector_type}")
                return False
            
            # Check if exactly one element was found
            return len(elements) == 1
        
        except Exception as e:
            logger.warning(f"Error validating selector: {e}")
            return False

    def optimize_selector(self, html_content: str, selector: str, selector_type: str = "css") -> str:
        """
        Optimize a selector to make it more robust.

        Args:
            html_content: HTML content
            selector: Selector to optimize
            selector_type: Type of selector (css or xpath)

        Returns:
            Optimized selector
        """
        try:
            # Parse HTML
            parsed_html = html.fromstring(html_content)
            
            # Find element with selector
            if selector_type == "css":
                elements = parsed_html.cssselect(selector)
            elif selector_type == "xpath":
                elements = parsed_html.xpath(selector)
            else:
                logger.error(f"Unsupported selector type: {selector_type}")
                return selector
            
            # Check if exactly one element was found
            if len(elements) != 1:
                logger.warning(f"Selector matches {len(elements)} elements, cannot optimize")
                return selector
            
            element = elements[0]
            
            # Generate new selectors
            element_info = {f"{selector_type}_selector": selector}
            new_selectors = self.generate_selectors(html_content, element_info)
            
            # Get the best selector
            best_type, best_selector = self.get_best_selector(new_selectors)
            
            if best_selector:
                return best_selector
            else:
                return selector
        
        except Exception as e:
            logger.warning(f"Error optimizing selector: {e}")
            return selector
