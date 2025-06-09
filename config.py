# config.py
# Every piece of knowledge must have a single, unambiguous, authoritative representation.
# This file serves as that single source of truth for DGM configuration.

# Ollama and Vector DB Configuration
OLLAMA_BASE_URL = "http://ollama:11434"
KNOWLEDGE_BASE_DIR = "./knowledge_base"
VECTOR_STORE_DIR = "./vector_store" # This is no longer used by the agent but is kept for context.
DOCUMENT_GLOB_PATTERN = "**/*.py"

# --- Evolvable Genome Parameters ---
# These lists define the discrete choices for the evolutionary algorithm.
# The DGM will evolve to select the optimal combination of these components.
AVAILABLE_EMBEDDING_MODELS = [
    "gemma:7b",
    "mistral:latest",
]

AVAILABLE_GENERATOR_MODELS = [
    "llama3:8b",
    "mistral:latest",
    "gemma:7b",
    "codellama:latest",
]

# Initial prompt templates. The EA will mutate and evolve these strings.
INITIAL_PROMPT_TEMPLATES = [
    """
    You are an AI programming assistant. Your task is to analyze the provided code context and resolve the user's query.
    Based on the following code context, provide a refactored and improved version of the specified function.
    Only output the complete, valid Python code for the function. Do not include explanations or prose.

    Code Context:
    {context}

    User Query:
    {query}
    """,
    """
    As a master software architect, your goal is to enhance the provided code.
    Review the code context below and address the user's request by generating superior code.
    The output must be only the raw Python code block for the requested function.

    Context from Knowledge Base:
    {context}

    Request:
    {query}
    """
]

# --- Evolutionary Algorithm Parameters ---
POPULATION_SIZE = 10
NUM_GENERATIONS = 25
MUTATION_RATE = 0.1
TOURNAMENT_SIZE = 3

# --- Fitness Evaluation Parameters ---
# The DGM's objective is to generate code that is correct and efficient.
# We will use weights to create a multi-objective fitness function.
FITNESS_WEIGHTS = {
    "correctness": 1.0,  # Did the code execute without errors?
    "efficiency": 0.2    # Penalize high resource usage (CPU/memory)
}
