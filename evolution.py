# evolution.py
# Implements the core Darwinian operators: variation and selection. 

import random
import copy
import config

def initialize_population() -> list[dict]:
    """
    Creates the initial population of RAG strategies (genomes).
    Each individual is a dictionary representing a unique configuration.
    """
    population = []
    for _ in range(config.POPULATION_SIZE):
        genome = {
            "embedding_model": random.choice(config.AVAILABLE_EMBEDDING_MODELS),
            "generator_model": random.choice(config.AVAILABLE_GENERATOR_MODELS),
            "prompt_template": random.choice(config.INITIAL_PROMPT_TEMPLATES),
            "fitness": 0.0 # Initialize fitness to 0
        }
        population.append(genome)
    return population

def selection(population: list[dict]) -> list[dict]:
    """
    Selects the fittest individuals for reproduction using tournament selection. 
    """
    selected = []
    for _ in range(len(population)):
        tournament = random.sample(population, config.TOURNAMENT_SIZE)
        winner = max(tournament, key=lambda x: x["fitness"])
        selected.append(copy.deepcopy(winner))
    return selected

def crossover(parent1: dict, parent2: dict) -> tuple[dict, dict]:
    """
    Performs one-point crossover on the parents' genomes.
    We treat the discrete choices as single points for swapping.
    """
    child1, child2 = copy.deepcopy(parent1), copy.deepcopy(parent2)
    
    # Crossover embedding model
    if random.random() < 0.5:
        child1["embedding_model"], child2["embedding_model"] = child2["embedding_model"], child1["embedding_model"]
        
    # Crossover generator model
    if random.random() < 0.5:
        child1["generator_model"], child2["generator_model"] = child2["generator_model"], child1["generator_model"]
        
    # Crossover prompt template
    if random.random() < 0.5:
        child1["prompt_template"], child2["prompt_template"] = child2["prompt_template"], child1["prompt_template"]
        
    return child1, child2

def mutation(individual: dict):
    """
    Applies random mutations to an individual's genome. 
    """
    if random.random() < config.MUTATION_RATE:
        individual["embedding_model"] = random.choice(config.AVAILABLE_EMBEDDING_MODELS)
        
    if random.random() < config.MUTATION_RATE:
        individual["generator_model"] = random.choice(config.AVAILABLE_GENERATOR_MODELS)
        
    if random.random() < config.MUTATION_RATE:
        # Simple mutation: swap for another template. More advanced would be LLM-based mutation. 
        individual["prompt_template"] = random.choice(config.INITIAL_PROMPT_TEMPLATES)
        
    return individual
