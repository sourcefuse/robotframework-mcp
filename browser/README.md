# rf-browser-mcp

MCP server exposing Robot Framework's [Browser library](https://robotframework-browser.org/)
(Playwright-based) as tools for LLM-driven browser automation.

This is the `--library=browser` backend of
[robotframework-mcp-server](https://www.npmjs.com/package/robotframework-mcp-server).
It is normally installed and started for you by the Node launcher:

```bash
npx -y robotframework-mcp-server --library=browser --setup   # one-time setup
npx -y robotframework-mcp-server --library=browser           # run the MCP server
```

Manual setup (from this directory):

```bash
python3 -m venv .venv
.venv/bin/pip install -e .
.venv/bin/rfbrowser init
.venv/bin/python -m rf_browser_mcp.server
```
