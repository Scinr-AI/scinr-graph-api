from fastapi import FastAPI

import logging

# For routing
from api.graphApiRouter import router as graphApiRouter
from mcp_servers.graphMcp import mcp

from fastapi.middleware.cors import CORSMiddleware

from dotenv import load_dotenv


loaded = load_dotenv(".env")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# stateless_http=True: no server-side sessions — each request is independent.
# This is mandatory for Lambda/serverless where the process dies between invocations.
mcp_app = mcp.http_app(path="/", stateless_http=True)

app = FastAPI(
    title="SCINR Graph Service",
    description="Graph service for read neo4j database operations",
    version="1.0.0",
    root_path="/graphApi",  # Avisa a fastapi que vive debajo de un reverse proxy en ese endpoint
    lifespan=mcp_app.lifespan,  # CRITICAL: initializes the MCP session manager
)

# Mount sub-routers
app.include_router(prefix="/api/graph", router=graphApiRouter)

origins = [
    # '*', # permite todo
    "http://localhost:3000",  # React, Angular, Vue frontend (for example)
    "http://localhost:8001",  # Api and MCP Graph Server
    # "http://localhost:5173",   # Vite frontend
    # "http://127.0.0.1:5500",   # Local static server (e.g., Live Server extension)
    # "http://localhost:8000",   # Another backend (if needed)
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


# Mount MCP server at /mcp — endpoint becomes /graphApi/mcp behind the reverse proxy
app.mount("/mcp", mcp_app)
# host = "0.0.0.0"
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host=host, port=8001)
