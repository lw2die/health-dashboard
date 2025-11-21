#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Preparador de Métricas - Cálculo de todas las métricas del dashboard
Centraliza el cálculo de PAI, TSB, VO2max, sueño, SpO2, etc.
"""

from datetime import datetime, timedelta
from collections import defaultdict
from utils.logger import logger
from metricas.pai import calcular_pai_semanal
from metricas.fitness import calcular_tsb
from metricas.score import calcular_score_longevidad, generar_recomendaciones
from metricas.healthspan import calcular_healthspan_index


def calcular_glucemia_ayunas_postprandial(glucosa_data, dias=7):
    """
    Calcula promedios de glucemia en ayunas y postprandial.
    CORRECCIÓN: Fuerza fechas naive (sin zona horaria) para evitar errores de comparación.
    """
    if not glucosa_data:
        return {"ayunas": None, "postprandial": None}
    
    fecha_limite = datetime.now() - timedelta(days=dias)
    
    ayunas_valores = []
    postprandial_valores = []
    
    for g in glucosa_data:
        try:
            ts = g.get("timestamp", g.get("fecha", ""))
            # Parseamos y FORZAMOS a naive (sin zona horaria) para evitar errores
            dt_local = datetime.fromisoformat(ts.replace("Z", "")).replace(tzinfo=None)
            
            # Filtrar por fecha
            if dt_local < fecha_limite:
                continue
            
            valor = g.get("nivel_mg_dl", 0)
            if valor <= 0: continue
            
            relacion = g.get("relacion_comida")
            es_basal = False
            
            # 1. REGLA DE ORO: Hora Literal < 08:00 = BASAL
            if dt_local.hour < 8:
                es_basal = True
            # 2. Si es más tarde, miramos la etiqueta
            elif relacion == 1 or relacion == "1": 
                es_basal = True
            elif relacion in [2, 4, "2", "4"]: 
                es_basal = False
            else:
                es_basal = False
            
            if es_basal:
                ayunas_valores.append(valor)
            else:
                postprandial_valores.append(valor)
                
        except Exception as e:
            continue
    
    ayunas_promedio = sum(ayunas_valores) / len(ayunas_valores) if ayunas_valores else None
    postprandial_promedio = sum(postprandial_valores) / len(postprandial_valores) if postprandial_valores else None
    
    return {
        "ayunas": ayunas_promedio,
        "postprandial": postprandial_promedio
    }


def calcular_hba1c_estimada(glucosa_data, dias=90):
    """Calcula HbA1c Estimada (ADAG)"""
    if not glucosa_data:
        return {"hba1c": None, "glucosa_promedio": None, "num_mediciones": 0}
    
    fecha_limite = datetime.now() - timedelta(days=dias)
    
    valores_glucosa = []
    for g in glucosa_data:
        try:
            ts = g.get("timestamp", g.get("fecha", ""))
            dt = datetime.fromisoformat(ts.replace("Z", "")).replace(tzinfo=None)
            
            if dt < fecha_limite:
                continue
            nivel = g.get("nivel_mg_dl", 0)
            if nivel > 0:
                valores_glucosa.append(nivel)
        except Exception:
            continue
    
    if not valores_glucosa:
        return {"hba1c": None, "glucosa_promedio": None, "num_mediciones": 0}
    
    glucosa_promedio = sum(valores_glucosa) / len(valores_glucosa)
    hba1c = (glucosa_promedio + 46.7) / 28.7
    
    return {
        "hba1c": round(hba1c, 1),
        "glucosa_promedio": round(glucosa_promedio, 1),
        "num_mediciones": len(valores_glucosa)
    }


def calcular_metricas(ejercicios, peso, sueno, spo2, grasa_corporal, 
                     masa_muscular, vo2max_medido, fc_reposo, pasos, 
                     presion_arterial, nutrition, tasa_metabolica, calorias_totales, glucosa=None):
    """Calcula todas las métricas del dashboard."""
    
    pai_semanal = calcular_pai_semanal(ejercicios)
    peso_actual = peso[-1]["peso"] if peso else None
    
    peso_hace_7_dias = peso_actual
    if peso:
        fecha_limite = datetime.now() - timedelta(days=7)
        for p in reversed(peso):
            try:
                fecha = datetime.fromisoformat(p["fecha"].replace("Z", "")).replace(tzinfo=None)
                if fecha <= fecha_limite:
                    peso_hace_7_dias = p.get("peso", peso_actual)
                    break
            except: continue
    
    vo2max = vo2max_medido[-1]["vo2max"] if vo2max_medido else None
    tsb_dict = calcular_tsb(ejercicios) if ejercicios else {"tsb": 0, "ctl": 0, "atl": 0}
    tsb_actual = tsb_dict.get("tsb", 0) if isinstance(tsb_dict, dict) else tsb_dict
    
    promedio_sueno_horas = None
    if sueno:
        sueno_por_dia = defaultdict(float)
        for s in sueno:
            try:
                fecha = datetime.fromisoformat(s["fecha"].replace("Z", "")).strftime("%Y-%m-%d")
                sueno_por_dia[fecha] += s.get("duracion", 0)
            except: continue
        fechas_ordenadas = sorted(sueno_por_dia.keys())[-7:]
        if fechas_ordenadas:
            total_minutos = sum(sueno_por_dia[f] for f in fechas_ordenadas)
            promedio_sueno_horas = (total_minutos / len(fechas_ordenadas)) / 60
    
    spo2_promedio = None
    if spo2:
        spo2_recientes = spo2[-7:] if len(spo2) >= 7 else spo2
        spo2_promedio = sum(s.get("porcentaje", 0) for s in spo2_recientes) / len(spo2_recientes)
    
    grasa_actual = grasa_corporal[-1]["porcentaje"] if grasa_corporal else None
    masa_muscular_actual = masa_muscular[-1]["masa_kg"] if masa_muscular else None
    
    fc_reposo_promedio = None
    if fc_reposo:
        fc_recientes = fc_reposo[-7:] if len(fc_reposo) >= 7 else fc_reposo
        fc_reposo_promedio = sum(fc.get("bpm", 0) for fc in fc_recientes) / len(fc_recientes)
    
    pasos_promedio = None
    if pasos:
        pasos_por_dia = defaultdict(list)
        for p in pasos:
            try:
                fecha = datetime.fromisoformat(p["fecha"].replace("Z", "")).strftime("%Y-%m-%d")
                pasos_por_dia[fecha].append(p.get("pasos", 0))
            except: continue
        fechas_ordenadas = sorted(pasos_por_dia.keys())[-7:]
        if fechas_ordenadas:
            total_pasos = sum(max(pasos_por_dia[f]) for f in fechas_ordenadas)
            pasos_promedio = total_pasos / len(fechas_ordenadas)
            
    presion_sistolica = None
    presion_diastolica = None
    if presion_arterial:
        presion_recientes = presion_arterial[-7:] if len(presion_arterial) >= 7 else presion_arterial
        presion_sistolica = sum(p.get("sistolica", 0) for p in presion_recientes) / len(presion_recientes)
        presion_diastolica = sum(p.get("diastolica", 0) for p in presion_recientes) / len(presion_recientes)
    
    # GLUCOSA Y HbA1c
    glucemia_data = calcular_glucemia_ayunas_postprandial(glucosa, dias=7) if glucosa else {"ayunas": None, "postprandial": None}
    hba1c_data = calcular_hba1c_estimada(glucosa, dias=90) if glucosa else {"hba1c": None, "glucosa_promedio": None, "num_mediciones": 0}
    
    # Promedios 7d para Healthspan
    peso_promedio_7d = None
    if peso:
        peso_recientes = peso[-7:] if len(peso) >= 7 else peso
        peso_promedio_7d = sum(p.get("peso", 0) for p in peso_recientes) / len(peso_recientes)
        
    grasa_promedio_7d = None
    if grasa_corporal:
        grasa_recientes = grasa_corporal[-7:] if len(grasa_corporal) >= 7 else grasa_corporal
        grasa_promedio_7d = sum(g.get("porcentaje", 0) for g in grasa_recientes) / len(grasa_recientes)
        
    masa_muscular_promedio_7d = None
    if masa_muscular:
        masa_recientes = masa_muscular[-7:] if len(masa_muscular) >= 7 else masa_muscular
        masa_muscular_promedio_7d = sum(m.get("masa_kg", 0) for m in masa_recientes) / len(masa_recientes)
        
    score_longevidad = calcular_score_longevidad(peso_actual, pai_semanal, vo2max, promedio_sueno_horas)
    recomendaciones = generar_recomendaciones(peso_actual, pai_semanal, promedio_sueno_horas)
    
    metricas_base = {
        "pai_semanal": pai_semanal,
        "peso_promedio_7d": peso_promedio_7d,
        "vo2max": vo2max,
        "tsb_promedio_7d": tsb_actual,
        "promedio_sueno": promedio_sueno_horas,
        "spo2_promedio": spo2_promedio,
        "grasa_promedio_7d": grasa_promedio_7d,
        "masa_muscular_promedio_7d": masa_muscular_promedio_7d,
        "fc_reposo_promedio": fc_reposo_promedio,
        "pasos_promedio": pasos_promedio,
        "presion_sistolica": presion_sistolica,
        "presion_diastolica": presion_diastolica,
    }
    
    healthspan_data = calcular_healthspan_index(metricas_base)
    
    return {
        **metricas_base,
        "peso_actual": peso_actual,
        "peso_hace_7_dias": peso_hace_7_dias,
        "grasa_actual": grasa_actual,
        "masa_muscular_actual": masa_muscular_actual,
        "tsb_actual": tsb_actual,
        "glucemia_ayunas": glucemia_data.get("ayunas"),
        "glucemia_postprandial": glucemia_data.get("postprandial"),
        "hba1c": hba1c_data.get("hba1c"),
        "hba1c_glucosa_promedio": hba1c_data.get("glucosa_promedio"),
        "hba1c_num_mediciones": hba1c_data.get("num_mediciones"),
        "tsb_dict": tsb_dict,
        "score_longevidad": score_longevidad,
        "recomendaciones": recomendaciones,
        "healthspan_data": healthspan_data
    }