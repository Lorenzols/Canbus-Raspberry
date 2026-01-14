#!/usr/bin/env python3
"""
Test sincrónico para diagnosticar conectar_camara()
"""

import sys
import logging

# Configurar logging para ver TODO
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)

print("\n" + "="*60)
print("🔍 TEST SINCRÓNICO - DIAGNOSTICO DE CÁMARA")
print("="*60 + "\n")

try:
    print("1️⃣  Importando camera.py...")
    from camera import CameraManager
    print("   ✅ camera.py importado\n")
    
    print("2️⃣  Creando CameraManager...")
    manager = CameraManager()
    print("   ✅ CameraManager creado\n")
    
    print("3️⃣  Llamando a conectar_camara() de forma SÍNCRONA...")
    resultado = manager.conectar_camara()
    print(f"\n   Resultado: {resultado}")
    
    if resultado:
        print("   ✅ ¡Conexión exitosa!\n")
        
        print("4️⃣  Leyendo 10 frames...")
        for i in range(10):
            ret, frame = manager.cap.read()
            if ret:
                print(f"   Frame {i+1}: ✅ OK ({frame.shape})")
            else:
                print(f"   Frame {i+1}: ❌ FALLO")
        
        print("\n✅ TODO FUNCIONA")
        manager.cerrar()
    else:
        print("   ❌ Conexión fallida")
        sys.exit(1)

except Exception as e:
    print(f"\n❌ ERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "="*60 + "\n")
