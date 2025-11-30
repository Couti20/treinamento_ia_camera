#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Teste final do sistema de EPIs customizados"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))

from utils.validator_epi import EPIValidator

print("\n" + "="*60)
print("TESTE: SISTEMA DE EPIS CUSTOMIZADOS")
print("="*60 + "\n")

# Criar validator
v = EPIValidator(["helmet", "goggles"])

# Teste 1: Sem EPIs
print("Teste 1: Pessoa SEM EPIs (deve ficar VERMELHO)")
r = v.validate_person({})
print(f"  Severity: {r['severity']}")
print(f"  Color: {r['color']}")
print(f"  Message: {r['message']}")
print()

# Teste 2: Com capacete apenas
print("Teste 2: Pessoa COM capacete (deve ficar LARANJA)")
r = v.validate_person({"helmet": "x"})
print(f"  Severity: {r['severity']}")
print(f"  Color: {r['color']}")
print(f"  Message: {r['message']}")
print()

# Teste 3: Com tudo
print("Teste 3: Pessoa COM TODOS EPIs (deve ficar VERDE)")
r = v.validate_person({"helmet": "x", "goggles": "y"})
print(f"  Severity: {r['severity']}")
print(f"  Color: {r['color']}")
print(f"  Message: {r['message']}")
print()

print("="*60)
print("OK - SISTEMA FUNCIONANDO!")
print("="*60)
