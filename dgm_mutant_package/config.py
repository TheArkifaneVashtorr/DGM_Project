RAG_PROMPT_TEMPLATE = """
Based on the following CONTEXT, write a Python function that correctly implements the TASK. Your response must contain ONLY the raw code for the function.

CONTEXT:
---
{context}
---

TASK:
---
{task_description}
---
"""