#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Detector melhorado para EPIs específicos (capacete, óculos, luvas)
Com suporte a modelo customizado e mapeamento automático de classes
"""

import cv2
import numpy as np
from ultralytics import YOLO
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


@dataclass
class Detection:
    """Representa uma detecção (pessoa ou EPI)."""
    class_id: int
    class_name: str
    bbox: Tuple[int, int, int, int]  # x1, y1, x2, y2
    confidence: float
    centroid: Tuple[int, int]

    def area(self) -> int:
        x1, y1, x2, y2 = self.bbox
        return (x2 - x1) * (y2 - y1)

    def iou(self, other: "Detection") -> float:
        """Calcular IoU (Intersection over Union) com outra detecção."""
        x1_a, y1_a, x2_a, y2_a = self.bbox
        x1_b, y1_b, x2_b, y2_b = other.bbox

        xi1 = max(x1_a, x1_b)
        yi1 = max(y1_a, y1_b)
        xi2 = min(x2_a, x2_b)
        yi2 = min(y2_a, y2_b)

        inter = max(0, xi2 - xi1) * max(0, yi2 - yi1)
        union = (x2_a - x1_a) * (y2_a - y1_a) + (x2_b - x1_b) * (y2_b - y1_b) - inter

        return inter / union if union > 0 else 0


@dataclass
class PersonEPIStatus:
    """Status de uma pessoa e seus EPIs."""
    person_id: int
    person_detection: Detection
    detected_ppes: Dict[str, Detection]  # chave: tipo EPI (ex: "helmet"), valor: Detection
    missing_ppes: List[str]
    confidence_score: float  # média de confiança


class EPIDetector:
    """Detector de EPIs usando YOLO com suporte a modelo customizado."""

    # Mapeamento de aliases para classes padrão
    EPI_ALIASES = {
        "helmet": ["helmet", "hard_hat", "hardhat", "hard-hat", "cap"],
        "goggles": ["goggles", "glasses", "safety_glasses", "eye_protection"],
        "gloves": ["gloves", "glove", "safety_glove", "hand_protection"],
        "vest": ["vest", "safety_vest", "colete", "collared_vest"],
    }

    def __init__(self, model_path: str, conf_threshold: float = 0.3, is_custom: bool = False):
        """
        Inicializar detector.
        
        Args:
            model_path: Caminho do modelo (yolov8n.pt ou models/epi_custom_best.pt)
            conf_threshold: Confiança mínima
            is_custom: True se modelo é customizado (tem capacete, óculos, etc)
        """
        self.model = YOLO(model_path)
        self.conf_threshold = conf_threshold
        self.class_names = self.model.names
        self.is_custom_model = is_custom
        self.person_class_ids = self._identify_person_classes()
        
        logger.info(f"Modelo carregado: {model_path}")
        logger.info(f"Tipo: {'Customizado' if is_custom else 'Genérico (COCO)'}")
        logger.info(f"Classes disponíveis: {list(self.class_names.values())}")

    def _identify_person_classes(self) -> List[int]:
        """Identificar IDs de classes que representam pessoas."""
        person_ids = [
            cid for cid, name in self.class_names.items()
            if "person" in name.lower() or "worker" in name.lower()
        ]
        if not person_ids:
            logger.warning("Nenhuma classe 'person' encontrada!")
        return person_ids

    def normalize_ppe_name(self, detected_class: str) -> Optional[str]:
        """
        Normalizar nome de EPI detectado para classe padrão.
        Ex: "safety_glasses" -> "goggles"
        """
        detected_lower = detected_class.lower()
        
        for standard_name, aliases in self.EPI_ALIASES.items():
            for alias in aliases:
                if detected_lower == alias or alias in detected_lower:
                    return standard_name
        
        # Se não encontrar alias, retorna a classe como está
        return detected_class

    def detect_frame(self, frame: np.ndarray) -> Tuple[List[Detection], List[Detection]]:
        """
        Detectar pessoas e EPIs em um frame.
        Retorna: (persons, ppes)
        """
        # Otimização para CPU: reduzir tamanho do frame
        h, w = frame.shape[:2]
        scale_factor = 0.5
        frame_resized = cv2.resize(frame, (int(w * scale_factor), int(h * scale_factor)))
        
        # Usar modelo em CPU com parâmetros otimizados
        results = self.model.predict(
            frame_resized, 
            conf=self.conf_threshold, 
            verbose=False,
            device="cpu",
            half=False,
        )
        r = results[0]

        persons = []
        ppes = []

        if r.boxes is None or len(r.boxes) == 0:
            return persons, ppes

        xyxy = r.boxes.xyxy.cpu().numpy()
        cls_ids = r.boxes.cls.cpu().numpy().astype(int)
        confs = r.boxes.conf.cpu().numpy()

        # Fator para voltar ao tamanho original
        scale_factor_inv = 1.0 / scale_factor

        for bbox, cls_id, conf in zip(xyxy, cls_ids, confs):
            x1, y1, x2, y2 = map(int, bbox * scale_factor_inv)
            centroid = ((x1 + x2) // 2, (y1 + y2) // 2)
            class_name = self.class_names.get(int(cls_id), str(cls_id))

            detection = Detection(
                class_id=int(cls_id),
                class_name=class_name,
                bbox=(x1, y1, x2, y2),
                confidence=float(conf),
                centroid=centroid,
            )

            if cls_id in self.person_class_ids:
                persons.append(detection)
            else:
                ppes.append(detection)

        return persons, ppes

    def associate_ppes_to_persons(
        self,
        persons: List[Detection],
        ppes: List[Detection],
        overlap_threshold: float = 0.08,
        centroid_threshold: int = 150,
    ) -> List[PersonEPIStatus]:
        """
        Associar EPIs às pessoas baseado em overlap e distância de centroid.
        """
        statuses = []

        for person_id, person in enumerate(persons):
            detected_ppes = {}  # tipo_epi -> Detection

            for ppe in ppes:
                # Calcular overlap
                x1_p, y1_p, x2_p, y2_p = person.bbox
                x1_e, y1_e, x2_e, y2_e = ppe.bbox

                overlap_x = max(0, min(x2_p, x2_e) - max(x1_p, x1_e))
                overlap_y = max(0, min(y2_p, y2_e) - max(y1_p, y1_e))
                overlap_area = overlap_x * overlap_y
                ppe_area = (x2_e - x1_e) * (y2_e - y1_e)

                overlap_ratio = overlap_area / ppe_area if ppe_area > 0 else 0

                # Calcular distância entre centroids
                dx = person.centroid[0] - ppe.centroid[0]
                dy = person.centroid[1] - ppe.centroid[1]
                centroid_dist = (dx**2 + dy**2) ** 0.5

                # Associar se overlap > threshold ou centroid < threshold
                if overlap_ratio > overlap_threshold or centroid_dist < centroid_threshold:
                    # Normalizar nome do EPI
                    ppe_type = self.normalize_ppe_name(ppe.class_name)
                    
                    # Guardar apenas EPI de maior confiança por tipo
                    if ppe_type not in detected_ppes or ppe.confidence > detected_ppes[ppe_type].confidence:
                        detected_ppes[ppe_type] = ppe

            status = PersonEPIStatus(
                person_id=person_id,
                person_detection=person,
                detected_ppes=detected_ppes,
                missing_ppes=[],
                confidence_score=person.confidence,
            )

            statuses.append(status)

        return statuses

    def get_model_info(self) -> Dict:
        """Retornar informações sobre o modelo"""
        return {
            "is_custom": self.is_custom_model,
            "classes": list(self.class_names.values()),
            "num_classes": len(self.class_names),
            "conf_threshold": self.conf_threshold,
        }
