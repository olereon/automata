# XPath Input Functionality

## Overview

The XPath input functionality allows users to generate selectors from XPath expressions or XPath files, providing an alternative way to target elements in HTML documents.

## Features

- **XPath Expression Input**: Direct input of XPath expressions via command line
- **XPath File Input**: Read XPath expressions from files
- **HTML Context Handling**: Provide HTML context for XPath evaluation
- **XPath Validation**: Validate XPath expressions before processing
- **Error Handling**: Comprehensive error reporting for invalid XPath

## Usage

### Command Line Options

The `generate-selectors` command in the `helper` group supports the following new options:

- `--xpath-expression`: Direct XPath expression input
- `--xpath-file`: Path to XPath expression file
- `--html-context`: HTML context for XPath evaluation
- `--html-context-file`: Path to HTML context file

### Examples

#### Generate selectors from XPath expression

```bash
python -m automata.cli helper generate-selectors \
  --xpath-expression "//button[@class='submit']" \
  --html-context-file page.html \
  --output selectors.json
```

#### Generate selectors from XPath file

```bash
python -m automata.cli.helper generate-selectors \
  --xpath-file expressions.xpath \
  --html-context-file page.html \
  --output selectors.json
```

#### Using inline HTML context

```bash
python -m automata.cli.helper generate-selectors \
  --xpath-expression "//div[@id='content']" \
  --html-context "<html><body><div id='content'>...</div></body></html>" \
  --output selectors.json
```

## XPath Support

### Supported XPath Features

- Element selection by tag name
- Attribute selection with `[@attribute='value']`
- ID selection with `[@id='value']`
- Class selection with `[@class='value']`
- Basic hierarchy navigation with `/` and `//`
- Wildcards with `*` (only when used with predicates, e.g., `//*[@id="submit"]`)

### Unsupported XPath Features

The following XPath features are not currently supported:

- Functions like `contains()`, `starts-with()`, `text()`
- Axes like `ancestor`, `descendant`, `following`, `preceding`
- Conditional expressions with `and`, `or`
- Numeric predicates like `[1]`, `[position()=2]`
- Wildcards without predicates (e.g., `//*`)

## Error Handling

### XPath Syntax Errors

If an XPath expression contains syntax errors (e.g., unbalanced brackets), the system will report:

```
Error: Invalid XPath syntax: Unbalanced brackets in expression
```

### Unsupported Features

If an XPath expression contains unsupported features, the system will report:

```
Error: Unsupported XPath feature: contains() function is not supported
```

### Missing HTML Context

If an XPath expression is provided without HTML context, the system will report:

```
Error: HTML context is required when using XPath input. Use --html-context or --html-context-file
```

## Output Format

The output format is consistent with other selector generation methods:

```json
{
  "element_0": {
    "selectors": {
      "id": "#submit-button",
      "css": "button.btn.primary",
      "xpath": "//button[@class='btn primary']"
    },
    "element_tag": "button",
    "element_text": "Submit"
  }
}
```

## Implementation Details

### Architecture

The XPath input functionality is implemented across several components:

1. **SelectorGenerator**: Extended with XPath processing methods
2. **CLI Interface**: Extended with XPath input options
3. **Error Handling**: Custom XPath error classes
4. **Validation**: XPath syntax and feature validation

### Processing Flow

1. Parse command line options
2. Validate XPath expression (if provided directly)
3. Read XPath expression from file (if provided)
4. Validate HTML context is provided
5. Read HTML context from file or use direct input
6. Prepare HTML context for evaluation
7. Evaluate XPath expression against HTML context
8. Generate selectors for matched elements
9. Output results in JSON format

## Testing

Comprehensive tests are provided to verify:

- XPath validation functionality
- HTML context preparation
- Selector generation from XPath expressions
- Selector generation from XPath files
- CLI interface with XPath options
- Error handling for various scenarios

Run tests with:

```bash
python test_xpath_input.py
python test_cli_xpath.py
```
