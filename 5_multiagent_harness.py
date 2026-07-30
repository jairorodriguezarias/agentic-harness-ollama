import os
import shutil
import tempfile
import subprocess
import ollama

MODEL_NAME = "gemma4"
SANDBOX_DIR = os.path.join(tempfile.gettempdir(), "harness_multiagent_sandbox")

def init_sandbox():
    if os.path.exists(SANDBOX_DIR):
        shutil.rmtree(SANDBOX_DIR)
    os.makedirs(SANDBOX_DIR, exist_ok=True)
    print(f"🔒 [SANDBOX] Espacio efímero activo: {SANDBOX_DIR}")

def clean_sandbox():
    if os.path.exists(SANDBOX_DIR):
        shutil.rmtree(SANDBOX_DIR)
        print("🧹 [SANDBOX] Entorno destruido. Recursos liberados.")

def safe_write_file(filename: str, content: str) -> str:
    path = os.path.abspath(os.path.join(SANDBOX_DIR, os.path.basename(filename)))
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return f"Éxito: Archivo '{os.path.basename(path)}' guardado."

def safe_run_command(command: str) -> str:
    try:
        res = subprocess.run(command, shell=True, cwd=SANDBOX_DIR, capture_output=True, text=True, timeout=10)
        return res.stdout.strip() if res.returncode == 0 else f"ERROR:\n{res.stderr.strip()}"
    except Exception as e:
        return f"Error ejecutando: {str(e)}"

def agent_coder(user_prompt: str) -> str:
    print("\n👨‍💻 [AGENTE 1: CODER] Diseñando e implementando la solución...")
    system_prompt = (
        "Eres un Desarrollador Senior de Python. Responde ÚNICAMENTE con código Python válido "
        "para la tarea solicitada, sin explicaciones ni bloques de texto adicionales."
    )
    res = ollama.chat(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )
    code = res["message"]["content"].replace("```python", "").replace("```", "").strip()
    safe_write_file("solution.py", code)
    print("   └─ Archivo 'solution.py' creado por el Agente Coder.")
    return code

def agent_tester(code_context: str) -> str:
    print("\n🧪 [AGENTE 2: TESTER] Diseñando suite de pruebas unitarias...")
    system_prompt = (
        "Eres un Ingeniero de QA. Escribe un script de prueba con 'unittest' o 'assert' para validar "
        "la lógica del archivo 'solution.py'. Importa 'solution' y prueba los casos borde. "
        "Responde ÚNICAMENTE con código Python válido."
    )
    res = ollama.chat(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Código a probar:\n{code_context}"}
        ]
    )
    test_code = res["message"]["content"].replace("```python", "").replace("```", "").strip()
    safe_write_file("test_solution.py", test_code)
    print("   └─ Archivo 'test_solution.py' creado por el Agente Tester.")
    return test_code

def agent_reviewer() -> bool:
    print("\n🔍 [AGENTE 3: REVIEWER] Realizando análisis estático de seguridad y estilo...")
    
    code_path = os.path.join(SANDBOX_DIR, "solution.py")
    with open(code_path, "r") as f:
        code_content = f.read()

    system_prompt = (
        "Eres un Auditor de Seguridad de Software (SAST). Revisa el siguiente código Python. "
        "Si identificas llamadas peligrosas (eval, exec, comandos os desprotegidos), responde 'REJECT'. "
        "Si el código es seguro y limpio, responde 'APPROVE'."
    )
    res = ollama.chat(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": code_content}
        ]
    )
    decision = res["message"]["content"].strip()
    
    if "APPROVE" in decision:
        print("   └─ ✅ [REVIEWER]: Código APROBADO sin vulnerabilidades de seguridad.")
        return True
    else:
        print("   └─ ❌ [REVIEWER]: Código RECHAZADO por políticas de seguridad.")
        return False

MAX_RETRIES = 3

def run_multiagent_pipeline(tarea: str):
    print("🚀 === INICIANDO MULTI-AGENT HARNESS PIPELINE ===")
    print(f"Objetivo: {tarea}")
    
    try:
        init_sandbox()
        
        code = agent_coder(tarea)
        
        if not agent_reviewer():
            print("🛑 Pipeline abortado por fallos de seguridad.")
            return

        agent_tester(code)
        
        for intento in range(1, MAX_RETRIES + 1):
            print(f"\n⚙️ [Intento {intento}/{MAX_RETRIES}] Ejecutando suite de pruebas en Sandbox...")
            test_output = safe_run_command("python3 test_solution.py")
            
            if "FAILED" not in test_output and "ERROR" not in test_output:
                print(f"\n🎉 ¡ÉXITO TOTAL EN EL INTENTO {intento}! Todos los tests pasaron en verde.")
                break
            else:
                print(f"⚠️ [Intento {intento}] Fallaron los tests. Solicitando corrección al Coder...")
                
                feedback_prompt = (
                    f"Tu código previo en 'solution.py' no pasó las pruebas creadas por el Tester.\n"
                    f"Detalle del fallo del test:\n{test_output}\n\n"
                    f"Ajusta el código para que pase exactamente todas las validaciones."
                )
                code = agent_coder(feedback_prompt)

    finally:
        clean_sandbox()

if __name__ == "__main__":
    prompt_usuario = "Crea una función 'invertir_cadena(texto)' que retorne el texto al revés."
    run_multiagent_pipeline(prompt_usuario)
