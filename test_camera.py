# -*- coding: utf-8 -*-
"""
Script de teste da câmera - versão que salva vídeo em arquivo
"""
import cv2
import logging
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))

from config.settings import (
    CONF_THRESHOLD,
    DEFAULT_REQUIRED_PPE,
    CSV_LOG_PATH,
    COLOR_OK,
    COLOR_ALERT,
    COLOR_WARNING,
    EPI_CLASS_MAPPING,
    OVERLAP_THRESHOLD,
    CENTROID_DISTANCE_THRESHOLD,
)
from utils.detector import EPIDetector
from utils.validator import EPIValidator
from logger.audit import AuditLogger

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def test_camera(duration_seconds=30, output_video="test_output.avi"):
    """Testar câmera e salvar vídeo com detecções."""
    
    logger.info("🎥 Iniciando teste de câmera...")
    
    # Inicializar detector
    model_path = "yolov8n.pt"
    detector = EPIDetector(model_path, CONF_THRESHOLD)
    validator = EPIValidator(DEFAULT_REQUIRED_PPE)
    audit_logger = AuditLogger(CSV_LOG_PATH)
    
    # Abrir câmera
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        logger.error("❌ Não consegui abrir a câmera!")
        return
    
    # Configurações do vídeo
    fps = int(cap.get(cv2.CAP_PROP_FPS)) or 30
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    logger.info(f"✅ Câmera aberta - {w}x{h} @ {fps} FPS")
    
    # Video writer
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(output_video, fourcc, fps, (w, h))
    
    frame_count = 0
    persons_detected = 0
    
    logger.info(f"⏱️ Capturando {duration_seconds} segundos...")
    logger.info(f"📹 Salvando em: {output_video}")
    
    while True:
        success, frame = cap.read()
        if not success:
            break
        
        frame_count += 1
        
        # Detectar
        persons, ppes = detector.detect_frame(frame)
        person_statuses = detector.associate_ppes_to_persons(
            persons, ppes,
            overlap_threshold=OVERLAP_THRESHOLD,
            centroid_threshold=CENTROID_DISTANCE_THRESHOLD,
        )
        
        # Desenhar detecções
        annotated = frame.copy()
        
        for status in person_statuses:
            persons_detected += 1
            person_det = status.person_detection
            x1, y1, x2, y2 = person_det.bbox
            
            # Validar
            validation = validator.validate_person(status.detected_ppes)
            missing_epis = validation["missing"]
            severity = validation["severity"]
            
            # Cor
            if severity == "info":
                color = COLOR_OK
                text = f"✓ PESSOA (conf: {person_det.confidence:.2f})"
            else:
                color = COLOR_ALERT
                text = f"⚠ PESSOA (falta: {', '.join(missing_epis)})"
            
            # Desenhar
            cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 3)
            cv2.putText(annotated, text, (x1, y1 - 15), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            
            logger.info(f"Frame {frame_count}: Pessoa detectada conf={person_det.confidence:.2f}")
            
            # Log
            audit_logger.log_detection(
                frame_number=frame_count,
                person_id=status.person_id,
                bbox=person_det.bbox,
                missing_epis=missing_epis,
                person_conf=person_det.confidence,
                severity=severity,
            )
        
        # Desenhar stats
        cv2.putText(annotated, f"Frame: {frame_count}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(annotated, f"Pessoas: {len(person_statuses)}", (10, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Salvar frame
        out.write(annotated)
        
        # Parar se atingiu duração
        if frame_count >= (duration_seconds * fps):
            break
    
    # Finalizar
    cap.release()
    out.release()
    audit_logger.flush()
    
    logger.info(f"\n✅ Teste finalizado!")
    logger.info(f"   Frames capturados: {frame_count}")
    logger.info(f"   Pessoas detectadas: {persons_detected}")
    logger.info(f"   Vídeo salvo: {output_video}")
    logger.info(f"   Log CSV: {CSV_LOG_PATH}")
    
    # Estatísticas
    stats = audit_logger.get_stats()
    logger.info(f"\n📊 Estatísticas:")
    logger.info(f"   Conformidade: {stats['compliance_rate']:.1f}%")
    logger.info(f"   Violações: {stats['violations']}")
    logger.info(f"   Alertas críticos: {stats['critical_alerts']}")


if __name__ == "__main__":
    test_camera(duration_seconds=30, output_video="test_output.avi")
    print("\n✅ Teste completo! Verifique 'test_output.avi' para ver o vídeo.")
