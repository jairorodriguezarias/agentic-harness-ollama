import os
import subprocess

def agent_git_commit_and_push(user_prompt: str, code: str):
    """Paso 4: Escribe el módulo en disco, crea una rama y hace el commit."""
    print("\n🚀 [Git Agent] Escribiendo archivo y gestionando repositorio Git...")
    
    filename = "app_module.py"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(code)
    print(f"💾 Código guardado en '{filename}'")

    branch = f"feature/auto-{os.urandom(2).hex()}"
    try:
        subprocess.run(["git", "checkout", "-b", branch], check=True)
        subprocess.run(["git", "add", filename, "GITHUB_ISSUE.md"], check=True)
        subprocess.run(["git", "commit", "-m", f"feat: {user_prompt[:50]}"], check=True)
        print(f"🌿 Cambios commiteados exitosamente en la rama local '{branch}'!")
        
        confirm = input("❓ ¿Deseas hacer 'git push origin' de esta rama? [s/N]: ")
        if confirm.lower() == 's':
            subprocess.run(["git", "push", "origin", branch], check=True)
            print("🎉 Rama subida a GitHub con éxito.")
    except Exception as e:
        print(f"⚠️ Error al ejecutar comandos de Git: {e}")