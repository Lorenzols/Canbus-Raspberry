#!/usr/bin/env python3
"""
Servidor Socket.IO para Raspberry Pi - Control de Ventanas del Coche
Conecta con el backend para recibir comandos y ejecutarlos mediante CAN
"""

import socketio
import time
import subprocess
import logging
from typing import Dict, Optional

# ==================== CONFIGURACIÓN ====================
BACKEND_URL = 'http://192.168.0.79:3000'  # Cambia esto por la IP real de tu backend
MI_COCHE_ID = 'CITROEN_C4_001'

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

# ==================== MAPEO DE VENTANAS ====================
# YA NO NECESITAMOS MAPEO AQUÍ, el backend envía los datos directamente
VENTANAS_CAN = {}

# ==================== CLIENTE SOCKET.IO ====================
sio = socketio.Client()
conectado = False


@sio.event
def connect():
    """Evento cuando se conecta al backend"""
    global conectado
    conectado = True
    logger.info('✅ Conectado al backend')
    
    # Registrar la Raspberry como el coche
    sio.emit('registro', {
        'tipo': 'coche',
        'cocheId': MI_COCHE_ID
    })


@sio.event
def disconnect():
    """Evento cuando se desconecta del backend"""
    global conectado
    conectado = False
    logger.error('❌ Desconectado del backend')


@sio.on('comando_ventana')
def on_comando_ventana(data):
    """Recibe comandos de ventana desde el backend"""
    procesar_comando_ventana(data)


@sio.on('ejecutar_ventana')
def on_ejecutar_ventana(data):
    """Recibe comandos del backend con datos CAN ya procesados"""
    procesar_comando_ventana(data)


@sio.on('ejecutar_bajar')
def on_ejecutar_bajar(data):
    """Recibe comandos del evento ejecutar_bajar (compatibilidad)"""
    procesar_comando_ventana(data)


def procesar_comando_ventana(data: Dict) -> None:
    """
    Procesa un comando de ventana recibido del backend
    El backend ya envía los datos CAN procesados
    
    Args:
        data: Diccionario con datos CAN del backend
    """
    id_can = data.get('idCAN')
    datos_can = data.get('datosCAN')
    descripcion = data.get('descripcion', 'Comando sin descripción')

    # Validar datos
    if not id_can or not datos_can:
        logger.error(f'❌ Datos incompletos')
        return

    # Construir comando CAN
    comando = f"cangen can0 -g 2 -I {id_can} -L 5 -D {datos_can} -n 25"

    # Loguear solo lo importante
    logger.info(f'🚗 {descripcion}')
    logger.info(f'⚙️ {comando}\n')

    # Ejecutar comando CAN
    ejecutar_comando_can(comando)


def ejecutar_comando_can(comando: str) -> bool:
    """
    Ejecuta un comando CAN en la Raspberry Pi
    
    Args:
        comando: Comando CAN a ejecutar
        
    Returns:
        True si se ejecutó correctamente, False si falló
    """
    try:
        # Ejecutar el comando CAN en la Raspberry Pi real
        subprocess.run(comando, shell=True, check=True)
        logger.info(f'✅ Comando CAN ejecutado correctamente')
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f'❌ Error ejecutando comando CAN: {e}')
        return False
    except Exception as e:
        logger.error(f'❌ Error inesperado: {e}')
        return False


def main():
    """Función principal"""
    logger.info('🚀 Servidor Raspberry Pi iniciado')
    logger.info(f'🔗 Backend: {BACKEND_URL}')
    logger.info(f'🚗 Coche: {MI_COCHE_ID}\n')
    
    try:
        # Conectar al backend
        sio.connect(BACKEND_URL)
        
        # Mantener la conexión abierta
        sio.wait()
        
    except Exception as e:
        logger.error(f'Error: {e}')
        logger.info('Reintentando en 5 segundos...')
        time.sleep(5)
        main()


if __name__ == '__main__':
    main()
