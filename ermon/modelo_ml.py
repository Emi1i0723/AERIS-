
import numpy as np
import json
from pathlib import Path

VARIABLES = (
    "frecuencia_cardiaca",
    "spo2",
    "aceleracion_g"
)

RUTA_MODELO = Path(
    "/home/pi/nasa_space_apps/ermon/modelo_ermon.npz"
)


class ModeloErmon:

    def __init__(self):
        self.media = None
        self.inversa_covarianza = None
        self.umbral = None

    def convertir_datos(self, mediciones):
        filas = []

        for medicion in mediciones:
            try:
                fila = [
                    float(medicion[v])
                    for v in VARIABLES
                ]

                if np.all(np.isfinite(fila)):
                    filas.append(fila)

            except (KeyError, ValueError, TypeError):
                continue

        return np.array(filas, dtype=float).reshape(
            -1, len(VARIABLES)
        )

    def entrenar(self, mediciones):
        X = self.convertir_datos(mediciones)

        if len(X) < 20:
            raise ValueError(
                "Se necesitan al menos 20 mediciones"
            )

        self.media = np.mean(X, axis=0)

        covarianza = np.cov(X, rowvar=False)

        # Regularizacion para evitar matrices singulares
        regularizacion = np.diag(
            np.maximum(np.diag(covarianza) * 0.01, 1e-4)
        )

        covarianza += regularizacion

        self.inversa_covarianza = np.linalg.inv(
            covarianza
        )

        distancias = self.calcular_distancias(X)

        # Umbral aprendido de los datos de entrenamiento
        self.umbral = float(
            np.percentile(distancias, 99)
        )

        return {
            "muestras_entrenamiento": len(X),
            "media": self.media.tolist(),
            "umbral": self.umbral
        }

    def calcular_distancias(self, X):
        diferencias = X - self.media

        distancias_cuadradas = np.einsum(
            "ij,jk,ik->i",
            diferencias,
            self.inversa_covarianza,
            diferencias
        )

        return np.sqrt(
            np.maximum(distancias_cuadradas, 0)
        )

    def predecir(self, medicion):
        if self.media is None:
            raise RuntimeError(
                "El modelo no esta entrenado"
            )

        X = self.convertir_datos([medicion])

        if len(X) != 1:
            return {
                "estado": "datos_invalidos"
            }

        distancia = float(
            self.calcular_distancias(X)[0]
        )

        return {
            "estado": (
                "anomalia_ml"
                if distancia > self.umbral
                else "patron_compatible"
            ),
            "distancia": round(distancia, 4),
            "umbral": round(self.umbral, 4),
            "variables": list(VARIABLES)
        }

    def guardar(self, ruta=RUTA_MODELO):
        if self.media is None or self.umbral is None:
            raise RuntimeError("Modelo no entrenado")

        np.savez(
            ruta,
            media=self.media,
            inversa_covarianza=self.inversa_covarianza,
            umbral=self.umbral
        )

    def cargar(self, ruta=RUTA_MODELO):
        with np.load(ruta, allow_pickle=False) as datos:
            self.media = datos["media"]
            self.inversa_covarianza = datos[
                "inversa_covarianza"
            ]
            self.umbral = float(datos["umbral"])


if __name__ == "__main__":
    from lector_datos import obtener_mediciones

    modelo = ModeloErmon()

    # Prueba inicial con datos historicos simulados
    mediciones = obtener_mediciones(
        "astronauta1",
        limite=100
    )

    resultado = modelo.entrenar(mediciones)

    print("ERMON - Entrenamiento ML")
    print(json.dumps(resultado, indent=2))

    modelo.guardar()

    print("\nModelo guardado correctamente")

    prueba = modelo.predecir(mediciones[-1])

    print("\nEvaluacion de prueba:")
    print(json.dumps(prueba, indent=2))
