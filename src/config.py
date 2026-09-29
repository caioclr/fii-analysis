import os
from pathlib import Path

# Diretórios base
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# Carrega arquivo .env da raiz do projeto automaticamente
ENV_FILE = BASE_DIR / ".env"
if ENV_FILE.exists():
    try:
        with open(ENV_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip().strip("'\""))
    except Exception:
        pass

DB_PATH = DATA_DIR / "portfolio.db"

# Categorias de Ativos
ASSET_TYPES = {
    "FII": "Fundos Imobiliários",
    "ACAO": "Ações",
    "RENDA_FIXA": "Renda Fixa",
    "OUTRO": "Outros"
}

# Segmentos comuns de FIIs
FII_SEGMENTS = [
    "Logística / Galpões",
    "Shoppings",
    "Papel / CRI",
    "Lajes Corporativas",
    "Híbrido",
    "Fundos de Fundos (FOF)",
    "Renda Urbana / Varejo",
    "Agro (Fiagro)",
    "Desenvolvimento",
    "Outros"
]

# Cache timeout em segundos (15 minutos para cotações)
CACHE_TTL_SECONDS = 900
