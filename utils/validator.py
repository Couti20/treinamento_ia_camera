"""
Validação de EPIs e geração de alertas.
"""
from typing import List, Dict
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
    missing_epis: List[str]  # Ex: ["helmet", "gloves"]
    severity: str  # "info", "warning", "critical"
    bbox: str  # "x1,y1,x2,y2"
    person_confidence: float

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2)


class EPIValidator:
    """Valida EPIs de pessoas contra requisitos."""

    def __init__(self, required_epis: List[str]):
        self.required_epis = [ppe.lower() for ppe in required_epis]

    def validate_person(self, detected_ppes: Dict[str, any]) -> Dict[str, any]:
        """
        Validar EPIs de uma pessoa.
        Retorna dict com: missing, present, complete (bool), severity
        """
        # Se não há requisitos, tudo é OK
        if not self.required_epis:
            return {
                "missing": [],
                "present": list(detected_ppes.keys()),
                "complete": True,
                "severity": "info",
                "missing_percent": 0.0,
            }
        
        detected_types = set()
        
        # Mapear classes detectadas para tipos de EPI esperados
        for detected_class in detected_ppes.keys():
            # Ignorar "person" - não é um EPI
            if detected_class.lower() == "person":
                continue
            
            detected_lower = detected_class.lower()
            for required in self.required_epis:
                # Verificar match EXATO ou como substring do início (evita falsos positivos)
                # Ex: "glove" == "gloves" -> True (substring exata)
                #     "ves" in "vest" -> False (evitar)
                if detected_lower == required or (
                    len(detected_lower) > len(required) and detected_lower.startswith(required)
                ) or (
                    len(required) > len(detected_lower) and required.startswith(detected_lower)
                ):
                    detected_types.add(required)
                    break

        missing = [ppe for ppe in self.required_epis if ppe not in detected_types]
        
        # Calcular severidade
        missing_percent = len(missing) / len(self.required_epis) if self.required_epis else 0
        if not missing:
            severity = "info"  # OK
        elif missing_percent < 0.5:
            severity = "warning"  # Falta alguns
        else:
            severity = "critical"  # Falta a maioria

        return {
            "missing": missing,
            "present": list(detected_types),
            "complete": len(missing) == 0,
            "severity": severity,
            "missing_percent": missing_percent,
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
