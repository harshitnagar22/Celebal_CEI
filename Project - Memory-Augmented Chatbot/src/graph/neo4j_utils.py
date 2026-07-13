from neo4j import GraphDatabase
from src.core.config import config

class Neo4jManager:
    def __init__(self):
        self.uri = config.NEO4J_URI
        self.user = config.NEO4J_USERNAME
        self.password = config.NEO4J_PASSWORD
        self.driver = None
        self._connect()

    def _connect(self):
        try:
            self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
            print("Connected to Neo4j successfully.")
        except Exception as e:
            print(f"Failed to connect to Neo4j: {e}")

    def close(self):
        if self.driver:
            self.driver.close()

    def create_entity(self, label, properties):
        # create a new node
        query = f"MERGE (n:{label} {{name: $name}}) "
        set_clauses = []
        for key in properties:
            if key != 'name':
                set_clauses.append(f"n.{key} = ${key}")
        if set_clauses:
            query += "SET " + ", ".join(set_clauses)
            
        with self.driver.session() as session:
            session.run(query, **properties)

    def create_relationship(self, entity1, label1, entity2, label2, relationship_type):
        # link two nodes together
        query = (
            f"MATCH (a:{label1} {{name: $name1}}) "
            f"MATCH (b:{label2} {{name: $name2}}) "
            f"MERGE (a)-[r:{relationship_type}]->(b)"
        )
        with self.driver.session() as session:
            session.run(query, name1=entity1, name2=entity2)

    def query_graph(self, query, parameters=None):
        # run raw cypher
        if parameters is None:
            parameters = {}
        with self.driver.session() as session:
            result = session.run(query, parameters)
            return [record.data() for record in result]
            
    def get_related_entities(self, entity_name):
        # basic query for context
        query = (
            "MATCH (n {name: $name})-[r]-(m) "
            "RETURN type(r) as relationship, m.name as related_entity, labels(m) as type"
        )
        return self.query_graph(query, {"name": entity_name})

if __name__ == "__main__":
    # Test connection and simple operations
    neo = Neo4jManager()
    if neo.driver:
        # Example insertion
        neo.create_entity("Concept", {"name": "Artificial Intelligence", "description": "Simulation of human intelligence"})
        neo.create_entity("Concept", {"name": "Machine Learning", "description": "Study of algorithms that learn from data"})
        neo.create_relationship("Artificial Intelligence", "Concept", "Machine Learning", "Concept", "INCLUDES")
        
        # Example query
        res = neo.get_related_entities("Artificial Intelligence")
        print("Related to AI:", res)
        neo.close()
