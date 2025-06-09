# dgm_core/knowledge_manager.py
# This module manages the system's long-term, persistent memory using a vector store.

import chromadb
import config.settings as settings

class KnowledgeManager:
    """
    Manages the persistent knowledge base (vector store) for the DGM.
    It handles loading, retrieving, and managing the system's own source code as knowledge.
    """
    def __init__(self, source_files: list):
        """
        Initializes the Knowledge Manager, sets up the ChromaDB client,
        and ensures the knowledge base is loaded.

        Args:
            source_files (list): A list of paths to the source code files
                                 that form the system's knowledge base.
        """
        print("Initializing Knowledge Manager...")
        try:
            # Use PersistentClient to store the database locally. This is more robust
            # and self-contained than requiring a separate running server.
            self.chroma_client = chromadb.PersistentClient(path=settings.CHROMA_DB_PATH)
            
            self.collection = self.chroma_client.get_or_create_collection(
                name=settings.COLLECTION_NAME
            )
            
            # Ensure the knowledge base is populated
            self._load_knowledge(source_files)
            print("Knowledge Manager initialized successfully.")

        except Exception as e:
            # Catching a broad exception here because chromadb can raise various errors
            # during initialization, and we want to provide a clear, fatal error message.
            raise RuntimeError(f"FATAL: Could not initialize or connect to ChromaDB. Error: {e}")

    def _load_knowledge(self, source_files: list):
        """
        Loads the content of the system's source files into the vector store.
        This process is idempotent; it won't duplicate existing documents.
        """
        print("  Loading knowledge into vector store...")
        doc_ids = [src.replace('/', '_') for src in source_files]
        
        # Check which documents already exist to avoid reprocessing
        existing_ids = set(self.collection.get(ids=doc_ids)['ids'])
        
        docs_to_add = []
        ids_to_add = []

        for src_file, doc_id in zip(source_files, doc_ids):
            if doc_id not in existing_ids:
                try:
                    with open(src_file, 'r') as f:
                        docs_to_add.append(f.read())
                        ids_to_add.append(doc_id)
                except FileNotFoundError:
                    print(f"Warning: Source file not found during knowledge loading: {src_file}")
        
        if docs_to_add:
            print(f"  Adding {len(docs_to_add)} new document(s) to the collection...")
            self.collection.add(
                documents=docs_to_add,
                ids=ids_to_add
            )
        else:
            print("  Knowledge base is already up-to-date.")

    def retrieve_context(self, query: str, n_results: int = 3) -> str:
        """
        Retrieves relevant context from the knowledge base for a given query.

        Args:
            query (str): The query or task description to find context for.
            n_results (int): The number of relevant documents to retrieve.

        Returns:
            str: A formatted string containing the retrieved context, or an empty string.
        """
        if not query:
            return ""
            
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results
            )
            context = "\n".join(results['documents'][0])
            return context
        except Exception as e:
            print(f"Error retrieving context from ChromaDB: {e}")
            return ""
