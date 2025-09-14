#!/usr/bin/env node
const { spawn, spawnSync } = require('child_process');
const path = require('path');
const os = require('os');
const fs = require('fs');

// Get the directory where this script is located
const scriptDir = path.dirname(__filename);
const pythonScript = path.join(scriptDir, '..', 'mcp_server.py');

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
                console.log(`Found Python: ${cmd} - ${output.trim()}`);
                
                // Check Python version
                const versionMatch = output.match(/Python (\d+)\.(\d+)/);
                if (versionMatch) {
                    const major = parseInt(versionMatch[1]);
                    const minor = parseInt(versionMatch[2]);
                    if (major >= 3 && minor >= 10) {
                        return cmd;
                    } else {
                        console.warn(`Python ${major}.${minor} found, but Python 3.10+ is required`);
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
    const venvPython = path.join(scriptDir, '..', '.venv', 'bin', 'python3');
    if (fs.existsSync(venvPython)) {
        console.log('✅ Found virtual environment: .venv');
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
        console.log('📦 Installing Python dependencies in .venv...');
    } else {
        console.warn('⚠️ No .venv found. It is strongly recommended to use a virtual environment!');
        console.warn('Run the following commands before using this tool:');
        console.warn('  python3 -m venv .venv');
        console.warn('  source .venv/bin/activate');
        console.warn('Then re-run this command.');
    }

    const install = spawn(python, ['-m', 'pip', 'install', 'mcp', 'selenium', 'robotframework-seleniumlibrary'], {
        stdio: 'inherit',
        shell: isWindows // Use shell on Windows
    });

    install.on('close', (code) => {
        if (code === 0) {
            console.log('✅ Dependencies installed successfully');
            startServer();
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

    console.log('🚀 Starting Robot Framework MCP server...');
    console.log(`Using Python: ${python}`);
    console.log(`Script path: ${pythonScript}`);

    const server = spawn(python, [pythonScript], {
        stdio: 'inherit',
        shell: isWindows // Use shell on Windows
    });

    server.on('close', (code) => {
        if (code === 0) {
            console.log('✅ Robot Framework MCP server stopped gracefully');
        } else {
            console.log(`❌ Robot Framework MCP server exited with code ${code}`);
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

// Main execution
try {
    installDependencies();
} catch (error) {
    console.error('Error:', error);
    process.exit(1);
}