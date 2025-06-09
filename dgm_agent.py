# dgm_agent.py (Simplified for Planner-Coder Architecture)
import os
import shutil
import json
import config
from evolution import initialize_population, selection, crossover, mutation
from rag_strategy import ConcreteRAGStrategy

def setup_knowledge_base():
    if os.path.exists(config.KNOWLEDGE_BASE_DIR):
        shutil.rmtree(config.KNOWLEDGE_BASE_DIR)
    os.makedirs(config.KNOWLEDGE_BASE_DIR)
    source_files = [f for f in os.listdir('.') if f.endswith('.py')]
    for file_name in source_files:
        shutil.copy(file_name, os.path.join(config.KNOWLEDGE_BASE_DIR, file_name))
    print(f"Knowledge base populated with {len(source_files)} source files.")

def main():
    print("--- Darwin Gödel Machine Initializing with Planner-Coder Architecture ---")
    setup_knowledge_base()
    population = initialize_population()
    print(f"Initialized population with {len(population)} individuals.")

    for generation in range(config.NUM_GENERATIONS):
        print(f"\n--- Starting Generation {generation + 1}/{config.NUM_GENERATIONS} ---")
        
        for i, individual in enumerate(population):
            print(f"--- Evaluating individual {i+1}/{len(population)} ---")
            
            # The strategy now encapsulates all logic, taking only the genome.
            strategy = ConcreteRAGStrategy(**individual)
            query = "Refactor the function 'example_function_to_refactor' in rag_strategy.py to be more Pythonic and efficient, returning a list of even numbers."
            
            results = strategy.execute(query)
            individual["fitness"] = results["final_fitness"]
            print(f"--- Individual {i+1} Final Fitness: {individual['fitness']:.4f} ---")

        best_of_generation = max(population, key=lambda x: x["fitness"])
        print(f"\nBest Fitness in Generation {generation + 1}: {best_of_generation['fitness']:.4f}")
        print(f"Best Genome: { {k:v for k,v in best_of_generation.items() if k != 'fitness'} }")

        mating_pool = selection(population)
        next_generation = []
        for i in range(0, len(mating_pool), 2):
            parent1 = mating_pool[i]
            parent2 = mating_pool[i+1] if (i+1) < len(mating_pool) else mating_pool[0]
            child1, child2 = crossover(parent1, parent2)
            next_generation.append(mutation(child1))
            next_generation.append(mutation(child2))
        population = next_generation[:config.POPULATION_SIZE]

    print("\n--- Evolutionary Process Concluded ---")
    final_best = max(population, key=lambda x: x["fitness"])
    print("Final Best Performing Strategy:")
    print(f"  Fitness: {final_best['fitness']:.4f}")
    print(f"  Genome: {final_best}")

if __name__ == "__main__":
    main()
