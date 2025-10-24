#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GeneraciÃ³n del dashboard HTML con grÃ¡ficos interactivos
VERSIÃ“N FINAL: TSB arreglado, PAI diario+ventana, TODAS las mÃ©tricas
"""

from datetime import datetime, timedelta
from config import (
    OUTPUT_HTML, EDAD, ALTURA_CM, FC_MAX, FC_REPOSO, PESO_OBJETIVO,
    PAI_OBJETIVO_SEMANAL, COLOR_EXCELENTE, COLOR_BUENO, COLOR_MALO,
    TSB_OPTIMO_MIN, TSB_OPTIMO_MAX
)
from metricas.pai import calcular_pai_semanal, preparar_datos_pai_historico
from metricas.fitness import calcular_tsb, preparar_datos_tsb_historico
from metricas.score import calcular_score_longevidad, generar_recomendaciones
from outputs.graficos import preparar_datos_peso
from utils.logger import logger

# ========================================
# IMPORTACIÃ“N PARA LABORATORIO
# ========================================
try:
    from metricas.laboratorio import obtener_datos_laboratorio_y_alertas
    LABORATORIO_DISPONIBLE = True
except ImportError:
    logger.warning("âš ï¸ MÃ³dulo laboratorio no disponible")
    LABORATORIO_DISPONIBLE = False


def _preparar_datos_spo2(spo2_data, dias=30):
    """Prepara datos de SpO2 para grÃ¡fico."""
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
    """Prepara datos de mÃ©tricas corporales."""
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
        por_dia[fecha].append(d[campo])
    
    fechas = sorted(por_dia.keys())
    valores = [sum(por_dia[f]) / len(por_dia[f]) for f in fechas]
    
    return {"fechas": fechas, "valores": valores}


def _preparar_datos_fc_reposo(fc_reposo_data, dias=30):
    """Prepara datos de FC en reposo."""
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


def _preparar_datos_pasos(pasos_data, dias=30):
    """Prepara datos de pasos diarios."""
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
    """Prepara datos de presiÃ³n arterial."""
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


def _preparar_datos_pai_completo(ejercicios, dias=30):
    """
    Prepara PAI con dos lÃ­neas:
    1. PAI diario de cada sesiÃ³n
    2. PAI acumulado ventana mÃ³vil 7 dÃ­as
    """
    if not ejercicios:
        return {"fechas": [], "pai_diario": [], "pai_ventana_7d": []}
    
    fecha_limite = datetime.now() - timedelta(days=dias)
    recientes = [
        e for e in ejercicios
        if datetime.fromisoformat(e["fecha"].replace("Z", "+00:00")).replace(tzinfo=None) >= fecha_limite
    ]
    
    # Agrupar PAI por dÃ­a
    por_dia = {}
    for e in recientes:
        fecha = datetime.fromisoformat(e["fecha"].replace("Z", "+00:00")).strftime("%Y-%m-%d")
        if fecha not in por_dia:
            por_dia[fecha] = 0
        por_dia[fecha] += e.get("pai", 0)
    
    # Ordenar fechas
    fechas = sorted(por_dia.keys())
    pai_diario = [por_dia[f] for f in fechas]
    
    # Calcular ventana mÃ³vil de 7 dÃ­as
    pai_ventana_7d = []
    for i, fecha in enumerate(fechas):
        fecha_obj = datetime.strptime(fecha, "%Y-%m-%d")
        inicio_ventana = fecha_obj - timedelta(days=6)
        
        suma_ventana = sum(
            por_dia[f] for f in fechas
            if inicio_ventana <= datetime.strptime(f, "%Y-%m-%d") <= fecha_obj
        )
        pai_ventana_7d.append(suma_ventana)
    
    return {
        "fechas": fechas,
        "pai_diario": pai_diario,
        "pai_ventana_7d": pai_ventana_7d
    }


def generar_dashboard(cache):
    """Genera dashboard HTML completo."""
    logger.info("Generando dashboard HTML con grÃ¡ficos...")
    
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
    
    # Calcular mÃ©tricas
    metricas = _calcular_metricas(
        ejercicios, peso, sueno, spo2, grasa_corporal,
        masa_muscular, vo2max_medido, fc_reposo, pasos, presion_arterial
    )
    
    # Laboratorio
    datos_laboratorio = {}
    if LABORATORIO_DISPONIBLE:
        try:
            datos_laboratorio = obtener_datos_laboratorio_y_alertas(
                edad=EDAD,
                altura_cm=ALTURA_CM,
                peso_kg=metricas.get("peso_actual", 83),
                vo2max_medido=metricas.get("vo2max", 38)
            )
            logger.info(f"âœ… Laboratorio procesado: Longevity Score = {datos_laboratorio.get('longevity_score', 'N/A')}/100")
        except Exception as e:
            logger.error(f"âŒ Error procesando laboratorio: {e}")
    
    # Preparar datos para grÃ¡ficos
    datos_graficos = {
        "pai": _preparar_datos_pai_completo(ejercicios),  # PAI diario + ventana
        "peso": preparar_datos_peso(peso),
        "tsb": preparar_datos_tsb_historico(ejercicios),  # TSB con CTL/ATL
        "spo2": _preparar_datos_spo2(spo2),
        "grasa": _preparar_datos_metrica_corporal(grasa_corporal, "porcentaje"),
        "masa_muscular": _preparar_datos_metrica_corporal(masa_muscular, "masa_kg"),
        "fc_reposo": _preparar_datos_fc_reposo(fc_reposo),
        "pasos": _preparar_datos_pasos(pasos),
        "presion_arterial": _preparar_datos_presion_arterial(presion_arterial)
    }
    
    entrenamientos_recientes = _obtener_entrenamientos_recientes(ejercicios)
    html = _generar_html(metricas, datos_graficos, entrenamientos_recientes, len(ejercicios), datos_laboratorio)
    
    with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
        f.write(html)
    
    logger.info(f"Dashboard generado: {OUTPUT_HTML}")


def _calcular_metricas(ejercicios, peso, sueno, spo2, grasa_corporal, masa_muscular, vo2max_medido, fc_reposo, pasos, presion_arterial):
    """Calcula todas las mÃ©tricas."""
    
    # PAI semanal
    pai_semanal = calcular_pai_semanal(ejercicios)
    
    # Peso actual
    peso_actual = peso[-1]["peso"] if peso else None
    
    # VO2max MEDIDO (del JSON, NO calculado)
    vo2max = None
    if vo2max_medido:
        vo2max = vo2max_medido[-1]["vo2max"]
    
    # TSB actual (RETORNA DICT con tsb, ctl, atl)
    tsb_dict = calcular_tsb(ejercicios) if ejercicios else {"tsb": 0, "ctl": 0, "atl": 0}
    tsb_actual = tsb_dict.get("tsb", 0) if isinstance(tsb_dict, dict) else tsb_dict
    
    # SueÃ±o (Ãºltimos 7 dÃ­as)
    if sueno:
        suenos_recientes = sueno[-7:] if len(sueno) >= 7 else sueno
        total_minutos = sum(s.get("duracion_minutos", 0) for s in suenos_recientes)
        promedio_sueno_horas = (total_minutos / len(suenos_recientes) / 60) if suenos_recientes else None
    else:
        promedio_sueno_horas = None
    
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
    
    # PresiÃ³n arterial promedio
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
    
    return {
        "pai_semanal": pai_semanal,
        "peso_actual": peso_actual,
        "vo2max": vo2max,
        "tsb_actual": tsb_actual,  # Solo el nÃºmero
        "tsb_dict": tsb_dict,  # Dict completo con ctl/atl
        "promedio_sueno": promedio_sueno_horas,
        "spo2_promedio": spo2_promedio,
        "grasa_actual": grasa_actual,
        "masa_muscular_actual": masa_muscular_actual,
        "fc_reposo_promedio": fc_reposo_promedio,
        "pasos_promedio": pasos_promedio,
        "presion_sistolica": presion_sistolica,
        "presion_diastolica": presion_diastolica,
        "score_longevidad": score_longevidad,
        "recomendaciones": recomendaciones
    }


def _obtener_entrenamientos_recientes(ejercicios, dias=7):
    """Obtiene entrenamientos recientes."""
    if not ejercicios:
        return []
    
    fecha_limite = datetime.now().replace(tzinfo=None) - timedelta(days=dias)
    recientes = [
        e for e in ejercicios
        if datetime.fromisoformat(e["fecha"].replace("Z", "+00:00")).replace(tzinfo=None) >= fecha_limite
    ]
    recientes.sort(key=lambda x: x["fecha"], reverse=True)
    return recientes[:10]


def _generar_html(metricas, datos_graficos, entrenamientos, total_ejercicios, datos_laboratorio):
    """Genera HTML completo."""
    html_laboratorio = ""
    if datos_laboratorio:
        html_laboratorio = _generar_html_laboratorio(datos_laboratorio)
    
    return f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Dashboard de Salud - HealthConnect</title>
        <script src="https://cdn.plot.ly/plotly-2.26.0.min.js"></script>
        {_generar_css()}
    </head>
    <body>
        <div class="container">
            <header>
                <h1>ðŸ“Š Dashboard de Salud</h1>
                <p class="subtitle">Ãšltima actualizaciÃ³n: {datetime.now().strftime("%d/%m/%Y %H:%M")}</p>
            </header>
            
            {html_laboratorio}
            
            <div class="metrics-grid">
                {_generar_card_pai(metricas)}
                {_generar_card_peso(metricas)}
                {_generar_card_vo2max(metricas)}
                {_generar_card_tsb(metricas)}
                {_generar_card_sueno(metricas)}
                {_generar_card_spo2(metricas)}
                {_generar_card_grasa(metricas)}
                {_generar_card_masa_muscular(metricas)}
                {_generar_card_fc_reposo(metricas)}
                {_generar_card_pasos(metricas)}
                {_generar_card_presion(metricas)}
                {_generar_card_score(metricas)}
            </div>
            
            <div class="charts-section">
                <h2>ðŸ“ˆ EvoluciÃ³n Temporal</h2>
                <div class="charts-grid">
                    <div class="chart-container">
                        <h3>PAI (Diario + Ventana MÃ³vil 7 dÃ­as)</h3>
                        <div id="pai-chart"></div>
                    </div>
                    <div class="chart-container">
                        <h3>Peso</h3>
                        <div id="peso-chart"></div>
                    </div>
                    <div class="chart-container">
                        <h3>TSB + CTL + ATL</h3>
                        <div id="tsb-chart"></div>
                    </div>
                    <div class="chart-container">
                        <h3>SpO2</h3>
                        <div id="spo2-chart"></div>
                    </div>
                    <div class="chart-container">
                        <h3>Grasa Corporal</h3>
                        <div id="grasa-chart"></div>
                    </div>
                    <div class="chart-container">
                        <h3>Masa Muscular</h3>
                        <div id="masa-chart"></div>
                    </div>
                    <div class="chart-container">
                        <h3>FC en Reposo</h3>
                        <div id="fc-reposo-chart"></div>
                    </div>
                    <div class="chart-container">
                        <h3>Pasos Diarios</h3>
                        <div id="pasos-chart"></div>
                    </div>
                    <div class="chart-container">
                        <h3>PresiÃ³n Arterial</h3>
                        <div id="presion-chart"></div>
                    </div>
                </div>
            </div>
            
            <div class="training-section">
                <h2>ðŸƒ Entrenamientos Recientes</h2>
                {_generar_tabla_entrenamientos(entrenamientos)}
            </div>
            
            <div class="recommendations-section">
                <h2>ðŸ’¡ Recomendaciones</h2>
                {_generar_recomendaciones_html(metricas["recomendaciones"])}
            </div>
        </div>
        
        <script>
            {_generar_javascript(datos_graficos)}
        </script>
    </body>
    </html>
    """


# ==================== CARDS ====================

def _generar_card_tsb(metricas):
    """Card TSB - CORREGIDO para manejar dict"""
    tsb = metricas.get("tsb_actual")  # Solo el nÃºmero
    tsb_dict = metricas.get("tsb_dict", {})  # Dict completo
    
    if tsb is None:
        return f"""
        <div class="metric-card">
            <div class="metric-label">TSB Actual</div>
            <div class="metric-value" style="color: #8b949e;">Sin datos</div>
        </div>
        """
    
    if TSB_OPTIMO_MIN <= tsb <= TSB_OPTIMO_MAX:
        color = COLOR_EXCELENTE
        estado = "Forma Ã³ptima"
    elif -20 < tsb < TSB_OPTIMO_MIN:
        color = COLOR_BUENO
        estado = "Neutral"
    else:
        color = COLOR_MALO
        estado = "Fatiga" if tsb < -20 else "Sobreentrenamiento"
    
    ctl = tsb_dict.get("ctl", 0)
    atl = tsb_dict.get("atl", 0)
    
    return f"""
    <div class="metric-card">
        <div class="metric-label">TSB Actual</div>
        <div class="metric-value" style="color: {color};">{tsb:.1f}</div>
        <div class="metric-detail">{estado}</div>
        <div class="metric-detail" style="font-size: 0.8em; color: #8b949e;">CTL: {ctl:.1f} | ATL: {atl:.1f}</div>
    </div>
    """


def _generar_card_pai(metricas):
    """Card PAI"""
    pai = metricas.get("pai_semanal", 0)
    
    if pai >= PAI_OBJETIVO_SEMANAL:
        color = COLOR_EXCELENTE
        estado = "Ã“ptimo"
    elif pai >= 50:
        color = COLOR_BUENO
        estado = "Bueno"
    else:
        color = COLOR_MALO
        estado = "Bajo"
    
    return f"""
    <div class="metric-card">
        <div class="metric-label">PAI Semanal</div>
        <div class="metric-value" style="color: {color};">{pai:.0f}</div>
        <div class="metric-detail">{estado} (Objetivo: {PAI_OBJETIVO_SEMANAL})</div>
    </div>
    """


def _generar_card_peso(metricas):
    """Card Peso"""
    peso = metricas.get("peso_actual")
    
    if peso is None:
        return f"""
        <div class="metric-card">
            <div class="metric-label">Peso Actual</div>
            <div class="metric-value" style="color: #8b949e;">Sin datos</div>
        </div>
        """
    
    diferencia = peso - PESO_OBJETIVO
    if abs(diferencia) <= 2:
        color = COLOR_EXCELENTE
        estado = "En objetivo"
    elif abs(diferencia) <= 5:
        color = COLOR_BUENO
        estado = "Cerca"
    else:
        color = COLOR_MALO
        estado = "Lejos"
    
    return f"""
    <div class="metric-card">
        <div class="metric-label">Peso Actual</div>
        <div class="metric-value" style="color: {color};">{peso:.1f} kg</div>
        <div class="metric-detail">{estado} ({diferencia:+.1f} kg)</div>
    </div>
    """


def _generar_card_vo2max(metricas):
    """Card VO2max MEDIDO"""
    vo2max = metricas.get("vo2max")
    
    if vo2max is None:
        return f"""
        <div class="metric-card">
            <div class="metric-label">VO2max (Medido)</div>
            <div class="metric-value" style="color: #8b949e;">Sin datos</div>
        </div>
        """
    
    if vo2max >= 40:
        color = COLOR_EXCELENTE
        estado = "Excelente"
    elif vo2max >= 35:
        color = COLOR_BUENO
        estado = "Bueno"
    else:
        color = COLOR_MALO
        estado = "Por debajo"
    
    return f"""
    <div class="metric-card">
        <div class="metric-label">VO2max (Medido)</div>
        <div class="metric-value" style="color: {color};">{vo2max:.1f}</div>
        <div class="metric-detail">{estado}</div>
    </div>
    """


def _generar_card_sueno(metricas):
    """Card SueÃ±o"""
    sueno = metricas.get("promedio_sueno")
    
    if sueno is None:
        return f"""
        <div class="metric-card">
            <div class="metric-label">SueÃ±o (7 dÃ­as)</div>
            <div class="metric-value" style="color: #8b949e;">Sin datos</div>
        </div>
        """
    
    if sueno >= 7:
        color = COLOR_EXCELENTE
        estado = "Ã“ptimo"
    elif sueno >= 6:
        color = COLOR_BUENO
        estado = "Aceptable"
    else:
        color = COLOR_MALO
        estado = "Insuficiente"
    
    return f"""
    <div class="metric-card">
        <div class="metric-label">SueÃ±o (7 dÃ­as)</div>
        <div class="metric-value" style="color: {color};">{sueno:.1f}h</div>
        <div class="metric-detail">{estado}</div>
    </div>
    """


def _generar_card_spo2(metricas):
    """Card SpO2"""
    spo2 = metricas.get("spo2_promedio")
    
    if spo2 is None:
        return f"""
        <div class="metric-card">
            <div class="metric-label">SpO2 (7 dÃ­as)</div>
            <div class="metric-value" style="color: #8b949e;">Sin datos</div>
        </div>
        """
    
    if spo2 >= 95:
        color = COLOR_EXCELENTE
        estado = "Normal"
    elif spo2 >= 90:
        color = COLOR_BUENO
        estado = "Aceptable"
    else:
        color = COLOR_MALO
        estado = "Bajo"
    
    return f"""
    <div class="metric-card">
        <div class="metric-label">SpO2 (7 dÃ­as)</div>
        <div class="metric-value" style="color: {color};">{spo2:.1f}%</div>
        <div class="metric-detail">{estado}</div>
    </div>
    """


def _generar_card_grasa(metricas):
    """Card Grasa"""
    grasa = metricas.get("grasa_actual")
    
    if grasa is None:
        return f"""
        <div class="metric-card">
            <div class="metric-label">Grasa Corporal</div>
            <div class="metric-value" style="color: #8b949e;">Sin datos</div>
        </div>
        """
    
    if grasa < 15:
        color = COLOR_EXCELENTE
        estado = "Bajo"
    elif grasa < 20:
        color = COLOR_BUENO
        estado = "Normal"
    else:
        color = COLOR_MALO
        estado = "Alto"
    
    return f"""
    <div class="metric-card">
        <div class="metric-label">Grasa Corporal</div>
        <div class="metric-value" style="color: {color};">{grasa:.1f}%</div>
        <div class="metric-detail">{estado}</div>
    </div>
    """


def _generar_card_masa_muscular(metricas):
    """Card Masa Muscular"""
    masa = metricas.get("masa_muscular_actual")
    
    if masa is None:
        return f"""
        <div class="metric-card">
            <div class="metric-label">Masa Muscular</div>
            <div class="metric-value" style="color: #8b949e;">Sin datos</div>
        </div>
        """
    
    return f"""
    <div class="metric-card">
        <div class="metric-label">Masa Muscular</div>
        <div class="metric-value" style="color: {COLOR_BUENO};">{masa:.1f} kg</div>
    </div>
    """


def _generar_card_fc_reposo(metricas):
    """Card FC Reposo"""
    fc = metricas.get("fc_reposo_promedio")
    
    if fc is None:
        return f"""
        <div class="metric-card">
            <div class="metric-label">FC Reposo (7d)</div>
            <div class="metric-value" style="color: #8b949e;">Sin datos</div>
        </div>
        """
    
    if fc < 60:
        color = COLOR_EXCELENTE
        estado = "Excelente"
    elif fc < 70:
        color = COLOR_BUENO
        estado = "Bueno"
    else:
        color = COLOR_MALO
        estado = "Elevado"
    
    return f"""
    <div class="metric-card">
        <div class="metric-label">FC Reposo (7d)</div>
        <div class="metric-value" style="color: {color};">{fc:.0f} bpm</div>
        <div class="metric-detail">{estado}</div>
    </div>
    """


def _generar_card_pasos(metricas):
    """Card Pasos"""
    pasos = metricas.get("pasos_promedio")
    
    if pasos is None:
        return f"""
        <div class="metric-card">
            <div class="metric-label">Pasos (7d)</div>
            <div class="metric-value" style="color: #8b949e;">Sin datos</div>
        </div>
        """
    
    if pasos >= 10000:
        color = COLOR_EXCELENTE
        estado = "Excelente"
    elif pasos >= 7000:
        color = COLOR_BUENO
        estado = "Bueno"
    else:
        color = COLOR_MALO
        estado = "Bajo"
    
    return f"""
    <div class="metric-card">
        <div class="metric-label">Pasos (7d)</div>
        <div class="metric-value" style="color: {color};">{pasos:,.0f}</div>
        <div class="metric-detail">{estado}</div>
    </div>
    """


def _generar_card_presion(metricas):
    """Card PresiÃ³n"""
    sistolica = metricas.get("presion_sistolica")
    diastolica = metricas.get("presion_diastolica")
    
    if sistolica is None or diastolica is None:
        return f"""
        <div class="metric-card">
            <div class="metric-label">PresiÃ³n (7d)</div>
            <div class="metric-value" style="color: #8b949e;">Sin datos</div>
        </div>
        """
    
    if sistolica < 120 and diastolica < 80:
        color = COLOR_EXCELENTE
        estado = "Normal"
    elif sistolica < 130 and diastolica < 85:
        color = COLOR_BUENO
        estado = "Elevada"
    else:
        color = COLOR_MALO
        estado = "Alta"
    
    return f"""
    <div class="metric-card">
        <div class="metric-label">PresiÃ³n (7d)</div>
        <div class="metric-value" style="color: {color};">{sistolica:.0f}/{diastolica:.0f}</div>
        <div class="metric-detail">{estado}</div>
    </div>
    """


def _generar_card_score(metricas):
    """Card Score"""
    score = metricas.get("score_longevidad", 0)
    
    if score >= 85:
        color = COLOR_EXCELENTE
        estado = "Excelente"
    elif score >= 70:
        color = COLOR_BUENO
        estado = "Bueno"
    else:
        color = COLOR_MALO
        estado = "Mejora"
    
    return f"""
    <div class="metric-card">
        <div class="metric-label">Score Longevidad</div>
        <div class="metric-value" style="color: {color};">{score:.0f}/100</div>
        <div class="metric-detail">{estado}</div>
    </div>
    """


def _generar_tabla_entrenamientos(entrenamientos):
    """Tabla entrenamientos"""
    if not entrenamientos:
        return "<p style='color: #8b949e;'>Sin entrenamientos</p>"
    
    filas = []
    for e in entrenamientos:
        fecha = datetime.fromisoformat(e["fecha"].replace("Z", "+00:00"))
        fecha_str = fecha.strftime("%d/%m %H:%M")
        pai_color = COLOR_EXCELENTE if e.get("pai", 0) > 10 else COLOR_BUENO if e.get("pai", 0) > 5 else COLOR_MALO
        
        fila = f"""
        <tr>
            <td>{fecha_str}</td>
            <td>{e['tipo']}</td>
            <td>{e['duracion']:.0f} min</td>
            <td>{e.get('fc_promedio', 'N/A')}</td>
            <td style="color: {pai_color}; font-weight: bold;">{e.get('pai', 0):.1f}</td>
            <td>{e.get('zona', 'N/A')}</td>
        </tr>
        """
        filas.append(fila)
    
    return f"""
    <table>
        <thead>
            <tr>
                <th>Fecha</th>
                <th>Tipo</th>
                <th>DuraciÃ³n</th>
                <th>FC Prom</th>
                <th>PAI</th>
                <th>Zona</th>
            </tr>
        </thead>
        <tbody>
            {"".join(filas)}
        </tbody>
    </table>
    """


def _generar_recomendaciones_html(recomendaciones):
    """Recomendaciones"""
    if not recomendaciones:
        return "<p style='color: #8b949e;'>Sin recomendaciones</p>"
    
    items = []
    for rec in recomendaciones:
        items.append(f"<li>{rec}</li>")
    
    return f"""
    <ul class="recommendations-list">
        {"".join(items)}
    </ul>
    """


def _generar_html_laboratorio(datos_laboratorio):
    """Laboratorio"""
    longevity = datos_laboratorio.get("longevity_score", 0)
    cardio = datos_laboratorio.get("cardio_score", 0)
    metabolic = datos_laboratorio.get("metabolic_score", 0)
    inflammation = datos_laboratorio.get("inflammation_score", 0)
    hormone = datos_laboratorio.get("hormone_score", 0)
    
    return f"""
    <div class="laboratorio-section">
        <h2>ðŸ§¬ Dashboard CientÃ­fico</h2>
        <div class="scores-grid">
            <div class="score-card score-main">
                <div class="score-label">Longevity Score</div>
                <div class="score-value" style="color: {_get_color_score(longevity)};">{longevity:.1f}/100</div>
            </div>
            <div class="score-card">
                <div class="score-label">CardioScore</div>
                <div class="score-value" style="color: {_get_color_score(cardio)};">{cardio:.1f}</div>
            </div>
            <div class="score-card">
                <div class="score-label">MetabolicScore</div>
                <div class="score-value" style="color: {_get_color_score(metabolic)};">{metabolic:.1f}</div>
            </div>
            <div class="score-card">
                <div class="score-label">InflammationScore</div>
                <div class="score-value" style="color: {_get_color_score(inflammation)};">{inflammation:.1f}</div>
            </div>
            <div class="score-card">
                <div class="score-label">HormoneScore</div>
                <div class="score-value" style="color: {_get_color_score(hormone)};">{hormone:.1f}</div>
            </div>
        </div>
        <div class="alertas-section">
            <h3>âš ï¸ Alertas</h3>
            {_generar_alertas_html(datos_laboratorio.get("alertas", []))}
        </div>
    </div>
    """


def _get_color_score(score):
    """Color segÃºn score"""
    if score >= 80:
        return COLOR_EXCELENTE
    elif score >= 60:
        return COLOR_BUENO
    else:
        return COLOR_MALO


def _generar_alertas_html(alertas):
    """Alertas"""
    if not alertas:
        return "<p style='color: #8b949e;'>Sin alertas</p>"
    
    items = []
    for alerta in alertas:
        severidad = alerta.get("severidad", "INFO")
        color = "#f85149" if severidad == "CRITICA" else "#f0883e" if severidad == "ALTA" else "#d29922"
        
        items.append(f"""
        <div class="alerta-item" style="border-left: 4px solid {color};">
            <div style="font-weight: bold; color: {color};">{alerta.get("titulo", "")}</div>
            <div style="color: #c9d1d9; margin-top: 5px;">{alerta.get("descripcion", "")}</div>
        </div>
        """)
    
    return "".join(items)


def _generar_css():
    """CSS"""
    return """
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
            background: linear-gradient(135deg, #0d1117 0%, #161b22 100%);
            color: #c9d1d9;
            padding: 20px;
            line-height: 1.6;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        header {
            text-align: center;
            margin-bottom: 40px;
        }
        
        h1 {
            font-size: 2.5em;
            color: #58a6ff;
            margin-bottom: 10px;
        }
        
        h2 {
            color: #58a6ff;
            margin: 30px 0 20px 0;
            font-size: 1.8em;
        }
        
        h3 {
            color: #79c0ff;
            margin-bottom: 15px;
            font-size: 1.2em;
        }
        
        .subtitle {
            color: #8b949e;
            font-size: 1.1em;
        }
        
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }
        
        .metric-card {
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 8px;
            padding: 20px;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        
        .metric-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 4px 12px rgba(88, 166, 255, 0.3);
        }
        
        .metric-label {
            color: #8b949e;
            font-size: 0.9em;
            margin-bottom: 10px;
        }
        
        .metric-value {
            font-size: 2em;
            font-weight: bold;
            margin-bottom: 5px;
        }
        
        .metric-detail {
            color: #8b949e;
            font-size: 0.9em;
        }
        
        .charts-section {
            margin: 40px 0;
        }
        
        .charts-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 30px;
        }
        
        .chart-container {
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 8px;
            padding: 20px;
        }
        
        .training-section, .recommendations-section {
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 8px;
            padding: 25px;
            margin: 30px 0;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }
        
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #30363d;
        }
        
        th {
            color: #58a6ff;
            font-weight: 600;
        }
        
        tr:hover {
            background: #0d1117;
        }
        
        .recommendations-list {
            list-style: none;
            padding: 0;
        }
        
        .recommendations-list li {
            padding: 12px;
            margin: 10px 0;
            background: #0d1117;
            border-left: 3px solid #58a6ff;
            border-radius: 4px;
        }
        
        .laboratorio-section {
            background: #161b22;
            border: 2px solid #58a6ff;
            border-radius: 12px;
            padding: 30px;
            margin-bottom: 40px;
        }
        
        .scores-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        
        .score-card {
            background: #0d1117;
            border: 1px solid #30363d;
            border-radius: 8px;
            padding: 20px;
            text-align: center;
        }
        
        .score-main {
            grid-column: 1 / -1;
            border: 2px solid #58a6ff;
        }
        
        .score-label {
            color: #8b949e;
            font-size: 0.9em;
            margin-bottom: 10px;
        }
        
        .score-value {
            font-size: 2.5em;
            font-weight: bold;
        }
        
        .alertas-section {
            margin-top: 30px;
        }
        
        .alerta-item {
            background: #0d1117;
            padding: 15px;
            margin: 10px 0;
            border-radius: 6px;
        }
        
        @media (max-width: 768px) {
            .charts-grid {
                grid-template-columns: 1fr;
            }
            h1 {
                font-size: 1.8em;
            }
        }
    </style>
    """


def _generar_javascript(datos_graficos):
    """JavaScript para grÃ¡ficos"""
    return f"""
        const layout_config = {{
            paper_bgcolor: '#0d1117',
            plot_bgcolor: '#161b22',
            font: {{ color: '#c9d1d9' }},
            margin: {{ l: 40, r: 20, t: 20, b: 40 }},
            showlegend: true,
            height: 300
        }};
        
        // PAI: Diario + Ventana MÃ³vil 7 dÃ­as
        const pai_diario = {{
            x: {datos_graficos['pai']['fechas']},
            y: {datos_graficos['pai']['pai_diario']},
            type: 'bar',
            name: 'PAI Diario',
            marker: {{ color: '#58a6ff' }}
        }};
        
        const pai_ventana = {{
            x: {datos_graficos['pai']['fechas']},
            y: {datos_graficos['pai']['pai_ventana_7d']},
            type: 'scatter',
            mode: 'lines+markers',
            name: 'Ventana 7d',
            line: {{ color: '#f85149', width: 3 }},
            marker: {{ size: 8 }},
            yaxis: 'y2'
        }};
        
        Plotly.newPlot('pai-chart', [pai_diario, pai_ventana], {{
            ...layout_config,
            yaxis: {{ title: 'PAI Diario', gridcolor: '#30363d' }},
            yaxis2: {{
                title: 'PAI Acumulado 7d',
                overlaying: 'y',
                side: 'right',
                gridcolor: '#30363d'
            }},
            xaxis: {{ gridcolor: '#30363d' }},
            shapes: [{{
                type: 'line',
                x0: 0, x1: 1, xref: 'paper',
                yref: 'y2',
                y0: {PAI_OBJETIVO_SEMANAL}, y1: {PAI_OBJETIVO_SEMANAL},
                line: {{ color: '#3fb950', width: 2, dash: 'dot' }}
            }}]
        }});
        
        // Peso
        const peso_data = {{
            x: {datos_graficos['peso']['fechas']},
            y: {datos_graficos['peso']['valores']},
            type: 'scatter',
            mode: 'lines+markers',
            line: {{ color: '#f85149', width: 2 }},
            marker: {{ size: 6 }}
        }};
        
        Plotly.newPlot('peso-chart', [peso_data], {{
            ...layout_config,
            yaxis: {{ title: 'Peso (kg)', gridcolor: '#30363d' }},
            xaxis: {{ gridcolor: '#30363d' }},
            shapes: [{{
                type: 'line',
                x0: 0, x1: 1, xref: 'paper',
                y0: {PESO_OBJETIVO}, y1: {PESO_OBJETIVO},
                line: {{ color: '#3fb950', width: 1, dash: 'dot' }}
            }}]
        }});
        
        // TSB + CTL + ATL
        const tsb_data = {{
            x: {datos_graficos['tsb']['fechas']},
            y: {datos_graficos['tsb']['tsb']},
            type: 'scatter',
            mode: 'lines',
            name: 'TSB',
            fill: 'tozeroy',
            line: {{ color: '#ffa657', width: 2 }}
        }};
        
        const ctl_data = {{
            x: {datos_graficos['tsb']['fechas']},
            y: {datos_graficos['tsb']['ctl']},
            type: 'scatter',
            mode: 'lines',
            name: 'CTL (Fitness)',
            line: {{ color: '#3fb950', width: 2 }}
        }};
        
        const atl_data = {{
            x: {datos_graficos['tsb']['fechas']},
            y: {datos_graficos['tsb']['atl']},
            type: 'scatter',
            mode: 'lines',
            name: 'ATL (Fatiga)',
            line: {{ color: '#f85149', width: 2 }}
        }};
        
        Plotly.newPlot('tsb-chart', [tsb_data, ctl_data, atl_data], {{
            ...layout_config,
            yaxis: {{ title: 'PuntuaciÃ³n', gridcolor: '#30363d' }},
            xaxis: {{ gridcolor: '#30363d' }},
            shapes: [{{
                type: 'rect',
                x0: 0, x1: 1, xref: 'paper',
                y0: {TSB_OPTIMO_MIN}, y1: {TSB_OPTIMO_MAX},
                fillcolor: '#3fb950', opacity: 0.1,
                line: {{ width: 0 }}
            }}]
        }});
        
        // SpO2
        const spo2_data = {{
            x: {datos_graficos['spo2']['fechas']},
            y: {datos_graficos['spo2']['valores']},
            type: 'scatter',
            mode: 'lines+markers',
            line: {{ color: '#79c0ff', width: 2 }},
            marker: {{ size: 6 }}
        }};
        
        if (spo2_data.x.length > 0) {{
            Plotly.newPlot('spo2-chart', [spo2_data], {{
                ...layout_config,
                yaxis: {{ title: 'SpO2 (%)', gridcolor: '#30363d', range: [90, 100] }},
                xaxis: {{ gridcolor: '#30363d' }},
                shapes: [{{
                    type: 'line',
                    x0: 0, x1: 1, xref: 'paper',
                    y0: 95, y1: 95,
                    line: {{ color: '#3fb950', width: 1, dash: 'dot' }}
                }}]
            }});
        }}
        
        // Grasa
        const grasa_data = {{
            x: {datos_graficos['grasa']['fechas']},
            y: {datos_graficos['grasa']['valores']},
            type: 'scatter',
            mode: 'lines+markers',
            line: {{ color: '#ff7b72', width: 2 }},
            marker: {{ size: 6 }}
        }};
        
        if (grasa_data.x.length > 0) {{
            Plotly.newPlot('grasa-chart', [grasa_data], {{
                ...layout_config,
                yaxis: {{ title: 'Grasa (%)', gridcolor: '#30363d' }},
                xaxis: {{ gridcolor: '#30363d' }}
            }});
        }}
        
        // Masa Muscular
        const masa_data = {{
            x: {datos_graficos['masa_muscular']['fechas']},
            y: {datos_graficos['masa_muscular']['valores']},
            type: 'scatter',
            mode: 'lines+markers',
            line: {{ color: '#a371f7', width: 2 }},
            marker: {{ size: 6 }}
        }};
        
        if (masa_data.x.length > 0) {{
            Plotly.newPlot('masa-chart', [masa_data], {{
                ...layout_config,
                yaxis: {{ title: 'Masa Muscular (kg)', gridcolor: '#30363d' }},
                xaxis: {{ gridcolor: '#30363d' }}
            }});
        }}
        
        // FC Reposo
        const fc_data = {{
            x: {datos_graficos['fc_reposo']['fechas']},
            y: {datos_graficos['fc_reposo']['valores']},
            type: 'scatter',
            mode: 'lines+markers',
            line: {{ color: '#f85149', width: 2 }},
            marker: {{ size: 6 }}
        }};
        
        if (fc_data.x.length > 0) {{
            Plotly.newPlot('fc-reposo-chart', [fc_data], {{
                ...layout_config,
                yaxis: {{ title: 'FC Reposo (bpm)', gridcolor: '#30363d' }},
                xaxis: {{ gridcolor: '#30363d' }},
                shapes: [{{
                    type: 'line',
                    x0: 0, x1: 1, xref: 'paper',
                    y0: 60, y1: 60,
                    line: {{ color: '#3fb950', width: 1, dash: 'dot' }}
                }}]
            }});
        }}
        
        // Pasos
        const pasos_data = {{
            x: {datos_graficos['pasos']['fechas']},
            y: {datos_graficos['pasos']['valores']},
            type: 'bar',
            marker: {{ color: '#3fb950' }}
        }};
        
        if (pasos_data.x.length > 0) {{
            Plotly.newPlot('pasos-chart', [pasos_data], {{
                ...layout_config,
                yaxis: {{ title: 'Pasos', gridcolor: '#30363d' }},
                xaxis: {{ gridcolor: '#30363d' }},
                shapes: [{{
                    type: 'line',
                    x0: 0, x1: 1, xref: 'paper',
                    y0: 10000, y1: 10000,
                    line: {{ color: '#58a6ff', width: 1, dash: 'dot' }}
                }}]
            }});
        }}
        
        // PresiÃ³n Arterial
        const presion_sistolica = {{
            x: {datos_graficos['presion_arterial']['fechas']},
            y: {datos_graficos['presion_arterial']['sistolica']},
            type: 'scatter',
            mode: 'lines+markers',
            name: 'SistÃ³lica',
            line: {{ color: '#f85149', width: 2 }},
            marker: {{ size: 6 }}
        }};
        
        const presion_diastolica = {{
            x: {datos_graficos['presion_arterial']['fechas']},
            y: {datos_graficos['presion_arterial']['diastolica']},
            type: 'scatter',
            mode: 'lines+markers',
            name: 'DiastÃ³lica',
            line: {{ color: '#79c0ff', width: 2 }},
            marker: {{ size: 6 }}
        }};
        
        if (presion_sistolica.x.length > 0) {{
            Plotly.newPlot('presion-chart', [presion_sistolica, presion_diastolica], {{
                ...layout_config,
                yaxis: {{ title: 'PresiÃ³n (mmHg)', gridcolor: '#30363d' }},
                xaxis: {{ gridcolor: '#30363d' }},
                legend: {{ bgcolor: '#161b22', bordercolor: '#30363d', borderwidth: 1 }}
            }});
        }}
    """