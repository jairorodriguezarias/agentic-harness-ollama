import time
import ollama
from typing import Dict, Any, Tuple

# Tag exacto de tu modelo local en Ollama (p. ej. "gemma4" o el que uses en tu Mac)
MODEL_NAME = "gemma4"

class LLMOpsMetricsCollector:
    """Clase encargada de capturar, procesar y presentar métricas de inferencia de Ollama."""
    
    @staticmethod
    def parse_ollama_metrics(response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extrae la telemetría nativa enviada por la API de Ollama y la convierte a unidades legibles:
        - total_duration: tiempo total en nanosegundos
        - prompt_eval_duration: tiempo procesando el prompt de entrada (TTFT aproximado)
        - eval_duration: tiempo de generación del completion
        - prompt_eval_count / eval_count: número de tokens
        """
        ns_to_sec = 1e-9  # Conversión de nanosegundos a segundos
        
        total_duration = response.get("total_duration", 0) * ns_to_sec
        prompt_eval_duration = response.get("prompt_eval_duration", 0) * ns_to_sec
        eval_duration = response.get("eval_duration", 0) * ns_to_sec
        
        prompt_tokens = response.get("prompt_eval_count", 0)
        completion_tokens = response.get("eval_count", 0)
        total_tokens = prompt_tokens + completion_tokens
        
        # Cálculo de velocidad de generación: tokens / segundo
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

def chat_with_telemetry(prompt: str, model: str = MODEL_NAME) -> Tuple[str, Dict[str, Any]]:
    """Ejecuta una llamada a Ollama y retorna el contenido junto con el reporte de telemetría."""
    print(f"⏱️ [LLMOps] Enviando prompt a Ollama ('{model}')...")
    
    start_wall_time = time.time()
    
    response = ollama.chat(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )
    
    end_wall_time = time.time()
    wall_clock_duration = end_wall_time - start_wall_time
    
    content = response.get("message", {}).get("content", "")
    metrics = LLMOpsMetricsCollector.parse_ollama_metrics(response)
    metrics["wall_clock_duration_sec"] = round(wall_clock_duration, 3)
    
    return content, metrics

def print_telemetry_report(metrics: Dict[str, Any]):
    """Imprime un reporte estructurado de rendimiento para el desarrollador o log del Harness Delegate."""
    print("\n" + "="*55)
    print(" REPORTE DE TELEMETRÍA DE INFERENCIA (LLMOps - Step 1)")
    print("="*55)
    print(f"Latencia Total (Wall Clock): {metrics['wall_clock_duration_sec']} s")
    print(f"Time to First Token (TTFT): {metrics['ttft_prompt_eval_sec']} s")
    print(f"Tiempo de Generación:       {metrics['generation_time_sec']} s")
    print(f"Velocidad de Generación:     {metrics['tokens_per_second']} tokens/seg")
    print("-" * 55)
    print(f"Tokens de Entrada (Prompt): {metrics['prompt_tokens']}")
    print(f"Tokens de Salida (Result): {metrics['completion_tokens']}")
    print(f"Tokens Totales Consumidos: {metrics['total_tokens']}")
    print("="*55 + "\n")

if __name__ == "__main__":
    prompt_prueba = (
        "Escribe una función en Python para calcular los primeros N números "
        "de la sucesión de Fibonacci y retorna una lista con el resultado."
    )
    
    respuesta, telemetria = chat_with_telemetry(prompt_prueba)
    
    print("[Respuesta del Modelo]:")
    print(respuesta)
    
    print_telemetry_report(telemetria)