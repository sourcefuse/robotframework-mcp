#!/usr/bin/env node
const { spawn, spawnSync } = require('child_process');
const path = require('path');
const os = require('os');
const fs = require('fs');

// Get the directory where this script is located
const scriptDir = path.dirname(__filename);
const packageRoot = path.join(scriptDir, '..');

// Check for --project-dir argument first, then environment variables, then fallback
const projectDirArg = process.argv.find(arg => arg.startsWith('--project-dir='));
const projectRoot = projectDirArg
    ? projectDirArg.split('=')[1]
    : (process.env.PWD || process.env.INIT_CWD || process.cwd());

// Which Robot Framework library backend to run: "selenium" (default, unchanged
// behavior) or "browser" (Playwright-based Browser library, bundled in packageRoot/browser).
const libraryArg = process.argv.find(arg => arg.startsWith('--library='));
const library = libraryArg
    ? libraryArg.split('=')[1]
    : (process.env.ROBOTFRAMEWORK_MCP_LIBRARY || 'selenium');

const SUPPORTED_LIBRARIES = ['selenium', 'browser'];
if (!SUPPORTED_LIBRARIES.includes(library)) {
    console.error(`❌ Unknown --library="${library}". Supported values: ${SUPPORTED_LIBRARIES.join(', ')}`);
    process.exit(1);
}

// --setup: install/prepare the selected backend, then exit without starting the
// MCP server. Lets users run the slow first-time setup (e.g. `rfbrowser init`,
// which downloads Playwright browsers) from a terminal instead of inside an MCP
// client, where it would exceed the client's startup timeout.
const setupOnly = process.argv.includes('--setup');

// stdout is the MCP JSON-RPC channel once the server runs, so the launcher and
// its setup subprocesses must never write to it: logs go to stderr (console.error)
// and installer output is redirected to stderr (fd 2).
const SETUP_STDIO = ['ignore', 2, 2];

const pythonScript = path.join(packageRoot, 'mcp_server.py');

// Check if Python is available
function checkPython() {
    // Windows-specific Python commands
    const isWindows = os.platform() === 'win32';
    const pythonCommands = isWindows
        ? ['py', 'python', 'python3', 'python.exe']
        : ['python3', 'python'];

    for (const cmd of pythonCommands) {
        try {
            const result = spawnSync(cmd, ['--version'], {
                stdio: 'pipe',
                shell: isWindows // Use shell on Windows
            });

            if (result.status === 0) {
                const output = result.stdout.toString() || result.stderr.toString();
                console.error(`Found Python: ${cmd} - ${output.trim()}`);

                // Check Python version
                const versionMatch = output.match(/Python (\d+)\.(\d+)/);
                if (versionMatch) {
                    const major = parseInt(versionMatch[1]);
                    const minor = parseInt(versionMatch[2]);
                    if (major >= 3 && minor >= 10) {
                        return cmd;
                    } else {
                        console.error(`Python ${major}.${minor} found, but Python 3.10+ is required`);
                    }
                }
            }
        } catch (error) {
            // Silently continue to next command
            continue;
        }
    }

    console.error('❌ Python 3.10+ not found.');
    console.error('');
    console.error('Please install Python 3.10 or higher:');
    if (isWindows) {
        console.error('  • Download from: https://www.python.org/downloads/');
        console.error('  • Or install from Microsoft Store');
        console.error('  • Make sure to check "Add Python to PATH" during installation');
        console.error('  • After installation, restart your terminal/command prompt');
    } else {
        console.error('  • macOS: brew install python@3.11');
        console.error('  • Linux: sudo apt-get install python3.11');
        console.error('  • Or download from: https://www.python.org/downloads/');
    }
    console.error('');
    process.exit(1);
}

// Find Python executable, preferring .venv if present
function getPythonExecutable() {
    console.error('🔍 Debug info:');
    console.error('  process.cwd():', process.cwd());
    console.error('  process.env.PWD:', process.env.PWD);
    console.error('  process.env.INIT_CWD:', process.env.INIT_CWD);
    console.error('  projectRoot:', projectRoot);

    const venvPython = path.join(projectRoot, '.venv', 'bin', 'python3');
    console.error('Script dir path: ', projectRoot);
    console.error('virtual environment path: ', venvPython);
    if (fs.existsSync(venvPython)) {
        console.error('✅ Found virtual environment: .venv');
        return venvPython;
    }
    // Fallback to system Python detection
    return checkPython();
}

// Install Python dependencies if needed
function installDependencies() {
    const python = getPythonExecutable();
    const isWindows = os.platform() === 'win32';

    if (python.includes('.venv')) {
        console.error('📦 Installing Python dependencies in .venv...');
    } else {
        console.error('⚠️ No .venv found. It is strongly recommended to use a virtual environment!');
        console.error('Run the following commands before using this tool:');
        console.error('  python3 -m venv .venv');
        console.error('  source .venv/bin/activate');
        console.error('Then re-run this command.');
    }

    const install = spawn(python, ['-m', 'pip', 'install', 'mcp', 'selenium', 'robotframework-seleniumlibrary'], {
        stdio: SETUP_STDIO,
        shell: isWindows // Use shell on Windows
    });

    install.on('close', (code) => {
        if (code === 0) {
            console.error('✅ Dependencies installed successfully');
            if (!setupOnly) startServer();
        } else {
            console.error('❌ Failed to install dependencies');
            console.error('Troubleshooting:');
            console.error('  • Ensure Python is properly installed and in PATH');
            console.error('  • Use a virtual environment (.venv) for best results');
            console.error('  • Try running manually: pip install mcp selenium robotframework-seleniumlibrary');
            console.error('  • Check if you need to use python -m pip instead of pip');
            process.exit(1);
        }
    });

    install.on('error', (error) => {
        console.error('❌ Error during installation:', error.message);
        process.exit(1);
    });
}

// Start the Python MCP server
function startServer() {
    const python = getPythonExecutable();
    const isWindows = os.platform() === 'win32';

    console.error('🚀 Starting Robot Framework MCP server...');
    console.error(`Using Python: ${python}`);
    console.error(`Script path: ${pythonScript}`);

    const server = spawn(python, [pythonScript], {
        stdio: 'inherit',
        shell: isWindows // Use shell on Windows
    });

    server.on('close', (code) => {
        if (code === 0) {
            console.error('✅ Robot Framework MCP server stopped gracefully');
        } else {
            console.error(`❌ Robot Framework MCP server exited with code ${code}`);
        }
    });

    server.on('error', (error) => {
        console.error('❌ Error starting Robot Framework MCP server:', error.message);
        console.error('Troubleshooting:');
        console.error('  • Check if mcp_server.py exists in the project directory');
        console.error('  • Ensure all Python dependencies are installed');
        console.error('  • Use a virtual environment (.venv) for best results');
        console.error('  • Try running manually: python mcp_server.py');
    });
}

// --- Browser (Playwright) library backend ------------------------------------
// Bundled under packageRoot/browser with its own .venv, since robotframework-browser
// needs an extra "rfbrowser init" step (downloads a Node side-car + Playwright
// browsers) that end users shouldn't have to run by hand.

const browserRoot = path.join(packageRoot, 'browser');
const browserVenvPython = path.join(browserRoot, '.venv', 'bin', 'python3');

function isBrowserBackendReady() {
    if (!fs.existsSync(browserVenvPython)) return false;
    const check = spawnSync(browserVenvPython, ['-c', 'import rf_browser_mcp'], { stdio: 'pipe' });
    return check.status === 0;
}

function setupBrowserBackend(onReady) {
    const isWindows = os.platform() === 'win32';
    console.error('📦 Setting up Browser-library backend (first run only)...');

    const venvCmd = fs.existsSync(browserVenvPython) ? null : checkPython();
    const steps = [];
    if (venvCmd) {
        steps.push(() => spawnSync(venvCmd, ['-m', 'venv', path.join(browserRoot, '.venv')], { stdio: SETUP_STDIO, shell: isWindows }));
    }
    steps.push(() => spawnSync(browserVenvPython, ['-m', 'pip', 'install', '-q', '-e', browserRoot], { stdio: SETUP_STDIO, shell: isWindows }));
    steps.push(() => spawnSync(path.join(browserRoot, '.venv', 'bin', 'rfbrowser'), ['init'], { stdio: SETUP_STDIO, shell: isWindows }));

    for (const step of steps) {
        const result = step();
        if (!result || result.status !== 0) {
            console.error('❌ Failed to set up the Browser-library backend.');
            console.error(`   Try running manually inside ${browserRoot}:`);
            console.error('     python3 -m venv .venv && .venv/bin/pip install -e . && .venv/bin/rfbrowser init');
            process.exit(1);
        }
    }

    console.error('✅ Browser-library backend ready');
    onReady();
}

function startBrowserServer() {
    const isWindows = os.platform() === 'win32';
    console.error('🚀 Starting Robot Framework MCP server (Browser library)...');
    console.error(`Using Python: ${browserVenvPython}`);

    const server = spawn(browserVenvPython, ['-m', 'rf_browser_mcp.server'], {
        cwd: browserRoot,
        stdio: 'inherit',
        shell: isWindows
    });

    server.on('close', (code) => {
        if (code === 0) {
            console.error('✅ Robot Framework MCP server stopped gracefully');
        } else {
            console.error(`❌ Robot Framework MCP server exited with code ${code}`);
        }
    });

    server.on('error', (error) => {
        console.error('❌ Error starting Robot Framework MCP server:', error.message);
        console.error('Troubleshooting:');
        console.error(`  • Check that ${browserRoot} has a working .venv`);
        console.error('  • Try running manually: .venv/bin/python -m rf_browser_mcp.server (from the browser/ dir)');
    });
}

function runBrowserLibrary() {
    if (setupOnly) {
        if (isBrowserBackendReady()) {
            console.error('✅ Browser-library backend already set up');
        } else {
            setupBrowserBackend(() => {});
        }
        return;
    }
    if (isBrowserBackendReady()) {
        startBrowserServer();
    } else {
        console.error('⚠️ Browser-library backend is not set up yet; setting it up now (can take a few minutes).');
        console.error('   If your MCP client times out, run this once in a terminal and restart the client:');
        console.error('     npx -y robotframework-mcp-server --library=browser --setup');
        setupBrowserBackend(startBrowserServer);
    }
}

// Main execution
try {
    if (library === 'browser') {
        runBrowserLibrary();
    } else {
        installDependencies();
    }
} catch (error) {
    console.error('Error:', error);
    process.exit(1);
}
