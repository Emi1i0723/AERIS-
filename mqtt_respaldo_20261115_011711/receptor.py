import json
import paho.mqtt.client as mqtt
from datetime import datetime

BROKER = "localhost"
PORT = 1883

USUARIO = "pi"
CONTRASENA = "nasa2026$"

TOPICO = "nasa/astronautas/#"


def al_conectar(client, userdata, flags, rc):
    if rc == 0:
        print("Conectado correctamente a Mosquitto")
        client.subscribe(TOPICO)
        print("Escuchando datos de los astronautas...")
    else:
        print("Error de conexión:", rc)


def al_recibir(client, userdata, mensaje):
    try:
        datos = json.loads(mensaje.payload.decode("utf-8"))

        print("\n--- NUEVO DATO RECIBIDO ---")
        print("Tópico:", mensaje.topic)
        print("Datos:", datos)
        print("Hora:", datetime.now())

    except json.JSONDecodeError:
        print("Error: mensaje JSON no válido")


cliente = mqtt.Client()
cliente.username_pw_set(USUARIO, CONTRASENA)

cliente.on_connect = al_conectar
cliente.on_message = al_recibir

print("Iniciando receptor MQTT...")

cliente.connect(BROKER, PORT, 60)
cliente.loop_forever()
