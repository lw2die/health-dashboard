#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dashboard Generator - Orquestador Principal (MODULAR)
✅ VERSIÓN CON HEALTHSPAN INDEX
Importa y coordina todos los módulos de generación
"""

from datetime import datetime, timedelta
from collections import defaultdict
from config import OUTPUT_HTML, EDAD, ALTURA_CM
from utils.logger import logger
from utils.logs_helper import leer_ultimos_logs, generar_resumen_ejecucion, formatear_logs_html

# Importar módulos de métricas
from metricas.pai import calcular_pai_semanal
from metricas.fitness import calcular_tsb, preparar_datos_tsb_historico
from metricas.score import calcular_score_longevidad, generar_recomendaciones
from metricas.healthspan import calcular_healthspan_index, generar_recomendaciones_healthspan  # ✅ NUEVO


def _preparar_datos_peso_deduplicado(peso_data, dias=90):
    """
    Prepara datos de peso DEDUPLICADOS por día.
    Si hay múltiples mediciones en un día, usa el promedio.
    """
    if not peso_data:
        return {"fechas": [], "valores": []}
    
    fecha_limite = datetime.now() - timedelta(days=dias)
    recientes = [
        p for p in peso_data
        if datetime.fromisoformat(p["fecha"].replace("Z", "+00:00")).replace(tzinfo=None) >= fecha_limite
    ]
    
    # ✅ Deduplicar por día - promediar si hay múltiples mediciones
    por_dia = {}
    for p in recientes:
        fecha = datetime.fromisoformat(p["fecha"].replace("Z", "+00:00")).strftime("%Y-%m-%d")
        if fecha not in por_dia:
            por_dia[fecha] = []
        por_dia[fecha].append(p["peso"])
    
    fechas = sorted(por_dia.keys())
    valores = [sum(por_dia[f]) / len(por_dia[f]) for f in fechas]
    
    return {"fechas": fechas, "valores": valores}

# Importar módulos de dashboard
from outputs.cards import (
    generar_card_pai, generar_card_peso, generar_card_vo2max,
    generar_card_tsb, generar_card_sueno, generar_card_spo2,
    generar_card_grasa, generar_card_masa_muscular, generar_card_fc_reposo,
    generar_card_pasos, generar_card_presion, generar_card_score
)
from outputs.html_builder import construir_html_completo
from outputs.laboratorio_renderer import (
    generar_html_laboratorio, generar_tabla_entrenamientos,
    generar_recomendaciones_html
)

# Laboratorio (opcional)
try:
    from metricas.laboratorio import obtener_datos_laboratorio_y_alertas
    LABORATORIO_DISPONIBLE = True
except ImportError:
    logger.warning("⚠️ Módulo laboratorio no disponible")
    LABORATORIO_DISPONIBLE = False


def generar_dashboard(cache):
    """
    Genera dashboard HTML completo.
    Orquesta todos los módulos para construir el dashboard.
    """
    logger.info("Generando dashboard HTML con gráficos...")
    
    # ═══════════════════════════════════════════════
    # 1. EXTRAER DATOS DEL CACHE
    # ═══════════════════════════════════════════════
    ejercicios = cache.get("ejercicio", [])
    peso = cache.get("peso", [])
    sueno = cache.get("sueno", [])
    spo2 = cache.get("spo2", [])
    grasa_corporal = cache.get("grasa_corporal", [])
    masa_muscular = cache.get("masa_muscular", [])
    vo2max_medido = cache.get("vo2max", [])
    fc_reposo = cache.get("fc_reposo", [])
    pasos = cache.get("pasos", [])
    presion_arterial = cache.get("presion_arterial", [])
    # ✅ NUEVAS MÉTRICAS
    glucosa = cache.get("glucosa", [])
    masa_osea = cache.get("masa_osea", [])
    masa_agua = cache.get("masa_agua", [])
    tasa_metabolica = cache.get("tasa_metabolica", [])
    distancia = cache.get("distancia", [])
    calorias_totales = cache.get("calorias_totales", [])
    
    # ═══════════════════════════════════════════════
    # 2. CALCULAR MÉTRICAS
    # ═══════════════════════════════════════════════
    metricas = _calcular_metricas(
        ejercicios, peso, sueno, spo2, grasa_corporal,
        masa_muscular, vo2max_medido, fc_reposo, pasos, presion_arterial
    )
    
    # ═══════════════════════════════════════════════
    # 3. PROCESAR LABORATORIO (si está disponible)
    # ═══════════════════════════════════════════════
    datos_laboratorio = {}
    if LABORATORIO_DISPONIBLE:
        try:
            datos_laboratorio = obtener_datos_laboratorio_y_alertas(
                edad=EDAD,
                altura_cm=ALTURA_CM,
                peso_kg=metricas.get("peso_actual", 83),
                vo2max_medido=metricas.get("vo2max", 38)
            )
            logger.info(f"✅ Laboratorio procesado: Longevity Score = {datos_laboratorio.get('longevity_score', 'N/A')}/100")
        except Exception as e:
            logger.error(f"❌ Error procesando laboratorio: {e}")
    
    # ═══════════════════════════════════════════════
    # 4. PREPARAR DATOS PARA GRÁFICOS
    # ═══════════════════════════════════════════════
    # Extraer frecuencia_cardiaca del cache
    frecuencia_cardiaca = cache.get("frecuencia_cardiaca", [])
    
    datos_graficos = {
        "pai": _preparar_datos_pai_completo(ejercicios),
        "peso": _preparar_datos_peso_deduplicado(peso),  # ✅ Deduplicado
        "tsb": preparar_datos_tsb_historico(ejercicios),
        "sueno": _preparar_datos_sueno(sueno),  # ✅ NUEVO - Gráfico de sueño
        "spo2": _preparar_datos_spo2(spo2),
        "grasa": _preparar_datos_metrica_corporal(grasa_corporal, "porcentaje"),
        "masa_muscular": _preparar_datos_metrica_corporal(masa_muscular, "masa_kg"),
        "fc_reposo": _preparar_datos_fc_reposo(fc_reposo),
        "frecuencia_cardiaca": _preparar_datos_fc_diurna(frecuencia_cardiaca),  # ✅ AGREGADO
        "pasos": _preparar_datos_pasos(pasos),
        "presion_arterial": _preparar_datos_presion_arterial(presion_arterial),
        # ✅ NUEVAS MÉTRICAS
        "glucosa": _preparar_datos_glucosa(glucosa),
        "masa_osea": _preparar_datos_metrica_corporal(masa_osea, "masa_kg"),
        "masa_agua": _preparar_datos_metrica_corporal(masa_agua, "masa_kg"),
        "tasa_metabolica": _preparar_datos_tasa_metabolica(tasa_metabolica),
        "distancia": _preparar_datos_distancia(distancia),
        "calorias_totales": _preparar_datos_calorias(calorias_totales)
    }
    
    # ═══════════════════════════════════════════════
    # 5. GENERAR COMPONENTES HTML
    # ═══════════════════════════════════════════════
    
    # Laboratorio
    html_laboratorio = generar_html_laboratorio(datos_laboratorio) if datos_laboratorio else ""
    
    # Healthspan Index (✅ NUEVO)
    healthspan_data = metricas.get("healthspan_data", {})
    
    # Cards
    cards_html = "".join([
        generar_card_pai(metricas),
        generar_card_peso(metricas),
        generar_card_vo2max(metricas),
        generar_card_tsb(metricas),
        generar_card_sueno(metricas),
        generar_card_spo2(metricas),
        generar_card_grasa(metricas),
        generar_card_masa_muscular(metricas),
        generar_card_fc_reposo(metricas),
        generar_card_pasos(metricas),
        generar_card_presion(metricas),
        generar_card_score(metricas)
    ])
    
    # Entrenamientos recientes
    entrenamientos = _obtener_entrenamientos_recientes(ejercicios)
    entrenamientos_html = generar_tabla_entrenamientos(entrenamientos)
    
    # Recomendaciones (✅ AHORA USA HEALTHSPAN)
    recomendaciones_healthspan = generar_recomendaciones_healthspan(healthspan_data, metricas)
    recomendaciones_html = generar_recomendaciones_html(metricas["recomendaciones"])
    
    # Generar sección de logs
    logs_lineas = leer_ultimos_logs(500)
    logs_html_content = formatear_logs_html(logs_lineas)
    resumen_ejecucion = generar_resumen_ejecucion(cache)
    
    # ═══════════════════════════════════════════════
    # 6. CONSTRUIR HTML COMPLETO
    # ═══════════════════════════════════════════════
    html = construir_html_completo(
        html_laboratorio,
        cards_html,
        entrenamientos_html,
        recomendaciones_html,
        datos_graficos,
        logs_html_content,
        resumen_ejecucion,
        healthspan_data  # Parámetro opcional al final
    )
    
    # ═══════════════════════════════════════════════
    # 7. GUARDAR ARCHIVO
    # ═══════════════════════════════════════════════
    with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
        f.write(html)
    
    logger.info(f"Dashboard generado: {OUTPUT_HTML}")


# ═══════════════════════════════════════════════════════════════
# FUNCIONES AUXILIARES
# ═══════════════════════════════════════════════════════════════

def _calcular_metricas(ejercicios, peso, sueno, spo2, grasa_corporal, masa_muscular, vo2max_medido, fc_reposo, pasos, presion_arterial):
    """Calcula todas las métricas del dashboard"""
    
    # PAI semanal
    pai_semanal = calcular_pai_semanal(ejercicios)
    
    # Peso actual
    peso_actual = peso[-1]["peso"] if peso else None
    
    # VO2max MEDIDO
    vo2max = vo2max_medido[-1]["vo2max"] if vo2max_medido else None
    
    # TSB actual
    tsb_dict = calcular_tsb(ejercicios) if ejercicios else {"tsb": 0, "ctl": 0, "atl": 0}
    tsb_actual = tsb_dict.get("tsb", 0) if isinstance(tsb_dict, dict) else tsb_dict
    
    # ✅ SUEÑO CORREGIDO - Agrupar por DÍA primero
    promedio_sueno_horas = None
    if sueno:
        # Agrupar por día
        sueno_por_dia = defaultdict(float)
        for s in sueno:
            try:
                fecha = datetime.fromisoformat(s["fecha"].replace("Z", "+00:00")).strftime("%Y-%m-%d")
                sueno_por_dia[fecha] += s.get("duracion", 0)
            except:
                continue
        
        # Tomar últimos 7 días
        fechas_ordenadas = sorted(sueno_por_dia.keys())[-7:]
        if fechas_ordenadas:
            total_minutos = sum(sueno_por_dia[f] for f in fechas_ordenadas)
            promedio_sueno_horas = (total_minutos / len(fechas_ordenadas)) / 60
    
    # SpO2 promedio
    spo2_promedio = None
    if spo2:
        spo2_recientes = spo2[-7:] if len(spo2) >= 7 else spo2
        spo2_promedio = sum(s.get("porcentaje", 0) for s in spo2_recientes) / len(spo2_recientes)
    
    # Grasa corporal actual
    grasa_actual = grasa_corporal[-1]["porcentaje"] if grasa_corporal else None
    
    # Masa muscular actual
    masa_muscular_actual = masa_muscular[-1]["masa_kg"] if masa_muscular else None
    
    # FC en reposo promedio
    fc_reposo_promedio = None
    if fc_reposo:
        fc_recientes = fc_reposo[-7:] if len(fc_reposo) >= 7 else fc_reposo
        fc_reposo_promedio = sum(fc.get("bpm", 0) for fc in fc_recientes) / len(fc_recientes)
    
    # Pasos promedio
    pasos_promedio = None
    if pasos:
        pasos_recientes = pasos[-7:] if len(pasos) >= 7 else pasos
        pasos_promedio = sum(p.get("pasos", 0) for p in pasos_recientes) / len(pasos_recientes)
    
    # Presión arterial promedio
    presion_sistolica = None
    presion_diastolica = None
    if presion_arterial:
        presion_recientes = presion_arterial[-7:] if len(presion_arterial) >= 7 else presion_arterial
        presion_sistolica = sum(p.get("sistolica", 0) for p in presion_recientes) / len(presion_recientes)
        presion_diastolica = sum(p.get("diastolica", 0) for p in presion_recientes) / len(presion_recientes)
    
    # Score de longevidad
    score_longevidad = calcular_score_longevidad(
        peso_actual, pai_semanal, vo2max, promedio_sueno_horas
    )
    
    # Recomendaciones
    recomendaciones = generar_recomendaciones(
        peso_actual, pai_semanal, promedio_sueno_horas
    )
    
    # ✅ HEALTHSPAN INDEX (NUEVO)
    metricas_base = {
        "pai_semanal": pai_semanal,
        "peso_actual": peso_actual,
        "vo2max": vo2max,
        "tsb_actual": tsb_actual,
        "promedio_sueno": promedio_sueno_horas,
        "spo2_promedio": spo2_promedio,
        "grasa_actual": grasa_actual,
        "masa_muscular_actual": masa_muscular_actual,
        "fc_reposo_promedio": fc_reposo_promedio,
        "pasos_promedio": pasos_promedio,
        "presion_sistolica": presion_sistolica,
        "presion_diastolica": presion_diastolica,
    }
    
    healthspan_data = calcular_healthspan_index(metricas_base)
    
    return {
        **metricas_base,
        "tsb_dict": tsb_dict,
        "score_longevidad": score_longevidad,
        "recomendaciones": recomendaciones,
        "healthspan_data": healthspan_data  # ✅ NUEVO
    }


def _obtener_entrenamientos_recientes(ejercicios, dias=7):
    """Obtiene entrenamientos de los últimos N días"""
    if not ejercicios:
        return []
    
    fecha_limite = datetime.now() - timedelta(days=dias)
    recientes = [
        e for e in ejercicios
        if datetime.fromisoformat(e["fecha"].replace("Z", "+00:00")).replace(tzinfo=None) >= fecha_limite
    ]
    recientes.sort(key=lambda x: x["fecha"], reverse=True)
    return recientes[:10]


def _preparar_datos_pai_completo(ejercicios_data, dias=30):
    """Prepara datos de PAI diario + ventana móvil"""
    if not ejercicios_data:
        return {
            "fechas": [],
            "pai_diario": [],
            "pai_ventana_movil": []
        }
    
    fecha_limite = datetime.now() - timedelta(days=dias)
    recientes = [
        e for e in ejercicios_data
        if datetime.fromisoformat(e["fecha"].replace("Z", "+00:00")).replace(tzinfo=None) >= fecha_limite
    ]
    
    pai_por_dia = defaultdict(float)
    for e in recientes:
        fecha = datetime.fromisoformat(e["fecha"].replace("Z", "+00:00")).strftime("%Y-%m-%d")
        pai_por_dia[fecha] += e.get("pai", 0)
    
    fechas = sorted(pai_por_dia.keys())
    pai_diario = [pai_por_dia[f] for f in fechas]
    
    # Ventana móvil de 7 días
    pai_ventana_movil = []
    for i, fecha in enumerate(fechas):
        inicio = max(0, i - 6)
        suma_ventana = sum(pai_diario[inicio:i + 1])
        pai_ventana_movil.append(suma_ventana)
    
    return {
        "fechas": fechas,
        "pai_diario": pai_diario,
        "pai_ventana_movil": pai_ventana_movil
    }


def _preparar_datos_sueno(sueno_data, dias=14):
    """
    ✅ NUEVO - Prepara datos de sueño para gráfico de barras apiladas.
    Últimos 14 días con todas las fases.
    
    Returns:
        dict: {
            "fechas": [...],
            "awake": [...],
            "light": [...],
            "deep": [...],
            "rem": [...]
        }
    """
    if not sueno_data:
        return {
            "fechas": [],
            "awake": [],
            "light": [],
            "deep": [],
            "rem": []
        }
    
    fecha_limite = datetime.now() - timedelta(days=dias)
    recientes = [
        s for s in sueno_data
        if datetime.fromisoformat(s["fecha"].replace("Z", "+00:00")).replace(tzinfo=None) >= fecha_limite
    ]
    
    # Agrupar por día (sumar si hay múltiples sesiones)
    por_dia = defaultdict(lambda: {"awake": 0, "light": 0, "deep": 0, "rem": 0})
    for s in recientes:
        fecha = datetime.fromisoformat(s["fecha"].replace("Z", "+00:00")).strftime("%Y-%m-%d")
        por_dia[fecha]["awake"] += s.get("awake", 0) / 60  # Convertir a horas
        por_dia[fecha]["light"] += s.get("light", 0) / 60
        por_dia[fecha]["deep"] += s.get("deep", 0) / 60
        por_dia[fecha]["rem"] += s.get("rem", 0) / 60
    
    fechas = sorted(por_dia.keys())
    awake = [por_dia[f]["awake"] for f in fechas]
    light = [por_dia[f]["light"] for f in fechas]
    deep = [por_dia[f]["deep"] for f in fechas]
    rem = [por_dia[f]["rem"] for f in fechas]
    
    return {
        "fechas": fechas,
        "awake": awake,
        "light": light,
        "deep": deep,
        "rem": rem
    }


def _preparar_datos_spo2(spo2_data, dias=30):
    """Prepara datos de SpO2"""
    if not spo2_data:
        return {"fechas": [], "valores": []}
    
    fecha_limite = datetime.now() - timedelta(days=dias)
    recientes = [
        s for s in spo2_data
        if datetime.fromisoformat(s["fecha"].replace("Z", "+00:00")).replace(tzinfo=None) >= fecha_limite
    ]
    
    por_dia = {}
    for s in recientes:
        fecha = datetime.fromisoformat(s["fecha"].replace("Z", "+00:00")).strftime("%Y-%m-%d")
        if fecha not in por_dia:
            por_dia[fecha] = []
        por_dia[fecha].append(s["porcentaje"])
    
    fechas = sorted(por_dia.keys())
    valores = [sum(por_dia[f]) / len(por_dia[f]) for f in fechas]
    
    return {"fechas": fechas, "valores": valores}


def _preparar_datos_metrica_corporal(datos, campo, dias=90):
    """Prepara datos genéricos de métricas corporales"""
    if not datos:
        return {"fechas": [], "valores": []}
    
    fecha_limite = datetime.now() - timedelta(days=dias)
    recientes = [
        d for d in datos
        if datetime.fromisoformat(d["fecha"].replace("Z", "+00:00")).replace(tzinfo=None) >= fecha_limite
    ]
    
    por_dia = {}
    for d in recientes:
        fecha = datetime.fromisoformat(d["fecha"].replace("Z", "+00:00")).strftime("%Y-%m-%d")
        if fecha not in por_dia:
            por_dia[fecha] = []
        por_dia[fecha].append(d.get(campo, 0))
    
    fechas = sorted(por_dia.keys())
    valores = [sum(por_dia[f]) / len(por_dia[f]) for f in fechas]
    
    return {"fechas": fechas, "valores": valores}


def _preparar_datos_fc_reposo(fc_reposo_data, dias=30):
    """Prepara datos de FC en reposo"""
    if not fc_reposo_data:
        return {"fechas": [], "valores": []}
    
    fecha_limite = datetime.now() - timedelta(days=dias)
    recientes = [
        fc for fc in fc_reposo_data
        if datetime.fromisoformat(fc["fecha"].replace("Z", "+00:00")).replace(tzinfo=None) >= fecha_limite
    ]
    
    por_dia = {}
    for fc in recientes:
        fecha = datetime.fromisoformat(fc["fecha"].replace("Z", "+00:00")).strftime("%Y-%m-%d")
        if fecha not in por_dia:
            por_dia[fecha] = []
        por_dia[fecha].append(fc["bpm"])
    
    fechas = sorted(por_dia.keys())
    valores = [sum(por_dia[f]) / len(por_dia[f]) for f in fechas]
    
    return {"fechas": fechas, "valores": valores}


def _preparar_datos_fc_diurna(fc_diurna_data, dias=30):
    """Prepara datos de FC diurna (continua) - min, max, promedio"""
    if not fc_diurna_data:
        return {"fechas": [], "bpm_min": [], "bpm_max": [], "bpm_promedio": []}
    
    fecha_limite = datetime.now() - timedelta(days=dias)
    recientes = [
        fc for fc in fc_diurna_data
        if datetime.fromisoformat(fc["fecha"].replace("Z", "+00:00")).replace(tzinfo=None) >= fecha_limite
    ]
    
    por_dia = {}
    for fc in recientes:
        fecha = datetime.fromisoformat(fc["fecha"].replace("Z", "+00:00")).strftime("%Y-%m-%d")
        if fecha not in por_dia:
            por_dia[fecha] = {
                "bpm_min": [],
                "bpm_max": [],
                "bpm_promedio": []
            }
        por_dia[fecha]["bpm_min"].append(fc.get("bpm_min", 0))
        por_dia[fecha]["bpm_max"].append(fc.get("bpm_max", 0))
        por_dia[fecha]["bpm_promedio"].append(fc.get("bpm_promedio", 0))
    
    fechas = sorted(por_dia.keys())
    bpm_min = [min(por_dia[f]["bpm_min"]) for f in fechas]
    bpm_max = [max(por_dia[f]["bpm_max"]) for f in fechas]
    bpm_promedio = [sum(por_dia[f]["bpm_promedio"]) / len(por_dia[f]["bpm_promedio"]) for f in fechas]
    
    return {
        "fechas": fechas,
        "bpm_min": bpm_min,
        "bpm_max": bpm_max,
        "bpm_promedio": bpm_promedio
    }


def _preparar_datos_pasos(pasos_data, dias=30):
    """Prepara datos de pasos diarios"""
    if not pasos_data:
        return {"fechas": [], "valores": []}
    
    fecha_limite = datetime.now() - timedelta(days=dias)
    recientes = [
        p for p in pasos_data
        if datetime.fromisoformat(p["fecha"].replace("Z", "+00:00")).replace(tzinfo=None) >= fecha_limite
    ]
    
    por_dia = {}
    for p in recientes:
        fecha = datetime.fromisoformat(p["fecha"].replace("Z", "+00:00")).strftime("%Y-%m-%d")
        if fecha not in por_dia:
            por_dia[fecha] = 0
        por_dia[fecha] += p["pasos"]
    
    fechas = sorted(por_dia.keys())
    valores = [por_dia[f] for f in fechas]
    
    return {"fechas": fechas, "valores": valores}


def _preparar_datos_presion_arterial(presion_data, dias=90):
    """Prepara datos de presión arterial"""
    if not presion_data:
        return {"fechas": [], "sistolica": [], "diastolica": []}
    
    fecha_limite = datetime.now() - timedelta(days=dias)
    recientes = [
        p for p in presion_data
        if datetime.fromisoformat(p["fecha"].replace("Z", "+00:00")).replace(tzinfo=None) >= fecha_limite
    ]
    
    por_dia = {}
    for p in recientes:
        fecha = datetime.fromisoformat(p["fecha"].replace("Z", "+00:00")).strftime("%Y-%m-%d")
        if fecha not in por_dia:
            por_dia[fecha] = {"sistolica": [], "diastolica": []}
        por_dia[fecha]["sistolica"].append(p["sistolica"])
        por_dia[fecha]["diastolica"].append(p["diastolica"])
    
    fechas = sorted(por_dia.keys())
    sistolica = [sum(por_dia[f]["sistolica"]) / len(por_dia[f]["sistolica"]) for f in fechas]
    diastolica = [sum(por_dia[f]["diastolica"]) / len(por_dia[f]["diastolica"]) for f in fechas]
    
    return {"fechas": fechas, "sistolica": sistolica, "diastolica": diastolica}


def _preparar_datos_glucosa(glucosa_data, dias=90):
    """Prepara datos de glucosa en sangre"""
    if not glucosa_data:
        return {"fechas": [], "valores": []}
    
    fecha_limite = datetime.now() - timedelta(days=dias)
    recientes = [
        g for g in glucosa_data
        if datetime.fromisoformat(g["fecha"].replace("Z", "+00:00")).replace(tzinfo=None) >= fecha_limite
    ]
    
    por_dia = {}
    for g in recientes:
        fecha = datetime.fromisoformat(g["fecha"].replace("Z", "+00:00")).strftime("%Y-%m-%d")
        if fecha not in por_dia:
            por_dia[fecha] = []
        por_dia[fecha].append(g.get("nivel_mg_dl", 0))
    
    fechas = sorted(por_dia.keys())
    valores = [sum(por_dia[f]) / len(por_dia[f]) for f in fechas]
    
    return {"fechas": fechas, "valores": valores}


def _preparar_datos_tasa_metabolica(tmb_data, dias=90):
    """Prepara datos de tasa metabólica basal"""
    if not tmb_data:
        return {"fechas": [], "valores": []}
    
    fecha_limite = datetime.now() - timedelta(days=dias)
    recientes = [
        t for t in tmb_data
        if datetime.fromisoformat(t["fecha"].replace("Z", "+00:00")).replace(tzinfo=None) >= fecha_limite
    ]
    
    por_dia = {}
    for t in recientes:
        fecha = datetime.fromisoformat(t["fecha"].replace("Z", "+00:00")).strftime("%Y-%m-%d")
        if fecha not in por_dia:
            por_dia[fecha] = []
        por_dia[fecha].append(t.get("kcal_dia", 0))
    
    fechas = sorted(por_dia.keys())
    valores = [sum(por_dia[f]) / len(por_dia[f]) for f in fechas]
    
    return {"fechas": fechas, "valores": valores}


def _preparar_datos_distancia(distancia_data, dias=90):
    """Prepara datos de distancia recorrida"""
    if not distancia_data:
        return {"fechas": [], "valores": []}
    
    fecha_limite = datetime.now() - timedelta(days=dias)
    recientes = [
        d for d in distancia_data
        if datetime.fromisoformat(d["fecha"].replace("Z", "+00:00")).replace(tzinfo=None) >= fecha_limite
    ]
    
    por_dia = {}
    for d in recientes:
        fecha = datetime.fromisoformat(d["fecha"].replace("Z", "+00:00")).strftime("%Y-%m-%d")
        if fecha not in por_dia:
            por_dia[fecha] = []
        por_dia[fecha].append(d.get("distancia_km", 0))
    
    fechas = sorted(por_dia.keys())
    valores = [sum(por_dia[f]) for f in fechas]  # Sumar distancia del día
    
    return {"fechas": fechas, "valores": valores}


def _preparar_datos_calorias(calorias_data, dias=90):
    """Prepara datos de calorías totales quemadas"""
    if not calorias_data:
        return {"fechas": [], "valores": []}
    
    fecha_limite = datetime.now() - timedelta(days=dias)
    recientes = [
        c for c in calorias_data
        if datetime.fromisoformat(c["fecha"].replace("Z", "+00:00")).replace(tzinfo=None) >= fecha_limite
    ]
    
    por_dia = {}
    for c in recientes:
        fecha = datetime.fromisoformat(c["fecha"].replace("Z", "+00:00")).strftime("%Y-%m-%d")
        if fecha not in por_dia:
            por_dia[fecha] = []
        por_dia[fecha].append(c.get("energia_kcal", 0))
    
    fechas = sorted(por_dia.keys())
    valores = [sum(por_dia[f]) for f in fechas]  # Sumar calorías del día
    
    return {"fechas": fechas, "valores": valores}