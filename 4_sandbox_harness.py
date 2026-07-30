import os
import shutil
import tempfile
import subprocess
import ollama

MODEL_NAME = "gemma4"
SANDBOX_DIR = os.path.join(tempfile.gettempdir(), "harness_sandbox")

def init_sandbox():
    if os.path.exists(SANDBOX_DIR):
        shutil.rmtree(SANDBOX_DIR)
    os.makedirs(SANDBOX_DIR, exist_ok=True)
    print(f"🔒 [SANDBOX] Aislamiento activado en directorio efímero: {SANDBOX_DIR}")

def clean_sandbox():
    if os.path.exists(SANDBOX_DIR):
        shutil.rmtree(SANDBOX_DIR)
        print("🧹 [SANDBOX] Entorno efímero destruido.")

def safe_write_file(path: str, content: str) -> str:
    safe_path = os.path.abspath(os.path.join(SANDBOX_DIR, os.path.basename(path)))
    try:
        with open(safe_path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Éxito [Sandbox]: Archivo '{os.path.basename(safe_path)}' guardado aisladamente."
    except Exception as e:
        return f"Error de Seguridad/Fichero: {str(e)}"

def safe_run_command(command: str) -> str:
    FORBIDDEN = ["rm -rf /", "sudo", "shutdown", "curl", "wget"]
    for word in FORBIDDEN:
        if word in command:
            return f"❌ ALERTA DE SEGURIDAD: Comando prohibido detectado ('{word}')."
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=SANDBOX_DIR,
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return f"EXITO:\n{result.stdout.strip()}"
        else:
            return f"ERROR (code {result.returncode}):\n{result.stderr.strip()}"
    except subprocess.TimeoutExpired:
        return "❌ ERROR: Tiempo de ejecución excedido (Timeout 5s)."
    except Exception as e:
        return f"Error en ejecutor sandbox: {str(e)}"

if __name__ == "__main__":
    try:
        init_sandbox()
        
        test_script = """import app

def test_resta():
    assert app.restar(10, 4) == 6, "10 - 4 debe ser 6"
    print("TEST PASADO")

if __name__ == '__main__':
    test_resta()
"""
        safe_write_file("test_app.py", test_script)
        
        prompt = "Crea un archivo 'app.py' con una función 'restar(a, b)' que devuelva la resta."
        print(f"🤖 [Agent Task]: {prompt}")
        
        codigo_generado = "def restar(a, b):\n    return a - b\n"
        print(safe_write_file("app.py", codigo_generado))
        
        res = safe_run_command("python3 test_app.py")
        print(f"🔍 Resultado en Sandbox:\n{res}")

    finally:
        clean_sandbox()
