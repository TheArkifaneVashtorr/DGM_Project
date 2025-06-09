# knowledge_manager.py
# Manages the RAG knowledge base using ChromaDB.

import os
import chromadb
import config

class KnowledgeManager:
    def __init__(self, source_files):
        print("Initializing Knowledge Manager...")
        self.source_files = source_files
        try:
            self.chroma_client = chromadb.HttpClient(host=config.CHROMA_HOST, port=config.CHROMA_PORT)
            self.knowledge_base = self._initialize_collection()
            self._load_documents()
            print("Knowledge Manager initialized successfully.")
        except Exception as e:
            raise RuntimeError(f"FATAL: Could not connect to ChromaDB. Error: {e}")

    def _initialize_collection(self):
        """Gets or creates the ChromaDB collection, ensuring it's empty first."""
        if config.KNOWLEDGE_BASE_COLLECTION in [c.name for c in self.chroma_client.list_collections()]:
            self.chroma_client.delete_collection(name=config.KNOWLEDGE_BASE_COLLECTION)
        return self.chroma_client.get_or_create_collection(name=config.KNOWLEDGE_BASE_COLLECTION)

    def _load_documents(self):
        """Loads source code and documentation into the knowledge base."""
        print(f"Loading knowledge from '{config.KNOWLEDGE_BASE_DIR}' and source files...")
        
        # Load files from the knowledge_base directory
        for filename in os.listdir(config.KNOWLEDGE_BASE_DIR):
            filepath = os.path.join(config.KNOWLEDGE_BASE_DIR, filename)
            if os.path.isfile(filepath):
                with open(filepath, 'r') as f:
                    self.knowledge_base.add(documents=[f.read()], ids=[filename])

        # Load the machine's own source code
        for filepath in self.source_files:
            if os.path.isfile(filepath):
                with open(filepath, 'r') as f:
                    self.knowledge_base.add(documents=[f.read()], ids=[os.path.basename(filepath)])
        
        print(f"Knowledge base loaded with {self.knowledge_base.count()} document(s).")

    def retrieve_context(self, query, n_results=1):
        """Retrieves relevant context for a given query."""
        if self.knowledge_base.count() == 0:
            return ""
        results = self.knowledge_base.query(query_texts=[query], n_results=n_results)
        return "\n".join(results['documents'][0]) if results and results.get('documents') else ""
