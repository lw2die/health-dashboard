#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuración del sistema de logging
Guarda logs tanto en consola como en archivo
"""

import logging
import sys
from pathlib import Path

# Ruta del archivo de log
LOG_FILE = Path("/home/ubuntu/gdrive_mount/log_monitoreo.log")

# Crear directorio si no existe
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

# Configurar formato
LOG_FORMAT = '%(asctime)s [%(levelname)s] - %(message)s'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

# Crear logger
logger = logging.getLogger('monitor_salud')
logger.setLevel(logging.INFO)

# Evitar duplicados si ya está configurado
if not logger.handlers:
    # Handler para consola (stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # Handler para archivo
    try:
        file_handler = logging.FileHandler(LOG_FILE, mode='a', encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        file_formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        # Si falla crear el archivo, solo usar consola
        logger.error(f"No se pudo crear handler de archivo: {e}")

# No propagar a loggers superiores
logger.propagate = False