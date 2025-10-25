from pathlib import Path

BASE_DIR = Path("/home/ubuntu/proyecto")
INPUT_DIR = BASE_DIR
PROCESADOS_DIR = INPUT_DIR / "procesados"

CACHE_JSON = BASE_DIR / "cache_datos.json"
OUTPUT_HTML = BASE_DIR / "index.html"
GIT_REPO = BASE_DIR

BASE_DIR.mkdir(parents=True, exist_ok=True)
PROCESADOS_DIR.mkdir(parents=True, exist_ok=True)

EDAD = 61
ALTURA_CM = 177
FC_REPOSO = 55
FC_MAX = 220 - EDAD
PESO_OBJETIVO = 79.0

PAI_OBJETIVO_SEMANAL = 100
PAI_VENTANA_DIAS = 7
VO2MAX_EXCELENTE = 35
VO2MAX_BUENO = 30
TSB_CTL_DIAS = 42
TSB_ATL_DIAS = 7
TSB_OPTIMO_MIN = -10
TSB_OPTIMO_MAX = 10
SUENO_OBJETIVO_HORAS = 7
SUENO_MINIMO_HORAS = 6

ZONAS_FC = {
    "recuperacion": (0.00, 0.60),
    "aerobico": (0.60, 0.70),
    "tempo": (0.70, 0.80),
    "umbral": (0.80, 0.90),
    "vo2max": (0.90, 1.00)
}

ARCHIVO_PREFIX = "health_data"
ARCHIVO_EXTENSION = ".json"
LIMPIEZA_AGRESIVA_FULL = True
LIMPIEZA_DIFF = False

GRAFICOS_DIAS_HISTORICO = 30
COLOR_EXCELENTE = "#3fb950"
COLOR_BUENO = "#d29922"
COLOR_MALO = "#f85149"
COLOR_PRIMARIO = "#58a6ff"
COLOR_FONDO = "#0d1117"

INTERVALO_MINUTOS = 30
GITHUB_REPO_URL = "https://lw2die.github.io/health-dashboard/"
GITHUB_BRANCH = "main"

LOG_LEVEL = "INFO"
LOG_FORMAT = '%(asctime)s [%(levelname)s] - %(message)s'
