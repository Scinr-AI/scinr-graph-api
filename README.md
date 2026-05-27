# SCINR Graph Service

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

> SCINR is the first AI-native supply chain autonomous orchestration platform purpose-built for the life sciences industry. It embeds AI at every step of the supply chain — enabling master data orchestration, continuous planning, and self-healing resiliency — to help pharmaceutical and biotech companies prevent medicine shortages, accelerate time-to-market, and maintain full regulatory compliance. Learn more at [scinr.com](https://www.scinr.com/).

The **SCINR Graph Service** is a FastAPI microservice that exposes Neo4j graph database read operations via a REST API and an integrated **MCP (Model Context Protocol) server**. It is a core component of the SCINR platform, enabling AI agents and external clients to query the supply chain knowledge graph safely and efficiently.

---

## 📋 Table of Contents

- [Tech Stack](#-tech-stack)
- [Prerequisites](#-prerequisites)
- [Project Structure](#-project-structure)
- [Installation](#-installation)
- [Environment Variables](#-environment-variables)
- [PYTHONPATH Configuration](#-pythonpath-configuration)
- [Running the Service](#-running-the-service)
- [API Endpoints](#-api-endpoints)
- [MCP Integration](#-mcp-integration)
- [Architecture Notes](#-architecture-notes)
- [License](#license)

---

## 🛠 Tech Stack

| Component | Version |
|---|---|
| Python | ≥ 3.14 |
| FastAPI | latest |
| `fastmcp` | ≥ 3.2.4 |
| `neo4j` Python driver | ≥ 6.2.0 |
| `uvicorn` | ASGI server |
| `uv` | Recommended package manager |

---

## ✅ Prerequisites

- **Python 3.14+**
- **`uv`** (recommended package manager — [install guide](https://docs.astral.sh/uv/getting-started/installation/))
- A **Neo4j database instance** with the **APOC plugin** installed and enabled (required for the `/schema` endpoint)

---

## 📁 Project Structure

```
graphApi/
├── src/
│   ├── main.py                  # App entry point, FastAPI + MCP setup
│   ├── api/
│   │   └── graphApiRouter.py    # Public REST API routes
│   ├── mcp_servers/
│   │   └── graphMcp.py          # FastMCP server definition & tools
│   ├── models/
│   │   └── graphModels.py       # Pydantic request/response models
│   └── utils/
│       └── neo4jUtils.py        # Neo4j driver & query helpers
├── pyproject.toml
├── uv.lock
└── .env
```

---

## 🚀 Installation

### Using `uv` (recommended)

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd graphApi
   ```

2. **Create a virtual environment**

   ```bash
   uv venv
   ```

3. **Activate the virtual environment**

   | Platform | Command |
   |---|---|
   | Linux / macOS | `source .venv/bin/activate` |
   | Windows CMD | `.venv\Scripts\activate` |
   | Windows PowerShell | `.venv\Scripts\Activate.ps1` |

4. **Install dependencies**

   ```bash
   uv sync
   ```

---

## 🔐 Environment Variables

Create a `.env` file at the root of the project with the following variables:

```dotenv
NEO4J_URI=neo4j+s://xxxx.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password
```

| Variable | Description | Example |
|---|---|---|
| `NEO4J_URI` | Connection URI for the Neo4j instance | `neo4j+s://xxxx.databases.neo4j.io` |
| `NEO4J_USERNAME` | Neo4j database username | `neo4j` |
| `NEO4J_PASSWORD` | Neo4j database password | `your_password` |

> ⚠️ **Do not commit your `.env` file.** It is already listed in `.gitignore`.

---

## 🐍 PYTHONPATH Configuration

Before running the application, set the `PYTHONPATH` environment variable to `src/` so Python can resolve internal module imports correctly.

```bash
# Linux / macOS
export PYTHONPATH=src/

# Windows CMD
set PYTHONPATH=src\

# Windows PowerShell
$env:PYTHONPATH="src/"
```

---

## ▶️ Running the Service

Once the environment variables and `PYTHONPATH` are configured, start the service with:

```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

| Resource | URL |
|---|---|
| REST API | `http://localhost:8000` |
| Swagger UI (interactive docs) | `http://localhost:8000/docs` |
| MCP Server | `http://localhost:8000/mcp` |

---

## 📡 API Endpoints

| Method | Path | Description | Access |
|---|---|---|---|
| `GET` | `/` | Health check | Public |
| `GET` | `/api/graph/schema` | Retrieve the full Neo4j graph schema (requires APOC plugin) | Public |
| `POST` | `/api/graph/read` | Execute a Cypher read query against the database | Public |

### `POST /api/graph/read` — Request Body

```json
{
  "query": "MATCH (n:Person) RETURN n LIMIT 10",
  "params": {}
}
```

> ⚠️ **Only read queries are allowed.** Write operations (`MERGE`, `CREATE`, `SET`, `DELETE`, etc.) are explicitly blocked at the application level.

---

## 🤖 MCP Integration

This service embeds a **Model Context Protocol (MCP) server** powered by [`fastmcp`](https://github.com/jlowin/fastmcp). The MCP server is mounted at `/mcp` and uses **stateless HTTP transport** (`stateless_http=True`), making it fully compatible with serverless deployments (e.g., AWS Lambda) where no persistent session state is maintained between requests.

### Available MCP Tools

| Tool | Description |
|---|---|
| `get_schema` | Lists all nodes, their properties, and relationships in the database |
| `read_neo4j_cypher` | Executes a Cypher read query and returns the results |

### Connecting an MCP Client

**Claude Desktop** — add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "scinr-graph": {
      "type": "http",
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

**Cursor** — add to `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "scinr-graph": {
      "type": "http",
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

---

## 🏗 Architecture Notes

- **Reverse Proxy**: The application is configured with `root_path="/graphApi"`, meaning it is designed to run behind a reverse proxy that forwards requests under that path prefix.

- **CORS**: Cross-Origin Resource Sharing is enabled for `http://localhost:3000` and `http://localhost:8000` by default. Update `origins` in `src/main.py` to match your frontend or client URLs.

- **MCP Stateless Transport**: The MCP server uses `stateless_http=True`, meaning each request is fully independent with no server-side session state. This is required for serverless deployments (e.g., AWS Lambda) where the process may be recycled between invocations. MCP tools call the REST handler functions directly in-process — no internal HTTP round-trip.

- **Read-Only**: The service only performs read operations on the Neo4j database. Write queries are rejected at the application level before reaching the database.

---

## License

This project is licensed under the **Apache License 2.0** — see the [LICENSE](./LICENSE) file for details.

Copyright 2026 SCINR

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

---

<p align="center">
  Built with ❤️ for the SCINR platform &mdash; <a href="https://www.scinr.com/">scinr.com</a>
</p>
