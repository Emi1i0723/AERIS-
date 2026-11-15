
import numpy as np
from lector_datos import obtener_mediciones

VARIABLES = {
    "frecuencia_cardiaca": "Frecuencia cardiaca",
    "spo2": "SpO2",
    "temperatura": "Temperatura",
    "aceleracion_g": "Aceleracion"
}

VENTANA = 30
MIN_MUESTRAS = 10
UMBRAL_Z = 2.5


def analizar_variable(mediciones, variable):
    """
    Compara la ultima medicion contra las anteriores.
    Utiliza media y desviacion estandar.
    """

    valores = []

    for medicion in mediciones:
        valor = medicion.get(variable)

        if isinstance(valor, (int, float)):
            if np.isfinite(valor):
                valores.append(float(valor))

    if len(valores) < MIN_MUESTRAS:
        return {
            "estado": "datos_insuficientes",
            "muestras": len(valores)
        }

    # La ultima muestra es la que evaluaremos
    actual = valores[-1]

    # Referencia construida con las muestras anteriores
    referencia = np.array(valores[:-1], dtype=float)

    media = float(np.mean(referencia))
    desviacion = float(np.std(referencia))

    diferencia = actual - media

    if desviacion < 1e-6:
        if abs(diferencia) < 1e-6:
            z_score = 0.0
        else:
            z_score = None
    else:
        z_score = float(diferencia / desviacion)

    if z_score is None:
        estado = "variacion_sin_referencia"
    elif abs(z_score) >= UMBRAL_Z:
        estado = "desviacion_detectada"
    else:
        estado = "sin_desviacion_estadistica"

    return {
        "estado": estado,
        "muestras": len(valores),
        "valor_actual": round(actual, 3),
        "media_referencia": round(media, 3),
        "desviacion_referencia": round(desviacion, 3),
        "diferencia": round(diferencia, 3),
        "z_score": (
            round(z_score, 3)
            if z_score is not None
            else None
        )
    }


def analizar_astronauta(astronauta_id):
    mediciones = obtener_mediciones(
        astronauta_id,
        limite=VENTANA
    )

    resultados = {}

    for variable in VARIABLES:
        resultados[variable] = analizar_variable(
            mediciones,
            variable
        )

    return {
        "astronauta_id": astronauta_id,
        "registros_consultados": len(mediciones),
        "ultimo_registro": (
            mediciones[-1]["id"]
            if mediciones else None
        ),
        "analisis": resultados
    }


if __name__ == "__main__":
    import json

    print("ERMON - Analisis estadistico")
    print("----------------------------")

    for astronauta in ("astronauta1", "astronauta2"):
        resultado = analizar_astronauta(astronauta)

        print(
            json.dumps(
                resultado,
                indent=2,
                ensure_ascii=False
            )
        )
