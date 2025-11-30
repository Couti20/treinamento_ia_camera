#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
GUIA PASSO-A-PASSO: Treinar Modelo Customizado de EPIs
"""

GUIA = """
╔═══════════════════════════════════════════════════════════════════════╗
║                                                                       ║
║  🎯 GUIA COMPLETO: TREINAR MODELO CUSTOMIZADO DE EPIs                ║
║     (Capacete, Óculos, Luvas - Com Detecção de Cores)               ║
║                                                                       ║
╚═══════════════════════════════════════════════════════════════════════╝

FASE 1: PREPARAÇÃO (5 minutos)
═══════════════════════════════════════════════════════════════════════

Passo 1: Criar estrutura de diretórios
   $ python setup_dataset.py
   
   Isso vai criar:
   ├── datasets/epi_dataset/
   ├── models/
   └── runs/train/

Passo 2: Verificar ambiente
   $ python -c "from ultralytics import YOLO; print('✓ YOLO OK')"
   $ python -c "import torch; print(f'✓ PyTorch OK. CUDA: {torch.cuda.is_available()}')"


FASE 2: COLETAR DATASET (15-60 minutos)
═══════════════════════════════════════════════════════════════════════

OPÇÃO A: Usar Roboflow (RECOMENDADO - Mais rápido)
   
   Passo 1: Ir para https://roboflow.com/search?q=helmet
   
   Passo 2: Escolher um dataset com bom score (ex: "Hard Hat Workers Safety")
   
   Passo 3: Fazer download
      • Clicar em "Download Dataset"
      • Selecionar "YOLOv8" format
      • Clicar em "Show Download Code"
   
   Passo 4: Executar código Python fornecido (ex):
      from roboflow import Roboflow
      rf = Roboflow(api_key="sua_chave")
      project = rf.workspace().project("hard-hats")
      dataset = project.version(1).download("yolov8")
   
   Passo 5: Mover dataset para pasta correta
      • Dataset vai baixar em uma pasta temporária
      • Mover para: datasets/epi_dataset/
      • Estrutura deve ser:
        datasets/epi_dataset/
        ├── images/
        │   ├── train/
        │   ├── val/
        │   └── test/
        ├── labels/
        │   ├── train/
        │   ├── val/
        │   └── test/
        └── data.yaml

OPÇÃO B: Coletar imagens manuais (Mais tempo)
   
   Passo 1: Tirar ~1000 fotos:
      • Com capacete
      • Sem capacete
      • Com óculos
      • Sem óculos
      • Com luvas
      • Sem luvas
      • Variações de ângulo/luz
   
   Passo 2: Anotar com Label Studio (https://labelstud.io)
      • Fazer download e instalar
      • Criar projeto YOLO
      • Anotar manualmente
      • Exportar em formato YOLOv8
   
   Passo 3: Organizar em datasets/epi_dataset/


FASE 3: VALIDAR DATASET (2 minutos)
═══════════════════════════════════════════════════════════════════════

Passo 1: Verificar estrutura
   $ ls -la datasets/epi_dataset/
   
   Deve ter:
   • data.yaml
   • images/train/ (com imagens .jpg/.png)
   • labels/train/ (com anotações .txt)

Passo 2: Verificar conteúdo data.yaml
   $ cat datasets/epi_dataset/data.yaml
   
   Deve parecer com:
   ┌──────────────────────────────────────┐
   │ path: datasets/epi_dataset           │
   │ train: images/train                  │
   │ val: images/val                      │
   │ test: images/test                    │
   │                                      │
   │ nc: 3                                │
   │ names:                               │
   │   0: helmet                          │
   │   1: goggles                         │
   │   2: gloves                          │
   └──────────────────────────────────────┘


FASE 4: TREINAR MODELO (30min-2h)
═══════════════════════════════════════════════════════════════════════

Passo 1: Iniciar treino
   $ python train_epi_model.py
   
   Isso vai:
   • Validar dataset
   • Carregar YOLOv8 Nano (base)
   • Treinar por 50 épocas
   • Usar GPU se disponível, senão CPU
   • Salvar modelo em runs/train/epi_custom/

Passo 2: Acompanhar progresso
   • Vai mostrar logs de treinamento
   • Vai salvar checkpoints automaticamente
   • Pode levar 30min (GPU) a 2h (CPU)

Passo 3: Validar modelo (Opcional)
   • Responder "s" para validar ao término
   • Vai mostrar mAP50, Precisão, Recall


FASE 5: TESTAR MODELO (5 minutos)
═══════════════════════════════════════════════════════════════════════

Passo 1: Encontrar modelo treinado
   $ ls -la runs/train/epi_custom/weights/
   
   Deve ter:
   • best.pt (melhor modelo)
   • last.pt (último checkpoint)

Passo 2: Copiar para pasta de modelos (automático pelo script)
   $ ls -la models/epi_custom_best.pt

Passo 3: Testar com câmera
   $ python main_epi.py
   
   Sistema vai:
   • Detectar novo modelo em models/epi_custom_best.pt
   • Usar automaticamente para detecção
   • Mostrar capacete/óculos em tempo real
   • Cores: Verde (OK) / Laranja (Falta alguns) / Vermelho (Crítico)


FASE 6: USAR EM PRODUÇÃO (Contínuo)
═══════════════════════════════════════════════════════════════════════

Passo 1: Configurar EPIs obrigatórios
   Editar: config/settings.py
   
   Alterar:
   DEFAULT_REQUIRED_PPE = ["helmet", "goggles"]
   
   Ou por setor:
   REQUIRED_PPE_BY_SECTOR = {
       "default": ["helmet", "goggles"],
       "construção": ["helmet", "goggles", "gloves"],
   }

Passo 2: Executar sistema
   $ python main_epi.py
   
   Cores:
   • 🟢 Verde: Todos os EPIs presentes (OK)
   • 🟠 Laranja: Alguns EPIs faltando (Aviso)
   • 🔴 Vermelho: Maioria dos EPIs faltando (Crítico)

Passo 3: Visualizar logs
   $ head -50 logs/ppe_audit.csv
   
   Salva timestamp, pessoa_id, EPIs faltantes, severity


═══════════════════════════════════════════════════════════════════════

📊 PERFORMANCE ESPERADA
═══════════════════════════════════════════════════════════════════════

Após treino com YOLOv8 Nano + ~1000 imagens:

GPU (NVIDIA RTX):
   • mAP50: ~80-85%
   • FPS: 10-15 fps
   • Frame time: 65-100ms

CPU (Notebook):
   • mAP50: ~75-80% (mesma acurácia)
   • FPS: 1-2 fps (mais lento)
   • Frame time: 500-1000ms

Acurácia vs Performance:
   • YOLOv8 Nano: Rápido, bom para CPU (recomendado)
   • YOLOv8 Small: Melhor acurácia, precisa mais power
   • YOLOv8 Medium: Máxima acurácia, precisa GPU


═══════════════════════════════════════════════════════════════════════

🐛 TROUBLESHOOTING
═══════════════════════════════════════════════════════════════════════

Problema: Dataset não encontrado
Solução: Verificar se data.yaml existe em datasets/epi_dataset/
         Roboflow baixa em pasta temporária, mover manualmente

Problema: CUDA Memory Error
Solução: Reduzir batch_size em train_epi_model.py (de 16 para 8)
         Ou usar CPU (device="cpu")

Problema: Model não detecta EPIs customizados
Solução: Verificar se best.pt tem 3 classes (helmet, goggles, gloves)
         python -c "from ultralytics import YOLO; m = YOLO('models/epi_custom_best.pt'); print(m.names)"

Problema: FPS muito lento
Solução: Normal em CPU. Use GPU ou modelo menor
         Ou reduzir tamanho de frame em detector_epi.py (scale_factor = 0.25)

Problema: Falsos positivos (detecta capacete em tudo)
Solução: Aumentar CONF_THRESHOLD em config/settings.py (de 0.3 para 0.5)
         Coletar mais imagens negativas no dataset


═══════════════════════════════════════════════════════════════════════

✨ PRÓXIMAS ETAPAS
═══════════════════════════════════════════════════════════════════════

1. ✅ Treinar modelo
2. ✅ Testar com câmera
3. 📊 Coletar dados de produção (opcional)
4. 🔄 Retreinar periodicamente com novas imagens
5. 🚀 Integrar com Spring Boot (webhook)
6. 📱 Criar dashboard web


═══════════════════════════════════════════════════════════════════════
"""

if __name__ == "__main__":
    print(GUIA)
