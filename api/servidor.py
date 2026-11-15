
from flask import Flask, jsonify, request, render_template
import sqlite3
import sys
from pathlib import Path

# CONFIGURACION
app = Flask(__name__)

BASE_PROYECTO = Path.home() / "nasa_space_apps"
BASE_DATOS = BASE_PROYECTO / "database" / "astronautas.db"

# Permitir importar los modulos de Ermon
RUTA_ERMON = BASE_PROYECTO / "ermon"
if str(RUTA_ERMON) not in sys.path:
    sys.path.insert(0, str(RUTA_ERMON))


# CONEXION A SQLITE
def conectar_bd():
    conexion = sqlite3.connect(BASE_DATOS)
    conexion.row_factory = sqlite3.Row
    return conexion

# DASHBOARD PRINCIPAL DE AERIS
@app.route("/", methods=["GET"])
def dashboard():
    return render_template("index.html")

# ESTADO DEL SERVIDOR
@app.route("/api/estado", methods=["GET"])
def estado():
    return jsonify({
        "sistema": "NASA Space Apps",
        "servidor": "Pi No Gemelo",
        "estado": "activo"
    })


# LISTA DE ASTRONAUTAS
@app.route("/api/astronautas", methods=["GET"])
def astronautas():
    try:
        with conectar_bd() as conexion:
            registros = conexion.execute("""
                SELECT DISTINCT astronauta_id
                FROM mediciones
                ORDER BY astronauta_id
            """).fetchall()

        return jsonify({
            "astronautas": [
                fila["astronauta_id"]
                for fila in registros
            ]
        })

    except sqlite3.Error:
        return jsonify({
            "error": "Error al consultar SQLite"
        }), 500


# ULTIMA MEDICION DE UN ASTRONAUTA
@app.route(
    "/api/astronautas/<astronauta_id>/ultimo",
    methods=["GET"]
)
def ultima_medicion(astronauta_id):
    try:
        with conectar_bd() as conexion:
            registro = conexion.execute("""
                SELECT *
                FROM mediciones
                WHERE astronauta_id = ?
                ORDER BY id DESC
                LIMIT 1
            """, (astronauta_id,)).fetchone()

        if registro is None:
            return jsonify({
                "error": "Astronauta sin mediciones"
            }), 404

        return jsonify(dict(registro))

    except sqlite3.Error:
        return jsonify({
            "error": "Error al consultar SQLite"
        }), 500


# HISTORICO DE MEDICIONES POR ASTRONAUTA
@app.route(
    "/api/astronautas/<astronauta_id>/historico",
    methods=["GET"]
)
def historico(astronauta_id):

    limite_texto = request.args.get("limite", "50")

    try:
        limite = int(limite_texto)
    except ValueError:
        return jsonify({
            "error": "El limite debe ser un numero entero"
        }), 400

    if limite < 1 or limite > 1000:
        return jsonify({
            "error": "El limite debe estar entre 1 y 1000"
        }), 400

    try:
        with conectar_bd() as conexion:
            registros = conexion.execute("""
                SELECT *
                FROM mediciones
                WHERE astronauta_id = ?
                ORDER BY id DESC
                LIMIT ?
            """, (
                astronauta_id,
                limite
            )).fetchall()

        mediciones = [
            dict(registro)
            for registro in reversed(registros)
        ]

        return jsonify({
            "astronauta_id": astronauta_id,
            "total": len(mediciones),
            "mediciones": mediciones
        })

    except sqlite3.Error:
        return jsonify({
            "error": "Error al consultar SQLite"
        }), 500


# ERMON - MONITOREO PREVENTIVO CON ML
@app.route(
    "/api/ermon/<astronauta_id>",
    methods=["GET"]
)
def consultar_ermon(astronauta_id):

    # Validar astronauta
    if astronauta_id not in (
        "astronauta1",
        "astronauta2"
    ):
        return jsonify({
            "error": "Astronauta no valido"
        }), 400

    try:
        from alertas import evaluar_astronauta

        resultado = evaluar_astronauta(
            astronauta_id
        )

        return jsonify(resultado)

    except (sqlite3.Error, OSError, ValueError,
            RuntimeError, KeyError, TypeError):
        app.logger.exception(
            "Error al ejecutar Ermon"
        )

        return jsonify({
            "error": "Error al ejecutar Ermon",
            "astronauta_id": astronauta_id
        }), 500


# INICIAR API
if __name__ == "__main__":
    print("Iniciando API NASA Space Apps...")
    print("Servidor: Pi No Gemelo")
    print("Puerto: 5000")

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )
