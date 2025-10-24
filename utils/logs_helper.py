#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Helper para leer y formatear logs del sistema"""

from datetime import datetime

LOG_PATH = "/home/ubuntu/gdrive_mount/log_monitoreo.log"

def leer_ultimos_logs(num_lineas=100):
    """Lee las últimas N líneas del log"""
    try:
        with open(LOG_PATH, 'r', encoding='utf-8') as f:
            todas_las_lineas = f.readlines()
            return todas_las_lineas[-num_lineas:]
    except FileNotFoundError:
        return ["# No se encontró el archivo de logs\n"]
    except Exception as e:
        return [f"# Error leyendo logs: {str(e)}\n"]

def generar_resumen_ejecucion(cache):
    """Genera resumen de la última ejecución"""
    try:
        archivos_procesados = cache.get("_archivos_procesados", [])
        return {
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
            "archivos_procesados": len(archivos_procesados),
            "total_ejercicios": len(cache.get("ejercicio", [])),
            "total_peso": len(cache.get("peso", [])),
            "total_pasos": len(cache.get("pasos", []))
        }
    except Exception as e:
        return {
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
            "archivos_procesados": 0,
            "error": str(e)
        }

def formatear_logs_html(lineas_log):
    """Convierte líneas de log a HTML escapado (seguridad)"""
    import html
    return ''.join([html.escape(linea) for linea in lineas_log])