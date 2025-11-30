# 🎬 Rodar Modelo YOLOv11 do Roboflow com Webcam

## ⚡ Quick Start (3 passos)

### 1️⃣ Instalar dependências
```bash
pip install inference-sdk supervision opencv-python
```

### 2️⃣ Pegar sua chave API Roboflow
- Ir para: https://app.roboflow.com/settings/account
- Copiar **"Private API Key"**

### 3️⃣ Configurar script
Abrir `run_roboflow_model.py` e substituir:

```python
API_KEY = "sua_chave_api_aqui"        # Colar chave copiada
MODEL_ID = "seu_projeto_aqui/1"       # Ver abaixo como pegar
```

### 4️⃣ Rodar
```bash
python run_roboflow_model.py
```

Pronto! 🚀 Webcam vai mostrar detecções com cores:
- 🟢 **VERDE** = EPIs OK (helmet, glove, vest, goggles)
- 🔴 **VERMELHO** = FALTA EPI (no-helmet, no-glove, no-vest, no-goggles)

---

## 🔑 Como Pegar seu MODEL_ID

1. Ir para: https://app.roboflow.com/projects
2. Clicar no seu projeto
3. Clicar em **"Deployments"** ou **"API Reference"**
4. Ver algo como: `"safety-equipment-detection/1"`
5. Copiar este valor

**Exemplo:**
- Se seu projeto é "safety-equipment-detection" versão 1
- MODEL_ID = `"safety-equipment-detection/1"`

---

## 🎮 Controles

| Tecla | Ação |
|-------|------|
| **Q** | Sair |
| **S** | Salvar frame atual |

---

## 📊 O que o script faz

✅ **Otimizado para CPU:**
- Redimensiona frame 50% (mais rápido)
- Pula frames (skip_frames=2)
- Mostra detecção em tempo real

✅ **Cores inteligentes:**
- VERMELHO = Perigo (sem EPI)
- VERDE = Segurança (com EPI)

✅ **Estatísticas:**
- Mostra total de detecções
- Mostra quantos "PERIGOS"
- Lista cada classe detectada

---

## ⚙️ Personalizações

### Mudar câmera
```python
detector.run(camera_id=0)  # 0 = webcam padrão, 1 = segunda câmera, etc
```

### Aumentar velocidade (pular mais frames)
```python
detector.run(skip_frames=3)  # Pula 3 frames entre detecções
```

### Mudar threshold de confiança
```python
detector = EPIDetector(
    api_key=API_KEY,
    model_id=MODEL_ID,
    confidence=0.7  # Mais rigoroso (0-1)
)
```

### Adicionar mais classes de "perigo"
```python
DANGER_CLASSES = {'no-helmet', 'no-glove', 'no-vest', 'no-goggles', 'sua-classe-aqui'}
```

---

## 🐛 Troubleshooting

### ❌ "ModuleNotFoundError: No module named 'inference'"
```bash
pip install inference-sdk
```

### ❌ "Câmera não encontrada"
- Verificar se câmera está conectada
- Tentar: `camera_id=1` ou `camera_id=2`

### ❌ "API key inválida"
- Ir para https://app.roboflow.com/settings/account
- Regenerar chave
- Copiar novamente

### ❌ "Model not found"
- Verificar MODEL_ID está correto
- Ir para https://app.roboflow.com/projects
- Confirmar nome exato

### ❌ "Muito lento na CPU"
```python
skip_frames=5  # Aumentar número
```

---

## 📈 Performance esperada

| Hardware | FPS | Latência |
|----------|-----|----------|
| CPU (notebook) | 5-10 FPS | 100-200ms |
| GPU | 30+ FPS | 30-50ms |

**Dica:** Aumentar `skip_frames` melhora FPS (menos detecções por segundo)

---

## 🎯 Exemplo completo configurado

```python
# Seu ambiente específico
API_KEY = "abcd1234efgh5678ijkl9012mnop3456"
MODEL_ID = "safety-equipment-detection/2"
CONFIDENCE = 0.6
SKIP_FRAMES = 2

detector = EPIDetector(API_KEY, MODEL_ID, CONFIDENCE)
detector.run(skip_frames=SKIP_FRAMES)
```

Pronto para usar! ✅
