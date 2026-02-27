import sys
import subprocess
import importlib.util

print("=" * 50)
print("VERIFICACAO DO AMBIENTE PYTHON")
print("=" * 50)

# Versao do Python
print(f"\n[Python]")
print(f"  Versao : {sys.version}")
print(f"  Caminho: {sys.executable}")

# Verificar dependencias do projeto
print(f"\n[Dependencias do Projeto]")
dependencias = ["requests", "python-dotenv"]

for dep in dependencias:
    # Normalizar nome para importacao
    nome_import = dep.replace("-", "_")
    if nome_import == "python_dotenv":
        nome_import = "dotenv"

    spec = importlib.util.find_spec(nome_import)
    if spec is not None:
        # Pegar versao instalada
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "show", dep],
                capture_output=True, text=True
            )
            versao = "?"
            for linha in result.stdout.split("\n"):
                if linha.startswith("Version:"):
                    versao = linha.split(": ")[1].strip()
            print(f"  [OK] {dep:<20} v{versao}")
        except Exception:
            print(f"  [OK] {dep:<20} (instalada)")
    else:
        print(f"  [FALTANDO] {dep:<20} => rode: pip install {dep}")

# Recomendação minima
print(f"\n[Recomendacao para VPS]")
major, minor = sys.version_info[:2]
if major >= 3 and minor >= 8:
    print(f"  [OK] Python {major}.{minor} esta dentro do suporte recomendado (>= 3.8)")
else:
    print(f"  [ATENCAO] Python {major}.{minor} pode ser muito antigo. Use Python 3.8+")

print("\n" + "=" * 50)
print("Para instalar dependencias na VPS:")
print("  pip install -r requirements.txt")
print("=" * 50)
