#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
telemetry.py – SISTEMA DE TELEMETRÍA ESTRUCTURADA
Responsabilidad: Registrar eventos en consola y en archivos JSON, con niveles
(INFO, WARNING, ERROR, DEBUG, CRITICAL).
"""

import logging
import json
import os
from datetime import datetime, timezone
from typing import Dict, Any, Optional

# Crear directorio de logs si no existe
LOG_DIR = 'logs'
os.makedirs(LOG_DIR, exist_ok=True)

class Telemetry:
    """
    Sistema de telemetría estructurada.
    Singleton que escribe logs en consola y en archivos por nivel.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_loggers()
        return cls._instance

    def _init_loggers(self):
        """Inicializa loggers por nivel."""
        self.loggers = {}
        levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        for level in levels:
            logger = logging.getLogger(f"telemetry.{level}")
            logger.setLevel(getattr(logging, level))

            # Consola
            console = logging.StreamHandler()
            console.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
            logger.addHandler(console)

            # Archivo
            file_path = os.path.join(LOG_DIR, f'{level.lower()}.log')
            file_handler = logging.FileHandler(file_path)
            file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
            logger.addHandler(file_handler)

            self.loggers[level] = logger

    def _log(self, level: str, module: str, message: str, data: Optional[Dict[str, Any]] = None):
        """Registra un evento estructurado."""
        entry = {
            'level': level.upper(),
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'module': module,
            'message': message,
            'data': data or {}
        }
        logger = self.loggers.get(level.upper())
        if logger:
            logger.info(json.dumps(entry))

# Instancia global
_telemetry = Telemetry()

# Funciones públicas
def log_info(module: str, message: str, data: Optional[Dict[str, Any]] = None):
    _telemetry._log('INFO', module, message, data)

def log_warning(module: str, message: str, data: Optional[Dict[str, Any]] = None):
    _telemetry._log('WARNING', module, message, data)

def log_error(module: str, message: str, data: Optional[Dict[str, Any]] = None):
    _telemetry._log('ERROR', module, message, data)

def log_debug(module: str, message: str, data: Optional[Dict[str, Any]] = None):
    _telemetry._log('DEBUG', module, message, data)

def log_critical(module: str, message: str, data: Optional[Dict[str, Any]] = None):
    _telemetry._log('CRITICAL', module, message, data)

def log_success(module: str, message: str, data: Optional[Dict[str, Any]] = None):
    """Mensaje de éxito con emoji (wrapper de INFO)."""
    _telemetry._log('INFO', module, f"✅ {message}", data)
