# 🤖 Dev Swarm Harness: Autonomous Agentic Engineering Platform

> **Local-First, Multi-Agent Development Swarm with AST Sandboxing, Style RAG, and OPA Governance**

---

## 📌 Visión General

**Dev Swarm Harness** es una plataforma modular de ingeniería asistida por inteligencia artificial que se ejecuta **100% On-Premises** utilizando **Ollama** (`qwen2.5-coder`).

Integra un enjambre de agentes especializados que colaboran de manera autónoma para desglosar requerimientos, recuperar guías de diseño, escribir código, aislar su ejecución en una sandbox, auditar la calidad mediante políticas OPA y commitear los resultados en Git.

---

## 🏛️ Arquitectura del Enjambre

```text
 💻 Usuario (Terminal CLI) ──► 📝 Issue Generator ──► 🕵️ Issue Critic
                                                          │
                                                          ▼
 🛡️ OPA Gate ◄── 🧪 AST Sandbox ◄── 🧐 Code Critic ◄── 👨‍💻 Coder Specialist (Style RAG)
      │               │                  ▲
   Score < 80     Violación              │ (Bucle Self-Healing)
   (Reintento)    (Reintento) ───────────┘
      │
   ✅ ALLOW
      │
      ▼
 🚀 Git Operations Agent (Branching -> Commit -> Push)