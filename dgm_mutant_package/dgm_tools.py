# dgm_tools.py
# A toolkit of stateless utility functions for the DGM.

import subprocess
import re

def evaluate_fitness(generated_code, test_code):
    """
    Executes generated code against a test suite to determine fitness.
    Returns 1 for success, 0 for failure.
    """
    if not generated_code: return 0
    full_script = generated_code + "\n\n" + test_code
    try:
        process = subprocess.run(
            ['python3', '-c', full_script], 
            capture_output=True, 
            text=True, 
            timeout=20
        )
        if process.returncode == 0:
            print("[Fitness Eval] All tests passed.")
            return 1
        else:
            print(f"[Fitness Eval] Test execution failed. Error: {process.stderr.strip()}")
            return 0
    except Exception as e:
        print(f"[Fitness Eval] Failed to execute script. Error: {e}")
        return 0

def clean_code(raw_response):
    """Robustly extracts code from markdown blocks."""
    match = re.search(r'```python\n(.*?)\n```', raw_response, re.DOTALL)
    if match:
        return match.group(1).strip()
    
    match = re.search(r'```(.*?)```', raw_response, re.DOTALL)
    if match:
        return match.group(1).strip()
        
    return raw_response.strip().strip('`')
