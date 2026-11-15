
import json
import time
import random
from datetime import datetime
import paho.mqtt.client as mqtt

# CONFIGURACIÓN MQTT
BROKER = "localhost"
PUERTO = 1883

USUARIO = "pi"
CONTRASENA = "TU_CONTRASENA_MQTT"

TOPICO = "nasa/astronautas/astronauta1"

# CREAR CLIENTE
cliente = mqtt.Client()
cliente.username_pw_set(USUARIO, CONTRASENA)

# CONECTAR
print("Conectando con Mosquitto...")
cliente.connect(BROKER, PUERTO, 60)
cliente.loop_start()

print("GENERADOR NASA INICIADO")
print("Enviando datos cada 3 segundos...")
print("Presiona Ctrl + C para detenerlo.")

try:
    while True:
        datos = {
            "astronauta_id": "astronauta1",
            "frecuencia_cardiaca": random.randint(65, 110),
            "spo2": random.randint(94, 100),
            "temperatura": round(random.uniform(36.0, 38.0), 1),
            "timestamp": datetime.now().isoformat()
        }

        mensaje = json.dumps(datos)

        resultado = cliente.publish(TOPICO, mensaje)

        if resultado.rc == mqtt.MQTT_ERR_SUCCESS:
            print("\nJSON ENVIADO CORRECTAMENTE:")
            print(json.dumps(datos, indent=4))
        else:
            print("Error al enviar el mensaje MQTT")

        time.sleep(3)

except KeyboardInterrupt:
    print("\nGenerador detenido por el usuario.")

finally:
    cliente.loop_stop()
    cliente.disconnect()
    print("Desconectado de Mosquitto.")

