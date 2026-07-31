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

---

## 🚀 Guía de Instalación y Uso

### Requisitos Previos
* **Python 3.10+**
* **Ollama** ejecutándose localmente (`ollama serve`)

```bash
# Servir e instalar el modelo
ollama pull gemma4
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

# Hito 6: Metric Harness
python3 6_metric_harness.py

# Harness Delegate Script Execution
./run_harness_agent.sh
```
