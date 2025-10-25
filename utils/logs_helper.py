#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Helper para leer y formatear logs del sistema"""

from datetime import datetime
import os

# Ruta del archivo de log (en /tmp para evitar problemas de permisos)
LOG_PATH = "/tmp/monitor_salud.log"

def leer_ultimos_logs(num_lineas=100):
    """Lee las últimas N líneas del log"""
    try:
        # Verificar que el archivo existe
        if not os.path.exists(LOG_PATH):
            return [f"# Archivo de logs no encontrado en: {LOG_PATH}\n"]
        
        # Verificar que se puede leer
        if not os.access(LOG_PATH, os.R_OK):
            return [f"# Sin permisos de lectura para: {LOG_PATH}\n"]
        
        with open(LOG_PATH, 'r', encoding='utf-8') as f:
            todas_las_lineas = f.readlines()
            
            # Si el archivo está vacío
            if not todas_las_lineas:
                return ["# Archivo de logs vacío\n"]
            
            # Retornar las últimas N líneas
            ultimas = todas_las_lineas[-num_lineas:]
            return ultimas if ultimas else ["# No hay logs disponibles\n"]
            
    except FileNotFoundError:
        return [f"# No se encontró el archivo de logs en: {LOG_PATH}\n"]
    except PermissionError:
        return [f"# Sin permisos para leer: {LOG_PATH}\n"]
    except Exception as e:
        return [f"# Error leyendo logs: {str(e)}\n# Ruta: {LOG_PATH}\n"]

def generar_resumen_ejecucion(cache):
    """Genera resumen de la última ejecución"""
    try:
        archivos_procesados = cache.get("_archivos_procesados", [])
        
        # Debug: verificar ruta del log
        import os
        log_existe = os.path.exists(LOG_PATH)
        log_size = os.path.getsize(LOG_PATH) if log_existe else 0
        
        return {
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
            "archivos_procesados": len(archivos_procesados),
            "total_ejercicios": len(cache.get("ejercicio", [])),
            "total_peso": len(cache.get("peso", [])),
            "total_pasos": len(cache.get("pasos", [])),
            "log_existe": log_existe,
            "log_size": log_size
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