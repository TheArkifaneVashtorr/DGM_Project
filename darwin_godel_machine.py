# darwin_godel_machine.py
# Janus - General Purpose Solver v2.1

import json
import re
import random
import uuid
import requests
import chromadb
import time
import subprocess # CORRECTED: Added missing import

# --- System Configuration ---
OLLAMA_API_URL = "http://localhost:11434/api/generate"
OLLAMA_TAGS_URL = "http://localhost:11434/api/tags"
CHROMA_HOST = "localhost"
CHROMA_PORT = "8000"
EVOLUTIONARY_ARCHIVE_COLLECTION = "dgm_archive_final" 

# --- Genetic Components ---
AVAILABLE_MODELS = ["codellama:latest", "llama3:latest"]
PROMPT_TEMPLATES = {
    "simple": "Based on the function signature and docstring, generate a complete Python function. Your response must contain ONLY the raw code for the function. Function: ```python\n{function_signature}\n    \"\"\"{docstring}\"\"\"\n```",
    "expert": "As an expert Python programmer, write the body of the following function to meet the requirements in its docstring. The code must be efficient and robust. Return ONLY the raw code for the full function. Function: ```python\n{function_signature}\n    \"\"\"{docstring}\"\"\"\n```"
}

class DarwinGodelMachine:
    """
    An AI that evolves code to solve programming tasks by passing a provided test suite.
    """
    def __init__(self):
        print("Initializing Darwin Gödel Machine v2.1...")
        self.chroma_client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
        self.archive = self.chroma_client.get_or_create_collection(name=EVOLUTIONARY_ARCHIVE_COLLECTION)
        print(f"Successfully connected to ChromaDB. Archive contains {self.archive.count()} items.")
        print("Initialization complete.")

    def _clean_code(self, raw_response):
        """Robustly extracts code from markdown blocks."""
        match = re.search(r'```python\n(.*?)\n```', raw_response, re.DOTALL)
        if match:
            return match.group(1).strip()
        
        # Fallback for code that isn't in a markdown block
        return raw_response.strip().strip('`')

    def _evaluate_fitness(self, generated_code, test_code):
        """
        Executes the generated code against the provided test suite.
        Fitness is the ratio of passing tests.
        """
        if not generated_code or not isinstance(generated_code, str): return 0.0
        
        full_script = generated_code + "\n\n" + test_code

        try:
            process = subprocess.run(
                ['python3', '-c', full_script],
                capture_output=True,
                text=True,
                timeout=15 
            )
            
            if process.returncode == 0:
                print("[Fitness Eval] All tests passed.")
                return 1.0
            else:
                error_output = process.stderr
                print(f"[Fitness Eval] Test execution failed. Error: {error_output.strip()}")
                return 0.1
        except subprocess.TimeoutExpired:
            print("[Fitness Eval] Execution timed out.")
            return 0.0
        except Exception as e:
            print(f"[Fitness Eval] Failed to execute script. Error: {e}")
            return 0.0

    def _generate_variation(self, task_description, function_signature, docstring):
        """Generates a new potential solution."""
        llm_model = random.choice(AVAILABLE_MODELS)
        query_text = task_description
        
        if self.archive.count() > 0 and random.random() < 0.75:
            retrieved_results = self.archive.query(query_texts=[query_text], n_results=1)
            if retrieved_results['ids'] and retrieved_results['ids'][0]:
                ancestor_code = self.archive.get(ids=retrieved_results['ids'][0])['documents'][0]
                print(f"\n--- Found ancestor. Mutating with {llm_model}. ---")
                prompt_text = f"Mutate the following Python code to better solve the described task. Return ONLY the raw code for the full function. Task: '{docstring}'. Original Code: {ancestor_code}"
                prompt_key = "mutation"
            else:
                prompt_key = random.choice(list(PROMPT_TEMPLATES.keys()))
                print(f"\n--- Exploring new solution with {llm_model} and '{prompt_key}' strategy. ---")
                prompt_text = PROMPT_TEMPLATES[prompt_key].format(function_signature=function_signature, docstring=docstring)
        else:
            prompt_key = random.choice(list(PROMPT_TEMPLATES.keys()))
            print(f"\n--- Archive empty or chose exploration. Generating new solution with {llm_model} and '{prompt_key}' strategy. ---")
            prompt_text = PROMPT_TEMPLATES[prompt_key].format(function_signature=function_signature, docstring=docstring)
        
        payload = {"model": llm_model, "prompt": prompt_text, "stream": False}
        try:
            response = requests.post(OLLAMA_API_URL, json=payload, timeout=180)
            response.raise_for_status()
            raw_response = response.json().get('response', '')
            generated_code = self._clean_code(raw_response)
            return generated_code, llm_model, prompt_key
        except requests.exceptions.RequestException as e:
            print(f"ERROR communicating with Ollama: {e}")
            return None, None, None

    def evolve(self, task_description, function_signature, test_code, generations=20):
        """Evolves a solution to pass the provided test suite."""
        print(f"\n=== Starting Evolution for General Task: '{task_description}' for {generations} generations ===")
        best_solution_so_far = {"code": "", "fitness": -1.0}
        docstring = task_description

        for gen in range(generations):
            print(f"\n--- Generation {gen + 1}/{generations} ---")
            generation_result = self._generate_variation(task_description, function_signature, docstring)
            if not generation_result or not generation_result[0]:
                print("Failed to generate code. Skipping generation.")
                continue
            
            generated_code, model, prompt_key = generation_result
            fitness_score = self._evaluate_fitness(generated_code, test_code)
            print(f"Generated Code (Fitness: {fitness_score:.2f}, Model: {model}, Strategy: {prompt_key}):")
            print("-" * 20 + "\n" + generated_code + "\n" + "-" * 20)

            if fitness_score >= 1.0:
                solution_id = str(uuid.uuid4())
                self.archive.add(
                    ids=[solution_id], 
                    documents=[generated_code], 
                    metadatas=[{"task": task_description, "fitness": fitness_score, "model": model, "prompt_key": prompt_key}]
                )
                print(f"PERFECT solution {solution_id[:8]} with fitness {fitness_score:.2f} added to archive.")
                if fitness_score > best_solution_so_far["fitness"]:
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
    
    # --- Define a new task and its test suite ---
    task_description = "Reverses a given string."
    function_signature = "def reverse_string(s: str) -> str:"
    test_code = """
assert reverse_string("hello") == "olleh"
assert reverse_string("world") == "dlrow"
assert reverse_string("") == ""
assert reverse_string("12345") == "54321"
assert reverse_string("Janus") == "sunaJ"
print("All tests passed for reverse_string!")
"""
    
    dgm.evolve(
        task_description=task_description, 
        function_signature=function_signature, 
        test_code=test_code, 
        generations=10
    )
