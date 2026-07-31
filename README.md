# 🤖 Agentic Engine & Harness Architecture with Ollama

Este repositorio contiene una arquitectura modular progresiva para la creación, evaluación, orquestación e integración de **Agentes Autónomos de Software** basados en **Ollama** (Gemma, Qwen, Llama 3) y pipelines de CI/CD como **Harness**.

---

## 🏛️ Arquitectura por Hitos

### Hito 1: Agent Skills & Harness Initializer (`1_agent_harness.py`)
Implementación básica de llamadas a herramientas (Tool Calling) utilizando Ollama. Modula el acceso determinista al sistema de archivos e invocaciones de comandos.

### Hito 2: Graph Engineering & Multi-Node Orchestration (`2_graph_harness.py`)
Arquitectura en Grafo Acíclico Dirigido (DAG) dividida en 3 nodos principales:
* **Planner**: Genera micro-tareas estructuradas en JSON.
* **Executor**: Selecciona e invoca las Skills necesarias.
* **Evaluator**: Valida determinísticamente el resultado final.

### Hito 3: Self-Healing & Loop Engineering (`3_loop_harness.py`)
Bucle de retroalimentación cerrado. Si una suite de pruebas falla, el sistema inyecta el *traceback* del error nuevamente al LLM para corregir el código automáticamente.

### Hito 4: Execution Isolation & Lightweight Sandbox (`4_sandbox_harness.py`)
Crea un entorno de ejecución efímero e insulado (`/tmp/harness_sandbox`) que bloquea ataques como *directory traversal* o comandos destructivos.

### Hito 5: Multi-Agent Swarm (`5_multiagent_harness.py`)
Orquestación colaborativa multi-persona utilizando un único modelo base:
* **Coder**: Genera la solución técnica.
* **Reviewer**: Realiza análisis estático de seguridad (SAST).
* **Tester**: Genera tests automáticos para validar la implementación.

### Hito 6: Metrics Harness (`6_metrics_harness.py`)
Orquestación colaborativa multi-persona utilizando un único modelo base:
* **Time to First Token (TTFT)**: Latencia en procesar y codificar el prompt inicial.
* **Tokens por Segundo (t/s)**: Velocidad real de generación del modelo en el hardware de tu Mac.
* **Consumo de Ventana de Contexto**: Total de prompt tokens de entrada y completion tokens de salida

### Hito 7: LLM as a judge
Insertar un Juez Evaluador en Python que actuará como Quality Gate

[ Agente Coder ] ──► [ Genera Código ] ──► [ LLM-as-a-Judge ]
                                                 				    │
                                     ┌───────────┴────┐
                                     ▼                       				      ▼
                               Score >= 80            				  Score < 80
                             (Aprobado CI/CD)     			(Fallo / Auto-Corrección)

### Hito 8: Policy
Crear un archivo REGO, con las politicas



### Hito 9:


### Hito 10: 


---

## 🚀 Guía de Instalación y Uso

### Requisitos Previos
* **Python 3.10+**
* **Ollama** ejecutándose localmente (`ollama serve`)

```bash
# Servir e instalar el modelo
ollama pull gemma4
ollama pull qwen2.5-coder
```

### Configuración del Entorno

```bash
# 1. Clonar el repositorio
git clone https://github.com/tu-usuario/agentic-harness-ollama.git
cd agentic-harness-ollama

# 2. Crear y activar el entorno virtual
python3 -m venv venv
source venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Dar permisos de ejecución a los scripts auxiliares
chmod +x run_harness_agent.sh
```

### Ejecución de los Agentes

```bash

###Parte 1: Basicos

# Hito 1: Tool Calling
python3 1_agent_harness.py

# Hito 2: Graph Pipeline
python3 2_graph_harness.py

# Hito 3: Self-Healing Loop
python3 3_loop_harness.py

# Hito 4: Sandbox
python3 4_sandbox_harness.py

# Hito 5: Multi-Agent Swarm
python3 5_multiagent_harness.py

###Parte 2: Metricas, evaluación y reportes

# Hito 6: Metric Harness
python3 6_metric_harness.py

# Hito 7: Evaluador Semántico (LLM-as-a-Judge)
python3 7_judge_harness.py

# Hito 8: Generación de Reporte y Quality Gate de Auditoría
python3 8_report_harness.py

###Parte 3: Gobernanza, Multi-Modelo y Trazabilidad Avanzada

# Hito 9: Policy-as-Code Engine (`9_opa_harness.py` + `policy.rego`)**
  Evaluación determinista de políticas corporativas mediante reglas Rego (OPA). Bloquea despliegues si la latencia o la calidad semántica no cumplen los SLAs exigidos.

# Hito 10: Multi-Model Orchestration (`10_multimodel_harness.py`)**
  Orquestación local en caliente combinando modelos especializados (Coder vs. Auditor) sin sobrecargar la RAM.

# Hito 11: Reasoning Trace Auditor (`11_reasoning_trace_harness.py`)**
  Extracción e inspección de las trazas de pensamiento internas (`<think>`) del modelo para auditoría de cumplimiento y depuración de decisiones de diseño (`reasoning_audit.log`).

# Simulador de Ejecución para Harness Delegate
./run_harness_agent.sh
```
