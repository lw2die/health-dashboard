#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuración del sistema de logging
Solo escribe a consola - el script bash redirige a archivo
"""

import logging
import sys

# Configurar formato
LOG_FORMAT = '%(asctime)s [%(levelname)s] - %(message)s'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

# Crear logger
logger = logging.getLogger('monitor_salud')
logger.setLevel(logging.INFO)

# Evitar duplicados si ya está configurado
if not logger.handlers:
    # Solo handler para consola (stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

# No propagar a loggers superiores
logger.propagate = False