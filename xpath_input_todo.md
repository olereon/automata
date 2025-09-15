# XPath Input Support Implementation Todo List

## Phase 1: Core Infrastructure
- [x] Add XPath-specific error classes to src/automata/core/errors.py
- [x] Create XPath validation utilities in src/automata/tools/selector_generator.py
- [x] Implement HTML context handling for XPath evaluation

## Phase 2: CLI Interface Extension
- [x] Extend the generate_selectors CLI command with --xpath-expression option
- [x] Extend the generate_selectors CLI command with --xpath-file option
- [x] Add --html-context and --html-context-file options
- [x] Implement input validation logic for XPath options

## Phase 3: Selector Generator Extension
- [x] Add generate_from_xpath method to SelectorGenerator class
- [x] Add generate_from_xpath_file method to SelectorGenerator class
- [x] Extend selector ranking system for XPath-based selectors
- [x] Implement output format enhancements for XPath-based generation

## Phase 4: Testing
- [x] Create unit tests for XPath validation
- [x] Create unit tests for HTML context handling
- [x] Create unit tests for selector generation from XPath
- [x] Create integration tests for CLI XPath options
- [x] Create error handling tests

## Phase 5: Documentation
- [x] Update CLI help text for new options
- [x] Create user documentation for XPath input feature
- [x] Update developer documentation
