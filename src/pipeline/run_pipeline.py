"""
Pipeline completo end-to-end (paso 1 al 5 de la propuesta).

    Acta (PDF/imagen) -> Preprocesamiento -> Detección de regiones ->
    Reconocimiento (OCR) -> Datos estructurados (JSON)

Produce por cada acta un JSON con la forma:
    {
      "mesa": "009655",
      "departamento": "...", "provincia": "...", "distrito": "...",
      "resultados": [{"lista": 1, "partido": "...", "votos": 3}, ...],
      "votos_blancos": 22, "votos_nulos": 11, "votos_impugnados": 10,
      "total_emitidos": 208, "total_ciudadanos_que_votaron": 208
    }

Uso:
    python run_pipeline.py --source ../../data/raw_img \
                           --weights ../detection/runs/detect/train/weights/best.pt \
                           --out ../../data/salida
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

import cv2

# permite importar los módulos hermanos sin instalar el paquete
sys.path.append(str(Path(__file__).resolve().parents[1]))
from preprocessing.preprocess import preprocess_image  # noqa: E402
from recognition.ocr import OCR  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s",
                    datefmt="%H:%M:%S")
log = logging.getLogger("pipeline")

# regiones cuyo valor es un número único
CAMPOS_NUMERICOS = {
    "numero_mesa": "mesa",
    "total_votos_emitidos": "total_emitidos",
    "total_ciudadanos": "total_ciudadanos_que_votaron",
    "votos_blancos": "votos_blancos",
    "votos_nulos": "votos_nulos",
    "votos_impugnados": "votos_impugnados",
}


def _crop(img, xyxy):
    x1, y1, x2, y2 = [int(v) for v in xyxy]
    return img[max(0, y1):y2, max(0, x1):x2]


def procesar_acta(img_path: Path, model, ocr: OCR) -> dict:
    raw = cv2.imread(str(img_path))
    if raw is None:
        raise FileNotFoundError(img_path)
    proc = preprocess_image(raw)  # gris realzado
    proc_bgr = cv2.cvtColor(proc, cv2.COLOR_GRAY2BGR)

    detections = model.predict(source=proc_bgr, conf=0.25, verbose=False)[0]
    from detection.detect import CLASES

    salida: dict = {"archivo": img_path.name, "resultados": []}
    for b in detections.boxes:
        cls = int(b.cls[0])
        clase = CLASES[cls] if cls < len(CLASES) else str(cls)
        crop = _crop(raw, b.xyxy[0].tolist())
        if crop.size == 0:
            continue
        if clase in CAMPOS_NUMERICOS:
            salida[CAMPOS_NUMERICOS[clase]] = ocr.leer_numero(crop)
        elif clase == "tabla_resultados":
            # la tabla se reconoce fila por fila en un módulo aparte;
            # aquí guardamos solo el texto bruto como referencia
            salida["resultados_raw"] = ocr.leer_texto(crop)
        elif clase == "observaciones":
            salida["observaciones"] = ocr.leer_texto(crop)
    return salida


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", type=Path, default=Path("../../data/raw_img"))
    ap.add_argument("--weights", required=True)
    ap.add_argument("--out", type=Path, default=Path("../../data/salida"))
    args = ap.parse_args()

    try:
        from ultralytics import YOLO
    except ImportError as exc:
        raise SystemExit("Falta ultralytics. Instala: pip install ultralytics") from exc

    model = YOLO(args.weights)
    ocr = OCR()
    args.out.mkdir(parents=True, exist_ok=True)

    imgs = [p for p in args.source.iterdir() if p.suffix.lower() in {".png", ".jpg", ".jpeg"}]
    log.info("Procesando %s actas...", len(imgs))
    for p in imgs:
        try:
            res = procesar_acta(p, model, ocr)
            (args.out / f"{p.stem}.json").write_text(
                json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
            log.info("OK %s", p.name)
        except Exception as exc:  # noqa: BLE001
            log.error("Error en %s: %s", p.name, exc)
    log.info("Resultados estructurados en: %s", args.out)


if __name__ == "__main__":
    main()
