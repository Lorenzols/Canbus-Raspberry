#!/usr/bin/env python3
"""
Test SIMPLE para diagnosticar problemas con la cámara
"""

import cv2
import sys

print("\n" + "="*60)
print("🔍 DIAGNÓSTICO DE CÁMARA - TEST SIMPLE")
print("="*60 + "\n")

print("Buscando cámaras disponibles...\n")

encontrada = False
for idx in range(10):
    print(f"Probando índice {idx}...", end=" ")
    cap = cv2.VideoCapture(idx)
    
    if cap.isOpened():
        # Intentar leer un frame
        ret, frame = cap.read()
        
        if ret:
            print("✅ CÁMARA ENCONTRADA!")
            encontrada = True
            
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            
            print(f"   Índice: {idx}")
            print(f"   Resolución: {width}x{height}")
            print(f"   FPS: {fps}")
            
            # Mostrar video
            print("\n📹 Mostrando video en vivo (presiona 'Q' para salir)\n")
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                cv2.imshow(f'Cámara - Índice {idx}', frame)
                
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q') or key == ord('Q'):
                    break
            
            cap.release()
            cv2.destroyAllWindows()
            break
        else:
            print("❌ No se pudo leer frame")
            cap.release()
    else:
        print("❌ No disponible")

if not encontrada:
    print("\n" + "="*60)
    print("❌ NO SE ENCONTRÓ NINGUNA CÁMARA")
    print("="*60)
    print("\n💡 Soluciones:")
    print("   1. Asegúrate de que la cámara USB está CONECTADA")
    print("   2. Abre Configuración → Privacidad → Cámara → Verifica permisos")
    print("   3. Prueba desconectar y reconectar la cámara")
    print("   4. Reinicia el ordenador")
    print("   5. Intenta con otra webcam o puerto USB")
    sys.exit(1)
else:
    print("\n✅ ¡ÉXITO! Tu cámara funciona correctamente")
