#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plan de Acción Personalizado para Healthspan Index
Genera roadmap temporal con metas específicas
"""

def generar_plan_accion(healthspan_data, metricas):
    """
    Genera plan de acción detallado con roadmap temporal.
    
    Returns:
        dict: {
            "meta_actual": int (healthspan actual),
            "meta_6m": int (proyección 6 meses),
            "meta_12m": int (proyección 12 meses),
            "brecha_principal": str (score más bajo),
            "acciones_2m": list,
            "acciones_6m": list,
            "acciones_12m": list,
            "proyecciones": dict
        }
    """
    
    # Scores actuales
    fitness = healthspan_data["fitness_score"]
    body = healthspan_data["body_score"]
    recovery = healthspan_data["recovery_score"]
    metabolic = healthspan_data["metabolic_score"]
    functional = healthspan_data["functional_score"]
    index_actual = healthspan_data["healthspan_index"]
    
    # Métricas actuales
    grasa = metricas.get("grasa_actual", 0)
    peso = metricas.get("peso_actual", 0)
    masa_muscular = metricas.get("masa_muscular", 0)
    pasos = metricas.get("pasos_promedio", 0)
    pai = metricas.get("pai_semanal", 0)
    vo2max = metricas.get("vo2max", 0)
    
    # Identificar score más bajo
    scores = {
        "Fitness": fitness,
        "Body": body,
        "Recovery": recovery,
        "Metabolic": metabolic,
        "Functional": functional
    }
    brecha_principal = min(scores, key=scores.get)
    score_mas_bajo = scores[brecha_principal]
    
    # Generar plan según brecha principal
    plan = {
        "meta_actual": index_actual,
        "brecha_principal": brecha_principal,
        "score_mas_bajo": score_mas_bajo,
        "acciones_2m": [],
        "acciones_6m": [],
        "acciones_12m": [],
        "proyecciones": {}
    }
    
    # ═══════════════════════════════════════════════════════════════
    # PLAN ESPECÍFICO SEGÚN BRECHA PRINCIPAL
    # ═══════════════════════════════════════════════════════════════
    
    if brecha_principal == "Body" and body < 70:
        # Body Score es el cuello de botella
        deficit_grasa = grasa - 18  # Objetivo intermedio: 18%
        deficit_peso = peso - 79    # Objetivo de peso
        
        plan["acciones_2m"] = [
            {
                "titulo": "🎯 Déficit Calórico Moderado",
                "descripcion": f"Reducir ingesta en 300-500 kcal/día. Meta: perder ~2 kg en 2 meses.",
                "metrica": f"Peso actual: {peso:.1f} kg → Meta 2m: {peso - 2:.1f} kg",
                "prioridad": "ALTA"
            },
            {
                "titulo": "🥩 Proteína Alta",
                "descripcion": f"Consumir 2g/kg de peso. Protege masa muscular durante el déficit.",
                "metrica": f"Meta diaria: {int(peso * 2)}g de proteína",
                "prioridad": "ALTA"
            },
            {
                "titulo": "💪 Mantener Entrenamiento de Fuerza",
                "descripcion": "3x semana, ejercicios compuestos. Evita pérdida muscular.",
                "metrica": f"Masa muscular actual: {masa_muscular:.1f} kg (mantener)",
                "prioridad": "ALTA"
            }
        ]
        
        plan["acciones_6m"] = [
            {
                "titulo": "📉 Continuar Déficit",
                "descripcion": "Objetivo acumulado: -4 kg de grasa en 6 meses.",
                "metrica": f"Grasa corporal: {grasa:.1f}% → Meta 6m: ~19%",
                "prioridad": "ALTA"
            },
            {
                "titulo": "📊 Ajustar Según Progreso",
                "descripcion": "Si la pérdida se estanca, aumentar cardio o reducir 100 kcal más.",
                "metrica": "Evaluar cada 4 semanas",
                "prioridad": "MEDIA"
            }
        ]
        
        plan["acciones_12m"] = [
            {
                "titulo": "🏆 Meta Final: 15-17% Grasa",
                "descripcion": "Composición corporal óptima para longevidad.",
                "metrica": f"Grasa actual {grasa:.1f}% → Meta 12m: 15-17%",
                "prioridad": "ALTA"
            },
            {
                "titulo": "🔄 Fase de Mantenimiento",
                "descripcion": "Una vez alcanzado el objetivo, aumentar calorías gradualmente.",
                "metrica": "Estabilizar en peso objetivo: 78-79 kg",
                "prioridad": "MEDIA"
            }
        ]
        
        # Proyecciones
        plan["proyecciones"] = {
            "2m": {
                "body_score": min(body + 10, 100),
                "healthspan": index_actual + 2,
                "grasa": grasa - 1.5,
                "peso": peso - 2
            },
            "6m": {
                "body_score": min(body + 25, 100),
                "healthspan": index_actual + 5,
                "grasa": grasa - 4,
                "peso": peso - 4
            },
            "12m": {
                "body_score": 90,
                "healthspan": min(index_actual + 10, 100),
                "grasa": 16,
                "peso": 78
            }
        }
    
    elif brecha_principal == "Metabolic":
        plan["acciones_2m"] = [
            {
                "titulo": "🩺 Actualizar Laboratorios",
                "descripcion": "Solicitar análisis completo: HbA1c, Vitamina D, B12, Ferritina.",
                "metrica": "Laboratorios desactualizados detectados",
                "prioridad": "ALTA"
            }
        ]
        
        plan["proyecciones"] = {
            "2m": {
                "metabolic_score": 100,
                "healthspan": index_actual + 3
            }
        }
    
    elif brecha_principal == "Recovery" and recovery < 85:
        fc_reposo = metricas.get("fc_reposo", 60)
        plan["acciones_2m"] = [
            {
                "titulo": "🏃 Cardio Base",
                "descripcion": "Agregar 20-30 min de cardio zona 2 (conversacional), 3-4x/semana.",
                "metrica": f"FC reposo actual: {fc_reposo:.0f} bpm → Meta: <55 bpm",
                "prioridad": "MEDIA"
            }
        ]
        
        plan["proyecciones"] = {
            "6m": {
                "recovery_score": 100,
                "healthspan": index_actual + 1
            }
        }
    
    elif brecha_principal == "Functional" and functional < 80:
        plan["acciones_2m"] = [
            {
                "titulo": "🚶 Aumentar Pasos",
                "descripcion": "Objetivo: promedio ≥10,000 pasos/día.",
                "metrica": f"Pasos actuales: {pasos:,.0f}/día → Meta: 10,000/día",
                "prioridad": "MEDIA"
            }
        ]
        
        plan["proyecciones"] = {
            "2m": {
                "functional_score": 100,
                "healthspan": index_actual + 1
            }
        }
    
    else:
        # Ya está cerca de 100, dar recomendaciones de mantenimiento
        plan["acciones_2m"] = [
            {
                "titulo": "✅ Mantener Nivel Actual",
                "descripcion": "Tu Healthspan Index es excelente. Enfócate en consistencia.",
                "metrica": f"Index actual: {index_actual}/100",
                "prioridad": "BAJA"
            }
        ]
        plan["proyecciones"] = {
            "12m": {
                "healthspan": index_actual
            }
        }
    
    # Calcular metas proyectadas
    plan["meta_2m"] = plan["proyecciones"].get("2m", {}).get("healthspan", index_actual)
    plan["meta_6m"] = plan["proyecciones"].get("6m", {}).get("healthspan", index_actual)
    plan["meta_12m"] = plan["proyecciones"].get("12m", {}).get("healthspan", index_actual)
    
    return plan


def renderizar_plan_accion_html(plan):
    """
    Genera HTML del plan de acción.
    """
    
    brecha = plan["brecha_principal"]
    actual = plan["meta_actual"]
    meta_2m = plan["meta_2m"]
    meta_6m = plan["meta_6m"]
    meta_12m = plan["meta_12m"]
    
    html = f"""
    <div style="background: linear-gradient(135deg, #1e3a5f 0%, #2d5a7b 100%); 
                border-radius: 12px; padding: 30px; margin: 30px 0; 
                border: 1px solid rgba(255,255,255,0.1);">
        
        <h2 style="color: #58a6ff; font-size: 24px; margin-bottom: 20px; display: flex; align-items: center;">
            🎯 Plan de Acción Personalizado
        </h2>
        
        <div style="background: rgba(0,0,0,0.3); padding: 20px; border-radius: 8px; margin-bottom: 25px;">
            <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px;">
                <div style="text-align: center;">
                    <div style="color: #8b949e; font-size: 12px; margin-bottom: 5px;">ACTUAL</div>
                    <div style="color: #58a6ff; font-size: 32px; font-weight: bold;">{actual}</div>
                </div>
                <div style="text-align: center;">
                    <div style="color: #8b949e; font-size: 12px; margin-bottom: 5px;">META 2 MESES</div>
                    <div style="color: #3fb950; font-size: 32px; font-weight: bold;">{meta_2m}</div>
                </div>
                <div style="text-align: center;">
                    <div style="color: #8b949e; font-size: 12px; margin-bottom: 5px;">META 6 MESES</div>
                    <div style="color: #3fb950; font-size: 32px; font-weight: bold;">{meta_6m}</div>
                </div>
                <div style="text-align: center;">
                    <div style="color: #8b949e; font-size: 12px; margin-bottom: 5px;">META 12 MESES</div>
                    <div style="color: #f0883e; font-size: 32px; font-weight: bold;">{meta_12m}</div>
                </div>
            </div>
        </div>
        
        <div style="background: rgba(240, 136, 62, 0.1); border-left: 4px solid #f0883e; 
                    padding: 15px; border-radius: 6px; margin-bottom: 25px;">
            <strong style="color: #f0883e;">🎯 Prioridad Principal:</strong> 
            <span style="color: #c9d1d9;">Mejorar {brecha} Score (actualmente: {plan["score_mas_bajo"]}/100)</span>
        </div>
    """
    
    # Renderizar acciones por plazo
    plazos = [
        ("📅 Acciones Inmediatas (2 meses)", plan["acciones_2m"], "#3fb950"),
        ("📅 Metas Mediano Plazo (6 meses)", plan["acciones_6m"], "#58a6ff"),
        ("📅 Objetivo Final (12 meses)", plan["acciones_12m"], "#f0883e")
    ]
    
    for titulo_plazo, acciones, color in plazos:
        if acciones:
            html += f"""
            <div style="margin-bottom: 30px;">
                <h3 style="color: {color}; font-size: 18px; margin-bottom: 15px;">{titulo_plazo}</h3>
            """
            
            for accion in acciones:
                prioridad_color = {
                    "ALTA": "#f85149",
                    "MEDIA": "#d29922",
                    "BAJA": "#3fb950"
                }.get(accion["prioridad"], "#58a6ff")
                
                html += f"""
                <div style="background: rgba(0,0,0,0.3); padding: 20px; border-radius: 8px; 
                            margin-bottom: 15px; border-left: 4px solid {prioridad_color};">
                    <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 10px;">
                        <strong style="color: #c9d1d9; font-size: 16px;">{accion["titulo"]}</strong>
                        <span style="background: {prioridad_color}; color: white; padding: 4px 12px; 
                                     border-radius: 12px; font-size: 11px; font-weight: bold;">
                            {accion["prioridad"]}
                        </span>
                    </div>
                    <p style="color: #8b949e; margin: 10px 0; line-height: 1.6;">{accion["descripcion"]}</p>
                    <div style="background: rgba(88, 166, 255, 0.1); padding: 10px; border-radius: 4px; margin-top: 10px;">
                        <strong style="color: #58a6ff; font-size: 12px;">📊 Métrica:</strong>
                        <span style="color: #c9d1d9; font-size: 14px;"> {accion["metrica"]}</span>
                    </div>
                </div>
                """
            
            html += "</div>"
    
    # Proyecciones detalladas
    if "2m" in plan["proyecciones"]:
        proy = plan["proyecciones"]
        html += """
        <div style="margin-top: 30px;">
            <h3 style="color: #58a6ff; font-size: 18px; margin-bottom: 15px;">📈 Proyecciones de Mejora</h3>
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px;">
        """
        
        for plazo, datos in [("2 meses", "2m"), ("6 meses", "6m"), ("12 meses", "12m")]:
            if datos in proy:
                d = proy[datos]
                html += f"""
                <div style="background: rgba(0,0,0,0.3); padding: 15px; border-radius: 8px;">
                    <div style="color: #8b949e; font-size: 12px; margin-bottom: 10px;">{plazo.upper()}</div>
                """
                
                if "body_score" in d:
                    html += f'<div style="color: #c9d1d9; margin: 5px 0;">Body: {d["body_score"]}/100</div>'
                if "grasa" in d:
                    html += f'<div style="color: #c9d1d9; margin: 5px 0;">Grasa: {d["grasa"]:.1f}%</div>'
                if "peso" in d:
                    html += f'<div style="color: #c9d1d9; margin: 5px 0;">Peso: {d["peso"]:.1f} kg</div>'
                if "healthspan" in d:
                    html += f'<div style="color: #3fb950; font-weight: bold; margin-top: 10px;">Index: {d["healthspan"]}/100</div>'
                
                html += "</div>"
        
        html += "</div></div>"
    
    html += "</div>"
    
    return html