# darwin_godel_machine.py
# Janus - Darwinian RAG v3.0

import json
import re
import random
import uuid
import requests
import chromadb
import time
import subprocess
import os

# --- System Configuration ---
OLLAMA_API_URL = "http://localhost:11434/api/generate"
CHROMA_HOST = "localhost"
CHROMA_PORT = "8000"
KNOWLEDGE_BASE_COLLECTION = "dgm_knowledge_base"
EVOLUTIONARY_ARCHIVE_COLLECTION = "dgm_evolutionary_archive"
KNOWLEDGE_BASE_DIR = "./knowledge_base"

# --- Genetic Components ---
AVAILABLE_MODELS = ["codellama:latest", "llama3:latest"]
PROMPT_TEMPLATE = """
Based on the following CONTEXT, write a Python function that correctly implements the TASK.
Your response must contain ONLY the raw code for the function.

CONTEXT:
---
{context}
---

TASK:
---
{task_description}
---
"""

class DarwinGodelMachine:
    """
    An AI that uses a Retrieval-Augmented Generation (RAG) pipeline
    to evolve code that solves problems based on an external knowledge base.
    """
    def __init__(self):
        print("Initializing Darwinian RAG v3.0...")
        try:
            self.chroma_client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
            self.knowledge_base = self.chroma_client.get_or_create_collection(name=KNOWLEDGE_BASE_COLLECTION)
            self.archive = self.chroma_client.get_or_create_collection(name=EVOLUTIONARY_ARCHIVE_COLLECTION)
            print("Successfully connected to ChromaDB.")
            self._load_knowledge_base()
        except Exception as e:
            print(f"FATAL: Could not connect to services. Error: {e}")
            exit(1)
        print("Initialization complete.")

    def _load_knowledge_base(self):
        """
        Reads documents, chunks them, and stores their embeddings in ChromaDB.
        """
        print(f"Loading knowledge from '{KNOWLEDGE_BASE_DIR}'...")
        if self.knowledge_base.count() > 0:
            print("Knowledge base is already loaded.")
            return

        try:
            for filename in os.listdir(KNOWLEDGE_BASE_DIR):
                filepath = os.path.join(KNOWLEDGE_BASE_DIR, filename)
                if os.path.isfile(filepath):
                    with open(filepath, 'r') as f:
                        content = f.read()
                        # Simple chunking by paragraph
                        chunks = [chunk for chunk in content.split('\n\n') if chunk.strip()]
                        for i, chunk in enumerate(chunks):
                            chunk_id = f"{filename}-{i}"
                            self.knowledge_base.add(documents=[chunk], ids=[chunk_id])
            print(f"Knowledge base loaded with {self.knowledge_base.count()} document chunks.")
        except FileNotFoundError:
            print(f"ERROR: Knowledge base directory '{KNOWLEDGE_BASE_DIR}' not found.")
        except Exception as e:
            print(f"ERROR: Failed to load knowledge base. {e}")
            
    def _retrieve_context(self, query, n_results=2):
        """Retrieves relevant context from the knowledge base."""
        results = self.knowledge_base.query(query_texts=[query], n_results=n_results)
        return "\n".join(results['documents'][0]) if results['documents'] else ""

    def _evaluate_fitness(self, generated_code, test_code):
        """Executes generated code against a test suite to determine fitness."""
        if not generated_code: return 0.0
        full_script = generated_code + "\n\n" + test_code
        try:
            process = subprocess.run(['python3', '-c', full_script], capture_output=True, text=True, timeout=15)
            if process.returncode == 0:
                print("[Fitness Eval] All tests passed.")
                return 1.0
            else:
                print(f"[Fitness Eval] Test execution failed. Error: {process.stderr.strip()}")
                return 0.1
        except Exception as e:
            print(f"[Fitness Eval] Failed to execute script. Error: {e}")
            return 0.0

    def _generate_variation(self, task_description):
        """Uses RAG to generate a solution."""
        llm_model = random.choice(AVAILABLE_MODELS)
        
        context = self._retrieve_context(task_description)
        if not context:
            print("WARNING: No relevant context found in the knowledge base for this task.")

        print(f"--- Retrieved Context ---\n{context}\n-------------------------")
        
        prompt_text = PROMPT_TEMPLATE.format(context=context, task_description=task_description)
        
        payload = {"model": llm_model, "prompt": prompt_text, "stream": False}
        try:
            response = requests.post(OLLAMA_API_URL, json=payload, timeout=180)
            response.raise_for_status()
            raw_response = response.json().get('response', '')
            generated_code = raw_response.strip('` \n')
            return generated_code, llm_model
        except requests.exceptions.RequestException as e:
            print(f"ERROR communicating with Ollama: {e}")
            return None, None

    def evolve(self, task_description, test_code, generations=10):
        """Evolves a solution using the RAG pipeline."""
        print(f"\n=== Starting RAG Evolution for Task: '{task_description}' for {generations} generations ===")
        best_solution_so_far = {"code": "", "fitness": -1.0}

        for gen in range(generations):
            print(f"\n--- Generation {gen + 1}/{generations} ---")
            generation_result = self._generate_variation(task_description)
            
            if not generation_result or not generation_result[0]:
                print("Failed to generate code. Skipping generation.")
                continue
            
            generated_code, model = generation_result
            fitness_score = self._evaluate_fitness(generated_code, test_code)
            
            print(f"Generated Code (Fitness: {fitness_score:.2f}, Model: {model}):")
            print("-" * 20 + "\n" + generated_code + "\n" + "-" * 20)

            if fitness_score >= 1.0:
                print("PERFECT solution found. Halting evolution.")
                best_solution_so_far = {"code": generated_code, "fitness": fitness_score, "generation": gen + 1}
                break

        print("\n=== Evolution Complete ===")
        if best_solution_so_far['fitness'] >= 1.0:
            print("\nPerfect solution found:")
            print(f"Fitness: {best_solution_so_far['fitness']:.2f} (found in generation {best_solution_so_far['generation']})")
            print(best_solution_so_far['code'])
        else:
            print("\nNo perfect solution was found in this evolutionary run.")

if __name__ == "__main__":
    dgm = DarwinGodelMachine()
    
    task_description = "Create the 'apply_transaction_fee' function as specified in the documentation."
    
    test_code = """
def test_fee_application():
    assert apply_transaction_fee(1000) == 1005, "Should add 5 cents to 1000"
    assert apply_transaction_fee(0) == 5, "Should add 5 cents to 0"
    assert apply_transaction_fee(999995) == 1000000, "Should handle large numbers"

test_fee_application()
print("All tests for apply_transaction_fee passed!")
"""
    
    dgm.evolve(
        task_description=task_description, 
        test_code=test_code, 
        generations=5
    )
