#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
GUIA PASSO-A-PASSO: Treinar Modelo Customizado de EPIs
Versão sem caracteres especiais para compatibilidade
"""

print("""
=== GUIA COMPLETO: TREINAR MODELO CUSTOMIZADO DE EPIs ===
(Capacete, Oculos, Luvas - Com Deteccao de Cores)

FASE 1: PREPARACAO (5 minutos)
===============================================

Passo 1: Criar estrutura de diretorios
   $ python setup_dataset.py
   
   Isso vai criar:
   - datasets/epi_dataset/
   - models/
   - runs/train/

Passo 2: Verificar ambiente
   $ python -c "from ultralytics import YOLO; print('OK')"


FASE 2: COLETAR DATASET (15-60 minutos)
===============================================

OPCAO A: Usar Roboflow (RECOMENDADO)
   
   1. Ir para: https://roboflow.com/search?q=helmet
   2. Escolher dataset (ex: "Hard Hat Workers Safety")
   3. Download em formato YOLOv8
   4. Executar codigo Python fornecido:
      
      from roboflow import Roboflow
      rf = Roboflow(api_key="sua_chave")
      project = rf.workspace().project("hard-hats")
      dataset = project.version(1).download("yolov8")
   
   5. Mover dataset para: datasets/epi_dataset/
   
      Estrutura esperada:
      datasets/epi_dataset/
      - images/train/
      - images/val/
      - images/test/
      - labels/train/
      - labels/val/
      - labels/test/
      - data.yaml

OPCAO B: Coletar imagens manuais (Mais tempo)
   
   1. Tirar ~1000 fotos:
      - Com capacete
      - Sem capacete
      - Com oculos
      - Sem oculos
      - Com luvas
      - Sem luvas
   
   2. Anotar com Label Studio (https://labelstud.io)
   3. Exportar em formato YOLOv8


FASE 3: VALIDAR DATASET (2 minutos)
===============================================

Verificar estrutura:
   $ ls -la datasets/epi_dataset/

Deve ter:
   - data.yaml
   - images/train/ (com .jpg/.png)
   - labels/train/ (com .txt)


FASE 4: TREINAR MODELO (30min-2h)
===============================================

Iniciar treino:
   $ python train_epi_model.py
   
   Vai:
   - Validar dataset
   - Carregar YOLOv8 Nano
   - Treinar por 50 epocas
   - Usar GPU se disponivel, senao CPU
   - Salvar em: runs/train/epi_custom/


FASE 5: TESTAR MODELO (5 minutos)
===============================================

Modelo vai ficar em:
   $ ls -la models/epi_custom_best.pt

Testar com camara:
   $ python main_epi.py
   
   Cores:
   - Verde: OK (todos os EPIs presentes)
   - Laranja: Aviso (alguns EPIs faltando)
   - Vermelho: Critico (maioria faltando)


FASE 6: USAR EM PRODUCAO
===============================================

Configurar EPIs obrigatorios:
   Editar: config/settings.py
   
   DEFAULT_REQUIRED_PPE = ["helmet", "goggles"]

Executar:
   $ python main_epi.py

Ver logs:
   $ head -50 logs/ppe_audit.csv


=== PERFORMANCE ESPERADA ===

COM GPU (NVIDIA RTX):
   - mAP50: ~80-85%
   - FPS: 10-15
   - Frame time: 65-100ms

COM CPU (Notebook):
   - mAP50: ~75-80%
   - FPS: 1-2
   - Frame time: 500-1000ms


=== TROUBLESHOOTING ===

Dataset nao encontrado?
   -> Verificar data.yaml em datasets/epi_dataset/

CUDA Memory Error?
   -> Reduzir batch_size em train_epi_model.py

Model nao detecta EPIs?
   -> Verificar se best.pt tem 3 classes


=== PROXIMOS PASSOS ===

1. python setup_dataset.py
2. Download dataset do Roboflow
3. python train_epi_model.py
4. python main_epi.py


""")
