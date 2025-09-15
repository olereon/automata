"""
Selector generator tool that converts HTML to robust selectors.
"""

import os
import re
import sys
from typing import Dict, Any, Optional, List, Union, Tuple
from lxml import html, etree
from ..core.errors import AutomationError, XPathError, XPathSyntaxError, XPathEvaluationError, XPathUnsupportedFeatureError
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
        self.important_elements = [
            "button", "input", "a", "select", "textarea", "form",
            "img", "table", "tr", "td", "th", "ul", "ol", "li"
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
            xpath = "//" + "/".join(path)
            
            # Try to make it more specific with attributes
            specific_xpath = self._make_xpath_more_specific(element, xpath)
            
            return f"xpath={specific_xpath}"
        
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

    def generate_from_file(self, file_path: str, element_info: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate selectors for an element from an HTML file.

        Args:
            file_path: Path to the HTML file
            element_info: Element information containing xpath or css_selector

        Returns:
            Dictionary with different types of selectors
        """
        logger.info(f"Generating selectors from HTML file: {file_path}")
        
        try:
            # Read HTML file
            with open(file_path, "r", encoding="utf-8") as f:
                html_content = f.read()
            
            # Generate selectors
            selectors = self.generate_selectors(html_content, element_info)
            
            logger.info(f"Generated {len(selectors)} selectors from file: {file_path}")
            return selectors
        
        except Exception as e:
            logger.error(f"Error generating selectors from file: {e}")
            raise AutomationError(f"Error generating selectors from file: {e}")

    def generate_from_file_legacy(self, file_path: str) -> Dict[str, str]:
        """
        Generate selectors for elements from an HTML file (legacy mode).

        Args:
            file_path: Path to the HTML file

        Returns:
            Dictionary with different types of selectors
        """
        logger.info(f"Generating selectors from HTML file (legacy mode): {file_path}")
        
        try:
            # Read HTML file
            with open(file_path, "r", encoding="utf-8") as f:
                html_content = f.read()
            
            # Parse HTML
            parsed_html = html.fromstring(html_content)
            
            # Find important elements
            important_elements = []
            
            # Find elements with important tags
            for tag in self.important_elements:
                elements = parsed_html.xpath(f"//{tag}")
                important_elements.extend(elements)
            
            # Find elements with IDs
            id_elements = parsed_html.xpath("//*[@id]")
            important_elements.extend(id_elements)
            
            # Remove duplicates while preserving order
            seen = set()
            unique_elements = []
            for element in important_elements:
                if element not in seen:
                    seen.add(element)
                    unique_elements.append(element)
            
            # Generate selectors for each important element
            all_selectors = {}
            for element in unique_elements:
                element_selectors = {
                    "xpath": self._generate_xpath(element),
                    "css": self._generate_css_selector(element),
                    "id": self._generate_id_selector(element),
                    "name": self._generate_name_selector(element),
                    "text": self._generate_text_selector(element),
                    "attribute": self._generate_attribute_selector(element),
                    "combined": self._generate_combined_selector(element)
                }
                
                # Filter out empty selectors
                element_selectors = {k: v for k, v in element_selectors.items() if v}
                
                # Add to all selectors
                all_selectors.update(element_selectors)
            
            logger.info(f"Generated {len(all_selectors)} selectors from file (legacy mode): {file_path}")
            return all_selectors
        
        except Exception as e:
            logger.error(f"Error generating selectors from file (legacy mode): {e}")
            raise AutomationError(f"Error generating selectors from file: {e}")


    def save_selectors(self, selectors: Dict[str, str], output_path: str) -> None:
        """
        Save selectors to a file.

        Args:
            selectors: Dictionary of selectors
            output_path: Path to save the file
        """
        logger.info(f"Saving selectors to: {output_path}")
        
        try:
            import json
            
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(selectors, f, indent=2)
            
            logger.info(f"Selectors saved successfully to: {output_path}")
        
        except Exception as e:
            logger.error(f"Error saving selectors: {e}")
            raise AutomationError(f"Error saving selectors: {e}")

    def is_html_fragment(self, html_content: str) -> bool:
        """
        Detect if the input is an HTML fragment (missing DOCTYPE, html, or body tags).

        Args:
            html_content: HTML content to check

        Returns:
            True if the content is a fragment, False if it's a complete HTML document
        
        Raises:
            AutomationError: If the HTML content is invalid or empty
        """
        try:
            # Check if HTML content is empty
            if not html_content or not html_content.strip():
                raise AutomationError("HTML content is empty")
            
            # Normalize whitespace and convert to lowercase for checking
            normalized = html_content.strip().lower()
            
            # Check if it has DOCTYPE
            if normalized.startswith('<!doctype'):
                return False
            
            # Check if it has html tag
            if '<html' in normalized[:1000]:  # Check first 1000 chars for efficiency
                return False
            
            # Check if it has body tag
            if '<body' in normalized[:1000]:  # Check first 1000 chars for efficiency
                return False
            
            # If none of the above, it's likely a fragment
            return True
        
        except AutomationError:
            # Re-raise AutomationError as-is
            raise
        except Exception as e:
            logger.warning(f"Error detecting HTML fragment: {e}")
            # Default to treating as fragment if detection fails
            return True

    def wrap_html_fragment(self, html_fragment: str) -> str:
        """
        Wrap an HTML fragment in a basic HTML structure.

        Args:
            html_fragment: HTML fragment to wrap

        Returns:
            Complete HTML document with the fragment wrapped in body tags
        
        Raises:
            AutomationError: If the HTML fragment is invalid or cannot be wrapped
        """
        try:
            # Check if HTML fragment is empty
            if not html_fragment or not html_fragment.strip():
                raise AutomationError("HTML fragment is empty")
            
            # Strip leading/trailing whitespace from the fragment
            fragment = html_fragment.strip()
            
            # Basic validation - check if it contains at least one HTML tag
            if not re.search(r'<[^>]+>', fragment):
                raise AutomationError("HTML fragment does not contain any valid HTML tags")
            
            # Create the wrapper HTML
            wrapped_html = f"""<!DOCTYPE html>
<html>
<head>
    <title>HTML Fragment</title>
</head>
<body>
{fragment}
</body>
</html>"""
            
            # Validate the wrapped HTML by trying to parse it
            try:
                html.fromstring(wrapped_html)
            except Exception as parse_error:
                raise AutomationError(f"Wrapped HTML is invalid: {parse_error}")
            
            return wrapped_html
        
        except AutomationError:
            # Re-raise AutomationError as-is
            raise
        except Exception as e:
            logger.error(f"Error wrapping HTML fragment: {e}")
            raise AutomationError(f"Error wrapping HTML fragment: {e}")

    def generate_from_fragment(
        self,
        html_fragment: str,
        targeting_mode: str = "all",
        custom_selector: Optional[str] = None,
        selector_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate selectors for elements in an HTML fragment.

        Args:
            html_fragment: HTML fragment content
            targeting_mode: How to target elements ("all", "selector", "auto")
            custom_selector: Custom selector to use when targeting_mode is "selector"
            selector_type: Type of custom selector ("css" or "xpath")

        Returns:
            Dictionary with selectors for targeted elements
        
        Raises:
            AutomationError: If there's an error processing the HTML fragment or generating selectors
        """
        logger.info(f"Generating selectors from HTML fragment with targeting mode: {targeting_mode}")
        
        try:
            # Validate targeting mode
            if targeting_mode not in ["all", "selector", "auto"]:
                raise AutomationError(f"Invalid targeting mode: {targeting_mode}. Must be one of: all, selector, auto")
            
            # Validate custom selector parameters
            if targeting_mode == "selector":
                if not custom_selector:
                    raise AutomationError("Custom selector is required when targeting_mode is 'selector'")
                if not custom_selector.strip():
                    raise AutomationError("Custom selector cannot be empty")
                if selector_type and selector_type not in ["css", "xpath"]:
                    raise AutomationError(f"Invalid selector type: {selector_type}. Must be one of: css, xpath")
            
            # Check if it's a fragment and wrap if needed
            if self.is_html_fragment(html_fragment):
                logger.info("Detected HTML fragment, wrapping in complete HTML structure")
                html_content = self.wrap_html_fragment(html_fragment)
            else:
                html_content = html_fragment
            
            # Parse HTML
            try:
                parsed_html = html.fromstring(html_content)
            except Exception as parse_error:
                raise AutomationError(f"Failed to parse HTML content: {parse_error}")
            
            # Find target elements based on targeting mode
            target_elements = []
            
            if targeting_mode == "all":
                # Get all elements in the fragment
                target_elements = self._get_all_elements(parsed_html)
            elif targeting_mode == "selector":
                # Use custom selector to find elements
                target_elements = self._find_elements_by_selector(
                    parsed_html, custom_selector, selector_type or "css"
                )
                
                # Check if any elements were found
                if not target_elements:
                    logger.warning(f"No elements found using selector: {custom_selector}")
                    return {}
            elif targeting_mode == "auto":
                # Auto-detect important elements
                target_elements = self._auto_detect_important_elements(parsed_html)
            
            if not target_elements:
                logger.warning("No target elements found in HTML fragment")
                return {}
            
            # Generate selectors for each target element
            results = {}
            for i, element in enumerate(target_elements):
                # Create element info for this element
                element_info = {}
                
                # Try to generate a unique identifier for this element
                element_id = f"element_{i}"
                
                # Generate selectors for this element
                selectors = self._generate_selectors_for_element(element, html_content)
                
                if selectors:
                    results[element_id] = {
                        "selectors": selectors,
                        "element_tag": element.tag,
                        "element_text": element.text_content().strip()[:50] if element.text_content() else ""
                    }
            
            logger.info(f"Generated selectors for {len(results)} elements from HTML fragment")
            return results
        
        except AutomationError:
            # Re-raise AutomationError as-is
            raise
        except Exception as e:
            logger.error(f"Error generating selectors from HTML fragment: {e}")
            raise AutomationError(f"Error generating selectors from HTML fragment: {e}")

    def _generate_selectors_for_element(self, element: html.HtmlElement, html_content: str) -> Dict[str, str]:
        """
        Generate selectors for a specific element.

        Args:
            element: HTML element to generate selectors for
            html_content: Full HTML content

        Returns:
            Dictionary with different types of selectors
        """
        try:
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
            
            return selectors
        
        except Exception as e:
            logger.warning(f"Error generating selectors for element: {e}")
            return {}

    def _get_all_elements(self, parsed_html: html.HtmlElement) -> List[html.HtmlElement]:
        """
        Get all elements from the parsed HTML.

        Args:
            parsed_html: Parsed HTML document

        Returns:
            List of all HTML elements
        """
        try:
            # Use XPath to get all elements
            all_elements = parsed_html.xpath("//*")
            
            # Filter out the html and body elements as they're part of our wrapper
            filtered_elements = [el for el in all_elements if el.tag not in ["html", "body"]]
            
            return filtered_elements
        
        except Exception as e:
            logger.warning(f"Error getting all elements: {e}")
            return []

    def _find_elements_by_selector(
        self,
        parsed_html: html.HtmlElement,
        selector: str,
        selector_type: str
    ) -> List[html.HtmlElement]:
        """
        Find elements using a custom selector.

        Args:
            parsed_html: Parsed HTML document
            selector: Selector to use
            selector_type: Type of selector ("css" or "xpath")

        Returns:
            List of matching HTML elements
        
        Raises:
            AutomationError: If the selector is invalid or cannot be processed
        """
        try:
            if not selector or not selector.strip():
                raise AutomationError("Selector cannot be empty")
            
            elements = []
            
            if selector_type == "css":
                try:
                    elements = parsed_html.cssselect(selector)
                except Exception as css_error:
                    raise AutomationError(f"Invalid CSS selector '{selector}': {css_error}")
            elif selector_type == "xpath":
                try:
                    elements = parsed_html.xpath(selector)
                except Exception as xpath_error:
                    raise AutomationError(f"Invalid XPath selector '{selector}': {xpath_error}")
            else:
                raise AutomationError(f"Unsupported selector type: {selector_type}")
            
            return elements
        
        except AutomationError:
            # Re-raise AutomationError as-is
            raise
        except Exception as e:
            logger.warning(f"Error finding elements by selector: {e}")
            return []

    def _auto_detect_important_elements(self, parsed_html: html.HtmlElement) -> List[html.HtmlElement]:
        """
        Auto-detect important elements in the HTML.

        Args:
            parsed_html: Parsed HTML document

        Returns:
            List of important HTML elements
        """
        try:
            important_elements = []
            
            # Find elements with important tags
            for tag in self.important_elements:
                elements = parsed_html.xpath(f"//{tag}")
                important_elements.extend(elements)
            
            # Find elements with IDs
            id_elements = parsed_html.xpath("//*[@id]")
            important_elements.extend(id_elements)
            
            # Find elements with test attributes
            for attr in ["data-testid", "data-test", "data-cy", "data-qa"]:
                elements = parsed_html.xpath(f"//*[@{attr}]")
                important_elements.extend(elements)
            
            # Remove duplicates while preserving order
            seen = set()
            unique_elements = []
            for element in important_elements:
                if element not in seen:
                    seen.add(element)
                    unique_elements.append(element)
            
            return unique_elements
        
        except Exception as e:
            logger.warning(f"Error auto-detecting important elements: {e}")
            return []

    def generate_from_fragment_file(
        self,
        file_path: str,
        targeting_mode: str = "all",
        custom_selector: Optional[str] = None,
        selector_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate selectors for elements from an HTML fragment file.

        Args:
            file_path: Path to the HTML fragment file
            targeting_mode: How to target elements ("all", "selector", "auto")
            custom_selector: Custom selector to use when targeting_mode is "selector"
            selector_type: Type of custom selector ("css" or "xpath")

        Returns:
            Dictionary with selectors for targeted elements
        
        Raises:
            AutomationError: If there's an error reading the file or generating selectors
        """
        logger.info(f"Generating selectors from HTML fragment file: {file_path}")
        
        try:
            # Check if file exists
            if not os.path.exists(file_path):
                raise AutomationError(f"File not found: {file_path}")
            
            # Check if it's a file (not a directory)
            if not os.path.isfile(file_path):
                raise AutomationError(f"Path is not a file: {file_path}")
            
            # Read HTML fragment file
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    html_fragment = f.read()
            except Exception as file_error:
                raise AutomationError(f"Error reading file {file_path}: {file_error}")
            
            # Check if file is empty
            if not html_fragment or not html_fragment.strip():
                raise AutomationError(f"File is empty: {file_path}")
            
            # Generate selectors
            results = self.generate_from_fragment(
                html_fragment, targeting_mode, custom_selector, selector_type
            )
            
            logger.info(f"Generated selectors for {len(results)} elements from file: {file_path}")
            return results
        
        except AutomationError:
            # Re-raise AutomationError as-is
            raise
        except Exception as e:
            logger.error(f"Error generating selectors from fragment file: {e}")
            raise AutomationError(f"Error generating selectors from fragment file: {e}")

    def generate_from_stdin(
        self,
        targeting_mode: str = "all",
        custom_selector: Optional[str] = None,
        selector_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate selectors for elements from HTML fragment read from stdin.

        Args:
            targeting_mode: How to target elements ("all", "selector", "auto")
            custom_selector: Custom selector to use when targeting_mode is "selector"
            selector_type: Type of custom selector ("css" or "xpath")

        Returns:
            Dictionary with selectors for targeted elements
        """
        logger.info("Generating selectors from HTML fragment from stdin")
        
        try:
            # Read HTML fragment from stdin
            if sys.stdin.isatty():
                # No input from stdin
                raise AutomationError("No HTML fragment provided via stdin")
            
            html_fragment = sys.stdin.read()
            
            if not html_fragment.strip():
                raise AutomationError("Empty HTML fragment provided via stdin")
            
            # Generate selectors
            results = self.generate_from_fragment(
                html_fragment, targeting_mode, custom_selector, selector_type
            )
            
            logger.info(f"Generated selectors for {len(results)} elements from stdin")
            return results
        
        except Exception as e:
            logger.error(f"Error generating selectors from stdin: {e}")
            raise AutomationError(f"Error generating selectors from stdin: {e}")

    def validate_xpath(self, xpath_expression: str) -> bool:
        """
        Validate an XPath expression for syntax correctness.

        Args:
            xpath_expression: XPath expression to validate

        Returns:
            True if the XPath expression is valid, False otherwise

        Raises:
            XPathSyntaxError: If the XPath expression has syntax errors
            XPathUnsupportedFeatureError: If the XPath expression uses unsupported features
        """
        try:
            if not xpath_expression or not xpath_expression.strip():
                raise XPathSyntaxError("XPath expression cannot be empty")

            # Basic syntax validation
            xpath = xpath_expression.strip()

            # Check for balanced brackets and parentheses
            if xpath.count("[") != xpath.count("]"):
                raise XPathSyntaxError("Unbalanced brackets in XPath expression")
            if xpath.count("(") != xpath.count(")"):
                raise XPathSyntaxError("Unbalanced parentheses in XPath expression")

            # Check for unsupported features
            unsupported_features = [
                # XPath axes
                "ancestor::", "ancestor-or-self::", "attribute::", "child::",
                "descendant::", "descendant-or-self::", "following::",
                "following-sibling::", "namespace::", "parent::",
                "preceding::", "preceding-sibling::", "self::",
                # XPath functions
                "namespace-uri(", "name(", "local-name(", "translate(",
                "normalize-space(", "string(", "number(", "boolean(",
                "not(", "true(", "false(", "lang(", "sum(", "floor(",
                "ceiling(", "round(", "concat(", "starts-with(",
                "contains(", "substring-before(", "substring-after(",
                "substring(", "string-length(", "current()", "id("
            ]

            for feature in unsupported_features:
                if feature in xpath:
                    raise XPathUnsupportedFeatureError(f"Unsupported XPath feature: {feature}")

            # Check for unsupported patterns
            # Allow wildcards when they're used with predicates (conditions in square brackets)
            if "//*" in xpath and not re.search(r"\/\/\*\[", xpath):
                raise XPathUnsupportedFeatureError("Unsupported XPath feature: wildcard (//*) without predicates")
            if re.search(r"\[\d+\]", xpath):
                raise XPathUnsupportedFeatureError("Unsupported XPath feature: numeric predicate")
            if re.search(r"\s+and\s+|\s+or\s+", xpath):
                raise XPathUnsupportedFeatureError("Unsupported XPath feature: logical operators")

            # Try to compile the XPath to validate syntax
            try:
                from lxml import etree
                etree.XPath(xpath)
            except Exception as e:
                raise XPathSyntaxError(f"Invalid XPath syntax: {e}")

            return True

        except XPathError:
            # Re-raise XPathError as-is
            raise
        except Exception as e:
            logger.error(f"Error validating XPath expression: {e}")
            raise XPathSyntaxError(f"Error validating XPath expression: {e}")

    def prepare_html_context(self, html_context: str) -> str:
        """
        Prepare HTML context for XPath evaluation.

        Args:
            html_context: HTML context string

        Returns:
            Prepared HTML context

        Raises:
            AutomationError: If the HTML context is invalid or cannot be prepared
        """
        try:
            if not html_context or not html_context.strip():
                # Create a minimal mock HTML structure if no context is provided
                return """<!DOCTYPE html>
<html>
<head>
    <title>Mock HTML Context</title>
</head>
<body>
    <div id="content">
        <!-- User's XPath will be evaluated against this structure -->
    </div>
</body>
</html>"""

            # Check if it's a fragment and wrap if needed
            if self.is_html_fragment(html_context):
                logger.info("Detected HTML fragment context, wrapping in complete HTML structure")
                return self.wrap_html_fragment(html_context)
            else:
                return html_context

        except Exception as e:
            logger.error(f"Error preparing HTML context: {e}")
            raise AutomationError(f"Error preparing HTML context: {e}")

    def generate_from_xpath(
        self,
        xpath_expression: str,
        html_context: str
    ) -> Dict[str, Any]:
        """
        Generate selectors for elements found using an XPath expression.

        Args:
            xpath_expression: XPath expression to evaluate
            html_context: HTML context to evaluate the XPath against

        Returns:
            Dictionary with selectors for elements found by the XPath

        Raises:
            XPathError: If there's an error with the XPath expression or evaluation
            AutomationError: If there's an error processing the HTML context
        """
        logger.info(f"Generating selectors from XPath expression: {xpath_expression}")

        try:
            # Validate XPath expression
            self.validate_xpath(xpath_expression)

            # Prepare HTML context
            prepared_html = self.prepare_html_context(html_context)

            # Parse HTML
            try:
                parsed_html = html.fromstring(prepared_html)
            except Exception as parse_error:
                raise AutomationError(f"Failed to parse HTML context: {parse_error}")

            # Find elements using XPath
            try:
                elements = parsed_html.xpath(xpath_expression)
            except Exception as xpath_error:
                raise XPathEvaluationError(f"Error evaluating XPath expression: {xpath_error}")

            if not elements:
                logger.warning(f"No elements found using XPath expression: {xpath_expression}")
                return {}

            # Generate selectors for each found element
            results = {}
            for i, element in enumerate(elements):
                # Create element info for this element
                element_id = f"element_{i}"

                # Generate selectors for this element
                selectors = self._generate_selectors_for_element(element, prepared_html)

                if selectors:
                    results[element_id] = {
                        "selectors": selectors,
                        "element_tag": element.tag,
                        "element_text": element.text_content().strip()[:50] if element.text_content() else "",
                        "source_xpath": xpath_expression,
                        "html_context": html_context[:100] + "..." if len(html_context) > 100 else html_context
                    }

            logger.info(f"Generated selectors for {len(results)} elements from XPath expression")
            return results

        except XPathError:
            # Re-raise XPathError as-is
            raise
        except Exception as e:
            logger.error(f"Error generating selectors from XPath: {e}")
            raise AutomationError(f"Error generating selectors from XPath: {e}")

    def generate_from_xpath_file(
        self,
        xpath_file_path: str,
        html_context: str
    ) -> Dict[str, Any]:
        """
        Generate selectors for elements found using an XPath expression from a file.

        Args:
            xpath_file_path: Path to the file containing the XPath expression
            html_context: HTML context to evaluate the XPath against

        Returns:
            Dictionary with selectors for elements found by the XPath

        Raises:
            XPathError: If there's an error with the XPath expression or evaluation
            AutomationError: If there's an error reading the file or processing the HTML context
        """
        logger.info(f"Generating selectors from XPath file: {xpath_file_path}")

        try:
            # Check if file exists
            if not os.path.exists(xpath_file_path):
                raise AutomationError(f"XPath file not found: {xpath_file_path}")

            # Check if it's a file (not a directory)
            if not os.path.isfile(xpath_file_path):
                raise AutomationError(f"XPath file path is not a file: {xpath_file_path}")

            # Read XPath expression from file
            try:
                with open(xpath_file_path, "r", encoding="utf-8") as f:
                    xpath_expression = f.read().strip()
            except Exception as file_error:
                raise AutomationError(f"Error reading XPath file {xpath_file_path}: {file_error}")

            # Check if file is empty
            if not xpath_expression:
                raise AutomationError(f"XPath file is empty: {xpath_file_path}")

            # Generate selectors using the XPath expression
            results = self.generate_from_xpath(xpath_expression, html_context)

            logger.info(f"Generated selectors for {len(results)} elements from XPath file: {xpath_file_path}")
            return results

        except AutomationError:
            # Re-raise AutomationError as-is
            raise
        except Exception as e:
            logger.error(f"Error generating selectors from XPath file: {e}")
            raise AutomationError(f"Error generating selectors from XPath file: {e}")
