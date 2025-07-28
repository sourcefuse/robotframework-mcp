#!/usr/bin/env node

const { execSync } = require('child_process');

// Function to find Python executable
function findPython() {
  const pythonCandidates = ['python3', 'python', 'py'];
  
  for (const candidate of pythonCandidates) {
    try {
      const result = execSync(`${candidate} --version`, { 
        encoding: 'utf8', 
        stdio: ['pipe', 'pipe', 'ignore'] 
      });
      
      if (result.includes('Python 3.')) {
        return candidate;
      }
    } catch (e) {
      // Continue to next candidate
    }
  }
  
  console.warn('⚠️  Python 3.10+ not found. Python dependencies will be installed when first running the MCP server.');
  return null;
}

// Install Python dependencies
function installPythonDeps() {
  console.log('📦 Installing Robot Framework MCP Server dependencies...');
  
  const python = findPython();
  
  if (!python) {
    console.log('ℹ️  Python not found during installation. Dependencies will be installed on first run.');
    return;
  }
  
  try {
    console.log('🔍 Checking Python dependencies...');
    execSync(`${python} -c "import mcp, robotframework, selenium"`, {
      stdio: 'ignore'
    });
    console.log('✅ Python dependencies already installed');
  } catch (e) {
    try {
      console.log('📥 Installing: mcp, robotframework, selenium, robotframework-seleniumlibrary...');
      execSync(`${python} -m pip install mcp robotframework selenium robotframework-seleniumlibrary`, {
        stdio: 'inherit'
      });
      console.log('✅ Python dependencies installed successfully');
    } catch (installError) {
      console.warn('⚠️  Could not install Python dependencies automatically.');
      console.warn('Please manually run: pip3 install mcp robotframework selenium robotframework-seleniumlibrary');
    }
  }
}

if (require.main === module) {
  installPythonDeps();
}
