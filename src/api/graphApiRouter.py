import json
import logging

from typing import Any

from fastapi import APIRouter, Body
from fastmcp.exceptions import ToolError
from fastmcp.tools import ToolResult
from mcp.types import TextContent
from neo4j.exceptions import ClientError, Neo4jError
from utils.neo4jUtils import _is_write_query, _read, neo4j_driver



logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/schema",
    summary="""
        List all nodes, their attributes and their relationships to other nodes in the neo4j database.
        This requires that the APOC plugin is installed and enabled.
        """,  # Esto es la descripción de la tool
    #  response_model=list[ToolResult], # Esto es lo que va a responder
    tags=["API"],
)  # tag que sirve para incluir o no los de cierto tag
async def get_schema():
    """
    List all nodes, their attributes and their relationships to other nodes in the neo4j database.
    This requires that the APOC plugin is installed and enabled.
    """

    get_schema_query = """
        CALL apoc.meta.schema();
        """

    def clean_schema(schema: dict) -> dict:
        cleaned = {}

        for key, entry in schema.items():
            new_entry = {"type": entry["type"]}
            if "count" in entry:
                new_entry["count"] = entry["count"]

            labels = entry.get("labels", [])
            if labels:
                new_entry["labels"] = labels

            props = entry.get("properties", {})
            clean_props = {}
            for pname, pinfo in props.items():
                cp = {}
                if "indexed" in pinfo:
                    cp["indexed"] = pinfo["indexed"]
                if "type" in pinfo:
                    cp["type"] = pinfo["type"]
                if cp:
                    clean_props[pname] = cp
            if clean_props:
                new_entry["properties"] = clean_props

            if entry.get("relationships"):
                rels_out = {}
                for rel_name, rel in entry["relationships"].items():
                    cr = {}
                    if "direction" in rel:
                        cr["direction"] = rel["direction"]
                    # nested labels
                    rlabels = rel.get("labels", [])
                    if rlabels:
                        cr["labels"] = rlabels
                    # nested properties
                    rprops = rel.get("properties", {})
                    clean_rprops = {}
                    for rpname, rpinfo in rprops.items():
                        crp = {}
                        if "indexed" in rpinfo:
                            crp["indexed"] = rpinfo["indexed"]
                        if "type" in rpinfo:
                            crp["type"] = rpinfo["type"]
                        if crp:
                            clean_rprops[rpname] = crp
                    if clean_rprops:
                        cr["properties"] = clean_rprops

                    if cr:
                        rels_out[rel_name] = cr

                if rels_out:
                    new_entry["relationships"] = rels_out

            cleaned[key] = new_entry

        return cleaned

    try:
        async with neo4j_driver.session() as session:
            results_json_str = await session.execute_read(
                _read, get_schema_query, dict()
            )

            logger.debug(f"Read query returned {len(results_json_str)} rows")

            schema = json.loads(results_json_str)[0].get("value")
            schema_clean = clean_schema(schema)
            schema_clean_str = json.dumps(schema_clean)

            return ToolResult(content=[TextContent(type="text", text=schema_clean_str)])

    except ClientError as e:
        if "Neo.ClientError.Procedure.ProcedureNotFound" in str(e):
            raise ToolError(
                "Neo4j Client Error: This instance of Neo4j does not have the APOC plugin installed. Please install and enable the APOC plugin to use the `get_neo4j_schema` tool."
            )
        else:
            raise ToolError(f"Neo4j Client Error: {e}")

    except Neo4jError as e:
        raise ToolError(f"Neo4j Error: {e}")

    except Exception as e:
        logger.error(f"Error retrieving Neo4j database schema: {e}")
        raise ToolError(f"Unexpected Error: {e}")


@router.post(
    "/read",
    summary="""
        Execute a read Cypher query on the neo4j database.
        """,  # Esto es la descripción de la tool
    #  response_model=list[ToolResult], # Esto es lo que va a responder
    tags=["API"],
)  # tag que sirve para incluir o no los de cierto tag
async def read_neo4j_cypher(
    query: str = Body(..., description="The Cypher query to execute."),
    params: dict[str, Any] = Body(
        dict(), description="The parameters to pass to the Cypher query."
    ),
):
    """Execute a read Cypher query on the neo4j database."""
    if _is_write_query(query):
        raise ValueError("Only MATCH queries are allowed for read-query")
    try:
        async with neo4j_driver.session() as session:
            results = await session.execute_read(_read, query, params)
            logger.debug(f"Read query returned {len(results)} rows")
            return results 

    except Neo4jError as e:
        logger.error(f"Neo4j Error executing read query: {e}\n{query}\n{params}")
        raise ToolError(f"Neo4j Error: {e}\n{query}\n{params}")

    except Exception as e:
        logger.error(f"Error executing read query: {e}\n{query}\n{params}")
        raise ToolError(f"Error: {e}\n{query}\n{params}")
