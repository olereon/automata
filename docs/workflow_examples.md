# Workflow Examples

## Table of Contents
- [Introduction](#introduction)
- [Web Scraping Examples](#web-scraping-examples)
  - [Simple Web Scraping](#simple-web-scraping)
  - [Pagination Handling](#pagination-handling)
  - [JavaScript-Rendered Content](#javascript-rendered-content)
- [Form Interaction Examples](#form-interaction-examples)
  - [Simple Form Submission](#simple-form-submission)
  - [Multi-Step Form](#multi-step-form)
  - [File Upload](#file-upload)
- [Data Extraction Examples](#data-extraction-examples)
  - [Table Data Extraction](#table-data-extraction)
  - [Product Information Extraction](#product-information-extraction)
  - [News Article Extraction](#news-article-extraction)
- [Authentication Examples](#authentication-examples)
  - [Form-Based Login](#form-based-login)
  - [OAuth Login](#oauth-login)
  - [Session Management](#session-management)
- [Testing Examples](#testing-examples)
  - [Form Validation Testing](#form-validation-testing)
  - [Link Checking](#link-checking)
  - [Performance Testing](#performance-testing)
- [Advanced Examples](#advanced-examples)
  - [Conditional Workflows](#conditional-workflows)
  - [Loop-Based Workflows](#loop-based-workflows)
  - [Error Handling and Recovery](#error-handling-and-recovery)

## Introduction

This document provides a collection of workflow examples for common automation scenarios. Each example includes a complete workflow definition in JSON format, along with an explanation of what the workflow does and how it works.

These examples are designed to help you understand how to use Automata for your own automation tasks and to serve as starting points that you can customize for your specific needs.

## Web Scraping Examples

### Simple Web Scraping

This example demonstrates how to scrape data from a simple web page. The workflow navigates to a page, waits for the content to load, extracts the titles and descriptions of all articles, and saves the results to a JSON file.

```json
{
  "name": "Simple Web Scraping",
  "version": "1.0.0",
  "description": "Scrape article titles and descriptions from a news website",
  "variables": {
    "url": "https://example-news.com",
    "output_file": "articles.json"
  },
  "steps": [
    {
      "name": "Navigate to page",
      "action": "navigate",
      "value": "{{url}}"
    },
    {
      "name": "Wait for articles to load",
      "action": "wait_for",
      "selector": ".article",
      "timeout": 10
    },
    {
      "name": "Extract article data",
      "action": "extract",
      "selector": ".article",
      "value": {
        "title": ".title",
        "description": ".description",
        "url": {
          "attribute": "href",
          "selector": "a"
        }
      }
    },
    {
      "name": "Save results to file",
      "action": "save",
      "value": "{{output_file}}"
    }
  ]
}
```

### Pagination Handling

This example demonstrates how to handle pagination when scraping data from multiple pages. The workflow navigates to the first page, extracts the data, clicks the "Next" button to go to the next page, and repeats the process until there are no more pages.

```json
{
  "name": "Pagination Handling",
  "version": "1.0.0",
  "description": "Scrape data from multiple pages with pagination",
  "variables": {
    "base_url": "https://example-news.com",
    "output_file": "articles.json",
    "max_pages": 10,
    "current_page": 1,
    "all_articles": []
  },
  "steps": [
    {
      "name": "Initialize articles array",
      "action": "set_variable",
      "selector": "all_articles",
      "value": []
    },
    {
      "name": "Loop through pages",
      "action": "loop",
      "value": {
        "type": "while",
        "condition": {
          "operator": "less_than_or_equals",
          "left": "{{current_page}}",
          "right": "{{max_pages}}"
        },
        "steps": [
          {
            "name": "Navigate to page",
            "action": "navigate",
            "value": "{{base_url}}?page={{current_page}}"
          },
          {
            "name": "Wait for articles to load",
            "action": "wait_for",
            "selector": ".article",
            "timeout": 10
          },
          {
            "name": "Extract article data",
            "action": "extract",
            "selector": ".article",
            "value": {
              "title": ".title",
              "description": ".description",
              "url": {
                "attribute": "href",
                "selector": "a"
              }
            }
          },
          {
            "name": "Add articles to collection",
            "action": "execute_script",
            "value": "all_articles = all_articles + extract_article_data; set_variable('all_articles', all_articles);"
          },
          {
            "name": "Check if next button exists",
            "action": "evaluate",
            "value": "document.querySelector('.next-button') !== null"
          },
          {
            "name": "Increment page counter",
            "action": "set_variable",
            "selector": "current_page",
            "value": "{{current_page + 1}}"
          },
          {
            "name": "Click next button if exists",
            "action": "if",
            "value": {
              "operator": "equals",
              "left": "{{evaluate}}",
              "right": true
            },
            "steps": [
              {
                "name": "Click next button",
                "action": "click",
                "selector": ".next-button"
              }
            ]
          }
        ]
      }
    },
    {
      "name": "Save results to file",
      "action": "save",
      "value": "{{output_file}}",
      "data": "{{all_articles}}"
    }
  ]
}
```

### JavaScript-Rendered Content

This example demonstrates how to scrape data from a web page that renders content using JavaScript. The workflow navigates to a page, waits for the JavaScript to execute and the content to load, and then extracts the data.

```json
{
  "name": "JavaScript-Rendered Content",
  "version": "1.0.0",
  "description": "Scrape data from a page with JavaScript-rendered content",
  "variables": {
    "url": "https://example-js-site.com",
    "output_file": "data.json"
  },
  "steps": [
    {
      "name": "Navigate to page",
      "action": "navigate",
      "value": "{{url}}"
    },
    {
      "name": "Wait for JavaScript to execute",
      "action": "wait",
      "value": 3
    },
    {
      "name": "Wait for content to load",
      "action": "wait_for",
      "selector": ".dynamic-content",
      "timeout": 15
    },
    {
      "name": "Extract data",
      "action": "extract",
      "selector": ".item",
      "value": {
        "name": ".name",
        "value": ".value",
        "description": ".description"
      }
    },
    {
      "name": "Save results to file",
      "action": "save",
      "value": "{{output_file}}"
    }
  ]
}
```

## Form Interaction Examples

### Simple Form Submission

This example demonstrates how to fill out and submit a simple form. The workflow navigates to a form page, fills in the form fields, and submits the form.

```json
{
  "name": "Simple Form Submission",
  "version": "1.0.0",
  "description": "Fill out and submit a simple form",
  "variables": {
    "url": "https://example.com/contact",
    "name": "John Doe",
    "email": "john.doe@example.com",
    "message": "This is a test message."
  },
  "steps": [
    {
      "name": "Navigate to form page",
      "action": "navigate",
      "value": "{{url}}"
    },
    {
      "name": "Wait for form to load",
      "action": "wait_for",
      "selector": "#contact-form",
      "timeout": 10
    },
    {
      "name": "Enter name",
      "action": "type",
      "selector": "#name",
      "value": "{{name}}"
    },
    {
      "name": "Enter email",
      "action": "type",
      "selector": "#email",
      "value": "{{email}}"
    },
    {
      "name": "Enter message",
      "action": "type",
      "selector": "#message",
      "value": "{{message}}"
    },
    {
      "name": "Submit form",
      "action": "click",
      "selector": "#submit-button"
    },
    {
      "name": "Wait for confirmation",
      "action": "wait_for",
      "selector": ".success-message",
      "timeout": 10
    }
  ]
}
```

### Multi-Step Form

This example demonstrates how to fill out a multi-step form. The workflow navigates to the first step of the form, fills in the fields, clicks the "Next" button to go to the next step, and repeats the process until the form is complete.

```json
{
  "name": "Multi-Step Form",
  "version": "1.0.0",
  "description": "Fill out a multi-step form",
  "variables": {
    "url": "https://example.com/register",
    "username": "johndoe",
    "password": "securepassword",
    "email": "john.doe@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "address": "123 Main St",
    "city": "Anytown",
    "state": "CA",
    "zip": "12345"
  },
  "steps": [
    {
      "name": "Navigate to registration page",
      "action": "navigate",
      "value": "{{url}}"
    },
    {
      "name": "Wait for form to load",
      "action": "wait_for",
      "selector": "#registration-form",
      "timeout": 10
    },
    {
      "name": "Step 1: Account Information",
      "action": "execute_script",
      "value": "console.log('Filling out Step 1: Account Information');"
    },
    {
      "name": "Enter username",
      "action": "type",
      "selector": "#username",
      "value": "{{username}}"
    },
    {
      "name": "Enter password",
      "action": "type",
      "selector": "#password",
      "value": "{{password}}"
    },
    {
      "name": "Enter email",
      "action": "type",
      "selector": "#email",
      "value": "{{email}}"
    },
    {
      "name": "Click next button",
      "action": "click",
      "selector": "#step1-next"
    },
    {
      "name": "Wait for step 2 to load",
      "action": "wait_for",
      "selector": "#step2",
      "timeout": 10
    },
    {
      "name": "Step 2: Personal Information",
      "action": "execute_script",
      "value": "console.log('Filling out Step 2: Personal Information');"
    },
    {
      "name": "Enter first name",
      "action": "type",
      "selector": "#first-name",
      "value": "{{first_name}}"
    },
    {
      "name": "Enter last name",
      "action": "type",
      "selector": "#last-name",
      "value": "{{last_name}}"
    },
    {
      "name": "Click next button",
      "action": "click",
      "selector": "#step2-next"
    },
    {
      "name": "Wait for step 3 to load",
      "action": "wait_for",
      "selector": "#step3",
      "timeout": 10
    },
    {
      "name": "Step 3: Address Information",
      "action": "execute_script",
      "value": "console.log('Filling out Step 3: Address Information');"
    },
    {
      "name": "Enter address",
      "action": "type",
      "selector": "#address",
      "value": "{{address}}"
    },
    {
      "name": "Enter city",
      "action": "type",
      "selector": "#city",
      "value": "{{city}}"
    },
    {
      "name": "Enter state",
      "action": "type",
      "selector": "#state",
      "value": "{{state}}"
    },
    {
      "name": "Enter zip code",
      "action": "type",
      "selector": "#zip",
      "value": "{{zip}}"
    },
    {
      "name": "Click submit button",
      "action": "click",
      "selector": "#submit-button"
    },
    {
      "name": "Wait for confirmation",
      "action": "wait_for",
      "selector": ".success-message",
      "timeout": 10
    }
  ]
}
```

### File Upload

This example demonstrates how to upload a file using a form. The workflow navigates to a form page with a file input field, selects a file to upload, and submits the form.

```json
{
  "name": "File Upload",
  "version": "1.0.0",
  "description": "Upload a file using a form",
  "variables": {
    "url": "https://example.com/upload",
    "file_path": "/path/to/file.txt",
    "description": "Test file upload"
  },
  "steps": [
    {
      "name": "Navigate to upload page",
      "action": "navigate",
      "value": "{{url}}"
    },
    {
      "name": "Wait for form to load",
      "action": "wait_for",
      "selector": "#upload-form",
      "timeout": 10
    },
    {
      "name": "Select file to upload",
      "action": "set_input_files",
      "selector": "#file-input",
      "value": "{{file_path}}"
    },
    {
      "name": "Enter description",
      "action": "type",
      "selector": "#description",
      "value": "{{description}}"
    },
    {
      "name": "Submit form",
      "action": "click",
      "selector": "#submit-button"
    },
    {
      "name": "Wait for confirmation",
      "action": "wait_for",
      "selector": ".success-message",
      "timeout": 30
    }
  ]
}
```

## Data Extraction Examples

### Table Data Extraction

This example demonstrates how to extract data from an HTML table. The workflow navigates to a page with a table, waits for the table to load, and extracts the data from all rows.

```json
{
  "name": "Table Data Extraction",
  "version": "1.0.0",
  "description": "Extract data from an HTML table",
  "variables": {
    "url": "https://example.com/data-table",
    "output_file": "table_data.json"
  },
  "steps": [
    {
      "name": "Navigate to page with table",
      "action": "navigate",
      "value": "{{url}}"
    },
    {
      "name": "Wait for table to load",
      "action": "wait_for",
      "selector": "#data-table",
      "timeout": 10
    },
    {
      "name": "Extract table headers",
      "action": "extract",
      "selector": "#data-table th",
      "value": {
        "header": "text"
      }
    },
    {
      "name": "Extract table rows",
      "action": "extract",
      "selector": "#data-table tbody tr",
      "value": {
        "cells": "td"
      }
    },
    {
      "name": "Process table data",
      "action": "execute_script",
      "value": "headers = extract_table_headers.map(h => h.header); rows = extract_table_rows.map(r => r.cells); table_data = rows.map(row => { obj = {}; headers.forEach((header, i) => { obj[header] = row[i] }); return obj; }); set_variable('processed_data', table_data);"
    },
    {
      "name": "Save results to file",
      "action": "save",
      "value": "{{output_file}}",
      "data": "{{processed_data}}"
    }
  ]
}
```

### Product Information Extraction

This example demonstrates how to extract product information from an e-commerce website. The workflow navigates to a product listing page, waits for the products to load, and extracts the name, price, and URL of each product.

```json
{
  "name": "Product Information Extraction",
  "version": "1.0.0",
  "description": "Extract product information from an e-commerce website",
  "variables": {
    "url": "https://example-store.com/products",
    "output_file": "products.json"
  },
  "steps": [
    {
      "name": "Navigate to product listing page",
      "action": "navigate",
      "value": "{{url}}"
    },
    {
      "name": "Wait for products to load",
      "action": "wait_for",
      "selector": ".product",
      "timeout": 10
    },
    {
      "name": "Extract product information",
      "action": "extract",
      "selector": ".product",
      "value": {
        "name": ".product-name",
        "price": ".product-price",
        "url": {
          "attribute": "href",
          "selector": ".product-link"
        },
        "image": {
          "attribute": "src",
          "selector": ".product-image img"
        }
      }
    },
    {
      "name": "Save results to file",
      "action": "save",
      "value": "{{output_file}}"
    }
  ]
}
```

### News Article Extraction

This example demonstrates how to extract news articles from a news website. The workflow navigates to a news page, waits for the articles to load, and extracts the title, summary, author, and publication date of each article.

```json
{
  "name": "News Article Extraction",
  "version": "1.0.0",
  "description": "Extract news articles from a news website",
  "variables": {
    "url": "https://example-news.com",
    "output_file": "articles.json"
  },
  "steps": [
    {
      "name": "Navigate to news page",
      "action": "navigate",
      "value": "{{url}}"
    },
    {
      "name": "Wait for articles to load",
      "action": "wait_for",
      "selector": ".article",
      "timeout": 10
    },
    {
      "name": "Extract article information",
      "action": "extract",
      "selector": ".article",
      "value": {
        "title": ".article-title",
        "summary": ".article-summary",
        "author": ".article-author",
        "date": ".article-date",
        "url": {
          "attribute": "href",
          "selector": ".article-link"
        }
      }
    },
    {
      "name": "Save results to file",
      "action": "save",
      "value": "{{output_file}}"
    }
  ]
}
```

## Authentication Examples

### Form-Based Login

This example demonstrates how to log in to a website using a form-based login. The workflow navigates to the login page, enters the username and password, and submits the form.

```json
{
  "name": "Form-Based Login",
  "version": "1.0.0",
  "description": "Log in to a website using a form-based login",
  "variables": {
    "login_url": "https://example.com/login",
    "username": "myuser",
    "password": "mypass"
  },
  "steps": [
    {
      "name": "Navigate to login page",
      "action": "navigate",
      "value": "{{login_url}}"
    },
    {
      "name": "Wait for login form to load",
      "action": "wait_for",
      "selector": "#login-form",
      "timeout": 10
    },
    {
      "name": "Enter username",
      "action": "type",
      "selector": "#username",
      "value": "{{username}}"
    },
    {
      "name": "Enter password",
      "action": "type",
      "selector": "#password",
      "value": "{{password}}"
    },
    {
      "name": "Submit login form",
      "action": "click",
      "selector": "#login-button"
    },
    {
      "name": "Wait for login to complete",
      "action": "wait_for",
      "selector": ".user-dashboard",
      "timeout": 10
    }
  ]
}
```

### OAuth Login

This example demonstrates how to log in to a website using OAuth. The workflow navigates to the login page, clicks the OAuth login button, switches to the OAuth provider's login page, enters the credentials, and submits the form.

```json
{
  "name": "OAuth Login",
  "version": "1.0.0",
  "description": "Log in to a website using OAuth",
  "variables": {
    "login_url": "https://example.com/login",
    "oauth_username": "myuser",
    "oauth_password": "mypass"
  },
  "steps": [
    {
      "name": "Navigate to login page",
      "action": "navigate",
      "value": "{{login_url}}"
    },
    {
      "name": "Wait for login form to load",
      "action": "wait_for",
      "selector": "#login-form",
      "timeout": 10
    },
    {
      "name": "Click OAuth login button",
      "action": "click",
      "selector": "#oauth-login"
    },
    {
      "name": "Wait for OAuth provider page to load",
      "action": "wait_for",
      "selector": "#oauth-form",
      "timeout": 10
    },
    {
      "name": "Enter OAuth username",
      "action": "type",
      "selector": "#oauth-username",
      "value": "{{oauth_username}}"
    },
    {
      "name": "Enter OAuth password",
      "action": "type",
      "selector": "#oauth-password",
      "value": "{{oauth_password}}"
    },
    {
      "name": "Submit OAuth form",
      "action": "click",
      "selector": "#oauth-submit"
    },
    {
      "name": "Wait for redirect back to original site",
      "action": "wait_for",
      "selector": ".user-dashboard",
      "timeout": 15
    }
  ]
}
```

### Session Management

This example demonstrates how to save and restore a browser session. The workflow logs in to a website, saves the session cookies, logs out, and then restores the session to log back in without entering credentials.

```json
{
  "name": "Session Management",
  "version": "1.0.0",
  "description": "Save and restore a browser session",
  "variables": {
    "login_url": "https://example.com/login",
    "username": "myuser",
    "password": "mypass",
    "session_file": "session.json"
  },
  "steps": [
    {
      "name": "Navigate to login page",
      "action": "navigate",
      "value": "{{login_url}}"
    },
    {
      "name": "Wait for login form to load",
      "action": "wait_for",
      "selector": "#login-form",
      "timeout": 10
    },
    {
      "name": "Enter username",
      "action": "type",
      "selector": "#username",
      "value": "{{username}}"
    },
    {
      "name": "Enter password",
      "action": "type",
      "selector": "#password",
      "value": "{{password}}"
    },
    {
      "name": "Submit login form",
      "action": "click",
      "selector": "#login-button"
    },
    {
      "name": "Wait for login to complete",
      "action": "wait_for",
      "selector": ".user-dashboard",
      "timeout": 10
    },
    {
      "name": "Save session cookies",
      "action": "execute_script",
      "value": "cookies = document.cookie.split(';').reduce((cookies, cookie) => { const [name, value] = cookie.trim().split('='); cookies[name] = value; return cookies; }, {}); set_variable('session_cookies', cookies);"
    },
    {
      "name": "Save session to file",
      "action": "save",
      "value": "{{session_file}}",
      "data": "{{session_cookies}}"
    },
    {
      "name": "Log out",
      "action": "click",
      "selector": "#logout-button"
    },
    {
      "name": "Wait for logout to complete",
      "action": "wait_for",
      "selector": "#login-form",
      "timeout": 10
    },
    {
      "name": "Load session from file",
      "action": "load",
      "value": "{{session_file}}"
    },
    {
      "name": "Restore session cookies",
      "action": "execute_script",
      "value": "Object.keys(load_session).forEach(name => { document.cookie = `${name}=${load_session[name]}`; });"
    },
    {
      "name": "Refresh page",
      "action": "navigate",
      "value": "{{login_url}}"
    },
    {
      "name": "Wait for login to complete",
      "action": "wait_for",
      "selector": ".user-dashboard",
      "timeout": 10
    }
  ]
}
```

## Testing Examples

### Form Validation Testing

This example demonstrates how to test form validation by submitting invalid data and checking for error messages. The workflow navigates to a form page, submits invalid data, and verifies that the appropriate error messages are displayed.

```json
{
  "name": "Form Validation Testing",
  "version": "1.0.0",
  "description": "Test form validation by submitting invalid data",
  "variables": {
    "url": "https://example.com/contact",
    "test_results": []
  },
  "steps": [
    {
      "name": "Initialize test results",
      "action": "set_variable",
      "selector": "test_results",
      "value": []
    },
    {
      "name": "Navigate to form page",
      "action": "navigate",
      "value": "{{url}}"
    },
    {
      "name": "Wait for form to load",
      "action": "wait_for",
      "selector": "#contact-form",
      "timeout": 10
    },
    {
      "name": "Test 1: Empty name field",
      "action": "execute_script",
      "value": "console.log('Running Test 1: Empty name field');"
    },
    {
      "name": "Clear name field",
      "action": "type",
      "selector": "#name",
      "value": ""
    },
    {
      "name": "Enter email",
      "action": "type",
      "selector": "#email",
      "value": "test@example.com"
    },
    {
      "name": "Enter message",
      "action": "type",
      "selector": "#message",
      "value": "This is a test message."
    },
    {
      "name": "Submit form",
      "action": "click",
      "selector": "#submit-button"
    },
    {
      "name": "Check for name error message",
      "action": "wait_for",
      "selector": "#name-error",
      "timeout": 5
    },
    {
      "name": "Get name error message",
      "action": "get_text",
      "selector": "#name-error"
    },
    {
      "name": "Add test result",
      "action": "execute_script",
      "value": "test_results.push({ test: 'Empty name field', expected: 'Name is required', actual: get_text_name_error, passed: get_text_name_error.includes('required') }); set_variable('test_results', test_results);"
    },
    {
      "name": "Test 2: Invalid email format",
      "action": "execute_script",
      "value": "console.log('Running Test 2: Invalid email format');"
    },
    {
      "name": "Enter name",
      "action": "type",
      "selector": "#name",
      "value": "John Doe"
    },
    {
      "name": "Enter invalid email",
      "action": "type",
      "selector": "#email",
      "value": "invalid-email"
    },
    {
      "name": "Submit form",
      "action": "click",
      "selector": "#submit-button"
    },
    {
      "name": "Check for email error message",
      "action": "wait_for",
      "selector": "#email-error",
      "timeout": 5
    },
    {
      "name": "Get email error message",
      "action": "get_text",
      "selector": "#email-error"
    },
    {
      "name": "Add test result",
      "action": "execute_script",
      "value": "test_results.push({ test: 'Invalid email format', expected: 'Valid email is required', actual: get_text_email_error, passed: get_text_email_error.includes('valid') }); set_variable('test_results', test_results);"
    },
    {
      "name": "Test 3: Empty message field",
      "action": "execute_script",
      "value": "console.log('Running Test 3: Empty message field');"
    },
    {
      "name": "Enter valid email",
      "action": "type",
      "selector": "#email",
      "value": "test@example.com"
    },
    {
      "name": "Clear message field",
      "action": "type",
      "selector": "#message",
      "value": ""
    },
    {
      "name": "Submit form",
      "action": "click",
      "selector": "#submit-button"
    },
    {
      "name": "Check for message error message",
      "action": "wait_for",
      "selector": "#message-error",
      "timeout": 5
    },
    {
      "name": "Get message error message",
      "action": "get_text",
      "selector": "#message-error"
    },
    {
      "name": "Add test result",
      "action": "execute_script",
      "value": "test_results.push({ test: 'Empty message field', expected: 'Message is required', actual: get_text_message_error, passed: get_text_message_error.includes('required') }); set_variable('test_results', test_results);"
    },
    {
      "name": "Save test results",
      "action": "save",
      "value": "form_validation_test_results.json",
      "data": "{{test_results}}"
    }
  ]
}
```

### Link Checking

This example demonstrates how to check for broken links on a web page. The workflow navigates to a page, extracts all the links, and checks each link to see if it returns a valid response.

```json
{
  "name": "Link Checking",
  "version": "1.0.0",
  "description": "Check for broken links on a web page",
  "variables": {
    "url": "https://example.com",
    "output_file": "link_check_results.json",
    "links": [],
    "results": []
  },
  "steps": [
    {
      "name": "Navigate to page",
      "action": "navigate",
      "value": "{{url}}"
    },
    {
      "name": "Wait for page to load",
      "action": "wait_for",
      "selector": "body",
      "timeout": 10
    },
    {
      "name": "Extract all links",
      "action": "extract",
      "selector": "a[href]",
      "value": {
        "url": {
          "attribute": "href"
        },
        "text": "text"
      }
    },
    {
      "name": "Filter and process links",
      "action": "execute_script",
      "value": "links = extract_all_links.filter(link => link.url && !link.url.startsWith('#') && !link.url.startsWith('javascript:')).map(link => ({ url: new URL(link.url, window.location.href).href, text: link.text })); set_variable('processed_links', links);"
    },
    {
      "name": "Initialize results",
      "action": "set_variable",
      "selector": "results",
      "value": []
    },
    {
      "name": "Check each link",
      "action": "loop",
      "value": {
        "type": "for_each",
        "items": "{{processed_links}}",
        "variable": "link",
        "steps": [
          {
            "name": "Check link status",
            "action": "execute_script",
            "value": "fetch('{{link.url}}', { method: 'HEAD' }).then(response => { results.push({ url: '{{link.url}}', text: '{{link.text}}', status: response.status, ok: response.ok }); set_variable('results', results); }).catch(error => { results.push({ url: '{{link.url}}', text: '{{link.text}}', status: 'Error', ok: false, error: error.message }); set_variable('results', results); });"
          }
        ]
      }
    },
    {
      "name": "Wait for all link checks to complete",
      "action": "wait",
      "value": 5
    },
    {
      "name": "Save results",
      "action": "save",
      "value": "{{output_file}}",
      "data": "{{results}}"
    }
  ]
}
```

### Performance Testing

This example demonstrates how to measure the performance of a web page. The workflow navigates to a page, measures the page load time, and saves the results.

```json
{
  "name": "Performance Testing",
  "version": "1.0.0",
  "description": "Measure the performance of a web page",
  "variables": {
    "url": "https://example.com",
    "output_file": "performance_results.json",
    "iterations": 5,
    "results": []
  },
  "steps": [
    {
      "name": "Initialize results",
      "action": "set_variable",
      "selector": "results",
      "value": []
    },
    {
      "name": "Run performance test",
      "action": "loop",
      "value": {
        "type": "for",
        "start": 1,
        "end": "{{iterations}}",
        "variable": "i",
        "steps": [
          {
            "name": "Start timer",
            "action": "execute_script",
            "value": "startTime = performance.now(); set_variable('start_time', startTime);"
          },
          {
            "name": "Navigate to page",
            "action": "navigate",
            "value": "{{url}}"
          },
          {
            "name": "Wait for page to load",
            "action": "wait_for",
            "selector": "body",
            "timeout": 30
          },
            {
              "name": "Stop timer",
              "action": "execute_script",
              "value": "endTime = performance.now(); loadTime = endTime - start_time; results.push({ iteration: {{i}}, url: '{{url}}', load_time_ms: loadTime }); set_variable('results', results);"
            }
          ]
        }
      },
      {
        "name": "Calculate average load time",
        "action": "execute_script",
        "value": "averageLoadTime = results.reduce((sum, result) => sum + result.load_time_ms, 0) / results.length; minLoadTime = Math.min(...results.map(r => r.load_time_ms)); maxLoadTime = Math.max(...results.map(r => r.load_time_ms)); set_variable('average_load_time', averageLoadTime); set_variable('min_load_time', minLoadTime); set_variable('max_load_time', maxLoadTime);"
      },
      {
        "name": "Create summary",
        "action": "execute_script",
        "value": "summary = { url: '{{url}}', iterations: {{iterations}}, average_load_time_ms: average_load_time, min_load_time_ms: min_load_time, max_load_time_ms: max_loadTime, results: results }; set_variable('summary', summary);"
      },
      {
        "name": "Save results",
        "action": "save",
        "value": "{{output_file}}",
        "data": "{{summary}}"
      }
    ]
  }
```

## Advanced Examples

### Conditional Workflows

This example demonstrates how to use conditional logic in a workflow. The workflow navigates to a page, checks if a specific element exists, and performs different actions based on the result.

```json
{
  "name": "Conditional Workflows",
  "version": "1.0.0",
  "description": "Use conditional logic in a workflow",
  "variables": {
    "url": "https://example.com",
    "output_file": "conditional_results.json"
  },
  "steps": [
    {
      "name": "Navigate to page",
      "action": "navigate",
      "value": "{{url}}"
    },
    {
      "name": "Wait for page to load",
      "action": "wait_for",
      "selector": "body",
      "timeout": 10
    },
    {
      "name": "Check if premium content is available",
      "action": "evaluate",
      "value": "document.querySelector('.premium-content') !== null"
    },
    {
      "name": "Process based on content availability",
      "action": "if",
      "value": {
        "operator": "equals",
        "left": "{{evaluate}}",
        "right": true
      },
      "steps": [
        {
          "name": "Extract premium content",
          "action": "extract",
          "selector": ".premium-content",
          "value": {
            "title": ".title",
            "content": ".content"
          }
        },
        {
          "name": "Set content type",
          "action": "set_variable",
          "selector": "content_type",
          "value": "premium"
        }
      ],
      "else_steps": [
        {
          "name": "Extract standard content",
          "action": "extract",
          "selector": ".standard-content",
          "value": {
            "title": ".title",
            "content": ".content"
          }
        },
        {
          "name": "Set content type",
          "action": "set_variable",
          "selector": "content_type",
          "value": "standard"
        }
      ]
    },
    {
      "name": "Create result object",
      "action": "execute_script",
      "value": "result = { content_type: content_type, data: content_type === 'premium' ? extract_premium_content : extract_standard_content }; set_variable('result', result);"
    },
    {
      "name": "Save results",
      "action": "save",
      "value": "{{output_file}}",
      "data": "{{result}}"
    }
  ]
}
```

### Loop-Based Workflows

This example demonstrates how to use loops in a workflow. The workflow navigates to a page with a list of items, loops through each item, and performs actions on each item.

```json
{
  "name": "Loop-Based Workflows",
  "version": "1.0.0",
  "description": "Use loops in a workflow",
  "variables": {
    "url": "https://example.com/items",
    "output_file": "loop_results.json",
    "results": []
  },
  "steps": [
    {
      "name": "Navigate to page",
      "action": "navigate",
      "value": "{{url}}"
    },
    {
      "name": "Wait for page to load",
      "action": "wait_for",
      "selector": ".item-list",
      "timeout": 10
    },
    {
      "name": "Extract items",
      "action": "extract",
      "selector": ".item",
      "value": {
        "id": {
          "attribute": "data-id"
        },
        "name": ".name",
        "price": ".price"
      }
    },
    {
      "name": "Initialize results",
      "action": "set_variable",
      "selector": "results",
      "value": []
    },
    {
      "name": "Process each item",
      "action": "loop",
      "value": {
        "type": "for_each",
        "items": "{{extract_items}}",
        "variable": "item",
        "steps": [
          {
            "name": "Navigate to item details page",
            "action": "navigate",
            "value": "{{url}}/{{item.id}}"
          },
          {
            "name": "Wait for item details to load",
            "action": "wait_for",
            "selector": ".item-details",
            "timeout": 10
          },
          {
            "name": "Extract item details",
            "action": "extract",
            "selector": ".item-details",
            "value": {
              "description": ".description",
              "availability": ".availability",
              "rating": ".rating"
            }
          },
            {
              "name": "Create item result",
              "action": "execute_script",
              "value": "itemResult = { id: '{{item.id}}', name: '{{item.name}}', price: '{{item.price}}', details: extract_item_details }; results.push(itemResult); set_variable('results', results);"
            }
          ]
        }
      },
      {
        "name": "Save results",
        "action": "save",
        "value": "{{output_file}}",
        "data": "{{results}}"
      }
    ]
  }
```

### Error Handling and Recovery

This example demonstrates how to handle errors and recover from failures in a workflow. The workflow attempts to perform an action, and if it fails, it retries a specified number of times before giving up.

```json
{
  "name": "Error Handling and Recovery",
  "version": "1.0.0",
  "description": "Handle errors and recover from failures in a workflow",
  "variables": {
    "url": "https://example.com",
    "output_file": "error_handling_results.json",
    "max_retries": 3,
    "retry_delay": 2,
    "retry_count": 0,
    "results": []
  },
  "steps": [
    {
      "name": "Navigate to page",
      "action": "navigate",
      "value": "{{url}}"
    },
    {
      "name": "Wait for page to load",
      "action": "wait_for",
      "selector": "body",
      "timeout": 10
    },
    {
      "name": "Initialize results",
      "action": "set_variable",
      "selector": "results",
      "value": []
    },
    {
      "name": "Try to click a button that might not exist",
      "action": "click",
      "selector": "#non-existent-button",
      "on_error": "retry",
      "retry": {
        "max_attempts": "{{max_retries}}",
        "delay": "{{retry_delay}}"
      }
    },
    {
      "name": "Check if button was clicked",
      "action": "evaluate",
      "value": "document.querySelector('.success-message') !== null"
    },
    {
      "name": "Process result",
      "action": "if",
      "value": {
        "operator": "equals",
        "left": "{{evaluate}}",
        "right": true
      },
      "steps": [
        {
          "name": "Add success result",
          "action": "execute_script",
          "value": "results.push({ action: 'Click button', status: 'success' }); set_variable('results', results);"
        }
      ],
      "else_steps": [
        {
          "name": "Add failure result",
          "action": "execute_script",
          "value": "results.push({ action: 'Click button', status: 'failed', retries: {{max_retries}} }); set_variable('results', results);"
        }
      ]
    },
    {
      "name": "Try to extract data from an element that might not exist",
      "action": "extract",
      "selector": ".non-existent-element",
      "value": {
        "data": "text"
      },
      "on_error": "continue"
    },
    {
      "name": "Check if data was extracted",
      "action": "evaluate",
      "value": "typeof extract_data !== 'undefined' && extract_data !== null"
    },
    {
      "name": "Process result",
      "action": "if",
      "value": {
        "operator": "equals",
        "left": "{{evaluate}}",
        "right": true
      },
      "steps": [
        {
          "name": "Add success result",
          "action": "execute_script",
          "value": "results.push({ action: 'Extract data', status: 'success', data: extract_data }); set_variable('results', results);"
        }
      ],
      "else_steps": [
        {
          "name": "Add failure result",
          "action": "execute_script",
          "value": "results.push({ action: 'Extract data', status: 'failed', error: 'Element not found' }); set_variable('results', results);"
        }
      ]
    },
    {
      "name": "Save results",
      "action": "save",
      "value": "{{output_file}}",
      "data": "{{results}}"
    }
  ]
}
```

## Conclusion

These examples demonstrate the power and flexibility of Automata for automating a wide range of web tasks. By combining different actions, conditions, and loops, you can create complex workflows that can handle almost any automation scenario.

Remember to customize these examples for your specific needs, and always test your workflows thoroughly before using them in production.
