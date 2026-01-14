#!/bin/bash
# Script de instalación automática para Raspberry Pi
# Uso: bash install_cameras.sh

set -e

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║     🎬 INSTALACIÓN - SISTEMA DE CÁMARAS CON YOLOv8          ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# Verificar que estamos en la carpeta correcta
if [ ! -f "server.py" ]; then
    echo "❌ Error: Este script debe ejecutarse desde la carpeta Canbus-Raspberry"
    echo "   Uso: cd Canbus-Raspberry && bash install_cameras.sh"
    exit 1
fi

echo "1️⃣  Actualizando sistema..."
sudo apt-get update
sudo apt-get upgrade -y

echo ""
echo "2️⃣  Instalando dependencias del sistema..."
sudo apt-get install -y python3-pip python3-dev

echo ""
echo "3️⃣  Creando carpeta de videos..."
mkdir -p videos_grabados
chmod 755 videos_grabados
echo "   ✅ Carpeta creada: videos_grabados/"

echo ""
echo "4️⃣  Instalando paquetes Python..."
echo "   ⏳ Esto puede tardar varios minutos (especialmente numpy y OpenCV)..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "5️⃣  Descargando modelo YOLOv8..."
echo "   ⏳ Descargando yolov8n.pt (~125MB)..."
python3 -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"

echo ""
echo "6️⃣  Probando cámara..."
if python3 -c "import cv2; cap = cv2.VideoCapture(0); exit(0 if cap.isOpened() else 1)"; then
    echo "   ✅ Cámara detectada correctamente"
else
    echo "   ⚠️  No se detectó cámara, pero la instalación continuó"
    echo "   📝 Comprueba con: lsusb"
fi

echo ""
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                    ✅ INSTALACIÓN COMPLETADA                  ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""
echo "📝 SIGUIENTES PASOS:"
echo ""
echo "1. Configura la IP del backend en server.py:"
echo "   nano server.py"
echo "   # Busca: BACKEND_URL = 'http://192.168.0.79:3000'"
echo "   # Cambiar 192.168.0.79 por tu IP real"
echo ""
echo "2. Ejecuta el servidor:"
echo "   python3 server.py"
echo ""
echo "3. Opcionalmente, prueba la cámara sin Socket.IO:"
echo "   python3 test_camera.py"
echo "   # Presiona 'q' para salir"
echo ""
echo "4. En el frontend, navega a '📹 Cámaras'"
echo ""
echo "📖 Para más información: cat CAMERAS.md"
echo ""
