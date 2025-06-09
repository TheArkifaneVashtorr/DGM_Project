# evolution.py (Simplified for Planner-Coder Architecture)
import random
import copy
import config

def initialize_population() -> list[dict]:
    """Initializes population without the prompt_template gene."""
    population = []
    for _ in range(config.POPULATION_SIZE):
        genome = {
            "embedding_model": random.choice(config.AVAILABLE_EMBEDDING_MODELS),
            "generator_model": random.choice(config.AVAILABLE_GENERATOR_MODELS),
            "chunk_size": random.choice(config.CHUNK_SIZES),
            "top_k": random.choice(config.TOP_K_VALUES),
            "temperature": random.choice(config.TEMPERATURE_VALUES),
            "fitness": 0.0
        }
        population.append(genome)
    return population

def selection(population: list[dict]) -> list[dict]:
    selected = []
    for _ in range(len(population)):
        tournament = random.sample(population, config.TOURNAMENT_SIZE)
        winner = max(tournament, key=lambda x: x["fitness"])
        selected.append(copy.deepcopy(winner))
    return selected

def crossover(parent1: dict, parent2: dict) -> tuple[dict, dict]:
    child1, child2 = copy.deepcopy(parent1), copy.deepcopy(parent2)
    keys_to_evolve = [k for k in parent1.keys() if k != 'fitness']
    for key in keys_to_evolve:
        if random.random() < 0.5:
            child1[key], child2[key] = child2[key], child1[key]
    return child1, child2

def mutation(individual: dict):
    if random.random() < config.MUTATION_RATE:
        individual["embedding_model"] = random.choice(config.AVAILABLE_EMBEDDING_MODELS)
    if random.random() < config.MUTATION_RATE:
        individual["generator_model"] = random.choice(config.AVAILABLE_GENERATOR_MODELS)
    if random.random() < config.MUTATION_RATE:
        individual["chunk_size"] = random.choice(config.CHUNK_SIZES)
    if random.random() < config.MUTATION_RATE:
        individual["top_k"] = random.choice(config.TOP_K_VALUES)
    if random.random() < config.MUTATION_RATE:
        individual["temperature"] = random.choice(config.TEMPERATURE_VALUES)
    return individual
