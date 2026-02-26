# import re
# from string import Template
# from urllib.parse import urlparse
# from mcp.server.fastmcp import FastMCP

# # Create an enhanced MCP server with validation and configurable selectors
# mcp = FastMCP("Robot framework MCP Server")

# class ValidationError(Exception):
#     """Custom exception for validation errors"""
#     pass

# class InputValidator:
#     """Centralized input validation for MCP tools"""
    
#     @staticmethod
#     def validate_url(url: str) -> str:
#         """Validate and return sanitized URL"""
#         if not url or not url.strip():
#             raise ValidationError("URL cannot be empty")
        
#         url = url.strip()
#         try:
#             result = urlparse(url)
#             if not all([result.scheme, result.netloc]):
#                 raise ValidationError(f"Invalid URL format: {url}")
            
#             if result.scheme not in ['http', 'https']:
#                 raise ValidationError(f"URL must use http or https protocol: {url}")
                
#             return url
#         except Exception as e:
#             raise ValidationError(f"URL validation failed: {str(e)}")

#     @staticmethod
#     def validate_credentials(username: str, password: str) -> tuple:
#         """Validate and return sanitized credentials"""
#         if not username or not username.strip():
#             raise ValidationError("Username cannot be empty")
        
#         if not password or not password.strip():
#             raise ValidationError("Password cannot be empty")
        
#         username = username.strip()
#         password = password.strip()
        
#         if len(username) > 100:
#             raise ValidationError("Username too long (max 100 characters)")
        
#         if len(password) > 100:
#             raise ValidationError("Password too long (max 100 characters)")
        
#         # Check for dangerous characters
#         dangerous_chars = ['<', '>', '"', "'", '&', '\n', '\r', '\t']
#         for char in dangerous_chars:
#             if char in username or char in password:
#                 raise ValidationError(f"Credentials contain invalid character: {char}")
        
#         return username, password
    
#     @staticmethod
#     def validate_selector(selector: str) -> str:
#         """Validate and return sanitized selector"""
#         if not selector or not selector.strip():
#             raise ValidationError("Selector cannot be empty")
        
#         selector = selector.strip()
        
#         # Basic validation patterns
#         valid_patterns = [
#             r'^id=.+',           # id=element-id
#             r'^name=.+',         # name=element-name
#             r'^class=.+',        # class=element-class
#             r'^css=.+',          # css=.class-name
#             r'^xpath=.+',        # xpath=//div[@id='test']
#             r'^tag=.+',          # tag=input
#             r'^\w+',             # plain CSS selector
#         ]
        
#         if not any(re.match(pattern, selector) for pattern in valid_patterns):
#             raise ValidationError(f"Invalid selector format: {selector}")
        
#         return selector

# # Predefined selector configurations for different applications
# SELECTOR_CONFIGS = {
#     "appLocator": {
#         "username_field": "id=user-name",
#         "password_field": "id=password",
#         "login_button": "id=login-button",
#         "success_indicator": "xpath=//span[@class='title']",
#         "error_message": "xpath=//h3[@data-test='error']",
#         "logout_button": "id=logout_sidebar_link"
#     },
#     "generic": {
#         "username_field": "id=username",
#         "password_field": "id=password",
#         "login_button": "css=button[type='submit']",
#         "success_indicator": "css=.dashboard",
#         "error_message": "css=.error",
#         "logout_button": "css=.logout"
#     },
#     "bootstrap": {
#         "username_field": "css=input[name='username']",
#         "password_field": "css=input[name='password']",
#         "login_button": "css=.btn-primary",
#         "success_indicator": "css=.navbar-brand",
#         "error_message": "css=.alert-danger",
#         "logout_button": "css=.btn-outline-secondary"
#     }
# }

# @mcp.tool()
# def create_login_test_case(url: str, username: str, password: str, template_type: str = "appLocator") -> str:
#     """Generate Robot Framework test case code for login functionality. Returns the complete .robot file content as text - does not execute the test."""
#     try:
#         # Validate inputs
#         validated_url = InputValidator.validate_url(url)
#         validated_username, validated_password = InputValidator.validate_credentials(username, password)
        
#         # Get selector configuration
#         selectors = SELECTOR_CONFIGS.get(template_type.lower(), SELECTOR_CONFIGS["generic"])
        
#         # Use Template for safe variable substitution and correct Robot Framework syntax
#         template = Template("""*** Settings ***
# Library    SeleniumLibrary

# *** Variables ***
# $${URL}           $url
# $${USERNAME}      $username
# $${PASSWORD}      $password
# $${BROWSER}       Chrome

# # Selector Variables
# $${USERNAME_FIELD}        $username_field
# $${PASSWORD_FIELD}        $password_field
# $${LOGIN_BUTTON}          $login_button
# $${SUCCESS_INDICATOR}     $success_indicator

# *** Test Cases ***
# Login Test
#     [Documentation]    Test login functionality for $template_type
#     [Tags]    smoke    login    $template_type
#     Open Browser    $${URL}    $${BROWSER}
#     Maximize Browser Window
#     Input Text    $${USERNAME_FIELD}    $${USERNAME}
#     Input Text    $${PASSWORD_FIELD}    $${PASSWORD}
#     Click Button    $${LOGIN_BUTTON}
#     Wait Until Page Contains Element    $${SUCCESS_INDICATOR}    10s
#     Element Text Should Be    $${SUCCESS_INDICATOR}    Products
#     [Teardown]    Close Browser
# """)
        
#         return template.substitute(
#             url=validated_url,
#             username=validated_username,
#             password=validated_password,
#             template_type=template_type,
#             username_field=selectors["username_field"],
#             password_field=selectors["password_field"],
#             login_button=selectors["login_button"],
#             success_indicator=selectors["success_indicator"]
#         )
        
#     except ValidationError as e:
#         return f"# VALIDATION ERROR: {str(e)}\n# Please correct the input and try again."
#     except Exception as e:
#         return f"# UNEXPECTED ERROR: {str(e)}\n# Please contact support."

# @mcp.tool()
# def create_page_object_login(template_type: str = "appLocator") -> str:
#     """Generate Robot Framework page object model code for login page. Returns .robot file content as text - does not execute."""
#     try:
#         # Get selector configuration
#         selectors = SELECTOR_CONFIGS.get(template_type.lower(), SELECTOR_CONFIGS["generic"])
        
#         # Use Template for safe variable substitution and correct Robot Framework syntax
#         template = Template("""*** Settings ***
# Library    SeleniumLibrary

# *** Variables ***
# # $template_type Application Selectors
# $${LOGIN_USERNAME_FIELD}    $username_field
# $${LOGIN_PASSWORD_FIELD}    $password_field
# $${LOGIN_BUTTON}           $login_button
# $${LOGIN_ERROR_MESSAGE}    $error_message

# *** Keywords ***
# Input Username
#     [Arguments]    $${username}
#     [Documentation]    Enter username in the username field
#     Wait Until Element Is Visible    $${LOGIN_USERNAME_FIELD}
#     Clear Element Text    $${LOGIN_USERNAME_FIELD}
#     Input Text    $${LOGIN_USERNAME_FIELD}    $${username}

# Input Password
#     [Arguments]    $${password}
#     [Documentation]    Enter password in the password field
#     Wait Until Element Is Visible    $${LOGIN_PASSWORD_FIELD}
#     Clear Element Text    $${LOGIN_PASSWORD_FIELD}
#     Input Text    $${LOGIN_PASSWORD_FIELD}    $${password}

# Click Login Button
#     [Documentation]    Click the login button
#     Wait Until Element Is Enabled    $${LOGIN_BUTTON}
#     Click Button    $${LOGIN_BUTTON}

# Login With Credentials
#     [Arguments]    $${username}    $${password}
#     [Documentation]    Complete login process with given credentials
#     Input Username    $${username}
#     Input Password    $${password}
#     Click Login Button

# Verify Error Message
#     [Arguments]    $${expected_message}
#     [Documentation]    Verify error message is displayed
#     Wait Until Element Is Visible    $${LOGIN_ERROR_MESSAGE}    10s
#     Element Text Should Be    $${LOGIN_ERROR_MESSAGE}    $${expected_message}
# """)
        
#         return template.substitute(
#             template_type=template_type.upper(),
#             username_field=selectors["username_field"],
#             password_field=selectors["password_field"],
#             login_button=selectors["login_button"],
#             error_message=selectors["error_message"]
#         )
        
#     except Exception as e:
#         return f"# ERROR: {str(e)}\n# Please contact support."

# @mcp.tool()
# def create_advanced_selenium_keywords() -> str:
#     """Generate Robot Framework keywords for advanced Selenium operations. Returns .robot file content as text - does not execute."""
#     template = """*** Settings ***
# Library    SeleniumLibrary

# *** Keywords ***
# # Dropdown/Select Operations
# Select Dropdown Option By Label
#     [Arguments]    ${locator}    ${label}
#     [Documentation]    Select option from dropdown by visible text
#     Wait Until Element Is Visible    ${locator}    10s
#     Select From List By Label    ${locator}    ${label}

# Select Dropdown Option By Value
#     [Arguments]    ${locator}    ${value}
#     [Documentation]    Select option from dropdown by value
#     Wait Until Element Is Visible    ${locator}    10s
#     Select From List By Value    ${locator}    ${value}

# # Checkbox Operations
# Select Checkbox If Not Selected
#     [Arguments]    ${locator}
#     [Documentation]    Select checkbox only if it's not already selected
#     Wait Until Element Is Visible    ${locator}    10s
#     ${is_selected}=    Run Keyword And Return Status    Checkbox Should Be Selected    ${locator}
#     Run Keyword If    not ${is_selected}    Select Checkbox    ${locator}

# Unselect Checkbox If Selected
#     [Arguments]    ${locator}
#     [Documentation]    Unselect checkbox only if it's currently selected
#     Wait Until Element Is Visible    ${locator}    10s
#     ${is_selected}=    Run Keyword And Return Status    Checkbox Should Be Selected    ${locator}
#     Run Keyword If    ${is_selected}    Unselect Checkbox    ${locator}

# # File Upload Operations
# Upload File To Element
#     [Arguments]    ${locator}    ${file_path}
#     [Documentation]    Upload file using file input element
#     Wait Until Element Is Visible    ${locator}    10s
#     Choose File    ${locator}    ${file_path}

# # Alert/Pop-up Operations
# Handle Alert And Accept
#     [Documentation]    Handle JavaScript alert and accept it
#     Alert Should Be Present
#     Accept Alert

# Handle Alert And Dismiss
#     [Documentation]    Handle JavaScript alert and dismiss it
#     Alert Should Be Present
#     Dismiss Alert

# Get Alert Text And Accept
#     [Documentation]    Get alert text and accept the alert
#     Alert Should Be Present
#     ${alert_text}=    Get Alert Message
#     Accept Alert
#     RETURN    ${alert_text}

# # Mouse Operations
# Hover Over Element
#     [Arguments]    ${locator}
#     [Documentation]    Hover mouse over an element
#     Wait Until Element Is Visible    ${locator}    10s
#     Mouse Over    ${locator}

# Double Click On Element
#     [Arguments]    ${locator}
#     [Documentation]    Double click on an element
#     Wait Until Element Is Visible    ${locator}    10s
#     Double Click Element    ${locator}

# Right Click On Element
#     [Arguments]    ${locator}
#     [Documentation]    Right click on an element
#     Wait Until Element Is Visible    ${locator}    10s
#     Open Context Menu    ${locator}

# # Scroll Operations
# Scroll To Element
#     [Arguments]    ${locator}
#     [Documentation]    Scroll element into view
#     Wait Until Element Is Visible    ${locator}    10s
#     Scroll Element Into View    ${locator}

# Scroll To Bottom Of Page
#     [Documentation]    Scroll to the bottom of the page
#     Execute JavaScript    window.scrollTo(0, document.body.scrollHeight)

# Scroll To Top Of Page
#     [Documentation]    Scroll to the top of the page
#     Execute JavaScript    window.scrollTo(0, 0)

# # Window/Tab Operations
# Switch To New Window
#     [Documentation]    Switch to the newly opened window/tab
#     ${current_windows}=    Get Window Handles
#     ${window_count}=    Get Length    ${current_windows}
#     Should Be True    ${window_count} > 1    New window should be opened
#     Switch Window    ${current_windows}[-1]

# Close Current Window And Switch Back
#     [Documentation]    Close current window and switch to previous one
#     Close Window
#     Switch Window    MAIN

# # JavaScript Operations
# Execute Custom JavaScript
#     [Arguments]    ${javascript_code}
#     [Documentation]    Execute custom JavaScript code
#     ${result}=    Execute JavaScript    ${javascript_code}
#     RETURN    ${result}

# Set Element Attribute
#     [Arguments]    ${locator}    ${attribute}    ${value}
#     [Documentation]    Set attribute value of an element using JavaScript
#     Wait Until Element Is Visible    ${locator}    10s
#     Execute JavaScript    arguments[0].setAttribute('${attribute}', '${value}');    ARGUMENTS    ${locator}

# Get Element Attribute Value
#     [Arguments]    ${locator}    ${attribute}
#     [Documentation]    Get attribute value of an element
#     Wait Until Element Is Visible    ${locator}    10s
#     ${value}=    Get Element Attribute    ${locator}    ${attribute}
#     RETURN    ${value}

# # Advanced Wait Operations
# Wait Until Element Contains Text
#     [Arguments]    ${locator}    ${expected_text}    ${timeout}=10s
#     [Documentation]    Wait until element contains specific text
#     Wait Until Element Is Visible    ${locator}    ${timeout}
#     Wait Until Element Contains    ${locator}    ${expected_text}    ${timeout}

# Wait Until Page Title Contains
#     [Arguments]    ${expected_title}    ${timeout}=10s
#     [Documentation]    Wait until page title contains expected text
#     Wait Until Title Contains    ${expected_title}    ${timeout}

# Wait For Element To Disappear
#     [Arguments]    ${locator}    ${timeout}=10s
#     [Documentation]    Wait for element to disappear from page
#     Wait Until Element Is Not Visible    ${locator}    ${timeout}

# # Table Operations
# Get Table Cell Text
#     [Arguments]    ${table_locator}    ${row}    ${column}
#     [Documentation]    Get text from specific table cell
#     ${cell_text}=    Get Table Cell    ${table_locator}    ${row}    ${column}
#     RETURN    ${cell_text}

# Get Table Row Count
#     [Arguments]    ${table_locator}
#     [Documentation]    Get number of rows in table
#     ${row_count}=    Get Element Count    ${table_locator}//tr
#     RETURN    ${row_count}

# # Form Validation
# Verify Field Is Required
#     [Arguments]    ${locator}
#     [Documentation]    Verify field has required attribute
#     ${is_required}=    Get Element Attribute    ${locator}    required
#     Should Not Be Empty    ${is_required}    Field should be required

# Verify Field Is Disabled
#     [Arguments]    ${locator}
#     [Documentation]    Verify field is disabled
#     Element Should Be Disabled    ${locator}

# Verify Field Is Enabled
#     [Arguments]    ${locator}
#     [Documentation]    Verify field is enabled
#     Element Should Be Enabled    ${locator}
# """
#     return template

# @mcp.tool()
# def create_extended_selenium_keywords() -> str:
#     """Generate extended Robot Framework keywords for screenshots, performance monitoring, and window management. Returns .robot file content as text - does not execute."""
#     return """*** Settings ***
# Library    SeleniumLibrary
# Library    Collections
# Library    String
# Library    DateTime

# *** Keywords ***
# # Screenshot Capabilities
# Capture Full Page Screenshot
#     [Arguments]    ${filename}=page_screenshot.png
#     [Documentation]    Capture screenshot of entire page
#     Capture Page Screenshot    ${filename}
#     Log    Screenshot saved as: ${filename}

# Capture Element Screenshot
#     [Arguments]    ${locator}    ${filename}=element_screenshot.png
#     [Documentation]    Capture screenshot of specific element
#     Wait Until Element Is Visible    ${locator}    10s
#     Capture Element Screenshot    ${locator}    ${filename}
#     Log    Element screenshot saved as: ${filename}

# Capture Screenshot With Timestamp
#     [Documentation]    Capture screenshot with current timestamp in filename
#     ${timestamp}=    Get Current Date    result_format=%Y%m%d_%H%M%S
#     ${filename}=    Set Variable    screenshot_${timestamp}.png
#     Capture Page Screenshot    ${filename}
#     RETURN    ${filename}

# Set Screenshot Directory
#     [Arguments]    ${directory_path}
#     [Documentation]    Set custom directory for screenshots
#     Set Screenshot Directory    ${directory_path}
#     Log    Screenshot directory set to: ${directory_path}

# # Text Retrieval Operations
# Get Element Text Value
#     [Arguments]    ${locator}
#     [Documentation]    Get text content from an element
#     Wait Until Element Is Visible    ${locator}    10s
#     ${text}=    Get Text    ${locator}
#     RETURN    ${text}

# Get Input Field Value
#     [Arguments]    ${locator}
#     [Documentation]    Get value from input field
#     Wait Until Element Is Visible    ${locator}    10s
#     ${value}=    Get Value    ${locator}
#     RETURN    ${value}
# Switch To Window By Title
#     [Documentation]    Switch to browser window by title
#     [Arguments]    ${expected_title}
#     @{windows}=    Get Window Handles
#     FOR    ${window}    IN    @{windows}
#         Switch Window    ${window}
#         ${title}=    Get Title
#         IF    '${title}' == '${expected_title}'
#             RETURN
#         END
#     END
#     Fail    Window with title '${expected_title}' not found

# Switch To Window By URL
#     [Documentation]    Switch to browser window by URL pattern
#     [Arguments]    ${url_pattern}
#     @{windows}=    Get Window Handles
#     FOR    ${window}    IN    @{windows}
#         Switch Window    ${window}
#         ${current_url}=    Get Location
#         IF    '${url_pattern}' in '${current_url}'
#             RETURN
#         END
#     END
#     Fail    Window with URL pattern '${url_pattern}' not found

# Close Other Windows
#     [Documentation]    Close all windows except the current one
#     ${main_window}=    Get Window Handles
#     ${main_window}=    Get From List    ${main_window}    0
#     @{all_windows}=    Get Window Handles
#     FOR    ${window}    IN    @{all_windows}
#         IF    '${window}' != '${main_window}'
#             Switch Window    ${window}
#             Close Window
#         END
#     END
#     Switch Window    ${main_window}

# Get Page Performance Metrics
#     [Documentation]    Get basic page performance metrics using JavaScript
#     ${load_time}=    Execute Javascript    return window.performance.timing.loadEventEnd - window.performance.timing.navigationStart
#     ${dom_ready}=    Execute Javascript    return window.performance.timing.domContentLoadedEventEnd - window.performance.timing.navigationStart
#     ${metrics}=    Create Dictionary    load_time=${load_time}    dom_ready=${dom_ready}
#     [Return]    ${metrics}

# Scroll To Element Smoothly
#     [Documentation]    Scroll to element with smooth animation
#     [Arguments]    ${locator}
#     Execute Javascript    
#     ...    var element = document.evaluate("${locator}", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
#     ...    if (element) { element.scrollIntoView({behavior: 'smooth', block: 'center'}); }

# Check Element Visibility Percentage
#     [Documentation]    Check what percentage of element is visible in viewport
#     [Arguments]    ${locator}
#     ${visibility}=    Execute Javascript    
#     ...    var element = document.evaluate("${locator}", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
#     ...    if (!element) return 0;
#     ...    var rect = element.getBoundingClientRect();
#     ...    var viewport = {width: window.innerWidth, height: window.innerHeight};
#     ...    var visible = Math.max(0, Math.min(rect.right, viewport.width) - Math.max(rect.left, 0)) *
#     ...               Math.max(0, Math.min(rect.bottom, viewport.height) - Math.max(rect.top, 0));
#     ...    var total = rect.width * rect.height;
#     ...    return total > 0 ? (visible / total * 100).toFixed(2) : 0;
#     [Return]    ${visibility}

# Take Element Screenshot
#     [Documentation]    Take screenshot of specific element
#     [Arguments]    ${locator}    ${filename}=element_screenshot.png
#     Capture Element Screenshot    ${locator}    ${filename}
#     [Return]    ${filename}

# Get All List Labels
#     [Arguments]    ${locator}
#     [Documentation]    Get all available option labels from dropdown
#     Wait Until Element Is Visible    ${locator}    10s
#     ${labels}=    Get List Items    ${locator}
#     RETURN    ${labels}

# Get Page Title
#     [Documentation]    Get current page title
#     ${title}=    Get Title
#     RETURN    ${title}

# Get Current URL
#     [Documentation]    Get current page URL
#     ${url}=    Get Location
#     RETURN    ${url}

# Get Page Source
#     [Documentation]    Get complete page source HTML
#     ${source}=    Get Source
#     RETURN    ${source}

# # Window Management Operations
# Get Current Window Position
#     [Documentation]    Get current window position coordinates
#     ${position}=    Get Window Position
#     Log    Current window position: ${position}
#     RETURN    ${position}

# Set Window Position
#     [Arguments]    ${x}    ${y}
#     [Documentation]    Set window position to specific coordinates
#     Set Window Position    ${x}    ${y}
#     Log    Window position set to: ${x}, ${y}

# Get Current Window Size
#     [Documentation]    Get current window size dimensions
#     ${size}=    Get Window Size
#     Log    Current window size: ${size}
#     RETURN    ${size}

# Set Window Size
#     [Arguments]    ${width}    ${height}
#     [Documentation]    Set window size to specific dimensions
#     Set Window Size    ${width}    ${height}
#     Log    Window size set to: ${width}x${height}

# Center Window On Screen
#     [Documentation]    Center the browser window on screen
#     ${screen_width}=    Execute JavaScript    return screen.width;
#     ${screen_height}=    Execute JavaScript    return screen.height;
#     ${window_width}=    Set Variable    1200
#     ${window_height}=    Set Variable    800
#     ${x}=    Evaluate    (${screen_width} - ${window_width}) // 2
#     ${y}=    Evaluate    (${screen_height} - ${window_height}) // 2
#     Set Window Size    ${window_width}    ${window_height}
#     Set Window Position    ${x}    ${y}

# Minimize Browser Window
#     [Documentation]    Minimize the browser window
#     Execute JavaScript    window.blur();

# Restore Window Size
#     [Arguments]    ${width}=1024    ${height}=768
#     [Documentation]    Restore window to default size
#     Set Window Size    ${width}    ${height}
#     Maximize Browser Window

# # Performance and Logging Operations
# Get Browser Console Logs
#     [Documentation]    Retrieve browser console logs
#     ${logs}=    Get Browser Logs
#     Log Many    @{logs}
#     RETURN    ${logs}

# Log Performance Metrics
#     [Documentation]    Log browser performance metrics
#     ${navigation_timing}=    Execute JavaScript    return JSON.stringify(performance.getEntriesByType('navigation')[0]);
#     ${paint_timing}=    Execute JavaScript    return JSON.stringify(performance.getEntriesByType('paint'));
#     Log    Navigation Timing: ${navigation_timing}
#     Log    Paint Timing: ${paint_timing}

# Measure Page Load Time
#     [Documentation]    Measure and return page load time in milliseconds
#     ${load_time}=    Execute JavaScript    return performance.getEntriesByType('navigation')[0].loadEventEnd - performance.getEntriesByType('navigation')[0].navigationStart;
#     Log    Page load time: ${load_time} ms
#     RETURN    ${load_time}

# Get Network Performance
#     [Documentation]    Get network performance information
#     ${network_info}=    Execute JavaScript    
#     ...    return JSON.stringify({
#     ...        connection: navigator.connection || navigator.mozConnection || navigator.webkitConnection,
#     ...        onLine: navigator.onLine,
#     ...        cookieEnabled: navigator.cookieEnabled
#     ...    });
#     Log    Network Info: ${network_info}
#     RETURN    ${network_info}

# Set Browser Implicit Wait
#     [Arguments]    ${timeout}=10s
#     [Documentation]    Set implicit wait timeout for element finding
#     Set Browser Implicit Wait    ${timeout}
#     Log    Browser implicit wait set to: ${timeout}

# Log Browser Information
#     [Documentation]    Log comprehensive browser information
#     ${user_agent}=    Execute JavaScript    return navigator.userAgent;
#     ${viewport}=    Execute JavaScript    return window.innerWidth + 'x' + window.innerHeight;
#     ${screen_resolution}=    Execute JavaScript    return screen.width + 'x' + screen.height;
#     ${color_depth}=    Execute JavaScript    return screen.colorDepth;
    
#     Log    User Agent: ${user_agent}
#     Log    Viewport Size: ${viewport}
#     Log    Screen Resolution: ${screen_resolution}
#     Log    Color Depth: ${color_depth}

# Monitor Page Resources
#     [Documentation]    Monitor and log page resource loading
#     ${resources}=    Execute JavaScript    
#     ...    var resources = performance.getEntriesByType('resource');
#     ...    var resourceInfo = resources.map(function(resource) {
#     ...        return {
#     ...            name: resource.name,
#     ...            type: resource.initiatorType,
#     ...            size: resource.transferSize,
#     ...            duration: resource.duration
#     ...        };
#     ...    });
#     ...    return JSON.stringify(resourceInfo);
#     Log    Page Resources: ${resources}
#     RETURN    ${resources}

# Clear Browser Performance Data
#     [Documentation]    Clear browser performance timing data
#     Execute JavaScript    performance.clearResourceTimings();
#     Execute JavaScript    performance.clearMarks();
#     Execute JavaScript    performance.clearMeasures();
#     Log    Browser performance data cleared

# # Enhanced Screenshot Operations with Elements
# Compare Screenshots
#     [Arguments]    ${baseline_screenshot}    ${current_screenshot}    ${threshold}=0.95
#     [Documentation]    Compare two screenshots (requires additional image comparison library)
#     Log    Comparing ${baseline_screenshot} with ${current_screenshot}
#     # Note: This would require additional image comparison library like Pillow
#     # For now, just logging the comparison request

# Take Screenshot On Failure
#     [Documentation]    Take screenshot when test fails (for teardown use)
#     ${test_name}=    Get Variable Value    ${TEST_NAME}    unknown_test
#     ${timestamp}=    Get Current Date    result_format=%Y%m%d_%H%M%S
#     ${filename}=    Set Variable    failure_${test_name}_${timestamp}.png
#     Capture Page Screenshot    ${filename}
#     Log    Failure screenshot saved: ${filename}

# Take Element Screenshot With Highlight
#     [Arguments]    ${locator}    ${filename}=highlighted_element.png
#     [Documentation]    Take screenshot of element with visual highlight
#     Wait Until Element Is Visible    ${locator}    10s
#     # Add visual highlight
#     Execute JavaScript    arguments[0].style.border = '3px solid red';    ARGUMENTS    ${locator}
#     Sleep    0.5s
#     Capture Element Screenshot    ${locator}    ${filename}
#     # Remove highlight
#     Execute JavaScript    arguments[0].style.border = '';    ARGUMENTS    ${locator}
#     Log    Highlighted element screenshot saved: ${filename}
# """
#     return template

# @mcp.tool()
# def create_performance_monitoring_test() -> str:
#     """Generate Robot Framework performance monitoring test code. Returns complete .robot file content as text - does not execute."""
#     return """*** Settings ***
# Library    SeleniumLibrary
# Library    Collections
# Library    DateTime
# Library    OperatingSystem

# *** Variables ***
# ${PERFORMANCE_THRESHOLD_LOAD}    3000    # 3 seconds
# ${PERFORMANCE_THRESHOLD_INTERACTIVE}    2000    # 2 seconds
# ${PERFORMANCE_THRESHOLD_PAINT}    1000    # 1 second

# *** Test Cases ***
# Website Performance Test
#     [Documentation]    Comprehensive website performance testing
#     [Tags]    performance    load-time    metrics
    
#     # Start performance monitoring
#     ${test_start}=    Get Current Date    result_format=epoch
    
#     Open Browser    ${TEST_URL}    chrome    options=add_argument("--enable-precise-memory-info")
    
#     # Wait for page to fully load
#     Wait Until Page Does Not Contain    Loading    timeout=30s
#     Sleep    2s    # Allow all resources to load
    
#     # Collect performance metrics
#     ${metrics}=    Collect Performance Metrics
    
#     # Validate performance thresholds
#     Validate Performance Thresholds    ${metrics}
    
#     # Test page interactions performance
#     Test Page Interaction Performance
    
#     # Generate performance report
#     Generate Performance Report    ${metrics}
    
#     Close Browser

# *** Keywords ***
# Collect Performance Metrics
#     [Documentation]    Collect comprehensive performance metrics
    
#     # Navigation timing metrics
#     ${navigation_timing}=    Execute Javascript    
#     ...    var timing = window.performance.timing;
#     ...    return {
#     ...        'dns_lookup': timing.domainLookupEnd - timing.domainLookupStart,
#     ...        'tcp_connect': timing.connectEnd - timing.connectStart,
#     ...        'request_response': timing.responseEnd - timing.requestStart,
#     ...        'dom_processing': timing.domComplete - timing.domLoading,
#     ...        'load_complete': timing.loadEventEnd - timing.navigationStart,
#     ...        'dom_ready': timing.domContentLoadedEventEnd - timing.navigationStart,
#     ...        'first_paint': timing.responseStart - timing.navigationStart
#     ...    };
    
#     # Paint timing metrics (if supported)
#     ${paint_timing}=    Execute Javascript    
#     ...    if ('getEntriesByType' in window.performance) {
#     ...        var paints = window.performance.getEntriesByType('paint');
#     ...        var result = {};
#     ...        paints.forEach(function(paint) {
#     ...            result[paint.name.replace('-', '_')] = paint.startTime;
#     ...        });
#     ...        return result;
#     ...    }
#     ...    return {};
    
#     # Memory usage (if supported)
#     ${memory_info}=    Execute Javascript    
#     ...    if ('memory' in window.performance) {
#     ...        return {
#     ...            'used_js_heap': window.performance.memory.usedJSHeapSize,
#     ...            'total_js_heap': window.performance.memory.totalJSHeapSize,
#     ...            'heap_limit': window.performance.memory.jsHeapSizeLimit
#     ...        };
#     ...    }
#     ...    return {};
    
#     # Resource timing
#     ${resource_count}=    Execute Javascript    
#     ...    if ('getEntriesByType' in window.performance) {
#     ...        var resources = window.performance.getEntriesByType('resource');
#     ...        var types = {};
#     ...        resources.forEach(function(resource) {
#     ...            var type = resource.initiatorType || 'other';
#     ...            types[type] = (types[type] || 0) + 1;
#     ...        });
#     ...        types['total'] = resources.length;
#     ...        return types;
#     ...    }
#     ...    return {};
    
#     # Combine all metrics
#     ${all_metrics}=    Create Dictionary
#     Set To Dictionary    ${all_metrics}    navigation=${navigation_timing}
#     Set To Dictionary    ${all_metrics}    paint=${paint_timing}
#     Set To Dictionary    ${all_metrics}    memory=${memory_info}
#     Set To Dictionary    ${all_metrics}    resources=${resource_count}
    
#     [Return]    ${all_metrics}

# Validate Performance Thresholds
#     [Documentation]    Validate performance against thresholds
#     [Arguments]    ${metrics}
    
#     ${navigation}=    Get From Dictionary    ${metrics}    navigation
    
#     # Check load time
#     ${load_time}=    Get From Dictionary    ${navigation}    load_complete
#     Should Be True    ${load_time} < ${PERFORMANCE_THRESHOLD_LOAD}    
#     ...    Page load time (${load_time}ms) exceeds threshold (${PERFORMANCE_THRESHOLD_LOAD}ms)
    
#     # Check DOM ready time
#     ${dom_ready}=    Get From Dictionary    ${navigation}    dom_ready
#     Should Be True    ${dom_ready} < ${PERFORMANCE_THRESHOLD_INTERACTIVE}    
#     ...    DOM ready time (${dom_ready}ms) exceeds threshold (${PERFORMANCE_THRESHOLD_INTERACTIVE}ms)
    
#     # Check first paint time (if available)
#     ${paint}=    Get From Dictionary    ${metrics}    paint
#     ${has_first_paint}=    Run Keyword And Return Status    Dictionary Should Contain Key    ${paint}    first_paint
#     IF    ${has_first_paint}
#         ${first_paint}=    Get From Dictionary    ${paint}    first_paint
#         Should Be True    ${first_paint} < ${PERFORMANCE_THRESHOLD_PAINT}    
#         ...    First paint time (${first_paint}ms) exceeds threshold (${PERFORMANCE_THRESHOLD_PAINT}ms)
#     END

# Test Page Interaction Performance
#     [Documentation]    Test performance of page interactions
    
#     # Test scroll performance
#     ${scroll_start}=    Get Time    epoch
#     Execute Javascript    window.scrollTo(0, document.body.scrollHeight);
#     Sleep    0.5s
#     Execute Javascript    window.scrollTo(0, 0);
#     ${scroll_end}=    Get Time    epoch
#     ${scroll_time}=    Evaluate    (${scroll_end} - ${scroll_start}) * 1000
    
#     Log    Scroll performance: ${scroll_time}ms
#     Should Be True    ${scroll_time} < 500    Scroll should be smooth (< 500ms)
    
#     # Test click response time (if interactive elements exist)
#     ${buttons}=    Get WebElements    css=button, input[type="submit"], .btn
#     ${button_count}=    Get Length    ${buttons}
    
#     IF    ${button_count} > 0
#         ${button}=    Get From List    ${buttons}    0
#         ${click_start}=    Get Time    epoch
#         Click Element    ${button}
#         Sleep    0.1s    # Small delay to register interaction
#         ${click_end}=    Get Time    epoch
#         ${click_time}=    Evaluate    (${click_end} - ${click_start}) * 1000
        
#         Log    Click response time: ${click_time}ms
#         Should Be True    ${click_time} < 200    Click response should be immediate (< 200ms)
#     END

# Generate Performance Report
#     [Documentation]    Generate detailed performance report
#     [Arguments]    ${metrics}
    
#     ${timestamp}=    Get Current Date    result_format=%Y-%m-%d_%H-%M-%S
#     ${report_file}=    Set Variable    performance_report_${timestamp}.txt
    
#     ${navigation}=    Get From Dictionary    ${metrics}    navigation
#     ${resources}=    Get From Dictionary    ${metrics}    resources
    
#     ${report_content}=    Catenate    SEPARATOR=\n
#     ...    PERFORMANCE TEST REPORT
#     ...    =========================
#     ...    Test URL: ${TEST_URL}
#     ...    Test Time: ${timestamp}
#     ...    
#     ...    NAVIGATION TIMING:
#     ...    - DNS Lookup: ${navigation}[dns_lookup]ms
#     ...    - TCP Connect: ${navigation}[tcp_connect]ms
#     ...    - Request/Response: ${navigation}[request_response]ms
#     ...    - DOM Processing: ${navigation}[dom_processing]ms
#     ...    - Page Load Complete: ${navigation}[load_complete]ms
#     ...    - DOM Ready: ${navigation}[dom_ready]ms
#     ...    
#     ...    RESOURCE LOADING:
#     ...    - Total Resources: ${resources}[total] if 'total' in ${resources} else 'N/A'
#     ...    
#     ...    PERFORMANCE THRESHOLDS:
#     ...    - Load Time Threshold: ${PERFORMANCE_THRESHOLD_LOAD}ms
#     ...    - Interactive Threshold: ${PERFORMANCE_THRESHOLD_INTERACTIVE}ms
#     ...    - Paint Threshold: ${PERFORMANCE_THRESHOLD_PAINT}ms
    
#     Create File    ${report_file}    ${report_content}
#     Log    Performance report saved to: ${report_file}

#     Performance Comparison Test
#     [Documentation]    Compare performance across multiple test runs
#     [Arguments]    ${test_iterations}=3
    
#     @{all_results}=    Create List
    
#     FOR    ${iteration}    IN RANGE    1    ${test_iterations + 1}
#         Log    Running performance test iteration ${iteration}
        
#         Open Browser    ${TEST_URL}    chrome
#         Sleep    2s
        
#         ${metrics}=    Collect Performance Metrics
#         Append To List    ${all_results}    ${metrics}
        
#         Close Browser
#         Sleep    5s    # Wait between tests
#     END
    
#     # Calculate average performance
#     ${avg_metrics}=    Calculate Average Performance    ${all_results}
#     Log    Average performance across ${test_iterations} runs: ${avg_metrics}

# Calculate Average Performance
#     [Documentation]    Calculate average performance from multiple test runs
#     [Arguments]    ${results_list}
    
#     ${total_load}=    Set Variable    0
#     ${total_dom}=    Set Variable    0
#     ${count}=    Get Length    ${results_list}
    
#     FOR    ${result}    IN    @{results_list}
#         ${navigation}=    Get From Dictionary    ${result}    navigation
#         ${load_time}=    Get From Dictionary    ${navigation}    load_complete
#         ${dom_time}=    Get From Dictionary    ${navigation}    dom_ready
        
#         ${total_load}=    Evaluate    ${total_load} + ${load_time}
#         ${total_dom}=    Evaluate    ${total_dom} + ${dom_time}
#     END
    
#     ${avg_load}=    Evaluate    ${total_load} / ${count}
#     ${avg_dom}=    Evaluate    ${total_dom} / ${count}
    
#     ${averages}=    Create Dictionary    avg_load_time=${avg_load}    avg_dom_ready=${avg_dom}
#     [Return]    ${averages}
# """

# @mcp.tool()
# def create_data_driven_test(test_data_file: str = "test_data.csv") -> str:
#     """Generate Robot Framework data-driven test template code. Returns .robot file content as text - does not execute."""
#     template = f"""*** Settings ***
# Library    SeleniumLibrary
# Library    DataDriver    {test_data_file}    encoding=utf-8
# Test Template    Login Test Template

# *** Variables ***
# ${{BROWSER}}        Chrome
# ${{BASE_URL}}       https://www.appurl.com

# *** Test Cases ***
# Login Test With ${{username}} And ${{password}}
#     [Tags]    data-driven    login
#     # Test case will be generated for each row in CSV

# *** Keywords ***
# Login Test Template
#     [Arguments]    ${{username}}    ${{password}}    ${{expected_result}}
#     [Documentation]    Template for data-driven login tests
    
#     Open Browser    ${{BASE_URL}}    ${{BROWSER}}
#     Maximize Browser Window
    
#     Input Text    id=user-name    ${{username}}
#     Input Text    id=password    ${{password}}
#     Click Button    id=login-button
    
#     Run Keyword If    '${{expected_result}}' == 'success'
#     ...    Wait Until Page Contains Element    xpath=//span[@class='title']    10s
#     ...    ELSE
#     ...    Wait Until Page Contains Element    xpath=//h3[@data-test='error']    10s
    
#     [Teardown]    Close Browser

# *** Comments ***
# # Create {test_data_file} with columns: username,password,expected_result
# # Example CSV content:
# # username,password,expected_result
# # standard_user,secret_sauce,success
# # locked_out_user,secret_sauce,error
# # invalid_user,wrong_password,error
# """
#     return template

# @mcp.tool()
# def create_api_integration_test(base_url: str, endpoint: str, method: str = "GET") -> str:
#     """Generate Robot Framework API integration test code. Returns .robot file content as text - does not execute."""
#     try:
#         validated_url = InputValidator.validate_url(base_url)
        
#         template = Template("""*** Settings ***
# Library    SeleniumLibrary
# Library    RequestsLibrary
# Library    Collections

# *** Variables ***
# $${BASE_URL}         $base_url
# $${API_ENDPOINT}     $endpoint
# $${BROWSER}          Chrome

# *** Test Cases ***
# API UI Integration Test
#     [Documentation]    Test API and UI integration
#     [Tags]    integration    api    ui
    
#     # API Setup and Validation
#     Create Session    api_session    $${BASE_URL}
#     $${api_response}=    GET On Session    api_session    $${API_ENDPOINT}
#     Status Should Be    200    $${api_response}
#     $${response_data}=    Set Variable    $${api_response.json()}
    
#     # UI Validation based on API data
#     Open Browser    $${BASE_URL}    $${BROWSER}
#     Maximize Browser Window
    
#     # Validate UI reflects API data
#     Wait Until Page Contains    $${response_data['title']}    10s
#     Page Should Contain    $${response_data['description']}
    
#     [Teardown]    Run Keywords
#     ...    Close Browser    AND
#     ...    Delete All Sessions

# *** Keywords ***
# Validate API Response Structure
#     [Arguments]    $${response}
#     [Documentation]    Validate API response has required fields
#     Dictionary Should Contain Key    $${response}    id
#     Dictionary Should Contain Key    $${response}    title
#     Dictionary Should Contain Key    $${response}    description
# """)
        
#         return template.substitute(
#             base_url=validated_url,
#             endpoint=endpoint,
#             method=method.upper()
#         )
        
#     except ValidationError as e:
#         return f"# VALIDATION ERROR: {str(e)}\n# Please correct the input and try again."
#     except Exception as e:
#         return f"# UNEXPECTED ERROR: {str(e)}\n# Please contact support."

# @mcp.tool()
# def validate_robot_framework_syntax(robot_code: str) -> str:
#     """Validate Robot Framework syntax and provide suggestions. Returns validation report as text - does not execute code."""
#     try:
#         lines = robot_code.split('\n')
#         errors = []
#         warnings = []
        
#         # Check for basic syntax issues
#         for i, line in enumerate(lines, 1):
#             line_stripped = line.strip()
#             if not line_stripped or line_stripped.startswith('#'):
#                 continue
                
#             # Check for proper section headers
#             if line_stripped.startswith('***') and not line_stripped.endswith('***'):
#                 errors.append(f"Line {i}: Section header must end with '***'")
            
#             # Check for proper variable syntax - should be ${variable} not ${{variable}}
#             if '${{' in line and '}}' in line:
#                 warnings.append(f"Line {i}: Use ${{variable}} syntax instead of ${{{{variable}}}}")
            
#             # Check for unclosed variable syntax
#             if '${' in line and '}' not in line:
#                 errors.append(f"Line {i}: Unclosed variable syntax")
            
#             # Check for proper spacing in variables section
#             if line_stripped.startswith('${') and '    ' not in line:
#                 warnings.append(f"Line {i}: Variables should use 4 spaces between name and value")
        
#         result = "# ROBOT FRAMEWORK SYNTAX VALIDATION\n\n"
        
#         if errors:
#             result += "## ERRORS (Must Fix):\n"
#             result += '\n'.join(f"- {error}" for error in errors) + "\n\n"
        
#         if warnings:
#             result += "## WARNINGS (Recommended Fixes):\n"
#             result += '\n'.join(f"- {warning}" for warning in warnings) + "\n\n"
        
#         if not errors and not warnings:
#             result += "✅ VALIDATION PASSED: No syntax errors found\n"
#         elif not errors:
#             result += "⚠️  VALIDATION PASSED WITH WARNINGS: No critical errors, but consider fixing warnings\n"
#         else:
#             result += "❌ VALIDATION FAILED: Critical errors found that must be fixed\n"
        
#         return result
            
#     except Exception as e:
#         return f"# VALIDATION ERROR: {str(e)}"

# @mcp.tool()
# def open_browser_with_url(url: str, browser: str = "chrome") -> str:
#     """
#     ⚠️ TEXT ONLY - NO BROWSER EXECUTION! Generate Robot Framework test code to open a browser. To actually open browser, use execute_browser_navigation instead.
#     - Defaults to Chrome if browser is not provided
#     - Supports only Chrome and Firefox
#     - Returns .robot file content as text (does not execute)
#     """
#     try:
#         # Validate URL
#         validated_url = InputValidator.validate_url(url)

#         # Normalize browser input
#         browser = browser.strip().lower() if browser else "chrome"

#         # Allow only Chrome and Firefox
#         supported_browsers = {
#             "chrome": "Chrome",
#             "firefox": "Firefox"
#         }

#         if browser not in supported_browsers:
#             return (
#                 "# VALIDATION ERROR: Unsupported browser\n"
#                 "# Supported browsers are: Chrome, Firefox\n"
#                 "# Example usage: browser=Chrome or browser=Firefox"
#             )

#         selected_browser = supported_browsers[browser]

#         template = Template("""*** Settings ***
# Library    SeleniumLibrary

# *** Variables ***
# $${URL}        $url
# $${BROWSER}    $browser

# *** Test Cases ***
# Open Browser Test
#     [Documentation]    Open browser and navigate to URL
#     [Tags]    browser    navigation

#     Open Browser    $${URL}    $${BROWSER}
#     Maximize Browser Window

#     [Teardown]    Close Browser
# """)

#         return template.substitute(
#             url=validated_url,
#             browser=selected_browser
#         )

#     except ValidationError as e:
#         return f"# VALIDATION ERROR: {str(e)}\n# Please correct the input and try again."
#     except Exception as e:
#         return f"# UNEXPECTED ERROR: {str(e)}\n# Please contact support."


# def main():
#     """Entry point for the Robot Framework MCP server"""
#     import sys
    
#     # Only print startup messages if not in stdio mode
#     if len(sys.argv) > 1 and '--stdio' in sys.argv:
#         # Running in stdio mode (MCP client mode)
#         pass
#     else:
#         # Running in standalone mode
#         print("Starting Robot Framework MCP server...")
#         print("Available templates: appLocator, generic, bootstrap")
#         print("Features: Input validation, configurable selectors, syntax validation")
#         print("Advanced tools: API integration, data-driven testing, responsive testing")

#     try:
#         mcp.run()
#     except Exception as e:
#         if len(sys.argv) <= 1 or '--stdio' not in sys.argv:
#             print(f"Error starting Robot framework MCP server: {e}")
#             import traceback
#             traceback.print_exc()
#         raise

# if __name__ == "__main__":
#     main()


import os
from urllib.parse import urlparse
from pathlib import Path
from mcp.server.fastmcp import FastMCP
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.firefox.options import Options as FirefoxOptions

mcp = FastMCP("Robot Framework Hybrid MCP Server")

browser_instance = None


# ===============================
# ROBOT FRAMEWORK TEMPLATE
# ===============================

ADVANCED_KEYWORDS_TEMPLATE = """*** Settings ***
Library    SeleniumLibrary

*** Keywords ***
# Dropdown/Select Operations
Select Dropdown Option By Label
    [Documentation]    Select option from dropdown by visible text
    [Arguments]    ${locator}    ${label}
    Wait Until Element Is Visible    ${locator}    10s
    Select From List By Label    ${locator}    ${label}

Select Dropdown Option By Value
    [Documentation]    Select option from dropdown by value
    [Arguments]    ${locator}    ${value}
    Wait Until Element Is Visible    ${locator}    10s
    Select From List By Value    ${locator}    ${value}

# Checkbox Operations
Select Checkbox If Not Selected
    [Documentation]    Select checkbox only if it's not already selected
    [Arguments]    ${locator}
    Wait Until Element Is Visible    ${locator}    10s
    ${is_selected}=    Run Keyword And Return Status    Checkbox Should Be Selected    ${locator}
    Run Keyword If    not ${is_selected}    Select Checkbox    ${locator}

Unselect Checkbox If Selected
    [Documentation]    Unselect checkbox only if it's currently selected
    [Arguments]    ${locator}
    Wait Until Element Is Visible    ${locator}    10s
    ${is_selected}=    Run Keyword And Return Status    Checkbox Should Be Selected    ${locator}
    Run Keyword If    ${is_selected}    Unselect Checkbox    ${locator}

# File Upload Operations
Upload File To Element
    [Documentation]    Upload file using file input element
    [Arguments]    ${locator}    ${file_path}
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
    [Documentation]    Hover mouse over an element
    [Arguments]    ${locator}
    Wait Until Element Is Visible    ${locator}    10s
    Mouse Over    ${locator}

Double Click On Element
    [Documentation]    Double click on an element
    [Arguments]    ${locator}
    Wait Until Element Is Visible    ${locator}    10s
    Double Click Element    ${locator}

Right Click On Element
    [Documentation]    Right click on an element
    [Arguments]    ${locator}
    Wait Until Element Is Visible    ${locator}    10s
    Open Context Menu    ${locator}

# Scroll Operations
Scroll To Element
    [Documentation]    Scroll element into view
    [Arguments]    ${locator}
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
    [Documentation]    Execute custom JavaScript code
    [Arguments]    ${javascript_code}
    ${result}=    Execute JavaScript    ${javascript_code}
    RETURN    ${result}

Set Element Attribute
    [Documentation]    Set attribute value of an element using JavaScript
    [Arguments]    ${locator}    ${attribute}    ${value}
    Wait Until Element Is Visible    ${locator}    10s
    Execute JavaScript    arguments[0].setAttribute('${attribute}', '${value}');    ARGUMENTS    ${locator}

Get Element Attribute Value
    [Documentation]    Get attribute value of an element
    [Arguments]    ${locator}    ${attribute}
    Wait Until Element Is Visible    ${locator}    10s
    ${value}=    Get Element Attribute    ${locator}    ${attribute}
    RETURN    ${value}

# Advanced Wait Operations
Wait Until Element Contains Text
    [Documentation]    Wait until element contains specific text
    [Arguments]    ${locator}    ${expected_text}    ${timeout}=10s
    Wait Until Element Is Visible    ${locator}    ${timeout}
    Wait Until Element Contains    ${locator}    ${expected_text}    ${timeout}

Wait Until Page Title Contains
    [Documentation]    Wait until page title contains expected text
    [Arguments]    ${expected_title}    ${timeout}=10s
    Wait Until Title Contains    ${expected_title}    ${timeout}

Wait For Element To Disappear
    [Documentation]    Wait for element to disappear from page
    [Arguments]    ${locator}    ${timeout}=10s
    Wait Until Element Is Not Visible    ${locator}    ${timeout}

# Table Operations
Get Table Cell Text
    [Documentation]    Get text from specific table cell
    [Arguments]    ${table_locator}    ${row}    ${column}
    ${cell_text}=    Get Table Cell    ${table_locator}    ${row}    ${column}
    RETURN    ${cell_text}

Get Table Row Count
    [Documentation]    Get number of rows in table
    [Arguments]    ${table_locator}
    ${row_count}=    Get Element Count    ${table_locator}//tr
    RETURN    ${row_count}

# Form Validation
Verify Field Is Required
    [Documentation]    Verify field has required attribute
    [Arguments]    ${locator}
    ${is_required}=    Get Element Attribute    ${locator}    required
    Should Not Be Empty    ${is_required}    Field should be required

Verify Field Is Disabled
    [Documentation]    Verify field is disabled
    [Arguments]    ${locator}
    Element Should Be Disabled    ${locator}

Verify Field Is Enabled
    [Documentation]    Verify field is enabled
    [Arguments]    ${locator}
    Element Should Be Enabled    ${locator}
"""


# =============================
# SESSION MANAGEMENT
# =============================

def is_browser_alive(driver):
    """Check if selenium session is still alive"""
    try:
        driver.current_url
        return True
    except Exception:
        return False


def create_browser(browser="chrome"):
    """Create a fresh browser instance"""
    global browser_instance

    if browser.lower() == "chrome":
        options = Options()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        options.add_argument("--remote-allow-origins=*")
        driver = webdriver.Chrome(options=options)
    elif browser.lower() == "firefox":
        options = FirefoxOptions()
        driver = webdriver.Firefox(options=options)
    else:
        raise ValueError(f"Unsupported browser: {browser}")

    browser_instance = driver
    return driver


# =============================
# UTILITY FUNCTIONS
# =============================

def validate_url(url):
    """Validate and clean URL"""
    if not url:
        raise ValueError("URL cannot be empty")

    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url

    result = urlparse(url)
    if not result.netloc:
        raise ValueError(f"Invalid URL: {url}")

    return url


def validate_file_path(filepath):
    """Validate and clean file path"""
    if not filepath:
        raise ValueError("File path cannot be empty")

    # Remove any potentially dangerous characters
    filepath = filepath.replace('..', '').replace('//', '/')

    return filepath


def extract_locators_from_page(url, driver):
    """Auto-detect locators from a web page"""
    driver.get(url)

    locators = []

    # Find all input fields
    inputs = driver.find_elements(By.TAG_NAME, "input")
    for inp in inputs:
        inp_id = inp.get_attribute("id")
        inp_name = inp.get_attribute("name")
        inp_type = inp.get_attribute("type")
        inp_class = inp.get_attribute("class")

        if inp_id:
            locators.append({
                "type": inp_type or "text",
                "locator": f"id={inp_id}",
                "variable_name": inp_id.upper().replace("-", "_").replace(" ", "_")
            })
        elif inp_name:
            locators.append({
                "type": inp_type or "text",
                "locator": f"name={inp_name}",
                "variable_name": inp_name.upper().replace("-", "_").replace(" ", "_")
            })

    # Find all buttons
    buttons = driver.find_elements(By.TAG_NAME, "button")
    for btn in buttons:
        btn_id = btn.get_attribute("id")
        btn_text = btn.text.strip()
        btn_class = btn.get_attribute("class")

        if btn_id:
            locators.append({
                "type": "button",
                "locator": f"id={btn_id}",
                "variable_name": btn_id.upper().replace("-", "_").replace(" ", "_")
            })
        elif btn_text:
            safe_name = btn_text.upper().replace(" ", "_").replace("-", "_")
            locators.append({
                "type": "button",
                "locator": f"xpath=//button[contains(text(),'{btn_text}')]",
                "variable_name": f"{safe_name}_BUTTON"
            })

    # Find all links
    links = driver.find_elements(By.TAG_NAME, "a")
    for link in links:
        link_id = link.get_attribute("id")
        link_text = link.text.strip()

        if link_id:
            locators.append({
                "type": "link",
                "locator": f"id={link_id}",
                "variable_name": link_id.upper().replace("-", "_").replace(" ", "_")
            })
        elif link_text and len(link_text) < 50:
            safe_name = link_text.upper().replace(" ", "_").replace("-", "_")[:30]
            locators.append({
                "type": "link",
                "locator": f"link={link_text}",
                "variable_name": f"{safe_name}_LINK"
            })

    return locators


def sanitize_filename(name):
    """Convert text to valid filename"""
    # Remove special characters and replace spaces with underscores
    name = name.lower().strip()
    name = ''.join(c if c.isalnum() or c in (' ', '_') else '' for c in name)
    name = name.replace(' ', '_')
    return name


@mcp.tool()
def generate_test_with_pom(
    test_name: str,
    url: str,
    pages: list[dict],
    test_steps: list[str] = None,
    output_dir: str = "robot_tests",
    append_to_existing: bool = True,
    test_file_name: str = None,
    tags: list[str] = None
) -> dict:
    """
    Generate Robot Framework test with Page Object Model structure.
    
    Args:
        test_name: Name of the test case (e.g., "Login Test")
        url: Target website URL
        pages: List of page objects with structure:
            [
                {
                    "name": "LoginPage",
                    "locators": [
                        {"name": "USERNAME_FIELD", "value": "id=username", "description": "Username input field"},
                        {"name": "PASSWORD_FIELD", "value": "id=password", "description": "Password input field"}
                    ],
                    "keywords": [
                        {
                            "name": "Login With Credentials",
                            "args": ["${username}", "${password}"],
                            "steps": [
                                "Input Text    ${USERNAME_FIELD}    ${username}",
                                "Input Text    ${PASSWORD_FIELD}    ${password}",
                                "Click Element    ${LOGIN_BUTTON}"
                            ],
                            "doc": "Login with provided username and password"
                        }
                    ]
                }
            ]
        test_steps: List of actual test steps to include in the test case (e.g., ["Login With Credentials    standard_user    secret_sauce", "Verify Login Successful"])
        output_dir: Directory where files will be generated
        append_to_existing: If True, add test case to existing test file instead of creating new file
        test_file_name: Specific test file name to use (optional, auto-generated from URL if not provided)
        tags: List of tags for the test case (default: ["smoke"])
    
    Returns:
        Dictionary with file paths and generation status
    """
    try:
        validated_url = validate_url(url)
        
        # Create directory structure
        # pages folder is OUTSIDE of tests folder
        base_path = Path(output_dir)
        pages_dir = base_path / "pages"
        tests_dir = base_path / "tests"
        
        pages_dir.mkdir(parents=True, exist_ok=True)
        tests_dir.mkdir(parents=True, exist_ok=True)
        
        generated_files = []
        page_imports = []
        updated_pages = []
        
        # Generate or update page object files (.robot files, NOT .resource)
        for page in pages:
            page_name = page["name"]
            safe_page_name = sanitize_filename(page_name)
            page_file = pages_dir / f"{safe_page_name}.robot"
            
            # Check if page file already exists
            if page_file.exists() and append_to_existing:
                # Read existing content
                with open(page_file, 'r', encoding='utf-8') as f:
                    existing_content = f.read()
                
                # Parse existing variables and keywords
                existing_vars = set()
                existing_keywords = set()
                
                in_vars = False
                in_keywords = False
                for line in existing_content.split('\n'):
                    if '*** Variables ***' in line:
                        in_vars = True
                        in_keywords = False
                    elif '*** Keywords ***' in line:
                        in_vars = False
                        in_keywords = True
                    elif in_vars and line.strip().startswith('${'):
                        var_name = line.split('}')[0].split('{')[1]
                        existing_vars.add(var_name)
                    elif in_keywords and line.strip() and not line.startswith('    ') and not line.startswith('#'):
                        existing_keywords.add(line.strip())
                
                # Build updated content - only add NEW locators and keywords
                page_content = existing_content.rstrip() + "\n"
                
                # Add new locators if any
                new_locators = []
                if "locators" in page:
                    for loc in page["locators"]:
                        loc_name = loc["name"]
                        if loc_name not in existing_vars:
                            new_locators.append(loc)
                
                if new_locators:
                    # Find the position after *** Variables *** section
                    vars_section_end = existing_content.find("*** Keywords ***")
                    if vars_section_end > 0:
                        before_keywords = existing_content[:vars_section_end]
                        after_keywords = existing_content[vars_section_end:]
                        
                        new_vars_content = ""
                        for loc in new_locators:
                            loc_name = loc["name"]
                            loc_value = loc["value"]
                            loc_desc = loc.get("description", "")
                            if loc_desc:
                                new_vars_content += f"# {loc_desc}\n"
                            new_vars_content += f"${{{loc_name}}}    {loc_value}\n"
                        
                        page_content = before_keywords + new_vars_content + "\n" + after_keywords
                
                # Add new keywords if any
                if "keywords" in page:
                    for kw in page["keywords"]:
                        kw_name = kw["name"]
                        if kw_name not in existing_keywords:
                            kw_doc = kw.get("doc", "")
                            kw_args = kw.get("args", [])
                            kw_steps = kw.get("steps", [])
                            
                            page_content += f"\n{kw_name}\n"
                            
                            if kw_doc:
                                page_content += f"    [Documentation]    {kw_doc}\n"
                            
                            if kw_args:
                                args_str = "    ".join(kw_args)
                                page_content += f"    [Arguments]    {args_str}\n"
                            
                            for step in kw_steps:
                                page_content += f"    {step}\n"
                
                updated_pages.append(page_name)
            else:
                # Create new page file
                page_content = f"""*** Settings ***
Library    SeleniumLibrary

*** Variables ***
"""
                
                # Add all locators at the TOP (not in the middle)
                if "locators" in page:
                    for loc in page["locators"]:
                        loc_name = loc["name"]
                        loc_value = loc["value"]
                        loc_desc = loc.get("description", "")
                        if loc_desc:
                            page_content += f"# {loc_desc}\n"
                        page_content += f"${{{loc_name}}}    {loc_value}\n"
                
                page_content += "\n*** Keywords ***\n"
                
                # Add keywords with proper [Documentation] indentation
                if "keywords" in page:
                    for kw in page["keywords"]:
                        kw_name = kw["name"]
                        kw_doc = kw.get("doc", "")
                        kw_args = kw.get("args", [])
                        kw_steps = kw.get("steps", [])
                        
                        page_content += f"{kw_name}\n"
                        
                        # Proper [Documentation] with 4-space indentation
                        if kw_doc:
                            page_content += f"    [Documentation]    {kw_doc}\n"
                        
                        # Add [Arguments] if present
                        if kw_args:
                            args_str = "    ".join(kw_args)
                            page_content += f"    [Arguments]    {args_str}\n"
                        
                        # Add steps
                        for step in kw_steps:
                            page_content += f"    {step}\n"
                        
                        page_content += "\n"
            
            # Write page file
            with open(page_file, 'w', encoding='utf-8') as f:
                f.write(page_content)
            
            generated_files.append(str(page_file))
            page_imports.append(f"Resource    ../pages/{safe_page_name}.robot")
        
        # Determine test file name
        if test_file_name is None:
            existing_tests = list(tests_dir.glob("*.robot"))
            
            if len(existing_tests) == 1:
                # If only one test file exists, reuse it
                test_file = existing_tests[0]
                test_file_name = test_file.stem
            else:
                parsed_url = urlparse(validated_url)
                domain = parsed_url.netloc.replace('www.', '').split('.')[0]
                test_file_name = f"{domain}_test"
        
        test_file_name = sanitize_filename(test_file_name)
        test_file = tests_dir / f"{test_file_name}.robot"
        
        # Check if test file exists and we should append
        if test_file.exists() and append_to_existing:
            # Read existing test file
            with open(test_file, 'r', encoding='utf-8') as f:
                existing_test_content = f.read()
            
            # Check if we need to add new page imports
            test_content = existing_test_content
            for imp in page_imports:
                if imp not in existing_test_content:
                    # Find where to insert (after existing Resource imports or after Library line)
                    if "Resource    " in existing_test_content:
                        lines = existing_test_content.split('\n')
                        insert_pos = 0
                        for i, line in enumerate(lines):
                            if line.startswith("Resource    "):
                                insert_pos = i + 1
                        lines.insert(insert_pos, imp)
                        test_content = '\n'.join(lines)
                    else:
                        # Insert after Library line
                        test_content = existing_test_content.replace(
                            "Library    SeleniumLibrary",
                            f"Library    SeleniumLibrary\n{imp}"
                        )
            
            # Check if test case already exists
            if f"*** Test Cases ***" in test_content and test_name not in test_content:
                # Build the test case
                tags_list = tags if tags else ["smoke"]
                tags_str = "    ".join(tags_list)
                
                test_case_content = f"""
{test_name}
    [Documentation]    Automated test for {test_name}
    [Tags]    {tags_str}
    Open Browser    ${{URL}}    ${{BROWSER}}
    Maximize Browser Window
"""
                
                # Add actual test steps if provided
                if test_steps and len(test_steps) > 0:
                    for step in test_steps:
                        test_case_content += f"    {step}\n"
                else:
                    test_case_content += "    # Add your test steps here\n"
                
                test_case_content += "    Close Browser\n"
                
                # Append new test case
                test_content = test_content.rstrip() + "\n" + test_case_content
            elif test_name in test_content:
                # Test case already exists - check if we should update it
                if test_steps and len(test_steps) > 0:
                    # Find and replace the test case with updated steps
                    import re
                    # Pattern to match the test case
                    pattern = rf"({re.escape(test_name)}\s+\[Documentation\].*?\n(?:.*?\n)*?)(\s+Close Browser)"
                    
                    # Build replacement with new steps
                    tags_list = tags if tags else ["smoke"]
                    tags_str = "    ".join(tags_list)
                    
                    replacement = f"""{test_name}
    [Documentation]    Automated test for {test_name}
    [Tags]    {tags_str}
    Open Browser    ${{URL}}    ${{BROWSER}}
    Maximize Browser Window
"""
                    for step in test_steps:
                        replacement += f"    {step}\n"
                    replacement += "    Close Browser"
                    
                    # Try to replace
                    new_content = re.sub(pattern, replacement, test_content, flags=re.DOTALL)
                    if new_content != test_content:
                        test_content = new_content
        else:
            # Create new test file
            test_content = f"""*** Settings ***
Documentation    Test Suite for {validated_url}
Library    SeleniumLibrary
"""
            
            # Add page imports
            for imp in page_imports:
                test_content += f"{imp}\n"
            
            test_content += f"""
*** Variables ***
${{URL}}    {validated_url}
${{BROWSER}}    chrome

*** Test Cases ***
"""
            
            # Add the test case
            tags_list = tags if tags else ["smoke"]
            tags_str = "    ".join(tags_list)
            
            test_content += f"""{test_name}
    [Documentation]    Automated test for {test_name}
    [Tags]    {tags_str}
    Open Browser    ${{URL}}    ${{BROWSER}}
    Maximize Browser Window
"""
            
            # Add actual test steps if provided
            if test_steps and len(test_steps) > 0:
                for step in test_steps:
                    test_content += f"    {step}\n"
            else:
                test_content += "    # Add your test steps here\n"
            
            test_content += "    Close Browser\n"
        
        # Write test file
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        generated_files.append(str(test_file))
        
        message = f"Generated POM test structure with {len(pages)} page objects"
        if updated_pages:
            message += f". Updated existing pages: {', '.join(updated_pages)}"
        
        return {
            "status": "success",
            "action": "generate_test_with_pom",
            "test_name": test_name,
            "url": validated_url,
            "generated_files": generated_files,
            "test_file": str(test_file),
            "structure": {
                "pages_dir": str(pages_dir),
                "tests_dir": str(tests_dir)
            },
            "message": message
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}


@mcp.tool()
def inspect_page_and_generate_pom(
    url: str,
    output_dir: str = "robot_tests",
    browser: str = "chrome",
    actually_inspect: bool = False
) -> dict:
    """
    Inspect a web page and auto-generate Page Object Model with proper locators.
    NOTE: This tool only opens a browser if actually_inspect=True. 
    For just creating test structure without inspection, use generate_test_with_pom instead.
    
    Args:
        url: URL to inspect
        output_dir: Output directory for generated files
        browser: Browser to use (chrome/firefox)
        actually_inspect: If True, opens browser to inspect page. If False, just creates test structure.
    
    Returns:
        Dictionary with detected elements and generated files
    """
    global browser_instance
    
    try:
        validated_url = validate_url(url)
        
        if actually_inspect:
            # Create or reuse browser
            if browser_instance is None or not is_browser_alive(browser_instance):
                driver = create_browser(browser)
            else:
                driver = browser_instance
            
            # Extract locators
            locators = extract_locators_from_page(validated_url, driver)
            
            # Determine page name from URL
            parsed_url = urlparse(validated_url)
            page_name = parsed_url.path.strip('/').split('/')[-1] or 'HomePage'
            page_name = ''.join(word.capitalize() for word in page_name.replace('-', ' ').replace('_', ' ').split())
            if not page_name.endswith('Page'):
                page_name += 'Page'
            
            # Build page structure with EXACT locator names matching the page
            page_locators = []
            for loc in locators:
                page_locators.append({
                    "name": loc["variable_name"],
                    "value": loc["locator"],
                    "description": f"{loc['type'].capitalize()} element"
                })
            
            # Generate POM structure
            pages = [{
                "name": page_name,
                "locators": page_locators,
                "keywords": []
            }]
            
            result = generate_test_with_pom(
                test_name=f"Test {page_name}",
                url=validated_url,
                pages=pages,
                output_dir=output_dir
            )
            
            result["detected_elements"] = len(locators)
            result["page_name"] = page_name
        else:
            # Just create basic structure without inspection
            parsed_url = urlparse(validated_url)
            page_name = parsed_url.path.strip('/').split('/')[-1] or 'HomePage'
            page_name = ''.join(word.capitalize() for word in page_name.replace('-', ' ').replace('_', ' ').split())
            if not page_name.endswith('Page'):
                page_name += 'Page'
            
            result = {
                "status": "info",
                "message": "Use generate_test_with_pom for creating test structure without browser inspection",
                "page_name": page_name,
                "url": validated_url
            }
        
        return result
        
    except Exception as e:
        return {"status": "error", "message": str(e)}


@mcp.tool()
def navigate_to(url: str, browser: str = "chrome") -> dict:
    """
    Navigate to a URL using Selenium WebDriver.
    
    Args:
        url: Target URL
        browser: Browser type (chrome/firefox)
    
    Returns:
        Navigation status and page information
    """
    global browser_instance
    
    try:
        validated_url = validate_url(url)
        
        # Create or reuse browser
        if browser_instance is None or not is_browser_alive(browser_instance):
            driver = create_browser(browser)
        else:
            driver = browser_instance
        
        driver.get(validated_url)
        
        # Get page info
        title = driver.title
        current_url = driver.current_url
        
        return {
            "status": "success",
            "action": "navigate",
            "url": current_url,
            "title": title,
            "message": f"Successfully navigated to {current_url}"
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}


@mcp.tool()
def find_element(
    locator_type: str,
    locator_value: str,
    get_attributes: bool = True
) -> dict:
    """
    Find element on current page and return its properties.
    
    Args:
        locator_type: Type of locator (id, name, xpath, css, class, tag, link_text)
        locator_value: Locator value
        get_attributes: Whether to fetch element attributes
    
    Returns:
        Element information
    """
    global browser_instance
    
    try:
        if browser_instance is None or not is_browser_alive(browser_instance):
            return {"status": "error", "message": "No active browser session"}
        
        # Map locator type to Selenium By type
        by_map = {
            "id": By.ID,
            "name": By.NAME,
            "xpath": By.XPATH,
            "css": By.CSS_SELECTOR,
            "class": By.CLASS_NAME,
            "tag": By.TAG_NAME,
            "link_text": By.LINK_TEXT,
            "partial_link": By.PARTIAL_LINK_TEXT
        }
        
        if locator_type.lower() not in by_map:
            return {"status": "error", "message": f"Invalid locator type: {locator_type}"}
        
        by_type = by_map[locator_type.lower()]
        element = browser_instance.find_element(by_type, locator_value)
        
        result = {
            "status": "success",
            "found": True,
            "visible": element.is_displayed(),
            "enabled": element.is_enabled(),
            "tag_name": element.tag_name,
            "text": element.text
        }
        
        if get_attributes:
            result["attributes"] = {
                "id": element.get_attribute("id"),
                "name": element.get_attribute("name"),
                "class": element.get_attribute("class"),
                "type": element.get_attribute("type"),
                "value": element.get_attribute("value")
            }
        
        return result
        
    except Exception as e:
        return {"status": "error", "found": False, "message": str(e)}


@mcp.tool()
def click_element(locator_type: str, locator_value: str) -> dict:
    """
    Click on an element.
    
    Args:
        locator_type: Type of locator (id, name, xpath, css, etc.)
        locator_value: Locator value
    
    Returns:
        Click action status
    """
    global browser_instance
    
    try:
        if browser_instance is None or not is_browser_alive(browser_instance):
            return {"status": "error", "message": "No active browser session"}
        
        by_map = {
            "id": By.ID,
            "name": By.NAME,
            "xpath": By.XPATH,
            "css": By.CSS_SELECTOR,
            "class": By.CLASS_NAME,
            "tag": By.TAG_NAME,
            "link_text": By.LINK_TEXT
        }
        
        by_type = by_map[locator_type.lower()]
        element = browser_instance.find_element(by_type, locator_value)
        element.click()
        
        return {
            "status": "success",
            "action": "click",
            "message": f"Successfully clicked element: {locator_type}={locator_value}"
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}


@mcp.tool()
def input_text(locator_type: str, locator_value: str, text: str) -> dict:
    """
    Input text into an element.
    
    Args:
        locator_type: Type of locator
        locator_value: Locator value
        text: Text to input
    
    Returns:
        Input action status
    """
    global browser_instance
    
    try:
        if browser_instance is None or not is_browser_alive(browser_instance):
            return {"status": "error", "message": "No active browser session"}
        
        by_map = {
            "id": By.ID,
            "name": By.NAME,
            "xpath": By.XPATH,
            "css": By.CSS_SELECTOR
        }
        
        by_type = by_map[locator_type.lower()]
        element = browser_instance.find_element(by_type, locator_value)
        element.clear()
        element.send_keys(text)
        
        return {
            "status": "success",
            "action": "input_text",
            "message": f"Successfully input text into: {locator_type}={locator_value}"
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}


@mcp.tool()
def close_browser() -> dict:
    """
    Close the browser session.
    
    Returns:
        Close action status
    """
    global browser_instance
    
    try:
        if browser_instance and is_browser_alive(browser_instance):
            browser_instance.quit()
            browser_instance = None
            return {"status": "success", "message": "Browser closed"}
        else:
            return {"status": "info", "message": "No active browser to close"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@mcp.tool()
def generate_basic_test(
    test_name: str,
    url: str,
    test_steps: list[str],
    output_file: str = "test.robot",
    output_dir: str = "robot_tests"
) -> dict:
    """
    Generate a basic Robot Framework test file.
    
    Args:
        test_name: Name of the test case
        url: Target URL
        test_steps: List of test steps in Robot Framework syntax
        output_file: Output filename
        output_dir: Output directory
    
    Returns:
        Generation status and file path
    """
    try:
        validated_url = validate_url(url)
        validated_output = validate_file_path(output_file)
        
        # Ensure .robot extension
        if not validated_output.endswith('.robot'):
            validated_output = validated_output.rsplit('.', 1)[0] + '.robot'
        
        # Create test content
        template = f"""*** Settings ***
Documentation    {test_name}
Library    SeleniumLibrary

*** Variables ***
${{URL}}    {validated_url}
${{BROWSER}}    chrome

*** Test Cases ***
{test_name}
    [Documentation]    Automated test case for {test_name}
    [Tags]    smoke
    Open Browser    ${{URL}}    ${{BROWSER}}
    Maximize Browser Window
"""
        
        # Add test steps with proper indentation
        for step in test_steps:
            template += f"    {step}\n"
        
        template += "    Close Browser\n"
        
        # Write file
        full_path = Path(output_dir) / validated_output
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(template)
        
        return {
            "status": "success",
            "action": "generate_basic_test",
            "file_path": str(full_path),
            "test_name": test_name,
            "url": validated_url,
            "message": f"Test file created at {full_path}"
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}


@mcp.tool()
def generate_advanced_keywords(
    output_file: str = "advanced_keywords.robot",
    output_dir: str = "robot_tests/keywords"
) -> dict:
    """
    Generate a library of advanced reusable Robot Framework keywords.
    
    Args:
        output_file: Output filename
        output_dir: Output directory
    
    Returns:
        Generation status and file path
    """
    try:
        validated_output = validate_file_path(output_file)
        
        # Ensure .robot extension
        if not validated_output.endswith('.robot'):
            validated_output = validated_output.rsplit('.', 1)[0] + '.robot'
        
        # Write file
        full_path = Path(output_dir) / validated_output
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(ADVANCED_KEYWORDS_TEMPLATE)
        
        return {
            "status": "success",
            "action": "generate_advanced_keywords",
            "file_path": str(full_path),
            "message": f"Advanced keywords library created at {full_path}"
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}


@mcp.tool()
def generate_data_driven_test(
    test_name: str,
    url: str,
    template_steps: list[str],
    test_data: list[dict],
    output_file: str = "data_driven_test.robot",
    output_dir: str = "robot_tests"
) -> dict:
    """
    Generate a data-driven test using Test Template.
    
    Args:
        test_name: Name of the test
        url: Target URL
        template_steps: Template keyword steps with ${arg1}, ${arg2} placeholders
        test_data: List of test data dictionaries
        output_file: Output filename
        output_dir: Output directory
    
    Returns:
        Generation status and file path
    """
    try:
        validated_url = validate_url(url)
        validated_output = validate_file_path(output_file)
        
        # Ensure .robot extension
        if not validated_output.endswith('.robot'):
            validated_output = validated_output.rsplit('.', 1)[0] + '.robot'
        
        # Build template
        template = f"""*** Settings ***
Documentation    Data-driven test: {test_name}
Library    SeleniumLibrary

*** Variables ***
${{URL}}    {validated_url}
${{BROWSER}}    chrome

*** Test Cases ***
{test_name}
    [Documentation]    Data-driven test case
    [Template]    Test With Data
    [Tags]    data-driven
"""
        
        # Add test data rows
        for data_row in test_data:
            values = "    ".join(str(v) for v in data_row.values())
            template += f"    {values}\n"
        
        template += "\n*** Keywords ***\nTest With Data\n"
        
        # Add arguments
        if test_data:
            args = "    ".join(f"${{{key}}}" for key in test_data[0].keys())
            template += f"    [Arguments]    {args}\n"
        
        template += "    Open Browser    ${URL}    ${BROWSER}\n"
        template += "    Maximize Browser Window\n"
        
        # Add template steps
        for step in template_steps:
            template += f"    {step}\n"
        
        template += "    Close Browser\n"
        
        # Write file
        full_path = Path(output_dir) / validated_output
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(template)
        
        return {
            "status": "success",
            "action": "generate_data_driven_test",
            "file_path": str(full_path),
            "test_name": test_name,
            "data_rows": len(test_data),
            "message": f"Data-driven test created at {full_path}"
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}


@mcp.tool()
def generate_api_test(
    test_name: str,
    base_url: str,
    endpoints: list[dict],
    output_file: str = "api_test.robot",
    output_dir: str = "robot_tests"
) -> dict:
    """
    Generate REST API test cases using RequestsLibrary.
    
    Args:
        test_name: Name of the API test
        base_url: Base API URL
        endpoints: List of endpoint configurations:
            [
                {
                    "name": "Get Users",
                    "method": "GET",
                    "path": "/api/users",
                    "expected_status": 200
                }
            ]
        output_file: Output filename
        output_dir: Output directory
    
    Returns:
        Generation status and file path
    """
    try:
        validated_url = validate_url(base_url)
        validated_output = validate_file_path(output_file)
        
        # Ensure .robot extension
        if not validated_output.endswith('.robot'):
            validated_output = validated_output.rsplit('.', 1)[0] + '.robot'
        
        template = f"""*** Settings ***
Documentation    API Test: {test_name}
Library    RequestsLibrary
Library    Collections

*** Variables ***
${{BASE_URL}}    {validated_url}

*** Test Cases ***
"""
        
        # Generate test cases for each endpoint
        for endpoint in endpoints:
            ep_name = endpoint.get("name", "API Test")
            method = endpoint.get("method", "GET").upper()
            path = endpoint.get("path", "/")
            expected_status = endpoint.get("expected_status", 200)
            headers = endpoint.get("headers", {})
            data = endpoint.get("data", {})
            
            template += f"{ep_name}\n"
            template += f"    [Documentation]    Test {method} {path}\n"
            template += f"    [Tags]    api\n"
            template += f"    Create Session    api    ${{BASE_URL}}\n"
            
            if method == "GET":
                template += f"    ${{response}}=    GET On Session    api    {path}    expected_status={expected_status}\n"
            elif method == "POST":
                template += f"    ${{response}}=    POST On Session    api    {path}    json={data}    expected_status={expected_status}\n"
            elif method == "PUT":
                template += f"    ${{response}}=    PUT On Session    api    {path}    json={data}    expected_status={expected_status}\n"
            elif method == "DELETE":
                template += f"    ${{response}}=    DELETE On Session    api    {path}    expected_status={expected_status}\n"
            
            template += f"    Status Should Be    {expected_status}    ${{response}}\n"
            template += f"    Log    ${{response.json()}}\n\n"
        
        # Write file
        full_path = Path(output_dir) / validated_output
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(template)
        
        return {
            "status": "success",
            "action": "generate_api_test",
            "file_path": str(full_path),
            "test_name": test_name,
            "endpoints": len(endpoints),
            "message": f"API test created at {full_path}"
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}


@mcp.tool()
def generate_performance_test(
    test_url: str,
    output_file: str = "performance_test.robot",
    output_dir: str = "robot_tests",
    load_threshold: int = 3000,
    interactive_threshold: int = 2000,
    paint_threshold: int = 1000
) -> dict:
    """
    Generate performance monitoring test using browser performance APIs.
    
    Args:
        test_url: URL to test
        output_file: Output filename
        output_dir: Output directory
        load_threshold: Max acceptable page load time in ms
        interactive_threshold: Max acceptable interactive time in ms
        paint_threshold: Max acceptable first paint time in ms
    
    Returns:
        Generation status and file path
    """
    
    template = f"""*** Settings ***
Documentation    Performance Monitoring Test
Library    SeleniumLibrary
Library    Collections

*** Variables ***
${{TEST_URL}}    {test_url}
${{BROWSER}}    chrome
${{PERFORMANCE_THRESHOLD_LOAD}}    {load_threshold}
${{PERFORMANCE_THRESHOLD_INTERACTIVE}}    {interactive_threshold}
${{PERFORMANCE_THRESHOLD_PAINT}}    {paint_threshold}

*** Test Cases ***
Test Page Load Performance
    [Documentation]    Measure and validate page load performance metrics
    [Tags]    performance
    
    Open Browser    ${{TEST_URL}}    ${{BROWSER}}
    Maximize Browser Window
    
    # Collect performance metrics
    ${{metrics}}=    Get Performance Metrics
    
    # Validate against thresholds
    Validate Performance Thresholds    ${{metrics}}
    
    # Generate detailed report
    Generate Performance Report    ${{metrics}}
    
    Close Browser

Run Performance Benchmark
    [Documentation]    Run multiple performance tests and calculate averages
    [Tags]    performance    benchmark
    
    @{{results}}=    Create List
    
    FOR    ${{i}}    IN RANGE    2
        Open Browser    ${{TEST_URL}}    ${{BROWSER}}
        Maximize Browser Window
        
        ${{metrics}}=    Get Performance Metrics
        Append To List    ${{results}}    ${{metrics}}
        
        Close Browser
        Sleep    2s
    END
    
    # Calculate averages
    ${{averages}}=    Calculate Average Performance    ${{results}}
    Log    Average Load Time: ${{averages['avg_load_time']}}ms
    Log    Average DOM Ready: ${{averages['avg_dom_ready']}}ms

Test Page Interaction Performance
    [Documentation]    Test performance of page interactions
    [Tags]    performance    interaction
    
    Open Browser    ${{TEST_URL}}    ${{BROWSER}}
    Maximize Browser Window
    
    Test Page Interaction Performance
    
    Close Browser

*** Keywords ***
Get Performance Metrics
    [Documentation]    Collect browser performance metrics using Performance API
    
    # Navigation timing
    ${{navigation_timing}}=    Execute Javascript    
    ...    if ('getEntriesByType' in window.performance) {{
    ...        var nav = window.performance.getEntriesByType('navigation')[0];
    ...        if (nav) {{
    ...            return {{
    ...                'dns_lookup': nav.domainLookupEnd - nav.domainLookupStart,
    ...                'tcp_connect': nav.connectEnd - nav.connectStart,
    ...                'request_response': nav.responseEnd - nav.requestStart,
    ...                'dom_processing': nav.domComplete - nav.domLoading,
    ...                'load_complete': nav.loadEventEnd - nav.fetchStart,
    ...                'dom_ready': nav.domContentLoadedEventEnd - nav.fetchStart
    ...            }};
    ...        }}
    ...    }}
    ...    return {{}};
    
    # Paint timing
    ${{paint_timing}}=    Execute Javascript    
    ...    if ('getEntriesByType' in window.performance) {{
    ...        var paints = window.performance.getEntriesByType('paint');
    ...        var result = {{}};
    ...        paints.forEach(function(paint) {{
    ...            result[paint.name.replace('-', '_')] = paint.startTime;
    ...        }});
    ...        return result;
    ...    }}
    ...    return {{}};
    
    # Memory usage (if supported)
    ${{memory_info}}=    Execute Javascript    
    ...    if ('memory' in window.performance) {{
    ...        return {{
    ...            'used_js_heap': window.performance.memory.usedJSHeapSize,
    ...            'total_js_heap': window.performance.memory.totalJSHeapSize,
    ...            'heap_limit': window.performance.memory.jsHeapSizeLimit
    ...        }};
    ...    }}
    ...    return {{}};
    
    # Resource timing
    ${{resource_count}}=    Execute Javascript    
    ...    if ('getEntriesByType' in window.performance) {{
    ...        var resources = window.performance.getEntriesByType('resource');
    ...        var types = {{}};
    ...        resources.forEach(function(resource) {{
    ...            var type = resource.initiatorType || 'other';
    ...            types[type] = (types[type] || 0) + 1;
    ...        }});
    ...        types['total'] = resources.length;
    ...        return types;
    ...    }}
    ...    return {{}};
    
    # Combine all metrics
    ${{all_metrics}}=    Create Dictionary
    Set To Dictionary    ${{all_metrics}}    navigation=${{navigation_timing}}
    Set To Dictionary    ${{all_metrics}}    paint=${{paint_timing}}
    Set To Dictionary    ${{all_metrics}}    memory=${{memory_info}}
    Set To Dictionary    ${{all_metrics}}    resources=${{resource_count}}
    
    RETURN    ${{all_metrics}}

Validate Performance Thresholds
    [Documentation]    Validate performance against thresholds
    [Arguments]    ${{metrics}}
    
    ${{navigation}}=    Get From Dictionary    ${{metrics}}    navigation
    
    # Check load time
    ${{load_time}}=    Get From Dictionary    ${{navigation}}    load_complete
    Should Be True    ${{load_time}} < ${{PERFORMANCE_THRESHOLD_LOAD}}    
    ...    Page load time (${{load_time}}ms) exceeds threshold (${{PERFORMANCE_THRESHOLD_LOAD}}ms)
    
    # Check DOM ready time
    ${{dom_ready}}=    Get From Dictionary    ${{navigation}}    dom_ready
    Should Be True    ${{dom_ready}} < ${{PERFORMANCE_THRESHOLD_INTERACTIVE}}    
    ...    DOM ready time (${{dom_ready}}ms) exceeds threshold (${{PERFORMANCE_THRESHOLD_INTERACTIVE}}ms)
    
    # Log all metrics
    Log    Load Time: ${{load_time}}ms (Threshold: ${{PERFORMANCE_THRESHOLD_LOAD}}ms)
    Log    DOM Ready: ${{dom_ready}}ms (Threshold: ${{PERFORMANCE_THRESHOLD_INTERACTIVE}}ms)

Test Page Interaction Performance
    [Documentation]    Test performance of page interactions
    
    # Test scroll performance
    ${{scroll_start}}=    Get Time    epoch
    Execute Javascript    window.scrollTo(0, document.body.scrollHeight);
    Sleep    0.5s
    Execute Javascript    window.scrollTo(0, 0);
    ${{scroll_end}}=    Get Time    epoch
    ${{scroll_time}}=    Evaluate    (${{scroll_end}} - ${{scroll_start}}) * 1000
    
    Log    Scroll performance: ${{scroll_time}}ms
    Should Be True    ${{scroll_time}} < 500    Scroll should be smooth (< 500ms)
    
    # Test if there are interactive elements
    ${{buttons}}=    Get WebElements    css=button, input[type="submit"], .btn
    ${{button_count}}=    Get Length    ${{buttons}}
    
    IF    ${{button_count}} > 0
        ${{button}}=    Get From List    ${{buttons}}    0
        ${{click_start}}=    Get Time    epoch
        Click Element    ${{button}}
        Sleep    0.1s    # Small delay to register interaction
        ${{click_end}}=    Get Time    epoch
        ${{click_time}}=    Evaluate    (${{click_end}} - ${{click_start}}) * 1000
        
        Log    Click response time: ${{click_time}}ms
        Should Be True    ${{click_time}} < 200    Click response should be immediate (< 200ms)
    END

Generate Performance Report
    [Documentation]    Generate detailed performance report
    [Arguments]    ${{metrics}}
    
    ${{timestamp}}=    Get Current Date    result_format=%Y-%m-%d_%H-%M-%S
    ${{report_file}}=    Set Variable    performance_report_${{timestamp}}.txt
    
    ${{navigation}}=    Get From Dictionary    ${{metrics}}    navigation
    ${{resources}}=    Get From Dictionary    ${{metrics}}    resources
    
    ${{dns}}=    Get From Dictionary    ${{navigation}}    dns_lookup
    ${{tcp}}=    Get From Dictionary    ${{navigation}}    tcp_connect
    ${{request}}=    Get From Dictionary    ${{navigation}}    request_response
    ${{dom_proc}}=    Get From Dictionary    ${{navigation}}    dom_processing
    ${{load}}=    Get From Dictionary    ${{navigation}}    load_complete
    ${{dom_ready}}=    Get From Dictionary    ${{navigation}}    dom_ready
    
    ${{total_resources}}=    Get From Dictionary    ${{resources}}    total    default=0
    
    ${{report_content}}=    Catenate    SEPARATOR=\\n
    ...    ========================================
    ...    PERFORMANCE TEST REPORT
    ...    ========================================
    ...    Test URL: ${{TEST_URL}}
    ...    Test Time: ${{timestamp}}
    ...    ${{EMPTY}}
    ...    NAVIGATION TIMING:
    ...    - DNS Lookup: ${{dns}}ms
    ...    - TCP Connect: ${{tcp}}ms
    ...    - Request/Response: ${{request}}ms
    ...    - DOM Processing: ${{dom_proc}}ms
    ...    - Page Load Complete: ${{load}}ms
    ...    - DOM Ready: ${{dom_ready}}ms
    ...    ${{EMPTY}}
    ...    RESOURCE LOADING:
    ...    - Total Resources: ${{total_resources}}
    ...    ${{EMPTY}}
    ...    PERFORMANCE THRESHOLDS:
    ...    - Load Time Threshold: ${{PERFORMANCE_THRESHOLD_LOAD}}ms
    ...    - Interactive Threshold: ${{PERFORMANCE_THRESHOLD_INTERACTIVE}}ms
    ...    - Paint Threshold: ${{PERFORMANCE_THRESHOLD_PAINT}}ms
    ...    ========================================
    
    Create File    ${{report_file}}    ${{report_content}}
    Log    Performance report saved to: ${{report_file}}

Calculate Average Performance
    [Documentation]    Calculate average performance from multiple test runs
    [Arguments]    ${{results_list}}
    
    ${{total_load}}=    Set Variable    0
    ${{total_dom}}=    Set Variable    0
    ${{count}}=    Get Length    ${{results_list}}
    
    FOR    ${{result}}    IN    @{{results_list}}
        ${{navigation}}=    Get From Dictionary    ${{result}}    navigation
        ${{load_time}}=    Get From Dictionary    ${{navigation}}    load_complete
        ${{dom_time}}=    Get From Dictionary    ${{navigation}}    dom_ready
        
        ${{total_load}}=    Evaluate    ${{total_load}} + ${{load_time}}
        ${{total_dom}}=    Evaluate    ${{total_dom}} + ${{dom_time}}
    END
    
    ${{avg_load}}=    Evaluate    ${{total_load}} / ${{count}}
    ${{avg_dom}}=    Evaluate    ${{total_dom}} / ${{count}}
    
    ${{averages}}=    Create Dictionary    avg_load_time=${{avg_load}}    avg_dom_ready=${{avg_dom}}
    RETURN    ${{averages}}
"""
    
    try:
        # Validate inputs
        validated_url = validate_url(test_url)
        validated_output = validate_file_path(output_file)
        
        # Ensure .robot extension
        if not validated_output.endswith('.robot'):
            validated_output = validated_output.rsplit('.', 1)[0] + '.robot'
        
        # Create full path
        full_path = Path(output_dir) / validated_output
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write the test file
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(template)
        
        return {
            "status": "success",
            "action": "generate_performance_test",
            "file_path": str(full_path),
            "test_url": validated_url,
            "thresholds": {
                "load": load_threshold,
                "interactive": interactive_threshold,
                "paint": paint_threshold
            },
            "test_count": 2,
            "message": f"Performance monitoring test created at {full_path} for {validated_url}"
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}


# =============================
# SERVER ENTRY
# =============================

def main():
    import sys

    if "--stdio" not in sys.argv:
        print("Robot Hybrid MCP Server Running")

    mcp.run()


if __name__ == "__main__":
    main()