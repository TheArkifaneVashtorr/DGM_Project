# utils/tools.py
# This module provides stateless utility functions for fitness evaluation and monitoring.

import subprocess
import time
import ast
import psutil
from radon.complexity import cc_visit
from dgm_core.verifier import Verifier

def get_system_usage() -> dict:
    # ... [The get_system_usage function remains the same, code omitted for brevity]
    usage = { "cpu_percent": psutil.cpu_percent(interval=1), "ram_percent": psutil.virtual_memory().percent, "gpu_utilization_percent": "N/A", "vram_used_mb": "N/A", "vram_total_mb": "N/A" }
    try:
        result = subprocess.run(['nvidia-smi', '--query-gpu=utilization.gpu,memory.used,memory.total', '--format=csv,noheader,nounits'], capture_output=True, text=True, check=True)
        gpu_util, vram_used, vram_total = result.stdout.strip().split(', ')
        usage.update({"gpu_utilization_percent": float(gpu_util), "vram_used_mb": int(vram_used), "vram_total_mb": int(vram_total)})
    except Exception:
        pass
    return usage


def get_behavioral_signature(solution_code: str, test_code: str) -> str:
    # ... [The get_behavioral_signature function remains the same, code omitted for brevity]
    try:
        tree = ast.parse(test_code); func_name = None
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and hasattr(node.func, 'id'):
                func_name = node.func.id; break
        if not func_name: return "signature_error:could_not_find_func_name"
        inputs = [-1, 0, 1, 10, "test", [1,2,3]]; outputs = []
        for i in inputs:
            input_val = f"'{i}'" if isinstance(i, str) else str(i)
            exec_script = f"import sys\n{solution_code}\ntry:\n    result = {func_name}({input_val})\n    print(str(result)[:50])\nexcept Exception as e:\n    print(f\"error:{{type(e).__name__}}\")"
            process = subprocess.run(['python3', '-c', exec_script], capture_output=True, text=True, timeout=2.0)
            outputs.append(process.stdout.strip() or process.stderr.strip())
        return "|".join(outputs)
    except Exception:
        return "signature_generation_error"


def evaluate_fitness(solution_code: str, test_code: str) -> tuple[float, float, float, float]:
    """
    Evaluates fitness based on correctness, efficiency, simplicity, and verifiability.
    """
    verifier = Verifier()
    correctness_score, efficiency_score, simplicity_score = 0.0, 0.0, 0.0
    
    # Run formal verification first
    verifiability_score = verifier.analyze_code(solution_code)

    full_code = f"{solution_code}\n\n{test_code}"
    try:
        start_time = time.monotonic()
        process = subprocess.run(
            ['python3', '-c', full_code],
            capture_output=True, text=True, timeout=5.0
        )
        end_time = time.monotonic()
        execution_time = end_time - start_time

        if process.returncode == 0:
            correctness_score = 1.0
            efficiency_score = max(0.0, 1.0 - (execution_time / 5.0))
            try:
                complexity_blocks = cc_visit(solution_code)
                total_complexity = sum(block.complexity for block in complexity_blocks)
                avg_complexity = (total_complexity / len(complexity_blocks)) if complexity_blocks else 1
                simplicity_score = 1.0 / avg_complexity
            except Exception:
                simplicity_score = 0.5
        # If tests fail, all other scores are zeroed out
        else:
            return (0.0, 0.0, 0.0, verifiability_score)

    except Exception:
        return (0.0, 0.0, 0.0, verifiability_score)

    return (correctness_score, efficiency_score, simplicity_score, verifiability_score)
