#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script profissional para rodar modelo YOLOv11 do Roboflow com Webcam
- Detecção de EPIs em tempo real
- Otimizado para CPU
- Cores: VERMELHO (perigo), VERDE (segurança)
- Usa API REST do Roboflow (compatível com Python 3.13)
"""

import cv2
import numpy as np
import json
import urllib.request
import urllib.error
from pathlib import Path
import sys
from datetime import datetime


class EPIDetector:
    """Detector de EPIs com Roboflow API REST + Webcam"""
    
    # Classes que indicam PERIGO (vermelho)
    DANGER_CLASSES = {'no-helmet', 'no-glove', 'no-vest', 'no-goggles'}
    
    # Classes que indicam SEGURANÇA (verde)
    SAFETY_CLASSES = {'helmet', 'glove', 'vest', 'goggles'}
    
    # Cores em BGR (OpenCV usa BGR, não RGB)
    COLOR_RED = (0, 0, 255)      # Perigo
    COLOR_GREEN = (0, 255, 0)    # Segurança
    COLOR_YELLOW = (0, 255, 255) # Neutro
    
    def __init__(self, api_key: str, model_id: str, confidence: float = 0.5):
        """
        Inicializar detector
        
        Args:
            api_key: Sua chave API Roboflow
            model_id: ID do seu modelo (ex: "safety-equipment-detection/1")
            confidence: Threshold de confiança (0-1)
        """
        self.api_key = api_key
        self.model_id = model_id
        self.confidence = confidence
        
        # URL base do Roboflow
        self.api_url = f"https://detect.roboflow.com/{model_id}"
        
        print(f"[OK] Detector configurado")
        print(f"  Model: {model_id}")
        print(f"  API: {self.api_url}")
        print()
    
    def predict(self, frame_bytes: bytes) -> dict:
        """
        Fazer predição via API REST do Roboflow
        
        Args:
            frame_bytes: Imagem em bytes (JPEG)
            
        Returns:
            dict com predições
        """
        try:
            # Preparar requisição
            url = f"{self.api_url}?api_key={self.api_key}&confidence={self.confidence}"
            
            # Enviar imagem
            req = urllib.request.Request(url, data=frame_bytes, method='POST')
            req.add_header('Content-Type', 'application/octet-stream')
            
            # Fazer requisição com timeout
            with urllib.request.urlopen(req, timeout=10) as response:
                result = json.loads(response.read().decode())
                return result
                
        except urllib.error.HTTPError as e:
            print(f"[ERR] Erro HTTP {e.code}: ", end="")
            if e.code == 401:
                print("Chave API invalida!")
            elif e.code == 404:
                print("Model ID nao encontrado!")
            else:
                print(e.reason)
            return {"predictions": []}
        except urllib.error.URLError as e:
            print(f"[ERR] Erro de conexao: {e.reason}")
            return {"predictions": []}
        except Exception as e:
            print(f"[ERR] Erro: {e}")
            return {"predictions": []}
        
    def get_color_for_class(self, class_name: str) -> tuple:
        """Retornar cor baseada na classe"""
        class_lower = class_name.lower().strip()
        
        if class_lower in self.DANGER_CLASSES:
            return self.COLOR_RED
        elif class_lower in self.SAFETY_CLASSES:
            return self.COLOR_GREEN
        else:
            return self.COLOR_YELLOW
    
    def draw_detections(self, frame: np.ndarray, results: dict) -> np.ndarray:
        """Desenhar detecções no frame com cores apropriadas"""
        
        frame_h, frame_w = frame.shape[:2]
        
        if 'predictions' not in results or not results['predictions']:
            return frame
        
        # Contar classes para estatísticas
        class_counts = {}
        danger_count = 0
        
        for pred in results['predictions']:
            # Extrair coordenadas
            x = pred.get('x', 0)
            y = pred.get('y', 0)
            width = pred.get('width', 0)
            height = pred.get('height', 0)
            confidence = pred.get('confidence', 0)
            class_name = pred.get('class', 'unknown')
            
            # Converter para coordenadas de caixa
            x1 = int(x - width / 2)
            y1 = int(y - height / 2)
            x2 = int(x + width / 2)
            y2 = int(y + height / 2)
            
            # Garantir que está dentro do frame
            x1 = max(0, x1)
            y1 = max(0, y1)
            x2 = min(frame_w, x2)
            y2 = min(frame_h, y2)
            
            # Obter cor
            color = self.get_color_for_class(class_name)
            
            # Desenhar caixa
            thickness = 2
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness)
            
            # Desenhar rótulo
            label = f"{class_name}: {confidence:.2f}"
            label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)
            
            # Fundo do texto
            cv2.rectangle(
                frame,
                (x1, y1 - label_size[1] - 8),
                (x1 + label_size[0] + 4, y1),
                color,
                -1
            )
            
            # Texto
            cv2.putText(
                frame,
                label,
                (x1 + 2, y1 - 4),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                1
            )
            
            # Contabilizar
            class_counts[class_name] = class_counts.get(class_name, 0) + 1
            if class_name.lower() in self.DANGER_CLASSES:
                danger_count += 1
        
        # Desenhar estatísticas
        self._draw_stats(frame, class_counts, danger_count)
        
        return frame
    
    def run(self, camera_id: int = 0, skip_frames: int = 2):
        """
        Rodar detecção com webcam
        
        Args:
            camera_id: ID da câmera (0 = padrão)
            skip_frames: Pular N frames entre detecções (para otimização em CPU)
        """
        
        print(f"[CAM] Abrindo camera {camera_id}...")
        cap = cv2.VideoCapture(camera_id)
        
        if not cap.isOpened():
            print(f"[ERR] Erro: Camera {camera_id} nao encontrada")
            sys.exit(1)
        
        # Configurar câmera
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 30)
        
        print("[OK] Camera aberta!")
        print("[INF] Pressione 'Q' para sair, 'S' para salvar frame")
        print()
        
        frame_count = 0
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    print("❌ Erro ao ler frame")
                    break
                
                frame_count += 1
                
                # Pular frames para otimizar CPU
                if frame_count % skip_frames != 0:
                    cv2.imshow("Deteccao de EPIs - YOLOv11 (Roboflow)", frame)
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord('q') or key == ord('Q'):
                        print("\n👋 Encerrando...")
                        break
                    continue
                
                print(f"[FRAME] {frame_count}... ", end="", flush=True)
                
                # Codificar frame como JPEG
                success, buffer = cv2.imencode('.jpg', frame)
                if not success:
                    print("[ERR] Erro ao codificar")
                    continue
                
                frame_bytes = buffer.tobytes()
                
                # Fazer predicao via API
                results = self.predict(frame_bytes)
                print("[OK]", flush=True)
                
                # Desenhar detecções
                frame = self.draw_detections(frame, results)
                
                # Mostrar frame
                cv2.imshow("Deteccao de EPIs - YOLOv11 (Roboflow)", frame)
                
                # Controles
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q') or key == ord('Q'):
                    print("\n[EXIT] Encerrando...")
                    break
                elif key == ord('s') or key == ord('S'):
                    filename = f"deteccao_{frame_count}.jpg"
                    cv2.imwrite(filename, frame)
                    print(f"\n[SAVE] Frame salvo: {filename}")
        
        except KeyboardInterrupt:
            print("\n\n[INT] Interrompido pelo usuario")
        
        finally:
            print("[CLEAN] Limpando recursos...")
            cap.release()
            cv2.destroyAllWindows()
            print("[DONE] Pronto!")


def main():
    """Função principal"""
    
    print("="*70)
    print("[*] DETECTOR DE EPIs COM YOLOV11 (Roboflow - API REST)")
    print("="*70)
    print()
    
    # ⚙️ CONFIGURAR AQUI
    API_KEY = "seu_api_key_aqui"          # ← SUBSTITUIR
    MODEL_ID = "seu_model_id_aqui/1"      # ← SUBSTITUIR (ex: "safety-equipment-detection/1")
    CONFIDENCE = 0.5                       # Threshold (0-1)
    SKIP_FRAMES = 2                        # Pular frames para otimizar
    
    # Validar configuração
    if "seu_api_key_aqui" in API_KEY:
        print("[ERR] ERRO: Configure sua API_KEY do Roboflow!")
        print()
        print("Como conseguir:")
        print("1. Ir para: https://app.roboflow.com/settings/account")
        print("2. Copiar 'Private API Key'")
        print("3. Substituir em API_KEY = '...'")
        print()
        sys.exit(1)
    
    if "seu_model_id_aqui" in MODEL_ID:
        print("[ERR] ERRO: Configure seu MODEL_ID do Roboflow!")
        print()
        print("Como conseguir:")
        print("1. Ir para: https://app.roboflow.com/projects")
        print("2. Selecionar seu projeto")
        print("3. Ver 'Model Deployment' -> 'API Reference'")
        print("4. Copiar format: 'projeto-xyz/1'")
        print()
        sys.exit(1)
    
    print(f"[CONFIG] Configuracao:")
    print(f"   API Key: {API_KEY[:10]}...")
    print(f"   Model ID: {MODEL_ID}")
    print(f"   Confianca: {CONFIDENCE}")
    print(f"   Skip Frames: {SKIP_FRAMES}")
    print()
    
    # Criar detector
    detector = EPIDetector(
        api_key=API_KEY,
        model_id=MODEL_ID,
        confidence=CONFIDENCE
    )
    
    # Rodar
    detector.run(skip_frames=SKIP_FRAMES)


if __name__ == "__main__":
    main()
