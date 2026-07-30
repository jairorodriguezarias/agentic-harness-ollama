import os
import json
import subprocess
import ollama

# ==========================================
# 1. DEFINICIÓN DE HERRAMIENTAS (SKILLS)
# ==========================================

def read_file(path: str) -> str:
    """Lee el contenido de un archivo local."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error al leer el archivo '{path}': {str(e)}"

def write_file(path: str, content: str) -> str:
    """Escribe o sobreescribe texto en un archivo local."""
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True) if os.path.dirname(path) else None
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Éxito: Archivo '{path}' escrito correctamente."
    except Exception as e:
        return f"Error al escribir el archivo '{path}': {str(e)}"

def run_command(command: str) -> str:
    """Ejecuta un comando en la terminal (modo sandbox básico)."""
    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, timeout=10
        )
        output = result.stdout if result.returncode == 0 else result.stderr
        return output.strip() if output else "Comando ejecutado sin salida."
    except Exception as e:
        return f"Error ejecutando comando '{command}': {str(e)}"

TOOL_MAP = {
    "read_file": read_file,
    "write_file": write_file,
    "run_command": run_command
}

# ==========================================
# 2. SCHEMAS EN JSON PARA OLLAMA
# ==========================================

tools_schema = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Lee el contenido de un archivo en el sistema de archivos.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Ruta relativa o absoluta del archivo"}
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Crea o modifica un archivo escribiendo contenido en él.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Ruta del archivo a guardar"},
                    "content": {"type": "string", "description": "Contenido en texto/código a escribir"}
                },
                "required": ["path", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_command",
            "description": "Ejecuta un comando de consola (Bash/Terminal).",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "Comando de consola a ejecutar"}
                },
                "required": ["command"]
            }
        }
    }
]

# ==========================================
# 3. EJECUTOR PRINCIPAL (HARNESS RUNNER)
# ==========================================

def run_agent_task(prompt: str, model_name: str = "gemma4"):
    print(f"🤖 [Prompt]: {prompt}")
    
    response = ollama.chat(
        model=model_name,
        messages=[{"role": "user", "content": prompt}],
        tools=tools_schema
    )

    message = response.get("message", {})
    tool_calls = message.get("tool_calls", [])

    if tool_calls:
        for tool_call in tool_calls:
            func_name = tool_call["function"]["name"]
            func_args = tool_call["function"]["arguments"]
            
            print(f"🛠️ [Tool Invocada]: {func_name} | Argumentos: {func_args}")
            
            if func_name in TOOL_MAP:
                output = TOOL_MAP[func_name](**func_args)
                print(f"⚙️ [Resultado Tool]: {output}")
            else:
                print(f"❌ Función '{func_name}' no disponible en TOOL_MAP.")
    else:
        print("💬 [Respuesta directa del Modelo]:")
        print(message.get("content"))

if __name__ == "__main__":
    MODEL_NAME = "gemma4" 
    test_prompt = "Escribe una función en Python dentro de 'math_utils.py' que calcule el factorial de un número."
    run_agent_task(test_prompt, model_name=MODEL_NAME)
