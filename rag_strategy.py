# rag_strategy.py (Refactored for Planner-Coder Architecture)
# The execute method now implements a Plan -> Code -> Test -> Debug workflow.

import os
import uuid
import time
import hashlib
import chromadb
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain_ollama import OllamaLLM, OllamaEmbeddings
import config
from fitness import evaluate_fitness

class RAGStrategy:
    def execute(self, query: str):
        raise NotImplementedError

class ConcreteRAGStrategy(RAGStrategy):
    def __init__(self, **genome):
        self.genome = genome
        self.llm = None
        self.retriever = None
        self._initialize_components()

    def _initialize_components(self):
        try:
            self.llm = OllamaLLM(
                base_url=config.OLLAMA_BASE_URL,
                model=self.genome['generator_model'],
                temperature=self.genome['temperature']
            )
            embeddings = OllamaEmbeddings(
                base_url=config.OLLAMA_BASE_URL,
                model=self.genome['embedding_model']
            )
            loader = DirectoryLoader(config.KNOWLEDGE_BASE_DIR, glob=config.DOCUMENT_GLOB_PATTERN, loader_cls=TextLoader)
            documents = loader.load()
            if not documents: return

            text_splitter = RecursiveCharacterTextSplitter(chunk_size=self.genome['chunk_size'], chunk_overlap=self.genome['chunk_size'] // 5)
            texts = text_splitter.split_documents(documents)
            
            client = chromadb.EphemeralClient()
            vector_store = Chroma.from_documents(
                documents=texts, embedding=embeddings, client=client, collection_name=uuid.uuid4().hex
            )
            self.retriever = vector_store.as_retriever(search_kwargs={"k": self.genome['top_k']})
        except Exception as e:
            print(f"Error initializing RAG components: {e}")

    def execute(self, query: str) -> dict:
        if not self.llm or not self.retriever:
            return {"result": "ERROR: Initialization failed.", "final_fitness": 0.0, "total_time": 0, "error_message": "Initialization failed."}

        start_time = time.time()
        
        # --- 1. PLANNER STEP ---
        print("--- Agent engaging Planner... ---")
        context_docs = self.retriever.get_relevant_documents(query)
        context_str = "\n\n".join([doc.page_content for doc in context_docs])
        
        planner_prompt = PromptTemplate.from_template(config.PLANNER_PROMPT_TEMPLATE)
        planner_chain = planner_prompt | self.llm | StrOutputParser()
        plan = planner_chain.invoke({"context": context_str, "query": query})
        print(f"--- Generated Plan ---\n{plan}\n--------------------")

        # --- 2. CODER STEP (First Attempt) ---
        print("--- Agent engaging Coder... ---")
        coder_prompt = PromptTemplate.from_template(config.CODER_PROMPT_TEMPLATE)
        coder_chain = coder_prompt | self.llm | StrOutputParser()
        first_attempt_code = coder_chain.invoke({"context": context_str, "query": query, "plan": plan})

        # --- 3. First Evaluation ---
        fitness_score, error_message = evaluate_fitness(first_attempt_code, 1.0)
        
        if error_message is None:
            print("--- First attempt SUCCEEDED. ---")
            total_time = time.time() - start_time
            final_fitness, _ = evaluate_fitness(first_attempt_code, total_time)
            return {"result": first_attempt_code, "final_fitness": final_fitness, "total_time": total_time, "error_message": None}
            
        # --- 4. DEBUGGER STEP ---
        print("--- First attempt FAILED. Engaging Debugger... ---")
        debug_prompt = PromptTemplate.from_template(config.DEBUGGING_PROMPT_TEMPLATE)
        debug_chain = debug_prompt | self.llm | StrOutputParser()
        
        corrected_code = debug_chain.invoke({
            "plan": plan,
            "faulty_code": first_attempt_code,
            "error_message": error_message
        })
        
        total_time = time.time() - start_time
        final_fitness, final_error_message = evaluate_fitness(corrected_code, total_time)
        
        return {"result": corrected_code, "final_fitness": final_fitness, "total_time": total_time, "error_message": final_error_message}
