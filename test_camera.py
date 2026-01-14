#!/usr/bin/env python3
"""
Script de prueba para la cámara y YOLOv8
Útil para debugging sin necesidad del servidor Socket.IO
"""

import cv2
import sys
import time

print("\n" + "="*60)
print("🎬 TEST DE CÁMARA CON YOLOv8")
print("="*60 + "\n")

try:
    print("1️⃣  Importando módulos...")
    from camera import CameraManager
    import threading
    print("   ✅ Módulos importados\n")
    
    # Crear gestor de cámara
    print("2️⃣  Inicializando cámara...")
    camera = CameraManager()
    print("   ✅ Creada\n")
    
    # Conectar cámara en MAIN THREAD (importante en Windows)
    print("3️⃣  Conectando cámara...")
    if not camera.conectar_camara():
        print("   ❌ Error al conectar cámara\n")
        sys.exit(1)
    print("   ✅ Conectada\n")
    
    # Iniciar thread de lectura
    print("4️⃣  Iniciando thread de lectura...")
    thread = threading.Thread(target=camera.capturar_frames, daemon=True)
    thread.start()
    print("   ✅ Thread iniciado\n")
    
    # Esperar primer frame
    print("5️⃣  Esperando primer frame...")
    for i in range(50):
        if camera.frame_actual is not None:
            print(f"   ✅ Recibido en {i*0.1:.1f}s\n")
            break
        time.sleep(0.1)
    
    if camera.frame_actual is None:
        print("   ❌ ERROR: No se recibió frame de la cámara\n")
        sys.exit(1)
    
    print("="*60)
    print("✅ ¡LISTO! Deberías ver una ventana con tu webcam")
    print("   - Presiona 'Q' para salir")
    print("   - Detecta automáticamente personas y perros")
    print("="*60 + "\n")
    
    frame_count = 0
    while True:
        # Obtener frame
        frame = camera.frame_actual
        detecciones = camera.detecciones
        estado = camera.obtener_estado()
        
        if frame is not None:
            # Mostrar frame en ventana
            cv2.imshow('YOLOv8 - Detección en vivo', frame)
            
            # Estadísticas
            frame_count += 1
            if frame_count % 30 == 0:  # Cada 30 frames
                print(f"\n📊 ESTADÍSTICAS (frame {frame_count}):")
                print(f"   Cámara: {'✅ Conectada' if estado['conectada'] else '❌ Desconectada'}")
                print(f"   Grabando: {'🔴 SÍ' if estado['grabando'] else '⚫ NO'}")
                print(f"   Detecciones: {estado['detecciones']}")
                if estado['clases']:
                    print(f"   Detectados: {', '.join(estado['clases'])}")
                print()
        
        # Salir con 'q' o 'Q'
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == ord('Q'):
            print("\n👋 Saliendo...")
            break
        
        time.sleep(0.01)

except ModuleNotFoundError as e:
    print(f"❌ ERROR: Módulo faltante: {e}")
    print("\n📝 Solución:")
    print("   pip install opencv-python ultralytics numpy")
    sys.exit(1)
    
except Exception as e:
    print(f"❌ ERROR: {type(e).__name__}: {e}")
    print("\n📝 Posibles soluciones:")
    print("   1. ¿Tienes una webcam USB conectada?")
    print("   2. ¿Está la cámara siendo usada por otra app?")
    print("   3. Intenta reiniciar Python")
    import traceback
    traceback.print_exc()
    sys.exit(1)

finally:
    print("\n🧹 Limpiando recursos...")
    camera.cerrar()
    cv2.destroyAllWindows()
    print("✅ Test completado")



