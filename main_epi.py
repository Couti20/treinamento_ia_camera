#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
EPI Detector - Sistema de Monitoramento de Equipamentos de Proteção
Versão com suporte a EPIs customizados (capacete, óculos, luvas)
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
    EPI_CLASS_MAPPING,
    OVERLAP_THRESHOLD,
    CENTROID_DISTANCE_THRESHOLD,
)

# Tentar importar novo detector/validator, fallback para antigos
try:
    from utils.detector_epi import EPIDetector
    from utils.validator_epi import EPIValidator
    logger_init_msg = "✓ Usando detectors customizados (com suporte a EPIs)"
except ImportError:
    from utils.detector import EPIDetector
    from utils.validator import EPIValidator
    logger_init_msg = "⚠ Usando detectors padrão (sem EPIs customizados)"

from logger.audit import AuditLogger

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)
logger.info(logger_init_msg)


class EPIMonitoringSystem:
    """Sistema completo de monitoramento de EPIs."""

    def __init__(
        self,
        model_path: str,
        video_source: int = 0,
        required_ppes: list = None,
        conf_threshold: float = 0.3,
        is_custom_model: bool = False,
    ):
        """
        Inicializar sistema.
        
        Args:
            model_path: Caminho do modelo
            video_source: Fonte de vídeo (0=webcam)
            required_ppes: EPIs obrigatórios
            conf_threshold: Confiança mínima
            is_custom_model: Se modelo é customizado
        """
        # Detectar se pode passar is_custom
        try:
            self.detector = EPIDetector(model_path, conf_threshold, is_custom=is_custom_model)
        except TypeError:
            # Fallback para detector antigo
            self.detector = EPIDetector(model_path, conf_threshold)
        
        self.validator = EPIValidator(required_ppes or DEFAULT_REQUIRED_PPE)
        self.audit_logger = AuditLogger(CSV_LOG_PATH)
        self.video_source = video_source
        self.frame_count = 0

        logger.info(
            f"Sistema inicializado. EPIs obrigatórios: {self.validator.required_epis}"
        )

    def run(self):
        """Executar monitoramento de vídeo."""
        cap = cv2.VideoCapture(self.video_source)

        if not cap.isOpened():
            logger.error(f"Erro ao abrir fonte de vídeo: {self.video_source}")
            return

        # Otimizar câmera para CPU
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 30)

        logger.info("Iniciando detecção. Pressione 'Q' para sair.")

        frame_times = []
        max_history = 30

        while True:
            start_time = time.time()
            success, frame = cap.read()

            if not success:
                logger.info("Fim do vídeo ou falha na leitura.")
                break

            self.frame_count += 1

            # Detectar pessoas e EPIs
            persons, ppes = self.detector.detect_frame(frame)

            # Associar EPIs às pessoas
            person_statuses = self.detector.associate_ppes_to_persons(
                persons,
                ppes,
                overlap_threshold=OVERLAP_THRESHOLD,
                centroid_threshold=CENTROID_DISTANCE_THRESHOLD,
            )

            # Validar e desenhar
            annotated_frame = self._process_detections(
                frame, person_statuses, persons, ppes
            )

            # Calcular FPS
            frame_time = time.time() - start_time
            frame_times.append(frame_time)
            if len(frame_times) > max_history:
                frame_times.pop(0)
            avg_fps = 1.0 / (sum(frame_times) / len(frame_times)) if frame_times else 0

            # Adicionar FPS na imagem
            cv2.putText(
                annotated_frame,
                f"FPS: {avg_fps:.1f}",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2,
            )

            # Mostrar
            cv2.imshow("EPI Detector - Monitoramento de Equipamentos", annotated_frame)

            # Pressionar 'Q' para sair
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q") or key == ord("Q") or key == 27:  # 27 = ESC
                break

        # Finalizar
        cap.release()
        cv2.destroyAllWindows()
        self.audit_logger.flush()

        logger.info("Monitoramento encerrado.")
        logger.info(f"Estatísticas: {self.audit_logger.get_stats()}")

    def _process_detections(self, frame, person_statuses, persons, ppes):
        """Processar detecções e desenhar na imagem."""
        annotated = frame.copy()
        violations_count = 0
        total_persons = len(person_statuses)

        for status in person_statuses:
            person_det = status.person_detection
            x1, y1, x2, y2 = person_det.bbox

            # Validar EPIs
            validation = self.validator.validate_person(status.detected_ppes)
            missing_epis = validation["missing"]
            severity = validation["severity"]
            color = validation.get("color", (128, 128, 128))
            message = validation.get("message", "")

            if severity != "ok":
                violations_count += 1

            # Desenhar caixa da pessoa com cor baseada em severidade
            cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 3)
            cv2.putText(
                annotated,
                message,
                (x1, y1 - 15),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                color,
                2,
            )

            # Registrar log
            self.audit_logger.log_detection(
                frame_number=self.frame_count,
                person_id=status.person_id,
                bbox=person_det.bbox,
                missing_epis=missing_epis,
                person_conf=person_det.confidence,
                severity=severity,
            )

            # Desenhar EPIs detectados (caixas menores)
            for ppe_type, ppe_det in status.detected_ppes.items():
                ex1, ey1, ex2, ey2 = ppe_det.bbox
                ppe_name = EPI_CLASS_MAPPING.get(ppe_type, ppe_type)
                cv2.rectangle(annotated, (ex1, ey1), (ex2, ey2), (255, 200, 0), 1)
                cv2.putText(
                    annotated,
                    f"{ppe_name} ({ppe_det.confidence:.2f})",
                    (ex1, ey1 - 5),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.45,
                    (255, 200, 0),
                    1,
                )

        # Desenhar estatísticas
        stats = self.audit_logger.get_stats()
        y_offset = 25
        info_lines = [
            f"Frame: {self.frame_count}",
            f"Pessoas: {total_persons}",
            f"Violações: {violations_count}",
            f"Conformidade: {stats.get('compliance_rate', 0):.1f}%",
        ]

        for i, line in enumerate(info_lines):
            cv2.putText(
                annotated,
                line,
                (10, y_offset + i * 25),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2,
            )

        return annotated


def main():
    """Função principal."""
    try:
        # Procurar modelo
        model_candidates = [
            ("models/epi_custom_best.pt", True),   # Modelo customizado
            ("best.pt", False),                     # Modelo local
            ("yolov8n.pt", False),                  # Modelo padrão COCO
        ]

        model_path = None
        is_custom = False
        
        for candidate, is_custom_candidate in model_candidates:
            if Path(candidate).exists():
                model_path = str(candidate)
                is_custom = is_custom_candidate
                logger.info(f"Modelo encontrado: {model_path}")
                break

        if not model_path:
            logger.warning("Nenhum modelo local encontrado. Tentando download automático...")
            model_path = "yolov8n.pt"
            is_custom = False

        # Inicializar sistema
        system = EPIMonitoringSystem(
            model_path=model_path,
            video_source=VIDEO_SOURCE,
            required_ppes=DEFAULT_REQUIRED_PPE,
            conf_threshold=CONF_THRESHOLD,
            is_custom_model=is_custom,
        )

        # Executar
        system.run()

    except Exception as e:
        logger.error(f"Erro fatal: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
