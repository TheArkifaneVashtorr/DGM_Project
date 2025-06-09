# darwin_godel_machine.py
# Janus - Final Prototype v1.0

import json
import re
import random
import uuid
import requests
import chromadb
import time

# --- System Configuration ---
OLLAMA_API_URL = "http://localhost:11434/api/generate"
OLLAMA_TAGS_URL = "http://localhost:11434/api/tags"
CHROMA_HOST = "localhost"
CHROMA_PORT = "8000"
EVOLUTIONARY_ARCHIVE_COLLECTION = "dgm_archive_final"

# --- Genetic Components ---
AVAILABLE_MODELS = ["codellama:latest", "llama3:latest"]
PROMPT_TEMPLATES = {
    "simple": "Generate a Python function that {task_description}. Your response must contain ONLY the Python code for the function, and nothing else.",
    "expert": "As an expert Python programmer, write a function that {task_description}. The code must be efficient and robust. Your response must contain ONLY the Python code for the function.",
    "concise": "Write a concise, single Python function for this task: {task_description}. Your response must contain ONLY the Python code for the function.",
}

class DarwinGodelMachine:
    """
    An AI that evolves its own code generation strategies to solve programming tasks.
    It uses a Darwinian process of variation, selection, and inheritance.
    """
    def __init__(self):
        print("Initializing Darwin Gödel Machine...")
        self._health_check()
        try:
            self.chroma_client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
            self.archive = self.chroma_client.get_or_create_collection(name=EVOLUTIONARY_ARCHIVE_COLLECTION)
            print(f"Successfully connected to ChromaDB. Archive contains {self.archive.count()} items.")
        except Exception as e:
            print(f"FATAL: Could not connect to ChromaDB. Error: {e}")
            exit(1)
        print("Initialization complete.")

    def _health_check(self):
        """Ensures the Ollama service is running and has the required models before starting."""
        print("Performing health check on Ollama service...")
        try:
            response = requests.get(OLLAMA_TAGS_URL, timeout=10)
            response.raise_for_status()
            models_data = response.json().get('models', [])
            # Correctly handle model tags like 'codellama:latest'
            model_names = [m['name'] for m in models_data]
            required_models_found = all(any(m.startswith(req) for m in model_names) for req in ["codellama", "llama3"])
            
            print(f"Ollama health check passed. Found models: {model_names}")
            if not required_models_found:
                 print(f"WARNING: Not all required base models found in Ollama.")
        except requests.exceptions.RequestException as e:
            print(f"\nFATAL: Could not connect to Ollama API. Please check Docker services.\nError: {e}\n")
            exit(1)

    def _clean_code(self, raw_response):
        """Robustly extracts code from markdown blocks."""
        if "```python" in raw_response:
            code = raw_response.split("```python")[1].split("```")[0]
        elif "```" in raw_response:
            code = re.search(r'```(.*?)```', raw_response, re.DOTALL).group(1) if re.search(r'```(.*?)```', raw_response, re.DOTALL) else raw_response
        else:
            code = raw_response
        return code.strip('` \n')

    def _evaluate_fitness(self, code, task_description):
        """Evaluates fitness with a task-specific execution test suite."""
        if not code or not isinstance(code, str): return 0.0
        try:
            compile(code, '<string>', 'exec')
        except SyntaxError as e:
            print(f"[Fitness Eval] Syntax Error: {e}. Fitness: 0.0")
            return 0.0
        
        # This is a task-specific test suite. A more advanced DGM would generate this too.
        if "fibonacci" in task_description.lower():
            try:
                namespace = {}
                exec(code, namespace)
                func_name = next((name for name, obj in namespace.items() if callable(obj) and not name.startswith("__")), None)
                if not func_name: raise ValueError("No function found in executed code.")
                
                fib_func = namespace[func_name]
                test_cases = [(0, 0), (1, 1), (2, 1), (5, 5), (8, 21), (10, 55), (12, 144)]
                passed_tests = sum(1 for n, expected in test_cases if fib_func(n) == expected)
                
                test_pass_ratio = passed_tests / len(test_cases)
                print(f"[Fitness Eval] Passed {passed_tests}/{len(test_cases)} execution tests.")
                score = 0.1 + (0.9 * test_pass_ratio)
            except Exception as e:
                print(f"[Fitness Eval] Execution test failed: {e}")
                score = 0.1
        else:
            score = 0.5
        return min(max(score, 0.0), 1.0)

    def _generate_variation(self, task_description):
        """Generates a new potential solution by mutation or fresh generation."""
        llm_model = random.choice(AVAILABLE_MODELS)
        
        # Exploit successful ancestors if they exist, otherwise explore.
        if self.archive.count() > 0 and random.random() < 0.80:
            retrieved_results = self.archive.query(query_texts=[task_description], n_results=1)
            if retrieved_results['ids'] and retrieved_results['ids'][0]:
                ancestor_code = self.archive.get(ids=retrieved_results['ids'][0])['documents'][0]
                print(f"\n--- Found ancestor. Mutating with {llm_model}. ---")
                prompt_text = f"Slightly mutate the following Python code that solves '{task_description}'. Introduce a meaningful variation or optimization. Return ONLY the raw code. Code: {ancestor_code}"
                prompt_key = "mutation"
            else: # Fallback to exploration if retrieval fails
                prompt_key = random.choice(list(PROMPT_TEMPLATES.keys()))
                print(f"\n--- Exploring new solution with {llm_model} and '{prompt_key}' strategy. ---")
                prompt_text = PROMPT_TEMPLATES[prompt_key].format(task_description=task_description)
        else:
            prompt_key = random.choice(list(PROMPT_TEMPLATES.keys()))
            print(f"\n--- Archive empty or chose exploration. Generating new solution with {llm_model} and '{prompt_key}' strategy. ---")
            prompt_text = PROMPT_TEMPLATES[prompt_key].format(task_description=task_description)
        
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

    def evolve(self, task_description, generations=20):
        """Runs the main evolutionary loop to solve a programming task."""
        print(f"\n=== Starting Evolution for Task: '{task_description}' for {generations} generations ===")
        best_solution_so_far = {"code": "", "fitness": -1.0}

        for gen in range(generations):
            print(f"\n--- Generation {gen + 1}/{generations} ---")
            generation_result = self._generate_variation(task_description)
            if not generation_result or not generation_result[0]:
                print("Failed to generate code. Skipping generation.")
                continue
            
            generated_code, model, prompt_key = generation_result
            fitness_score = self._evaluate_fitness(generated_code, task_description)
            print(f"Generated Code (Fitness: {fitness_score:.2f}, Model: {model}, Strategy: {prompt_key}):")
            print("-" * 20 + "\n" + generated_code + "\n" + "-" * 20)

            if fitness_score >= 0.99:
                solution_id = str(uuid.uuid4())
                self.archive.add(ids=[solution_id], documents=[generated_code], metadatas=[{"task": task_description, "fitness": fitness_score, "model": model, "prompt_key": prompt_key}])
                print(f"Solution {solution_id[:8]} with fitness {fitness_score:.2f} added to archive.")
                if fitness_score > best_solution_so_far["fitness"]:
                    best_solution_so_far = {"code": generated_code, "fitness": fitness_score, "generation": gen + 1}

        print("\n=== Evolution Complete ===")
        if best_solution_so_far['fitness'] > 0:
            print("\nBest solution found during this run:")
            print(f"Fitness: {best_solution_so_far['fitness']:.2f} (found in generation {best_solution_so_far['generation']})")
            print(best_solution_so_far['code'])
        else:
            print("\nNo satisfactory solution was found in this evolutionary run.")

if __name__ == "__main__":
    dgm = DarwinGodelMachine()
    coding_task = "create a function that calculates the nth fibonacci number recursively"
    dgm.evolve(task_description=coding_task, generations=15)
