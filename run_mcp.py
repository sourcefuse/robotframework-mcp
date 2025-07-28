#!/usr/bin/env python3
"""
UV-compatible entry point for Robot Framework MCP Server
"""

import sys
import os

def main():
    """Main entry point for UV execution"""
    # Add current directory to Python path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    
    # Import and run the MCP server
    try:
        from mcp_server import main as mcp_main
        mcp_main()
    except ImportError as e:
        print(f"Import error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
