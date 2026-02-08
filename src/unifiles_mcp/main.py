"""Main entry point for unifiles-mcp MCP server."""

from mcp.server.fastmcp import FastMCP

# Create FastMCP server instance
mcp = FastMCP(name="unifiles-mcp")

# Register all tools on this mcp instance (avoids circular import when run as __main__)
from .tools import register_all  # noqa: E402

register_all(mcp)


@mcp.tool()
async def ping() -> str:
    """Health check endpoint. Returns 'pong' if server is running."""
    return "pong"


def run() -> None:
    """Entry point for console_scripts. Starts the MCP server."""
    mcp.run()


if __name__ == "__main__":
    run()
