"""
Detección de regiones de interés en actas (paso 3 del pipeline).

Usa Ultralytics YOLO para localizar las regiones definidas en la propuesta:
    tabla_resultados, total_votos_emitidos, total_ciudadanos, firmas, observaciones,
    numero_mesa.

Entrena: python detect.py train --data ../../configs/actas.yaml --epochs 100
Infiere: python detect.py predict --weights runs/detect/train/weights/best.pt \
                                   --source ../../data/processed
"""
from __future__ import annotations

import argparse
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s",
                    datefmt="%H:%M:%S")
log = logging.getLogger("detect")

# Clases de regiones a detectar (deben coincidir con configs/actas.yaml)
CLASES = [
    "numero_mesa",
    "tabla_resultados",
    "total_votos_emitidos",
    "total_ciudadanos",
    "votos_blancos",
    "votos_nulos",
    "votos_impugnados",
    "firmas_miembros",
    "observaciones",
]


def _load_yolo(weights: str):
    try:
        from ultralytics import YOLO
    except ImportError as exc:
        raise SystemExit("Falta ultralytics. Instala: pip install ultralytics") from exc
    return YOLO(weights)


def train(args):
    model = _load_yolo(args.weights or "yolov8n.pt")
    log.info("Entrenando con data=%s, epochs=%s", args.data, args.epochs)
    model.train(data=args.data, epochs=args.epochs, imgsz=args.imgsz,
                batch=args.batch, project="runs/detect", name="train")
    log.info("Entrenamiento finalizado. Pesos en runs/detect/train/weights/best.pt")


def predict(args):
    model = _load_yolo(args.weights)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    log.info("Detectando regiones en: %s", args.source)
    results = model.predict(source=args.source, conf=args.conf, save=True,
                            project=str(out), name="pred")
    # Exporta las cajas a un JSON por imagen para el paso de OCR
    import json
    for r in results:
        det = []
        for b in r.boxes:
            cls = int(b.cls[0])
            det.append({
                "clase": CLASES[cls] if cls < len(CLASES) else str(cls),
                "conf": float(b.conf[0]),
                "xyxy": [float(x) for x in b.xyxy[0].tolist()],
            })
        stem = Path(r.path).stem
        (out / f"{stem}.json").write_text(json.dumps(det, ensure_ascii=False, indent=2),
                                          encoding="utf-8")
    log.info("Detecciones (JSON + imágenes) en: %s", out)


def main():
    ap = argparse.ArgumentParser(description="Detección de regiones en actas (YOLO)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    t = sub.add_parser("train")
    t.add_argument("--data", default="../../configs/actas.yaml")
    t.add_argument("--weights", default="yolov8n.pt")
    t.add_argument("--epochs", type=int, default=100)
    t.add_argument("--imgsz", type=int, default=1280)
    t.add_argument("--batch", type=int, default=8)
    t.set_defaults(func=train)

    p = sub.add_parser("predict")
    p.add_argument("--weights", required=True)
    p.add_argument("--source", default="../../data/processed")
    p.add_argument("--out", default="../../data/detections")
    p.add_argument("--conf", type=float, default=0.25)
    p.set_defaults(func=predict)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
