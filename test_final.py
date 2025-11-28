#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Teste rápido para validar sistema
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 60)
print("✓ TESTE FINAL - EPI DETECTOR")
print("=" * 60)
print()

# 1. Verificar imports
try:
    from config.settings import CONF_THRESHOLD, DEFAULT_REQUIRED_PPE
    print("✓ Config carregada")
except Exception as e:
    print(f"✗ Erro em config: {e}")
    sys.exit(1)

# 2. Verificar detector
try:
    from utils.detector import EPIDetector
    print("✓ Detector importado")
except Exception as e:
    print(f"✗ Erro em detector: {e}")
    sys.exit(1)

# 3. Verificar validator
try:
    from utils.validator import EPIValidator
    print("✓ Validator importado")
except Exception as e:
    print(f"✗ Erro em validator: {e}")
    sys.exit(1)

# 4. Verificar logger
try:
    from logger.audit import AuditLogger
    print("✓ Logger importado")
except Exception as e:
    print(f"✗ Erro em logger: {e}")
    sys.exit(1)

# 5. Verificar modelo
if Path("yolov8n.pt").exists():
    print("✓ Modelo yolov8n.pt encontrado")
elif Path("best.pt").exists():
    print("✓ Modelo best.pt encontrado")
else:
    print("✗ Nenhum modelo encontrado!")
    sys.exit(1)

# 6. Testar detector
try:
    import cv2
    import numpy as np
    
    detector = EPIDetector("yolov8n.pt", CONF_THRESHOLD)
    print("✓ Detector inicializado")
    
    # Frame dummy
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    persons, ppes = detector.detect_frame(frame)
    print(f"✓ Detecção funcionou (frame vazio: {len(persons)} pessoas, {len(ppes)} EPIs)")
    
except Exception as e:
    print(f"✗ Erro em detecção: {e}")
    sys.exit(1)

# 7. Testar validator
try:
    validator = EPIValidator(DEFAULT_REQUIRED_PPE)
    result = validator.validate_person({})
    print(f"✓ Validator funcionou: {result['severity']}")
except Exception as e:
    print(f"✗ Erro em validação: {e}")
    sys.exit(1)

# 8. Testar câmera
try:
    cap = cv2.VideoCapture(0)
    if cap.isOpened():
        print("✓ Câmera aberta com sucesso")
        cap.release()
    else:
        print("⚠ Câmera não está acessível (possivelmente em uso)")
except Exception as e:
    print(f"⚠ Aviso em câmera: {e}")

print()
print("=" * 60)
print("✓ TODOS OS TESTES PASSARAM!")
print("=" * 60)
print()
print("Próximo: python main.py")
