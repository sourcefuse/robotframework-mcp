# Robot Framework MCP Server

A Model Context Protocol (MCP) server for Robot Framework test automation with custom features

<a href="https://glama.ai/mcp/servers/@sourcefuse/robotframework-mcp">
  <img width="380" height="200" src="https://glama.ai/mcp/servers/@sourcefuse/robotframework-mcp/badge" alt="Robot Framework Server MCP server" />
</a>

## Features

- 🤖 Generate Robot Framework test cases with SeleniumLibrary
- 📄 Create page object models for web testing
- ⚡ Advanced Selenium keywords for common web interactions
- 📸 Screenshot capabilities and performance monitoring
- 🎯 Input validation and configurable selectors
- 📊 Performance monitoring and metrics collection
- 🔄 Data-driven testing templates
- 🌐 API integration testing capabilities
- 🖥️ Live browser control — launch, click, type, screenshot without writing `.robot` files
- 🚀 CI/CD pipeline generation for GitHub Actions

## Quick Demo Video


https://github.com/user-attachments/assets/47ef8f7b-e3f5-413c-b09f-40168a9d4b44


## Prerequisites

- **Python 3.10 or higher**
- **Node.js 14.0 or higher** (for npx method)
- **UV** (for UV method - optional but recommended)
- Git (for installation from repository)

## Installation & Usage

### Method 1: Using npx (Node.js Package Manager)

Add to your MCP client configuration (e.g., `mcp.json`) in your **VS code or VS code insider**:

```json
{
  "servers": {
    "robotframework-mcp": {
      "command": "npx",
      "args": [
        "-y",
        "git+https://github.com/sourcefuse/robotframework-MCP.git",
        "--project-dir=/path/to/your/project"  //Optional- If you want to run the mcp for local virtual environment or specific project only
      ],
      "type": "stdio"
    }
  }
}
```
### Method 2: Install from PyPI 

```bash
# Install the package
pip3 install robotframework-mcp

# Run the MCP server
robotframework-mcp
```

**For MCP Clients (VS code or VS code inside, etc.):**

```json
{
  "mcpServers": {
    "robotframework-mcp": {
      "command": "robotframework-mcp",
      "type": "stdio"
    }
  }
}
```

### Method 3: Using UV 

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

### Method 4: Clone Repository (Development/Local Setup)

For development or when you want to modify the source code:

```bash
# Clone the repository
git clone https://github.com/sourcefuse/robotframework-MCP.git
cd robotframework-MCP

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the MCP server directly
python mcp_server.py
```

**For MCP Clients (VS Code, Claude Desktop, etc.):**

```json
{
  "servers": {
    "robotframework-mcp": {
      "command": "python",
      "args": ["/path/to/cloned/robotframework-MCP/mcp_server.py"],
      "type": "stdio"
    }
  }
}
```

Or using the Node.js wrapper from cloned repo:

```json
{
  "servers": {
    "robotframework-mcp": {
      "command": "node",
      "args": [
        "/path/to/cloned/robotframework-MCP/bin/robotframework-mcp.js",
        "--project-dir=/path/to/your/project"
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

### 🖥️ Live Browser Control

Drive a real browser directly — no `.robot` file needed. All tools share a persistent session and support Robot Framework-style selector prefixes (`id=`, `css=`, `xpath=`, `name=`, `class=`, `tag=`, `link=`, `partial_link=`).

| Tool | Description |
|---|---|
| **`browser_launch(url, browser="Chrome", headless=False)`** | Open Chrome or Firefox and navigate to a URL |
| **`browser_navigate(url)`** | Go to a new URL in the active session |
| **`browser_click(selector, timeout=10)`** | Click an element, waits until it is clickable |
| **`browser_send_keys(selector, text, clear_first=True, timeout=10)`** | Type into an input field |
| **`browser_get_text(selector, timeout=10)`** | Read visible text from an element |
| **`browser_wait_for_element(selector, state="visible", timeout=10)`** | Wait for `visible`, `present`, `clickable`, or `hidden` |
| **`browser_screenshot(filename="")`** | Save a PNG screenshot, returns the file path |
| **`browser_close()`** | Quit the browser and clean up the session |

**Example — AI-driven login flow:**
```python
browser_launch("https://example.com")
browser_send_keys("id=username", "admin")
browser_send_keys("id=password", "secret")
browser_click("css=button[type='submit']")
browser_screenshot("results/after_login.png")
browser_close()
```

> **Note:** ChromeDriver must match your installed Chrome version. Update with `brew upgrade chromedriver` (macOS) or download from [googlechromelabs.github.io/chrome-for-testing](https://googlechromelabs.github.io/chrome-for-testing/).

### 🚀 CI/CD Pipeline Generation

- **`create_cicd_pipeline(project_name, python_version, test_directory, trigger_branches, schedule, output_dir, requirements_file)`** - Generate a GitHub Actions workflow file ready to drop into `.github/workflows/`

The generated workflow:
- Triggers on push and pull requests to specified branches
- Supports optional cron schedule (e.g. `"0 9 * * 1-5"` for weekdays at 09:00 UTC)
- Auto-detects the Python version from the current environment (can be overridden)
- Sets up Chrome in headless mode on the runner
- Installs from `requirements.txt` if present, falls back to core packages
- Uploads the full `results/` folder as a build artifact (30-day retention)
- Parses `output.xml` and reports pass/fail counts; fails the job if any test fails

**Example:**
```python
create_cicd_pipeline(
    project_name="my-rf-tests",
    trigger_branches="main, develop",
    schedule="0 9 * * 1-5",   # weekdays 09:00 UTC
    test_directory="tests/",
)
```

Save the output to `.github/workflows/robot-tests.yml` in your repository.

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


### 🤝 Contributing
Contributions are welcome!
To contribute:
 - Fork the repository
 - Create a new branch
 - Submit a pull request with a detailed description

### 📬 Contact
 Name: Meenu Rani
 Email: meenu.rani@sourcefuse.com
 GitHub: meenurani1

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

Copyright (c) 2025 Sourcefuse
