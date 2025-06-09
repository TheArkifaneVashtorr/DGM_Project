# run_dgm.py
# Main entry point and orchestrator for the Darwin Gödel Machine.

import sys
import json
import subprocess
import re

# Import the new, specialized modules
from knowledge_manager import KnowledgeManager
from llm_interface import LLMInterface
from solver import EvolutionarySolver
from mutator import SelfMutator

def run_meta_evolution():
    """The main meta-evolution loop."""
    print("Initializing Darwin Gödel Machine v5.0 (Networked)...")
    source_files = ["config.py", "dgm_tools.py", "knowledge_manager.py", "llm_interface.py", "solver.py", "mutator.py", "run_dgm.py"]
    
    # 1. Initialize all components of the network
    km = KnowledgeManager(source_files)
    llm = LLMInterface()
    solver = EvolutionarySolver(llm, km)
    mutator = SelfMutator(llm, source_files)

    # 2. Establish Baseline Performance
    print("\n\n=== META-EVOLUTION: Establishing Baseline Performance ===")
    with open('benchmark_suite.json', 'r') as f:
        benchmark_suite = json.load(f)
    
    total_gens = sum(solver.evolve(task['task_description'], task['test_code']) for task in benchmark_suite)
    baseline_score = total_gens / len(benchmark_suite)
    print(f"\nBASELINE PERFORMANCE: Average of {baseline_score:.2f} generations per task.")

    # 3. Propose and Package a Self-Modification
    print("\n\n=== META-EVOLUTION: Proposing Self-Modification ===")
    target_file = 'config.py'
    mutant_code = mutator.propose_modification(target_file)
    
    if not mutant_code:
        print("Halting: Failed to generate a valid mutant.")
        return

    mutant_package_dir = mutator.package_mutant(target_file, mutant_code)

    # 4. Test the Mutant (Simulation for this prototype)
    print("\n\n=== META-EVOLUTION: Testing Mutant Performance (Simulation) ===")
    print(f"A new version of the system has been packaged in '{mutant_package_dir}'.")
    print("A full production run would now execute this package against the benchmark suite.")
    print("If the mutant's performance were better, it would become the new baseline.")
    print("This completes the full, refactored meta-evolutionary loop.")


def run_benchmark_for_mutant():
    """The entry point for a mutant package to test itself."""
    print("--- Mutant Benchmark Initialized ---")
    source_files = ["config.py", "dgm_tools.py", "knowledge_manager.py", "llm_interface.py", "solver.py", "mutator.py", "run_dgm.py"]

    # Initialize components from within the mutant's own package
    km = KnowledgeManager(source_files)
    llm = LLMInterface()
    solver = EvolutionarySolver(llm, km)
    
    with open('benchmark_suite.json', 'r') as f:
        benchmark_suite = json.load(f)
    
    total_generations = sum(solver.evolve(task['task_description'], task['test_code'], max_generations=8) for task in benchmark_suite)
    benchmark_score = total_generations / len(benchmark_suite)
    
    # This specific print format is what a parent process would look for
    print(f"MUTANT BENCHMARK: Average of {benchmark_score:.2f} generations per task.")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == 'run_benchmark':
        run_benchmark_for_mutant()
    else:
        run_meta_evolution()
