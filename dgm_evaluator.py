# dgm_evaluator.py
import json
import logging
import sys
import argparse
from typing import Dict, Optional, Tuple

from dgm_core.dgm_config import DGMConfig
from dgm_core.dgm_genome import DGMGenome
from dgm_core.evolutionary_solver import EvolutionarySolver, Solution
from config import settings

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

class DGMEvaluator:
    """
    Encapsulates the logic for running the benchmark suite on a DGM instance.
    Accepts command-line arguments to specify the configuration to evaluate.
    """
    def __init__(self, solver_model: str = None):
        try:
            self.config = DGMConfig()
            self.genome = DGMGenome(self.config, solver_model_override=solver_model)
            self.solver = EvolutionarySolver(self.genome)
        except Exception as e:
            logger.error(f"Failed to initialize DGM components: {e}")
            sys.exit(1)

    def run_benchmark_suite(self) -> float:
        """
        Runs the full benchmark suite and returns the average generations per task.
        """
        try:
            with open(settings.BENCHMARK_FILE, 'r') as f:
                benchmarks = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            logger.error(f"Benchmark suite file not found or is invalid: {settings.BENCHMARK_FILE}")
            return float('inf')

        total_generations = 0
        successful_tasks = 0
        for task in benchmarks:
            logger.info(f">>> Evaluating Task: {task['description'][:70]}...")
            best_solution, generations = self.solver.solve(task)
            if best_solution:
                total_generations += generations
                successful_tasks += 1
            else:
                logger.warning(f"  Failed to solve task: {task['name']}\n")
                return float('inf')

        if successful_tasks == 0:
            return float('inf')
        
        return total_generations / successful_tasks

def main():
    """
    Main entry point for the evaluator script.
    Parses command-line arguments and runs the evaluation.
    """
    parser = argparse.ArgumentParser(description="DGM Evaluation Script.")
    parser.add_argument('--solver-model', type=str, help='The solver model to use for this evaluation run.')
    args = parser.parse_args()

    logger.info("--- DGM Evaluator Initialized ---")
    evaluator = DGMEvaluator(solver_model=args.solver_model)
    result = evaluator.run_benchmark_suite()
    
    if result == float('inf'):
        print(f"BENCHMARK_RESULT:{result}")
        sys.exit(1)
    else:
        print(f"BENCHMARK_RESULT:{result}")
        sys.exit(0)

if __name__ == "__main__":
    main()
