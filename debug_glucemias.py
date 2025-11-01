#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de DEBUG para verificar por qué no se usan las glucemias diarias
"""

import json
import sys
from pathlib import Path

print("=" * 80)
print("DEBUG: Verificando glucemias en cache y función de laboratorio")
print("=" * 80)

# 1. Verificar cache
cache_path = Path("cache_datos.json")  # ✅ En la raíz de SCRIPT
if cache_path.exists():
    with open(cache_path, 'r', encoding='utf-8') as f:
        cache = json.load(f)
    
    glucosa = cache.get("glucosa", [])
    print(f"\n✓ Cache encontrado")
    print(f"  Total glucemias en cache: {len(glucosa)} registros")
    
    if glucosa:
        print("\n  Primeras 3 glucemias:")
        for g in glucosa[:3]:
            fecha = g.get('fecha', 'N/A')
            valor = g.get('valor') or g.get('glucosa', 'N/A')
            print(f"    - Fecha: {fecha}, Valor: {valor}")
        
        print("\n  📋 Estructura completa de la primera glucemia:")
        print(f"    {json.dumps(glucosa[0], indent=4, ensure_ascii=False)}")
    else:
        print("\n  ⚠️ NO HAY GLUCEMIAS EN EL CACHE")
else:
    print("\n✗ Cache no encontrado")
    sys.exit(1)

# 2. Simular llamada a laboratorio
print("\n" + "=" * 80)
print("Simulando llamada a obtener_datos_laboratorio_y_alertas...")
print("=" * 80)

sys.path.insert(0, 'metricas')
from laboratorio import obtener_datos_laboratorio_y_alertas

resultado = obtener_datos_laboratorio_y_alertas(
    edad=61,
    altura_cm=177,
    peso_kg=82.2,
    vo2max_medido=27.7,
    glucemias_diarias=glucosa  # Pasar las glucemias
)

print(f"\nLongevity Score: {resultado.get('longevity_score')}")

# 3. Verificar alertas
alertas = resultado.get('alertas', [])
print(f"\nTotal alertas: {len(alertas)}")

print("\nAlertas relacionadas con glucemia/HbA1c:")
for alerta in alertas:
    titulo = alerta.get('titulo', '')
    descripcion = alerta.get('descripcion', '')
    severidad = alerta.get('severidad', '')
    
    if any(keyword in titulo.lower() + descripcion.lower() 
           for keyword in ['glucemia', 'hba1c', 'prediabetes', 'glucémico', 'control']):
        emoji = {"CRITICA": "🔴", "ALTA": "🟠", "MODERADA": "🟡", "INFO": "🔵", "BUENA": "🟢"}.get(severidad, "⚪")
        print(f"\n{emoji} [{severidad}] {titulo}")
        print(f"   {descripcion}")

print("\n" + "=" * 80)
print("FIN DEBUG")
print("=" * 80)