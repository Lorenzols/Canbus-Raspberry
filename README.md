# Servidor CAN Bus - Raspberry Pi

Servidor Socket.IO en Python para controlar las ventanas del coche mediante CAN Bus.

## 📋 Requisitos

- **Python 3.7+** instalado
- **pip** (gestor de paquetes de Python)
- Conexión a la red local con el backend
- (En Raspberry Pi) CAN Bus configurado

## 🚀 Instalación

### 1. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 2. Configurar IP del backend

Edita `server.py` y cambia esta línea con la IP real de tu backend:

```python
BACKEND_URL = 'http://192.168.0.79:3000'  # Cambia esto
```

## ▶️ Ejecución

### Opción 1: Ejecución simple

```bash
python3 server.py
```

### Opción 2: Ejecución en background (Raspberry Pi)

```bash
nohup python3 server.py > server.log 2>&1 &
```

### Opción 3: Ejecución con auto-reinicio (Raspberry Pi)

Instala supervisord:
```bash
sudo apt-get install supervisor
```

Crea archivo `/etc/supervisor/conf.d/canbus.conf`:
```ini
[program:canbus]
command=/usr/bin/python3 /home/pi/TFG/Canbus-Raspberry/server.py
autostart=true
autorestart=true
stderr_logfile=/var/log/canbus.err.log
stdout_logfile=/var/log/canbus.out.log
user=pi
```

Luego:
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start canbus
```

## 📊 Salida esperada

```
🚀 Servidor Raspberry Pi iniciado
🔗 Conectando a backend: http://192.168.0.79:3000
🚗 ID del coche: CITROEN_C4_001

✅ Conectado al backend
📍 Registrado como coche: CITROEN_C4_001

📥 Comando ventana recibido: {'ventanaId': 'ventana_conductor', 'accion': 'bajar'}

🚗 Ejecutando acción: BAJAR
📍 Ventana: Ventana Conductor (Delantera Izquierda)
📊 ID CAN: 14C
📤 Datos CAN: 8080000080
⚙️ Comando: cangen can0 -g 2 -I 14C -L 5 -D 8080000080 -n 25

✅ [SIMULACIÓN] Comando CAN ejecutado correctamente
```

## 🔧 Configuración de CAN Bus en Raspberry Pi

### Habilitar CAN0

```bash
sudo nano /boot/config.txt
```

Agrega al final:
```
dtparam=spi=on
dtoverlay=mcp2515-can0,oscillator=16000000,interrupt=25
dtoverlay=spi-bcm2835-overlay
```

Reinicia:
```bash
sudo reboot
```

Verifica:
```bash
ifconfig can0
sudo ip link set can0 up type can bitrate 500000
```

### Instalar herramientas CAN (opcional)

```bash
sudo apt-get install can-utils
```

Prueba:
```bash
cangen can0 -g 2 -I 14C -L 5 -D 8080000080 -n 1
```

## ⚠️ Notas importantes

1. **Testing sin hardware CAN**: El servidor funciona en modo simulación. Solo loguea los comandos sin ejecutarlos.

2. **Ejecutar en Raspberry real**: Descomenta la línea en `ejecutar_comando_can()`:
   ```python
   subprocess.run(comando, shell=True, check=True)
   ```

3. **Verifica la IP del backend** antes de ejecutar

4. **Logs**: Revisa la salida para diagnosticar problemas

## 🐛 Troubleshooting

**Error: "No module named 'socketio'"**
```bash
pip install python-socketio
```

**Error de conexión al backend**
- Verifica que la IP y puerto sean correctos
- Comprueba que el backend está ejecutándose
- Verifica la conexión de red

**Comando CAN no se ejecuta**
- Debes estar en una Raspberry Pi real con CAN Bus configurado
- Descomenta la línea de `subprocess.run()` en el código
- Verifica que `cangen` está instalado: `which cangen`

## 📞 Soporte

Para más información sobre Socket.IO en Python:
https://python-socketio.readthedocs.io/
