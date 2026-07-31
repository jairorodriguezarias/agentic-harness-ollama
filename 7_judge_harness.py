import json
import ollama
from typing import Dict, Any

MODEL_NAME = "gemma4"

def llm_as_a_judge(user_prompt: str, generated_code: str) -> Dict[str, Any]:
    """
    Nodo Evaluador Semántico (LLM-as-a-Judge).
    Analiza la calidad, seguridad y mantenibilidad del código generado.
    """
    print("\n⚖️ [LLM-as-a-Judge] Evaluando calidad semántica del código...")
    
    judge_system_prompt = (
        "Eres un Auditor Senior de Código y QA Lead en un pipeline de CI/CD empresarial.\n"
        "Tu tarea es evaluar el código Python generado por un agente de IA.\n\n"
        "Criterios de evaluación (0 a 100):\n"
        "1. Correctitud lógica y cumplimiento de la consigna.\n"
        "2. Manejo de excepciones y casos borde.\n"
        "3. Buenas prácticas de código (clean code, nombres claros, sin funciones peligrosas).\n\n"
        "Debes responder ÚNICAMENTE en formato JSON sintácticamente válido con la siguiente estructura:\n"
        '{\n'
        '  "score": <int_0_100>,\n'
        '  "approved": <bool>,\n'
        '  "summary": "<resumen_breve_de_la_evaluacion>",\n'
        '  "objections": ["<objecion_1>", "<objecion_2>"]\n'
        '}'
    )
    
    user_context = (
        f"--- CONSIGNA DE USUARIO ---\n{user_prompt}\n\n"
        f"--- CÓDIGO GENERADO A EVALUAR ---\n{generated_code}"
    )
    
    response = ollama.chat(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": judge_system_prompt},
            {"role": "user", "content": user_context}
        ]
    )
    
    content = response.get("message", {}).get("content", "")
    
    # Limpieza de bloques de formato Markdown si el modelo los genera
    clean_json = content.replace("```json", "").replace("```", "").strip()
    
    try:
        evaluation = json.loads(clean_json)
        return evaluation
    except Exception as e:
        # Fallback en caso de que falle la decodificación JSON
        return {
            "score": 50,
            "approved": False,
            "summary": f"Fallo al parsear la respuesta del Juez: {str(e)}",
            "objections": ["La salida del evaluador no fue un JSON válido."]
        }

if __name__ == "__main__":
    prompt_original = "Escribe una función 'dividir(a, b)' en Python."
    
    # 🔴 Ejemplo 1: Código deficiente / inseguro
    codigo_malo = """
def dividir(a, b):
    return eval(f"{a} / {b}")
"""
    
    # 🟢 Ejemplo 2: Código robusto
    codigo_bueno = """
def dividir(a: float, b: float) -> float:
    if b == 0:
        raise ValueError("No se puede dividir por cero.")
    return a / b
"""

    print("--- TEST 1: Evaluando código deficiente ---")
    resultado_1 = llm_as_a_judge(prompt_original, codigo_malo)
    print(f"📊 Score: {resultado_1.get('score')} | Aprobado: {resultado_1.get('approved')}")
    print(f"💬 Resumen: {resultado_1.get('summary')}")
    print(f"⚠️ Objeciones: {resultado_1.get('objections')}\n")

    print("--- TEST 2: Evaluando código limpio ---")
    resultado_2 = llm_as_a_judge(prompt_original, codigo_bueno)
    print(f"📊 Score: {resultado_2.get('score')} | Aprobado: {resultado_2.get('approved')}")
    print(f"💬 Resumen: {resultado_2.get('summary')}")
    print(f"⚠️ Objeciones: {resultado_2.get('objections')}")