# EPI Detector - Monitoramento Profissional de Equipamentos de Proteção

Sistema inteligente de detecção e monitoramento de Equipamentos de Proteção Individual (EPIs) em tempo real usando YOLO v8 e OpenCV.

## 🎯 Recursos

- ✅ **Detecção de EPIs**: Capacetes, luvas, óculos, coletes
- ✅ **Alertas em Tempo Real**: Código de cores (Verde = OK, Laranja = Aviso, Vermelho = Crítico)
- ✅ **Logging Estruturado**: Auditoria completa em CSV com timestamp e detalhes
- ✅ **Análise Estatística**: Taxa de conformidade, número de violações
- ✅ **Estrutura Modular**: Código profissional e facilmente extensível
- ✅ **Suporte Multi-Setor**: Diferentes requisitos de EPI por área/cargo

## 📁 Estrutura do Projeto

```
camera-pyton/
├── config/
│   └── settings.py          # Configuração centralizada
├── utils/
│   ├── detector.py          # Lógica de detecção YOLO
│   └── validator.py         # Validação e alertas de EPIs
├── logger/
│   └── audit.py             # Logging em CSV/JSON
├── alerts/                  # Módulo de alertas (future)
├── logs/                    # Pasta de saída (criada automaticamente)
│   └── ppe_audit.csv        # Log de detecções
├── main.py                  # Script principal
├── requirements.txt         # Dependências
└── README.md               # Este arquivo
```

## 🚀 Instalação

### Pré-requisitos
- Python 3.8+
- pip
- Webcam ou arquivo de vídeo

### Passos

1. **Clonar/Baixar o projeto**
```bash
cd camera-pyton
```

2. **Criar ambiente virtual (recomendado)**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate
```

3. **Instalar dependências**
```bash
pip install -r requirements.txt
```

## ⚙️ Configuração

Edite `config/settings.py` para customizar:

```python
# Fonte de vídeo
VIDEO_SOURCE = 0  # 0 = webcam, ou caminho do arquivo

# Confiança mínima para detecções
CONF_THRESHOLD = 0.4

# EPIs obrigatórios
DEFAULT_REQUIRED_PPE = ["helmet", "gloves", "vest", "goggles"]

# Thresholds de associação
OVERLAP_THRESHOLD = 0.08        # Overlap de caixa
CENTROID_DISTANCE_THRESHOLD = 150  # Distância entre centroides (pixels)
```

## ▶️ Rodar

```bash
python main.py
```

**Controle**:
- Pressione `Q` para sair
- Monitore a janela de vídeo para alertas em tempo real

## 📊 Saída

### Arquivo CSV (`logs/ppe_audit.csv`)
```csv
timestamp,frame,pessoa_id,bbox,missing_ppe,person_conf,severity
2025-11-26T14:30:00.123,125,1,"100,50,250,400","helmet;gloves",0.95,critical
2025-11-26T14:30:01.456,126,2,"300,60,450,410","",0.88,info
```

### Console
```
[INFO] Sistema inicializado. EPIs obrigatórios: ['helmet', 'hardhat', 'gloves', 'vest']
[INFO] Iniciando detecção. Pressione 'Q' para sair.
...
[INFO] Monitoramento encerrado.
[INFO] Estatísticas: {'total_detections': 500, 'violations': 45, 'compliance_rate': 91.0}
```

## 🔌 Integração com Spring Boot

### API REST (Future)

Será exposta em `http://localhost:8000/api/`:

```bash
# Status da detecção
GET /api/detection/status

# Iniciar detecção
POST /api/detection/start

# Parar detecção
POST /api/detection/stop

# Obter logs
GET /api/detection/logs

# Configuração
GET /api/config
```

### Webhook para Alertas Críticos

Configure em `settings.py`:
```python
WEBHOOK_ENABLED = True
WEBHOOK_URL = "http://localhost:8080/api/alerts/ppe"
```

O sistema enviará POST JSON quando detectar violações críticas.

## 🎨 Cores e Status

- **Verde (0,255,0)**: OK - Todos os EPIs presentes
- **Laranja (0,165,255)**: Aviso - Alguns EPIs faltando
- **Vermelho (0,0,255)**: Crítico - Maioria dos EPIs faltando

## 📈 Estatísticas Disponíveis

```json
{
  "total_detections": 500,
  "violations": 45,
  "critical_alerts": 12,
  "warning_alerts": 33,
  "compliance_rate": 91.0
}
```

## 🔧 Personalização

### Adicionar Novos EPIs

1. Treinar modelo YOLO com novas classes
2. Atualizar `config/settings.py`:

```python
EPI_CLASS_MAPPING = {
    "helmet": "capacete",
    "gloves": "luvas",
    "NEW_EPI": "novo_equipamento",  # Adicionar aqui
}

DEFAULT_REQUIRED_PPE = [..., "NEW_EPI"]
```

### Criar Perfil por Setor

```python
REQUIRED_PPE_BY_SECTOR = {
    "construção": ["helmet", "gloves", "vest"],
    "químico": ["helmet", "gloves", "goggles", "vest"],
    "escritório": ["glasses"],
}
```

## 🐛 Troubleshooting

| Erro | Solução |
|------|---------|
| `ModuleNotFoundError: No module named 'cv2'` | `pip install opencv-python` |
| `ModuleNotFoundError: No module named 'ultralytics'` | `pip install ultralytics` |
| Janela não abre | Verifique se webcam está disponível / use VIDEO_SOURCE = "video.mp4" |
| Detecções ruins | Aumentar `CONF_THRESHOLD` ou usar modelo treinado customizado |

## 📝 Logs

Todos os logs são salvos em `logs/ppe_audit.csv` com:
- Timestamp
- Frame number
- ID da pessoa
- Bounding box
- EPIs faltando
- Confiança
- Severidade

Para exportar em JSON:
```python
from logger.audit import AuditLogger
logger = AuditLogger("logs/ppe_audit.csv")
logger.export_json("logs/ppe_audit.json")
```

## 🤝 Integração com Sistemas Existentes

### Com Spring Boot

```java
// Cliente HTTP para chamar API Python
@RestController
@RequestMapping("/api/epi")
public class EPIController {
    
    @GetMapping("/status")
    public ResponseEntity<?> getStatus() {
        // Chamar http://localhost:8000/api/detection/status
        RestTemplate template = new RestTemplate();
        return template.getForEntity("http://localhost:8000/api/detection/status", Object.class);
    }
}
```

### Com Frontend

```javascript
// Buscar status
fetch('http://localhost:8000/api/detection/status')
    .then(r => r.json())
    .then(data => {
        document.getElementById('status').textContent = 
            data.running ? 'Ativo' : 'Inativo';
    });
```

## 📄 Licença

Projeto interno - Confisafe

## 👨‍💼 Suporte

Para dúvidas ou problemas, abra uma issue ou contacte o time de desenvolvimento.
