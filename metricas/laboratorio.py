#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de procesamiento de laboratorio clínico
Integración con dashboard de HealthConnect - CORREGIDO
"""

import json
from pathlib import Path
from datetime import datetime

def obtener_datos_laboratorio_y_alertas(edad=61, altura_cm=177, peso_kg=83, vo2max_medido=None, glucemias_diarias=None):
    """
    Procesa laboratorio y genera scores científicos.
    
    Args:
        edad: Edad del usuario
        altura_cm: Altura en cm
        peso_kg: Peso actual en kg
        vo2max_medido: VO2max medido por dispositivo (puede ser None)
        glucemias_diarias: Lista de mediciones diarias de glucosa [{"fecha": "", "valor": X}, ...]
        
    Returns:
        dict con scores, alertas y parámetros
    """
    
    # Buscar archivo de laboratorio
    rutas_posibles = [
        Path(r"H:\Mi unidad\HealthConnect Exports\LAB\lab_jcp.json"),
        Path("LAB/lab_jcp.json"),
        Path("../LAB/lab_jcp.json"),
        Path("cache/laboratorio_cache.json")
    ]
    
    laboratorio_data = None
    for ruta in rutas_posibles:
        if ruta.exists():
            try:
                with open(ruta, 'r', encoding='utf-8') as f:
                    laboratorio_data = json.load(f)
                break
            except:
                continue
    
    # Si no encuentra laboratorio, retornar estructura vacía
    if not laboratorio_data:
        return {
            "longevity_score": 0,
            "scores": {},
            "alertas": [],
            "parametros": {}
        }
    
    
    # ✅ EXTRAER PARÁMETROS REALES DE TODOS LOS INFORMES (valor más reciente de cada uno)
    parametros = _extraer_parametros_mas_recientes(laboratorio_data)
    
    # Calcular scores
    scores = calcular_scores_cientificos(parametros, vo2max_medido, peso_kg, altura_cm, edad)
    
    # Generar alertas (con glucemias diarias para evaluar control glucémico)
    alertas = generar_alertas_laboratorio(parametros, scores, glucemias_diarias)
    
    # Calcular Longevity Score integrado
    longevity_score = calcular_longevity_score(scores)
    
    return {
        "longevity_score": longevity_score,
        "scores": scores,
        "alertas": alertas,
        "parametros": parametros
    }


def calcular_scores_cientificos(parametros, vo2max, peso, altura, edad):
    """
    Calcula 4 scores científicos basados en laboratorio.
    MANEJA vo2max None correctamente.
    """
    scores = {}
    
    # CardioScore (0-100) - Riesgo cardiovascular
    # Solo penalizar si HAY datos y están mal, no inventar valores
    ldl = parametros.get("LDL", {}).get("valor")
    hdl = parametros.get("HDL", {}).get("valor")
    trig = parametros.get("Triglicéridos", {}).get("valor")
    pcr = parametros.get("PCR", {}).get("valor")
    
    cardio_score = 100
    
    # Solo evaluar si el dato existe
    if ldl is not None:
        if ldl > 130: cardio_score -= 30
        elif ldl > 100: cardio_score -= 15
    
    if hdl is not None:
        if hdl < 40: cardio_score -= 25
        elif hdl < 55: cardio_score -= 10
    
    if trig is not None:
        if trig > 150: cardio_score -= 15
    
    if pcr is not None:
        if pcr > 3: cardio_score -= 20
        elif pcr > 1: cardio_score -= 10
    
    # ✅ Bonus por VO2max alto (validar que no sea None)
    if vo2max is not None and vo2max > 40:
        cardio_score += 10
    
    scores["CardioScore"] = max(0, min(100, cardio_score))
    
    # MetabolicScore (0-100) - Salud metabólica
    glucemia = parametros.get("Glucemia", {}).get("valor")
    hba1c = parametros.get("HbA1c", {}).get("valor")
    
    metabolic_score = 100
    
    if hba1c is not None:
        if hba1c >= 6.5: metabolic_score -= 50
        elif hba1c >= 5.7: metabolic_score -= 25
    
    if glucemia is not None:
        if glucemia > 125: metabolic_score -= 30
        elif glucemia > 100: metabolic_score -= 15
    
    # IMC (validar altura > 0)
    if altura > 0:
        imc = peso / ((altura/100) ** 2)
        if imc > 30: metabolic_score -= 20
        elif imc > 25: metabolic_score -= 10
    
    scores["MetabolicScore"] = max(0, min(100, metabolic_score))
    
    # InflammationScore (0-100)
    inflammation_score = 100
    
    if pcr is not None:
        if pcr > 3: inflammation_score -= 40
        elif pcr > 1: inflammation_score -= 20
    
    ferritina = parametros.get("Ferritina", {}).get("valor")
    if ferritina is not None and ferritina > 300:
        inflammation_score -= 15
    
    scores["InflammationScore"] = max(0, min(100, inflammation_score))
    
    # HormoneScore (0-100)
    tsh = parametros.get("TSH", {}).get("valor")
    vit_d = parametros.get("Vitamina D", {}).get("valor")
    b12 = parametros.get("B12", {}).get("valor")
    
    hormone_score = 100
    
    if tsh is not None:
        if tsh > 4.0: hormone_score -= 20
        elif tsh < 0.4: hormone_score -= 15
    
    if vit_d is not None:
        if vit_d < 20: hormone_score -= 25
        elif vit_d < 30: hormone_score -= 10
    
    if b12 is not None:
        if b12 < 200: hormone_score -= 20
        elif b12 < 400: hormone_score -= 10
    scores["HormoneScore"] = max(0, min(100, hormone_score))
    
    return scores


def calcular_longevity_score(scores):
    """Calcula score integrado de longevidad con ponderación."""
    if not scores:
        return 0
        
    ponderacion = {
        "CardioScore": 0.40,
        "MetabolicScore": 0.30,
        "InflammationScore": 0.20,
        "HormoneScore": 0.10
    }
    
    score_total = 0
    for nombre, peso in ponderacion.items():
        score_total += scores.get(nombre, 0) * peso
    
    return round(score_total, 1)


def generar_alertas_laboratorio(parametros, scores, glucemias_diarias=None):
    """
    Genera alertas basadas en valores de laboratorio.
    Considera glucemias diarias para evaluar control glucémico real.
    """
    import logging
    logger = logging.getLogger(__name__)
    
    alertas = []
    
    # DEBUG: Log de glucemias recibidas
    if glucemias_diarias:
        logger.info(f"📊 Glucemias diarias recibidas: {len(glucemias_diarias)} registros")
    else:
        logger.info("⚠️ NO se recibieron glucemias diarias - Se usará solo HbA1c")
    
    # ✅ ALERTAS CRÍTICAS - HbA1c CON LÓGICA INTELIGENTE
    hba1c_valor = parametros.get("HbA1c", {}).get("valor")
    hba1c_fecha = parametros.get("HbA1c", {}).get("fecha")
    
    # Calcular promedio de glucemias diarias recientes (últimos 90 días)
    glucemia_promedio_reciente = None
    if glucemias_diarias and len(glucemias_diarias) > 0:
        from datetime import datetime, timedelta
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"🔍 DEBUG Glucemias: Recibidas {len(glucemias_diarias)} mediciones")
        
        fecha_limite = datetime.now() - timedelta(days=90)
        
        glucemias_recientes = []
        for g in glucemias_diarias:
            try:
                fecha_g = datetime.fromisoformat(g.get("fecha", "").replace("Z", "+00:00"))
                # Convertir a naive para comparar
                fecha_g_naive = fecha_g.replace(tzinfo=None)
                
                if fecha_g_naive >= fecha_limite:
                    # ✅ Buscar valor en diferentes campos (Samsung Health usa "nivel_mg_dl")
                    valor = g.get("nivel_mg_dl") or g.get("valor") or g.get("glucosa")
                    if valor is not None:
                        glucemias_recientes.append(valor)
            except Exception as e:
                logger.debug(f"Error procesando glucemia: {e}")
                continue
        
        if glucemias_recientes:
            glucemia_promedio_reciente = sum(glucemias_recientes) / len(glucemias_recientes)
            logger.info(f"📈 Promedio glucemias últimos 90d: {glucemia_promedio_reciente:.1f} mg/dL ({len(glucemias_recientes)} mediciones)")
        else:
            logger.info("⚠️ No se encontraron glucemias en los últimos 90 días")
    else:
        logger = logging.getLogger(__name__)
        if glucemias_diarias is None:
            logger.info("ℹ️ glucemias_diarias = None (no se pasaron datos)")
        else:
            logger.info(f"ℹ️ glucemias_diarias = lista vacía (len={len(glucemias_diarias)})")
    
    # Decidir qué alerta generar según datos disponibles
    if glucemia_promedio_reciente is not None:
        # ✅ HAY GLUCEMIAS DIARIAS RECIENTES - Usar como referencia principal
        if glucemia_promedio_reciente >= 126:
            alertas.append({
                "severidad": "CRITICA",
                "titulo": "⚠️ Glucemia Elevada Persistente",
                "descripcion": f"Promedio de glucemias últimos 90 días: {glucemia_promedio_reciente:.1f} mg/dL (límite: 126). Indica diabetes no controlada.",
                "accion": "URGENTE: Consultar endocrinólogo para ajuste de medicación"
            })
        elif glucemia_promedio_reciente >= 100:
            alertas.append({
                "severidad": "MODERADA",
                "titulo": "⚠️ Glucemias en Rango Pre-diabético",
                "descripcion": f"Promedio de glucemias últimos 90 días: {glucemia_promedio_reciente:.1f} mg/dL (objetivo: <100). Control glucémico subóptimo.",
                "accion": "Revisar dieta, ejercicio y medicación con tu médico"
            })
        else:
            # Glucemias bien controladas - NO alertar prediabetes aunque HbA1c vieja diga 5.7%
            if hba1c_valor is not None and hba1c_valor >= 5.7:
                logger.info(f"✅ Control glucémico EXCELENTE detectado - NO se alerta prediabetes (HbA1c vieja: {hba1c_valor}%)")
                alertas.append({
                    "severidad": "BUENA",
                    "titulo": "✅ Control Glucémico Actual: EXCELENTE",
                    "descripcion": f"Glucemias recientes bien controladas (promedio: {glucemia_promedio_reciente:.1f} mg/dL). Tu tratamiento funciona correctamente.",
                    "accion": "Continuar con tratamiento actual. HbA1c probablemente mejoró desde último análisis."
                })
    
    elif hba1c_valor is not None and hba1c_valor >= 5.7:
        # ⚠️ NO HAY GLUCEMIAS DIARIAS - Usar HbA1c como referencia
        alertas.append({
            "severidad": "CRITICA",
            "titulo": "Prediabetes Detectada",
            "descripcion": f"HbA1c en {hba1c_valor}% indica prediabetes",
            "accion": "Consultar endocrinólogo. Considerar mediciones diarias de glucosa para mejor control.",
            "impacto_longevidad": "-5 a -10 años si progresa"
        })
    
    # Alertas de riesgo alto
    hdl = parametros.get("HDL", {}).get("valor")
    if hdl is not None and hdl < 40:
        alertas.append({
            "severidad": "ALTA",
            "titulo": "HDL Muy Bajo",
            "descripcion": f"HDL en {hdl} mg/dL aumenta riesgo CV",
            "accion": "Aumentar ejercicio aeróbico y omega-3",
            "impacto_longevidad": "-3 años por riesgo CV"
        })
    
    tsh = parametros.get("TSH", {}).get("valor")
    if tsh is not None and tsh > 4.0:
        alertas.append({
            "severidad": "ALTA",
            "titulo": "Hipotiroidismo Subclínico",
            "descripcion": f"TSH en {tsh} mUI/L indica tiroides lenta",
            "accion": "Evaluar T3/T4",
            "impacto_longevidad": "Fatiga crónica, metabolismo lento"
        })
    
    # Alertas moderadas
    pcr = parametros.get("PCR", {}).get("valor")
    if pcr is not None and pcr > 1.0:
        alertas.append({
            "severidad": "MODERADA",
            "titulo": "Inflamación Sistémica Leve",
            "descripcion": f"PCR en {pcr} mg/L indica inflamación",
            "accion": "Dieta antiinflamatoria",
            "impacto_longevidad": "Envejecimiento acelerado"
        })
    
    # Alertas positivas
    ldl = parametros.get("LDL", {}).get("valor")
    if ldl is not None and ldl < 70:
        alertas.append({
            "severidad": "BUENA",
            "titulo": "LDL Excelente",
            "descripcion": f"LDL en {ldl} mg/dL es óptimo",
            "accion": "Mantener régimen actual",
            "impacto_longevidad": "+3 años de protección CV"
        })
    
    # ✅ ALERTAS INTELIGENTES: PARÁMETROS FALTANTES O DESACTUALIZADOS
    from datetime import datetime, timedelta
    
    # Parámetros CRÍTICOS para Healthspan (impactan scores principales)
    parametros_criticos = {
        "HbA1c": "Hemoglobina Glicosilada (control glucémico - crítico para MetabolicScore)",
        "LDL": "Colesterol LDL (riesgo cardiovascular - crítico para CardioScore)",
        "HDL": "Colesterol HDL (protección cardiovascular - crítico para CardioScore)",
        "Triglicéridos": "Triglicéridos (perfil lipídico - crítico para CardioScore)",
        "PCR": "Proteína C Reactiva (inflamación - crítico para InflammationScore)",
        "TSH": "TSH (función tiroidea - importante para HormoneScore)"
    }
    
    # Parámetros IMPORTANTES (complementarios)
    parametros_importantes = {
        "Vitamina D": "Vitamina D (salud ósea e inmune)",
        "Ferritina": "Ferritina (reservas de hierro)",
        "B12": "Vitamina B12 (función neurológica)",
        "Glucemia": "Glucosa en ayunas"
    }
    
    fecha_actual = datetime.now()
    limite_12_meses = fecha_actual - timedelta(days=365)
    
    # Revisar parámetros CRÍTICOS
    for param, descripcion in parametros_criticos.items():
        param_data = parametros.get(param, {})
        valor = param_data.get("valor")
        fecha_str = param_data.get("fecha")
        
        if valor is None:
            # CRÍTICO FALTANTE
            alertas.append({
                "severidad": "ALTA",
                "titulo": f"⚠️ Análisis Crítico Faltante: {param}",
                "descripcion": f"No se encontró {descripcion}. Este parámetro es crítico para tu Healthspan Index.",
                "accion": "IMPORTANTE: Solicitar este análisis a tu médico en el próximo control"
            })
        elif fecha_str:
            # Verificar antigüedad
            try:
                fecha_analisis = datetime.strptime(fecha_str, "%Y-%m-%d")
                if fecha_analisis < limite_12_meses:
                    meses_antiguedad = int((fecha_actual - fecha_analisis).days / 30)
                    alertas.append({
                        "severidad": "MODERADA",
                        "titulo": f"🕐 Actualizar: {param}",
                        "descripcion": f"Tu último análisis de {param} tiene {meses_antiguedad} meses (fecha: {fecha_str}). Se recomienda actualizar.",
                        "accion": f"Solicitar nuevo análisis de {param} en tu próximo control"
                    })
            except:
                pass
    
    # Revisar parámetros IMPORTANTES (no críticos)
    for param, descripcion in parametros_importantes.items():
        param_data = parametros.get(param, {})
        valor = param_data.get("valor")
        fecha_str = param_data.get("fecha")
        
        if valor is None:
            # IMPORTANTE FALTANTE (severidad INFO, no ALTA)
            alertas.append({
                "severidad": "INFO",
                "titulo": f"📋 Considerar análisis: {param}",
                "descripcion": f"No se encontró {descripcion}. Recomendado para evaluación completa.",
                "accion": "Opcional: Consultar con tu médico si es necesario este análisis"
            })
        elif fecha_str:
            # Verificar antigüedad
            try:
                fecha_analisis = datetime.strptime(fecha_str, "%Y-%m-%d")
                if fecha_analisis < limite_12_meses:
                    meses_antiguedad = int((fecha_actual - fecha_analisis).days / 30)
                    alertas.append({
                        "severidad": "INFO",
                        "titulo": f"🕐 {param} desactualizado",
                        "descripcion": f"Último análisis: {fecha_str} ({meses_antiguedad} meses). Considera actualizar.",
                        "accion": f"Opcional: Solicitar {param} en próximo control"
                    })
            except:
                pass
    
    return alertas

def _extraer_parametros_ultimo_informe(laboratorio_data):
    """
    Extrae parámetros REALES del JSON de laboratorio.
    Lee el informe más reciente y construye el diccionario de parámetros.
    """
    informes = laboratorio_data.get("informes", [])
    if not informes:
        return {}
    
    # Ordenar por fecha y tomar el más reciente
    informes_ordenados = sorted(
        informes, 
        key=lambda x: datetime.strptime(x.get("fecha_estudio", "2000-01-01"), "%Y-%m-%d"),
        reverse=True
    )
    ultimo_informe = informes_ordenados[0]
    resultados = ultimo_informe.get("resultados", {})
    
    parametros = {}
    
    # Extraer de perfil_lipidico
    perfil = resultados.get("perfil_lipidico", [])
    for item in perfil:
        param = item.get("parametro", "")
        if "Colesterol Total" in param:
            parametros["Colesterol Total"] = {
                "valor": item.get("valor"),
                "rango": item.get("rango_referencia", ""),
                "estado": _evaluar_estado(item)
            }
        elif "LDL" in param:
            parametros["LDL"] = {
                "valor": item.get("valor"),
                "rango": item.get("rango_referencia", ""),
                "estado": _evaluar_estado(item)
            }
        elif "HDL" in param:
            parametros["HDL"] = {
                "valor": item.get("valor"),
                "rango": item.get("rango_referencia", ""),
                "estado": _evaluar_estado(item)
            }
        elif "Triglicéridos" in param or "Trigliceridos" in param:
            parametros["Triglicéridos"] = {
                "valor": item.get("valor"),
                "rango": item.get("rango_referencia", ""),
                "estado": _evaluar_estado(item)
            }
    
    # Extraer de quimica_sanguinea
    quimica = resultados.get("quimica_sanguinea", [])
    for item in quimica:
        param = item.get("parametro", "")
        if "Glucosa" in param:
            parametros["Glucemia"] = {
                "valor": item.get("valor"),
                "rango": item.get("rango_referencia", ""),
                "estado": _evaluar_estado(item)
            }
        elif "Hemoglobina Glicosilada" in param or "A1C" in param:
            parametros["HbA1c"] = {
                "valor": item.get("valor"),
                "rango": item.get("rango_referencia", ""),
                "estado": _evaluar_estado(item)
            }
    
    # Extraer de endocrinologia
    endocrino = resultados.get("endocrinologia", [])
    if not endocrino:
        endocrino = resultados.get("endocrinologia_y_marcadores", [])
    
    for item in endocrino:
        param = item.get("parametro", "")
        if "TSH" in param or "Tirotrofina" in param:
            parametros["TSH"] = {
                "valor": item.get("valor"),
                "rango": item.get("rango_referencia", ""),
                "estado": _evaluar_estado(item)
            }
        elif "Vitamina D" in param:
            parametros["Vitamina D"] = {
                "valor": item.get("valor"),
                "rango": item.get("rango_referencia", ""),
                "estado": _evaluar_estado(item)
            }
    
    # PCR, Ferritina, B12 - buscar en varias secciones
    # Por ahora dejar vacíos si no se encuentran
    if "PCR" not in parametros:
        parametros["PCR"] = {"valor": None, "rango": "", "estado": "N/A"}
    if "Ferritina" not in parametros:
        parametros["Ferritina"] = {"valor": None, "rango": "", "estado": "N/A"}
    if "B12" not in parametros:
        parametros["B12"] = {"valor": None, "rango": "", "estado": "N/A"}
    
    return parametros


def _evaluar_estado(item):
    """Evalúa si un parámetro está en rango o no (simplificado)"""
    # Por ahora retornar "normal" - se puede mejorar con lógica de rangos
    return "normal"
def _extraer_parametros_mas_recientes(laboratorio_data):
    """
    Extrae parámetros REALES de TODOS los informes del JSON.
    Para cada parámetro, toma el valor MÁS RECIENTE disponible.
    NO inventa valores - solo usa datos reales del JSON.
    """
    from datetime import datetime
    
    informes = laboratorio_data.get("informes", [])
    if not informes:
        return {}
    
    # Ordenar informes por fecha (más reciente primero)
    informes_ordenados = sorted(
        informes,
        key=lambda x: datetime.strptime(x.get("fecha_estudio", "2000-01-01"), "%Y-%m-%d"),
        reverse=True
    )
    
    # Diccionario para almacenar el valor más reciente de cada parámetro
    parametros = {}
    
    # Mapeo de parámetros clave
    mapeo_parametros = {
        "Colesterol Total": ["COLESTEROL TOTAL", "COLESTEROL"],
        "LDL": ["LDL", "COLESTEROL LDL"],
        "HDL": ["HDL", "COLESTEROL HDL"],
        "Triglicéridos": ["TRIGLICERIDOS", "TRIGLICÉRIDOS"],
        "Glucemia": ["GLUCOSA", "GLUCEMIA", "GLUCOSA (BASAL)", "GLUCEMIA (BASAL)"],
        "HbA1c": ["HBA1C", "HEMOGLOBINA GLICOSILADA", "A1C"],
        "PCR": ["PCR", "PROTEINA C REACTIVA", "PROTEÍNA C REACTIVA"],
        "TSH": ["TSH", "TIROTROFINA"],
        "Vitamina D": ["VITAMINA D", "VITAMINA D 25 OH", "25-OH VITAMINA D"],
        "B12": ["B12", "VITAMINA B12", "COBALAMINA"],
        "Ferritina": ["FERRITINA"]
    }
    
    # Iterar sobre todos los informes (del más reciente al más antiguo)
    for informe in informes_ordenados:
        resultados = informe.get("resultados", {})
        fecha_informe = informe.get("fecha_estudio", "N/A")
        
        # Buscar en todas las secciones posibles
        todas_secciones = []
        for seccion_key, seccion_datos in resultados.items():
            if isinstance(seccion_datos, list):
                todas_secciones.extend(seccion_datos)
        
        # Buscar cada parámetro que aún no tenemos
        for param_nombre, variantes in mapeo_parametros.items():
            # Si ya encontramos este parámetro en un informe más reciente, saltar
            if param_nombre in parametros:
                continue
            
            # Buscar el parámetro en este informe
            for item in todas_secciones:
                if not isinstance(item, dict):
                    continue
                
                param_item = item.get("parametro", "").upper()
                valor = item.get("valor")
                
                # Verificar si coincide con alguna variante
                if any(variante in param_item for variante in variantes):
                    # Manejar PCR con "Menor de 0.6"
                    if param_nombre == "PCR" and isinstance(valor, str) and "menor" in valor.lower():
                        # Extraer número si es posible
                        try:
                            valor = float(valor.lower().replace("menor de", "").replace("menor a", "").strip())
                        except:
                            valor = 0.5  # Asumir valor bajo si dice "menor de X"
                    
                    parametros[param_nombre] = {
                        "valor": valor,
                        "rango": item.get("rango_referencia", ""),
                        "fecha": fecha_informe
                    }
                    break  # Encontrado, pasar al siguiente parámetro
    
    return parametros