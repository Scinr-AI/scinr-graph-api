from fastapi import FastAPI
from fastapi_mcp import  FastApiMCP
from fastapi.routing import APIRoute

import logging
# For routing
from api.graphMcpRouter import router as graphMcpRouter
from api.graphApiRouter import router as graphApiRouter

from fastapi.middleware.cors import CORSMiddleware

from dotenv import load_dotenv

loaded = load_dotenv(".env")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



app = FastAPI(
    title="SCINR Graph Service",
    description="Graph service for read neo4j database operations",
    version="1.0.0",
    root_path="/graphApi" # Avisa a fast api que vive debajo de un reverse proxy en ese endpoint, pero el resto de llamadas quedan igual
    
)

# Mount sub-routers
app.include_router(prefix="/api/graph",router=graphApiRouter)
app.include_router(prefix="/graph",router=graphMcpRouter)

origins = [
    # '*', # permite todo
    "http://localhost:3000",  # React, Angular, Vue frontend (for example)
    "http://localhost:8000",  #Api and MCP Graph Server
]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # List of allowed origins
    allow_credentials=True,  # Whether to allow cookies/auth headers
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers
)


@app.get("/")
async def root():
    return {"message": "Hello World"}

def use_route_names_as_operation_ids(app: FastAPI) -> None:
    """
    Simplify operation IDs so that generated API clients have simpler function
    names.

    Should be called only after all routes have been added.
    
    The operationIds are used as the names of the tools exposed in the MCP server.
    This way, the names functions are the names used by the tools, so they should be descriptive and UNIQUE
    The operationIds are used for something else in OpenApi Documentation as well
    """
    for route in app.routes:
        if isinstance(route, APIRoute):
            route.operation_id = route.name  # in this case, 'read_items'

use_route_names_as_operation_ids(app)

mcp = FastApiMCP(app,
                 name="My API MCP",
                description="Very cool MCP server",
                # describe_all_responses=True, #Not very necessary
                # describe_full_response_schema=True,
                include_tags=["MCP"] # exclude_operations=["delete_user"], no al mismo tiempo
               )
# Mount the MCP server directly to your FastAPI app
mcp.mount_http()

# host = "0.0.0.0"
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host=host, port=8001)