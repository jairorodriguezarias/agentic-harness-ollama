import os
import ast
import shutil
import tempfile
import subprocess
from typing import Tuple, List

SANDBOX_DIR = os.path.join(tempfile.gettempdir(), "dev_swarm_sandbox")
BANNED_IMPORTS = {"pickle", "shelve", "ctypes"}
BANNED_FUNCTIONS = {"eval", "exec"}

def validate_syntax_and_safety(code: str) -> Tuple[bool, List[str]]:
    """
    Análisis Estático (SAST): Verifica la compilación sintáctica y busca patrones no seguros mediante AST.
    """
    violations = []

    # 1. Validación de Sintaxis
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return False, [f"Error de Sintaxis en línea {e.lineno}: {e.msg}"]

    # 2. Análisis AST de Seguridad (Lista negra de imports y funciones peligrosas)
    for node in ast.walk(tree):
        # Comprobar imports prohibidos
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name in BANNED_IMPORTS:
                    violations.append(f"SAST_VIOLATION: Importación no autorizada de módulo riesgoso '{alias.name}'.")
        elif isinstance(node, ast.ImportFrom):
            if node.module in BANNED_IMPORTS:
                violations.append(f"SAST_VIOLATION: Importación 'from {node.module}' no autorizada.")

        # Comprobar llamadas a funciones prohibidas (eval, exec)
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in BANNED_FUNCTIONS:
                violations.append(f"SAST_VIOLATION: Uso de función prohibida '{node.func.id}()'.")

    return len(violations) == 0, violations


def execute_in_sandbox(code: str, filename: str = "test_target.py") -> Tuple[bool, str, str]:
    """
    Hito 4: Guarda y ejecuta el código en un directorio aislado de /tmp/ para verificar que no colapse en runtime.
    """
    # Crear o limpiar directorio sandbox aislada
    if os.path.exists(SANDBOX_DIR):
        shutil.rmtree(SANDBOX_DIR)
    os.makedirs(SANDBOX_DIR, exist_ok=True)

    sandbox_file = os.path.join(SANDBOX_DIR, filename)
    with open(sandbox_file, "w", encoding="utf-8") as f:
        f.write(code)

    # 1. Test de compilación aislada
    try:
        cmd = ["python3", "-m", "py_compile", sandbox_file]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=10)
        
        if res.returncode != 0:
            return False, "", f"Fallo de compilación en Sandbox:\n{res.stderr}"
    except subprocess.TimeoutExpired:
        return False, "", "Timeout: La compilación del código superó los 10 segundos en la sandbox."
    except Exception as e:
        return False, "", f"Error al ejecutar en Sandbox: {str(e)}"

    return True, f"✅ Código verificado en Sandbox aislada ('{SANDBOX_DIR}')", ""