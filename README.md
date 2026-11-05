# Robot Framework MCP Server

A Model Context Protocol (MCP) server for Robot Framework test automation, with two interchangeable browser-automation backends: **SeleniumLibrary** and **Playwright (Robot Framework Browser library)**.

<a href="https://glama.ai/mcp/servers/@sourcefuse/robotframework-mcp">
  <img width="380" height="200" src="https://glama.ai/mcp/servers/@sourcefuse/robotframework-mcp/badge" alt="Robot Framework Server MCP server" />
</a>

## 🎭 Playwright / Browser Library Support

Alongside the original SeleniumLibrary tooling, this server now ships a **Playwright-powered backend** using Robot Framework's [Browser library](https://robotframework-browser.org/) — the modern, actively-developed, high-demand choice for browser automation (auto-wait, multi-browser support for Chromium/Firefox/WebKit, faster and more reliable than Selenium for most workflows).

Switch backends with a single flag — no separate install to manage, it's bundled in this package:

```bash
npx -y robotframework-mcp-server --library=browser    # Playwright / Browser library
npx -y robotframework-mcp-server --library=selenium   # SeleniumLibrary (default)
```

First run with `--library=browser` bootstraps its own environment automatically (installs deps + `rfbrowser init`, one-time, a couple of minutes). Because that can exceed an MCP client's startup timeout, it's best to run the setup once from a terminal first:

```bash
npx -y robotframework-mcp-server --library=browser --setup   # prepare the backend, then exit
```

See "Browser Library (Playwright) Tools" below for the full tool list.

## Features

- 🎭 **Playwright / Browser library backend** — modern, auto-waiting, multi-browser (Chromium/Firefox/WebKit) automation, selectable with `--library=browser`
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

This server has two interchangeable backends, selected with `--library`:

- **`selenium`** (default) — SeleniumLibrary-based code generation + live browser control tools.
- **`browser`** — Playwright-based Robot Framework [Browser library](https://robotframework-browser.org/) tools. Self-contained: on first run it creates its own `.venv` under `browser/` and runs `rfbrowser init` automatically (downloads Playwright browsers, one-time, a couple of minutes).

> **`--library` support by install method:** works with **Method 1 (npx)**, **Method 2 (PyPI, with the `[browser]` extra)** and the Node-wrapper variant of **Method 4**. **Method 3 (UV)** and the plain `python mcp_server.py` variant of Method 4 run the Selenium backend only.

### Method 1: Using npx (Node.js Package Manager)

Add to your MCP client configuration (e.g., `mcp.json`) in your **VS code or VS code insider**:

```json
{
  "servers": {
    "robotframework-mcp": {
      "command": "npx",
      "args": [
        "-y",
        "robotframework-mcp-server",
        "--project-dir=/path/to/your/project",  //Optional- If you want to run the mcp for local virtual environment or specific project only
        "--library=browser"  //Optional- "selenium" (default) or "browser" (Playwright)
      ],
      "type": "stdio"
    }
  }
}
```
### Method 2: Install from PyPI

```bash
# SeleniumLibrary backend (default)
pip3 install robotframework-mcp
robotframework-mcp

# Playwright / Browser library backend
pip3 install "robotframework-mcp[browser]"
robotframework-mcp --library=browser --setup   # one-time: downloads Playwright browsers
robotframework-mcp --library=browser
```

`pip3 install robotframework-mcp` installs only the Selenium dependencies. The `[browser]` extra adds the Playwright-based Browser library. If you installed without the extra, `robotframework-mcp --library=browser --setup` installs the Browser library into the same environment for you, then runs `rfbrowser init`. Run `--setup` once from a terminal before adding the server to your MCP client, because the first-time download can exceed the client's startup timeout.

**For MCP Clients (VS code or VS code inside, etc.):**

```json
{
  "mcpServers": {
    "robotframework-mcp": {
      "command": "robotframework-mcp",
      "args": ["--library=browser"],  //Optional- "selenium" (default) or "browser" (needs the [browser] extra)
      "type": "stdio"
    }
  }
}
```

### Method 3: Using UV

> Selenium backend only — `--library` is not supported here.

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

# Run the MCP server directly (Selenium backend only)
python mcp_server.py
```

**For MCP Clients (VS Code, Claude Desktop, etc.) — Selenium backend only, `--library` not supported:**

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

Or using the Node.js wrapper from cloned repo — this variant supports `--library=selenium|browser`:

```json
{
  "servers": {
    "robotframework-mcp": {
      "command": "node",
      "args": [
        "/path/to/cloned/robotframework-MCP/bin/robotframework-mcp.js",
        "--project-dir=/path/to/your/project",
        "--library=browser"
      ],
      "type": "stdio"
    }
  }
}
```

## Available Tools

The MCP server provides the following comprehensive tools for Robot Framework test automation:

### 🎭 Browser Library (Playwright) Tools — `--library=browser`

Available only when the server is started with `--library=browser`. Each tool is a thin wrapper around a real Robot Framework [Browser library](https://robotframework-browser.org/) keyword, run against a single persistent session.

| Tool | Description |
|---|---|
| **`open_browser(url, browser="chromium", headless=True)`** | Launch a browser (`chromium`, `firefox`, or `webkit`) |
| **`new_page(url)`** / **`close_page()`** / **`close_browser()`** | Manage pages and the browser session |
| **`session_status()`** | Real current state: browser open?, open pages, active URL and title |
| **`reset_session(url=None)`** | Close everything and optionally start a fresh browser on `url` — recover from an unreliable state |
| **`go_to(url, timeout_s=None)`**, **`get_url()`**, **`get_title()`** | Navigation |
| **`click(selector)`**, **`fill_text`**, **`type_text`**, **`clear_text`**, **`press_keys`** | Interactions |
| **`check_checkbox`** / **`uncheck_checkbox`** / **`select_options_by`** | Form controls |
| **`get_text`**, **`get_attribute`**, **`get_element_count`** | Reading page content |
| **`wait_for_elements_state(selector, state="visible")`** | Wait for an element state |
| **`take_screenshot`**, **`evaluate_javascript`** | Screenshots & JS |
| **`run_keyword(name, args)`** | Escape hatch — run any Browser-library keyword by name |
| **`export_robot_test(test_name, path=None, overwrite=False)`** | Export the steps that ran and passed as a draft `.robot` test for review |
| **`clear_recording()`** | Drop the steps recorded so far, so the export starts from now |

**Turning an exploration into a reviewable test.** While the assistant drives the browser, every keyword that passes is recorded exactly as it ran. `export_robot_test` writes those steps into a draft `.robot` file. Failed attempts are left out, and values the assistant only read (`get_text`, `get_url`, …) appear as commented assertions holding the value it saw, so a reviewer chooses which checks to keep:

```robotframework
*** Test Cases ***
Login Works
    New Browser    browser=chromium    headless=True
    New Page    https://example.com/login
    Fill Text    id=user    meenu
    Fill Text    id=pw    ${PASSWORD}    # typed values are recorded as-is: replace secrets
    Click    id=go
    # Get Text    id=h    ==    Welcome meenu
```

`reset_session` also clears the recording. Use `reset_session(url)` before the clean run you want to keep, so the test starts from a fresh browser.

**When a step fails** (navigation timeout, missing element, bad argument…), the tool returns a proper MCP error (`isError: true`) containing Browser library's real message **plus a snapshot of the page state after the failure**, so the model re-plans from where the browser actually is instead of assuming the step worked:

```text
'Go To' failed: TimeoutError: page.goto: Timeout 3000ms exceeded.

Page state after the failure (the page may be partially loaded or unchanged -- verify before continuing):
- url: https://example.com/
- title: Loading http://127.0.0.1:50315/
- open pages: 1
```

If the server itself stops waiting on a keyword, the error says the state is **unknown** (the keyword may still be running) and points the model to `session_status` / `reset_session`.

The following tools are available with the default `--library=selenium` backend:

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

Copyright (c) 2026 Sourcefuse
