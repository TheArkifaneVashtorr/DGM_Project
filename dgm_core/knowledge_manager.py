# dgm_core/knowledge_manager.py
import os
import logging
import chromadb
from chromadb.utils import embedding_functions
from config import settings

class KnowledgeManager:
    """
    Manages the DGM's knowledge base using a vector store (ChromaDB).
    It is responsible for loading, embedding, and querying documents.
    """
    COLLECTION_NAME = "dgm_knowledge"

    def __init__(self, source_files: list[str]):
        logging.basicConfig(level=logging.INFO, format='%(message)s')
        self.logger = logging.getLogger(__name__)
        self.source_files = source_files
        self.collection = None
        
        try:
            # Use the default sentence transformer for local embeddings
            self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name="all-MiniLM-L6-v2"
            )
            # Initialize the ChromaDB client with a persistent path
            self.chroma_client = chromadb.PersistentClient(path=settings.CHROMA_DB_PATH)
            
            # Get or create the collection
            self.collection = self.chroma_client.get_or_create_collection(
                name=self.COLLECTION_NAME,
                embedding_function=self.embedding_function
            )
        except Exception as e:
            # This broad exception is to catch potential issues with ChromaDB/SentenceTransformer setup
            # which can be numerous (network, file permissions, etc.)
            raise RuntimeError(f"FATAL: Could not initialize or connect to ChromaDB. Error: {e}")

    def _load_and_process_documents(self) -> tuple[list[str], list[str]]:
        """Loads documents from the knowledge_base directory."""
        documents = []
        ids = []
        for file_name in self.source_files:
            file_path = os.path.join(settings.KNOWLEDGE_BASE_DIR, file_name)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    # Treat each file as a single document
                    documents.append(f.read())
                    ids.append(file_name) # Use filename as the document ID
            except FileNotFoundError:
                self.logger.warning(f"Knowledge source not found, skipping: {file_path}")
            except Exception as e:
                self.logger.error(f"Error reading {file_path}: {e}")
        return documents, ids

    def initialize(self):
        """Initializes the vector store, loading documents if necessary."""
        self.logger.info("Initializing Knowledge Manager...")
        
        # Check if the database already contains the expected documents
        if self.collection.count() >= len(self.source_files):
             self.logger.info("  Knowledge base is already up-to-date.")
             return

        self.logger.info("  Loading knowledge into vector store...")
        documents, ids = self._load_and_process_documents()

        if not documents:
            self.logger.error("No documents found to load into knowledge base.")
            return

        try:
            # Add documents to the collection. ChromaDB handles embedding automatically.
            self.collection.add(
                documents=documents,
                ids=ids
            )
            self.logger.info(f"  Successfully loaded {len(documents)} documents.")
        except Exception as e:
            self.logger.error(f"Failed to add documents to Chroma collection: {e}")

    def query(self, query_text: str, n_results: int = 3) -> list:
        """Queries the knowledge base for relevant documents."""
        if not self.collection:
            self.logger.error("Knowledge collection is not initialized.")
            return []
            
        try:
            results = self.collection.query(
                query_texts=[query_text],
                n_results=n_results
            )
            # The 'documents' key contains a list of lists.
            return [doc for doc in results['documents'][0]]
        except Exception as e:
            self.logger.error(f"An error occurred during knowledge query: {e}")
            return []
