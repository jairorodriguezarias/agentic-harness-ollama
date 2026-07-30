import os
import json
import subprocess
import ollama

MODEL_NAME = "gemma4"
MAX_RETRIES = 3

def write_file(path: str, content: str) -> str:
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True) if os.path.dirname(path) else None
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Éxito: Archivo '{path}' actualizado."
    except Exception as e:
        return f"Error al escribir archivo: {str(e)}"

def run_command(command: str) -> str:
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=15)
        stdout = result.stdout.strip()
        stderr = result.stderr.strip()
        if result.returncode == 0:
            return f"EXITO:\n{stdout}" if stdout else "EXITO (Sin salida)"
        else:
            return f"ERROR (code {result.returncode}):\n{stderr if stderr else stdout}"
    except Exception as e:
        return f"Error ejecutando comando: {str(e)}"

TOOL_MAP = {"write_file": write_file, "run_command": run_command}

TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Crea o modifica un archivo de código.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "content": {"type": "string"}
                },
                "required": ["path", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_command",
            "description": "Ejecuta un comando en la terminal (ej: python3 test.py).",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string"}
                },
                "required": ["command"]
            }
        }
    }
]

def run_self_healing_loop(prompt_tarea: str, script_test_path: str):
    print(f"\n🔄 === INICIANDO BUCLE DE AUTO-CORRECCIÓN ===")
    print(f"Objetivo: {prompt_tarea}\n")
    
    contexto_mensajes = [
        {"role": "system", "content": "Eres un desarrollador experto. Usa las herramientas disponibles para escribir código sintácticamente correcto que pase los tests."},
        {"role": "user", "content": prompt_tarea}
    ]
    
    for intento in range(1, MAX_RETRIES + 1):
        print(f"─── 🔁 Intento {intento}/{MAX_RETRIES} ───")
        
        res = ollama.chat(model=MODEL_NAME, messages=contexto_mensajes, tools=TOOLS_SCHEMA)
        msg = res.get("message", {})
        tool_calls = msg.get("tool_calls", [])
        
        if tool_calls:
            for call in tool_calls:
                func_name = call["function"]["name"]
                func_args = call["function"]["arguments"]
                print(f"🛠️ [Tool Invocada]: {func_name}")
                
                if func_name in TOOL_MAP:
                    out = TOOL_MAP[func_name](**func_args)
                    print(f"   └─ Output: {out[:100]}...")
        
        print("🔍 Ejecutando suite de pruebas de validación...")
        test_res = run_command(f"python3 {script_test_path}")
        
        if test_res.startswith("EXITO"):
            print(f"\n🎉 ¡ÉXITO TOTAL EN EL INTENTO {intento}! El código pasó todas las pruebas deterministas.")
            return True
        else:
            print(f"⚠️ Las pruebas fallaron en el intento {intento}.")
            print(f"   Detalle del error:\n{test_res}")
            
            feedback = (
                f"El código generado anteriormente produjo el siguiente fallo durante las pruebas:\n\n"
                f"{test_res}\n\n"
                f"Por favor analiza el traceback, arregla la implementación y usa 'write_file' para corregir el archivo."
            )
            contexto_mensajes.append({"role": "user", "content": feedback})

    print(f"\n❌ Se alcanzó el límite de reintentos ({MAX_RETRIES}). El pipeline no pudo auto-corregirse.")
    return False

if __name__ == "__main__":
    test_code = """import math_utils

def test_primo():
    assert math_utils.es_primo(7) == True, "7 debe ser primo"
    assert math_utils.es_primo(4) == False, "4 NO debe ser primo"
    print("TODOS LOS TESTS PASARON")

if __name__ == '__main__':
    test_primo()
"""
    write_file("test_runner.py", test_code)
    prompt = "Modifica o crea 'math_utils.py' escribiendo una función 'es_primo(n)' que retorne True si es primo y False si no lo es."
    run_self_healing_loop(prompt, "test_runner.py")
