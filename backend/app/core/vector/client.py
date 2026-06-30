import logging
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

logger = logging.getLogger(__name__)


class VectorDBClient:
    """Singleton for Qdrant Vector DB."""

    def __init__(self):
        # For development, we use an in-memory Qdrant instance.
        # In production, this would point to a real Qdrant cluster.
        self.client = AsyncQdrantClient(location=":memory:")
        self.collection_name = "repositories"
        self._initialized = False

    async def init_collection(self):
        if self._initialized:
            return
        
        exists = await self.client.collection_exists(self.collection_name)
        if not exists:
            await self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=384, distance=Distance.COSINE),
            )
            logger.info(f"Created Qdrant collection: {self.collection_name}")
        self._initialized = True

    async def upsert_repository(self, repo_id: str, vector: list[float], payload: dict):
        await self.init_collection()
        await self.client.upsert(
            collection_name=self.collection_name,
            points=[
                PointStruct(
                    id=repo_id,
                    vector=vector,
                    payload=payload
                )
            ]
        )

    async def search(self, vector: list[float], limit: int = 10) -> list[dict]:
        await self.init_collection()
        results = await self.client.search(
            collection_name=self.collection_name,
            query_vector=vector,
            limit=limit,
        )
        return [
            {
                "id": hit.id,
                "score": hit.score,
                "payload": hit.payload
            }
            for hit in results
        ]

vector_db = VectorDBClient()
