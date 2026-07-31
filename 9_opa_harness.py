import json
import os
import sys

REPORT_PATH = "eval_report.json"

def evaluate_opa_policy(report_file: str) -> dict:
    """
    Simula el motor de validación de Open Policy Agent (OPA / Rego)[cite: 353, 920].
    Somete el artefacto eval_report.json a las políticas estrictas de gobernanza[cite: 353, 921].
    """
    print(f"🔒 [OPA Policy Engine] Cargando informe de auditoría '{report_file}'...")
    
    if not os.path.exists(report_file):
        return {
            "allow": False,
            "violations": [f"El archivo de evidencia '{report_file}' no existe."]
        }
        
    with open(report_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    violations = []
    
    # Extraer campos de la evidencia
    quality_gate = data.get("quality_gate", {})
    telemetry = data.get("telemetry", {})
    
    score = quality_gate.get("score", 0)
    approved = quality_gate.get("approved", False)
    objections = quality_gate.get("objections", [])
    latency = telemetry.get("wall_clock_duration_sec", 999.0)
    
    # Evaluación de Reglas Rego
    if score < 80:
        violations.append(f"REGO_RULE_01: Score insuficiente ({score}/100). Mínimo requerido: 80.")
        
    if not approved:
        violations.append(f"REGO_RULE_02: El flag 'approved' es False. Objeciones: {objections}")
        
    if latency > 120.0:
        violations.append(f"REGO_RULE_03: Latencia excesiva ({latency}s). Máximo permitido: 120s.")
        
    allow = len(violations) == 0
    
    return {
        "allow": allow,
        "score": score,
        "latency": latency,
        "violations": violations
    }

if __name__ == "__main__":
    resultado = evaluate_opa_policy(REPORT_PATH)
    
    print("\n" + "="*55)
    print("🛡️ REPORTE DE GOBERNANZA POLICY-AS-CODE (OPA)")
    print("="*55)
    print(f"🎯 Estado de la Política: {'✅ ALLOW (Pasa a CD)' if resultado['allow'] else '❌ DENY (Bloqueado por OPA)'}")
    print(f"📊 Score Validado:       {resultado['score']}/100")
    print(f"⏱️ Latencia Validada:    {resultado['latency']} s")
    
    if resultado["violations"]:
        print("\n🚨 VIOLACIONES DE POLÍTICA DETECTADAS:")
        for v in resultado["violations"]:
            print(f"  └─ {v}")
    print("="*55 + "\n")
    
    # Retornar código de salida para Harness Delegate [cite: 15, 165, 826]
    if not resultado["allow"]:
        sys.exit(1)