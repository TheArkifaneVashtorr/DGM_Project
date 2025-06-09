# dgm_agent.py (Refactored)
# The main agent loop for the Darwin Gödel Machine.

import os
import time
import shutil
import config
from evolution import initialize_population, selection, crossover, mutation
from rag_strategy import ConcreteRAGStrategy
from fitness import evaluate_fitness

def setup_knowledge_base():
    """Copies the DGM's own source code into the knowledge base directory."""
    if os.path.exists(config.KNOWLEDGE_BASE_DIR):
        shutil.rmtree(config.KNOWLEDGE_BASE_DIR)
    os.makedirs(config.KNOWLEDGE_BASE_DIR)
    
    source_files = [f for f in os.listdir('.') if f.endswith('.py')]
    for file_name in source_files:
        shutil.copy(file_name, os.path.join(config.KNOWLEDGE_BASE_DIR, file_name))
    print(f"Knowledge base populated with {len(source_files)} source files.")

def main():
    """Main execution loop for the Darwin Gödel Machine."""
    print("--- Darwin Gödel Machine Initializing ---")
    
    setup_knowledge_base()
    
    # FIX: Remove the logic for clearing a persistent vector store, as it is now in-memory.
    
    population = initialize_population()
    print(f"Initialized population with {len(population)} individuals.")

    for generation in range(config.NUM_GENERATIONS):
        print(f"\n--- Starting Generation {generation + 1}/{config.NUM_GENERATIONS} ---")
        
        for i, individual in enumerate(population):
            print(f"Evaluating individual {i+1}/{len(population)}...")
            
            strategy = ConcreteRAGStrategy(
                embedding_model=individual["embedding_model"],
                generator_model=individual["generator_model"],
                prompt_template=individual["prompt_template"]
            )
            
            query = "Refactor the function 'example_function_to_refactor' in rag_strategy.py to be more Pythonic and efficient."
            
            start_time = time.time()
            result = strategy.execute(query)
            end_time = time.time()
            
            generated_code = result.get("result", "")
            execution_time = end_time - start_time
            
            fitness_score = evaluate_fitness(generated_code, execution_time)
            individual["fitness"] = fitness_score
            
            print(f"Individual {i+1} Fitness: {fitness_score:.4f}")
            # print(f"Generated Code:\n---\n{generated_code}\n---")

        best_of_generation = max(population, key=lambda x: x["fitness"])
        print(f"\nBest Fitness in Generation {generation + 1}: {best_of_generation['fitness']:.4f}")
        print(f"Best Genome: Embed='{best_of_generation['embedding_model']}', Gen='{best_of_generation['generator_model']}'")

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
    print(f"  Embedding Model: {final_best['embedding_model']}")
    print(f"  Generator Model: {final_best['generator_model']}")
    print(f"  Prompt Template:\n{final_best['prompt_template']}")
    # In a true DGM, the final_best genome's generated code would be written back to its own source file.


if __name__ == "__main__":
    main()
