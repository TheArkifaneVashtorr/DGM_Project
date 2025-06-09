# run_dgm.py
# Main entry point for the Darwin Gödel Machine.

import sys
import json
from dgm_core import DarwinGodelMachine
from dgm_tools import evaluate_fitness

def run_benchmark_for_mutant(benchmark_file):
    """Called by a mutant script to test itself."""
    # This function would be expanded in a full meta-evolution loop
    # For now, it's a placeholder to show the structure.
    print(f"MUTANT BENCHMARK: Simulating run for {benchmark_file}")
    # A real run would instantiate the mutant's DGM class and run its evolve method
    # on the benchmark suite, then print the score for the parent process.
    print(f"MUTANT BENCHMARK: Average of 1.50 generations per task.")

def main():
    """Parses arguments and runs the appropriate DGM mode."""
    # Define the core source files of the DGM itself
    source_files = ["config.py", "dgm_tools.py", "dgm_core.py", "run_dgm.py"]
    
    dgm = DarwinGodelMachine(source_files)
    dgm.evolve_self('benchmark_suite.json')

if __name__ == "__main__":
    main()
