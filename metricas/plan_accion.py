#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plan de Acción - Sistema de Adherencia y Predicción
Monitorea cumplimiento del plan de déficit calórico y proteína
"""

from datetime import datetime, timedelta


def generar_plan_accion(metricas, nutrition_data, tmb_data, calorias_data):
    """
    Genera plan de acción basado en adherencia a 7 días.
    """
    
    print("=" * 60)
    print("🎯 GENERANDO PLAN DE ACCIÓN - ADHERENCIA 7 DÍAS")
    print("=" * 60)
    
    # Constantes
    PESO_META = 79.0
    PROTEINA_META = 160  # gramos/día
    DEFICIT_MIN = 0   # ✅ Cualquier déficit positivo cuenta
    
    # ═══════════════════════════════════════════════════════════════
    # 1. CALCULAR DÉFICIT CALÓRICO DIARIO (últimos 7 días)
    # ═══════════════════════════════════════════════════════════════
    
    from outputs.prep_graficos_activity import calcular_deficit_calorico
    
    datos_deficit = calcular_deficit_calorico(nutrition_data, tmb_data, calorias_data, dias=7)
    
    print(f"📊 Datos de déficit (7 días): {len(datos_deficit.get('fechas', []))} días")
    print(f"   Déficits: {datos_deficit.get('deficit', [])}")
    
    # ═══════════════════════════════════════════════════════════════
    # 2. ANALIZAR ADHERENCIA AL DÉFICIT CALÓRICO
    # ═══════════════════════════════════════════════════════════════
    
    dias_deficit_ok = 0
    total_dias_deficit = 0
    
    deficits = datos_deficit.get("deficit", [])
    
    for deficit in deficits:
        if deficit != 0:  # Solo contar días con datos
            total_dias_deficit += 1
            # Déficit debe ser positivo (comiste menos de lo presupuestado)
            if deficit > DEFICIT_MIN:
                dias_deficit_ok += 1
    
    porcentaje_adherencia_deficit = (dias_deficit_ok / total_dias_deficit * 100) if total_dias_deficit > 0 else 0
    
    print(f"✅ Adherencia déficit: {dias_deficit_ok}/{total_dias_deficit} días ({porcentaje_adherencia_deficit:.0f}%)")
    
    # ═══════════════════════════════════════════════════════════════
    # 3. ANALIZAR ADHERENCIA A PROTEÍNA
    # ═══════════════════════════════════════════════════════════════
    
    dias_proteina_ok = 0
    total_dias_proteina = 0
    
    # Agrupar nutrition_data por día
    proteina_por_dia = {}
    
    print(f"📊 Total registros nutrition_data: {len(nutrition_data) if nutrition_data else 0}")
    
    if nutrition_data:
        for n in nutrition_data:
            try:
                fecha = datetime.fromisoformat(n["timestamp"].replace("Z", "+00:00"))
                dia = fecha.strftime("%Y-%m-%d")
                
                proteina = n.get("protein_g", 0)  # ✅ CORREGIDO: sin acento
                
                if dia not in proteina_por_dia:
                    proteina_por_dia[dia] = 0
                proteina_por_dia[dia] += proteina
            except Exception as e:
                continue
    
    print(f"📊 Días con datos de proteína: {list(proteina_por_dia.keys())[:10]}")  # Solo primeros 10
    
    # Analizar últimos 7 días
    hoy = datetime.now()
    ultimos_7_dias = []
    for i in range(7):
        dia = (hoy - timedelta(days=i)).strftime("%Y-%m-%d")
        ultimos_7_dias.append(dia)
        
        if dia in proteina_por_dia:
            total_dias_proteina += 1
            prot = proteina_por_dia[dia]
            cumple = prot >= PROTEINA_META
            print(f"   {dia}: {prot:.0f}g {'✅' if cumple else '❌'}")
            if cumple:
                dias_proteina_ok += 1
    
    porcentaje_adherencia_proteina = (dias_proteina_ok / total_dias_proteina * 100) if total_dias_proteina > 0 else 0
    
    print(f"🥩 Adherencia proteína: {dias_proteina_ok}/{total_dias_proteina} días ({porcentaje_adherencia_proteina:.0f}%)")
    
    # ═══════════════════════════════════════════════════════════════
    # 4. BARRA DE PROGRESO DE PESO (VENTANA MÓVIL 7 DÍAS)
    # ═══════════════════════════════════════════════════════════════
    
    peso_actual = metricas.get("peso_actual", 0)
    peso_hace_7_dias = metricas.get("peso_hace_7_dias", peso_actual)  # Buscar en cache
    
    # Buscar peso inicial (hace 2 meses o el más viejo registrado)
    peso_inicial = 83.0  # Valor de referencia fijo
    
    kg_perdidos_total = peso_inicial - peso_actual
    kg_faltantes = peso_actual - PESO_META
    
    progreso_porcentaje = 0
    if peso_inicial > PESO_META:
        progreso_porcentaje = (kg_perdidos_total / (peso_inicial - PESO_META)) * 100
    
    print(f"⚖️  Peso inicial: {peso_inicial:.1f}kg")
    print(f"⚖️  Peso actual: {peso_actual:.1f}kg")
    print(f"⚖️  Peso hace 7 días: {peso_hace_7_dias:.1f}kg")
    print(f"⚖️  Peso meta: {PESO_META}kg")
    print(f"📊 Progreso total: {progreso_porcentaje:.1f}% ({kg_perdidos_total:.1f}kg perdidos, faltan {kg_faltantes:.1f}kg)")
    
    # ═══════════════════════════════════════════════════════════════
    # 5. ALERTAS DINÁMICAS
    # ═══════════════════════════════════════════════════════════════
    
    alertas = []
    
    # PAI
    pai = metricas.get("pai_semanal", 0)
    if pai < 100:
        alertas.append({
            "tipo": "warning",
            "icono": "⚠️",
            "titulo": "PAI Insuficiente",
            "mensaje": f"PAI actual: {pai:.0f}/100. Meta: ≥100 para salud cardiovascular óptima."
        })
    else:
        alertas.append({
            "tipo": "success",
            "icono": "✅",
            "titulo": "PAI Excelente",
            "mensaje": f"PAI: {pai:.0f}/100. ¡Mantén este nivel de actividad!"
        })
    
    # Proteína baja últimos 3 días
    ultimos_3_dias = []
    for i in range(3):
        dia = (hoy - timedelta(days=i)).strftime("%Y-%m-%d")
        ultimos_3_dias.append(dia)
    
    proteina_baja_consecutiva = all(
        proteina_por_dia.get(d, 0) < PROTEINA_META for d in ultimos_3_dias if d in proteina_por_dia
    )
    
    if proteina_baja_consecutiva and total_dias_proteina >= 3:
        alertas.append({
            "tipo": "danger",
            "icono": "🥩",
            "titulo": "Proteína Baja 3 Días Seguidos",
            "mensaje": f"Riesgo de pérdida muscular. Meta: {PROTEINA_META}g/día. Agrega 1 snack proteico."
        })
    
    # Adherencia general
    adherencia_promedio = (porcentaje_adherencia_deficit + porcentaje_adherencia_proteina) / 2
    
    if adherencia_promedio >= 80:
        alertas.append({
            "tipo": "success",
            "icono": "🎯",
            "titulo": "Buena Adherencia al Plan",
            "mensaje": f"{adherencia_promedio:.0f}% de cumplimiento. ¡Vas por buen camino!"
        })
    elif adherencia_promedio < 50 and total_dias_proteina > 0:
        alertas.append({
            "tipo": "danger",
            "icono": "⚠️",
            "titulo": "Adherencia Baja",
            "mensaje": f"Solo {adherencia_promedio:.0f}% de cumplimiento. Revisa tu plan."
        })
    
    # ═══════════════════════════════════════════════════════════════
    # 6. PREDICCIÓN (VENTANA MÓVIL 7 DÍAS)
    # ═══════════════════════════════════════════════════════════════
    
    # ✅ CORREGIDO: kg/semana = peso hace 7 días - peso actual
    kg_por_semana = peso_hace_7_dias - peso_actual
    
    print(f"🔮 Cálculo kg/semana: {peso_hace_7_dias:.1f}kg (hace 7d) - {peso_actual:.1f}kg (hoy) = {kg_por_semana:.2f} kg/semana")
    
    # Si hay progreso, calcular semanas restantes
    semanas_restantes = 0
    tiempo_estimado = "N/A"
    
    if kg_por_semana > 0.05:  # Mínimo 50g/semana para considerar progreso real
        semanas_restantes = kg_faltantes / kg_por_semana
        
        if semanas_restantes < 4:
            tiempo_estimado = f"{int(semanas_restantes)} semanas"
        else:
            meses = int(semanas_restantes / 4)
            semanas = int(semanas_restantes % 4)
            tiempo_estimado = f"{meses} meses" + (f" y {semanas} semanas" if semanas > 0 else "")
    
    prediccion = {
        "kg_por_semana": kg_por_semana,
        "semanas_restantes": semanas_restantes,
        "tiempo_estimado": tiempo_estimado,
        "adherencia_actual": adherencia_promedio
    }
    
    print(f"🔮 Predicción: {kg_por_semana:.2f} kg/semana → {tiempo_estimado} para llegar a meta")
    print("=" * 60)
    
    # ═══════════════════════════════════════════════════════════════
    # RETORNAR PLAN
    # ═══════════════════════════════════════════════════════════════
    
    return {
        "adherencia_deficit": {
            "dias_cumplidos": dias_deficit_ok,
            "total_dias": total_dias_deficit,
            "porcentaje": porcentaje_adherencia_deficit
        },
        "adherencia_proteina": {
            "dias_cumplidos": dias_proteina_ok,
            "total_dias": total_dias_proteina,
            "porcentaje": porcentaje_adherencia_proteina
        },
        "peso_inicial": peso_inicial,
        "peso_actual": peso_actual,
        "peso_meta": PESO_META,
        "progreso_porcentaje": progreso_porcentaje,
        "kg_perdidos": kg_perdidos_total,
        "kg_faltantes": kg_faltantes,
        "alertas": alertas,
        "prediccion": prediccion
    }


def renderizar_plan_accion_html(plan):
    """
    Genera HTML del plan de acción con adherencia.
    """
    
    adh_deficit = plan["adherencia_deficit"]
    adh_proteina = plan["adherencia_proteina"]
    
    peso_inicial = plan["peso_inicial"]
    peso_actual = plan["peso_actual"]
    peso_meta = plan["peso_meta"]
    progreso = plan["progreso_porcentaje"]
    kg_perdidos = plan["kg_perdidos"]
    kg_faltantes = plan["kg_faltantes"]
    
    alertas = plan["alertas"]
    pred = plan["prediccion"]
    
    # Color según adherencia
    def color_adherencia(pct):
        if pct >= 80:
            return "#3fb950"
        elif pct >= 50:
            return "#d29922"
        else:
            return "#f85149"
    
    color_deficit = color_adherencia(adh_deficit["porcentaje"])
    color_proteina = color_adherencia(adh_proteina["porcentaje"])
    
    html = f"""
    <div style="background: linear-gradient(135deg, #1e3a5f 0%, #2d5a7b 100%); 
                border-radius: 12px; padding: 30px; margin: 30px 0; 
                border: 1px solid rgba(255,255,255,0.1);">
        
        <h2 style="color: #58a6ff; font-size: 24px; margin-bottom: 20px; display: flex; align-items: center;">
            📋 Plan de Implementación
        </h2>
        
        <!-- Adherencia al Plan (7 días) -->
        <div style="background: rgba(0,0,0,0.3); padding: 20px; border-radius: 8px; margin-bottom: 25px;">
            <h3 style="color: #c9d1d9; font-size: 18px; margin-bottom: 15px;">
                1. Adherencia al Plan (7 días)
            </h3>
            
            <!-- Déficit Calórico -->
            <div style="margin-bottom: 15px;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                    <span style="color: #8b949e;">🔥 Déficit: Días en déficit calórico (>0 kcal)</span>
                    <span style="color: {color_deficit}; font-weight: bold;">
                        {adh_deficit["dias_cumplidos"]}/{adh_deficit["total_dias"]} días ({adh_deficit["porcentaje"]:.0f}%)
                    </span>
                </div>
                <div style="background: rgba(139, 148, 158, 0.3); height: 8px; border-radius: 4px; overflow: hidden;">
                    <div style="background: {color_deficit}; height: 100%; width: {adh_deficit['porcentaje']}%; transition: width 0.3s;"></div>
                </div>
            </div>
            
            <!-- Proteína -->
            <div style="margin-bottom: 10px;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                    <span style="color: #8b949e;">🥩 Proteína: >160g (tu meta)</span>
                    <span style="color: {color_proteina}; font-weight: bold;">
                        {adh_proteina["dias_cumplidos"]}/{adh_proteina["total_dias"]} días ({adh_proteina["porcentaje"]:.0f}%)
                    </span>
                </div>
                <div style="background: rgba(139, 148, 158, 0.3); height: 8px; border-radius: 4px; overflow: hidden;">
                    <div style="background: {color_proteina}; height: 100%; width: {adh_proteina['porcentaje']}%; transition: width 0.3s;"></div>
                </div>
            </div>
            
            <!-- % Cumplimiento -->
            <div style="margin-top: 15px; padding: 10px; background: rgba(88, 166, 255, 0.1); border-radius: 6px;">
                <span style="color: #58a6ff; font-size: 12px;">Calculado % días cumpliendo</span>
            </div>
        </div>
        
        <!-- Barra de Progreso -->
        <div style="background: rgba(0,0,0,0.3); padding: 20px; border-radius: 8px; margin-bottom: 25px;">
            <h3 style="color: #c9d1d9; font-size: 18px; margin-bottom: 15px;">
                2. Barra de Progreso
            </h3>
            
            <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                <div style="text-align: left;">
                    <div style="color: #8b949e; font-size: 11px;">PESO INICIAL</div>
                    <div style="color: #f85149; font-size: 18px; font-weight: bold;">{peso_inicial:.1f} kg</div>
                </div>
                <div style="text-align: center;">
                    <div style="color: #8b949e; font-size: 11px;">PESO ACTUAL</div>
                    <div style="color: #58a6ff; font-size: 18px; font-weight: bold;">{peso_actual:.1f} kg</div>
                </div>
                <div style="text-align: right;">
                    <div style="color: #8b949e; font-size: 11px;">PESO META</div>
                    <div style="color: #3fb950; font-size: 18px; font-weight: bold;">{peso_meta:.1f} kg</div>
                </div>
            </div>
            
            <!-- Barra de progreso -->
            <div style="background: rgba(139, 148, 158, 0.3); height: 20px; border-radius: 10px; overflow: hidden; margin-bottom: 10px;">
                <div style="background: linear-gradient(90deg, #3fb950 0%, #58a6ff 100%); height: 100%; width: {min(progreso, 100)}%; transition: width 0.5s;"></div>
            </div>
            
            <div style="text-align: center; color: #c9d1d9; font-size: 14px;">
                % progreso = ({kg_perdidos:.1f} kg perdidos / {peso_inicial - peso_meta:.1f} kg total) = {progreso:.1f}%
            </div>
        </div>
        
        <!-- Alertas Dinámicas -->
        <div style="background: rgba(0,0,0,0.3); padding: 20px; border-radius: 8px; margin-bottom: 25px;">
            <h3 style="color: #c9d1d9; font-size: 18px; margin-bottom: 15px;">
                3. Alertas Dinámicas
            </h3>
    """
    
    # Renderizar alertas
    for alerta in alertas:
        color_map = {
            "success": "#3fb950",
            "warning": "#d29922",
            "danger": "#f85149"
        }
        color = color_map.get(alerta["tipo"], "#58a6ff")
        
        html += f"""
            <div style="background: rgba(0,0,0,0.2); padding: 15px; border-radius: 6px; 
                        margin-bottom: 10px; border-left: 4px solid {color};">
                <div style="display: flex; align-items: start; gap: 10px;">
                    <span style="font-size: 24px;">{alerta["icono"]}</span>
                    <div>
                        <div style="color: #c9d1d9; font-weight: bold; margin-bottom: 5px;">
                            {alerta["titulo"]}
                        </div>
                        <div style="color: #8b949e; font-size: 14px;">
                            {alerta["mensaje"]}
                        </div>
                    </div>
                </div>
            </div>
        """
    
    html += """
        </div>
        
        <!-- Predicción -->
        <div style="background: rgba(0,0,0,0.3); padding: 20px; border-radius: 8px;">
            <h3 style="color: #c9d1d9; font-size: 18px; margin-bottom: 15px;">
                4. Predicción
            </h3>
    """
    
    if pred["kg_por_semana"] > 0.05:
        html += f"""
            <div style="margin-bottom: 15px;">
                <div style="color: #8b949e; font-size: 14px; margin-bottom: 5px;">
                    🎯 Ritmo actual: {pred["kg_por_semana"]:.2f} kg/semana
                </div>
                <div style="color: #c9d1d9; font-size: 16px; font-weight: bold;">
                    Tiempo estimado: {pred["tiempo_estimado"]}
                </div>
            </div>
            
            <div style="background: rgba(88, 166, 255, 0.1); padding: 12px; border-radius: 6px;">
                <div style="color: #58a6ff; font-size: 13px; margin-bottom: 8px;">
                    📊 Para mantener el progreso:
                </div>
                <div style="color: #8b949e; font-size: 12px;">
                    • Mantener déficit calórico consistente (comé menos de lo que quemás)<br>
                    • Cumplir meta de proteína (≥160g) para preservar músculo<br>
                    • Registrar todas las comidas para mejor seguimiento<br>
                    • Adherencia actual: {pred["adherencia_actual"]:.0f}%
                </div>
            </div>
        """
    else:
        html += """
            <div style="color: #8b949e; text-align: center; padding: 20px;">
                Necesitas más datos para generar predicciones (mínimo 50g/semana de cambio)
            </div>
        """
    
    html += """
        </div>
    </div>
    """
    
    return html