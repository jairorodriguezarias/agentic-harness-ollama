#!/bin/bash
set -e

echo "🚀 [Harness Delegate Step] Iniciando Agente de IA..."

# 1. Asegurar entorno virtual
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# 2. Ejecutar el Bucle de Auto-Corrección
python3 3_loop_harness.py

# 3. Retornar código de salida para Harness Manager
if [ $? -eq 0 ]; then
    echo "✅ [Harness Step] El agente completó la tarea y pasó los tests con éxito."
    exit 0
else
    echo "❌ [Harness Step] El agente falló al auto-corregir el código."
    exit 1
fi
