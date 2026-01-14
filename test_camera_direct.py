#!/usr/bin/env python3
"""
Test directo sin usar inicializar_camera()
"""

import logging
import sys
import time
import threading

# Asegurar que logging funciona
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)

print("\n" + "="*60)
print("🔍 TEST DIRECTO - Conectar en main thread")
print("="*60 + "\n")

try:
    print("1️⃣  Importando camera.py...")
    from camera import CameraManager
    print("   ✅ Importado\n")
    
    print("2️⃣  Creando CameraManager()...")
    manager = CameraManager()
    print("   ✅ Creado\n")
    
    print("3️⃣  Conectando cámara en MAIN THREAD (esto es importante en Windows)...")
    if not manager.conectar_camara():
        print("   ❌ Fallo al conectar\n")
        sys.exit(1)
    print("   ✅ Cámara conectada\n")
    
    print("4️⃣  Iniciando thread de lectura de frames...")
    thread = threading.Thread(target=manager.capturar_frames, daemon=True)
    thread.start()
    print("   ✅ Thread iniciado\n")
    
    print("5️⃣  Esperando primer frame (5 segundos max)...")
    for i in range(50):
        if manager.frame_actual is not None:
            print(f"   ✅ ¡Frame recibido en {i*0.1:.1f} segundos!\n")
            break
        time.sleep(0.1)
    
    if manager.frame_actual is None:
        print("   ❌ Timeout - no hay frames\n")
        sys.exit(1)
    
    print("6️⃣  Mostrando video en vivo (presiona Q para salir)...")
    print("   (Si no ves la ventana, es normal en ciertos entornos)")
    print()
    
    import cv2
    frame_count = 0
    while True:
        frame = manager.frame_actual
        if frame is not None:
            cv2.imshow('Test Directo - YOLOv8', frame)
            frame_count += 1
            
            if frame_count % 30 == 0:
                print(f"   📹 {frame_count} frames mostrados")
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == ord('Q'):
            break
        
        time.sleep(0.01)
    
    cv2.destroyAllWindows()
    manager.cerrar()
    print("\n✅ Test completado exitosamente")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

