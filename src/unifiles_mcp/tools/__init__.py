"""Tools module for unifiles-mcp.

This module contains all MCP tools for file operations.
"""

from typing import Any


def register_all(server: Any) -> None:
    """Register all tools from excel, pdf, word, sqlite on the given FastMCP server."""
    from . import excel, pdf, sqlite, word

    excel.register(server)
    pdf.register(server)
    word.register(server)
    sqlite.register(server)
