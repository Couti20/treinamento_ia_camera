#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para treinar modelo customizado de EPIs (capacete, óculos, etc)
Usando YOLOv8 com dataset do Roboflow

Passos:
1. Ir para https://roboflow.com
2. Procurar por "safety equipment detection" ou "helmet goggles dataset"
3. Fazer download em formato YOLOv8
4. Extrair em datasets/epi_dataset/
5. Executar este script
"""

import os
import sys
from pathlib import Path
from ultralytics import YOLO

# Configurações
DATASET_PATH = "datasets/epi_dataset"
OUTPUT_DIR = "runs/train"
MODEL_NAME = "epi_custom"
EPOCHS = 50
IMG_SIZE = 640
BATCH_SIZE = 16  # Reduzir para 8 se memória insuficiente

def check_dataset():
    """Verificar se dataset está disponível"""
    dataset_path = Path(DATASET_PATH)
    data_yaml = dataset_path / "data.yaml"
    
    if not data_yaml.exists():
        print("❌ Erro: Dataset não encontrado!")
        print(f"\nPor favor, siga estes passos:")
        print("\n1. Ir para: https://roboflow.com")
        print("2. Procurar dataset com: 'helmet detection', 'safety equipment', etc")
        print("3. Fazer download em formato YOLOv8")
        print(f"4. Extrair em: {DATASET_PATH}/")
        print("5. Executar este script novamente")
        print("\nExemplos de datasets:")
        print("- https://universe.roboflow.com/search?q=helmet+detection")
        print("- https://universe.roboflow.com/search?q=safety+equipment")
        print("- https://universe.roboflow.com/search?q=ppe+detection")
        return False
    
    print(f"✓ Dataset encontrado: {data_yaml}")
    return True


def train_model():
    """Treinar modelo customizado"""
    print("\n" + "="*60)
    print("🚀 TREINAMENTO DO MODELO CUSTOMIZADO DE EPIs")
    print("="*60 + "\n")
    
    if not check_dataset():
        sys.exit(1)
    
    # Criar modelo baseado em yolov8n
    print("📥 Carregando modelo base: YOLOv8 Nano...")
    model = YOLO("yolov8n.pt")
    
    print(f"\n📊 Configurações de treino:")
    print(f"  Dataset: {DATASET_PATH}")
    print(f"  Épocas: {EPOCHS}")
    print(f"  Tamanho imagem: {IMG_SIZE}")
    print(f"  Batch size: {BATCH_SIZE}")
    print(f"  Output: {OUTPUT_DIR}")
    
    print(f"\n🔄 Iniciando treino...")
    print("   (Isso pode levar 30min-2h dependendo do hardware)\n")
    
    # Treinar
    results = model.train(
        data=f"{DATASET_PATH}/data.yaml",
        epochs=EPOCHS,
        imgsz=IMG_SIZE,
        batch=BATCH_SIZE,
        patience=10,
        save=True,
        device=0 if _has_cuda() else "cpu",  # GPU se disponível
        project=OUTPUT_DIR,
        name=MODEL_NAME,
        pretrained=True,
        optimizer="SGD",
        lr0=0.01,
        lrf=0.01,
        momentum=0.937,
        weight_decay=0.0005,
        warmup_epochs=3,
        close_mosaic=10,
        mosaic=1.0,
    )
    
    print("\n✅ Treino concluído!")
    print(f"📁 Modelo salvo em: {results.save_dir}")
    
    # Copiar modelo para pasta principal
    best_model = Path(results.save_dir) / "weights" / "best.pt"
    if best_model.exists():
        import shutil
        dest = Path("models/epi_custom_best.pt")
        dest.parent.mkdir(exist_ok=True)
        shutil.copy(best_model, dest)
        print(f"📋 Cópia do modelo em: {dest}")
        print(f"\n⚠️  Para usar este modelo, atualize em config/settings.py:")
        print(f"    MODEL_PATH = 'models/epi_custom_best.pt'")


def validate_model():
    """Validar modelo em dados de teste"""
    print("\n" + "="*60)
    print("✓ VALIDANDO MODELO")
    print("="*60 + "\n")
    
    best_model = Path(f"{OUTPUT_DIR}/{MODEL_NAME}/weights/best.pt")
    
    if not best_model.exists():
        print(f"❌ Modelo não encontrado: {best_model}")
        return
    
    model = YOLO(str(best_model))
    metrics = model.val(data=f"{DATASET_PATH}/data.yaml")
    
    print("\n📊 Resultados de Validação:")
    print(f"  mAP50: {metrics.box.map50:.3f}")
    print(f"  mAP50-95: {metrics.box.map:.3f}")
    print(f"  Precisão: {metrics.box.mp:.3f}")
    print(f"  Recall: {metrics.box.mr:.3f}")


def _has_cuda():
    """Verificar se tem GPU CUDA disponível"""
    try:
        import torch
        return torch.cuda.is_available()
    except:
        return False


def test_model():
    """Testar modelo em imagem de exemplo"""
    print("\n" + "="*60)
    print("🧪 TESTANDO MODELO EM IMAGEM DE EXEMPLO")
    print("="*60 + "\n")
    
    best_model = Path(f"{OUTPUT_DIR}/{MODEL_NAME}/weights/best.pt")
    
    if not best_model.exists():
        print(f"❌ Modelo não encontrado: {best_model}")
        return
    
    # Testar em imagem de validação
    test_image = Path(f"{DATASET_PATH}/valid/images")
    if test_image.exists():
        images = list(test_image.glob("*.jpg")) + list(test_image.glob("*.png"))
        if images:
            print(f"📷 Testando em: {images[0].name}")
            model = YOLO(str(best_model))
            results = model.predict(str(images[0]), conf=0.5, save=True)
            print(f"✅ Resultado salvo em: {results[0].save_dir}")


if __name__ == "__main__":
    try:
        # 1. Treinar
        train_model()
        
        # 2. Validar
        if input("\nValidar modelo? (s/n): ").lower() == "s":
            validate_model()
        
        # 3. Testar
        if input("\nTestar em imagem de exemplo? (s/n): ").lower() == "s":
            test_model()
        
        print("\n" + "="*60)
        print("✅ TREINO FINALIZADO COM SUCESSO!")
        print("="*60)
        
    except KeyboardInterrupt:
        print("\n⚠️  Treino interrompido pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro durante treino: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
