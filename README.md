# Robot Framework MCP Server

A Model Context Protocol (MCP) server for Robot Framework test automation 

## Features

- 🤖 Generate Robot Framework test cases with SeleniumLibrary
- 📄 Create page object models for web testing
- ⚡ Advanced Selenium keywords for common web interactions
- 📸 Screenshot capabilities and performance monitoring
- 🎯 Input validation and configurable selectors
- 📊 Performance monitoring and metrics collection
- 🔄 Data-driven testing templates
- 🌐 API integration testing capabilities

## Prerequisites

- **Python 3.10 or higher**
- **Node.js 14.0 or higher** (for npx method)
- **UV** (for UV method - optional but recommended)
- Git (for installation from repository)

## Installation & Usage

### Method 1: Using npx (Node.js Package Manager)

Add to your MCP client configuration (e.g., `mcp.json` or Claude Desktop settings):

```json
{
  "servers": {
    "robotframework-mcp": {
      "command": "npx",
      "args": [
        "-y",
        "git+https://github.com/sourcefuse/robotframework-MCP.git"
      ],
      "type": "stdio"
    }
  }
}
```

### Method 2: Using UV (Recommended - Faster & More Reliable)

First install UV:
```bash
# Install UV (choose one method)
curl -LsSf https://astral.sh/uv/install.sh | sh  # Unix/macOS
# OR
pip install uv  # Any platform
# OR on Windows PowerShell (as Administrator)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Then add to your MCP configuration:

```json
{
  "servers": {
    "robotframework-mcp": {
      "command": "uv",
      "args": [
        "run",
        "--with",
        "git+https://github.com/sourcefuse/robotframework-MCP.git",
        "python",
        "-c",
        "import mcp_server; mcp_server.main()"
      ],
      "type": "stdio"
    }
  }
}
```

## Available Tools

The MCP server provides the following comprehensive tools for Robot Framework test automation:

### 🔧 Core Test Generation
- **`create_login_test_case(url, username, password, template_type="appLocator")`** - Generate validated login test with configurable selectors
- **`create_page_object_login(template_type="appLocator")`** - Generate login page object model with validation
- **`create_data_driven_test(test_data_file="test_data.csv")`** - Generate data-driven test templates
- **`create_api_integration_test(base_url, endpoint, method="GET")`** - Generate API + UI integration tests

### ⚡ Advanced Keywords
- **`create_advanced_selenium_keywords()`** - Generate advanced SeleniumLibrary keywords (dropdowns, checkboxes, file uploads, alerts, etc.)
- **`create_extended_selenium_keywords()`** - Generate extended keywords with screenshots, performance monitoring, and window management

### 📊 Performance & Monitoring
- **`create_performance_monitoring_test()`** - Generate comprehensive performance testing with metrics collection

### 🔍 Validation & Syntax
- **`validate_robot_framework_syntax(robot_code)`** - Validate Robot Framework syntax and provide improvement suggestions

### 📋 Template Options

The server supports multiple selector templates for different applications:

- **`appLocator`** (default) - For web apps
- **`generic`** - Generic web application selectors
- **`bootstrap`** - Bootstrap-based applications

### 🎯 Input Validation

All tools include comprehensive input validation:
- URL validation with protocol checking
- Credential sanitization and length limits
- Selector format validation
- Safe variable substitution in templates

## Credits

** Developer & Creator:** [Meenu Rani](https://github.com/meenurani1)
- 🚀 Initial concept and architecture design
- 💻 Core implementation and development
- 📚 Documentation and examples
- 🔧 Maintenance and feature development

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

Copyright (c) 2025 Sourcefuse
