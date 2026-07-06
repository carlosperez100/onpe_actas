# onpe_actas — Detección y Reconocimiento Automático de Resultados Electorales en Actas de Escrutinio (ONPE 2026 – 1ª Vuelta)

**Maestría en Inteligencia Artificial · Visión por Computadora · Grupo 3 · Sección B · 2026‑1**

Sistema de Visión por Computadora que **detecta las regiones de interés** de las
actas de escrutinio de la ONPE y **reconoce los valores numéricos** (totales,
votos por organización política, votos en blanco/nulos/impugnados), para
transformar la información visual en **datos estructurados (JSON)** listos para
análisis y auditoría.

> 🗳️ **Resumen visual del proyecto** (pipeline, resultados con IC 95%,
> hallazgos y entregables):
> **https://claude.ai/code/artifact/f8bc673f-349c-43a1-9917-a08c532980f7**
>
> ▶️ **Correrlo tú mismo sin asistente:** doble clic en `EJECUTAR.bat`
> (guía completa en [docs/COMO_CORRERLO.md](docs/COMO_CORRERLO.md)) ·
> 📄 Paper IEEE/WVC bilingüe en [paper/](paper/) ·
> 📊 Evaluación nacional en [docs/EVALUACION_NACIONAL.md](docs/EVALUACION_NACIONAL.md)

---

## Integrantes

- Josemanuel Rossy Cañari Palante — jose.canari@outlook.com.pe
- Kenny Asto Hinostroza — kenny.asto.hinostroza@gmail.com
- Melissa Dessire Aylas Barranca — melissa.aylas@gmail.com
- Carlos Pérez Pérez

---

## 1. Problema

Las actas de escrutinio son la fuente oficial de los resultados por mesa, pero
se publican en **formato visual** (PDF/imagen), lo que impide su procesamiento
automático a gran escala. La extracción manual es lenta, propensa a errores de
digitación y difícil de auditar. Además, las imágenes presentan ruido, baja
resolución, inclinación, sellos y firmas que complican el reconocimiento.

## 2. Objetivo

Desarrollar un sistema basado en Visión por Computadora capaz de **detectar y
reconocer automáticamente** los resultados electorales de las actas de las
Elecciones Generales del Perú 2026.

**Objetivos específicos**

1. Construir un dataset de actas obtenidas del portal oficial de la ONPE.
2. Detectar las regiones de interés mediante *Object Detection* (YOLOv8).
3. Reconocer los valores numéricos registrados (OCR de dígitos manuscritos).
4. Transformar la información en datos estructurados (JSON).
5. Evaluar el sistema con métricas de detección y reconocimiento.

## 3. Dataset

**Actas de Escrutinio – Elecciones Generales del Perú 2026 (1ª Vuelta).**

- **Fuente:** Portal de Resultados Electorales de la ONPE (actas oficiales en
  PDF/imagen).
- **Recolección:** descarga automatizada con el scraper de este repo
  (`src/scraper/download_actas.py`).
- **Contenido aprovechable:** número de mesa, resultados por organización
  política, votos blancos/nulos/impugnados, total de votos emitidos, total de
  ciudadanos que votaron, firmas de miembros de mesa.

### Relevancia para la tarea
Las actas tienen regiones claramente delimitadas (tabla de resultados, totales,
firmas, observaciones) ideales para **detección**, y campos manuscritos
(números y totales) que requieren **reconocimiento**. Aplicación real:
automatización del procesamiento documental electoral y apoyo a auditorías.

### Limitaciones y desafíos
- **Calidad de imagen:** resoluciones distintas, inclinación, contraste variable.
- **Escritura manuscrita:** estilos diversos, trazos poco legibles, números
  parciales.
- **Ruido visual:** sellos sobre los campos, firmas cercanas, marcas de impresión.
- **Desbalance:** partidos con pocos votos, predominio de valores pequeños.
- **Etiquetado:** el dataset no trae anotaciones de detección; se generan a mano.
- **Complejidad documental:** múltiples formatos (presidencial vs. congresal).

## 4. Enfoque / Pipeline

```
1. ENTRADA            Acta digitalizada (PDF → imagen)
2. PREPROCESAMIENTO   Deskew · CLAHE · denoise · binarización/normalización
3. DETECCIÓN          YOLOv8 localiza regiones de interés
4. RECONOCIMIENTO     OCR (EasyOCR/Tesseract) sobre cada región
5. SALIDA             Datos estructurados (JSON) por acta
```

### Métricas de evaluación
- **Detección:** mAP, Precision, Recall (Ultralytics `val`).
- **Reconocimiento:** CER (Character Error Rate), WER (Word Error Rate).
- **Desempeño general:** exactitud por campo y por documento.

## 5. Motivación, supuestos, riesgos y restricciones

- **Motivación:** aplicar VC moderna a un problema documental real con impacto
  social (transparencia electoral).
- **Supuestos:** actas representativas, calidad suficiente, valores legibles.
- **Riesgos:** calidad insuficiente, errores en manuscrito, necesidad de muchas
  anotaciones, límites de hardware.
- **Restricciones:** tiempo de entrenamiento, recursos computacionales,
  disponibilidad parcial del dataset durante el proyecto.

---

## Estructura del repositorio

```
onpe_actas/
├── configs/actas.yaml            # clases y rutas para YOLO
├── data/                         # dataset (no versionado; se regenera)
│   ├── raw_pdf/  raw_img/  processed/  annotations/
├── clase_pdfs/                   # material/PDFs del curso (Teachlr)
├── notebooks/                    # exploración y experimentos
├── src/
│   ├── scraper/                  # descarga de actas + PDF→imagen
│   ├── preprocessing/            # deskew, CLAHE, denoise, binarización
│   ├── detection/                # entrenamiento e inferencia YOLO
│   ├── recognition/              # OCR de dígitos/manuscrito
│   ├── pipeline/                 # orquestación end-to-end
│   └── utils/                    # métricas (CER/WER, exactitud)
├── docs/                         # documentación del proyecto
├── requirements.txt
├── SUBIR_A_GITHUB.sh
└── README.md
```

## Instalación

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Uso rápido

```bash
# 1) Descargar actas de la ONPE
python src/scraper/download_actas.py --tipo presidencial --max 200 --out data/raw_pdf

# 2) Convertir PDF a imágenes
python src/scraper/pdf_to_images.py --in data/raw_pdf --out data/raw_img --dpi 300

# 3) Preprocesar
python src/preprocessing/preprocess.py --in data/raw_img --out data/processed

# 4) (tras anotar) Entrenar el detector
python src/detection/detect.py train --data configs/actas.yaml --epochs 100

# 5) Pipeline completo -> JSON estructurado
python src/pipeline/run_pipeline.py --source data/raw_img \
    --weights src/detection/runs/detect/train/weights/best.pt --out data/salida
```

## Ejemplo de salida (JSON)

```json
{
  "mesa": "009655",
  "departamento": "Ayacucho", "provincia": "Huamanga", "distrito": "Ayacucho",
  "resultados": [
    {"lista": 1, "partido": "Alianza ...", "votos": 3},
    {"lista": 2, "partido": "Partido X", "votos": 2}
  ],
  "votos_blancos": 22, "votos_nulos": 11, "votos_impugnados": 10,
  "total_emitidos": 208, "total_ciudadanos_que_votaron": 208
}
```

## Nota legal y de datos

Las actas son documentos públicos publicados por la ONPE. Este proyecto es
**académico**; el dataset se reconstruye localmente con el scraper y no se
versiona en el repositorio. Si los endpoints de la ONPE cambian, ajusta
`src/scraper/download_actas.py`.
