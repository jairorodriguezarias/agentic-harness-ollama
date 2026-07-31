import os
import time
import json
import ollama
from typing import Dict, Any, Tuple

MODEL_NAME = "gemma4"
REPORT_PATH = "eval_report.json"

# ==========================================
# 1. CAPTURA DE MÉTRICAS (PASO 1)
# ==========================================
def parse_ollama_metrics(response: Dict[str, Any]) -> Dict[str, Any]:
    ns_to_sec = 1e-9
    total_duration = response.get("total_duration", 0) * ns_to_sec
    prompt_eval_duration = response.get("prompt_eval_duration", 0) * ns_to_sec
    eval_duration = response.get("eval_duration", 0) * ns_to_sec
    
    prompt_tokens = response.get("prompt_eval_count", 0)
    completion_tokens = response.get("eval_count", 0)
    total_tokens = prompt_tokens + completion_tokens
    
    tokens_per_second = completion_tokens / eval_duration if eval_duration > 0 else 0.0
    
    return {
        "total_latency_sec": round(total_duration, 3),
        "ttft_prompt_eval_sec": round(prompt_eval_duration, 3),
        "generation_time_sec": round(eval_duration, 3),
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": total_tokens,
        "tokens_per_second": round(tokens_per_second, 2)
    }

# ==========================================
# 2. EVALUACIÓN SEMÁNTICA (PASO 2)
# ==========================================
def llm_as_a_judge(user_prompt: str, generated_code: str) -> Dict[str, Any]:
    judge_system_prompt = (
        "Eres un Auditor Senior de Código y QA Lead en un pipeline de CI/CD empresarial.\n"
        "Evalúa el código Python generado según correctitud, manejo de excepciones y seguridad.\n"
        "Responde ÚNICAMENTE en formato JSON válido:\n"
        '{\n'
        '  "score": <int_0_100>,\n'
        '  "approved": <bool>,\n'
        '  "summary": "<resumen_breve>",\n'
        '  "objections": ["<objecion_1>"]\n'
        '}'
    )
    
    user_context = (
        f"--- CONSIGNA --- \n{user_prompt}\n\n"
        f"--- CÓDIGO GENERADO --- \n{generated_code}"
    )
    
    response = ollama.chat(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": judge_system_prompt},
            {"role": "user", "content": user_context}
        ]
    )
    
    content = response.get("message", {}).get("content", "").replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(content)
    except Exception as e:
        return {
            "score": 0,
            "approved": False,
            "summary": f"Fallo al parsear JSON del Juez: {str(e)}",
            "objections": ["Respuesta no parseable"]
        }

# ==========================================
# 3. GENERADOR DE REPORTES (PASO 3)
# ==========================================
def run_llmops_pipeline(prompt_tarea: str, target_file_path: str) -> bool:
    print("🚀 === INICIANDO PIPELINE DE EVALUACIÓN LLMOPS & TRACING ===")
    
    start_wall_time = time.time()
    
    # Paso A: Generar respuesta con el Coder y capturar telemetría
    print(f"1️⃣ Generando código con '{MODEL_NAME}'...")
    response = ollama.chat(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": "Responde ÚNICAMENTE con código Python válido sin bloques de texto."},
            {"role": "user", "content": prompt_tarea}
        ]
    )
    
    wall_clock_duration = time.time() - start_wall_time
    code_generated = response.get("message", {}).get("content", "").replace("```python", "").replace("```", "").strip()
    
    # Paso B: Extraer Métricas
    metrics = parse_ollama_metrics(response)
    metrics["wall_clock_duration_sec"] = round(wall_clock_duration, 3)
    
    # Paso C: Guardar el código generado
    with open(target_file_path, "w", encoding="utf-8") as f:
        f.write(code_generated)
    print(f"   └─ Archivo '{target_file_path}' generado en disco.")
    
    # Paso D: Evaluación Semántica
    print("2️⃣ Invocando Nodo 'LLM-as-a-Judge'...")
    judge_evaluation = llm_as_a_judge(prompt_tarea, code_generated)
    
    # Paso E: Ensamblar Informe Unificado
    full_report = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "model": MODEL_NAME,
        "target_file": target_file_path,
        "telemetry": metrics,
        "quality_gate": judge_evaluation
    }
    
    # Paso F: Exportar JSON de evidencia para el Harness Delegate
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(full_report, f, indent=2, ensure_ascii=False)
    
    print(f"3️⃣ Reporte de auditoría exportado correctamente en: '{REPORT_PATH}'\n")
    
    # Imprimir resumen de aprobación
    score = judge_evaluation.get("score", 0)
    approved = judge_evaluation.get("approved", False)
    
    print("="*55)
    print(" RESULTADO FINAL DEL QUALITY GATE (Harness CI/CD)")
    print("="*55)
    print(f" Score Semántico:     {score}/100")
    print(f" Latencia Total:       {metrics['wall_clock_duration_sec']} s")
    print(f" Velocidad:            {metrics['tokens_per_second']} tokens/seg")
    print(f" Decisión Quality Gate: {' APROBADO' if approved and score >= 80 else ' RECHAZADO'}")
    print("="*55)
    
    return approved and score >= 80

if __name__ == "__main__":
    prompt = "Crea un módulo en Python con una función 'es_palindromo(texto)' que ignore espacios y mayúsculas/minúsculas."
    exito = run_llmops_pipeline(prompt, "palindromo_utils.py")
    
    # Si falla el Quality Gate, abortar ejecutable (Exit Code 1)
    if not exito:
        exit(1)