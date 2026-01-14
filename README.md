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

Para más información sobre Socket.IO en Python:
https://python-socketio.readthedocs.io/
