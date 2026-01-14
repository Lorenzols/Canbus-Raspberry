#!/usr/bin/env python3
"""
Sistema de Cámara con Detección de Objetos usando YOLOv8
Detecta personas y perros, y graba cuando se detectan
"""

import cv2
import numpy as np
from ultralytics import YOLO
import logging
import threading
import time
from datetime import datetime
from pathlib import Path
import base64

# ==================== CONFIGURACIÓN ====================
logger = logging.getLogger(__name__)

# Clases a detectar
CLASES_DETECTAR = ['person', 'dog']  # YOLOv8 names: 'person' y 'dog'

# Configuración de grabación
VIDEO_OUTPUT_DIR = Path('videos_grabados')
VIDEO_OUTPUT_DIR.mkdir(exist_ok=True)

# ==================== CLASE DE CÁMARA ====================
class CameraManager:
    def __init__(self, cargar_yolo=False):
        """Inicializar gestor de cámara
        
        Args:
            cargar_yolo: Si True, carga el modelo YOLOv8 (más recursos)
        """
        self.cap = None
        self.modelo = None
        self.frame_actual = None
        self.grabando = False
        self.video_writer = None
        self.detecciones = []
        self.fps = 30
        self.ancho = 640
        self.alto = 480
        self.lock = threading.Lock()
        self.cargar_yolo = cargar_yolo
        
        # Cargar modelo YOLOv8 solo si se solicita
        if self.cargar_yolo:
            self.cargar_modelo()
        
        # **IMPORTANTE: Conectar cámara en el main thread, no en capturar_frames**
        # Esto evita problemas de threading en Windows
        
    def cargar_modelo(self):
        """Cargar modelo YOLOv8"""
        try:
            logger.info('📦 Cargando modelo YOLOv8...')
            self.modelo = YOLO('yolov8n.pt')  # nano es más rápido
            logger.info('✅ Modelo YOLOv8 cargado')
        except Exception as e:
            logger.error(f'❌ Error cargando modelo: {e}')
            
    def conectar_camara(self, camera_index=0):
        """Conectar a la cámara (debe llamarse desde main thread en Windows)"""
        try:
            logger.info(f'📷 Buscando cámara...')
            
            # Intentar con diferentes índices
            indices_a_probar = [0, 1, 2, 3, 4]
            
            for idx in indices_a_probar:
                logger.info(f'   Probando índice {idx}...')
                cap = cv2.VideoCapture(idx)
                logger.info(f'      cv2.VideoCapture({idx}) creado')
                
                if not cap.isOpened():
                    logger.info(f'      ❌ No abierto')
                    cap.release()
                    continue
                
                logger.info(f'      ✅ Abierto, probando lectura...')
                
                # Esperar un poco para que se inicialice
                ret = False
                for intento in range(5):
                    ret, frame = cap.read()
                    logger.info(f'         Intento {intento+1}: ret={ret}')
                    if ret and frame is not None:
                        logger.info(f'✅ Cámara encontrada en índice {idx}')
                        self.cap = cap
                        break
                    time.sleep(0.5)
                
                if self.cap is not None and self.cap.isOpened():
                    break
                else:
                    logger.info(f'      ❌ No se pudo leer')
                    cap.release()
            
            if self.cap is None or not self.cap.isOpened():
                logger.error('❌ No se encontró ninguna cámara en índices 0-4')
                logger.error('   💡 Intenta:')
                logger.error('      1. Desconecta y reconecta la cámara USB')
                logger.error('      2. Cierra la app de Cámara de Windows')
                logger.error('      3. Reinicia Python')
                return False
                
            # Configurar resolución
            logger.info(f'📐 Configurando resolución {self.ancho}x{self.alto}...')
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.ancho)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.alto)
            self.cap.set(cv2.CAP_PROP_FPS, self.fps)
            
            logger.info(f'✅ Cámara conectada ({self.ancho}x{self.alto}@{self.fps}fps)')
            return True
            
        except Exception as e:
            logger.error(f'❌ Error conectando cámara: {e}')
            import traceback
            traceback.print_exc()
            return False
            
    def detectar_objetos(self, frame):
        """Detectar personas y perros en el frame"""
        if self.modelo is None:
            return frame, []
            
        try:
            # Ejecutar detección
            resultados = self.modelo(frame, conf=0.5, verbose=False)
            detecciones = []
            
            # Procesar resultados
            for result in resultados:
                for box in result.boxes:
                    clase_id = int(box.cls[0])
                    clase_nombre = result.names[clase_id]
                    confianza = float(box.conf[0])
                    
                    # Solo nos interesan personas y perros
                    if clase_nombre in CLASES_DETECTAR:
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        
                        # Dibujar rectángulo
                        color = (0, 255, 0) if clase_nombre == 'person' else (255, 0, 0)
                        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                        
                        # Dibujar etiqueta
                        etiqueta = f'{clase_nombre} {confianza:.2f}'
                        cv2.putText(frame, etiqueta, (x1, y1 - 10),
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                        
                        detecciones.append({
                            'clase': clase_nombre,
                            'confianza': confianza,
                            'bbox': (x1, y1, x2, y2)
                        })
            
            return frame, detecciones
            
        except Exception as e:
            logger.error(f'❌ Error en detección: {e}')
            return frame, []
            
    def iniciar_grabacion(self):
        """Iniciar grabación de video"""
        if self.grabando:
            return
            
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            nombre_archivo = VIDEO_OUTPUT_DIR / f'video_{timestamp}.mp4'
            
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            self.video_writer = cv2.VideoWriter(
                str(nombre_archivo),
                fourcc,
                self.fps,
                (self.ancho, self.alto)
            )
            
            self.grabando = True
            logger.info(f'🎥 Grabación iniciada: {nombre_archivo}')
            
        except Exception as e:
            logger.error(f'❌ Error iniciando grabación: {e}')
            
    def detener_grabacion(self):
        """Detener grabación"""
        if not self.grabando:
            return
            
        try:
            if self.video_writer:
                self.video_writer.release()
            self.grabando = False
            logger.info('⏹️ Grabación detenida')
        except Exception as e:
            logger.error(f'❌ Error deteniendo grabación: {e}')
            
    def escribir_frame_grabacion(self, frame):
        """Escribir frame a archivo de video"""
        if self.grabando and self.video_writer:
            try:
                self.video_writer.write(frame)
            except Exception as e:
                logger.error(f'❌ Error escribiendo frame: {e}')
                
    def capturar_frames(self):
        """Capturar frames continuamente (ejecutar en thread)"""
        try:
            logger.info("📹 [THREAD] Iniciando loop de lectura...")
            
            if self.cap is None or not self.cap.isOpened():
                logger.error("❌ [THREAD] Cámara no está conectada")
                return
                
            frame_count = 0
            tiempo_sin_detecciones = 0
            
            while self.cap.isOpened():
                try:
                    ret, frame = self.cap.read()
                    
                    if not ret:
                        logger.error('❌ [THREAD] Error leyendo frame')
                        break
                    
                    frame_count += 1
                    
                    # Procesar con YOLOv8 cada N frames (para optimizar)
                    frame_procesado = frame.copy()
                    detecciones = []
                    
                    if frame_count % 2 == 0 and self.modelo is not None:  # Cada 2 frames
                        frame_procesado, detecciones = self.detectar_objetos(frame)
                    
                    # Actualizar estado
                    with self.lock:
                        self.frame_actual = frame_procesado
                        self.detecciones = detecciones
                    
                    # Lógica de grabación automática
                    if detecciones:  # Se detectó algo
                        if not self.grabando:
                            self.iniciar_grabacion()
                        tiempo_sin_detecciones = 0
                        if self.grabando:
                            self.escribir_frame_grabacion(frame_procesado)
                    else:  # No se detectó nada
                        tiempo_sin_detecciones += 1
                        
                        # Detener grabación después de 5 segundos sin detecciones
                        if self.grabando and tiempo_sin_detecciones > (self.fps * 5):
                            self.detener_grabacion()
                        elif self.grabando:
                            self.escribir_frame_grabacion(frame_procesado)
                    
                    if frame_count == 1:
                        logger.info(f"✅ [THREAD] ¡Primer frame capturado!")
                    
                    # Sin logs frecuentes para no afectar rendimiento
                    
                except Exception as e:
                    logger.error(f'❌ [THREAD] Error en loop: {e}')
                    import traceback
                    traceback.print_exc()
                    break
            
            logger.info("⏹️ [THREAD] Loop detenido")
            
        except Exception as e:
            logger.error(f'❌ [THREAD] Error general: {e}')
            import traceback
            traceback.print_exc()
                
    def obtener_frame_base64(self):
        """Obtener frame actual codificado en Base64"""
        with self.lock:
            if self.frame_actual is None:
                return None
                
            try:
                # Redimensionar para menor tamaño (más rápido)
                frame_resized = cv2.resize(self.frame_actual, (480, 360))
                # Codificar frame a JPEG con calidad equilibrada para 60 FPS
                ret, buffer = cv2.imencode('.jpg', frame_resized, [cv2.IMWRITE_JPEG_QUALITY, 60])
                if ret:
                    # Convertir a Base64
                    frame_b64 = base64.b64encode(buffer).decode('utf-8')
                    return frame_b64
            except Exception as e:
                logger.error(f'❌ Error codificando frame: {e}')
                
        return None
        
    def obtener_estado(self):
        """Obtener estado actual de la cámara"""
        with self.lock:
            num_detecciones = len(self.detecciones)
            clases_detectadas = [d['clase'] for d in self.detecciones]
            
            return {
                'conectada': self.cap is not None and self.cap.isOpened(),
                'grabando': self.grabando,
                'detecciones': num_detecciones,
                'clases': clases_detectadas
            }
            
    def cerrar(self):
        """Cerrar cámara y limpiar recursos"""
        try:
            self.detener_grabacion()
            if self.cap:
                self.cap.release()
            logger.info('✅ Cámara cerrada')
        except Exception as e:
            logger.error(f'❌ Error cerrando cámara: {e}')


# ==================== FUNCIÓN GLOBAL ====================
camera = None

def inicializar_camera(cargar_yolo=False):
    """Inicializar gestor de cámara global
    
    Args:
        cargar_yolo: Si True, carga YOLOv8 para detección de objetos
    """
    global camera
    camera = CameraManager(cargar_yolo=cargar_yolo)
    
    # **IMPORTANTE: Conectar cámara en main thread PRIMERO**
    logger.info('🔌 Conectando cámara en main thread...')
    if not camera.conectar_camara():
        logger.error('❌ No se pudo conectar a la cámara')
        return None
    
    logger.info('✅ Cámara conectada')
    
    # Ahora iniciar thread de captura (solo lectura)
    thread_captura = threading.Thread(target=camera.capturar_frames, daemon=True)
    thread_captura.start()
    logger.info('🎬 Thread de lectura iniciado')
    
    # Esperar a que se capture el primer frame
    max_espera = 5  # 5 segundos máximo
    inicio = time.time()
    while camera.frame_actual is None:
        time.sleep(0.1)
        if time.time() - inicio > max_espera:
            logger.error('❌ Timeout esperando primer frame')
            break
    
    if camera.frame_actual is not None:
        logger.info('✅ Primer frame capturado')
    
    return camera

def obtener_frame_base64():
    """Obtener frame en Base64 para enviar al frontend"""
    if camera is None:
        return None
    return camera.obtener_frame_base64()

def obtener_estado_camera():
    """Obtener estado de la cámara"""
    if camera is None:
        return {'conectada': False, 'grabando': False}
    return camera.obtener_estado()

def cerrar_camera():
    """Cerrar la cámara"""
    global camera
    if camera:
        camera.cerrar()
