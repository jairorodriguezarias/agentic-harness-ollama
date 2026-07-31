import json
import ollama
from typing import Dict, Any, List
from src.rag_engine import get_style_rules

MODEL_CODER = "gemma4"
MODEL_JUDGE = "gemma4"

def agent_issue_pipeline(user_prompt: str) -> str:
    """Paso 1: Genera y refina automáticamente la Issue técnica."""
    print("\n📝 [Issue Generator] Creando borrador de Issue...")
    res_draft = ollama.chat(
        model=MODEL_CODER,
        messages=[{"role": "user", "content": f"Crea una Issue técnica para GitHub basada en: {user_prompt}"}]
    )
    draft = res_draft.get("message", {}).get("content", "")

    print("🕵️ [Issue Critic - Auto-Mejora] Auditando y refinando la Issue...")
    prompt_critic = (
        "Eres un Product Owner y QA Lead. Revisa el borrador. Si faltan criterios de aceptación "
        "o hay ambigüedades, REFACTORIZA y devuelve la versión final perfeccionada en Markdown."
    )
    res_refined = ollama.chat(
        model=MODEL_JUDGE,
        messages=[
            {"role": "system", "content": prompt_critic},
            {"role": "user", "content": f"BORRADOR:\n{draft}"}
        ]
    )
    issue_refined = res_refined.get("message", {}).get("content", "")

    with open("GITHUB_ISSUE.md", "w", encoding="utf-8") as f:
        f.write(issue_refined)
    print("📁 Issue refinada guardada en 'GITHUB_ISSUE.md'")
    return issue_refined

def agent_coder_pipeline(user_prompt: str, issue_text: str, feedback: str = None) -> str:
    """Paso 2: Genera código inyectando RAG de Estilo y auto-mejora con el Code Critic."""
    rules = get_style_rules(user_prompt)
    rules_str = "\n".join([f"- {r}" for r in rules])
    print(f"📖 [Style RAG Inyectado]:\n{rules_str}")

    print("👨‍💻 [Coder Specialist] Programando solución...")
    system_prompt = (
        "Eres un Desarrollador Senior de Python.\n"
        "Debes cumplir estrictamente con estas REGLAS DE ARQUITECTURA:\n"
        f"{rules_str}\n\n"
        "Responde ÚNICAMENTE con código Python válido sin bloques de texto adicionales."
    )
    user_context = f"ISSUE DE ORIGEN:\n{issue_text}"
    if feedback:
        user_context += f"\n\n⚠️ RECHAZADO EN EVALUACIÓN PREVIA. CORRIGE ESTAS OBJECIONES:\n{feedback}"

    res_coder = ollama.chat(
        model=MODEL_CODER,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_context}
        ]
    )
    code_raw = res_coder.get("message", {}).get("content", "").replace("```python", "").replace("```", "").strip()

    print("🧐 [Code Critic - Auto-Mejora] Revisando código y aplicando refactorización...")
    res_critic = ollama.chat(
        model=MODEL_JUDGE,
        messages=[
            {"role": "system", "content": "Eres un Revisor de Código. Si encuentras fallos o mejoras, devuelve el CÓDIGO CORREGIDO."},
            {"role": "user", "content": f"CÓDIGO:\n{code_raw}"}
        ]
    )
    improved_code = res_critic.get("message", {}).get("content", "").replace("```python", "").replace("```", "").strip()
    return improved_code if "def " in improved_code else code_raw