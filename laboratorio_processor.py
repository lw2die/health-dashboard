#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Procesador de datos de laboratorio clínico
Parsea, normaliza y valida parámetros contra rangos de referencia
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional

class LaboratorioProcessor:
    """Procesa archivos JSON de laboratorio clínico"""
    
    # Rangos de referencia normales (adultos)
    RANGOS_REFERENCIA = {
        "ldl_mg_dl": (0, 100),           # mg/dL - Óptimo <100
        "hdl_mg_dl": (40, 300),          # mg/dL - Bueno >40
        "triglic_mg_dl": (0, 150),       # mg/dL - Normal <150
        "glucosa_mg_dl": (70, 100),      # mg/dL - Ayuno
        "hba1c_porciento": (0, 5.7),     # % - Normal <5.7%
        "tsh_uiu_ml": (0.4, 4.0),        # mIU/mL
        "creatinina_mg_dl": (0.6, 1.2),  # mg/dL
        "urea_mg_dl": (7, 20),           # mg/dL
        "pcr_mg_l": (0, 3.0),            # mg/L
        "pa_sistolica": (0, 120),        # mmHg
        "pa_diastolica": (0, 80),        # mmHg
    }
    
    def __init__(self, ruta_json: str = None):
        """Inicializa con ruta a archivo JSON"""
        self.ruta_json = ruta_json
        self.datos_raw = {}
        self.datos_procesados = {}
        
    def cargar(self, ruta: str = None) -> bool:
        """Carga archivo JSON de laboratorio"""
        if ruta:
            self.ruta_json = ruta
            
        if not self.ruta_json:
            return False
            
        try:
            with open(self.ruta_json, 'r', encoding='utf-8') as f:
                self.datos_raw = json.load(f)
            return True
        except Exception as e:
            print(f"Error al cargar laboratorio: {e}")
            return False
    
    def procesar(self) -> Dict[str, Any]:
        """Procesa todos los datos del laboratorio"""
        if not self.datos_raw:
            return {}
        
        # Extraer informes
        informes = self._extraer_informes()
        
        # Procesar cada informe
        procesados = []
        for informe in informes:
            proc = self._procesar_informe(informe)
            if proc:
                procesados.append(proc)
        
        # Agregar validaciones
        self.datos_procesados = {
            "informes": procesados,
            "tendencias": self._calcular_tendencias(procesados) if len(procesados) > 1 else {},
            "validacion": self._validar_rangos(procesados[-1] if procesados else {})
        }
        
        return self.datos_procesados
    
    def _extraer_informes(self) -> List[Dict]:
        """Extrae lista de informes del JSON"""
        informes = []
        
        # Buscar estructura de informes (puede variar)
        for clave, valor in self.datos_raw.items():
            if isinstance(valor, dict) and "data" in valor:
                # Estructura con "data" array
                if isinstance(valor["data"], list):
                    informes.extend(valor["data"])
            elif isinstance(valor, list):
                # Estructura directa de array
                informes.extend(valor)
            elif isinstance(valor, dict) and clave not in ["metadata", "fecha"]:
                informes.append(valor)
        
        return informes
    
    def _procesar_informe(self, informe: Dict) -> Optional[Dict]:
        """Procesa un informe individual"""
        try:
            resultado = {
                "fecha": self._extraer_fecha(informe),
                "parametros": {},
                "notas": informe.get("notas", "")
            }
            
            # Mapear parámetros comunes
            mapeos = {
                "ldl_mg_dl": ["ldl", "LDL", "colesterol_ldl"],
                "hdl_mg_dl": ["hdl", "HDL", "colesterol_hdl"],
                "triglic_mg_dl": ["trigliceridos", "triglic", "TG"],
                "glucosa_mg_dl": ["glucosa", "glucose", "glu"],
                "hba1c_porciento": ["hba1c", "HbA1c", "hemoglobina_a1c"],
                "tsh_uiu_ml": ["tsh", "TSH"],
                "creatinina_mg_dl": ["creatinina", "crea"],
                "urea_mg_dl": ["urea", "BUN"],
                "pcr_mg_l": ["pcr", "PCR", "proteina_c_reactiva"],
                "pa_sistolica": ["presion_sistolica", "pas", "sistolica"],
                "pa_diastolica": ["presion_diastolica", "pad", "diastolica"],
            }
            
            # Buscar y extraer valores
            for param_std, aliases in mapeos.items():
                for alias in aliases:
                    if alias in informe:
                        valor = self._normalizar_valor(param_std, informe[alias])
                        if valor is not None:
                            resultado["parametros"][param_std] = valor
                        break
            
            return resultado if resultado["parametros"] else None
            
        except Exception as e:
            print(f"Error procesando informe: {e}")
            return None
    
    def _extraer_fecha(self, informe: Dict) -> str:
        """Extrae fecha del informe"""
        for clave in ["fecha", "date", "timestamp", "fecha_informe"]:
            if clave in informe:
                fecha_str = str(informe[clave])
                try:
                    # Intentar parsear ISO format
                    if "T" in fecha_str:
                        dt = datetime.fromisoformat(fecha_str.replace("Z", "+00:00"))
                    else:
                        dt = datetime.fromisoformat(fecha_str.split()[0])
                    return dt.strftime("%Y-%m-%d")
                except:
                    return fecha_str[:10]
        
        return datetime.now().strftime("%Y-%m-%d")
    
    def _normalizar_valor(self, parametro: str, valor: Any) -> Optional[float]:
        """Normaliza valores a formato estándar"""
        try:
            if isinstance(valor, (int, float)):
                return float(valor)
            elif isinstance(valor, str):
                # Limpiar caracteres especiales
                valor_limpio = valor.replace(",", ".").strip()
                return float(valor_limpio)
            return None
        except:
            return None
    
    def _calcular_tendencias(self, informes_procesados: List[Dict]) -> Dict:
        """Calcula tendencias entre informes"""
        if len(informes_procesados) < 2:
            return {}
        
        tendencias = {}
        informe_anterior = informes_procesados[0]
        informe_actual = informes_procesados[-1]
        
        for param in informe_actual["parametros"]:
            if param in informe_anterior["parametros"]:
                valor_anterior = informe_anterior["parametros"][param]
                valor_actual = informe_actual["parametros"][param]
                cambio = valor_actual - valor_anterior
                pct_cambio = (cambio / valor_anterior * 100) if valor_anterior != 0 else 0
                
                tendencias[param] = {
                    "anterior": valor_anterior,
                    "actual": valor_actual,
                    "cambio_absoluto": round(cambio, 2),
                    "cambio_pct": round(pct_cambio, 1),
                    "direccion": "↑" if cambio > 0 else "↓" if cambio < 0 else "→"
                }
        
        return tendencias
    
    def _validar_rangos(self, informe: Dict) -> Dict:
        """Valida parámetros contra rangos de referencia"""
        validacion = {}
        parametros = informe.get("parametros", {})
        
        for param, valor in parametros.items():
            if param in self.RANGOS_REFERENCIA:
                min_val, max_val = self.RANGOS_REFERENCIA[param]
                estado = "NORMAL"
                if valor < min_val:
                    estado = "BAJO"
                elif valor > max_val:
                    estado = "ALTO"
                
                validacion[param] = {
                    "valor": valor,
                    "rango": f"{min_val}-{max_val}",
                    "estado": estado
                }
        
        return validacion
    
    def obtener_parametro(self, parametro: str, informe_idx: int = -1) -> Optional[float]:
        """Obtiene un parámetro específico"""
        if not self.datos_procesados or not self.datos_procesados.get("informes"):
            return None
        
        try:
            informe = self.datos_procesados["informes"][informe_idx]
            return informe["parametros"].get(parametro)
        except:
            return None
    
    def obtener_todos_parametros(self, informe_idx: int = -1) -> Dict:
        """Obtiene todos los parámetros del informe más reciente"""
        if not self.datos_procesados or not self.datos_procesados.get("informes"):
            return {}
        
        try:
            return self.datos_procesados["informes"][informe_idx]["parametros"]
        except:
            return {}


# Interfaz pública
def cargar_laboratorio(ruta_json: str) -> LaboratorioProcessor:
    """Carga y procesa laboratorio"""
    processor = LaboratorioProcessor(ruta_json)
    if processor.cargar():
        processor.procesar()
        return processor
    return None