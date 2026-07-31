package harness.quality_gate

default allow = false

# Regla principal de aprobación
allow {
    score_suficiente
    sin_vulnerabilidades_criticas
    latencia_aceptable
}

# 1. El Score del Judge debe ser igual o mayor a 80
score_suficiente {
    input.quality_gate.score >= 80
}

# 2. El booleano 'approved' debe ser True
sin_vulnerabilidades_criticas {
    input.quality_gate.approved == true
}

# 3. La latencia total de inferencia debe ser inferior a 120 segundos
latencia_aceptable {
    input.telemetry.wall_clock_duration_sec < 120.0
}