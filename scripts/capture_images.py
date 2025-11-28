#!/usr/bin/env python3
"""
Capture utility for dataset collection.

Usage:
  - Automatic mode: capture frames every N seconds and save (useful to collect many images quickly).
  - Interactive (tagged) mode: press `c` to capture a frame, then press a class key (1..N) to tag.

The script saves images to `dataset/images/` and appends rows to `dataset/labels.csv` with columns: filename,class

Designed for classes: helmet,glasses,vest,gloves by default (keys 1-4).
"""
import cv2
import argparse
import time
from pathlib import Path
import csv
from datetime import datetime


DEFAULT_CLASSES = ["helmet", "glasses", "vest", "gloves"]


def ensure_dirs(output_dir: Path):
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "images").mkdir(exist_ok=True)


def append_label(csv_path: Path, filename: str, label: str):
    header = ["filename", "class"]
    write_header = not csv_path.exists()
    with open(csv_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow(header)
        writer.writerow([filename, label])


def auto_mode(args):
    out = Path(args.output_dir)
    ensure_dirs(out)
    csv_path = out / "labels.csv"

    cap = cv2.VideoCapture(args.camera)
    if not cap.isOpened():
        print("Erro: não foi possível abrir a câmera.")
        return

    print(f"Capturando automaticamente a cada {args.interval}s. Pressione Ctrl+C para parar.")
    try:
        count = 0
        while args.max is None or count < args.max:
            ret, frame = cap.read()
            if not ret:
                print("Falha ao ler frame; saindo.")
                break

            ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            fname = f"img_{ts}.jpg"
            path = out / "images" / fname
            cv2.imwrite(str(path), frame)
            append_label(csv_path, f"images/{fname}", "")
            count += 1
            time.sleep(args.interval)

    except KeyboardInterrupt:
        print("Captura automática interrompida pelo usuário.")
    finally:
        cap.release()


def tagged_mode(args):
    out = Path(args.output_dir)
    ensure_dirs(out)
    csv_path = out / "labels.csv"

    classes = args.classes.split(",") if args.classes else DEFAULT_CLASSES
    classes = [c.strip() for c in classes]

    print("Modo interativo: pressione 'c' para capturar, depois pressione a tecla do número da classe para tag (1..N). Pressione 'q' para sair.")
    print("Classes:")
    for i, c in enumerate(classes, start=1):
        print(f"  {i}: {c}")

    cap = cv2.VideoCapture(args.camera)
    if not cap.isOpened():
        print("Erro: não foi possível abrir a câmera.")
        return

    last_frame = None
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Falha ao ler frame; saindo.")
                break

            display = frame.copy()
            cv2.putText(display, "Press 'c' capture, 'q' quit", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)
            cv2.imshow("Capture - Interactive", display)
            key = cv2.waitKey(1) & 0xFF

            if key == ord("q"):
                break
            if key == ord("c"):
                # capture
                ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                fname = f"img_{ts}.jpg"
                path = out / "images" / fname
                cv2.imwrite(str(path), frame)
                print(f"Capturado: {fname} — aguarde tag (pressione 1..{len(classes)} para classificar, qualquer outra para deixar em branco)")
                # wait for class key
                while True:
                    k = cv2.waitKey(0) & 0xFF
                    if k == 255:
                        continue
                    if k == ord("q"):
                        # quit tagging and exit
                        label = ""
                        append_label(csv_path, f"images/{fname}", label)
                        return
                    if k >= ord("1") and k < ord("1") + len(classes):
                        idx = k - ord("1")
                        label = classes[idx]
                        append_label(csv_path, f"images/{fname}", label)
                        print(f"Imagem {fname} etiquetada como: {label}")
                        break
                    else:
                        # any other key -> blank label
                        append_label(csv_path, f"images/{fname}", "")
                        print(f"Imagem {fname} salva sem etiqueta.")
                        break

    finally:
        cap.release()
        cv2.destroyAllWindows()


def main():
    p = argparse.ArgumentParser(description="Capture images for dataset (automatic or interactive).")
    p.add_argument("--output-dir", default="dataset", help="Base output directory (default: dataset)")
    p.add_argument("--mode", choices=["auto","tagged"], default="auto", help="Capture mode: auto or tagged")
    p.add_argument("--interval", type=float, default=2.0, help="Interval seconds for auto mode")
    p.add_argument("--max", type=int, default=None, help="Max number of images to capture (auto mode)")
    p.add_argument("--camera", type=int, default=0, help="Camera index (default 0)")
    p.add_argument("--classes", type=str, default=",".join(DEFAULT_CLASSES), help="Comma-separated class names for tagged mode")

    args = p.parse_args()

    if args.mode == "auto":
        auto_mode(args)
    else:
        tagged_mode(args)


if __name__ == "__main__":
    main()
