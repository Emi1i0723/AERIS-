import json
import sqlite3
from pathlib import Path
from datetime import datetime, timezone

import paho.mqtt.client as mqtt

# CONFIGURACION MQTT
BROKER = "localhost"
PORT = 1883
USUARIO = "pi"

# Conservar aqui la contrasena MQTT existente
CONTRASENA = "nasa2026$"

TOPICO = "nasa/astronautas/#"

# BASE DE DATOS
BASE_DATOS = (
    Path.home()
    / "nasa_space_apps"
    / "database"
    / "astronautas.db"
)

CAMPOS = (
    "astronauta_id",
    "frecuencia_cardiaca",
    "spo2",
    "temperatura",
    "ax",
    "ay",
    "az",
    "aceleracion_g"
)


def validar_datos(datos):
    if not isinstance(datos, dict):
        raise ValueError("El JSON debe ser un objeto")

    faltantes = [c for c in CAMPOS if c not in datos]

    if faltantes:
        raise ValueError(
            "Campos faltantes: " + ", ".join(faltantes)
        )

    astronauta = datos["astronauta_id"]

    if not isinstance(astronauta, str) or not astronauta.strip():
        raise ValueError("astronauta_id no valido")

    for campo in ("frecuencia_cardiaca", "spo2"):
        valor = datos[campo]
        if type(valor) is not int:
            raise ValueError(campo + " debe ser entero")

    if not 0 <= datos["frecuencia_cardiaca"] <= 250:
        raise ValueError("Frecuencia cardiaca fuera de rango")

    if not 0 <= datos["spo2"] <= 100:
        raise ValueError("SpO2 fuera de rango")

    for campo in ("temperatura", "ax", "ay", "az", "aceleracion_g"):
        valor = datos[campo]

        if type(valor) not in (int, float):
            raise ValueError(campo + " debe ser numerico")

        import math
        if not math.isfinite(valor):
            raise ValueError(campo + " no es finito")

    if datos["aceleracion_g"] < 0:
        raise ValueError("Aceleracion negativa")

    return True


def guardar_medicion(datos):
    fecha = datetime.now(timezone.utc).isoformat()

    with sqlite3.connect(BASE_DATOS) as conexion:
        cursor = conexion.execute("""
            INSERT INTO mediciones (
                astronauta_id,
                frecuencia_cardiaca,
                spo2,
                temperatura,
                ax,
                ay,
                az,
                aceleracion_g,
                fecha_recepcion
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            datos["astronauta_id"],
            datos["frecuencia_cardiaca"],
            datos["spo2"],
            datos["temperatura"],
            datos["ax"],
            datos["ay"],
            datos["az"],
            datos["aceleracion_g"],
            fecha
        ))

        return cursor.lastrowid


def al_conectar(client, userdata, flags, rc):
    if rc == 0:
        print("Conectado correctamente a Mosquitto")
        client.subscribe(TOPICO)
        print("Escuchando datos de los astronautas...")
    else:
        print("Error de conexion MQTT:", rc)


def al_recibir(client, userdata, mensaje):
    try:
        datos = json.loads(
            mensaje.payload.decode("utf-8")
        )

        validar_datos(datos)

        registro_id = guardar_medicion(datos)

        print("\n--- NUEVO DATO RECIBIDO ---")
        print("Topico:", mensaje.topic)
        print("Astronauta:", datos["astronauta_id"])
        print("Datos:", datos)
        print("Registro SQLite:", registro_id)
        print("Guardado correctamente")

    except (UnicodeDecodeError, json.JSONDecodeError):
        print("Error: mensaje JSON no valido")

    except ValueError as error:
        print("Error de validacion:", error)

    except sqlite3.Error as error:
        print("Error al guardar en SQLite:", error)


# INICIAR RECEPTOR MQTT
cliente = mqtt.Client()
cliente.username_pw_set(USUARIO, CONTRASENA)

cliente.on_connect = al_conectar
cliente.on_message = al_recibir

print("Iniciando receptor MQTT con SQLite...")

cliente.connect(BROKER, PORT, 60)
cliente.loop_forever()
