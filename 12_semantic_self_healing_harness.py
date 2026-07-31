import json
import time
import ollama
from typing import Dict, Any, Tuple

MODEL_CODER = "qwen2.5-coder"
MODEL_JUDGE = "gemma4"
MAX_RETRIES = 3

def generate_code(prompt: str, feedback: str = None) -> str:
    """Agente Coder: Genera o refactoriza código según el prompt y objeciones de OPA/Judge."""
    system_prompt = (
        "Eres un Desarrollador Senior de Python. Responde ÚNICAMENTE con código Python válido "
        "sin bloques de texto explicativo adicionales."
    )
    
    user_context = prompt
    if feedback:
        user_context += f"\n\n⚠️ TU CÓDIGO ANTERIOR FUE RECHAZADO POR GOBERNANZA. DEBES CORREGIR LO SIGUIENTE:\n{feedback}"
    
    response = ollama.chat(
        model=MODEL_CODER,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_context}
        ]
    )
    
    code = response.get("message", {}).get("content", "").replace("```python", "").replace("```", "").strip()
    return code

def judge_and_opa_gate(prompt: str, code: str) -> Tuple[bool, int, list, str]:
    """Nodo Evaluador + OPA Policy Engine simulado en memoria."""
    judge_system_prompt = (
        "Eres un Auditor Senior de Código y Motor OPA. Evalúa el código según correctitud, "
        "manejo de excepciones, type checking y seguridad.\n"
        "Responde ÚNICAMENTE en JSON sintácticamente válido:\n"
        '{\n'
        '  "score": <int_0_100>,\n'
        '  "approved": <bool>,\n'
        '  "summary": "<resumen_breve>",\n'
        '  "objections": ["<objecion_1>", "<objecion_2>"]\n'
        '}'
    )
    
    user_context = f"TAREA: {prompt}\n\nCÓDIGO GENERADO:\n{code}"
    
    response = ollama.chat(
        model=MODEL_JUDGE,
        messages=[
            {"role": "system", "content": judge_system_prompt},
            {"role": "user", "content": user_context}
        ]
    )
    
    raw_content = response.get("message", {}).get("content", "").replace("```json", "").replace("```", "").strip()
    
    try:
        eval_data = json.loads(raw_content)
        score = eval_data.get("score", 0)
        approved = eval_data.get("approved", False)
        objections = eval_data.get("objections", [])
        summary = eval_data.get("summary", "")
        
        # Criterio OPA: score >= 80 y approved == True
        allow = approved and score >= 80
        return allow, score, objections, summary
    except Exception as e:
        return False, 0, [f"Error al parsear respuesta JSON del Judge: {str(e)}"], "Respuesta no parseable"

def run_semantic_self_healing_pipeline(task_prompt: str) -> bool:
    print("\n🚀 === INICIANDO BUCLE DE AUTO-CORRECCIÓN SEMÁNTICA (HITO 12) ===")
    print(f"🎯 Tarea Objetivo: {task_prompt}\n")
    
    current_feedback = None
    
    for attempt in range(1, MAX_RETRIES + 1):
        print(f"─── 🔁 Intento {attempt}/{MAX_RETRIES} ───")
        
        # 1. Coder genera o refactoriza código
        code = generate_code(task_prompt, feedback=current_feedback)
        print("👨‍💻 [Coder] Nuevo código generado.")
        
        # 2. Judge + OPA verifican la calidad y gobernanza
        allow, score, objections, summary = judge_and_opa_gate(task_prompt, code)
        
        print(f"⚖️ [Judge/OPA] Score: {score}/100 | Dictamen: {'✅ ALLOW' if allow else '❌ DENY'}")
        print(f"   └─ Resumen: {summary}")
        
        if allow:
            print(f"\n🎉 ¡ÉXITO DE GOBERNANZA EN EL INTENTO {attempt}! Código aprobado por OPA.")
            print("\n💻 CÓDIGO FINAL APROBADO:")
            print(code)
            
            # Guardar solución aprobada
            with open("solution_approved.py", "w", encoding="utf-8") as f:
                f.write(code)
            return True
        else:
            print(f"⚠️ Intento {attempt} bloqueado por OPA. Motivos/Objeciones:")
            for obj in objections:
                print(f"   ├─ {obj}")
            
            # Construir feedback para la siguiente iteración
            current_feedback = "\n".join([f"- {o}" for o in objections])
            print("🔄 Reinyectando objeciones al Coder para auto-corrección semántica...\n")
            
    print(f"\n❌ Se alcanzó el límite de reintentos ({MAX_RETRIES}). No se logró aprobación semántica.")
    return False

if __name__ == "__main__":
    prompt = "Crea una función 'es_palindromo(texto)' que retorne True si la cadena es palíndromo ignorando mayúsculas, espacios y caracteres de puntuación."
    run_semantic_self_healing_pipeline(prompt)