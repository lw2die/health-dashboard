#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuración global del Monitor de Longevidad v4.0
Centraliza todas las constantes y parámetros del sistema
"""

from pathlib import Path

# ============================================================================
# RUTAS DEL SISTEMA
# ============================================================================

BASE_DIR = Path(r"H:\My Drive\HealthConnect Exports\SCRIPT")
INPUT_DIR = BASE_DIR.parent  # H:\My Drive\HealthConnect Exports
CACHE_JSON = BASE_DIR / "cache_datos.json"
OUTPUT_HTML = BASE_DIR / "index.html"
GIT_REPO = BASE_DIR

# ============================================================================
# PARÁMETROS DEL USUARIO
# ============================================================================

EDAD = 61
ALTURA_CM = 177
FC_REPOSO = 55
FC_MAX = 220 - EDAD  # 159 bpm
PESO_OBJETIVO = 79.0

# ============================================================================
# CONFIGURACIÓN DE MÉTRICAS
# ============================================================================

# PAI (Personal Activity Intelligence)
PAI_OBJETIVO_SEMANAL = 100
PAI_VENTANA_DIAS = 7

# VO2max
VO2MAX_EXCELENTE = 35  # ml/kg/min para edad 61
VO2MAX_BUENO = 30

# Training Stress Balance (TSB)
TSB_CTL_DIAS = 42  # Chronic Training Load (fitness de largo plazo)
TSB_ATL_DIAS = 7   # Acute Training Load (fatiga aguda)
TSB_OPTIMO_MIN = -10
TSB_OPTIMO_MAX = 10

# Sueño
SUENO_OBJETIVO_HORAS = 7
SUENO_MINIMO_HORAS = 6

# ============================================================================
# ZONAS DE FRECUENCIA CARDÍACA
# ============================================================================

ZONAS_FC = {
    "recuperacion": (0.00, 0.60),      # < 60% FC_max
    "aerobico": (0.60, 0.70),          # 60-70% FC_max
    "tempo": (0.70, 0.80),             # 70-80% FC_max
    "umbral": (0.80, 0.90),            # 80-90% FC_max
    "vo2max": (0.90, 1.00)             # > 90% FC_max
}

# ============================================================================
# CONFIGURACIÓN DE PROCESAMIENTO
# ============================================================================

# Archivos a procesar
ARCHIVO_PREFIX = "health_data"
ARCHIVO_EXTENSION = ".json"

# Estrategia de limpieza
LIMPIEZA_AGRESIVA_FULL = True  # Archivos FULL: 1 sesión/día
LIMPIEZA_DIFF = False          # Archivos DIFF: sin limpieza

# ============================================================================
# CONFIGURACIÓN DE VISUALIZACIÓN
# ============================================================================

# Gráficos
GRAFICOS_DIAS_HISTORICO = 30  # Mostrar últimos 30 días en gráficos

# Colores (tema oscuro GitHub)
COLOR_EXCELENTE = "#3fb950"
COLOR_BUENO = "#d29922"
COLOR_MALO = "#f85149"
COLOR_PRIMARIO = "#58a6ff"
COLOR_FONDO = "#0d1117"

# ============================================================================
# CONFIGURACIÓN DE EJECUCIÓN
# ============================================================================

# Loop principal
INTERVALO_MINUTOS = 30  # Ejecutar cada 30 minutos

# GitHub Pages
GITHUB_REPO_URL = "https://lw2die.github.io/health-dashboard/"
GITHUB_BRANCH = "main"

# ============================================================================
# LOGGING
# ============================================================================

LOG_LEVEL = "INFO"
LOG_FORMAT = '%(asctime)s [%(levelname)s] - %(message)s'