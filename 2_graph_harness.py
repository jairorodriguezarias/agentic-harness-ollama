import os
import json
import subprocess
import ollama

# ==========================================
# 1. HERRAMIENTAS (SKILLS)
# ==========================================
def write_file(path: str, content: str) -> str:
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True) if os.path.dirname(path) else None
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Éxito: Archivo '{path}' escrito."
    except Exception as e:
        return f"Error: {str(e)}"

def run_command(command: str) -> str:
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=10)
        output = result.stdout if result.returncode == 0 else result.stderr
        return output.strip() if output else "Ejecutado sin salida."
    except Exception as e:
        return f"Error al ejecutar comando: {str(e)}"

TOOL_MAP = {"write_file": write_file, "run_command": run_command}

TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Escribe contenido en un archivo.",
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
            "description": "Ejecuta un comando en terminal.",
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

# ==========================================
# 2. NODOS DEL GRAFO (GRAPH ENGINEERING)
# ==========================================
MODEL_NAME = "gemma4"

def node_planner(user_goal: str) -> list:
    """NODO 1: Planifica la estrategia dividiéndola en micro-tareas."""
    print("\n🧠 [NODO 1: PLANNER] Diseñando plan de ejecución...")
    system_prompt = (
        "Eres un orquestador de software. Divide el objetivo del usuario en 2 pasos secuenciales simples.\n"
        "Responde ÚNICAMENTE en JSON con este formato:\n"
        '{"steps": ["Paso 1: escribir código...", "Paso 2: crear test..."]}'
    )
    
    res = ollama.chat(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_goal}
        ]
    )
    
    try:
        content = res["message"]["content"]
        clean_content = content.replace("```json", "").replace("```", "").strip()
        plan = json.loads(clean_content)
        return plan.get("steps", [])
    except Exception as e:
        print(f"⚠️ Error parseando el plan: {e}. Usando plan por defecto.")
        return [
            f"Escribir el código fuente para: {user_goal}",
            "Crear un test unitario rápido en Python."
        ]

def node_executor(step_description: str):
    """NODO 2: Ejecuta la Skill adecuada para la tarea del plan."""
    print(f"\n⚙️ [NODO 2: EXECUTOR] Ejecutando: '{step_description}'")
    
    response = ollama.chat(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": f"Ejecuta la tool necesaria para esta tarea: {step_description}"}],
        tools=TOOLS_SCHEMA
    )
    
    tool_calls = response.get("message", {}).get("tool_calls", [])
    
    if tool_calls:
        for call in tool_calls:
            func_name = call["function"]["name"]
            func_args = call["function"]["arguments"]
            print(f"   🛠️ Skill seleccionada: {func_name}")
            if func_name in TOOL_MAP:
                result = TOOL_MAP[func_name](**func_args)
                print(f"   --> {result}")
    else:
        print(f"   💬 Salida directa: {response['message']['content']}")

def node_evaluator(target_file: str) -> bool:
    """NODO 3: Verifica determinísticamente si los artefactos existen."""
    print(f"\n🔍 [NODO 3: EVALUATOR] Verificando estado final...")
    exists = os.path.exists(target_file)
    if exists:
        print(f"✅ VERIFICADO: El archivo '{target_file}' fue creado correctamente en el sistema.")
    else:
        print(f"❌ FALLO DE EVALUACIÓN: No se encontró el archivo '{target_file}'.")
    return exists

# ==========================================
# 3. PIPELINE MAIN (GRAPH ORCHESTRATOR)
# ==========================================
def run_graph_pipeline(user_goal: str):
    print(f"🚀 === INICIANDO AGENTIC GRAPH PIPELINE ===")
    print(f"Objetivo global: {user_goal}")
    
    steps = node_planner(user_goal)
    for i, step in enumerate(steps, 1):
        print(f"   {i}. {step}")
    
    for step in steps:
        node_executor(step)
        
    node_evaluator("math_utils.py")

if __name__ == "__main__":
    prompt = "Crea un módulo en Python llamado 'math_utils.py' con una función para verificar si un número es primo."
    run_graph_pipeline(prompt)
