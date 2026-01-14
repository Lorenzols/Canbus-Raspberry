#!/usr/bin/env python3
"""
Servidor WebRTC alternativo usando ffmpeg y av (PyAV)
Más simple y confiable que Aiortc
"""

import asyncio
import logging
from aiohttp import web
from av import VideoFrame
import cv2
import numpy as np
import threading
import time
from camera import inicializar_camera, obtener_frame_base64, cerrar_camera

# Para WebRTC alternativa, usamos una solución basada en MJPEG que es más simple
# y funciona mejor en Windows

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MJPEGStreamer:
    """Servidor MJPEG (Motion JPEG) - más simple que WebRTC pero muy eficaz"""
    
    def __init__(self):
        self.clients = set()
        self.frame_buffer = None
        self.lock = threading.Lock()
        
    async def stream(self, request):
        """Streamer MJPEG"""
        response = web.StreamResponse()
        response.content_type = 'multipart/x-mixed-replace; boundary=--frame'
        await response.prepare(request)
        
        self.clients.add(response)
        logger.info(f'✅ Cliente MJPEG conectado ({len(self.clients)} total)')
        
        try:
            while True:
                with self.lock:
                    if self.frame_buffer:
                        frame_data = self.frame_buffer
                    else:
                        frame_data = None
                
                if frame_data:
                    await response.write(b'--frame\r\n')
                    await response.write(b'Content-Type: image/jpeg\r\n')
                    await response.write(f'Content-Length: {len(frame_data)}\r\n\r\n'.encode())
                    await response.write(frame_data)
                    await response.write(b'\r\n')
                
                await asyncio.sleep(0.0167)  # 60 FPS
        except Exception as e:
            logger.error(f'❌ Error en stream MJPEG: {e}')
        finally:
            self.clients.discard(response)
            logger.info(f'📴 Cliente MJPEG desconectado ({len(self.clients)} total)')
        
        return response
    
    def update_frame(self, frame_base64):
        """Actualizar frame para todos los clientes"""
        if frame_base64:
            import base64
            try:
                frame_data = base64.b64decode(frame_base64)
                with self.lock:
                    self.frame_buffer = frame_data
            except Exception as e:
                logger.error(f'❌ Error decodificando frame: {e}')

# Instancia global
streamer = MJPEGStreamer()

async def video_feed(request):
    """Endpoint para video feed MJPEG"""
    return await streamer.stream(request)

async def index(request):
    """Página HTML para visualizar video"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>📹 Streaming Cámara - MJPEG</title>
        <style>
            body {
                font-family: Arial;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                margin: 0;
                padding: 0;
            }
            .container {
                background: white;
                border-radius: 10px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.3);
                padding: 20px;
                text-align: center;
            }
            h1 {
                color: #333;
                margin: 0 0 20px 0;
            }
            #video {
                width: 800px;
                height: 600px;
                background: black;
                border: 3px solid #667eea;
                border-radius: 8px;
                display: block;
                margin: 0 auto;
            }
            .status {
                margin-top: 15px;
                font-size: 14px;
                color: #666;
            }
            .info {
                margin-top: 10px;
                padding: 10px;
                background: #f0f0f0;
                border-radius: 5px;
                font-size: 12px;
                color: #333;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📹 Streaming de Cámara en Vivo</h1>
            <img id="video" src="/video_feed" alt="Video Stream">
            <div class="status">
                <p>🟢 Conectado - MJPEG Stream @ 60 FPS</p>
            </div>
            <div class="info">
                <p>Resolución: 480x360 | Calidad: 60%</p>
                <p>Sin latencia de codificación WebRTC</p>
            </div>
        </div>

        <script>
            // Reconectar automáticamente si se cae
            const img = document.getElementById('video');
            
            img.onerror = function() {
                console.log('❌ Error en stream, reconectando...');
                setTimeout(() => {
                    img.src = '/video_feed?t=' + Date.now();
                }, 2000);
            };
            
            // Forzar recarga periódica para evitar cache
            setInterval(() => {
                img.src = '/video_feed?t=' + Date.now();
            }, 5000);
        </script>
    </body>
    </html>
    """
    return web.Response(text=html, content_type='text/html')

def frame_feed_thread():
    """Thread para actualizar frames continuamente"""
    logger.info('▶️ Thread de frames iniciado')
    contador = 0
    
    while True:
        try:
            frame_b64 = obtener_frame_base64()
            if frame_b64:
                streamer.update_frame(frame_b64)
                contador += 1
                if contador % 60 == 0:
                    logger.info(f'✅ {contador} frames enviados')
            time.sleep(0.0167)  # 60 FPS
        except Exception as e:
            logger.error(f'❌ Error en thread de frames: {e}')
            time.sleep(0.5)

async def main():
    """Función principal"""
    logger.info('🚀 Iniciando servidor MJPEG...')
    
    # Inicializar cámara CON YOLOv8 para detección
    logger.info('📷 Inicializando cámara CON YOLOv8...')
    inicializar_camera(cargar_yolo=True)
    
    # Iniciar thread de frames
    frame_thread = threading.Thread(target=frame_feed_thread, daemon=True)
    frame_thread.start()
    
    # Crear app web
    app = web.Application()
    app.router.add_get('/', index)
    app.router.add_get('/video_feed', video_feed)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    await site.start()
    
    logger.info('✅ Servidor MJPEG corriendo en http://0.0.0.0:8080')
    logger.info('📹 Abre el navegador para ver el video en vivo')
    
    # Mantener activo
    await asyncio.Event().wait()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info('⏹️ Servidor detenido')
        cerrar_camera()
