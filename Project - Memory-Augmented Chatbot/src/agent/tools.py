from langchain.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun
from src.rag.vector_db import VectorDBManager
from src.graph.neo4j_utils import Neo4jManager

# Initialize standard search tool
search_tool = DuckDuckGoSearchRun()

# Initialize Vector DB
try:
    vdb = VectorDBManager()
    retriever = vdb.as_retriever()
except Exception as e:
    print(f"Warning: VectorDB not initialized properly. {e}")
    retriever = None

# Initialize Graph DB
try:
    neo = Neo4jManager()
except Exception as e:
    print(f"Warning: Neo4j not initialized properly. {e}")
    neo = None

@tool
def web_search(query: str) -> str:
    """Use this tool to search the web for real-time information that you don't know."""
    return search_tool.invoke(query)

@tool
def query_knowledge_base(query: str) -> str:
    """Use this tool to search the internal knowledge base for specific domain knowledge (AI, ML, LLMs)."""
    if retriever is None:
        return "Internal knowledge base is not available."
    docs = retriever.invoke(query)
    return "\n\n".join([doc.page_content for doc in docs])

@tool
def query_knowledge_graph(entity: str) -> str:
    """Use this tool to find relationships and structured data about a specific entity from the Knowledge Graph."""
    if neo is None or not neo.driver:
        return "Knowledge Graph is not available."
    
    results = neo.get_related_entities(entity)
    if not results:
        return f"No relationships found for {entity}."
    
    formatted_results = []
    for row in results:
        formatted_results.append(f"{entity} --[{row['relationship']}]--> {row['related_entity']}")
    return "\n".join(formatted_results)

tools = [web_search, query_knowledge_base, query_knowledge_graph]
