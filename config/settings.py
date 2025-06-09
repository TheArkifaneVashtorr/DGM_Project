# config/settings.py
import os

# --- Core DGM Paths ---
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# --- Service Configuration ---
OLLAMA_HOST_URL = os.getenv("DGM_OLLAMA_HOST_URL", "http://ollama:11434")

# --- Mutation Target ---
MUTATION_TARGET_FILE = os.path.join(PROJECT_ROOT, "dgm_core", "evolutionary_solver.py")

# --- Model Configuration ---
# Expanded list of models based on performance and hardware feasibility
AVAILABLE_SOLVER_MODELS = [
    "gemma:2b", 
    "llama3:8b", 
    "mistral:latest",
    "starcoder2:15b",
    "codellama:34b",
    "deepseek-coder:16b"
]
DEFAULT_SOLVER_MODEL = "gemma:2b"
MUTATOR_MODEL = "llama3:8b"

# --- Evolutionary Solver Settings ---
MAX_GENERATIONS = 10
POPULATION_SIZE = 5
ELITISM_COUNT = 1
TOURNAMENT_SIZE = 3
MUTATION_RATE = 0.1

# --- Fitness Evaluation Settings ---
FITNESS_WEIGHTS = {
    "correctness": 0.6,
    "efficiency": 0.1,
    "simplicity": 0.1,
    "verifiability": 0.1,
    "model_cost": 0.1
}

# --- Self-Modification Settings ---
MUTATION_ATTEMPTS = 3
DGM_VERSION_FILE = os.path.join(PROJECT_ROOT, "dgm_version.txt")

# --- Knowledge Base Settings ---
KNOWLEDGE_BASE_DIR = os.path.join(PROJECT_ROOT, "knowledge_base")
CHROMA_DB_PATH = os.path.join(PROJECT_ROOT, "chroma_db")
DOCUMENT_SOURCES = [
    "AlphaCode into Darwin Gödel Machine_.txt",
    "Design, Errors, and Strategy Pattern_.txt",
    "Evolving LLM System Components_.txt",
    "LLM Traits for Code_.txt",
    "Ollama Docker LLM Deployment_.txt",
    "Open-source coding LLM comparison.txt",
    "RAG Systems with Persistent Memory_.txt",
    "Rumsfeld's Logic in Tech Projects_.txt",
    "Strategic Plan_ DGM v9.txt"
]

# --- Orchestrator Settings ---
BENCHMARK_FILE = os.path.join(PROJECT_ROOT, "config", "benchmark_suite.json")
MAX_META_CYCLES = 10
STAGNATION_THRESHOLD = 3

# --- Mutant Execution Settings ---
MUTANT_EXECUTION_TIMEOUT = 600
