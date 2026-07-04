#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# Sube el proyecto onpe_actas a GitHub.
# Requisitos: git instalado y una cuenta de GitHub.
#
#   1) Crea el repo vacío en https://github.com/new
#      Nombre sugerido: onpe_actas  (Public)
#   2) Ejecuta este script desde la carpeta onpe_actas:
#         bash SUBIR_A_GITHUB.sh
# ---------------------------------------------------------------------------
set -e

USUARIO="carlosperez100"          # <-- cambia si usas otro usuario
REPO="onpe_actas"

echo ">> Inicializando repositorio git..."
git init -b main

echo ">> Agregando archivos..."
git add .
git commit -m "Proyecto inicial: detección y reconocimiento de actas ONPE 2026"

echo ">> Conectando con GitHub (https)..."
git remote add origin "https://github.com/${USUARIO}/${REPO}.git" 2>/dev/null || \
  git remote set-url origin "https://github.com/${USUARIO}/${REPO}.git"

echo ">> Subiendo a GitHub..."
git push -u origin main

echo ""
echo "Listo. Repo: https://github.com/${USUARIO}/${REPO}"
echo "Si pide credenciales, usa un Personal Access Token como contraseña."
