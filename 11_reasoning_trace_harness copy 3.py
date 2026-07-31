import re
import json
import ollama
from typing import Tuple, Dict, Any

MODEL_NAME = "gemma4"

def parse_reasoning_trace(raw_response: str) -> Tuple[str, str]:
    """
    Extrae la traza de razonamiento (<think>...</think>) y la separa de la respuesta final.
    """
    think_pattern = r"<think>(.*?)</think>"
    match = re.search(think_pattern, raw_response, re.DOTALL)
    
    if match:
        reasoning_trace = match.group(1).strip()
        # Eliminar el bloque <think> del contenido final
        clean_content = re.sub(think_pattern, "", raw_response, flags=re.DOTALL).strip()
    else:
        reasoning_trace = "No se detectó un bloque explícito <think>. Razonamiento implícito."
        clean_content = raw_response.strip()
        
    return reasoning_trace, clean_content

def ask_model_with_reasoning_trace(prompt: str) -> Dict[str, Any]:
    """
    Fuerza al modelo a explicitar su razonamiento en un bloque <think> antes de dar el código.
    """
    print(f"\n🧠 [Reasoning Engine] Procesando prompt con inspección de pensamiento...")
    
    system_prompt = (
        "Eres un Ingeniero de Software Senior.\n"
        "ANTES de escribir el código final, debes incluir un bloque <think> en el que expliques paso a paso:\n"
        "1. Tus suposiciones y análisis del problema.\n"
        "2. Qué casos borde vas a manejar.\n"
        "3. La complejidad temporal y espacial estimada.\n"
        "</think>\n\n"
        "Después de cerrar la etiqueta </think>, escribe ÚNICAMENTE el código Python final."
    )
    
    response = ollama.chat(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
    )
    
    raw_content = response.get("message", {}).get("content", "")
    trace, code = parse_reasoning_trace(raw_content)
    
    return {
        "reasoning_trace": trace,
        "final_code": code.replace("```python", "").replace("```", "").strip()
    }

if __name__ == "__main__":
    prompt_usuario = "Implementa una función 'buscar_subcadena_kmp(texto, patron)' que use el algoritmo Knuth-Morris-Pratt."
    
    resultado = ask_model_with_reasoning_trace(prompt_usuario)
    
    print("\n" + "="*60)
    print("🔍 TRAZA DE RAZONAMIENTO AUDITADA (Chain-of-Thought Trace)")
    print("="*60)
    print(resultado["reasoning_trace"])
    print("="*60)
    
    print("\n💻 CÓDIGO GENERADO:")
    print(resultado["final_code"])
    print("="*60 + "\n")
    
    # Exportar la traza a un log de auditoría local
    with open("reasoning_audit.log", "w", encoding="utf-8") as f:
        f.write(f"PROMPT: {prompt_usuario}\n\n")
        f.write(f"TRAZA DE RAZONAMIENTO:\n{resultado['reasoning_trace']}\n\n")
        f.write(f"CÓDIGO RESULTANTE:\n{resultado['final_code']}\n")
    print("📁 Traza de razonamiento guardada en 'reasoning_audit.log'")