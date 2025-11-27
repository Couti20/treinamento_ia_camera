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
CONF_THRESHOLD = 0.4

# Definir EPIs obrigatórios por setor/cargo (mapeamento)
# Exemplo: {"obra": ["helmet", "gloves", "vest"], "escritório": ["glasses"]}
REQUIRED_PPE_BY_SECTOR = {
    "default": ["helmet", "hardhat", "gloves", "glove", "vest", "goggles", "glasses"],
    "construção": ["helmet", "hardhat", "gloves", "glove", "vest"],
    "química": ["helmet", "gloves", "goggles", "vest"],
    "limpeza": ["gloves", "glasses"],
}

# PPE padrão (usado se nenhum setor for especificado)
DEFAULT_REQUIRED_PPE = REQUIRED_PPE_BY_SECTOR["default"]

# Mapeamento de classes do modelo para tipos de EPI (customize conforme seu modelo)
EPI_CLASS_MAPPING = {
    "helmet": "capacete",
    "hardhat": "capacete",
    "gloves": "luvas",
    "glove": "luvas",
    "goggles": "óculos",
    "glasses": "óculos",
    "vest": "colete/avental",
    "safety_vest": "colete/avental",
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
