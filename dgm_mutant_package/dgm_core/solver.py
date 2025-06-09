# dgm_core/solver.py
# This module contains the EvolutionarySolver agent responsible for solving programming tasks.

from collections import defaultdict
import config.settings as settings
from utils.tools import evaluate_fitness, get_behavioral_signature
from dgm_core.llm_interface import LLMInterface
from dgm_core.knowledge_manager import KnowledgeManager

class EvolutionarySolver:
    """
    An agent that uses a population-based evolutionary loop, with diversity
    maintenance, to solve programming tasks.
    """
    def __init__(self, llm_interface: LLMInterface, knowledge_manager: KnowledgeManager):
        self.llm = llm_interface
        self.km = knowledge_manager

    def _calculate_composite_fitness(self, scores: tuple[float, float, float]) -> float:
        """Calculates a single fitness score from multiple objectives using a weighted sum."""
        correctness, efficiency, simplicity = scores
        if correctness == 0.0: return 0.0
        
        return (correctness * 0.7 + efficiency * 0.2 + simplicity * 0.1)

    def evolve(self, task_description: str, test_code: str, max_generations: int = settings.MAX_GENERATIONS) -> int:
        print(f"\n>>> Solving Task: {task_description[:80]}...")
        best_solution_from_last_gen = "No previous solution."

        for gen in range(1, max_generations + 1):
            print(f"  Generation {gen}/{max_generations}")
            
            # --- 1. GENERATION ---
            population = []
            for i in range(settings.POPULATION_SIZE):
                print(f"    - Generating candidate {i+1}/{settings.POPULATION_SIZE}")
                context = self.km.retrieve_context(f"Task: {task_description}\nHint from previous best attempt:\n{best_solution_from_last_gen}")
                prompt = f"Solve this task: {task_description}\n\nContext:\n{context}\n\nPrevious best solution:\n{best_solution_from_last_gen}\n\nProvide only complete, executable Python code."
                
                solution_code = self.llm.query(prompt)
                if solution_code:
                    population.append({"code": solution_code, "fitness": -1.0, "scores": (0,0,0)})

            if not population:
                print("  LLM failed to generate any candidates. Continuing.")
                continue

            # --- 2. EVALUATION ---
            successful_candidates = []
            for candidate in population:
                fitness_scores = evaluate_fitness(candidate["code"], test_code)
                if fitness_scores[0] == 1.0:
                    print(f"  Task solved successfully in {gen} generation(s).")
                    print(f"    - Final Scores (Correctness, Efficiency, Simplicity): {fitness_scores}")
                    return gen
                
                # We still consider candidates that are partially correct or promising
                candidate["scores"] = fitness_scores
                candidate["fitness"] = self._calculate_composite_fitness(fitness_scores)
                if candidate["fitness"] > 0: # Only consider candidates that are not complete failures
                    successful_candidates.append(candidate)

            if not successful_candidates:
                print("  No candidates passed initial evaluation. Evolving...")
                best_solution_from_last_gen = "No solution was viable."
                continue
            
            # --- 3. DIVERSITY-AWARE SELECTION ---
            # Group candidates by their behavioral signature
            clusters = defaultdict(list)
            for candidate in successful_candidates:
                signature = get_behavioral_signature(candidate["code"], test_code)
                clusters[signature].append(candidate)
            
            print(f"  Found {len(clusters)} distinct solution clusters.")

            # Sort clusters by size (number of candidates)
            sorted_clusters = sorted(clusters.values(), key=len, reverse=True)
            
            # Select the fittest candidate from each of the top N clusters
            parents_for_next_gen = []
            for cluster in sorted_clusters[:settings.DIVERSITY_CLUSTER_COUNT]:
                fittest_in_cluster = max(cluster, key=lambda x: x["fitness"])
                parents_for_next_gen.append(fittest_in_cluster)
            
            # The hint for the next generation is the absolute best solution found so far
            if parents_for_next_gen:
                best_overall_candidate = max(parents_for_next_gen, key=lambda x: x["fitness"])
                best_solution_from_last_gen = best_overall_candidate["code"]
                print(f"  Highest composite fitness this generation: {best_overall_candidate['fitness']:.4f}. Evolving from {len(parents_for_next_gen)} diverse parents.")
            else:
                best_solution_from_last_gen = "No solution was viable."

        print(f"  Failed to solve task within {max_generations} generations.")
        return max_generations
