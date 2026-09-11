import sqlite3

# Conexión: crea el archivo .db si no existe (acá, en memoria, para no
# dejar un archivo suelto — es solo para entender los conceptos).
conexion = sqlite3.connect(":memory:")
cursor = conexion.cursor()

# CREATE TABLE: define las COLUMNAS que va a tener cada REGISTRO (fila).
# "id INTEGER PRIMARY KEY" = una columna que identifica a cada fila de
# forma única y automática (SQLite le asigna el número solo).
cursor.execute("""
    CREATE TABLE jobs (
        id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        province TEXT NOT NULL
    )
""")

# INSERT: agrega un REGISTRO (una fila) a la TABLA.
cursor.execute(
    "INSERT INTO jobs (title, province) VALUES (?, ?)",
    ("Recepcionista", "Misiones")
)
cursor.execute(
    "INSERT INTO jobs (title, province) VALUES (?, ?)",
    ("Desarrollador/a", "Buenos Aires")
)
conexion.commit()  # guarda los cambios de verdad

# SELECT: consulta registros. WHERE filtra, como los "if" de filtrar_jobs().
cursor.execute("SELECT * FROM jobs WHERE province = ?", ("Misiones",))
for fila in cursor.fetchall():
    print(fila)   # (1, 'Recepcionista', 'Misiones')

conexion.close()

# Nota sobre Primary Key y Foreign Key:
# - Primary key: identifica cada fila de ESTA tabla (acá, "id").
# - Foreign key: una columna que APUNTA al id de OTRA tabla, para
#   relacionar datos (ej: si tuviéramos una tabla "companies",
#   jobs.company_id sería foreign key hacia companies.id).
#   Job todavía no tiene ninguna — va a aparecer cuando agreguemos
#   User, Company, etc. en los próximos módulos.
