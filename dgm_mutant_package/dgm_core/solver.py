# dgm_core/solver.py
# This module contains the EvolutionarySolver agent responsible for solving programming tasks.

from collections import defaultdict
import config.settings as settings
from utils.tools import evaluate_fitness, get_behavioral_signature
from dgm_core.llm_interface import LLMInterface
from dgm_core.knowledge_manager import KnowledgeManager

class EvolutionarySolver:
    """
    An agent that uses a population-based evolutionary loop, optimizing for a
    multi-objective fitness function that now includes formal verifiability.
    """
    def __init__(self, llm_interface: LLMInterface, knowledge_manager: KnowledgeManager):
        self.llm = llm_interface
        self.km = knowledge_manager

    def _calculate_composite_fitness(self, scores: tuple[float, float, float, float]) -> float:
        """Calculates a single fitness score from multiple objectives."""
        correctness, efficiency, simplicity, verifiability = scores
        
        # Correctness is the absolute gate.
        if correctness == 0.0:
            return 0.0
            
        # Define weights for each objective. Verifiability is highly prized.
        weight_correctness = 0.5
        weight_verifiability = 0.3
        weight_efficiency = 0.1
        weight_simplicity = 0.1

        composite_score = (correctness * weight_correctness +
                           verifiability * weight_verifiability +
                           efficiency * weight_efficiency +
                           simplicity * weight_simplicity)
                           
        return composite_score

    def evolve(self, task_description: str, test_code: str, max_generations: int = settings.MAX_GENERATIONS) -> int:
        print(f"\n>>> Solving Task: {task_description[:80]}...")
        best_solution_from_last_gen = "No previous solution."

        for gen in range(1, max_generations + 1):
            print(f"  Generation {gen}/{max_generations}")
            population = []
            for i in range(settings.POPULATION_SIZE):
                print(f"    - Generating candidate {i+1}/{settings.POPULATION_SIZE}")
                context = self.km.retrieve_context(f"Task: {task_description}\nHint from previous best attempt:\n{best_solution_from_last_gen}")
                prompt = f"Solve this task: {task_description}\n\nContext:\n{context}\n\nPrevious best solution:\n{best_solution_from_last_gen}\n\nProvide only complete, executable Python code."
                solution_code = self.llm.query(prompt)
                if solution_code:
                    population.append({"code": solution_code, "fitness": -1.0, "scores": (0,0,0,0)})

            if not population:
                print("  LLM failed to generate any candidates. Continuing.")
                continue

            successful_candidates = []
            for candidate in population:
                fitness_scores = evaluate_fitness(candidate["code"], test_code)
                candidate["scores"] = fitness_scores
                
                if fitness_scores[0] == 1.0:
                    print(f"  Task solved successfully in {gen} generation(s).")
                    print(f"    - Final Scores (Correctness, Efficiency, Simplicity, Verifiability): {fitness_scores}")
                    return gen
                
                candidate["fitness"] = self._calculate_composite_fitness(fitness_scores)
                if candidate["fitness"] > 0:
                    successful_candidates.append(candidate)

            if not successful_candidates:
                print("  No candidates passed initial evaluation. Evolving...")
                best_solution_from_last_gen = "No solution was viable."
                continue
            
            clusters = defaultdict(list)
            for candidate in successful_candidates:
                signature = get_behavioral_signature(candidate["code"], test_code)
                clusters[signature].append(candidate)
            
            print(f"  Found {len(clusters)} distinct solution clusters.")
            sorted_clusters = sorted(clusters.values(), key=len, reverse=True)
            
            parents_for_next_gen = [max(cluster, key=lambda x: x["fitness"]) for cluster in sorted_clusters[:settings.DIVERSITY_CLUSTER_COUNT]]
            
            if parents_for_next_gen:
                best_overall_candidate = max(parents_for_next_gen, key=lambda x: x["fitness"])
                best_solution_from_last_gen = best_overall_candidate["code"]
                print(f"  Highest composite fitness this generation: {best_overall_candidate['fitness']:.4f}. Evolving from {len(parents_for_next_gen)} diverse parents.")
            else:
                best_solution_from_last_gen = "No solution was viable."

        print(f"  Failed to solve task within {max_generations} generations.")
        return max_generations
