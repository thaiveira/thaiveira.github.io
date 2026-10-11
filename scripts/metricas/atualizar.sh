#!/bin/bash
cd "$(dirname "$0")" || exit 1
source ../.venv/bin/activate
python3 scripts/metricas/gerar_metricas.py
