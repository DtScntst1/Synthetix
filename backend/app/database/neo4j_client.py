from neo4j import GraphDatabase, AsyncGraphDatabase
from app.core.config import settings
from app.database.schema import GraphNode, GraphEdge
import logging

logger = logging.getLogger(__name__)

class Neo4jClient:
    def __init__(self):
        self.uri = settings.NEO4J_URI
        self.user = settings.NEO4J_USER
        self.password = settings.NEO4J_PASSWORD
        self._driver = None

    async def connect(self):
        """Initializes the async driver for Neo4j."""
        try:
            self._driver = AsyncGraphDatabase.driver(self.uri, auth=(self.user, self.password))
            await self._driver.verify_connectivity()
            logger.info("Successfully connected to Neo4j Graph Database.")
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            raise e

    async def close(self):
        """Closes the driver connection."""
        if self._driver:
            await self._driver.close()

    async def create_node(self, node: GraphNode):
        """
        Creates or updates a node in the graph, respecting RBAC and temporal metadata.
        """
        query = (
            f"MERGE (n:{node.label} {{id: $id}}) "
            "SET n += $props, "
            "n.valid_from = $valid_from, "
            "n.valid_to = $valid_to, "
            "n.clearance_level = $clearance_level, "
            "n.source_document_id = $source_document_id, "
            "n.source_page_number = $source_page_number "
            "RETURN n"
        )
        
        async with self._driver.session() as session:
            result = await session.run(
                query,
                id=node.id,
                props=node.properties,
                valid_from=node.valid_from.isoformat() if node.valid_from else None,
                valid_to=node.valid_to.isoformat() if node.valid_to else None,
                clearance_level=node.clearance_level,
                source_document_id=node.source_document_id,
                source_page_number=node.source_page_number
            )
            return await result.single()

    async def create_edge(self, edge: GraphEdge):
        """
        Creates a relationship between two nodes. Nodes must exist.
        """
        query = (
            "MATCH (a {id: $source_id}) "
            "MATCH (b {id: $target_id}) "
            f"MERGE (a)-[r:{edge.type}]->(b) "
            "SET r += $props, "
            "r.valid_from = $valid_from, "
            "r.valid_to = $valid_to "
            "RETURN r"
        )
        
        async with self._driver.session() as session:
            result = await session.run(
                query,
                source_id=edge.source_id,
                target_id=edge.target_id,
                props=edge.properties,
                valid_from=edge.valid_from.isoformat() if edge.valid_from else None,
                valid_to=edge.valid_to.isoformat() if edge.valid_to else None
            )
            return await result.single()

neo4j_client = Neo4jClient()
