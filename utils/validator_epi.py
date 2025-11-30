#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Validador melhorado de EPIs com cores corretas
Verde: Todos os EPIs presentes
Laranja: Alguns EPIs faltando
Vermelho: Maioria dos EPIs faltando
"""

from typing import List, Dict, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)


@dataclass
class EPIAlert:
    """Representa um alerta de EPI faltando."""
    timestamp: str
    frame_number: int
    person_id: int
    missing_epis: List[str]
    severity: str  # "ok", "warning", "critical"
    bbox: str  # "x1,y1,x2,y2"
    person_confidence: float

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2)


class EPIValidator:
    """Valida EPIs de pessoas contra requisitos."""

    # Cores BGR (OpenCV usa BGR)
    COLORS = {
        "ok": (0, 255, 0),         # Verde
        "warning": (0, 165, 255),  # Laranja
        "critical": (0, 0, 255),   # Vermelho
        "neutral": (128, 128, 128) # Cinza
    }

    def __init__(self, required_epis: List[str]):
        """
        Inicializar validador.
        
        Args:
            required_epis: Lista de EPIs obrigatórios (ex: ["helmet", "goggles"])
        """
        self.required_epis = [ppe.lower() for ppe in required_epis]
        logger.info(f"Validador inicializado. EPIs obrigatórios: {self.required_epis}")

    def validate_person(self, detected_ppes: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validar EPIs de uma pessoa.
        
        Args:
            detected_ppes: Dict com EPIs detectados (chave: "helmet", "goggles", etc)
        
        Returns:
            Dict com: missing, present, complete (bool), severity, color, message
        """
        detected_types = set()
        
        # Mapear classes detectadas para tipos de EPI esperados
        for detected_class in detected_ppes.keys():
            detected_lower = detected_class.lower()
            
            # Verificar match com requisitos
            for required in self.required_epis:
                if detected_lower == required or (
                    len(detected_lower) > len(required) and 
                    detected_lower.startswith(required)
                ) or (
                    len(required) > len(detected_lower) and 
                    required.startswith(detected_lower)
                ):
                    detected_types.add(required)
                    break

        # EPIs faltando
        missing = [ppe for ppe in self.required_epis if ppe not in detected_types]
        
        # Calcular severidade
        if not self.required_epis:
            # Sem requisitos definidos, apenas detectar pessoas
            severity = "ok"
            missing_percent = 0
            color = self.COLORS["ok"]
            message = "Pessoa detectada"
        elif not missing:
            # Todos os EPIs presentes
            severity = "ok"
            missing_percent = 0
            color = self.COLORS["ok"]
            message = f"✓ OK - Todos os {len(self.required_epis)} EPIs"
        else:
            missing_percent = len(missing) / len(self.required_epis) if self.required_epis else 0
            
            if missing_percent < 0.5:
                # Menos de 50% faltando
                severity = "warning"
                color = self.COLORS["warning"]
                message = f"⚠ FALTA: {', '.join(missing)}"
            else:
                # Mais de 50% faltando
                severity = "critical"
                color = self.COLORS["critical"]
                message = f"🛑 CRÍTICO: {len(missing)} EPIs faltando"

        return {
            "missing": missing,
            "present": list(detected_types),
            "complete": len(missing) == 0,
            "severity": severity,
            "missing_percent": missing_percent,
            "color": color,
            "message": message,
        }

    def create_alert(
        self,
        frame_number: int,
        person_id: int,
        missing_epis: List[str],
        bbox: tuple,
        person_conf: float,
        severity: str,
    ) -> EPIAlert:
        """Criar alerta estruturado."""
        bbox_str = f"{bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]}"
        return EPIAlert(
            timestamp=datetime.now().isoformat(timespec="milliseconds"),
            frame_number=frame_number,
            person_id=person_id,
            missing_epis=missing_epis,
            severity=severity,
            bbox=bbox_str,
            person_confidence=person_conf,
        )

    def get_color(self, severity: str) -> tuple:
        """Retornar cor BGR para severidade"""
        return self.COLORS.get(severity, self.COLORS["neutral"])

    def format_message(self, validation: Dict) -> str:
        """Formatar mensagem de validação"""
        return validation.get("message", "")
