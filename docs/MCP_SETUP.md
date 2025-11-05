# MCP Server Setup Documentation

**Date:** 2025-11-04
**Issue:** #1 - Install and configure MCP server for web navigation
**Status:** ✓ Complete

---

## Overview

This document describes the installation and configuration of the Microsoft Playwright MCP (Model Context Protocol) server for automated web navigation and data extraction from Vanderbilt University websites.

## MCP Server Selection

After research, we selected the **Microsoft Playwright MCP Server** for the following reasons:

### Why Playwright MCP?

1. **Official Support:** Developed and maintained by Microsoft
2. **Structured Data Access:** Uses Playwright's accessibility tree (not pixel-based)
3. **No Vision Models Needed:** Operates on structured HTML/DOM data
4. **Cross-Browser Support:** Supports Chromium, Firefox, and WebKit
5. **JavaScript Rendering:** Handles modern JavaScript-heavy websites
6. **Claude Code Integration:** Direct integration via MCP protocol

### Alternatives Considered

- **Puppeteer MCP:** Similar capabilities, but Playwright is more modern and officially supported
- **Selenium MCP:** Older technology, less suited for modern web scraping
- **Custom scraping:** Would require more manual code and maintenance

## Installation

### Command Used

```bash
claude mcp add npx @playwright/mcp@latest
```

### What This Does

1. Registers the Playwright MCP server with Claude Code
2. Configures it to run via `npx` (no global installation needed)
3. Stores configuration in `~/.claude.json` for the current project
4. Makes Playwright tools available in Claude Code sessions

### Installation Output

```
Added stdio MCP server npx with command: @playwright/mcp@latest to local config
File modified: /Users/spencejb/.claude.json [project: /Users/spencejb/Documents/projects/grant-match]
```

## Configuration

### Location

Configuration is stored in `~/.claude.json` under the project-specific settings:

```json
"/Users/spencejb/Documents/projects/grant-match": {
  "mcpServers": {
    "npx": {
      "type": "stdio",
      "command": "@playwright/mcp@latest",
      "args": [],
      "env": {}
    }
  }
}
```

### Configuration Details

- **Server Name:** `npx`
- **Transport Type:** `stdio` (standard input/output)
- **Command:** `@playwright/mcp@latest` (always uses latest version)
- **Arguments:** None (default configuration)
- **Environment Variables:** None (inherits from parent process)

### Customization Options (if needed later)

The configuration can be modified to include:

```json
{
  "type": "stdio",
  "command": "@playwright/mcp@latest",
  "args": [
    "--browser=chromium",  // Specify browser
    "--headless=false"     // Show browser window
  ],
  "env": {
    "PLAYWRIGHT_TIMEOUT": "30000"  // Set custom timeout
  }
}
```

## Available Capabilities

Once activated in a Claude Code session, the Playwright MCP server provides the following capabilities:

### Navigation & Interaction

- **Navigate to URLs:** Open and navigate web pages
- **Click Elements:** Interact with buttons, links, forms
- **Fill Forms:** Enter data into input fields
- **Take Screenshots:** Capture page visuals for analysis
- **Execute JavaScript:** Run custom scripts on pages

### Content Extraction

- **Accessibility Tree:** Extract structured page content
- **Text Content:** Get readable text from pages
- **DOM Elements:** Access specific HTML elements
- **Form Data:** Extract form structures and values

### Session Management

- **Persistent Context:** Maintain browser state across operations
- **Cookie Management:** Handle authentication and sessions
- **Multi-page Support:** Navigate across multiple pages

## Usage in Claude Code

### Viewing Available Tools

To see all Playwright tools available in a session:

```bash
/mcp
```

Then navigate to the `playwright` section to view all available tools.

### Example Usage Patterns

When working with Claude Code, you can request:

1. **"Navigate to the Vanderbilt Engineering website"**
   - Claude will use Playwright to open the page

2. **"Extract faculty names from the Biomedical Engineering department page"**
   - Claude will navigate, extract structured data

3. **"Fill out the contact form on this page"**
   - Claude can interact with form elements

4. **"Take a screenshot of the current page"**
   - Useful for debugging or verification

### Important Notes

- **First Use:** You may need to explicitly mention "use Playwright MCP" initially
- **Browser Window:** The browser window stays visible for interaction
- **Authentication:** You can manually sign in to websites when needed
- **Rate Limiting:** Respect server resources with delays between requests

## Testing the Installation

### Basic Test

To verify the MCP server is working:

```
Navigate to https://engineering.vanderbilt.edu/ using Playwright
```

Expected behavior:
- Playwright browser opens
- Page loads successfully
- Content is extracted

### Test for Faculty Pages

```
Use Playwright to navigate to the Vanderbilt Biomedical Engineering faculty page
and extract the list of faculty names
```

Expected behavior:
- Successfully loads the faculty listing page
- Extracts structured faculty information
- Returns data for further processing

## Troubleshooting

### MCP Server Not Starting

If the MCP server fails to start:

1. **Check Node.js version:** Playwright requires Node.js 18+
   ```bash
   node --version
   ```

2. **Check network access:** Ensure you can reach npm registry
   ```bash
   npm ping
   ```

3. **View debug logs:** Run Claude Code with MCP debug mode
   ```bash
   claude --mcp-debug
   ```

### Browser Not Opening

If Playwright doesn't open a browser:

1. **Install browser binaries:**
   ```bash
   npx playwright install chromium
   ```

2. **Check system dependencies:** Ensure required libraries are installed
   ```bash
   npx playwright install-deps
   ```

### Permission Issues

If tools are restricted:

1. **Check project trust:** Ensure project is trusted in Claude Code
2. **Review permissions:** Use `/permissions` to view tool access
3. **Grant MCP access:** Approve Playwright tools when prompted

## Best Practices for Web Scraping

### Respect Vanderbilt Resources

1. **Rate Limiting:** Add delays between requests (2-5 seconds)
2. **Robots.txt:** Check and respect robots.txt directives
3. **User Agent:** Identify scraper appropriately
4. **Off-Peak:** Consider scraping during off-peak hours

### Error Handling

1. **Timeouts:** Set reasonable timeouts for page loads
2. **Retries:** Implement exponential backoff for failures
3. **Validation:** Verify extracted data quality
4. **Logging:** Track all navigation and extraction attempts

### Data Quality

1. **Consistency:** Use consistent selectors and extraction patterns
2. **Validation:** Verify extracted data matches expected format
3. **Deduplication:** Handle duplicate entries
4. **Completeness:** Check for missing data and log gaps

## Next Steps

With the MCP server installed and configured, you can now proceed to:

1. **Issue #3:** Map Vanderbilt Engineering department structure
   - Use Playwright to explore department pages
   - Document URL patterns and page structures

2. **Issue #4:** Scrape faculty listings
   - Use Playwright to extract faculty information
   - Handle JavaScript-rendered content

3. **Issue #5:** Extract research information from faculty websites
   - Navigate to individual faculty pages
   - Extract research descriptions and publications

## Resources

### Official Documentation

- **Playwright MCP Server:** https://github.com/microsoft/playwright-mcp
- **Playwright Documentation:** https://playwright.dev/
- **MCP Protocol:** https://modelcontextprotocol.io/
- **Claude Code MCP Guide:** https://docs.claude.com/en/docs/claude-code/mcp

### Vanderbilt Resources

- **Engineering Home:** https://engineering.vanderbilt.edu/
- **Engineering Faculty:** https://engineering.vanderbilt.edu/people/
- **Robots.txt:** https://vanderbilt.edu/robots.txt

## Maintenance

### Updating the MCP Server

The MCP server uses `@latest` tag, so it automatically uses the latest version. To force an update:

```bash
# Remove and re-add the MCP server
claude mcp remove npx
claude mcp add npx @playwright/mcp@latest
```

### Monitoring

Check MCP server health with:

```bash
claude mcp list
```

This shows status of all configured MCP servers.

## Version Information

- **Playwright MCP Version:** Latest (auto-updated via npx)
- **Node.js Version:** 18+ required
- **Installation Date:** 2025-11-04
- **Installation Method:** npx (no global install)
- **Transport:** stdio

---

**Document Status:** Complete
**Last Updated:** 2025-11-04
**Issue Status:** #1 - Complete ✓
