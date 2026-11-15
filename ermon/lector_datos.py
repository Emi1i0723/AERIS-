
import sqlite3
from pathlib import Path

# Base de datos utilizada por el receptor MQTT
BASE_DATOS = Path(
    "/home/pi/nasa_space_apps/database/astronautas.db"
)

ASTRONAUTAS = ("astronauta1", "astronauta2")


def obtener_mediciones(astronauta_id, limite=30):
    """
    Recupera las ultimas mediciones de un astronauta.
    Devuelve una lista ordenada cronologicamente.
    """

    if astronauta_id not in ASTRONAUTAS:
        raise ValueError("Identificador de astronauta no valido")

    if not isinstance(limite, int) or not 1 <= limite <= 1000:
        raise ValueError("El limite debe estar entre 1 y 1000")

    # Abrimos SQLite exclusivamente en modo lectura
    conexion = sqlite3.connect(
        f"file:{BASE_DATOS}?mode=ro",
        uri=True,
        timeout=5
    )

    conexion.row_factory = sqlite3.Row

    try:
        cursor = conexion.execute(
            """
            SELECT
                id,
                astronauta_id,
                frecuencia_cardiaca,
                spo2,
                temperatura,
                ax,
                ay,
                az,
                aceleracion_g,
                fecha_recepcion
            FROM mediciones
            WHERE astronauta_id = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (astronauta_id, limite)
        )

        mediciones = [
            dict(fila) for fila in cursor.fetchall()
        ]

        mediciones.reverse()
        return mediciones

    finally:
        conexion.close()


def obtener_ultima_medicion(astronauta_id):
    """Devuelve la medicion mas reciente o None."""

    mediciones = obtener_mediciones(astronauta_id, 1)

    if mediciones:
        return mediciones[0]

    return None


if __name__ == "__main__":
    print("ERMON - Lector de datos SQLite")
    print("--------------------------------")

    for astronauta in ASTRONAUTAS:
        medicion = obtener_ultima_medicion(astronauta)

        if medicion is None:
            print(f"{astronauta}: sin mediciones")
        else:
            print(f"\n{astronauta}")
            print(f"Registro: {medicion['id']}")
            print(
                f"Frecuencia cardiaca: "
                f"{medicion['frecuencia_cardiaca']} bpm"
            )
            print(f"SpO2: {medicion['spo2']} %")
            print(f"Temperatura: {medicion['temperatura']} C")
            print(
                f"Aceleracion: "
                f"{medicion['aceleracion_g']} g"
            )
            print(
                f"Fecha: {medicion['fecha_recepcion']}"
            )
