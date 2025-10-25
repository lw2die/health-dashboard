#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuración del sistema de logging
"""

import sys
import logging
from config import LOG_LEVEL, LOG_FORMAT


def setup_logger(name=__name__):
    """
    Configura y retorna un logger con formato estandarizado.
    
    Args:
        name: Nombre del logger (generalmente __name__ del módulo)
    
    Returns:
        Logger configurado
    """
    logger = logging.getLogger(name)
    
    # Evitar duplicar handlers si ya está configurado
    if logger.handlers:
        return logger
    
    logger.setLevel(getattr(logging, LOG_LEVEL))
    
    # Handler para stdout
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(getattr(logging, LOG_LEVEL))
    
    # Formato
    formatter = logging.Formatter(LOG_FORMAT)
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    
    return logger


# Logger global por defecto
logger = setup_logger("monitor_salud")