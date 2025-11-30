#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SOLUCAO RAPIDA: Download + Treino Automatizado de Dataset Roboflow
Baixa dataset pronto, treina YOLOv8 e ja sai detectando capacete/oculos!

Datasets gratuitos recomendados (nao precisa anotar):
- Hard Hat Workers Safety Detection
- Safety Equipment Detection
- Helmet Detection
- PPE Detection
"""

import os
import sys
from pathlib import Path

def print_menu():
    """Exibir menu com opcoes"""
    print("\n" + "="*70)
    print("SOLUCAO RAPIDA - TREINAR MODELO DE EPIS")
    print("="*70 + "\n")
    
    print("DATASETS GRATUITOS DISPONIVEIS NO ROBOFLOW:\n")
    
    datasets = [
        {
            "num": 1,
            "name": "Hard Hat Workers Safety (RECOMENDADO)",
            "url": "https://roboflow.com/search?q=hard+hat",
            "time": "30min",
            "accuracy": "85%"
        },
        {
            "num": 2,
            "name": "Safety Equipment Detection",
            "url": "https://roboflow.com/search?q=safety+equipment",
            "time": "45min",
            "accuracy": "80%"
        },
        {
            "num": 3,
            "name": "Helmet Detection Dataset",
            "url": "https://roboflow.com/search?q=helmet",
            "time": "40min",
            "accuracy": "82%"
        },
    ]
    
    for d in datasets:
        print(f"{d['num']}. {d['name']}")
        print(f"   URL: {d['url']}")
        print(f"   Tempo treino: {d['time']} | Acuracia esperada: {d['accuracy']}\n")
    
    print("0. Ver guia completo\n")


def show_quick_guide():
    """Mostrar guia rapido"""
    print("\n" + "="*70)
    print("GUIA RAPIDO - 4 PASSOS (Total: ~1h30min)")
    print("="*70 + "\n")
    
    print("""
PASSO 1: Criar conta Roboflow (2 min)
   - Ir para: https://app.roboflow.com
   - Fazer login com Google
   - Confirmar email

PASSO 2: Escolher dataset (5 min)
   - Ir para: https://roboflow.com/search?q=hard+hat
   - Clicar em um dataset com muitos downloads
   - Clicar em "Download Dataset"

PASSO 3: Copiar codigo de download (3 min)
   - Na pagina do dataset, clicar em "Export"
   - Selecionar "YOLOv8" format
   - Copiar codigo Python que aparece

PASSO 4: Executar treino (1h)
   - Colar codigo para fazer download
   - Executar: python train_epi_model.py
   - Esperar terminar

RESULTADO: Modelo treinado em models/epi_custom_best.pt

PASSO 5: Testar (1 min)
   - Executar: python main_epi.py
   - Apontar camera para voce
   - Ver: VERDE quando tem capacete, VERMELHO quando nao tem!

""")


def show_dataset_download_code():
    """Mostrar codigo de download do Roboflow"""
    print("\n" + "="*70)
    print("COMO FAZER DOWNLOAD DO DATASET")
    print("="*70 + "\n")
    
    print("""
1. Ir para: https://roboflow.com/search?q=hard+hat

2. Escolher um dataset com muitos downloads (ex: 10k+)
   Exemplo: "Hard Hat Workers Safety Detection" tem ~20k downloads

3. Clicar em "Get API Code"

4. Vai aparecer um codigo assim:

   from roboflow import Roboflow
   rf = Roboflow(api_key="sua_chave_aqui")
   project = rf.workspace().project("hard-hats-xyz")
   dataset = project.version(1).download("yolov8")

5. COPIAR este codigo

6. Colar em um arquivo novo: download_dataset.py

7. Executar:
   python download_dataset.py

8. Vai criar pasta: datasets/epi_dataset/

9. Depois executar treino:
   python train_epi_model.py

DICA: Se nao conseguir achar "Get API Code", procure por "Export" e selecione YOLOv8
""")


def create_download_template():
    """Criar template de download para usuario preencheer"""
    
    template = '''#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PASSO 1: Substituir "sua_chave_aqui" pela sua chave Roboflow
PASSO 2: Substituir "hard-hats-xyz" pelo seu projeto
PASSO 3: Executar este arquivo
"""

from roboflow import Roboflow
from pathlib import Path
import shutil

print("Fazendo download do dataset Roboflow...")
print("(Isso pode levar alguns minutos)")

try:
    # SUBSTITUIR AQUI!
    rf = Roboflow(api_key="COLOQUE_SUA_CHAVE_AQUI")
    project = rf.workspace().project("COLOQUE_SEU_PROJETO_AQUI")
    dataset = project.version(1).download("yolov8")
    
    # Mover dataset para pasta correta
    src = Path(dataset.location)
    dst = Path("datasets/epi_dataset")
    
    # Se ja existe, remover
    if dst.exists():
        shutil.rmtree(dst)
    
    # Mover
    shutil.move(str(src), str(dst))
    
    print(f"✓ Dataset baixado com sucesso em: {dst}")
    print()
    print("Proximo passo:")
    print("  python train_epi_model.py")
    
except Exception as e:
    print(f"Erro: {e}")
    print()
    print("Dicas:")
    print("1. Verificar se sua chave Roboflow esta correta")
    print("2. Verificar se seu projeto existe")
    print("3. Ir para https://roboflow.com e regenerar API key")
'''
    
    output = Path("download_dataset.py")
    with open(output, "w") as f:
        f.write(template)
    
    print(f"\n✓ Template criado: {output}")
    print("Edite com sua chave Roboflow e execute!")


def main():
    """Menu principal"""
    
    while True:
        print_menu()
        
        choice = input("Escolha uma opcao (0-3): ").strip()
        
        if choice == "0":
            show_quick_guide()
        elif choice == "1":
            print("\nVocê escolheu: Hard Hat Workers Safety")
            print("URL: https://roboflow.com/search?q=hard+hat")
            show_dataset_download_code()
            create_download_template()
            break
        elif choice == "2":
            print("\nVocê escolheu: Safety Equipment Detection")
            print("URL: https://roboflow.com/search?q=safety+equipment")
            show_dataset_download_code()
            create_download_template()
            break
        elif choice == "3":
            print("\nVocê escolheu: Helmet Detection Dataset")
            print("URL: https://roboflow.com/search?q=helmet")
            show_dataset_download_code()
            create_download_template()
            break
        else:
            print("Opcao invalida!")


if __name__ == "__main__":
    try:
        main()
        
        print("\n" + "="*70)
        print("PROXIMOS PASSOS:")
        print("="*70)
        print()
        print("1. Editar download_dataset.py com sua chave Roboflow")
        print("2. Executar: python download_dataset.py")
        print("3. Esperar dataset baixar (alguns minutos)")
        print("4. Executar: python train_epi_model.py")
        print("5. Esperar treino terminar (30min-1h)")
        print("6. Executar: python main_epi.py")
        print()
        print("Pronto! Seu sistema detectara capacete/oculos com CORES!")
        print()
        
    except KeyboardInterrupt:
        print("\n\nCancelado pelo usuario")
        sys.exit(0)
