# dgm_core.py
# Janus - Self-Modifying Machine v4.5 (Hardened)

import os
import requests
import chromadb
import random
import json
import subprocess
import re
import shutil
import time

# Import from our new modules
import config
from dgm_tools import evaluate_fitness, clean_code

class DarwinGodelMachine:
    """The main class orchestrating the evolution and self-modification loops."""
    
    def __init__(self, source_files):
        print("Initializing Self-Modifying Machine v4.5...")
        self.source_files = source_files
        try:
            self.chroma_client = chromadb.HttpClient(host=config.CHROMA_HOST, port=config.CHROMA_PORT)
            self.knowledge_base = self.chroma_client.get_or_create_collection(name=config.KNOWLEDGE_BASE_COLLECTION)
            self._load_knowledge_base()
        except Exception as e:
            print(f"FATAL: Could not connect to services. Error: {e}")
            exit(1)
        print("Initialization complete.")

    def _load_knowledge_base(self):
        """Loads or re-loads documents from the knowledge base directory."""
        print(f"Loading knowledge from '{config.KNOWLEDGE_BASE_DIR}'...")
        if self.knowledge_base.count() > 0:
            self.chroma_client.delete_collection(name=config.KNOWLEDGE_BASE_COLLECTION)
        self.knowledge_base = self.chroma_client.get_or_create_collection(name=config.KNOWLEDGE_BASE_COLLECTION)
        
        for filename in self.source_files:
            if os.path.isfile(filename):
                with open(filename, 'r') as f:
                    content = f.read()
                    self.knowledge_base.add(documents=[content], ids=[filename])
        print(f"Knowledge base loaded with {self.knowledge_base.count()} source file(s).")
            
    def _retrieve_context(self, query, n_results=1):
        """Retrieves relevant context from the knowledge base."""
        results = self.knowledge_base.query(query_texts=[query], n_results=n_results)
        return "\n".join(results['documents'][0]) if results and results['documents'] else ""

    def _generate_solution(self, task_description):
        """Generates a single solution attempt using the RAG pipeline."""
        llm_model = random.choice(config.AVAILABLE_MODELS)
        context = self._retrieve_context(task_description)
        prompt = config.RAG_PROMPT_TEMPLATE.format(context=context, task_description=task_description)
        payload = {"model": llm_model, "prompt": prompt, "stream": False}
        try:
            response = requests.post(config.OLLAMA_API_URL, json=payload, timeout=180)
            response.raise_for_status()
            raw_response = response.json().get('response', '')
            return clean_code(raw_response)
        except requests.exceptions.RequestException as e:
            print(f"ERROR: Ollama communication failed: {e}")
            return None

    def evolve(self, task_description, test_code, max_generations=10):
        """Evolves a solution for a given task, returns generations taken."""
        for gen in range(1, max_generations + 1):
            code = self._generate_solution(task_description)
            if evaluate_fitness(code, test_code) == 1:
                print(f"Solved '{task_description}' in {gen} generation(s).")
                return gen
        print(f"Failed to solve '{task_description}' within {max_generations} generations.")
        return max_generations + 1

    def evolve_self(self, benchmark_file):
        """The META-EVOLUTION LOOP. The machine attempts to improve itself."""
        print("\n\n=== META-EVOLUTION PROTOCOL INITIATED ===")
        print("\n--- Phase 1: Establishing Baseline Performance ---")
        with open(benchmark_file, 'r') as f:
            benchmark_suite = json.load(f)
        total_gens = sum(self.evolve(task['task_description'], task['test_code']) for task in benchmark_suite)
        baseline_score = total_gens / len(benchmark_suite)
        print(f"\nBASELINE PERFORMANCE: Average of {baseline_score:.2f} generations per task.")

        print("\n--- Phase 2: Proposing Self-Modification ---")
        target_file_to_improve = 'config.py'
        print(f"Attempting to evolve the RAG prompt in '{target_file_to_improve}'...")
        with open(target_file_to_improve, 'r') as f:
            source_code = f.read()
        
        prompt = config.SELF_MODIFY_PROMPT_TEMPLATE.format(source_code=source_code)
        payload = {"model": "llama3:latest", "prompt": prompt, "stream": False, "options": {"temperature": 0.25}}
        print("Generating mutant version of config...")
        try:
            response = requests.post(config.OLLAMA_API_URL, json=payload, timeout=300)
            response.raise_for_status()
            mutant_code = clean_code(response.json().get('response', ''))
            
            # FINAL VALIDATION STEP: Compile the proposed code to check for syntax errors.
            try:
                compile(mutant_code, '<string>', 'exec')
                print("Validation successful: Generated mutant code is syntactically correct.")
            except SyntaxError as e:
                print("\n" + "="*60)
                print("MUTATION REJECTED: LLM generated syntactically invalid code.")
                print(f"This is a successful test of the system's new validation layer.")
                print(f"Error details: {e}")
                print("="*60 + "\n")
                return # Halt this meta-evolution attempt

            mutant_package_dir = self._package_mutant(target_file_to_improve, mutant_code)
            print(f"Mutant package created at '{mutant_package_dir}'.")

        except requests.exceptions.RequestException as e:
            print(f"ERROR: Failed to generate mutant. {e}")
            return
        
        print("\n--- Phase 3: Testing Mutant Performance ---")
        try:
            # We must use the mutant's own runner script
            mutant_runner_path = os.path.join(mutant_package_dir, 'run_dgm.py')
            process = subprocess.run(
                ['python3', mutant_runner_path, 'run_benchmark'], 
                capture_output=True, text=True, timeout=600,
                cwd=mutant_package_dir # IMPORTANT: Run the process from within the mutant's directory
            )
            if process.returncode != 0:
                print(f"MUTANT FAILED TO RUN. Discarding. Error:\n{process.stderr}")
                return
            
            output = process.stdout
            match = re.search(r'MUTANT BENCHMARK: Average of ([\d.]+) generations per task.', output)
            if not match:
                print(f"MUTANT FAILED TO REPORT SCORE. Discarding. Output:\n{output}")
                return
            mutant_score = float(match.group(1))
            print(f"MUTANT PERFORMANCE: Average of {mutant_score:.2f} generations per task.")

            print("\n--- Phase 4: Selection ---")
            if mutant_score < baseline_score:
                print("\nSUCCESS: The mutant version performed better.")
                print(f"To apply the improvement, run: cp {mutant_package_dir}/config.py .")
            else:
                print("\nFAILURE: The mutant version did not improve performance. Discarding mutation.")
        except subprocess.TimeoutExpired:
            print("MUTANT TIMED OUT during benchmark. Discarding.")
        finally:
            if os.path.exists(mutant_package_dir):
                shutil.rmtree(mutant_package_dir)

    def _package_mutant(self, target_file, mutant_code):
        """Creates a runnable package for the mutant."""
        package_dir = "dgm_mutant_package"
        if os.path.exists(package_dir): shutil.rmtree(package_dir)
        os.makedirs(package_dir)

        for f in self.source_files:
            shutil.copy(f, package_dir)
        
        with open(os.path.join(package_dir, os.path.basename(target_file)), "w") as f:
            f.write(mutant_code)
        
        shutil.copy("benchmark_suite.json", package_dir)
        # We also need the knowledge base for the mutant to run its baseline
        shutil.copytree(config.KNOWLEDGE_BASE_DIR, os.path.join(package_dir, config.KNOWLEDGE_BASE_DIR))
        return package_dir

def run_benchmark_for_mutant(benchmark_file):
    """Called when a mutant script is executed to test itself."""
    print("--- Mutant Benchmark Initialized ---")
    source_files = ["config.py", "dgm_tools.py", "dgm_core.py", "run_dgm.py"]
    # Re-initialize the machine with its own (mutated) source files
    dgm = DarwinGodelMachine(source_files)
    with open(benchmark_file, 'r') as f:
        benchmark_suite = json.load(f)
    total_generations = sum(dgm.evolve(task['task_description'], task['test_code'], max_generations=8) for task in benchmark_suite)
    benchmark_score = total_generations / len(benchmark_suite)
    print(f"MUTANT BENCHMARK: Average of {benchmark_score:.2f} generations per task.")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'run_benchmark':
        run_benchmark_for_mutant('benchmark_suite.json')
    else:
        source_files = ["config.py", "dgm_tools.py", "dgm_core.py", "run_dgm.py"]
        dgm = DarwinGodelMachine(source_files)
        dgm.evolve_self('benchmark_suite.json')
