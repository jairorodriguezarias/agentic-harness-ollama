import json
import ollama
from typing import Tuple, List

MODEL_JUDGE = "gemma4"

def evaluate_quality_gate(code: str) -> Tuple[bool, int, List[str]]:
    """Paso 3: Somete el código al filtro de OPA / LLM-as-a-Judge."""
    print("🛡️ [Quality Gate / OPA Engine] Evaluando calidad y gobernanza semántica...")
    
    system_prompt = (
        "Eres un Auditor de Código y Motor OPA. Evalúa el código Python y responde ÚNICAMENTE en JSON válido:\n"
        '{\n  "score": <int_0_100>,\n  "approved": <bool>,\n  "objections": ["<objecion_1>"]\n}'
    )
    
    res = ollama.chat(
        model=MODEL_JUDGE,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"CÓDIGO:\n{code}"}
        ]
    )
    
    raw = res.get("message", {}).get("content", "").replace("```json", "").replace("```", "").strip()
    
    try:
        data = json.loads(raw)
        score = data.get("score", 0)
        approved = data.get("approved", False)
        objections = data.get("objections", [])
        allow = approved and score >= 80
        return allow, score, objections
    except Exception as e:
        return False, 0, [f"Error al parsear respuesta JSON de OPA: {str(e)}"]