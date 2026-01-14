#!/usr/bin/env python3
"""
Servidor WebRTC para streaming de video en Raspberry Pi
Mucho más eficiente que Socket.IO + Base64
"""

import asyncio
import logging
from aiohttp import web
from aiortc import RTCPeerConnection, RTCSessionDescription, VideoStreamTrack
from av import VideoFrame
import cv2
import threading
from camera import inicializar_camera, obtener_frame_base64, cerrar_camera
import numpy as np

# ==================== CONFIGURACIÓN ====================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== TRACK DE VIDEO ====================
class CameraVideoTrack(VideoStreamTrack):
    """Track de video que obtiene frames de la cámara"""
    
    def __init__(self):
        super().__init__()
        self.counter = 0
        logger.info('✅ CameraVideoTrack inicializado')
    
    async def recv(self):
        """Recibir frame de la cámara y enviarlo por WebRTC"""
        pts, time_base = await self.next_timestamp()
        
        try:
            # Obtener frame en Base64
            frame_b64 = obtener_frame_base64()
            
            if frame_b64:
                import base64
                try:
                    # Decodificar Base64 a imagen
                    frame_data = base64.b64decode(frame_b64)
                    nparr = np.frombuffer(frame_data, np.uint8)
                    frame_cv = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                    
                    if frame_cv is not None:
                        # Convertir BGR a RGB
                        frame_rgb = cv2.cvtColor(frame_cv, cv2.COLOR_BGR2RGB)
                        
                        # Crear VideoFrame para aiortc
                        frame = VideoFrame.from_ndarray(frame_rgb, format="rgb24")
                        frame.pts = pts
                        frame.time_base = time_base
                        
                        self.counter += 1
                        if self.counter % 60 == 0:
                            logger.info(f'✅ {self.counter} frames enviados por WebRTC')
                        
                        return frame
                except Exception as decode_error:
                    logger.error(f'❌ Error decodificando frame: {decode_error}')
        except Exception as e:
            logger.error(f'❌ Error en recv(): {e}')
        
        # Fallback: crear frame gris si hay error
        fallback_frame = np.ones((360, 480, 3), dtype=np.uint8) * 128
        frame = VideoFrame.from_ndarray(fallback_frame, format="rgb24")
        frame.pts = pts
        frame.time_base = time_base
        return frame


# ==================== SERVIDOR WEB ====================
pcs = set()

async def offer(request):
    """Endpoint para recibir oferta WebRTC"""
    try:
        params = await request.json()
        logger.info('📡 Oferta WebRTC recibida')
        
        # Parsear oferta
        offer_sdp = RTCSessionDescription(sdp=params["sdp"], type=params["type"])

        # Crear conexión
        pc = RTCPeerConnection()
        pcs.add(pc)
        logger.info('✅ PeerConnection creada')

        # Manejar cambios de estado
        @pc.on("connectionstatechange")
        async def on_connectionstatechange():
            logger.info(f'📡 Estado WebRTC: {pc.connectionState}')
            if pc.connectionState == "failed":
                await pc.close()
                pcs.discard(pc)

        # Agregar track de VIDEO
        video_track = CameraVideoTrack()
        pc.addTrack(video_track)
        logger.info('✅ Track de video agregado')

        # Procesar oferta remota
        logger.info('🔄 Procesando oferta remota...')
        await pc.setRemoteDescription(offer_sdp)
        logger.info('✅ Oferta remota procesada')

        # Crear y establecer respuesta
        logger.info('🔄 Creando respuesta...')
        answer = await pc.createAnswer()
        logger.info('✅ Respuesta creada')
        
        logger.info('🔄 Estableciendo descripción local...')
        await pc.setLocalDescription(answer)
        logger.info('✅ Descripción local establecida')

        logger.info('✅ Oferta WebRTC procesada correctamente')
        return web.json_response({
            "sdp": pc.localDescription.sdp,
            "type": pc.localDescription.type
        })
        
    except Exception as e:
        logger.error(f'❌ Error en offer(): {e}')
        import traceback
        traceback.print_exc()
        return web.json_response({"error": str(e)}, status=500)


async def on_shutdown(app):
    """Cerrar todas las conexiones al apagar"""
    coros = [pc.close() for pc in pcs]
    await asyncio.gather(*coros)
    pcs.clear()


async def index(request):
    """Servir página HTML con cliente WebRTC"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Streaming WebRTC</title>
        <style>
            body { font-family: Arial; display: flex; justify-content: center; align-items: center; height: 100vh; background: #222; }
            #video { width: 800px; height: 600px; background: black; border: 2px solid #00ff00; }
        </style>
    </head>
    <body>
        <div>
            <h1 style="color: white;">📹 Streaming WebRTC</h1>
            <video id="video" autoplay playsinline></video>
        </div>
        <script src="https://webrtc.github.io/adapter/adapter-latest.js"></script>
        <script>
            const pc = new RTCPeerConnection({
                iceServers: [{urls: ['stun:stun.l.google.com:19302']}]
            });

            pc.addEventListener('track', function(evt) {
                console.log('📹 Video track recibido');
                if (evt.track.kind === 'video') {
                    document.getElementById('video').srcObject = evt.streams[0];
                }
            });

            async function start() {
                const offer = await pc.createOffer();
                await pc.setLocalDescription(offer);

                const response = await fetch('/offer', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        sdp: pc.localDescription.sdp,
                        type: pc.localDescription.type
                    })
                });

                const answer = await response.json();
                await pc.setRemoteDescription(new RTCSessionDescription(answer));
                console.log('✅ Conexión WebRTC establecida');
            }

            start().catch(console.error);
        </script>
    </body>
    </html>
    """
    return web.Response(text=html, content_type='text/html')


async def main():
    """Función principal"""
    global camera
    
    logger.info('🚀 Iniciando servidor WebRTC...')
    
    # Inicializar cámara
    inicializar_camera()
    
    # Crear app web
    app = web.Application()
    app.router.add_get('/', index)
    app.router.add_post('/offer', offer)
    app.on_shutdown.append(on_shutdown)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    await site.start()
    
    logger.info('✅ Servidor WebRTC corriendo en http://0.0.0.0:8080')
    logger.info('📹 Accede desde cualquier navegador para ver el streaming')
    
    # Mantener el servidor activo
    await asyncio.Event().wait()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info('⏹️ Servidor detenido')
        cerrar_camera()
