#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para testar o detector com salvamento em arquivo de vídeo.
Não usa GUI, apenas processa e salva o vídeo anotado.
"""
import cv2
import logging
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from config.settings import (
    VIDEO_SOURCE,
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


def test_video_output(duration_seconds=15, output_video="logs/test_output.mp4"):
    """
    Testar detector salvando vídeo anotado.
    
    Args:
        duration_seconds: Quanto tempo processar (segundos)
        output_video: Caminho do vídeo de saída
    """
    
    # Procurar modelo
    model_path = None
    for candidate in ["yolov8n.pt", "best.pt"]:
        if Path(candidate).exists():
            model_path = str(candidate)
            logger.info(f"Modelo encontrado: {model_path}")
            break
    
    if not model_path:
        logger.error("Modelo não encontrado!")
        return
    
    # Inicializar
    detector = EPIDetector(model_path, CONF_THRESHOLD)
    validator = EPIValidator(DEFAULT_REQUIRED_PPE)
    audit_logger = AuditLogger(CSV_LOG_PATH)
    
    # Abrir câmera
    cap = cv2.VideoCapture(VIDEO_SOURCE)
    if not cap.isOpened():
        logger.error(f"Erro ao abrir câmera: {VIDEO_SOURCE}")
        return
    
    # Otimizar câmera
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)
    
    # VideoWriter
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    output_path = Path(output_video)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    out = cv2.VideoWriter(
        str(output_path),
        fourcc,
        30.0,
        (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), 
         int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    )
    
    logger.info(f"Iniciando captura de {duration_seconds}s...")
    logger.info(f"Vídeo será salvo em: {output_path}")
    
    start_time = time.time()
    frame_count = 0
    frame_times = []
    
    try:
        while time.time() - start_time < duration_seconds:
            t0 = time.time()
            success, frame = cap.read()
            
            if not success:
                logger.info("Fim da câmera")
                break
            
            frame_count += 1
            
            # Detectar
            persons, ppes = detector.detect_frame(frame)
            person_statuses = detector.associate_ppes_to_persons(
                persons, ppes,
                overlap_threshold=OVERLAP_THRESHOLD,
                centroid_threshold=CENTROID_DISTANCE_THRESHOLD,
            )
            
            # Anotar frame
            annotated = frame.copy()
            
            for status in person_statuses:
                person_det = status.person_detection
                x1, y1, x2, y2 = person_det.bbox
                
                # Desenhar pessoa
                cv2.rectangle(annotated, (x1, y1), (x2, y2), COLOR_OK, 2)
                cv2.putText(
                    annotated,
                    f"Person (conf: {person_det.confidence:.2f})",
                    (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    COLOR_OK,
                    1,
                )
                
                # Desenhar EPIs detectados
                for ppe_type, ppe_det in status.detected_ppes.items():
                    ex1, ey1, ex2, ey2 = ppe_det.bbox
                    cv2.rectangle(annotated, (ex1, ey1), (ex2, ey2), (255, 200, 0), 1)
                    cv2.putText(
                        annotated,
                        f"{ppe_type} ({ppe_det.confidence:.2f})",
                        (ex1, ey1 - 5),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.35,
                        (255, 200, 0),
                        1,
                    )
            
            # FPS
            ft = time.time() - t0
            frame_times.append(ft)
            if len(frame_times) > 30:
                frame_times.pop(0)
            avg_fps = 1.0 / (sum(frame_times) / len(frame_times))
            
            # Info
            cv2.putText(
                annotated,
                f"FPS: {avg_fps:.1f} | Pessoas: {len(person_statuses)} | Frame: {frame_count}",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2,
            )
            
            # Escrever
            out.write(annotated)
            
            if frame_count % 30 == 0:
                logger.info(f"Frame {frame_count} processado | FPS: {avg_fps:.1f}")
    
    except KeyboardInterrupt:
        logger.info("Interrompido pelo usuário")
    
    finally:
        cap.release()
        out.release()
        audit_logger.flush()
        
        logger.info(f"✓ Captura finalizada")
        logger.info(f"  Frames processados: {frame_count}")
        logger.info(f"  Tempo total: {time.time() - start_time:.1f}s")
        logger.info(f"  FPS médio: {frame_count / (time.time() - start_time):.1f}")
        logger.info(f"  Vídeo salvo em: {output_path}")
        logger.info(f"  CSV log: {CSV_LOG_PATH}")


if __name__ == "__main__":
    # Testar com 20 segundos
    test_video_output(duration_seconds=20, output_video="logs/test_output.mp4")
