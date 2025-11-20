#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTML Sections - Generadores de secciones HTML específicas
Contiene funciones para generar nutrition, logs y healthspan hero
"""


def generar_healthspan_hero(healthspan_data):
    """Genera el hero card de Healthspan Index"""
    if not healthspan_data:
        return ""
    
    index = healthspan_data.get("healthspan_index", 0)
    status = healthspan_data.get("status", "")
    fitness = healthspan_data.get("fitness_score", 0)
    body = healthspan_data.get("body_score", 0)
    recovery = healthspan_data.get("recovery_score", 0)
    metabolic = healthspan_data.get("metabolic_score", 0)
    functional = healthspan_data.get("functional_score", 0)
    
    # Determinar color principal
    if index >= 85:
        main_color = "#3fb950"
        status_color = "#3fb950"
    elif index >= 70:
        main_color = "#58a6ff"
        status_color = "#58a6ff"
    elif index >= 55:
        main_color = "#d29922"
        status_color = "#d29922"
    else:
        main_color = "#f85149"
        status_color = "#f85149"
    
    # Función para determinar color de subscore
    def get_subscore_color(score):
        if score >= 85:
            return "#3fb950"
        elif score >= 70:
            return "#d29922"
        else:
            return "#f85149"
    
    return f"""
    <div class="healthspan-hero">
        <div class="healthspan-title">🏆 HEALTHSPAN INDEX</div>
        <div class="healthspan-main-score">
            <div class="healthspan-value" style="color: {main_color};">{index}</div>
            <div class="healthspan-status" style="color: {status_color};">{status}</div>
            <div class="healthspan-description">Indicador de años de vida saludable basado en fitness, composición corporal y recuperación (ventana 7 días)</div>
        </div>
        
        <div class="healthspan-subscores">
            <div class="subscore-card">
                <div class="subscore-label">💪 FITNESS</div>
                <div class="subscore-value" style="color: {get_subscore_color(fitness)};">{fitness}</div>
                <div class="subscore-bar">
                    <div class="subscore-fill" style="width: {fitness}%; background: {get_subscore_color(fitness)};"></div>
                </div>
                <div class="subscore-description">PAI semanal + balance entrenamiento (TSB) + capacidad aeróbica (VO2max)</div>
            </div>
            
            <div class="subscore-card">
                <div class="subscore-label">🏋️ BODY</div>
                <div class="subscore-value" style="color: {get_subscore_color(body)};">{body}</div>
                <div class="subscore-bar">
                    <div class="subscore-fill" style="width: {body}%; background: {get_subscore_color(body)};"></div>
                </div>
                <div class="subscore-description">Peso, grasa corporal y masa muscular vs objetivos (promedio 7d)</div>
            </div>
            
            <div class="subscore-card">
                <div class="subscore-label">😴 RECOVERY</div>
                <div class="subscore-value" style="color: {get_subscore_color(recovery)};">{recovery}</div>
                <div class="subscore-bar">
                    <div class="subscore-fill" style="width: {recovery}%; background: {get_subscore_color(recovery)};"></div>
                </div>
                <div class="subscore-description">Calidad de sueño + frecuencia cardíaca en reposo + saturación de oxígeno</div>
            </div>
            
            <div class="subscore-card">
                <div class="subscore-label">🔥 METABOLIC</div>
                <div class="subscore-value" style="color: {get_subscore_color(metabolic)};">{metabolic}</div>
                <div class="subscore-bar">
                    <div class="subscore-fill" style="width: {metabolic}%; background: {get_subscore_color(metabolic)};"></div>
                </div>
                <div class="subscore-description">Presión arterial + biomarcadores de salud metabólica</div>
            </div>
            
            <div class="subscore-card">
                <div class="subscore-label">⚡ FUNCTIONAL</div>
                <div class="subscore-value" style="color: {get_subscore_color(functional)};">{functional}</div>
                <div class="subscore-bar">
                    <div class="subscore-fill" style="width: {functional}%; background: {get_subscore_color(functional)};"></div>
                </div>
                <div class="subscore-description">Pasos diarios y movilidad funcional (promedio 7d)</div>
            </div>
        </div>
    </div>
    """


def generar_seccion_nutrition(circulo_data, datos_graficos, macros_7d=None):
    """
    ✅ REEMPLAZADO: Sección HTML de nutrición estilo Samsung Health
    - Círculo de calorías restantes (día actual)
    - 3 círculos de macros en porcentaje
    - ✅ NUEVO: Comparación Recomendados vs Real (últimos 7 días)
    - Gráfico de presupuesto/consumo (14 días)
    """
    if not circulo_data:
        return ""
    
    presupuesto = circulo_data.get("presupuesto", 0)
    comido = circulo_data.get("comido", 0)
    ejercicio = circulo_data.get("ejercicio", 0)
    restante = circulo_data.get("restante", 0)
    
    # Determinar color y texto del estado
    if restante > 0:
        estado_color = "#3fb950"
        estado_texto = "✅ En déficit: Perdiendo peso"
    elif restante > -200:
        estado_color = "#ffa657"
        estado_texto = "➡️ En mantenimiento"
    else:
        estado_color = "#f85149"
        estado_texto = "🔺 En superávit: Ganando peso"
    
    # Datos de macros 7 días (si existen)
    if macros_7d:
        pct_prot_real = macros_7d.get("pct_proteinas", 0)
        pct_carb_real = macros_7d.get("pct_carbohidratos", 0)
        pct_gras_real = macros_7d.get("pct_grasas", 0)
        
        g_prot_real = macros_7d.get("proteinas_g", 0)
        g_carb_real = macros_7d.get("carbohidratos_g", 0)
        g_gras_real = macros_7d.get("grasas_g", 0)
    else:
        pct_prot_real = pct_carb_real = pct_gras_real = 0
        g_prot_real = g_carb_real = g_gras_real = 0
    
    return f"""
            <div class="nutrition-section">
                <h2>🍽️ Nutrición y Balance Calórico</h2>
                
                <!-- Grid principal: Círculo + Macros -->
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 30px; margin-bottom: 30px;">
                    
                    <!-- CÍRCULO DE CALORÍAS RESTANTES -->
                    <div class="nutrition-card" style="padding: 30px;">
                        <h3>📊 Ingesta de alimentos</h3>
                        <div style="position: relative; width: 200px; height: 200px; margin: 20px auto;">
                            <canvas id="circulo-calorias"></canvas>
                            <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); text-align: center;">
                                <div id="restante-valor" style="font-size: 2.5em; font-weight: bold; color: {estado_color};">{abs(restante)}</div>
                                <div style="font-size: 0.9em; color: #8b949e;">Restante</div>
                            </div>
                        </div>
                        
                        <!-- Información del día -->
                        <div style="margin-top: 20px;">
                            <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                                <span style="color: #8b949e;">🍽️ Comido</span>
                                <span id="comido-valor" style="color: #ff6384; font-weight: bold;">{comido}</span>
                            </div>
                            <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                                <span style="color: #8b949e;">🔥 Ejercicio</span>
                                <span id="ejercicio-valor" style="color: #10b981; font-weight: bold;">{ejercicio}</span>
                            </div>
                            <div style="display: flex; justify-content: space-between; padding-top: 10px; border-top: 1px solid rgba(139, 148, 158, 0.2);">
                                <span style="color: #8b949e;">Meta de ingesta:</span>
                                <span id="presupuesto-valor" style="color: #58a6ff; font-weight: bold;">{presupuesto} kcal</span>
                            </div>
                        </div>
                        
                        <div style="margin-top: 15px; padding: 10px; background: rgba(139, 148, 158, 0.1); border-radius: 6px; text-align: center;">
                            <small style="color: {estado_color}; font-weight: 600;">{estado_texto}</small>
                        </div>
                    </div>
                    
                    <!-- MACROS EN PORCENTAJE -->
                    <div class="nutrition-card" style="padding: 30px;">
                        <h3>Macros</h3>
                        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-top: 30px;">
                            
                            <!-- Carbohidratos -->
                            <div style="text-align: center;">
                                <div style="position: relative; width: 100px; height: 100px; margin: 0 auto;">
                                    <canvas id="macro-carbohidratos"></canvas>
                                    <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);">
                                        <div id="carbohidratos-pct" style="font-size: 1.4em; font-weight: bold; color: #3b82f6;">{circulo_data.get('pct_carbohidratos', 0)}%</div>
                                    </div>
                                </div>
                                <div style="margin-top: 10px;">
                                    <div style="color: #8b949e; font-size: 0.85em;">🍞 Carbohidrat...</div>
                                    <div id="carbohidratos-g" style="color: #c9d1d9; font-weight: bold;">{circulo_data.get('carbohidratos_g', 0)}g</div>
                                </div>
                            </div>
                            
                            <!-- Proteínas -->
                            <div style="text-align: center;">
                                <div style="position: relative; width: 100px; height: 100px; margin: 0 auto;">
                                    <canvas id="macro-proteinas"></canvas>
                                    <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);">
                                        <div id="proteinas-pct" style="font-size: 1.4em; font-weight: bold; color: #a855f7;">{circulo_data.get('pct_proteinas', 0)}%</div>
                                    </div>
                                </div>
                                <div style="margin-top: 10px;">
                                    <div style="color: #8b949e; font-size: 0.85em;">🥩 Proteínas</div>
                                    <div id="proteinas-g" style="color: #c9d1d9; font-weight: bold;">{circulo_data.get('proteinas_g', 0)}g</div>
                                </div>
                            </div>
                            
                            <!-- Grasas -->
                            <div style="text-align: center;">
                                <div style="position: relative; width: 100px; height: 100px; margin: 0 auto;">
                                    <canvas id="macro-grasas"></canvas>
                                    <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);">
                                        <div id="grasas-pct" style="font-size: 1.4em; font-weight: bold; color: #f59e0b;">{circulo_data.get('pct_grasas', 0)}%</div>
                                    </div>
                                </div>
                                <div style="margin-top: 10px;">
                                    <div style="color: #8b949e; font-size: 0.85em;">🥑 Grasas</div>
                                    <div id="grasas-g" style="color: #c9d1d9; font-weight: bold;">{circulo_data.get('grasas_g', 0)}g</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- ✅ NUEVO: COMPARACIÓN RECOMENDADOS VS REAL -->
                <div class="nutrition-card" style="padding: 30px; margin-bottom: 30px;">
                    <h3 style="text-align: center; margin-bottom: 30px;">📊 Comparación de Macronutrientes (promedio 7 días)</h3>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 40px;">
                        
                        <!-- RECOMENDADOS -->
                        <div style="text-align: center;">
                            <div style="position: relative; width: 250px; height: 250px; margin: 0 auto;">
                                <canvas id="macros-recomendados"></canvas>
                            </div>
                            <div style="margin-top: 20px;">
                                <div style="font-size: 1.2em; font-weight: bold; color: #c9d1d9; margin-bottom: 10px;">Recomendados</div>
                                <div style="color: #8b949e; font-size: 0.9em;">
                                    <span style="color: #3b82f6;">⬤</span> Carb: <strong>55%</strong> &nbsp;
                                    <span style="color: #f59e0b;">⬤</span> Grasa: <strong>25%</strong> &nbsp;
                                    <span style="color: #a855f7;">⬤</span> Proteína: <strong>20%</strong>
                                </div>
                            </div>
                        </div>
                        
                        <!-- REAL -->
                        <div style="text-align: center;">
                            <div style="position: relative; width: 250px; height: 250px; margin: 0 auto;">
                                <canvas id="macros-reales"></canvas>
                            </div>
                            <div style="margin-top: 20px;">
                                <div style="font-size: 1.2em; font-weight: bold; color: #c9d1d9; margin-bottom: 10px;">Real</div>
                                <div style="color: #8b949e; font-size: 0.9em;">
                                    <span style="color: #3b82f6;">⬤</span> Carb: <strong>{pct_carb_real}%</strong> ({g_carb_real}g) &nbsp;
                                    <span style="color: #f59e0b;">⬤</span> Grasa: <strong>{pct_gras_real}%</strong> ({g_gras_real}g) &nbsp;
                                    <span style="color: #a855f7;">⬤</span> Proteína: <strong>{pct_prot_real}%</strong> ({g_prot_real}g)
                                </div>
                            </div>
                        </div>
                        
                    </div>
                </div>
                
                <!-- GRÁFICO DE PRESUPUESTO Y CONSUMO -->
                <div class="chart-container">
                    <canvas id="presupuesto-consumo-chart" style="height: 350px;"></canvas>
                </div>
            </div>
    """


def generar_seccion_logs(logs_content, resumen):
    """Genera la sección HTML de logs"""
    if not resumen:
        return ""
    
    # Info de debug del archivo de log
    log_info = ""
    if 'log_existe' in resumen:
        if resumen.get('log_existe'):
            log_info = f"<p style='color: #8b949e; font-size: 0.9em;'>📄 Log file: {resumen.get('log_size', 0)} bytes</p>"
        else:
            log_info = "<p style='color: #f85149; font-size: 0.9em;'>⚠️ Archivo de log no encontrado</p>"
    
    return f"""
    <div class="logs-section">
        <h2>📋 Última Ejecución</h2>
        <div class="logs-summary">
            <p>✅ <strong>Fecha:</strong> {resumen.get('fecha', 'N/A')}</p>
            <p>✅ <strong>Archivos procesados:</strong> {resumen.get('archivos_procesados', 0)}</p>
            <p>✅ <strong>Total ejercicios:</strong> {resumen.get('total_ejercicios', 0)}</p>
            <p>✅ <strong>Total registros peso:</strong> {resumen.get('total_peso', 0)}</p>
            <p>✅ <strong>Total registros pasos:</strong> {resumen.get('total_pasos', 0)}</p>
            {log_info}
            <button id="logs-toggle-btn" class="logs-toggle-btn" onclick="toggleLogs()">▼ Ver logs completos (últimas 500 líneas)</button>
        </div>
        <pre id="logs-content" class="logs-hidden">{logs_content}</pre>
    </div>
    """