#!/usr/bin/env python3
"""
Script para iniciar ambos servidores: Socket.IO + WebRTC
"""

import subprocess
import time
import os
import signal
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Procesos
processes = []

def signal_handler(sig, frame):
    """Detener todos los procesos al presionar Ctrl+C"""
    logger.info('⏹️ Deteniendo servidores...')
    for process in processes:
        process.terminate()
    time.sleep(1)
    for process in processes:
        if process.poll() is None:
            process.kill()
    sys.exit(0)

def main():
    """Ejecutar ambos servidores en paralelo"""
    signal.signal(signal.SIGINT, signal_handler)
    
    logger.info('🚀 Iniciando servidores...')
    
    # Servidor Socket.IO (para controles)
    logger.info('📡 Iniciando server.py en puerto 3000...')
    process_socket = subprocess.Popen([sys.executable, 'server.py'])
    processes.append(process_socket)
    time.sleep(2)  # Esperar a que se inicie
    
    # Servidor MJPEG (para video)
    logger.info('📹 Iniciando webrtc_server_mjpeg.py en puerto 8080...')
    process_mjpeg = subprocess.Popen([sys.executable, 'webrtc_server_mjpeg.py'])
    processes.append(process_mjpeg)
    time.sleep(2)  # Esperar a que se inicie
    
    logger.info('✅ Ambos servidores están corriendo')
    logger.info('   📡 Socket.IO: http://192.168.0.79:3000 (controles)')
    logger.info('   📹 MJPEG: http://192.168.0.79:8080 (video @ 60 FPS)')
    logger.info('   (Presiona Ctrl+C para detener ambos)')
    
    # Mantener los procesos activos
    while True:
        # Verificar si algún proceso se cerró
        if process_socket.poll() is not None:
            logger.error('❌ server.py se cerró, intentando reiniciar...')
            process_socket = subprocess.Popen([sys.executable, 'server.py'])
            processes[0] = process_socket
        
        if process_mjpeg.poll() is not None:
            logger.error('❌ webrtc_server_mjpeg.py se cerró, intentando reiniciar...')
            process_mjpeg = subprocess.Popen([sys.executable, 'webrtc_server_mjpeg.py'])
            processes[1] = process_mjpeg
        
        time.sleep(1)

if __name__ == '__main__':
    main()
