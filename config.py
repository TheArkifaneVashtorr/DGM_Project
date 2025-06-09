# config.py
# Central configuration for the Darwin Gödel Machine

# --- Service Endpoints ---
OLLAMA_API_URL = "http://localhost:11434/api/generate"
CHROMA_HOST = "localhost"
CHROMA_PORT = "8000"

# --- DB and Directory Names ---
KNOWLEDGE_BASE_COLLECTION = "dgm_knowledge_base_v4"
KNOWLEDGE_BASE_DIR = "./knowledge_base"

# --- Evolutionary Parameters ---
AVAILABLE_MODELS = ["codellama:latest", "llama3:latest"]

# --- Prompt Templates ---
RAG_PROMPT_TEMPLATE = """
Based on the following CONTEXT, write a Python function that correctly implements the TASK.
Your response must contain ONLY the raw code for the function.

CONTEXT:
---
{context}
---

TASK:
---
{task_description}
---
"""

# FINAL SELF-MODIFY PROMPT: Radically simplified and focused on one variable.
SELF_MODIFY_PROMPT_TEMPLATE = """
**ROLE:** You are an automated code refactoring system.
**TASK:** Your only task is to rewrite the `RAG_PROMPT_TEMPLATE` variable in the following Python script to make it more effective. The goal is to get a better code solution from the worker LLM.
**CRITICAL OUTPUT FORMATTING RULES:**
- Return the COMPLETE and UNCHANGED source code for the file.
- The ONLY change you are allowed to make is to the string value of the `RAG_PROMPT_TEMPLATE` variable.
- Your entire response must be ONLY raw Python code. Do not add any commentary or markdown.

**FULL SOURCE CODE TO MODIFY:**
---
{source_code}
---
"""
