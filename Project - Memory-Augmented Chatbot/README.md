# Memory-Augmented Chatbot

A production-ready memory-augmented chatbot system combining Retrieval-Augmented Generation (RAG), a Knowledge Graph, and long-term user memory to deliver context-aware and personalized responses.

This project uses **LangGraph** as the agent orchestration engine, **FastAPI** for the backend, **Neo4j** for structured knowledge storage, and **Chroma** (via LangChain) for vector storage.

## Features

- **Long-Term Memory:** Uses LangGraph check-pointing (SQLite) to maintain conversation history across sessions.
- **Hybrid Retrieval System:** Combines vector-based semantic search with Knowledge Graph structured querying.
- **Dynamic Tool Integration:** Leverages DuckDuckGo search API to answer real-time queries.
- **Data Pipeline:** Includes web scrapers (BeautifulSoup) for automated knowledge ingestion.
- **Evaluation Framework:** Includes a basic script to evaluate chatbot responses.

## Prerequisites

- Python 3.9+
- Docker (for local Neo4j database)

## Setup Instructions

### 1. Environment Configuration

Copy the example environment file and configure it:

```bash
cp .env.example .env
```

Open `.env` and configure:
- `GOOGLE_API_KEY`: Your Gemini API key.
- `NEO4J_URI`, `NEO4J_USERNAME`, `NEO4J_PASSWORD`: Set up for local Neo4j (via Docker) or use Neo4j Aura cloud.

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Start Neo4j (Optional if using AuraDB)

If you're using a local Neo4j database, start it using Docker:

```bash
docker-compose up -d
```
The Neo4j browser will be available at `http://localhost:7474`.

### 4. Data Ingestion (One-time setup)

Run the scraper to build the local dataset (scrapes AI-related topics from Wikipedia):

```bash
python -m src.data_pipeline.scraper
```

Clean and chunk the scraped data:

```bash
python -m src.data_pipeline.cleaner
```

Populate the Vector DB:

```bash
python -m src.rag.vector_db
```

*Note: You can manually populate Neo4j via the `src/graph/neo4j_utils.py` test block to see graph relationships in action.*

## Running the Application

### Option A: Command-Line Interface (CLI)
You can run the agent directly in the terminal to test memory and tools:

```bash
python -m src.agent.graph
```

### Option B: FastAPI Server
Start the backend server:

```bash
python -m src.api.main
```
The API documentation (Swagger UI) will be available at `http://localhost:8000/docs`.

## Evaluation
Run the automated evaluation suite:

```bash
python -m src.evaluation.evaluator
```

## Tech Stack
- **Language**: Python
- **LLM Engine**: Gemini 1.5 Flash (via LangChain / LangGraph)
- **Vector Database**: Chroma
- **Graph Database**: Neo4j
- **API Framework**: FastAPI
