import json
import time
import ollama

# Asignación de modelos especializados en local
MODEL_CODER = "qwen2.5-coder" # O usa "gemma4" si aún no descargaste qwen
MODEL_JUDGE = "gemma4"

def generate_code_with_specialist(prompt: str) -> str:
    """Invoca al modelo especializado en generación de código (Coder)."""
    print(f"\n👨‍💻 [CODER] Solicitando implementación a '{MODEL_CODER}'...")
    response = ollama.chat(
        model=MODEL_CODER,
        messages=[
            {"role": "system", "content": "Eres un Desarrollador Senior de Python. Responde ÚNICAMENTE con código Python válido."},
            {"role": "user", "content": prompt}
        ]
    )
    code = response.get("message", {}).get("content", "").replace("```python", "").replace("```", "").strip()
    return code

def evaluate_code_with_judge(prompt: str, code: str) -> dict:
    """Invoca al modelo especializado en auditoría y calidad (Judge)."""
    print(f"⚖️ [JUDGE] Invocando auditoría semántica con '{MODEL_JUDGE}'...")
    system_prompt = (
        "Eres un Auditor Senior de Código. Evalúa el código Python y responde ÚNICAMENTE en JSON válido:\n"
        '{\n  "score": <int_0_100>,\n  "approved": <bool>,\n  "summary": "<resumen>",\n  "objections": ["<objecion>"]\n}'
    )
    response = ollama.chat(
        model=MODEL_JUDGE,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Tarea: {prompt}\n\nCódigo:\n{code}"}
        ]
    )
    content = response.get("message", {}).get("content", "").replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(content)
    except Exception as e:
        return {"score": 0, "approved": False, "summary": f"Error JSON: {str(e)}", "objections": []}

if __name__ == "__main__":
    prompt_tarea = "Escribe una función 'es_anagrama(palabra1, palabra2)' en Python que ordene y compare cadenas ignorando espacios."
    
    # 1. El Coder genera la solución
    codigo = generate_code_with_specialist(prompt_tarea)
    print("\n📝 [Código Producido por Coder]:")
    print(codigo)
    
    # 2. El Judge realiza la auditoría
    evaluacion = evaluate_code_with_judge(prompt_tarea, codigo)
    
    print("\n📊 [Resultado de la Evaluación Multi-Modelo]:")
    print(f"  └─ Score: {evaluacion.get('score')}/100")
    print(f"  └─ Aprobado: {evaluacion.get('approved')}")
    print(f"  └─ Objeciones: {evaluacion.get('objections')}")