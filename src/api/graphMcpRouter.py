import logging
from typing import Any

from api.graphApiRouter import get_schema, read_neo4j_cypher

from fastapi import APIRouter, Body, Depends, HTTPException, Request, status


logger = logging.getLogger(__name__)

router = APIRouter()


async def verify_mcp(request: Request):
    if (
        request.client.host == "127.0.0.1"
    ):  # La llamada siempre la hace el propio server que esta en local
        return True
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Only MCP Server can call this endpoint",
    )


@router.get(
    "/schema",
    summary="""
        List all nodes, their attributes and their relationships to other nodes in the neo4j database.
        This requires that the APOC plugin is installed and enabled.
        """,  # Esto es la descripción de la tool
    #  response_model=list[ToolResult], # Esto es lo que va a responder
    tags=["MCP"],
)  # tag que sirve para incluir o no los de cierto tag
async def get_schema_mcp(mcpCall: bool = Depends(verify_mcp)):
    """
    List all nodes, their attributes and their relationships to other nodes in the neo4j database.
    This requires that the APOC plugin is installed and enabled.
    """
    if not mcpCall:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Only MCP Server can call this endpoint",
        )
    return await get_schema()


@router.post(
    "/read",
    summary="""
        Execute a read Cypher query on the neo4j database.
        """,  # Esto es la descripción de la tool
    #  response_model=list[ToolResult], # Esto es lo que va a responder
    tags=["MCP"],
)  # tag que sirve para incluir o no los de cierto tag
async def read_neo4j_cypher_mcp(
    query: str = Body(..., description="The Cypher query to execute."),
    params: dict[str, Any] = Body(
        dict(), description="The parameters to pass to the Cypher query."
    ),
    mcpCall: bool = Depends(verify_mcp),
):
    if not mcpCall:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Only MCP Server can call this endpoint",
        )
    return await read_neo4j_cypher(query=query, params=params)
