import re
from string import Template
from urllib.parse import urlparse
from mcp.server.fastmcp import FastMCP

# Create an enhanced MCP server with validation and configurable selectors
mcp = FastMCP("Robot framework MCP Server")

class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass

class InputValidator:
    """Centralized input validation for MCP tools"""
    
    @staticmethod
    def validate_url(url: str) -> str:
        """Validate and return sanitized URL"""
        if not url or not url.strip():
            raise ValidationError("URL cannot be empty")
        
        url = url.strip()
        try:
            result = urlparse(url)
            if not all([result.scheme, result.netloc]):
                raise ValidationError(f"Invalid URL format: {url}")
            
            if result.scheme not in ['http', 'https']:
                raise ValidationError(f"URL must use http or https protocol: {url}")
                
            return url
        except Exception as e:
            raise ValidationError(f"URL validation failed: {str(e)}")

    @staticmethod
    def validate_credentials(username: str, password: str) -> tuple:
        """Validate and return sanitized credentials"""
        if not username or not username.strip():
            raise ValidationError("Username cannot be empty")
        
        if not password or not password.strip():
            raise ValidationError("Password cannot be empty")
        
        username = username.strip()
        password = password.strip()
        
        if len(username) > 100:
            raise ValidationError("Username too long (max 100 characters)")
        
        if len(password) > 100:
            raise ValidationError("Password too long (max 100 characters)")
        
        # Check for dangerous characters
        dangerous_chars = ['<', '>', '"', "'", '&', '\n', '\r', '\t']
        for char in dangerous_chars:
            if char in username or char in password:
                raise ValidationError(f"Credentials contain invalid character: {char}")
        
        return username, password
    
    @staticmethod
    def validate_selector(selector: str) -> str:
        """Validate and return sanitized selector"""
        if not selector or not selector.strip():
            raise ValidationError("Selector cannot be empty")
        
        selector = selector.strip()
        
        # Basic validation patterns
        valid_patterns = [
            r'^id=.+',           # id=element-id
            r'^name=.+',         # name=element-name
            r'^class=.+',        # class=element-class
            r'^css=.+',          # css=.class-name
            r'^xpath=.+',        # xpath=//div[@id='test']
            r'^tag=.+',          # tag=input
            r'^\w+',             # plain CSS selector
        ]
        
        if not any(re.match(pattern, selector) for pattern in valid_patterns):
            raise ValidationError(f"Invalid selector format: {selector}")
        
        return selector

# Predefined selector configurations for different applications
SELECTOR_CONFIGS = {
    "appLocator": {
        "username_field": "id=user-name",
        "password_field": "id=password",
        "login_button": "id=login-button",
        "success_indicator": "xpath=//span[@class='title']",
        "error_message": "xpath=//h3[@data-test='error']",
        "logout_button": "id=logout_sidebar_link"
    },
    "generic": {
        "username_field": "id=username",
        "password_field": "id=password",
        "login_button": "css=button[type='submit']",
        "success_indicator": "css=.dashboard",
        "error_message": "css=.error",
        "logout_button": "css=.logout"
    },
    "bootstrap": {
        "username_field": "css=input[name='username']",
        "password_field": "css=input[name='password']",
        "login_button": "css=.btn-primary",
        "success_indicator": "css=.navbar-brand",
        "error_message": "css=.alert-danger",
        "logout_button": "css=.btn-outline-secondary"
    }
}

@mcp.tool()
def create_login_test_case(url: str, username: str, password: str, template_type: str = "appLocator") -> str:
    """Generate Robot Framework test case code for login functionality. Returns the complete .robot file content as text - does not execute the test."""
    try:
        # Validate inputs
        validated_url = InputValidator.validate_url(url)
        validated_username, validated_password = InputValidator.validate_credentials(username, password)
        
        # Get selector configuration
        selectors = SELECTOR_CONFIGS.get(template_type.lower(), SELECTOR_CONFIGS["generic"])
        
        # Use Template for safe variable substitution and correct Robot Framework syntax
        template = Template("""*** Settings ***
Library    SeleniumLibrary

*** Variables ***
$${URL}           $url
$${USERNAME}      $username
$${PASSWORD}      $password
$${BROWSER}       Chrome

# Selector Variables
$${USERNAME_FIELD}        $username_field
$${PASSWORD_FIELD}        $password_field
$${LOGIN_BUTTON}          $login_button
$${SUCCESS_INDICATOR}     $success_indicator

*** Test Cases ***
Login Test
    [Documentation]    Test login functionality for $template_type
    [Tags]    smoke    login    $template_type
    Open Browser    $${URL}    $${BROWSER}
    Maximize Browser Window
    Input Text    $${USERNAME_FIELD}    $${USERNAME}
    Input Text    $${PASSWORD_FIELD}    $${PASSWORD}
    Click Button    $${LOGIN_BUTTON}
    Wait Until Page Contains Element    $${SUCCESS_INDICATOR}    10s
    Element Text Should Be    $${SUCCESS_INDICATOR}    Products
    [Teardown]    Close Browser
""")
        
        return template.substitute(
            url=validated_url,
            username=validated_username,
            password=validated_password,
            template_type=template_type,
            username_field=selectors["username_field"],
            password_field=selectors["password_field"],
            login_button=selectors["login_button"],
            success_indicator=selectors["success_indicator"]
        )
        
    except ValidationError as e:
        return f"# VALIDATION ERROR: {str(e)}\n# Please correct the input and try again."
    except Exception as e:
        return f"# UNEXPECTED ERROR: {str(e)}\n# Please contact support."

@mcp.tool()
def create_page_object_login(template_type: str = "appLocator") -> str:
    """Generate Robot Framework page object model code for login page. Returns .robot file content as text - does not execute."""
    try:
        # Get selector configuration
        selectors = SELECTOR_CONFIGS.get(template_type.lower(), SELECTOR_CONFIGS["generic"])
        
        # Use Template for safe variable substitution and correct Robot Framework syntax
        template = Template("""*** Settings ***
Library    SeleniumLibrary

*** Variables ***
# $template_type Application Selectors
$${LOGIN_USERNAME_FIELD}    $username_field
$${LOGIN_PASSWORD_FIELD}    $password_field
$${LOGIN_BUTTON}           $login_button
$${LOGIN_ERROR_MESSAGE}    $error_message

*** Keywords ***
Input Username
    [Arguments]    $${username}
    [Documentation]    Enter username in the username field
    Wait Until Element Is Visible    $${LOGIN_USERNAME_FIELD}
    Clear Element Text    $${LOGIN_USERNAME_FIELD}
    Input Text    $${LOGIN_USERNAME_FIELD}    $${username}

Input Password
    [Arguments]    $${password}
    [Documentation]    Enter password in the password field
    Wait Until Element Is Visible    $${LOGIN_PASSWORD_FIELD}
    Clear Element Text    $${LOGIN_PASSWORD_FIELD}
    Input Text    $${LOGIN_PASSWORD_FIELD}    $${password}

Click Login Button
    [Documentation]    Click the login button
    Wait Until Element Is Enabled    $${LOGIN_BUTTON}
    Click Button    $${LOGIN_BUTTON}

Login With Credentials
    [Arguments]    $${username}    $${password}
    [Documentation]    Complete login process with given credentials
    Input Username    $${username}
    Input Password    $${password}
    Click Login Button

Verify Error Message
    [Arguments]    $${expected_message}
    [Documentation]    Verify error message is displayed
    Wait Until Element Is Visible    $${LOGIN_ERROR_MESSAGE}    10s
    Element Text Should Be    $${LOGIN_ERROR_MESSAGE}    $${expected_message}
""")
        
        return template.substitute(
            template_type=template_type.upper(),
            username_field=selectors["username_field"],
            password_field=selectors["password_field"],
            login_button=selectors["login_button"],
            error_message=selectors["error_message"]
        )
        
    except Exception as e:
        return f"# ERROR: {str(e)}\n# Please contact support."

@mcp.tool()
def create_advanced_selenium_keywords() -> str:
    """Generate Robot Framework keywords for advanced Selenium operations. Returns .robot file content as text - does not execute."""
    template = """*** Settings ***
Library    SeleniumLibrary

*** Keywords ***
# Dropdown/Select Operations
Select Dropdown Option By Label
    [Arguments]    ${locator}    ${label}
    [Documentation]    Select option from dropdown by visible text
    Wait Until Element Is Visible    ${locator}    10s
    Select From List By Label    ${locator}    ${label}

Select Dropdown Option By Value
    [Arguments]    ${locator}    ${value}
    [Documentation]    Select option from dropdown by value
    Wait Until Element Is Visible    ${locator}    10s
    Select From List By Value    ${locator}    ${value}

# Checkbox Operations
Select Checkbox If Not Selected
    [Arguments]    ${locator}
    [Documentation]    Select checkbox only if it's not already selected
    Wait Until Element Is Visible    ${locator}    10s
    ${is_selected}=    Run Keyword And Return Status    Checkbox Should Be Selected    ${locator}
    Run Keyword If    not ${is_selected}    Select Checkbox    ${locator}

Unselect Checkbox If Selected
    [Arguments]    ${locator}
    [Documentation]    Unselect checkbox only if it's currently selected
    Wait Until Element Is Visible    ${locator}    10s
    ${is_selected}=    Run Keyword And Return Status    Checkbox Should Be Selected    ${locator}
    Run Keyword If    ${is_selected}    Unselect Checkbox    ${locator}

# File Upload Operations
Upload File To Element
    [Arguments]    ${locator}    ${file_path}
    [Documentation]    Upload file using file input element
    Wait Until Element Is Visible    ${locator}    10s
    Choose File    ${locator}    ${file_path}

# Alert/Pop-up Operations
Handle Alert And Accept
    [Documentation]    Handle JavaScript alert and accept it
    Alert Should Be Present
    Accept Alert

Handle Alert And Dismiss
    [Documentation]    Handle JavaScript alert and dismiss it
    Alert Should Be Present
    Dismiss Alert

Get Alert Text And Accept
    [Documentation]    Get alert text and accept the alert
    Alert Should Be Present
    ${alert_text}=    Get Alert Message
    Accept Alert
    RETURN    ${alert_text}

# Mouse Operations
Hover Over Element
    [Arguments]    ${locator}
    [Documentation]    Hover mouse over an element
    Wait Until Element Is Visible    ${locator}    10s
    Mouse Over    ${locator}

Double Click On Element
    [Arguments]    ${locator}
    [Documentation]    Double click on an element
    Wait Until Element Is Visible    ${locator}    10s
    Double Click Element    ${locator}

Right Click On Element
    [Arguments]    ${locator}
    [Documentation]    Right click on an element
    Wait Until Element Is Visible    ${locator}    10s
    Open Context Menu    ${locator}

# Scroll Operations
Scroll To Element
    [Arguments]    ${locator}
    [Documentation]    Scroll element into view
    Wait Until Element Is Visible    ${locator}    10s
    Scroll Element Into View    ${locator}

Scroll To Bottom Of Page
    [Documentation]    Scroll to the bottom of the page
    Execute JavaScript    window.scrollTo(0, document.body.scrollHeight)

Scroll To Top Of Page
    [Documentation]    Scroll to the top of the page
    Execute JavaScript    window.scrollTo(0, 0)

# Window/Tab Operations
Switch To New Window
    [Documentation]    Switch to the newly opened window/tab
    ${current_windows}=    Get Window Handles
    ${window_count}=    Get Length    ${current_windows}
    Should Be True    ${window_count} > 1    New window should be opened
    Switch Window    ${current_windows}[-1]

Close Current Window And Switch Back
    [Documentation]    Close current window and switch to previous one
    Close Window
    Switch Window    MAIN

# JavaScript Operations
Execute Custom JavaScript
    [Arguments]    ${javascript_code}
    [Documentation]    Execute custom JavaScript code
    ${result}=    Execute JavaScript    ${javascript_code}
    RETURN    ${result}

Set Element Attribute
    [Arguments]    ${locator}    ${attribute}    ${value}
    [Documentation]    Set attribute value of an element using JavaScript
    Wait Until Element Is Visible    ${locator}    10s
    Execute JavaScript    arguments[0].setAttribute('${attribute}', '${value}');    ARGUMENTS    ${locator}

Get Element Attribute Value
    [Arguments]    ${locator}    ${attribute}
    [Documentation]    Get attribute value of an element
    Wait Until Element Is Visible    ${locator}    10s
    ${value}=    Get Element Attribute    ${locator}    ${attribute}
    RETURN    ${value}

# Advanced Wait Operations
Wait Until Element Contains Text
    [Arguments]    ${locator}    ${expected_text}    ${timeout}=10s
    [Documentation]    Wait until element contains specific text
    Wait Until Element Is Visible    ${locator}    ${timeout}
    Wait Until Element Contains    ${locator}    ${expected_text}    ${timeout}

Wait Until Page Title Contains
    [Arguments]    ${expected_title}    ${timeout}=10s
    [Documentation]    Wait until page title contains expected text
    Wait Until Title Contains    ${expected_title}    ${timeout}

Wait For Element To Disappear
    [Arguments]    ${locator}    ${timeout}=10s
    [Documentation]    Wait for element to disappear from page
    Wait Until Element Is Not Visible    ${locator}    ${timeout}

# Table Operations
Get Table Cell Text
    [Arguments]    ${table_locator}    ${row}    ${column}
    [Documentation]    Get text from specific table cell
    ${cell_text}=    Get Table Cell    ${table_locator}    ${row}    ${column}
    RETURN    ${cell_text}

Get Table Row Count
    [Arguments]    ${table_locator}
    [Documentation]    Get number of rows in table
    ${row_count}=    Get Element Count    ${table_locator}//tr
    RETURN    ${row_count}

# Form Validation
Verify Field Is Required
    [Arguments]    ${locator}
    [Documentation]    Verify field has required attribute
    ${is_required}=    Get Element Attribute    ${locator}    required
    Should Not Be Empty    ${is_required}    Field should be required

Verify Field Is Disabled
    [Arguments]    ${locator}
    [Documentation]    Verify field is disabled
    Element Should Be Disabled    ${locator}

Verify Field Is Enabled
    [Arguments]    ${locator}
    [Documentation]    Verify field is enabled
    Element Should Be Enabled    ${locator}
"""
    return template

@mcp.tool()
def create_extended_selenium_keywords() -> str:
    """Generate extended Robot Framework keywords for screenshots, performance monitoring, and window management. Returns .robot file content as text - does not execute."""
    return """*** Settings ***
Library    SeleniumLibrary
Library    Collections
Library    String
Library    DateTime

*** Keywords ***
# Screenshot Capabilities
Capture Full Page Screenshot
    [Arguments]    ${filename}=page_screenshot.png
    [Documentation]    Capture screenshot of entire page
    Capture Page Screenshot    ${filename}
    Log    Screenshot saved as: ${filename}

Capture Element Screenshot
    [Arguments]    ${locator}    ${filename}=element_screenshot.png
    [Documentation]    Capture screenshot of specific element
    Wait Until Element Is Visible    ${locator}    10s
    Capture Element Screenshot    ${locator}    ${filename}
    Log    Element screenshot saved as: ${filename}

Capture Screenshot With Timestamp
    [Documentation]    Capture screenshot with current timestamp in filename
    ${timestamp}=    Get Current Date    result_format=%Y%m%d_%H%M%S
    ${filename}=    Set Variable    screenshot_${timestamp}.png
    Capture Page Screenshot    ${filename}
    RETURN    ${filename}

Set Screenshot Directory
    [Arguments]    ${directory_path}
    [Documentation]    Set custom directory for screenshots
    Set Screenshot Directory    ${directory_path}
    Log    Screenshot directory set to: ${directory_path}

# Text Retrieval Operations
Get Element Text Value
    [Arguments]    ${locator}
    [Documentation]    Get text content from an element
    Wait Until Element Is Visible    ${locator}    10s
    ${text}=    Get Text    ${locator}
    RETURN    ${text}

Get Input Field Value
    [Arguments]    ${locator}
    [Documentation]    Get value from input field
    Wait Until Element Is Visible    ${locator}    10s
    ${value}=    Get Value    ${locator}
    RETURN    ${value}
Switch To Window By Title
    [Documentation]    Switch to browser window by title
    [Arguments]    ${expected_title}
    @{windows}=    Get Window Handles
    FOR    ${window}    IN    @{windows}
        Switch Window    ${window}
        ${title}=    Get Title
        IF    '${title}' == '${expected_title}'
            RETURN
        END
    END
    Fail    Window with title '${expected_title}' not found

Switch To Window By URL
    [Documentation]    Switch to browser window by URL pattern
    [Arguments]    ${url_pattern}
    @{windows}=    Get Window Handles
    FOR    ${window}    IN    @{windows}
        Switch Window    ${window}
        ${current_url}=    Get Location
        IF    '${url_pattern}' in '${current_url}'
            RETURN
        END
    END
    Fail    Window with URL pattern '${url_pattern}' not found

Close Other Windows
    [Documentation]    Close all windows except the current one
    ${main_window}=    Get Window Handles
    ${main_window}=    Get From List    ${main_window}    0
    @{all_windows}=    Get Window Handles
    FOR    ${window}    IN    @{all_windows}
        IF    '${window}' != '${main_window}'
            Switch Window    ${window}
            Close Window
        END
    END
    Switch Window    ${main_window}

Get Page Performance Metrics
    [Documentation]    Get basic page performance metrics using JavaScript
    ${load_time}=    Execute Javascript    return window.performance.timing.loadEventEnd - window.performance.timing.navigationStart
    ${dom_ready}=    Execute Javascript    return window.performance.timing.domContentLoadedEventEnd - window.performance.timing.navigationStart
    ${metrics}=    Create Dictionary    load_time=${load_time}    dom_ready=${dom_ready}
    [Return]    ${metrics}

Scroll To Element Smoothly
    [Documentation]    Scroll to element with smooth animation
    [Arguments]    ${locator}
    Execute Javascript    
    ...    var element = document.evaluate("${locator}", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
    ...    if (element) { element.scrollIntoView({behavior: 'smooth', block: 'center'}); }

Check Element Visibility Percentage
    [Documentation]    Check what percentage of element is visible in viewport
    [Arguments]    ${locator}
    ${visibility}=    Execute Javascript    
    ...    var element = document.evaluate("${locator}", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
    ...    if (!element) return 0;
    ...    var rect = element.getBoundingClientRect();
    ...    var viewport = {width: window.innerWidth, height: window.innerHeight};
    ...    var visible = Math.max(0, Math.min(rect.right, viewport.width) - Math.max(rect.left, 0)) *
    ...               Math.max(0, Math.min(rect.bottom, viewport.height) - Math.max(rect.top, 0));
    ...    var total = rect.width * rect.height;
    ...    return total > 0 ? (visible / total * 100).toFixed(2) : 0;
    [Return]    ${visibility}

Take Element Screenshot
    [Documentation]    Take screenshot of specific element
    [Arguments]    ${locator}    ${filename}=element_screenshot.png
    Capture Element Screenshot    ${locator}    ${filename}
    [Return]    ${filename}

Get All List Labels
    [Arguments]    ${locator}
    [Documentation]    Get all available option labels from dropdown
    Wait Until Element Is Visible    ${locator}    10s
    ${labels}=    Get List Items    ${locator}
    RETURN    ${labels}

Get Page Title
    [Documentation]    Get current page title
    ${title}=    Get Title
    RETURN    ${title}

Get Current URL
    [Documentation]    Get current page URL
    ${url}=    Get Location
    RETURN    ${url}

Get Page Source
    [Documentation]    Get complete page source HTML
    ${source}=    Get Source
    RETURN    ${source}

# Window Management Operations
Get Current Window Position
    [Documentation]    Get current window position coordinates
    ${position}=    Get Window Position
    Log    Current window position: ${position}
    RETURN    ${position}

Set Window Position
    [Arguments]    ${x}    ${y}
    [Documentation]    Set window position to specific coordinates
    Set Window Position    ${x}    ${y}
    Log    Window position set to: ${x}, ${y}

Get Current Window Size
    [Documentation]    Get current window size dimensions
    ${size}=    Get Window Size
    Log    Current window size: ${size}
    RETURN    ${size}

Set Window Size
    [Arguments]    ${width}    ${height}
    [Documentation]    Set window size to specific dimensions
    Set Window Size    ${width}    ${height}
    Log    Window size set to: ${width}x${height}

Center Window On Screen
    [Documentation]    Center the browser window on screen
    ${screen_width}=    Execute JavaScript    return screen.width;
    ${screen_height}=    Execute JavaScript    return screen.height;
    ${window_width}=    Set Variable    1200
    ${window_height}=    Set Variable    800
    ${x}=    Evaluate    (${screen_width} - ${window_width}) // 2
    ${y}=    Evaluate    (${screen_height} - ${window_height}) // 2
    Set Window Size    ${window_width}    ${window_height}
    Set Window Position    ${x}    ${y}

Minimize Browser Window
    [Documentation]    Minimize the browser window
    Execute JavaScript    window.blur();

Restore Window Size
    [Arguments]    ${width}=1024    ${height}=768
    [Documentation]    Restore window to default size
    Set Window Size    ${width}    ${height}
    Maximize Browser Window

# Performance and Logging Operations
Get Browser Console Logs
    [Documentation]    Retrieve browser console logs
    ${logs}=    Get Browser Logs
    Log Many    @{logs}
    RETURN    ${logs}

Log Performance Metrics
    [Documentation]    Log browser performance metrics
    ${navigation_timing}=    Execute JavaScript    return JSON.stringify(performance.getEntriesByType('navigation')[0]);
    ${paint_timing}=    Execute JavaScript    return JSON.stringify(performance.getEntriesByType('paint'));
    Log    Navigation Timing: ${navigation_timing}
    Log    Paint Timing: ${paint_timing}

Measure Page Load Time
    [Documentation]    Measure and return page load time in milliseconds
    ${load_time}=    Execute JavaScript    return performance.getEntriesByType('navigation')[0].loadEventEnd - performance.getEntriesByType('navigation')[0].navigationStart;
    Log    Page load time: ${load_time} ms
    RETURN    ${load_time}

Get Network Performance
    [Documentation]    Get network performance information
    ${network_info}=    Execute JavaScript    
    ...    return JSON.stringify({
    ...        connection: navigator.connection || navigator.mozConnection || navigator.webkitConnection,
    ...        onLine: navigator.onLine,
    ...        cookieEnabled: navigator.cookieEnabled
    ...    });
    Log    Network Info: ${network_info}
    RETURN    ${network_info}

Set Browser Implicit Wait
    [Arguments]    ${timeout}=10s
    [Documentation]    Set implicit wait timeout for element finding
    Set Browser Implicit Wait    ${timeout}
    Log    Browser implicit wait set to: ${timeout}

Log Browser Information
    [Documentation]    Log comprehensive browser information
    ${user_agent}=    Execute JavaScript    return navigator.userAgent;
    ${viewport}=    Execute JavaScript    return window.innerWidth + 'x' + window.innerHeight;
    ${screen_resolution}=    Execute JavaScript    return screen.width + 'x' + screen.height;
    ${color_depth}=    Execute JavaScript    return screen.colorDepth;
    
    Log    User Agent: ${user_agent}
    Log    Viewport Size: ${viewport}
    Log    Screen Resolution: ${screen_resolution}
    Log    Color Depth: ${color_depth}

Monitor Page Resources
    [Documentation]    Monitor and log page resource loading
    ${resources}=    Execute JavaScript    
    ...    var resources = performance.getEntriesByType('resource');
    ...    var resourceInfo = resources.map(function(resource) {
    ...        return {
    ...            name: resource.name,
    ...            type: resource.initiatorType,
    ...            size: resource.transferSize,
    ...            duration: resource.duration
    ...        };
    ...    });
    ...    return JSON.stringify(resourceInfo);
    Log    Page Resources: ${resources}
    RETURN    ${resources}

Clear Browser Performance Data
    [Documentation]    Clear browser performance timing data
    Execute JavaScript    performance.clearResourceTimings();
    Execute JavaScript    performance.clearMarks();
    Execute JavaScript    performance.clearMeasures();
    Log    Browser performance data cleared

# Enhanced Screenshot Operations with Elements
Compare Screenshots
    [Arguments]    ${baseline_screenshot}    ${current_screenshot}    ${threshold}=0.95
    [Documentation]    Compare two screenshots (requires additional image comparison library)
    Log    Comparing ${baseline_screenshot} with ${current_screenshot}
    # Note: This would require additional image comparison library like Pillow
    # For now, just logging the comparison request

Take Screenshot On Failure
    [Documentation]    Take screenshot when test fails (for teardown use)
    ${test_name}=    Get Variable Value    ${TEST_NAME}    unknown_test
    ${timestamp}=    Get Current Date    result_format=%Y%m%d_%H%M%S
    ${filename}=    Set Variable    failure_${test_name}_${timestamp}.png
    Capture Page Screenshot    ${filename}
    Log    Failure screenshot saved: ${filename}

Take Element Screenshot With Highlight
    [Arguments]    ${locator}    ${filename}=highlighted_element.png
    [Documentation]    Take screenshot of element with visual highlight
    Wait Until Element Is Visible    ${locator}    10s
    # Add visual highlight
    Execute JavaScript    arguments[0].style.border = '3px solid red';    ARGUMENTS    ${locator}
    Sleep    0.5s
    Capture Element Screenshot    ${locator}    ${filename}
    # Remove highlight
    Execute JavaScript    arguments[0].style.border = '';    ARGUMENTS    ${locator}
    Log    Highlighted element screenshot saved: ${filename}
"""
    return template

@mcp.tool()
def create_performance_monitoring_test() -> str:
    """Generate Robot Framework performance monitoring test code. Returns complete .robot file content as text - does not execute."""
    return """*** Settings ***
Library    SeleniumLibrary
Library    Collections
Library    DateTime
Library    OperatingSystem

*** Variables ***
${PERFORMANCE_THRESHOLD_LOAD}    3000    # 3 seconds
${PERFORMANCE_THRESHOLD_INTERACTIVE}    2000    # 2 seconds
${PERFORMANCE_THRESHOLD_PAINT}    1000    # 1 second

*** Test Cases ***
Website Performance Test
    [Documentation]    Comprehensive website performance testing
    [Tags]    performance    load-time    metrics
    
    # Start performance monitoring
    ${test_start}=    Get Current Date    result_format=epoch
    
    Open Browser    ${TEST_URL}    chrome    options=add_argument("--enable-precise-memory-info")
    
    # Wait for page to fully load
    Wait Until Page Does Not Contain    Loading    timeout=30s
    Sleep    2s    # Allow all resources to load
    
    # Collect performance metrics
    ${metrics}=    Collect Performance Metrics
    
    # Validate performance thresholds
    Validate Performance Thresholds    ${metrics}
    
    # Test page interactions performance
    Test Page Interaction Performance
    
    # Generate performance report
    Generate Performance Report    ${metrics}
    
    Close Browser

*** Keywords ***
Collect Performance Metrics
    [Documentation]    Collect comprehensive performance metrics
    
    # Navigation timing metrics
    ${navigation_timing}=    Execute Javascript    
    ...    var timing = window.performance.timing;
    ...    return {
    ...        'dns_lookup': timing.domainLookupEnd - timing.domainLookupStart,
    ...        'tcp_connect': timing.connectEnd - timing.connectStart,
    ...        'request_response': timing.responseEnd - timing.requestStart,
    ...        'dom_processing': timing.domComplete - timing.domLoading,
    ...        'load_complete': timing.loadEventEnd - timing.navigationStart,
    ...        'dom_ready': timing.domContentLoadedEventEnd - timing.navigationStart,
    ...        'first_paint': timing.responseStart - timing.navigationStart
    ...    };
    
    # Paint timing metrics (if supported)
    ${paint_timing}=    Execute Javascript    
    ...    if ('getEntriesByType' in window.performance) {
    ...        var paints = window.performance.getEntriesByType('paint');
    ...        var result = {};
    ...        paints.forEach(function(paint) {
    ...            result[paint.name.replace('-', '_')] = paint.startTime;
    ...        });
    ...        return result;
    ...    }
    ...    return {};
    
    # Memory usage (if supported)
    ${memory_info}=    Execute Javascript    
    ...    if ('memory' in window.performance) {
    ...        return {
    ...            'used_js_heap': window.performance.memory.usedJSHeapSize,
    ...            'total_js_heap': window.performance.memory.totalJSHeapSize,
    ...            'heap_limit': window.performance.memory.jsHeapSizeLimit
    ...        };
    ...    }
    ...    return {};
    
    # Resource timing
    ${resource_count}=    Execute Javascript    
    ...    if ('getEntriesByType' in window.performance) {
    ...        var resources = window.performance.getEntriesByType('resource');
    ...        var types = {};
    ...        resources.forEach(function(resource) {
    ...            var type = resource.initiatorType || 'other';
    ...            types[type] = (types[type] || 0) + 1;
    ...        });
    ...        types['total'] = resources.length;
    ...        return types;
    ...    }
    ...    return {};
    
    # Combine all metrics
    ${all_metrics}=    Create Dictionary
    Set To Dictionary    ${all_metrics}    navigation=${navigation_timing}
    Set To Dictionary    ${all_metrics}    paint=${paint_timing}
    Set To Dictionary    ${all_metrics}    memory=${memory_info}
    Set To Dictionary    ${all_metrics}    resources=${resource_count}
    
    [Return]    ${all_metrics}

Validate Performance Thresholds
    [Documentation]    Validate performance against thresholds
    [Arguments]    ${metrics}
    
    ${navigation}=    Get From Dictionary    ${metrics}    navigation
    
    # Check load time
    ${load_time}=    Get From Dictionary    ${navigation}    load_complete
    Should Be True    ${load_time} < ${PERFORMANCE_THRESHOLD_LOAD}    
    ...    Page load time (${load_time}ms) exceeds threshold (${PERFORMANCE_THRESHOLD_LOAD}ms)
    
    # Check DOM ready time
    ${dom_ready}=    Get From Dictionary    ${navigation}    dom_ready
    Should Be True    ${dom_ready} < ${PERFORMANCE_THRESHOLD_INTERACTIVE}    
    ...    DOM ready time (${dom_ready}ms) exceeds threshold (${PERFORMANCE_THRESHOLD_INTERACTIVE}ms)
    
    # Check first paint time (if available)
    ${paint}=    Get From Dictionary    ${metrics}    paint
    ${has_first_paint}=    Run Keyword And Return Status    Dictionary Should Contain Key    ${paint}    first_paint
    IF    ${has_first_paint}
        ${first_paint}=    Get From Dictionary    ${paint}    first_paint
        Should Be True    ${first_paint} < ${PERFORMANCE_THRESHOLD_PAINT}    
        ...    First paint time (${first_paint}ms) exceeds threshold (${PERFORMANCE_THRESHOLD_PAINT}ms)
    END

Test Page Interaction Performance
    [Documentation]    Test performance of page interactions
    
    # Test scroll performance
    ${scroll_start}=    Get Time    epoch
    Execute Javascript    window.scrollTo(0, document.body.scrollHeight);
    Sleep    0.5s
    Execute Javascript    window.scrollTo(0, 0);
    ${scroll_end}=    Get Time    epoch
    ${scroll_time}=    Evaluate    (${scroll_end} - ${scroll_start}) * 1000
    
    Log    Scroll performance: ${scroll_time}ms
    Should Be True    ${scroll_time} < 500    Scroll should be smooth (< 500ms)
    
    # Test click response time (if interactive elements exist)
    ${buttons}=    Get WebElements    css=button, input[type="submit"], .btn
    ${button_count}=    Get Length    ${buttons}
    
    IF    ${button_count} > 0
        ${button}=    Get From List    ${buttons}    0
        ${click_start}=    Get Time    epoch
        Click Element    ${button}
        Sleep    0.1s    # Small delay to register interaction
        ${click_end}=    Get Time    epoch
        ${click_time}=    Evaluate    (${click_end} - ${click_start}) * 1000
        
        Log    Click response time: ${click_time}ms
        Should Be True    ${click_time} < 200    Click response should be immediate (< 200ms)
    END

Generate Performance Report
    [Documentation]    Generate detailed performance report
    [Arguments]    ${metrics}
    
    ${timestamp}=    Get Current Date    result_format=%Y-%m-%d_%H-%M-%S
    ${report_file}=    Set Variable    performance_report_${timestamp}.txt
    
    ${navigation}=    Get From Dictionary    ${metrics}    navigation
    ${resources}=    Get From Dictionary    ${metrics}    resources
    
    ${report_content}=    Catenate    SEPARATOR=\n
    ...    PERFORMANCE TEST REPORT
    ...    =========================
    ...    Test URL: ${TEST_URL}
    ...    Test Time: ${timestamp}
    ...    
    ...    NAVIGATION TIMING:
    ...    - DNS Lookup: ${navigation}[dns_lookup]ms
    ...    - TCP Connect: ${navigation}[tcp_connect]ms
    ...    - Request/Response: ${navigation}[request_response]ms
    ...    - DOM Processing: ${navigation}[dom_processing]ms
    ...    - Page Load Complete: ${navigation}[load_complete]ms
    ...    - DOM Ready: ${navigation}[dom_ready]ms
    ...    
    ...    RESOURCE LOADING:
    ...    - Total Resources: ${resources}[total] if 'total' in ${resources} else 'N/A'
    ...    
    ...    PERFORMANCE THRESHOLDS:
    ...    - Load Time Threshold: ${PERFORMANCE_THRESHOLD_LOAD}ms
    ...    - Interactive Threshold: ${PERFORMANCE_THRESHOLD_INTERACTIVE}ms
    ...    - Paint Threshold: ${PERFORMANCE_THRESHOLD_PAINT}ms
    
    Create File    ${report_file}    ${report_content}
    Log    Performance report saved to: ${report_file}

    Performance Comparison Test
    [Documentation]    Compare performance across multiple test runs
    [Arguments]    ${test_iterations}=3
    
    @{all_results}=    Create List
    
    FOR    ${iteration}    IN RANGE    1    ${test_iterations + 1}
        Log    Running performance test iteration ${iteration}
        
        Open Browser    ${TEST_URL}    chrome
        Sleep    2s
        
        ${metrics}=    Collect Performance Metrics
        Append To List    ${all_results}    ${metrics}
        
        Close Browser
        Sleep    5s    # Wait between tests
    END
    
    # Calculate average performance
    ${avg_metrics}=    Calculate Average Performance    ${all_results}
    Log    Average performance across ${test_iterations} runs: ${avg_metrics}

Calculate Average Performance
    [Documentation]    Calculate average performance from multiple test runs
    [Arguments]    ${results_list}
    
    ${total_load}=    Set Variable    0
    ${total_dom}=    Set Variable    0
    ${count}=    Get Length    ${results_list}
    
    FOR    ${result}    IN    @{results_list}
        ${navigation}=    Get From Dictionary    ${result}    navigation
        ${load_time}=    Get From Dictionary    ${navigation}    load_complete
        ${dom_time}=    Get From Dictionary    ${navigation}    dom_ready
        
        ${total_load}=    Evaluate    ${total_load} + ${load_time}
        ${total_dom}=    Evaluate    ${total_dom} + ${dom_time}
    END
    
    ${avg_load}=    Evaluate    ${total_load} / ${count}
    ${avg_dom}=    Evaluate    ${total_dom} / ${count}
    
    ${averages}=    Create Dictionary    avg_load_time=${avg_load}    avg_dom_ready=${avg_dom}
    [Return]    ${averages}
"""

@mcp.tool()
def create_data_driven_test(test_data_file: str = "test_data.csv") -> str:
    """Generate Robot Framework data-driven test template code. Returns .robot file content as text - does not execute."""
    template = f"""*** Settings ***
Library    SeleniumLibrary
Library    DataDriver    {test_data_file}    encoding=utf-8
Test Template    Login Test Template

*** Variables ***
${{BROWSER}}        Chrome
${{BASE_URL}}       https://www.appurl.com

*** Test Cases ***
Login Test With ${{username}} And ${{password}}
    [Tags]    data-driven    login
    # Test case will be generated for each row in CSV

*** Keywords ***
Login Test Template
    [Arguments]    ${{username}}    ${{password}}    ${{expected_result}}
    [Documentation]    Template for data-driven login tests
    
    Open Browser    ${{BASE_URL}}    ${{BROWSER}}
    Maximize Browser Window
    
    Input Text    id=user-name    ${{username}}
    Input Text    id=password    ${{password}}
    Click Button    id=login-button
    
    Run Keyword If    '${{expected_result}}' == 'success'
    ...    Wait Until Page Contains Element    xpath=//span[@class='title']    10s
    ...    ELSE
    ...    Wait Until Page Contains Element    xpath=//h3[@data-test='error']    10s
    
    [Teardown]    Close Browser

*** Comments ***
# Create {test_data_file} with columns: username,password,expected_result
# Example CSV content:
# username,password,expected_result
# standard_user,secret_sauce,success
# locked_out_user,secret_sauce,error
# invalid_user,wrong_password,error
"""
    return template

@mcp.tool()
def create_api_integration_test(base_url: str, endpoint: str, method: str = "GET") -> str:
    """Generate Robot Framework API integration test code. Returns .robot file content as text - does not execute."""
    try:
        validated_url = InputValidator.validate_url(base_url)
        
        template = Template("""*** Settings ***
Library    SeleniumLibrary
Library    RequestsLibrary
Library    Collections

*** Variables ***
$${BASE_URL}         $base_url
$${API_ENDPOINT}     $endpoint
$${BROWSER}          Chrome

*** Test Cases ***
API UI Integration Test
    [Documentation]    Test API and UI integration
    [Tags]    integration    api    ui
    
    # API Setup and Validation
    Create Session    api_session    $${BASE_URL}
    $${api_response}=    GET On Session    api_session    $${API_ENDPOINT}
    Status Should Be    200    $${api_response}
    $${response_data}=    Set Variable    $${api_response.json()}
    
    # UI Validation based on API data
    Open Browser    $${BASE_URL}    $${BROWSER}
    Maximize Browser Window
    
    # Validate UI reflects API data
    Wait Until Page Contains    $${response_data['title']}    10s
    Page Should Contain    $${response_data['description']}
    
    [Teardown]    Run Keywords
    ...    Close Browser    AND
    ...    Delete All Sessions

*** Keywords ***
Validate API Response Structure
    [Arguments]    $${response}
    [Documentation]    Validate API response has required fields
    Dictionary Should Contain Key    $${response}    id
    Dictionary Should Contain Key    $${response}    title
    Dictionary Should Contain Key    $${response}    description
""")
        
        return template.substitute(
            base_url=validated_url,
            endpoint=endpoint,
            method=method.upper()
        )
        
    except ValidationError as e:
        return f"# VALIDATION ERROR: {str(e)}\n# Please correct the input and try again."
    except Exception as e:
        return f"# UNEXPECTED ERROR: {str(e)}\n# Please contact support."

@mcp.tool()
def validate_robot_framework_syntax(robot_code: str) -> str:
    """Validate Robot Framework syntax and provide suggestions. Returns validation report as text - does not execute code."""
    try:
        lines = robot_code.split('\n')
        errors = []
        warnings = []
        
        # Check for basic syntax issues
        for i, line in enumerate(lines, 1):
            line_stripped = line.strip()
            if not line_stripped or line_stripped.startswith('#'):
                continue
                
            # Check for proper section headers
            if line_stripped.startswith('***') and not line_stripped.endswith('***'):
                errors.append(f"Line {i}: Section header must end with '***'")
            
            # Check for proper variable syntax - should be ${variable} not ${{variable}}
            if '${{' in line and '}}' in line:
                warnings.append(f"Line {i}: Use ${{variable}} syntax instead of ${{{{variable}}}}")
            
            # Check for unclosed variable syntax
            if '${' in line and '}' not in line:
                errors.append(f"Line {i}: Unclosed variable syntax")
            
            # Check for proper spacing in variables section
            if line_stripped.startswith('${') and '    ' not in line:
                warnings.append(f"Line {i}: Variables should use 4 spaces between name and value")
        
        result = "# ROBOT FRAMEWORK SYNTAX VALIDATION\n\n"
        
        if errors:
            result += "## ERRORS (Must Fix):\n"
            result += '\n'.join(f"- {error}" for error in errors) + "\n\n"
        
        if warnings:
            result += "## WARNINGS (Recommended Fixes):\n"
            result += '\n'.join(f"- {warning}" for warning in warnings) + "\n\n"
        
        if not errors and not warnings:
            result += "✅ VALIDATION PASSED: No syntax errors found\n"
        elif not errors:
            result += "⚠️  VALIDATION PASSED WITH WARNINGS: No critical errors, but consider fixing warnings\n"
        else:
            result += "❌ VALIDATION FAILED: Critical errors found that must be fixed\n"
        
        return result
            
    except Exception as e:
        return f"# VALIDATION ERROR: {str(e)}"


def main():
    """Entry point for the Robot Framework MCP server"""
    import sys
    
    # Only print startup messages if not in stdio mode
    if len(sys.argv) > 1 and '--stdio' in sys.argv:
        # Running in stdio mode (MCP client mode)
        pass
    else:
        # Running in standalone mode
        print("Starting Robot Framework MCP server...")
        print("Available templates: appLocator, generic, bootstrap")
        print("Features: Input validation, configurable selectors, syntax validation")
        print("Advanced tools: API integration, data-driven testing, responsive testing")

    try:
        mcp.run()
    except Exception as e:
        if len(sys.argv) <= 1 or '--stdio' not in sys.argv:
            print(f"Error starting Robot framework MCP server: {e}")
            import traceback
            traceback.print_exc()
        raise

if __name__ == "__main__":
    main()