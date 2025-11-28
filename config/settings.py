"""
Configuração centralizada do projeto EPI Detector.
"""
import os
from pathlib import Path

# Diretórios
BASE_DIR = Path(__file__).parent.parent
LOGS_DIR = BASE_DIR / "logs"
MODELS_DIR = BASE_DIR / "models"
CONFIG_DIR = BASE_DIR / "config"

# Criar diretórios se não existirem
LOGS_DIR.mkdir(exist_ok=True)
MODELS_DIR.mkdir(exist_ok=True)

# Fonte de vídeo (0 = webcam padrão, ou caminho de arquivo)
VIDEO_SOURCE = 0

# Confiança mínima para detecções
CONF_THRESHOLD = 0.3  # Reduzido para 0.3 (mais sensível)

# Definir EPIs obrigatórios por setor/cargo (usando classes COCO)
# NOTA: Modelo COCO atual NÃO detecta EPIs específicos (helmet, gloves, etc)
# Para fase de TESTES: apenas detectar pessoas. Preparado para EPIs customizados depois.
REQUIRED_PPE_BY_SECTOR = {
    "default": ["person"],  # Apenas detectar pessoas por enquanto
    "construção": ["person"],  # TODO: Retreinar com dataset de EPIs
    "química": ["person"],
    "limpeza": ["person"],
}

# PPE padrão (usado se nenhum setor for especificado)
# COCO classes disponíveis para detecção: backpack, handbag, tie, suitcase, etc
# Se vazio, apenas detecta pessoas
DEFAULT_REQUIRED_PPE = []  # Vazio por enquanto - apenas detecta pessoas

# Mapeamento de classes do modelo COCO para tipos de EPI
# Usando modelo COCO padrão: adaptar classes existentes para EPIs
EPI_CLASS_MAPPING = {
    "person": "pessoa",
    "backpack": "mochila/equipamento",
    "handbag": "bolsa",
    "tie": "uniforme",
    "baseball_glove": "luvas",
    # TODO: Adicione mapeamentos de EPIs customizados quando modelo for retreinado
}

# Limiar de overlap para associação EPI↔pessoa (0.0-1.0)
OVERLAP_THRESHOLD = 0.08

# Limiar de distância centroid (pixels) para associação alternativa
CENTROID_DISTANCE_THRESHOLD = 150

# Salvar vídeo anotado (True/False)
SAVE_ANNOTATED_VIDEO = False
OUTPUT_VIDEO_PATH = LOGS_DIR / "annotated_output.mp4"

# Logging CSV
CSV_LOG_PATH = LOGS_DIR / "ppe_audit.csv"

# Banco de dados (opcional)
# USE_DATABASE = True
# DATABASE_URL = "sqlite:///logs/ppe_detector.db"

# API REST
API_HOST = "0.0.0.0"
API_PORT = 8000

# Email para alertas críticos (opcional)
ALERT_EMAIL_ENABLED = False
ALERT_EMAIL_TO = "supervisor@empresa.com"
ALERT_EMAIL_FROM = "ppe-detector@empresa.com"

# Webhook para alertas (integração com Spring Boot)
WEBHOOK_URL = "http://localhost:8080/api/alerts/ppe"
WEBHOOK_ENABLED = False

# Cores BGR (OpenCV usa BGR, não RGB)
COLOR_OK = (0, 255, 0)  # Verde
COLOR_WARNING = (0, 165, 255)  # Laranja
COLOR_ALERT = (0, 0, 255)  # Vermelho
COLOR_NEUTRAL = (128, 128, 128)  # Cinza (neutro)

# Texto e desenho
FONT = "FONT_HERSHEY_SIMPLEX"
FONT_SCALE = 0.6
FONT_THICKNESS = 2

print(f"[CONFIG] Configuração carregada. Diretório base: {BASE_DIR}")
