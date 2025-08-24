# Claude Project Configuration

This folder contains project-scoped Claude settings and MCP server configuration.

## Files
- `settings.json`: Hook automations for Claude Code events (safe to customize).
- `hooks.json`: Global hooks example (notifications, logging).
- `mcp.servers.json`: Project-level MCP server definitions used by code in this repo.

## MCP Servers
Two servers are referenced by projects here:
- `zapier`: Exposes Google Drive and Airtable actions (used by Project Starlink).
- `playwright`: Provides browser automation tools (used by InterviewAgent).

### Using with Claude Desktop
To enable servers globally in Claude Desktop, add the `mcpServers` block to your desktop config:

- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\\Claude\\claude_desktop_config.json`
- Linux: `~/.config/Claude/claude_desktop_config.json`

Example snippet to merge under the top-level `mcpServers` key:

```
{
  "mcpServers": {
    "zapier": { "command": "npx", "args": ["-y", "@zapier/mcp-server"], "env": {} },
    "playwright": { "command": "npx", "args": ["-y", "@modelcontextprotocol/server-playwright"], "env": {} }
  }
}
```

Alternatively, some editors support loading project-level config from `.claude/mcp.servers.json` directly.

### Notes
- Ensure `node` and `npx` are available on your PATH for the above commands.
- You can set API keys or options in each server's `env` block if required.
- Restart Claude Desktop (or reload the extension) after changes.

