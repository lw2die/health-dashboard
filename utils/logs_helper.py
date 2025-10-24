#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Helper para leer y formatear logs del sistema
"""

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
        num_archivos = len(archivos_procesados)
        
        # Obtener último archivo procesado si existe
        ultimo_archivo = archivos_procesados[-1] if archivos_procesados else "Ninguno"
        
        # Contar métricas totales
        ejercicios = len(cache.get("ejercicio", []))
        peso = len(cache.get("peso", []))
        pasos = len(cache.get("pasos", []))
        
        return {
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
            "archivos_procesados": num_archivos,
            "ultimo_archivo": ultimo_archivo,
            "total_ejercicios": ejercicios,
            "total_peso": peso,
            "total_pasos": pasos
        }
    except Exception as e:
        return {
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
            "archivos_procesados": 0,
            "error": str(e)
        }


def formatear_logs_html(lineas_log):
    """Convierte líneas de log a HTML escapado"""
    import html
    
    html_lines = []
    for linea in lineas_log:
        # Escapar HTML para evitar problemas
        linea_safe = html.escape(linea)
        html_lines.append(linea_safe)
    
    return ''.join(html_lines)