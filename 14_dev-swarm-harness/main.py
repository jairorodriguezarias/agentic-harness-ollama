import os
from src.agents import agent_issue_pipeline, agent_coder_pipeline
from src.sandbox import validate_syntax_and_safety, execute_in_sandbox
from src.quality_gate import evaluate_quality_gate
from src.git_automation import agent_git_commit_and_push

MAX_RETRIES = 3

def main():
    print("="*65)
    print("🤖 DEV SWARM CLI: AGENTE END-TO-END CON SANDBOXING & OPA")
    print("="*65)
    
    # 1. ENTREVISTA E IDEA INICIAL
    user_prompt = input("\n💬 ¿Qué funcionalidad o módulo quieres construir hoy?: ")
    if not user_prompt.strip():
        print("❌ Requerimiento vacío. Abortando.")
        return

    # 2. PASO 1: ANÁLISIS Y DESGLOSE DINÁMICO DE ISSUES
    print("\n---------------------------------------------------------")
    print("📌 PASO 1: Análisis de Complejidad & Desglose de Issues")
    print("---------------------------------------------------------")
    issues = agent_issue_pipeline(user_prompt)

    print("\n" + "─"*50)
    print(f"📋 [PLAN DE TRABAJO GENERADO: {len(issues)} ISSUE(S)]:")
    print("─"*50)
    for idx, iss in enumerate(issues, 1):
        print(f"  {idx}. [{iss['id']}] {iss['title']} -> ({iss['filepath']})")
    print("─"*50)

    confirm_plan = input("\n❓ ¿Apruebas este plan de trabajo para proceder? [S/n]: ")
    if confirm_plan.strip().lower() in ['n', 'no']:
        print("🛑 Proceso cancelado por el usuario.")
        return

    # 3. PASO 2 & 3: BUCLE CODER + SANDBOX + QUALITY GATE OPA
    generated_code_files = []

    for idx, issue in enumerate(issues, 1):
        print("\n=========================================================")
        print(f"📌 PROCESANDO {issue['id']} ({idx}/{len(issues)}): {issue['title']}")
        print("=========================================================")
        
        feedback_opa = None
        success = False

        for attempt in range(1, MAX_RETRIES + 1):
            print(f"\n─── 🔄 INTENTO {attempt}/{MAX_RETRIES} DE CALIDAD PARA {issue['id']} ───")
            
            # A) Generación de Código con Qwen2.5-Coder + RAG
            final_code, metrics = agent_coder_pipeline(user_prompt, issue['content'], feedback=feedback_opa)
            
            # Telemetría de Ollama
            print(f"⚡ [TELEMETRÍA]: TTFT: {metrics['ttft_ms']}ms | Speed: {metrics['tokens_per_second']} t/s | Tokens: {metrics['total_tokens']}")

            # B) Paso por Sandbox (Análisis AST + Aislamiento en /tmp/)
            print("🛡️ [Hito 4: Sandbox] Validando sintaxis AST y ejecutando en aislado...")
            is_safe, safety_violations = validate_syntax_and_safety(final_code)
            
            if not is_safe:
                print(f"❌ [SANDBOX REJECT]: Violaciones AST detectadas: {safety_violations}")
                feedback_opa = "\n".join(safety_violations)
                continue

            sandbox_ok, sb_msg, sb_err = execute_in_sandbox(final_code, filename=f"test_{issue['id']}.py")
            if not sandbox_ok:
                print(f"❌ [SANDBOX EXEC FAIL]: {sb_err}")
                feedback_opa = f"Error de ejecución en Sandbox: {sb_err}"
                continue
                
            print(f"   └─ {sb_msg}")

            # C) Someter al Quality Gate OPA (Hito 9)
            allow, score, objections = evaluate_quality_gate(final_code)
            print(f"📊 Score OPA: {score}/100 | Dictamen: {'✅ ALLOW' if allow else '❌ DENY'}")

            if allow:
                success = True
                print(f"🎉 {issue['id']} APROBADA en el intento {attempt}.")
                
                # Persistir módulo oficial
                filename = f"module_{issue['id'].lower().replace('-', '_')}.py"
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(final_code)
                generated_code_files.append(filename)
                print(f"💾 Módulo guardado en '{filename}'")
                break
            else:
                print(f"⚠️ Objeciones OPA: {objections}")
                feedback_opa = "\n".join([f"- {o}" for o in objections])

        if not success:
            print(f"\n❌ Se superaron los reintentos para {issue['id']}. Abortando el resto del pipeline.")
            return

    # 4. PASO 4: AUTOMATIZACIÓN DE GIT
    print("\n---------------------------------------------------------")
    print("📌 PASO 4: Finalización & Automatización de Git")
    print("---------------------------------------------------------")
    print(f"✅ Se han completado {len(generated_code_files)} módulo(s): {generated_code_files}")
    
    confirm_git = input("\n❓ ¿Quieres crear la rama de Git y commitear todo el trabajo? [S/n]: ")
    if confirm_git.strip().lower() not in ['n', 'no']:
        agent_git_commit_and_push(user_prompt, generated_code_files)
    else:
        print("💾 Archivos persistidos localmente sin commit.")

if __name__ == "__main__":
    main()