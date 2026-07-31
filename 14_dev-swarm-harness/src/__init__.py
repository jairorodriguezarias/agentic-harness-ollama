"""
Dev Swarm Harness Package
Plataforma modular e interactiva de desarrollo asistido por Enjambre Multi-Agente.
"""

from src.rag_engine import get_style_rules
from src.agents import agent_issue_pipeline, agent_coder_pipeline
from src.sandbox import execute_in_sandbox, validate_syntax_and_safety
from src.quality_gate import evaluate_quality_gate
from src.git_automation import agent_git_commit_and_push

__version__ = "1.0.0"
__all__ = [
    "get_style_rules",
    "agent_issue_pipeline",
    "agent_coder_pipeline",
    "execute_in_sandbox",
    "validate_syntax_and_safety",
    "evaluate_quality_gate",
    "agent_git_commit_and_push",
]