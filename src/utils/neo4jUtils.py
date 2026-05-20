from dotenv import load_dotenv
import os

import json
import re
from typing import Any


from neo4j import (
    AsyncDriver,
    AsyncGraphDatabase,
    AsyncResult,
    AsyncTransaction,
)


loaded=load_dotenv(".env")

# Configuration
DBURL = os.getenv("NEO4J_URI") 
DBUSERNAME = os.getenv('NEO4J_USERNAME')
DBPASS =  os.getenv('NEO4J_PASSWORD')

neo4j_driver = AsyncGraphDatabase.driver(
    DBURL,
    auth=(
        DBUSERNAME,
        DBPASS,
    ),
)
def _format_namespace(namespace: str) -> str:
    if namespace:
        if namespace.endswith("-"):
            return namespace
        else:
            return namespace + "-"
    else:
        return ""

async def _read(tx: AsyncTransaction, query: str, params: dict[str, Any]) -> str:
    raw_results = await tx.run(query, params)
    eager_results = await raw_results.to_eager_result()

    return json.dumps([r.data() for r in eager_results.records], default=str)


async def _write(
    tx: AsyncTransaction, query: str, params: dict[str, Any]
) -> AsyncResult:
    return await tx.run(query, params)


def _is_write_query(query: str) -> bool:
    """Check if the query is a write query."""
    return (
        re.search(r"\b(MERGE|CREATE|SET|DELETE|REMOVE|ADD)\b", query, re.IGNORECASE)
        is not None
    )