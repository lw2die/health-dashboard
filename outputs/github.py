#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integración con GitHub Pages
Push automático del dashboard
"""

import os
import subprocess
from datetime import datetime
from config import GIT_REPO, OUTPUT_HTML, GITHUB_REPO_URL, GITHUB_BRANCH
from utils.logger import logger


def publicar_github():
    """
    Publica dashboard a GitHub Pages vía git push.
    Maneja conflictos automáticamente con force push si es necesario.
    """
    try:
        os.chdir(GIT_REPO)
        
        # Verificar que es un repositorio git válido
        result = subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            logger.error("El directorio no es un repositorio git válido.")
            return False
        
        logger.info("Repositorio local encontrado. Intentando actualizar...")
        
        # Git add
        subprocess.run(
            ["git", "add", "index.html"],
            check=True,
            capture_output=True
        )
        
        # Git commit
        commit_msg = f"Update dashboard: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        commit_result = subprocess.run(
            ["git", "commit", "-m", commit_msg],
            capture_output=True,
            text=True
        )
        
        # Si no hay cambios, salir
        if commit_result.returncode == 1 and "nothing to commit" in commit_result.stdout:
            logger.info("No hay cambios en index.html")
            return True
        
        # Git push
        push_result = subprocess.run(
            ["git", "push", "--set-upstream", "origin", GITHUB_BRANCH],
            capture_output=True,
            text=True
        )
        
        # Si hay conflicto, hacer force push
        if push_result.returncode != 0:
            stderr = push_result.stderr if push_result.stderr else ""
            stdout = push_result.stdout if push_result.stdout else ""
            
            if "rejected" in stderr or "rejected" in stdout or "non-fast-forward" in stderr:
                logger.info("Detectado conflicto - haciendo push --force...")
                push_result = subprocess.run(
                    ["git", "push", "--force"],
                    capture_output=True,
                    text=True
                )
        
        # Resultado final
        if push_result.returncode == 0:
            logger.info("-" * 70)
            logger.info(f"✓ Dashboard actualizado: {GITHUB_REPO_URL}")
            logger.info("-" * 70)
            return True
        else:
            stderr = push_result.stderr if push_result.stderr else ""
            logger.warning(f"Error al hacer push a GitHub: {stderr[:200]}")
            logger.info(f"Dashboard disponible localmente: {OUTPUT_HTML}")
            return False
    
    except Exception as e:
        logger.warning(f"No se pudo publicar en GitHub: {str(e)}")
        logger.info(f"Dashboard disponible localmente: {OUTPUT_HTML}")
        return False