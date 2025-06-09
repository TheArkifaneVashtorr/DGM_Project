# config.py (Refactored for Planner-Coder Architecture)

# Ollama and Vector DB Configuration
OLLAMA_BASE_URL = "http://ollama:11434"
KNOWLEDGE_BASE_DIR = "./knowledge_base"
DOCUMENT_GLOB_PATTERN = "**/*.py"

# --- Evolvable Genome Parameters ---
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

# NEW: Prompts for the Planner-Coder workflow
PLANNER_PROMPT_TEMPLATE = (
    "You are a senior software architect. Your task is to create a clear, step-by-step, language-agnostic plan to solve the following user query based on the provided code context.\n"
    "Do not write any code. Your output must be only the numbered steps of the plan.\n\n"
    "--- CONTEXT ---\n{context}\n\n"
    "--- USER QUERY ---\n{query}\n\n"
    "--- PLAN ---\n"
)

CODER_PROMPT_TEMPLATE = (
    "You are a senior software developer. Your task is to write the Python code that precisely implements the following step-by-step plan.\n"
    "Only output the raw Python code for the function. Do not include explanations or prose.\n\n"
    "--- CONTEXT ---\n{context}\n\n"
    "--- PLAN ---\n{plan}\n\n"
    "--- PYTHON CODE ---\n"
)

# The debugging prompt is now simpler, as the primary logic is in the main loop.
DEBUGGING_PROMPT_TEMPLATE = (
    "Your previous code attempt failed. Analyze the plan, your faulty code, and the error. Provide a corrected Python function.\n"
    "Only output the raw Python code.\n\n"
    "--- PLAN ---\n{plan}\n\n"
    "--- FAULTY CODE ---\n```python\n{faulty_code}\n```\n\n"
    "--- ERROR ---\n{error_message}\n\n"
    "--- CORRECTED PYTHON CODE ---\n"
)

# Evolvable hyperparameters
CHUNK_SIZES = [500, 1000, 2000]
TOP_K_VALUES = [2, 3, 5]
TEMPERATURE_VALUES = [0.2, 0.7, 1.2]


# --- Evolutionary Algorithm Parameters ---
POPULATION_SIZE = 10
NUM_GENERATIONS = 25
MUTATION_RATE = 0.15
TOURNAMENT_SIZE = 3

# --- Fitness Evaluation Parameters ---
FITNESS_WEIGHTS = {
    "correctness": 1.0,
    "efficiency": 0.2
}
