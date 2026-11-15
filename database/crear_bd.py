
import sqlite3
from pathlib import Path

# Ubicacion de la base de datos
CARPETA = Path(__file__).resolve().parent
BASE_DATOS = CARPETA / "astronautas.db"

# Conectar a SQLite
conexion = sqlite3.connect(BASE_DATOS)
cursor = conexion.cursor()

# Crear tabla de mediciones
cursor.execute("""
CREATE TABLE IF NOT EXISTS mediciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    astronauta_id TEXT NOT NULL,
    frecuencia_cardiaca INTEGER,
    spo2 INTEGER,
    temperatura REAL,
    ax REAL,
    ay REAL,
    az REAL,
    aceleracion_g REAL,
    fecha_recepcion TEXT NOT NULL
        DEFAULT (strftime('%Y-%m-%dT%H:%M:%f', 'now'))
)
""")

# Guardar cambios
conexion.commit()

# Cerrar conexion
conexion.close()

print("Base de datos creada correctamente.")
print("Archivo:", BASE_DATOS)
print("Tabla: mediciones")
