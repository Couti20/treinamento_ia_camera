#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cv2
import numpy as np
import requests
import json
import sys
import time
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
        'pessoa sem capacete': 'no-helmet',
        'pessoa_sem_capacete': 'no-helmet',
        'person without helmet': 'no-helmet',
        'person_without_helmet': 'no-helmet',
        'no helmet': 'no-helmet',
        'no_helmet': 'no-helmet',
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

        # codificar frame para JPEG com qualidade melhorada (PC bom pode suportar)
        _, img_encoded = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
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
        
        t_start = time.time()
        try:
            resp = requests.post(url, files=files, timeout=8)
        except Exception as e:
            if self.debug:
                print(f"[ERR] Erro ao enviar imagem para detect endpoint: {e}")
            return {"predictions": [], "time_ms": 0}

        t_elapsed = (time.time() - t_start) * 1000  # converter para ms

        if resp.status_code != 200:
            if self.debug:
                print(f"[DEBUG] detect endpoint HTTP {resp.status_code}: {resp.text}")
            return {"predictions": [], "time_ms": t_elapsed}

        try:
            j = resp.json()
            j["time_ms"] = t_elapsed  # adicionar tempo da requisição
        except Exception:
            if self.debug:
                print("[DEBUG] não foi possível interpretar JSON da resposta detect")
            return {"predictions": [], "time_ms": t_elapsed}

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

    def run(self, camera_id=0, skip_frames=2):
        """
        skip_frames: enviar 1 frame a cada N capturados (reduz carga API)
        Para PC bom: skip_frames=2 (envia metade dos frames)
        Para PC excelente: skip_frames=1 (envia todos os frames, máxima detecção)
        Para PC lento: aumente para 5-10
        """
        print(f"[CAM] Abrindo camera {camera_id}...")
        cap = cv2.VideoCapture(camera_id)

        if not cap.isOpened():
            print("[ERR] ERRO: Não foi possível abrir a câmera!")
            sys.exit(1)

        print("[OK] Camera aberta!")
        print(f"[INFO] Skip: 1 frame a cada {skip_frames} | Q=sair | D=diminuir conf | A=aumentar conf")
        print("[INFO] Para PC muito lento, aumente skip_frames no código\n")

        frame_count = 0
        last_result = {"predictions": []}
        
        # criar janela e maximizar
        window_name = "Detecção de EPIs (Roboflow API Nova)"
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, 1280, 960)  # janela grande
        
        # monitorar performance
        fps_times = []
        api_times = []
        t_start_overall = time.time()

        while True:
            ret, frame = cap.read()
            if not ret:
                print("[ERR] Falha ao capturar frame")
                break

            frame_count += 1
            
            # registrar tempo de captura (FPS)
            t_frame = time.time()
            if fps_times:
                fps_times.append(t_frame - fps_times[-1])
                if len(fps_times) > 30:
                    fps_times.pop(0)

            # enviar para API só a cada skip_frames frames
            if frame_count % skip_frames == 0:
                # redimensionar antes de enviar (melhor resolução para PC bom)
                frame_small = cv2.resize(frame, (480, 360))  # 50% maior que antes
                result = self.predict(frame_small)
                
                # registrar tempo da API
                if "time_ms" in result:
                    api_times.append(result["time_ms"])
                    if len(api_times) > 30:
                        api_times.pop(0)
                
                if result.get("predictions"):
                    last_result = result
            else:
                result = last_result

            # Desenhar resultado
            frame = self.draw_detections(frame, result)

            # desenhar informações de status (confiança atual, frame count)
            status = f"conf={self.confidence:.2f} | frame {frame_count}"
            cv2.putText(frame, status, (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

            # calcular e mostrar FPS e tempo da API
            if fps_times:
                avg_fps = 1.0 / (sum(fps_times) / len(fps_times)) if fps_times else 0
                fps_text = f"FPS: {avg_fps:.1f}"
                cv2.putText(frame, fps_text, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            
            if api_times:
                avg_api = sum(api_times) / len(api_times)
                api_text = f"API: {avg_api:.0f}ms"
                cv2.putText(frame, api_text, (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 200, 255), 1)

            cv2.imshow(window_name, frame)

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
    detector = EPIDetector(API_KEY, MODEL_ID, CONFIDENCE, debug=False)  # False para menos verbosidade

    # skip_frames: aumentado para 4 (API lenta = enviar menos frames)
    # Com API 1500ms: skip_frames=4 = ~1 requisição a cada 4 frames (~20 req/seg max)
    # Se ficar lento, aumente para 5-6
    detector.run(skip_frames=4)


if __name__ == "__main__":
    main()
