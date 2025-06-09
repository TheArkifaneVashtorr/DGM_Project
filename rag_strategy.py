# rag_strategy.py (Architecturally Hardened)
# Implements the Strategy design pattern with fully isolated components.

import os
# FIX: Import uuid to generate unique identifiers.
import uuid
import chromadb
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain_ollama import OllamaLLM, OllamaEmbeddings
import config

class RAGStrategy:
    """Abstract base class for a RAG strategy."""
    def execute(self, query: str):
        raise NotImplementedError("This method should be overridden by subclasses.")

class ConcreteRAGStrategy(RAGStrategy):
    """
    Represents a specific, executable RAG pipeline configuration.
    """
    def __init__(self, embedding_model: str, generator_model: str, prompt_template: str):
        self.embedding_model = embedding_model
        self.generator_model = generator_model
        self.prompt_template_str = prompt_template
        self.qa_chain = None

        print(f"Initializing Strategy: Embed='{self.embedding_model}', Gen='{self.generator_model}'")
        self._initialize_components()

    def _initialize_components(self):
        """Initializes components with a uniquely named, isolated vector store and an explicit LCEL chain."""
        try:
            embeddings = OllamaEmbeddings(
                base_url=config.OLLAMA_BASE_URL,
                model=self.embedding_model
            )
            llm = OllamaLLM(
                base_url=config.OLLAMA_BASE_URL,
                model=self.generator_model
            )

            loader = DirectoryLoader(
                config.KNOWLEDGE_BASE_DIR,
                glob=config.DOCUMENT_GLOB_PATTERN,
                loader_cls=TextLoader
            )
            documents = loader.load()
            
            if not documents:
                print("Warning: No documents found in the knowledge base.")
                self.qa_chain = None
                return

            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            texts = text_splitter.split_documents(documents)
            
            client = chromadb.EphemeralClient()

            # FIX: Provide a unique collection name for every instance.
            # This is the final step to ensure complete vector store isolation
            # and resolve the dimensionality conflict permanently.
            unique_collection_name = uuid.uuid4().hex
            vector_store = Chroma.from_documents(
                documents=texts,
                embedding=embeddings,
                client=client,
                collection_name=unique_collection_name
            )
            retriever = vector_store.as_retriever()

            prompt = PromptTemplate(
                template=self.prompt_template_str,
                input_variables=["context", "query"]
            )
            
            self.qa_chain = (
                {"context": retriever, "query": RunnablePassthrough()}
                | prompt
                | llm
                | StrOutputParser()
            )

        except Exception as e:
            print(f"Error initializing RAG components: {e}")
            self.qa_chain = None

    def execute(self, query: str) -> dict:
        """Executes the RAG query and returns the result."""
        if not self.qa_chain:
            print("Cannot execute strategy: QA chain not initialized.")
            return {"result": "ERROR: Initialization failed."}
            
        print(f"Executing query: '{query}' with strategy.")
        try:
            result_str = self.qa_chain.invoke(query)
            return {"result": result_str}
        except Exception as e:
            print(f"Error during strategy execution: {e}")
            return {"result": f"ERROR: Execution failed. Details: {e}"}

def example_function_to_refactor():
    # This is an inefficient example.
    my_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    evens = []
    for item in my_list:
        if item % 2 == 0:
            evens.append(item)
    return evens
