# run_dgm.py
# Main entry point and orchestrator for the Darwin Gödel Machine.

import sys
import json
import subprocess
import os

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
                    print(f"Error building model '{model_name}':")
                    print(build_result.stderr)
                    sys.exit(1)
                print(f"Successfully built model '{model_name}'.")
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"Error interacting with Ollama CLI: {e}")
        print("Please ensure Ollama is installed and running.")
        sys.exit(1)

def run_meta_evolution():
    """The main meta-evolution loop."""
    print("Initializing Darwin Gödel Machine v6.1 (Diversity Engine)...")
    build_ollama_models()
    source_files = ["config/settings.py", "utils/tools.py", "dgm_core/knowledge_manager.py", "dgm_core/llm_interface.py", "dgm_core/solver.py", "dgm_core/mutator.py", "run_dgm.py"]

    mutator_llm = LLMInterface(model_name=settings.MUTATOR_MODEL_NAME)
    solver_llm = LLMInterface(model_name=settings.SOLVER_MODEL_NAME)
    km = KnowledgeManager(source_files)
    solver = EvolutionarySolver(solver_llm, km)
    mutator = SelfMutator(mutator_llm, source_files)

    print("\n\n=== META-EVOLUTION: Establishing Baseline Performance ===")
    
# ... inside run_meta_evolution function ...
    # --- THIS IS THE REVERTED LINE ---
    with open('benchmarks/benchmark_suite.json', 'r') as f:
        benchmark_suite = json.load(f)
# ... rest of the file is the same ...

    total_gens = sum(solver.evolve(task['task_description'], task['test_code']) for task in benchmark_suite)
    baseline_score = total_gens / len(benchmark_suite)
    print(f"\nBASELINE PERFORMANCE: Average of {baseline_score:.2f} generations per task.")

    print("\n\n=== META-EVOLUTION: Proposing Self-Modification ===")
    target_file = 'config/settings.py'
    mutant_code = mutator.propose_modification(target_file)

    if not mutant_code:
        print("Halting: Failed to generate a valid mutant.")
        return

    mutant_package_dir = mutator.package_mutant(target_file, mutant_code)

    print("\n\n=== META-EVOLUTION: Final Phase ===")
    print("The system has successfully proposed and packaged a mutation.")
    print(f"The mutant package is preserved at '{mutant_package_dir}' for inspection.")
    print("This concludes the operational test of the diversity engine architecture.")


def run_benchmark_for_mutant():
    """The entry point for a mutant package to test itself."""
    print("--- Mutant Benchmark Initialized ---")
    build_ollama_models()
    source_files = ["config/settings.py", "utils/tools.py", "dgm_core/knowledge_manager.py", "dgm_core/llm_interface.py", "dgm_core/solver.py", "dgm_core/mutator.py", "run_dgm.py"]

    mutator_llm = LLMInterface(model_name=settings.MUTATOR_MODEL_NAME)
    solver_llm = LLMInterface(model_name=settings.SOLVER_MODEL_NAME)
    km = KnowledgeManager(source_files)
    solver = EvolutionarySolver(solver_llm, km)

    with open('benchmarks/challenge_benchmark.json', 'r') as f:
        benchmark_suite = json.load(f)

    total_generations = sum(solver.evolve(task['task_description'], task['test_code'], max_generations=8) for task in benchmark_suite)
    benchmark_score = total_generations / len(benchmark_suite)
    print(f"MUTANT BENCHMARK: Average of {benchmark_score:.2f} generations per task.")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == 'run_benchmark':
        run_benchmark_for_mutant()
    else:
        run_meta_evolution()
