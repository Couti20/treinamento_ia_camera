#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cv2
import numpy as np
import requests
import json
import sys
from datetime import datetime


class EPIDetector:
    """Detector de EPIs via API nova do Roboflow"""

    DANGER_CLASSES = {'no-helmet', 'no-glove', 'no-vest', 'no-goggles'}
    SAFETY_CLASSES = {'helmet', 'glove', 'vest', 'goggles'}

    COLOR_RED = (0, 0, 255)
    COLOR_GREEN = (0, 255, 0)
    COLOR_YELLOW = (0, 255, 255)

    # mapagem simples para rótulos em pt/en e "no-*"
    EPI_ALIASES = {
        'capacete': 'helmet',
        'helmet': 'helmet',
        'capacete-sem': 'no-helmet',
        'sem-capacete': 'no-helmet',
        'oculos': 'goggles',
        'óculos': 'goggles',
        'goggles': 'goggles',
        'sem-oculos': 'no-goggles',
        'no-oculos': 'no-goggles',
        'colete': 'vest',
        'vest': 'vest',
        'sem-colete': 'no-vest',
        'no-colete': 'no-vest',
        'luva': 'glove',
        'luvas': 'glove',
        'glove': 'glove',
        'sem-luva': 'no-glove',
        'no-luva': 'no-glove'
    }

    def __init__(self, api_key: str, model_id: str, confidence: float = 0.5, debug: bool = False):
        self.api_key = api_key
        self.model_id = model_id
        self.confidence = confidence
        self.debug = debug

        # endpoint "nova" (API) e endpoint público de detecção (detect)
        self.api_url = f"https://api.roboflow.com/models/{model_id}/infer"
        # endpoint de detecção público — costuma aceitar files multipart e query string api_key
        self.detect_url = f"https://detect.roboflow.com/{model_id}?api_key={api_key}&confidence={confidence}"

        print(f"[OK] Detector configurado")
        print(f"Model: {model_id}")
        print(f"Endpoint API: {self.api_url}")
        print(f"Endpoint Detect: {self.detect_url}")
        if self.debug:
            print("[DEBUG] modo debug ativado")
        print()

    def predict(self, frame):
        """ Envia imagem para o Roboflow usando POST multipart/form-data """

        # codificar frame para JPEG
        _, img_encoded = cv2.imencode(".jpg", frame)
        img_bytes = img_encoded.tobytes()

        files = {
            "file": ("frame.jpg", img_bytes, "image/jpeg")
        }

        data = {
            "api_key": self.api_key,
            "confidence": self.confidence,
            "overlap": 0.5
        }

        # Usar somente o endpoint público detect.roboflow.com para simplicidade/compatibilidade.
        # Reconstruir a URL com a confiança atual (self.confidence) para permitir ajustes dinâmicos.
        url = f"https://detect.roboflow.com/{self.model_id}?api_key={self.api_key}&confidence={self.confidence}"
        try:
            resp = requests.post(url, files=files, timeout=10)
        except Exception as e:
            if self.debug:
                print(f"[ERR] Erro ao enviar imagem para detect endpoint: {e}")
            return {"predictions": []}

        if resp.status_code != 200:
            if self.debug:
                print(f"[DEBUG] detect endpoint HTTP {resp.status_code}: {resp.text}")
            return {"predictions": []}

        try:
            j = resp.json()
        except Exception:
            if self.debug:
                print("[DEBUG] não foi possível interpretar JSON da resposta detect")
            return {"predictions": []}

        # retornar o JSON (pode ter 'predictions':[] caso sem detecções)
        return j

    def get_color_for_class(self, class_name: str):
        norm = self.normalize_class_name(class_name)
        if norm in self.DANGER_CLASSES:
            return self.COLOR_RED
        elif norm in self.SAFETY_CLASSES:
            return self.COLOR_GREEN
        else:
            return self.COLOR_YELLOW

    def normalize_class_name(self, raw: str):
        if not raw:
            return raw
        key = raw.lower().strip()
        # remover prefixos como "no-" ou "sem-" e mapear
        if key.startswith('no-') or key.startswith('sem-'):
            # tentar mapear direto
            mapped = self.EPI_ALIASES.get(key)
            if mapped:
                return mapped
        # mapear alias simples
        return self.EPI_ALIASES.get(key, key)

    def draw_detections(self, frame, result):
        if "predictions" not in result:
            return frame

        for pred in result["predictions"]:
            # Roboflow pode devolver x,y como centro + width/height
            try:
                cx = float(pred.get('x', 0))
                cy = float(pred.get('y', 0))
                w = float(pred.get('width', 0))
                h = float(pred.get('height', 0))
            except Exception:
                continue

            x1 = int(cx - w / 2)
            y1 = int(cy - h / 2)
            x2 = int(x1 + w)
            y2 = int(y1 + h)

            # limitar aos limites da imagem
            h_img, w_img = frame.shape[:2]
            x1 = max(0, min(x1, w_img - 1))
            x2 = max(0, min(x2, w_img - 1))
            y1 = max(0, min(y1, h_img - 1))
            y2 = max(0, min(y2, h_img - 1))

            class_name = pred.get('class', '')
            conf = float(pred.get('confidence', 0.0))

            color = self.get_color_for_class(class_name)

            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

            # usar nome normalizado no rótulo para consistência
            label_class = self.normalize_class_name(class_name)
            label = f"{label_class} {conf:.2f}"
            cv2.putText(frame, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        return frame

    def run(self, camera_id=0):
        print(f"[CAM] Abrindo camera {camera_id}...")
        cap = cv2.VideoCapture(camera_id)

        if not cap.isOpened():
            print("[ERR] ERRO: Não foi possível abrir a câmera!")
            sys.exit(1)

        print("[OK] Camera aberta!")
        print("[INFO] Pressione Q para sair | D para diminuir | A para aumentar confiança\n")

        while True:
            ret, frame = cap.read()
            if not ret:
                print("[ERR] Falha ao capturar frame")
                break

            # Predição
            result = self.predict(frame)

            # Desenhar resultado
            frame = self.draw_detections(frame, result)

            # desenhar informações de status (confiança atual)
            status = f"conf={self.confidence:.2f}"
            cv2.putText(frame, status, (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 2)

            cv2.imshow("Detecção de EPIs (Roboflow API Nova)", frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            # diminuir confiança com D
            if key == ord('d'):
                self.confidence = max(0.01, round(self.confidence - 0.05, 2))
                print(f"[INFO] confiança ajustada: {self.confidence}")
            # aumentar confiança com A
            if key == ord('a'):
                self.confidence = min(0.99, round(self.confidence + 0.05, 2))
                print(f"[INFO] confiança ajustada: {self.confidence}")

        cap.release()
        cv2.destroyAllWindows()


def main():

    API_KEY = "4cRmXBXKWBpD8jW2NOxr"
    MODEL_ID = "confi_safe-xoeio/1"  # exemplo: project/1
    CONFIDENCE = 0.5

    # ativar debug=True para ver as respostas brutas (útil para diagnosticar ausência de detections)
    detector = EPIDetector(API_KEY, MODEL_ID, CONFIDENCE, debug=True)

    detector.run()


if __name__ == "__main__":
    main()
