---

```markdown
# 🤖 Agentic Engine & Harness Architecture with Ollama

Este repositorio contiene una arquitectura modular e incremental para diseñar, evaluar, gobernar y auditar **Agentes Autónomos de Software** basados en **Ollama** (Gemma, Qwen 2.5 Coder) e integrados localmente con pipelines de CI/CD como **Harness**.

Toda la arquitectura funciona **100% On-Premises / Local First**, optimizada para ejecutarse en entornos con recursos limitados (como una MacBook Air) sin depender de servicios de nube pagados ni GPUs externas.

---

## 🏛️ Arquitectura por Hitos (1 al 13)

### 🟢 Parte 1: Agent Architecture & Execution Isolation

* **Hito 1: Agent Skills & Harness Initializer (`1_agent_harness.py`)**
  Implementación básica de llamadas a herramientas (*Tool Calling*) deterministas con Ollama. Modula el acceso seguro al sistema de archivos (`read_file`, `write_file`) y la ejecución de comandos.

* **Hito 2: Graph Engineering & Multi-Node Orchestration (`2_graph_harness.py`)**
  Estructuración de la ejecución como un Grafo Dirigido Acíclico (DAG) dividido en 3 nodos independientes:
  * **Planner**: Desglosa el objetivo en micro-tareas estructuradas en JSON.
  * **Executor**: Selecciona e invoca las herramientas (*Skills*) requeridas.
  * **Evaluator**: Valida determinísticamente la existencia y estado de los artefactos.

* **Hito 3: Self-Healing & Loop Engineering (`3_loop_harness.py`)**
  Bucle de retroalimentación cerrado para errores de ejecución. Si la suite de pruebas unitarias falla, el *traceback* del error se inyecta de nuevo al modelo para corregir el código automáticamente (hasta `MAX_RETRIES = 3`).

* **Hito 4: Execution Isolation & Lightweight Sandbox (`4_sandbox_harness.py`)**
  Entorno de ejecución efímero e insulado (`/tmp/harness_sandbox`) que optimiza la memoria RAM y bloquea ataques de *directory traversal* o comandos destructivos (`sudo`, `rm -rf`).

* **Hito 5: Multi-Agent Swarm (`5_multiagent_harness.py`)**
  Orquestación colaborativa de tres roles en memoria compartiendo una sola instancia del modelo en RAM:
  * **Coder**: Diseña e implementa el código.
  * **Reviewer**: Realiza análisis estático de seguridad (SAST).
  * **Tester**: Genera y ejecuta la suite de pruebas unitarias.

---

### 🟣 Parte 2: LLMOps, Métricas y Evaluación Semántica

* **Hito 6: LLMOps Metrics & Token Tracking (`6_metrics_harness.py`)**
  Instrumentación de la telemetría de inferencia enviada por Ollama en tiempo real:
  * **Time to First Token (TTFT)**: Latencia en procesar y codificar el prompt de entrada.
  * **Tokens por Segundo (t/s)**: Velocidad real de generación del modelo.
  * **Consumo de Contexto**: Mapeo exacto de *prompt tokens* de entrada y *completion tokens* de salida.

* **Hito 7: Semantic Evaluation & LLM-as-a-Judge (`7_judge_harness.py`)**
  Nodo Evaluador Semántico que actúa como *Quality Gate*. Evalúa arquitectura, legibilidad, seguridad y manejo de excepciones, asignando un Score de 0 a 100 y una lista de objeciones:

```text
[ Agente Coder ] ──► [ Genera Código ] ──► [ LLM-as-a-Judge ]
                                                 │
                                     ┌───────────┴───────────┐
                                     ▼                       ▼
                               Score >= 80              Score < 80
                             (Aprobado CI/CD)     (Rechazado / Reintento)

```

* **Hito 8: Audit Report & Evidence Export (`8_report_harness.py`)**
Consolidación de métricas de latencia, código producido y la evaluación del *Judge* en un archivo JSON unificado (`eval_report.json`). Sirve como artefacto de evidencia para el Harness Delegate.

---

### 🔴 Parte 3: Gobernanza, Multi-Modelo y Trazabilidad

* **Hito 9: Policy-as-Code Engine (`9_opa_harness.py` + `policy.rego`)**
Evaluador de políticas de gobernanza basado en **Open Policy Agent (OPA)**. Valida reglas declarativas escritas en **Rego** sobre `eval_report.json` para autorizar (`ALLOW`) o bloquear (`DENY`) el despliegue.
* **Hito 10: Multi-Model Orchestration (`10_multimodel_harness.py`)**
Orquestación local en caliente combinando modelos especializados por función (ej. `qwen2.5-coder` para síntesis de código y `gemma4` para auditoría y juicio) sin saturar la RAM.
* **Hito 11: Chain-of-Thought Reasoning Trace Auditor (`11_reasoning_trace_harness.py`)**
Extracción y separación del proceso de pensamiento del modelo (`<think>...</think>`) de la solución final. Exporta la traza de razonamiento a `reasoning_audit.log` para auditorías de diseño.

---

### 🟡 Parte 4: Resiliencia Semántica y Memoria Local

* **Hito 12: Semantic Self-Healing Loop (`12_semantic_self_healing_harness.py`)**
Bucle de auto-corrección de calidad y gobernanza. Si OPA o el Judge rechazan el código por falta de *type checking* o casos borde no cubiertos, las objeciones se inyectan como *feedback prompt* estructurado para refactorizar la solución automáticamente hasta lograr aprobación:

```text
[ Coder Genera Código ] ──► [ Judge + OPA Evalúan ]
            ▲                               │
            │                         Score < 80 / DENY
            └─ Reinyecta Objeciones ────────┴─ (Bucle de Corrección Semántica)

```

* **Hito 13: Lightweight Style RAG & Local Memory (`13_lightweight_rag_harness.py`)**
Motor de memoria de estilo y arquitectura ultra-ligero (basado en TF-IDF en Python puro sin dependencias externas pesadas). Almacena convenciones en `style_memory.json` e inyecta las reglas relevantes al prompt del Coder.

---

## 🚀 Guía de Instalación y Uso

### Requisitos Previos

* **Python 3.10+**
* **Ollama** instalado y ejecutándose localmente (`ollama serve`)

```bash
# Descargar el modelo base en Ollama
ollama pull gemma4

```

### Configuración del Entorno Local

```bash
# 1. Clonar el repositorio
git clone [https://github.com/jairorodriguezarias/agentic-harness-ollama.git](https://github.com/jairorodriguezarias/agentic-harness-ollama.git)
cd agentic-harness-ollama

# 2. Crear y activar el entorno virtual
python3 -m venv venv
source venv/bin/activate

# 3. Instalar dependencias ligeras
pip install -r requirements.txt

# 4. Asignar permisos de ejecución a los scripts
chmod +x run_harness_agent.sh run_all_harness_checks.sh

```

### Ejecución por Hitos

```bash
# Parte 1: Arquitectura de Agentes
python3 1_agent_harness.py
python3 2_graph_harness.py
python3 3_loop_harness.py
python3 4_sandbox_harness.py
python3 5_multiagent_harness.py

# Parte 2: LLMOps & Métricas
python3 6_metrics_harness.py
python3 7_judge_harness.py
python3 8_report_harness.py

# Parte 3: Gobernanza & Observabilidad
python3 9_opa_harness.py
python3 10_multimodel_harness.py
python3 11_reasoning_trace_harness.py

# Parte 4: Resiliencia & Memoria
python3 12_semantic_self_healing_harness.py
python3 13_lightweight_rag_harness.py

# Suite Unificada para Harness Delegate (CI/CD Pipeline)
./run_all_harness_checks.sh

```

```

```