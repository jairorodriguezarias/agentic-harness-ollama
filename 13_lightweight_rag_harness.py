import os
import json
import re
import math
import ollama
from typing import List, Dict, Any

MODEL_CODER = "qwen2.5-coder"
STORAGE_PATH = "style_memory.json"

# ==========================================
# 1. MOTOR DE BÚSQUEDA LÉXICA ULTRA-LIGERO (TF-IDF)
# ==========================================
def tokenize(text: str) -> List[str]:
    """Tokeniza y limpia texto en palabras clave minúsculas."""
    return re.findall(r'\w+', text.lower())

def compute_tfidf_similarity(query: str, doc: str) -> float:
    """Calcula similitud de relevancia basada en coincidencia de términos de búsqueda."""
    query_tokens = set(tokenize(query))
    doc_tokens = tokenize(doc)
    
    if not query_tokens or not doc_tokens:
        return 0.0
        
    score = 0.0
    for token in query_tokens:
        count = doc_tokens.count(token)
        if count > 0:
            # Frecuencia de término simple ponderada por longitud
            score += (count / len(doc_tokens)) * (1 + math.log(len(token)))
            
    return score

# ==========================================
# 2. ALMACÉN DE MEMORIA EN JSON
# ==========================================
class LightweightStyleMemory:
    def __init__(self, storage_path: str = STORAGE_PATH):
        self.storage_path = storage_path
        self.memory: List[Dict[str, str]] = []
        self._load_memory()

    def _load_memory(self):
        if os.path.exists(self.storage_path):
            with open(self.storage_path, "r", encoding="utf-8") as f:
                self.memory = json.load(f)
            print(f"📚 [StyleMemory] Cargadas {len(self.memory)} reglas de arquitectura desde JSON.")
        else:
            self.memory = []

    def save_memory(self):
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump(self.memory, f, indent=2, ensure_ascii=False)

    def add_rule(self, rule_id: str, content: str):
        self.memory.append({"id": rule_id, "content": content})
        self.save_memory()

    def search_rules(self, query: str, top_k: int = 2) -> List[str]:
        if not self.memory:
            return []
            
        scores = []
        for item in self.memory:
            sim = compute_tfidf_similarity(query, item["content"])
            scores.append((sim, item["content"]))
            
        # Ordenar por relevancia
        scores.sort(key=lambda x: x[0], reverse=True)
        return [content for sim, content in scores[:top_k] if sim > 0] or [m["content"] for m in self.memory[:top_k]]

# ==========================================
# 3. PIPELINE DE GENERACIÓN CON RAG DE ESTILO
# ==========================================
def seed_style_guidelines(memory: LightweightStyleMemory):
    """Poblar la memoria local si está vacía."""
    if len(memory.memory) == 0:
        print("🌱 Poblando la memoria de convenciones de arquitectura...")
        memory.add_rule("rule_typing", "REGLA_ESTILO_01: Todo código Python debe incluir Type Hints explícitos en los parámetros y retorno.")
        memory.add_rule("rule_exceptions", "REGLA_ESTILO_02: Valida siempre tipos de entrada y lanza explicítamente excepciones como ValueError o TypeError.")
        memory.add_rule("rule_formatting", "REGLA_ESTILO_03: Incluye docstrings explicativos para cada función creada.")

def generate_code_with_style_rag(task_prompt: str) -> str:
    memory = LightweightStyleMemory()
    seed_style_guidelines(memory)
    
    # RAG: Buscar las reglas más relevantes
    print(f"\n🔍 [RAG Light] Buscando reglas de arquitectura relevantes para: '{task_prompt}'...")
    relevant_rules = memory.search_rules(task_prompt, top_k=2)
    
    rules_text = "\n".join([f"- {r}" for r in relevant_rules])
    print(f"📖 [Reglas Inyectadas de la Memoria Local]:\n{rules_text}\n")
    
    system_prompt = (
        "Eres un Desarrollador Senior de Python.\n"
        "Debes cumplir estrictamente con las siguientes REGLAS DE ARQUITECTURA:\n"
        f"{rules_text}\n\n"
        "Responde ÚNICAMENTE con código Python válido que aplique estas reglas."
    )
    
    response = ollama.chat(
        model=MODEL_CODER,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": task_prompt}
        ]
    )
    
    code = response.get("message", {}).get("content", "").replace("```python", "").replace("```", "").strip()
    return code

if __name__ == "__main__":
    prompt_usuario = "Crea una función 'calcular_promedio(numeros)' que retorne la media aritmética de una lista."
    codigo = generate_code_with_style_rag(prompt_usuario)
    
    print("💻 [Código Generado con Memoria de Estilo]:")
    print(codigo)