# Rodar Modelo YOLOv11 do Roboflow com Webcam (Python 3.13 Compatible)

## Quick Start - 3 passos

### 1. Unica dependencia necessaria
```bash
pip install opencv-python
```

(NumPy ja vem com OpenCV)

### 2. Configurar seu script

Abrir `run_roboflow_model.py` e mudar:

```python
API_KEY = "SUA_CHAVE_AQUI"      # De https://app.roboflow.com/settings/account
MODEL_ID = "seu_projeto/1"      # De https://app.roboflow.com/projects
```

### 3. Rodar
```bash
python run_roboflow_model.py
```

---

## Como Pegar API_KEY

1. Ir para: https://app.roboflow.com/settings/account
2. Copiar "Private API Key"
3. Colar em: `API_KEY = "..."`

Exemplo:
```python
API_KEY = "abc123def456ghi789"
```

---

## Como Pegar MODEL_ID

1. Ir para: https://app.roboflow.com/projects
2. Clicar no seu projeto de EPIs
3. Ir para "Deploy" ou "Model Info"
4. Ver algo como: `safety-equipment-detection/1`
5. Copiar e colar

Exemplo:
```python
MODEL_ID = "safety-equipment-detection/1"
```

---

## O que Vai Aparecer

Webcam com deteccoes em CORES:

- GREEN = EPIs OK (helmet, glove, vest, goggles)
- RED = FALTA EPI (no-helmet, no-glove, no-vest, no-goggles)

Tambem mostra:
- Total de deteccoes
- Quantos "PERIGOS" (sem EPI)
- Lista de cada classe encontrada

---

## Controles

| Tecla | Acao |
|-------|------|
| Q | Sair |
| S | Salvar frame |

---

## Personalizacoes

### Detectar TODO frame (mais preciso)
```python
detector.run(skip_frames=1)
```

### Otimizar CPU (detectar menos vezes)
```python
detector.run(skip_frames=3)  # Detecta a cada 3 frames
```

### Usar outra camera
```python
detector.run(camera_id=1)  # 0 = padrao, 1 = segunda, etc
```

### Mudar threshold
```python
CONFIDENCE = 0.7  # Padrao: 0.5 (0-1)
```

---

## Troubleshooting

### "Camera nao encontrada"
```python
camera_id=1  # Tentar 0, 1, 2...
```

### "Chave API invalida"
- Ir para: https://app.roboflow.com/settings/account
- Regenerar chave

### "Model nao encontrado"
- Verificar em: https://app.roboflow.com/projects
- Copiar nome exato

### "Conexao falhou"
- Verificar internet
- Servers Roboflow podem estar down

---

## Configuracao Recomendada

```python
API_KEY = "sua_chave"
MODEL_ID = "safety-equipment-detection/1"
CONFIDENCE = 0.5
SKIP_FRAMES = 2  # Bom balance CPU vs Precisao

detector = EPIDetector(API_KEY, MODEL_ID, CONFIDENCE)
detector.run(skip_frames=SKIP_FRAMES)
```

---

## Performance

| Sistema | FPS | Latencia |
|---------|-----|----------|
| CPU (notebook) | 5-10 | 100-200ms |
| GPU | 30+ | 30-50ms |

---

PRONTO! Detector funcionando com Python 3.13! [OK]
