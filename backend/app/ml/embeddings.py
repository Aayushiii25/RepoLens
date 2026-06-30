import logging
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

class EmbeddingService:
    """Service to generate embeddings for semantic search."""
    
    def __init__(self):
        logger.info("Loading SentenceTransformer model (all-MiniLM-L6-v2)...")
        # all-MiniLM-L6-v2 is small, fast, and generates 384-dimensional vectors
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        logger.info("Model loaded successfully.")
    
    def encode(self, text: str | list[str]) -> list[float] | list[list[float]]:
        """Encode text or a list of texts into vector embeddings."""
        embeddings = self.model.encode(text)
        return embeddings.tolist()

# Singleton instance
embedding_service = EmbeddingService()
