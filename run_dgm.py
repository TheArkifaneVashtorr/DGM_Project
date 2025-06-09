# run_dgm.py
# Main entry point and orchestrator for the Darwin Gödel Machine.

import sys
import json
import subprocess
import os
import re
import shutil

from dgm_core.knowledge_manager import KnowledgeManager
from dgm_core.llm_interface import LLMInterface
from dgm_core.solver import EvolutionarySolver
from dgm_core.mutator import SelfMutator
import config.settings as settings

def build_ollama_models():
    """Builds custom models from Modelfiles if they don't exist."""
    print("--- Verifying and building Ollama models ---")
    models_to_build = {
        settings.SOLVER_MODEL_NAME: "models/solver_model.modelfile",
        settings.MUTATOR_MODEL_NAME: "models/mutator_model.modelfile"
    }
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, check=True)
        existing_models = result.stdout
        for model_name, modelfile_path in models_to_build.items():
            if model_name in existing_models:
                print(f"Model '{model_name}' already exists. Skipping build.")
            else:
                print(f"Model '{model_name}' not found. Building from '{modelfile_path}'...")
                if not os.path.exists(modelfile_path):
                    print(f"Error: Modelfile not found at '{modelfile_path}'. Halting.")
                    sys.exit(1)
                build_result = subprocess.run(
                    ['ollama', 'create', model_name, '-f', modelfile_path],
                    capture_output=True, text=True
                )
                if build_result.returncode != 0:
                    print(f"Error building model '{model_name}': {build_result.stderr}")
                    sys.exit(1)
                print(f"Successfully built model '{model_name}'.")
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"Error interacting with Ollama CLI: {e}")
        print("Please ensure Ollama is installed and running.")
        sys.exit(1)

def run_meta_evolution():
    """The main meta-evolution loop."""
    print("Initializing Darwin Gödel Machine v7.0 (Self-Modifying)...")
    build_ollama_models()
    source_files = ["config/settings.py", "utils/tools.py", "dgm_core/knowledge_manager.py", "dgm_core/llm_interface.py", "dgm_core/solver.py", "dgm_core/mutator.py", "dgm_core/verifier.py", "run_dgm.py"]

    mutator_llm = LLMInterface(model_name=settings.MUTATOR_MODEL_NAME)
    solver_llm = LLMInterface(model_name=settings.SOLVER_MODEL_NAME)
    km = KnowledgeManager(source_files)
    solver = EvolutionarySolver(solver_llm, km)
    mutator = SelfMutator(mutator_llm, source_files)

    # 1. ESTABLISH PARENT BASELINE
    print("\n\n=== [PHASE 1] Establishing Baseline Performance of Parent ===")
    with open('benchmarks/benchmark_suite.json', 'r') as f:
        benchmark_suite = json.load(f)

    total_gens = sum(solver.evolve(task['task_description'], task['test_code']) for task in benchmark_suite)
    baseline_score = total_gens / len(benchmark_suite)
    print(f"\nPARENT BASELINE PERFORMANCE: Average of {baseline_score:.2f} generations per task.")

    # 2. PROPOSE AND PACKAGE MUTATION
    print("\n\n=== [PHASE 2] Proposing and Packaging Self-Modification ===")
    target_file = 'config/settings.py' # For demonstration, we target a simple file
    mutant_code = mutator.propose_modification(target_file)
    if not mutant_code:
        print("Halting: Mutator failed to generate a valid modification.")
        return
    mutant_package_dir = mutator.package_mutant(target_file, mutant_code)

    # 3. EXECUTE AND EVALUATE MUTANT
    print("\n\n=== [PHASE 3] Executing and Evaluating Mutant ===")
    mutant_score = float('inf') # Higher is worse
    try:
        # The mutant runs its own benchmark test
        mutant_run_command = ['python3', 'run_dgm.py', 'run_benchmark']
        result = subprocess.run(mutant_run_command, cwd=mutant_package_dir, capture_output=True, text=True, timeout=300.0)
        
        if result.returncode != 0:
            print(f"Mutant execution failed. Error:\n{result.stderr}")
        else:
            print("--- Mutant Output ---")
            print(result.stdout)
            print("---------------------")
            # Parse the mutant's performance score from its output
            match = re.search(r"MUTANT BENCHMARK: Average of (\d+\.\d+) generations per task.", result.stdout)
            if match:
                mutant_score = float(match.group(1))
                print(f"Successfully parsed mutant performance score: {mutant_score:.2f}")
            else:
                print("Could not parse mutant performance score from output.")

    except subprocess.TimeoutExpired:
        print("Mutant execution timed out.")
    except Exception as e:
        print(f"An unexpected error occurred during mutant execution: {e}")

    # 4. COMPARE AND SELF-MODIFY (THE GÖDELIAN CHOICE)
    print("\n\n=== [PHASE 4] Comparing and Selecting for Self-Modification ===")
    print(f"Parent Score: {baseline_score:.2f}")
    print(f"Mutant Score: {mutant_score:.2f}")

    if mutant_score < baseline_score:
        print("\n\n>>> MUTATION IS SUPERIOR. INTEGRATING CHANGES. <<<")
        try:
            # Copy the improved file(s) from the mutant package to the parent directory
            source_path = os.path.join(mutant_package_dir, target_file)
            dest_path = target_file
            shutil.copy(source_path, dest_path)
            print(f"Successfully overwrote '{dest_path}' with improved mutant version.")
            print("SELF-MODIFICATION COMPLETE.")
        except Exception as e:
            print(f"CRITICAL ERROR during self-modification file copy: {e}")
    else:
        print("\n\n>>> MUTATION IS NOT SUPERIOR. DISCARDING CHANGES. <<<")
        print("No self-modification occurred.")
    
    # 5. CLEANUP
    print("\n--- Cleaning up mutant package ---")
    if os.path.exists(mutant_package_dir):
        shutil.rmtree(mutant_package_dir)
    print("Cleanup complete.")
    print("\nEND OF META-EVOLUTIONARY CYCLE.")


def run_benchmark_for_mutant():
    """The entry point for a mutant package to test itself."""
    print("--- Mutant Benchmark Initialized ---")
    build_ollama_models()
    source_files = ["config/settings.py", "utils/tools.py", "dgm_core/knowledge_manager.py", "dgm_core/llm_interface.py", "dgm_core/solver.py", "dgm_core/verifier.py", "run_dgm.py"]

    solver_llm = LLMInterface(model_name=settings.SOLVER_MODEL_NAME)
    km = KnowledgeManager(source_files)
    solver = EvolutionarySolver(solver_llm, km)

    with open('benchmarks/benchmark_suite.json', 'r') as f:
        benchmark_suite = json.load(f)

    total_generations = sum(solver.evolve(task['task_description'], task['test_code'], max_generations=8) for task in benchmark_suite)
    benchmark_score = total_generations / len(benchmark_suite)
    print(f"\nMUTANT BENCHMARK: Average of {benchmark_score:.2f} generations per task.")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == 'run_benchmark':
        run_benchmark_for_mutant()
    else:
        run_meta_evolution()
