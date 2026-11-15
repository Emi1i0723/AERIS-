
import json
import time
import random
import math
import ast
from pathlib import Path

import paho.mqtt.client as mqtt

# CONFIGURACION MQTT
BROKER = "localhost"
PUERTO = 1883
USUARIO = "pi"

# Leer la contrasena MQTT del receptor local
ARCHIVO_RECEPTOR = (
    Path.home() / "nasa_space_apps" / "mqtt" / "receptor.py"
)

arbol = ast.parse(ARCHIVO_RECEPTOR.read_text())

CONTRASENA = next(
    nodo.value.value
    for nodo in arbol.body
    if isinstance(nodo, ast.Assign)
    and any(
        isinstance(t, ast.Name) and t.id == "CONTRASENA"
        for t in nodo.targets
    )
)

ASTRONAUTAS = ("astronauta1", "astronauta2")

# GENERACION DE DATOS SIMULADOS
def generar_datos(astronauta):
    ax = round(random.uniform(-0.20, 0.20), 2)
    ay = round(random.uniform(-0.20, 0.20), 2)
    az = round(random.uniform(0.90, 1.10), 2)

    aceleracion = round(
        math.sqrt(ax**2 + ay**2 + az**2), 2
    )

    return {
        "astronauta_id": astronauta,
        "frecuencia_cardiaca": random.randint(60, 110),
        "spo2": random.randint(94, 100),
        "temperatura": round(random.uniform(20, 38), 2),
        "ax": ax,
        "ay": ay,
        "az": az,
        "aceleracion_g": aceleracion
    }


# CLIENTE MQTT
cliente = mqtt.Client()
cliente.username_pw_set(USUARIO, CONTRASENA)

conectado = False


def al_conectar(client, userdata, flags, rc):
    global conectado

    conectado = (rc == 0)

    if conectado:
        print("Conectado correctamente a Mosquitto")
    else:
        print("Error de conexion MQTT:", rc)


def al_desconectar(client, userdata, rc):
    global conectado
    conectado = False
    print("Conexion MQTT interrumpida:", rc)


cliente.on_connect = al_conectar
cliente.on_disconnect = al_desconectar

print("Conectando con Mosquitto...")
cliente.connect(BROKER, PUERTO, 60)
cliente.loop_start()

try:
    # Esperar confirmacion de conexion
    for _ in range(50):
        if conectado:
            break
        time.sleep(0.1)

    if not conectado:
        raise ConnectionError(
            "No se pudo establecer conexion MQTT"
        )

    print("\nGENERADOR NASA INICIADO")
    print("Simulando dos astronautas")
    print("Intervalo: 3 segundos")
    print("Presiona Ctrl + C para detenerlo")

    while True:
        for astronauta in ASTRONAUTAS:
            if not conectado:
                print("Esperando reconexion MQTT...")
                break

            datos = generar_datos(astronauta)

            topico = (
                "nasa/astronautas/" + astronauta
            )

            mensaje = json.dumps(datos)

            resultado = cliente.publish(
                topico,
                mensaje,
                qos=1
            )

            if resultado.rc == mqtt.MQTT_ERR_SUCCESS:
                resultado.wait_for_publish(timeout=5)

                if resultado.is_published():
                    print("\nJSON PUBLICADO:")
                    print("Topico:", topico)
                    print(json.dumps(datos, indent=4))
                else:
                    print("Publicacion no confirmada:", astronauta)
            else:
                print(
                    "Error al publicar:",
                    astronauta,
                    resultado.rc
                )

        time.sleep(3)

except KeyboardInterrupt:
    print("\nGenerador detenido por el usuario")

except (ConnectionError, OSError) as error:
    print("Error:", error)

finally:
    cliente.loop_stop()
    cliente.disconnect()
    print("Desconectado de Mosquitto")
