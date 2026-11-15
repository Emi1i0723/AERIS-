
import json
import math
from datetime import datetime, timezone

from analizador import analizar_astronauta
from lector_datos import obtener_ultima_medicion
from modelo_ml import ModeloErmon


MAX_ANTIGUEDAD_SEG = 30

VARIABLES = (
    "frecuencia_cardiaca",
    "spo2",
    "temperatura",
    "aceleracion_g"
)


def evaluar_modelo_ml(medicion):
    """
    Evalua el modelo experimental de aprendizaje automatico.
    No realiza diagnosticos medicos.
    """
    try:
        modelo = ModeloErmon()
        modelo.cargar()

        resultado = modelo.predecir(medicion)

        resultado["modo"] = "experimental"
        resultado["validacion"] = "pendiente"

        return resultado

    except (OSError, ValueError, RuntimeError) as error:
        return {
            "estado": "modelo_no_disponible",
            "modo": "experimental",
            "mensaje": str(error)
        }


def evaluar_astronauta(astronauta_id):
    """
    Evalua calidad, vigencia, desviaciones estadisticas
    y patrones multivariables mediante ML experimental.
    No realiza diagnosticos medicos.
    """

    analisis = analizar_astronauta(astronauta_id)
    ultima = obtener_ultima_medicion(astronauta_id)

    alertas = []
    fecha_actual = datetime.now(timezone.utc)

    if ultima is None:
        return {
            "astronauta_id": astronauta_id,
            "estado_general": "sin_datos",
            "modelo_ml": {
                "estado": "sin_datos",
                "modo": "experimental"
            },
            "alertas": [{
                "tipo": "datos",
                "nivel": "informativo",
                "mensaje": "No hay mediciones disponibles"
            }]
        }

    # Verificar antiguedad de la medicion
    try:
        fecha_medicion = datetime.fromisoformat(
            ultima["fecha_recepcion"].replace("Z", "+00:00")
        )

        if fecha_medicion.tzinfo is None:
            fecha_medicion = fecha_medicion.replace(
                tzinfo=timezone.utc
            )

        antiguedad = (
            fecha_actual - fecha_medicion
        ).total_seconds()

    except (ValueError, TypeError, KeyError):
        antiguedad = None

    if antiguedad is None:
        alertas.append({
            "tipo": "datos",
            "nivel": "atencion",
            "mensaje": "Fecha de medicion no valida"
        })

    elif antiguedad > MAX_ANTIGUEDAD_SEG:
        alertas.append({
            "tipo": "datos",
            "nivel": "atencion",
            "mensaje": "No se reciben mediciones recientes"
        })

    # Verificar calidad de los valores
    datos_validos = True

    for variable in VARIABLES:
        valor = ultima.get(variable)

        if (
            isinstance(valor, bool)
            or not isinstance(valor, (int, float))
            or not math.isfinite(valor)
        ):
            datos_validos = False

            alertas.append({
                "tipo": "calidad_datos",
                "nivel": "atencion",
                "variable": variable,
                "mensaje": "Valor ausente o no valido"
            })

    # Analisis estadistico
    for variable, resultado in analisis["analisis"].items():
        estado = resultado["estado"]

        if estado == "desviacion_detectada":
            alertas.append({
                "tipo": "anomalia_estadistica",
                "nivel": "atencion",
                "variable": variable,
                "z_score": resultado.get("z_score"),
                "mensaje": "Desviacion estadistica detectada"
            })

        elif estado == "variacion_sin_referencia":
            alertas.append({
                "tipo": "anomalia_estadistica",
                "nivel": "informativo",
                "variable": variable,
                "mensaje": "Cambio respecto a referencia constante"
            })

        elif estado == "datos_insuficientes":
            alertas.append({
                "tipo": "datos",
                "nivel": "informativo",
                "variable": variable,
                "mensaje": "Historial insuficiente para analizar"
            })

    # Evaluacion con aprendizaje automatico
    if datos_validos:
        resultado_ml = evaluar_modelo_ml(ultima)
    else:
        resultado_ml = {
            "estado": "datos_invalidos",
            "modo": "experimental"
        }

    # El modelo actual fue entrenado con datos simulados.
    # Sus resultados se reportan como informativos.
    if resultado_ml["estado"] == "anomalia_ml":
        alertas.append({
            "tipo": "anomalia_ml",
            "nivel": "informativo",
            "distancia": resultado_ml["distancia"],
            "umbral": resultado_ml["umbral"],
            "mensaje": (
                "Patron diferente al modelo experimental"
            )
        })

    # Determinar estado general
    if any(a["nivel"] == "atencion" for a in alertas):
        estado_general = "atencion"
    elif alertas:
        estado_general = "informativo"
    else:
        estado_general = "sin_alertas"

    return {
        "astronauta_id": astronauta_id,
        "estado_general": estado_general,
        "ultimo_registro": ultima["id"],
        "fecha_medicion": ultima["fecha_recepcion"],
        "antiguedad_seg": (
            round(antiguedad, 1)
            if antiguedad is not None else None
        ),
        "alertas": alertas,
        "analisis": analisis["analisis"],
        "modelo_ml": resultado_ml
    }


if __name__ == "__main__":
    print("ERMON - Evaluacion preventiva")
    print("-----------------------------")

    for astronauta in ("astronauta1", "astronauta2"):
        resultado = evaluar_astronauta(astronauta)

        print(
            json.dumps(
                resultado,
                indent=2,
                ensure_ascii=False
            )
        )
