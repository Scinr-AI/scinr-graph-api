import logging

from fastmcp import FastMCP
from fastmcp.tools import ToolResult
from api.graphApiRouter import get_schema, read_neo4j_cypher

logger = logging.getLogger(__name__)

# FastMCP server — stateless HTTP transport required for Lambda (no persistent sessions)
mcp = FastMCP("My API MCP", instructions="Very cool MCP server")


@mcp.tool
async def get_schema_mcp() -> ToolResult:
    """
    List all nodes, their attributes and their relationships to other nodes in the neo4j database.
    This requires that the APOC plugin is installed and enabled.
    """
    # get_schema() returns ToolResult(content=[TextContent(type="text", text=...)])
    # Extract the plain string so it matches the -> str return annotation
    return await get_schema()


@mcp.tool
async def read_neo4j_cypher_mcp(query: str, params: dict | None = None) -> str:
    """Execute a read Cypher query on the neo4j database."""
    return await read_neo4j_cypher(query=query, params=params or {})
