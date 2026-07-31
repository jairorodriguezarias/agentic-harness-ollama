import os
import json
import re
import math
from typing import List

STORAGE_PATH = os.path.join("config", "style_memory.json")

def tokenize(text: str) -> List[str]:
    return re.findall(r'\w+', text.lower())

def compute_tfidf(query: str, doc: str) -> float:
    q_tokens = set(tokenize(query))
    d_tokens = tokenize(doc)
    if not q_tokens or not d_tokens:
        return 0.0
    return sum((d_tokens.count(t) / len(d_tokens)) * (1 + math.log(len(t))) for t in q_tokens if t in d_tokens)

def get_style_rules(task_description: str) -> List[str]:
    """Recupera las normas de arquitectura relevantes para la tarea."""
    if not os.path.exists(STORAGE_PATH):
        return ["REGLA: Usa Type Hints y docstrings explícitos."]

    with open(STORAGE_PATH, "r", encoding="utf-8") as f:
        memory = json.load(f)

    scores = [(compute_tfidf(task_description, item["content"]), item["content"]) for item in memory]
    scores.sort(key=lambda x: x[0], reverse=True)
    return [content for sim, content in scores[:2]] or [m["content"] for m in memory[:2]]