@echo off
REM ============================================================================
REM  EJECUTAR.bat — Corre TODO el pipeline de actas ONPE sin asistente.
REM
REM  Uso:   doble clic  (corre 10 actas)
REM         EJECUTAR.bat 50            (corre 50 actas)
REM         EJECUTAR.bat 10 nopause    (sin pausa final; para scripts/CI)
REM
REM  Etapas: muestreo+descarga -> PDF a PNG -> preproceso -> recorte por
REM  plantilla registrada -> OCR -> evaluacion vs oficial -> estadistica.
REM  Salidas en data\corrida\  (resultados: data\corrida\analisis.json)
REM
REM  Requisitos (ya instalados en esta maquina): Python de C:\ProgramData\
REM  anaconda3 con curl_cffi, pymupdf, opencv, easyocr. Internet para
REM  descargar actas (y modelos de EasyOCR la primera vez).
REM ============================================================================
setlocal
chcp 65001 >nul

REM --- entorno Python (obligatorio en esta maquina: sin PYTHONHOME el
REM     interprete toma la carpeta actual como prefix y no arranca) ---------
set "PYTHONHOME=C:\ProgramData\anaconda3"
set "PYTHONUTF8=1"
set "PY=C:\ProgramData\anaconda3\python.exe"

REM --- cuantas actas (parametro 1; por defecto 10) --------------------------
set "N=%~1"
if "%N%"=="" set "N=10"

cd /d "%~dp0"
echo.
echo  ============================================================
echo   PIPELINE ACTAS ONPE EG2026  -  %N% actas (muestreo nacional)
echo  ============================================================
echo.

echo [1/7] Muestreo aleatorio nacional + descarga de PDFs y votos oficiales...
pushd src\scraper
"%PY%" muestreo_nacional.py --n %N% --seed 2026 --out ..\..\data\corrida
if errorlevel 1 goto :error
popd

echo [2/7] Convirtiendo PDF a PNG (300 DPI)...
pushd src\scraper
"%PY%" pdf_to_images.py --in ..\..\data\corrida\raw_pdf --out ..\..\data\corrida\raw_img --dpi 300
if errorlevel 1 goto :error
popd

echo [3/7] Preprocesando (deskew + CLAHE + denoise)...
pushd src\preprocessing
"%PY%" preprocess.py --in ..\..\data\corrida\raw_img --out ..\..\data\corrida\processed
if errorlevel 1 goto :error
popd

echo [4/7] Recortando 46 regiones por plantilla registrada (fiduciales)...
pushd src\detection
"%PY%" regiones_plantilla.py --in ..\..\data\corrida\processed --out ..\..\data\corrida\crops
if errorlevel 1 goto :error
popd

REM las actas electronicas (STAE, 2 paginas -> carpetas _p0/_p1) no van al OCR
for /d %%D in ("data\corrida\crops\*_p0") do rd /s /q "%%D"
for /d %%D in ("data\corrida\crops\*_p1") do rd /s /q "%%D"

echo [5/7] Leyendo con OCR (aprox. 1 min por acta en CPU; paciencia)...
pushd src\pipeline
"%PY%" piloto_10_actas.py --modo limpio --crops ..\..\data\corrida\crops --gt ..\..\data\corrida\ground_truth --out ..\..\data\corrida\salida
if errorlevel 1 goto :error

echo [6/7] Evaluando contra los votos oficiales (regla celda-vacia = 0)...
"%PY%" evaluar_salidas.py --salidas ..\..\data\corrida\salida --gt ..\..\data\corrida\ground_truth --regla-cero --out ..\..\data\corrida\evaluacion.json
if errorlevel 1 goto :error

echo [7/7] Estadistica: exactitud con IC 95%% (bootstrap por acta)...
"%PY%" analisis_estadistico.py --eval ..\..\data\corrida\evaluacion.json --muestra ..\..\data\corrida\muestra.json --out ..\..\data\corrida\analisis.json
if errorlevel 1 goto :error
popd

echo.
echo  ============================================================
echo   LISTO. Resultados en data\corrida\ :
echo     - analisis.json     (exactitud + IC 95%%)
echo     - evaluacion.json   (detalle por acta y por campo)
echo     - salida\*.json     (lectura estructurada de cada acta)
echo  ============================================================
if /i not "%~2"=="nopause" pause
exit /b 0

:error
popd 2>nul
echo.
echo  *** ERROR en la etapa anterior. Revisa el mensaje de arriba. ***
echo  Pistas: internet activo? EasyOCR descarga modelos la 1ra vez.
if /i not "%~2"=="nopause" pause
exit /b 1
