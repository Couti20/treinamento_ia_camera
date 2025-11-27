"""
Sistema de logging estruturado para auditoria.
"""
import csv
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict
from dataclasses import asdict

logger = logging.getLogger(__name__)


class AuditLogger:
    """Registra detecções e alertas em CSV e JSON."""

    def __init__(self, csv_path: Path, json_path: Path = None):
        self.csv_path = csv_path
        self.json_path = json_path
        self._init_csv()
        self.logs_buffer = []

    def _init_csv(self):
        """Criar arquivo CSV com cabeçalhos se não existir."""
        if not self.csv_path.parent.exists():
            self.csv_path.parent.mkdir(parents=True, exist_ok=True)

        if not self.csv_path.exists():
            with open(self.csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "timestamp",
                    "frame",
                    "pessoa_id",
                    "bbox",
                    "missing_ppe",
                    "person_conf",
                    "severity",
                ])
            logger.info(f"Arquivo CSV criado: {self.csv_path}")

    def log_detection(
        self,
        frame_number: int,
        person_id: int,
        bbox: tuple,
        missing_epis: List[str],
        person_conf: float,
        severity: str = "info",
    ):
        """Registrar uma detecção."""
        timestamp = datetime.now().isoformat(timespec="milliseconds")
        bbox_str = f"{bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]}"
        missing_str = ";".join(missing_epis) if missing_epis else ""

        row = [timestamp, frame_number, person_id, bbox_str, missing_str, person_conf, severity]

        self.logs_buffer.append(row)

        # Escrever em buffer a cada 10 detecções (reduz I/O)
        if len(self.logs_buffer) >= 10:
            self.flush()

    def flush(self):
        """Escrever buffer em CSV."""
        if not self.logs_buffer:
            return

        try:
            with open(self.csv_path, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerows(self.logs_buffer)
            self.logs_buffer.clear()
        except Exception as e:
            logger.error(f"Erro ao escrever CSV: {e}")

    def get_logs(self, limit: int | None = 100) -> List[Dict]:
        """Retornar logs recentes em formato JSON.

        Args:
            limit: número máximo de registros a retornar. Se `None`, retorna todos.
        """
        self.flush()  # Garantir que tudo foi escrito

        logs = []
        try:
            with open(self.csv_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    logs.append(row)
        except Exception as e:
            logger.error(f"Erro ao ler CSV: {e}")

        if limit is None:
            return logs
        # Se limit for maior que o total, devolve tudo
        if limit >= len(logs):
            return logs
        return logs[-limit:]

    def export_json(self, output_path: Path = None):
        """Exportar logs em JSON."""
        self.flush()
        output_path = output_path or self.json_path or self.csv_path.parent / "ppe_audit.json"

        logs = self.get_logs(limit=None)
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(logs, f, indent=2, ensure_ascii=False)
            logger.info(f"Logs exportados para JSON: {output_path}")
        except Exception as e:
            logger.error(f"Erro ao exportar JSON: {e}")

    def get_stats(self) -> Dict:
        """Retornar estatísticas dos logs."""
        logs = self.get_logs(limit=None)

        total = len(logs)
        violations = len([log for log in logs if log.get("missing_ppe", "")])
        critical = len([log for log in logs if log.get("severity") == "critical"])
        warning = len([log for log in logs if log.get("severity") == "warning"])

        return {
            "total_detections": total,
            "violations": violations,
            "critical_alerts": critical,
            "warning_alerts": warning,
            "compliance_rate": (1 - violations / total) * 100 if total > 0 else 100,
        }
