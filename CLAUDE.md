# CLAUDE.md — Guía para asistentes de IA en este repo

## Qué es
`onpe_actas`: sistema de Visión por Computadora para detectar regiones y
reconocer valores numéricos en actas de escrutinio de la ONPE 2026 (1ª vuelta).
Proyecto académico de la Maestría en IA — Visión por Computadora, Grupo 3, Sec. B.

## Arquitectura (pipeline)
1. `src/scraper/` — descarga de actas (curl_cffi + impersonate chrome) y PDF→PNG.
2. `src/preprocessing/` — deskew, CLAHE, denoise, binarización (OpenCV).
3. `src/detection/` — YOLOv8 (Ultralytics): train + predict. Clases en `configs/actas.yaml`.
4. `src/recognition/` — OCR (EasyOCR/Tesseract) de dígitos manuscritos y texto.
5. `src/pipeline/run_pipeline.py` — orquesta todo y emite JSON por acta.
6. `src/utils/metrics.py` — CER, WER, exactitud por campo.

## Convenciones
- Código y comentarios en español.
- Rutas relativas a la raíz del repo en los ejemplos del README.
- El dataset NO se versiona (ver `.gitignore`); se regenera con el scraper.
- Las clases de detección deben coincidir entre `detect.py::CLASES` y `configs/actas.yaml`.

## Endpoints ONPE (frágiles)
Si la descarga falla, revisar `BASE_URL`/`build_acta_url` en
`src/scraper/download_actas.py`. ONPE cambia rutas entre procesos.

## Cómo correr rápido
Ver sección "Uso rápido" del README. Sin pesos entrenados, el pipeline requiere
primero anotar y entrenar el detector (`detect.py train`).
