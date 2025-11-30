#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para baixar dataset de EPIs do Roboflow

Dataset recomendados:
- Hard Hat Workers Safety Dataset
- COCO Safety Equipment Detection
- Helmet Detection
- PPE Detection
"""

import os
import sys
from pathlib import Path

def download_roboflow_dataset():
    """Baixar dataset do Roboflow"""
    
    print("="*70)
    print("📥 DOWNLOAD DE DATASET - ROBOFLOW")
    print("="*70)
    print()
    
    print("Para baixar um dataset de EPIs do Roboflow:")
    print()
    print("1️⃣  Ir para: https://roboflow.com/search?q=helmet")
    print("2️⃣  Escolher um dataset (ex: 'Hard Hat Workers')")
    print("3️⃣  Clicar em 'Download Dataset'")
    print("4️⃣  Selecionar formato: 'YOLOv8'")
    print("5️⃣  Copiar código Python que aparece")
    print("6️⃣  Executar código no terminal:")
    print()
    print("   Exemplo de código Roboflow:")
    print("   ┌─────────────────────────────────────────────────────┐")
    print("   │ from roboflow import Roboflow                        │")
    print("   │ rf = Roboflow(api_key=\"sua_chave_api\")             │")
    print("   │ project = rf.workspace().project(\"hard-hats\")      │")
    print("   │ dataset = project.version(1).download(\"yolov8\")    │")
    print("   └─────────────────────────────────────────────────────┘")
    print()
    
    print("Datasets recomendados:")
    print()
    print("🟢 Hard Hat Workers Safety Dataset")
    print("   • Capacetes e trabalhadores")
    print("   • Qualidade alta")
    print("   URL: https://roboflow.com/search?q=hard+hat+workers")
    print()
    
    print("🟢 Safety Equipment Detection")
    print("   • Capacetes, luvas, coletes, óculos")
    print("   • Múltiplas classes")
    print("   URL: https://roboflow.com/search?q=safety+equipment")
    print()
    
    print("🟢 PPE Detection")
    print("   • Equipamentos de proteção variados")
    print("   • Grande dataset")
    print("   URL: https://roboflow.com/search?q=ppe+detection")
    print()
    
    print("="*70)
    print()
    print("Após baixar, extraia em: datasets/epi_dataset/")
    print("Estrutura esperada:")
    print("""
    datasets/epi_dataset/
    ├── data.yaml           (arquivo de configuração)
    ├── images/
    │   ├── train/
    │   ├── val/
    │   └── test/
    └── labels/
        ├── train/
        ├── val/
        └── test/
    """)
    print()


def setup_directories():
    """Criar diretórios necessários"""
    
    dirs = [
        "datasets/epi_dataset",
        "models",
        "runs/train",
    ]
    
    for d in dirs:
        Path(d).mkdir(parents=True, exist_ok=True)
        print(f"✓ Diretório pronto: {d}")


def create_data_yaml_template():
    """Criar template de data.yaml para usuários que querem criar manualmente"""
    
    template = """# YOLOv8 dataset configuration

path: datasets/epi_dataset  # dataset root
train: images/train
val: images/val
test: images/test

# number of classes
nc: 3

# class names
names:
  0: helmet
  1: goggles
  2: gloves
"""
    
    output_file = Path("datasets/epi_dataset_template/data.yaml")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, "w") as f:
        f.write(template)
    
    print(f"✓ Template data.yaml criado em: {output_file}")


if __name__ == "__main__":
    try:
        setup_directories()
        print()
        download_roboflow_dataset()
        create_data_yaml_template()
        
        print("\n" + "="*70)
        print("✅ PRÓXIMAS AÇÕES:")
        print("="*70)
        print()
        print("1. Acesse https://roboflow.com/search?q=helmet")
        print("2. Escolha um dataset de capacetes/EPIs")
        print("3. Faça download em formato YOLOv8")
        print("4. Extraia em: datasets/epi_dataset/")
        print("5. Execute: python train_epi_model.py")
        print()
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        sys.exit(1)
