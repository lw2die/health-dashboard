#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Preparadores de Gráficos - Actividad Física
Prepara datos para gráficos de PAI, TSB, pasos, sueño, nutrition y déficit
"""

from datetime import datetime, timedelta
from collections import defaultdict
from metricas.fitness import preparar_datos_tsb_historico


def preparar_datos_pai_completo(ejercicios_data, dias=30):
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


def preparar_datos_pasos(pasos_data, dias=30):
    """Prepara datos de pasos diarios (Samsung guarda valores acumulados)"""
    if not pasos_data:
        return {"fechas": [], "valores": []}
    
    fecha_limite = datetime.now() - timedelta(days=dias)
    recientes = [
        p for p in pasos_data
        if datetime.fromisoformat(p["fecha"].replace("Z", "+00:00")).replace(tzinfo=None) >= fecha_limite
    ]
    
    # Agrupar por día y tomar MÁXIMO (Samsung guarda acumulados)
    por_dia = {}
    for p in recientes:
        fecha = datetime.fromisoformat(p["fecha"].replace("Z", "+00:00")).strftime("%Y-%m-%d")
        if fecha not in por_dia:
            por_dia[fecha] = []
        por_dia[fecha].append(p["pasos"])
    
    fechas = sorted(por_dia.keys())
    valores = [max(por_dia[f]) for f in fechas]
    
    return {"fechas": fechas, "valores": valores}


def preparar_datos_sueno(sueno_data, dias=14):
    """
    Prepara datos de sueño para gráfico de barras apiladas.
    Últimos 14 días con todas las fases.
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


def preparar_datos_distancia(distancia_data, dias=90):
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


def preparar_datos_calorias(calorias_data, dias=90):
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


def preparar_datos_nutrition(nutrition_data, dias=14):
    """
    Prepara datos de nutrición agrupados por día.
    ✅ MODIFICADO: 14 días en lugar de 7
    Calcula totales diarios de calorías y macronutrientes.
    """
    if not nutrition_data:
        return {
            "fechas": [],
            "calorias": [],
            "proteinas": [],
            "carbohidratos": [],
            "grasas": [],
            "por_comida": {
                "desayuno": [],
                "almuerzo": [],
                "cena": [],
                "snack": []
            }
        }
    
    fecha_limite = datetime.now() - timedelta(days=dias)
    recientes = [
        n for n in nutrition_data
        if datetime.fromisoformat(n["timestamp"].replace("Z", "+00:00")).replace(tzinfo=None) >= fecha_limite
    ]
    
    por_dia = defaultdict(lambda: {
        "calorias": 0,
        "proteinas": 0,
        "carbohidratos": 0,
        "grasas": 0,
        "desayuno": 0,
        "almuerzo": 0,
        "cena": 0,
        "snack": 0
    })
    
    meal_type_map = {
        1: "desayuno",
        2: "almuerzo",
        3: "cena",
        4: "snack"
    }
    
    for n in recientes:
        fecha = datetime.fromisoformat(n["timestamp"].replace("Z", "+00:00")).strftime("%Y-%m-%d")
        por_dia[fecha]["calorias"] += n.get("energy_kcal", 0)
        por_dia[fecha]["proteinas"] += n.get("protein_g", 0)
        por_dia[fecha]["carbohidratos"] += n.get("carbs_g", 0)
        por_dia[fecha]["grasas"] += n.get("fat_total_g", 0)
        
        meal_type = n.get("meal_type", 0)
        meal_name = meal_type_map.get(meal_type, "snack")
        por_dia[fecha][meal_name] += n.get("energy_kcal", 0)
    
    fechas = sorted(por_dia.keys())
    
    return {
        "fechas": fechas,
        "calorias": [round(por_dia[f]["calorias"], 0) for f in fechas],
        "proteinas": [round(por_dia[f]["proteinas"], 1) for f in fechas],
        "carbohidratos": [round(por_dia[f]["carbohidratos"], 1) for f in fechas],
        "grasas": [round(por_dia[f]["grasas"], 1) for f in fechas],
        "por_comida": {
            "desayuno": [round(por_dia[f]["desayuno"], 0) for f in fechas],
            "almuerzo": [round(por_dia[f]["almuerzo"], 0) for f in fechas],
            "cena": [round(por_dia[f]["cena"], 0) for f in fechas],
            "snack": [round(por_dia[f]["snack"], 0) for f in fechas]
        }
    }


def calcular_deficit_calorico(nutrition_data, tmb_data, calorias_data, dias=14):
    """
    ✅ MODIFICADO: Muestra solo días con AL MENOS un dato real (Samsung Health style)
    No rellena con 0s los días sin datos.
    
    Fórmula Samsung Health:
    - Presupuesto = TMB + Ejercicio del día
    - Comido = nutrition del día
    - Ejercicio = active_calories del día
    """
    # Generar los últimos 14 días como candidatos
    hoy = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    dias_candidatos = [(hoy - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(dias-1, -1, -1)]
    
    # Agrupar COMIDO por día
    comido_por_dia = defaultdict(float)
    if nutrition_data:
        for n in nutrition_data:
            try:
                fecha = datetime.fromisoformat(n["timestamp"].replace("Z", "+00:00"))
                dia = fecha.strftime("%Y-%m-%d")
                comido_por_dia[dia] += n.get("energy_kcal", 0)
            except:
                continue
    
    # Agrupar TMB por día
    tmb_por_dia = {}
    if tmb_data:
        for t in tmb_data:
            try:
                fecha = datetime.fromisoformat(t["timestamp"].replace("Z", "+00:00"))
                dia = fecha.strftime("%Y-%m-%d")
                tmb_por_dia[dia] = t.get("kcal_dia", 1700)
            except:
                continue
    
    # Agrupar EJERCICIO por día
    ejercicio_por_dia = defaultdict(float)
    if calorias_data:
        for c in calorias_data:
            try:
                fecha = datetime.fromisoformat(c.get("fecha", c.get("timestamp", "")).replace("Z", "+00:00"))
                dia = fecha.strftime("%Y-%m-%d")
                ejercicio_por_dia[dia] += c.get("energia_kcal", 0)
            except:
                continue
    
    # Filtrar solo días con AL MENOS un dato real
    fechas_con_datos = []
    for fecha in dias_candidatos:
        tiene_comido = fecha in comido_por_dia and comido_por_dia[fecha] > 0
        tiene_tmb = fecha in tmb_por_dia
        tiene_ejercicio = fecha in ejercicio_por_dia and ejercicio_por_dia[fecha] > 0
        
        if tiene_comido or tiene_tmb or tiene_ejercicio:
            fechas_con_datos.append(fecha)
    
    # Construir resultado solo con días que tienen datos
    resultado = {
        "fechas": fechas_con_datos,
        "presupuesto": [],
        "comido": [],
        "ejercicio": []
    }
    
    for fecha in fechas_con_datos:
        comido = comido_por_dia.get(fecha, 0)
        tmb = tmb_por_dia.get(fecha, 1700)
        ejercicio = ejercicio_por_dia.get(fecha, 0)
        
        # Presupuesto = TMB + Ejercicio (como Samsung Health)
        presupuesto = tmb + ejercicio
        
        resultado["presupuesto"].append(round(presupuesto, 0))
        resultado["comido"].append(round(comido, 0))
        resultado["ejercicio"].append(round(ejercicio, 0))
    
    return resultado


def calcular_circulo_hoy(nutrition_data, tmb_data, calorias_data):
    """
    ✅ NUEVO: Calcula datos para el círculo de calorías del DÍA ACTUAL
    Returns: dict con presupuesto, comido, ejercicio, restante, macros %
    """
    from utils.logger import logger
    
    hoy = datetime.now().strftime("%Y-%m-%d")
    logger.info(f"🔍 Calculando círculo para HOY: {hoy}")
    
    # Comido hoy
    comido = 0
    proteinas = 0
    carbohidratos = 0
    grasas = 0
    
    if nutrition_data:
        logger.info(f"📊 Total registros de nutrition en cache: {len(nutrition_data)}")
        registros_hoy = 0
        for n in nutrition_data:
            try:
                fecha = datetime.fromisoformat(n["timestamp"].replace("Z", "+00:00"))
                dia = fecha.strftime("%Y-%m-%d")
                if dia == hoy:
                    registros_hoy += 1
                    comido += n.get("energy_kcal", 0)
                    proteinas += n.get("protein_g", 0)
                    carbohidratos += n.get("carbs_g", 0)
                    grasas += n.get("fat_total_g", 0)
            except Exception as e:
                logger.error(f"Error procesando registro nutrition: {e}")
                continue
        logger.info(f"✅ Registros de nutrition HOY: {registros_hoy}, Calorías: {comido}")
    else:
        logger.warning("⚠️ No hay datos de nutrition en cache")
    
    # TMB hoy
    tmb = 1700  # default
    if tmb_data:
        for t in tmb_data:
            try:
                fecha = datetime.fromisoformat(t["timestamp"].replace("Z", "+00:00"))
                if fecha.strftime("%Y-%m-%d") == hoy:
                    tmb = t.get("kcal_dia", 1700)
                    logger.info(f"✅ TMB HOY: {tmb} kcal")
                    break
            except:
                continue
    
    # Ejercicio hoy
    ejercicio = 0
    if calorias_data:
        for c in calorias_data:
            try:
                # ✅ CORRECCIÓN: calorias_totales usa 'fecha' no 'timestamp'
                fecha = datetime.fromisoformat(c.get("fecha", c.get("timestamp", "")).replace("Z", "+00:00"))
                if fecha.strftime("%Y-%m-%d") == hoy:
                    ejercicio += c.get("energia_kcal", 0)
            except:
                continue
        logger.info(f"✅ Ejercicio HOY: {ejercicio} kcal")
    
    presupuesto = tmb + ejercicio
    restante = presupuesto - comido
    
    logger.info(f"📈 RESULTADO: Presupuesto={presupuesto}, Comido={comido}, Restante={restante}")
    
    # Calcular porcentajes de macros
    total_calorias_macros = (proteinas * 4) + (carbohidratos * 4) + (grasas * 9)
    
    if total_calorias_macros > 0:
        pct_proteinas = round((proteinas * 4 / total_calorias_macros) * 100)
        pct_carbohidratos = round((carbohidratos * 4 / total_calorias_macros) * 100)
        pct_grasas = round((grasas * 9 / total_calorias_macros) * 100)
    else:
        pct_proteinas = 0
        pct_carbohidratos = 0
        pct_grasas = 0
    
    return {
        "presupuesto": round(presupuesto, 0),
        "comido": round(comido, 0),
        "ejercicio": round(ejercicio, 0),
        "restante": round(restante, 0),
        "proteinas_g": round(proteinas, 1),
        "carbohidratos_g": round(carbohidratos, 1),
        "grasas_g": round(grasas, 1),
        "pct_proteinas": pct_proteinas,
        "pct_carbohidratos": pct_carbohidratos,
        "pct_grasas": pct_grasas
    }