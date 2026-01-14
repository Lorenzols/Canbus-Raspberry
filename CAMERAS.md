# 📹 Sistema de Cámaras con YOLOv8

## Descripción General

Sistema de vigilancia con IA que:
- Captura video en tiempo real desde una webcam USB conectada a la Raspberry Pi
- Detecta automáticamente **personas** y **perros** usando YOLOv8
- **Graba automáticamente** cuando detecta algo
- Transmite el video en vivo al frontend React Native
- Visualiza detecciones en tiempo real con bounding boxes

## 🏗️ Arquitectura

```
Frontend (React Native)
    ↓ (solicita frames)
Backend (Node.js/Socket.IO)
    ↓ (retransmite frames)
Raspberry Pi (Python/YOLOv8)
    ↓ (captura + detecta)
Webcam USB + Almacenamiento (videos_grabados/)
```

## 📋 Requisitos

### Hardware
- Raspberry Pi 4 (recomendado) o Pi 3
- Webcam USB (cualquier modelo compatible con Linux)
- 2GB RAM mínimo
- 16GB SD Card mínimo (para grabar videos)

### Software
- Python 3.7+
- pip
- OpenCV
- YOLOv8 (Ultralytics)

## 🚀 Instalación

### 1. Instalar dependencias en Raspberry Pi

```bash
cd Canbus-Raspberry
pip install -r requirements.txt
```

**Nota:** YOLOv8 descargará el modelo `yolov8n.pt` (125MB) automáticamente en la primera ejecución.

### 2. Configurar IP del Backend

Edita `server.py`:

```python
BACKEND_URL = 'http://192.168.0.79:3000'  # Cambia por tu IP
```

### 3. Probar conexión de la cámara

```bash
python3 -c "import cv2; cap = cv2.VideoCapture(0); print('OK' if cap.isOpened() else 'FALLO')"
```

### 4. Ejecutar servidor Raspberry Pi

```bash
python3 server.py
```


## 🔧 Configuración Avanzada

### Ajustar sensibilidad de detección

En `camera.py`, línea ~100:

```python
resultados = self.modelo(frame, conf=0.5, verbose=False)
                                      ↑
                           Cambiar 0.5 a 0.3 (más sensible)
                           o a 0.7 (menos sensible)
```

### Cambiar FPS de captura

En `camera.py`, línea ~30:

```python
self.fps = 30  # Cambiar a 15 para menos carga CPU
```

### Cambiar tiempo de grabación automática

En `camera.py`, línea ~180:

```python
if self.grabando and tiempo_sin_detecciones > (self.fps * 5):
                                                         ↑
                                    Cambiar 5 a 10 (10 segundos)
```

### Cambiar modelo YOLOv8

En `camera.py`, línea ~40:

```python
self.modelo = YOLO('yolov8n.pt')  # nano (125MB, rápido)
# Opciones:
# yolov8s.pt - small (42MB)
# yolov8m.pt - medium (49MB)
# yolov8l.pt - large (83MB)
# yolov8x.pt - extra large (168MB)
```

## 📚 Referencias

- [YOLOv8 Documentación](https://docs.ultralytics.com/)
- [OpenCV Python](https://docs.opencv.org/master/d6/d00/tutorial_py_root.html)
- [Socket.IO Python](https://python-socketio.readthedocs.io/)
