#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dashboard Generator - Orquestador Principal MODULAR
Coordina todos los módulos de generación del dashboard
"""

from datetime import datetime, timedelta
from config import OUTPUT_HTML, EDAD, ALTURA_CM
from utils.logger import logger
from utils.logs_helper import leer_ultimos_logs, generar_resumen_ejecucion, formatear_logs_html

# Módulos de métricas
from outputs.preparador_metricas import calcular_metricas

# Módulos de preparación de gráficos
from outputs.prep_graficos_activity import (
    preparar_datos_pai_completo, preparar_datos_pasos, preparar_datos_sueno,
    preparar_datos_distancia, preparar_datos_calorias,
    preparar_datos_nutrition, calcular_deficit_calorico, calcular_circulo_hoy,
    calcular_macros_promedio_7d  # ✅ CAMBIO 1: Agregar import
)
from outputs.prep_graficos_body import (
    preparar_datos_peso_deduplicado, preparar_datos_metrica_corporal,
    preparar_datos_tasa_metabolica
)
from outputs.prep_graficos_cardio import (
    preparar_datos_fc_reposo, preparar_datos_fc_diurna,
    preparar_datos_presion_arterial, preparar_datos_spo2, preparar_datos_glucosa
)

# Módulos de TSB
from metricas.fitness import preparar_datos_tsb_historico

# Módulos de plan de acción
from metricas.plan_accion import generar_plan_accion, renderizar_plan_accion_html
from metricas.healthspan import generar_recomendaciones_healthspan

# Módulos de dashboard
from outputs.cards import (
    generar_card_pai, generar_card_peso, generar_card_vo2max,
    generar_card_tsb, generar_card_sueno, generar_card_spo2,
    generar_card_grasa, generar_card_masa_muscular, generar_card_fc_reposo,
    generar_card_pasos, generar_card_presion, generar_card_glucemia,
    generar_card_gmi, generar_card_score
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
    logger.warning("Módulo laboratorio no disponible")
    LABORATORIO_DISPONIBLE = False


def generar_dashboard(cache):
    """
    Genera dashboard HTML completo.
    Orquesta todos los módulos para construir el dashboard.
    """
    logger.info("Generando dashboard HTML con gráficos...")
    
    # 1. EXTRAER DATOS DEL CACHE
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
    glucosa = cache.get("glucosa", [])
    masa_osea = cache.get("masa_osea", [])
    masa_agua = cache.get("masa_agua", [])
    tasa_metabolica = cache.get("tasa_metabolica", [])
    distancia = cache.get("distancia", [])
    calorias_totales = cache.get("calorias_totales", [])
    nutrition = cache.get("nutrition", [])
    frecuencia_cardiaca = cache.get("frecuencia_cardiaca", [])
    
    # 2. CALCULAR MÉTRICAS
    metricas = calcular_metricas(
        ejercicios, peso, sueno, spo2, grasa_corporal,
        masa_muscular, vo2max_medido, fc_reposo, pasos, presion_arterial,
        nutrition, tasa_metabolica, calorias_totales, glucosa
    )
    
    # 3. PROCESAR LABORATORIO (si está disponible)
    datos_laboratorio = {}
    if LABORATORIO_DISPONIBLE:
        try:
            datos_laboratorio = obtener_datos_laboratorio_y_alertas(
                edad=EDAD,
                altura_cm=ALTURA_CM,
                peso_kg=metricas.get("peso_actual", 83),
                vo2max_medido=metricas.get("vo2max", 38),
                glucemias_diarias=glucosa
            )
            logger.info(f"Laboratorio procesado: Longevity Score = {datos_laboratorio.get('longevity_score', 'N/A')}/100")
        except Exception as e:
            logger.error(f"Error procesando laboratorio: {e}")
    
    # 4. PREPARAR DATOS PARA GRÁFICOS
    datos_graficos = {
        "pai": preparar_datos_pai_completo(ejercicios),
        "peso": preparar_datos_peso_deduplicado(peso),
        "tsb": preparar_datos_tsb_historico(ejercicios),
        "sueno": preparar_datos_sueno(sueno),
        "spo2": preparar_datos_spo2(spo2),
        "grasa": preparar_datos_metrica_corporal(grasa_corporal, "porcentaje"),
        "masa_muscular": preparar_datos_metrica_corporal(masa_muscular, "masa_kg"),
        "fc_reposo": preparar_datos_fc_reposo(fc_reposo),
        "frecuencia_cardiaca": preparar_datos_fc_diurna(frecuencia_cardiaca),
        "pasos": preparar_datos_pasos(pasos),
        "presion_arterial": preparar_datos_presion_arterial(presion_arterial),
        "glucosa": preparar_datos_glucosa(glucosa),
        "masa_osea": preparar_datos_metrica_corporal(masa_osea, "masa_kg"),
        "masa_agua": preparar_datos_metrica_corporal(masa_agua, "masa_kg"),
        "tasa_metabolica": preparar_datos_tasa_metabolica(tasa_metabolica),
        "distancia": preparar_datos_distancia(distancia),
        "calorias_totales": preparar_datos_calorias(calorias_totales),
        "nutrition": preparar_datos_nutrition(nutrition, dias=14),
        "deficit": calcular_deficit_calorico(nutrition, tasa_metabolica, calorias_totales, dias=14)
    }
    
    # Calcular círculo del día actual
    circulo_data = calcular_circulo_hoy(nutrition, tasa_metabolica, calorias_totales)
    
    # ✅ CAMBIO 2: Calcular macros promedio 7 días
    macros_7d = calcular_macros_promedio_7d(nutrition)
    
    # 5. GENERAR COMPONENTES HTML
    html_laboratorio = generar_html_laboratorio(datos_laboratorio) if datos_laboratorio else ""
    
    healthspan_data = metricas.get("healthspan_data", {})
    
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
        generar_card_glucemia(metricas),
        generar_card_gmi(metricas),
        generar_card_score(metricas)
    ])
    
    entrenamientos = _obtener_entrenamientos_recientes(ejercicios)
    entrenamientos_html = generar_tabla_entrenamientos(entrenamientos)
    
    # PLAN DE ACCIÓN PERSONALIZADO
    try:
        logger.info("Intentando generar plan de acción...")
        plan_accion = generar_plan_accion(metricas, nutrition, tasa_metabolica, calorias_totales)
        logger.info("Plan de acción generado correctamente")
        plan_accion_html = renderizar_plan_accion_html(plan_accion)
        logger.info("HTML del plan renderizado correctamente")
    except Exception as e:
        logger.error(f"ERROR generando plan de acción: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        plan_accion_html = ""
    
    recomendaciones_healthspan = generar_recomendaciones_healthspan(healthspan_data, metricas)
    recomendaciones_html = generar_recomendaciones_html(metricas["recomendaciones"])
    
    logs_lineas = leer_ultimos_logs(500)
    logs_html_content = formatear_logs_html(logs_lineas)
    resumen_ejecucion = generar_resumen_ejecucion(cache)
    
    # 6. CONSTRUIR HTML COMPLETO
    # ✅ CAMBIO 3: Pasar macros_7d a construir_html_completo
    html = construir_html_completo(
        html_laboratorio,
        cards_html,
        entrenamientos_html,
        recomendaciones_html,
        datos_graficos,
        logs_html_content,
        resumen_ejecucion,
        healthspan_data,
        plan_accion_html,
        circulo_data=circulo_data,
        macros_7d=macros_7d  # ✅ NUEVO PARÁMETRO
    )
    
    # 7. GUARDAR ARCHIVO
    with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
        f.write(html)
    
    logger.info(f"Dashboard generado: {OUTPUT_HTML}")


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