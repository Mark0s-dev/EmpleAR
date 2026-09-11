from datetime import date

from flask import Flask, jsonify, request
from flask_cors import CORS

from data import CATEGORIES, LOCATIONS, SOURCES
from models import Job, db

app = Flask(__name__)
app.json.ensure_ascii = False  # así "í", "ñ", etc. se ven legibles en las respuestas

# CORS = Cross-Origin Resource Sharing. El navegador, por seguridad,
# bloquea que una página (ej. http://127.0.0.1:5500, el frontend con
# Live Server) le pida datos a otro origen (http://127.0.0.1:5000,
# este backend) — un "origen" distinto es cualquier combinación
# diferente de protocolo+dominio+puerto. CORS(app) le agrega a cada
# respuesta un header que le dice al navegador "está permitido".
CORS(app)

# sqlite:///emplear.db = usar SQLite, guardando en el archivo
# emplear.db (se crea solo, al lado de este archivo).
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///emplear.db"
db.init_app(app)


@app.route("/")
def home():
    return "EmpleAR backend funcionando 🚀"


def _dias_desde(fecha_iso, referencia):
    return (referencia - date.fromisoformat(fecha_iso)).days


def _fecha_mas_reciente(jobs):
    """La fecha más nueva entre los jobs de la base: la usamos como
    'hoy' del demo, igual que hacíamos en filters.js con getMockToday()."""
    return max(date.fromisoformat(j["publishedAt"]) for j in jobs)


def filtrar_jobs(criterios):
    # Job.query.all() trae TODAS las filas de la tabla "jobs" desde
    # SQLite. El filtrado, por ahora, lo seguimos haciendo acá en
    # Python (igual que con MOCK_JOBS) para no mezclar dos temas
    # nuevos a la vez — filtrar con SQL directamente (más eficiente
    # con muchos datos) lo vemos en el Módulo 7.
    jobs = [job.to_dict() for job in Job.query.all()]
    if not jobs:
        return []

    keyword = criterios.get("keyword", "").strip().lower()
    referencia = _fecha_mas_reciente(jobs)
    resultado = []

    for job in jobs:
        if keyword and keyword not in job["title"].lower() \
                and keyword not in job["company"].lower() \
                and keyword not in job["description"].lower():
            continue
        if criterios.get("provincia") and job["province"] != criterios["provincia"]:
            continue
        if criterios.get("ciudad") and job["city"] != criterios["ciudad"]:
            continue
        if criterios.get("categoria") and job["category"] != criterios["categoria"]:
            continue
        if criterios.get("modalidad") and job["modality"] != criterios["modalidad"]:
            continue
        if criterios.get("contrato") and job["contract"] != criterios["contrato"]:
            continue
        if criterios.get("horario") and job["schedule"] != criterios["horario"]:
            continue
        if criterios.get("fuente") and job["source"] != criterios["fuente"]:
            continue

        rango = criterios.get("fecha")
        if rango:
            dias = _dias_desde(job["publishedAt"], referencia)
            limite = {"24h": 1, "7d": 7, "30d": 30}.get(rango)
            if limite is not None and dias > limite:
                continue

        resultado.append(job)

    return resultado


# ===================== EMPLEOS =====================

@app.route("/api/jobs")
def get_jobs():
    # request.args son los ?parámetros=de la URL (ej: ?provincia=Misiones)
    criterios = {
        "keyword": request.args.get("keyword", ""),
        "provincia": request.args.get("provincia", ""),
        "ciudad": request.args.get("ciudad", ""),
        "categoria": request.args.get("categoria", ""),
        "modalidad": request.args.get("modalidad", ""),
        "contrato": request.args.get("contrato", ""),
        "horario": request.args.get("horario", ""),
        "fuente": request.args.get("fuente", ""),
        "fecha": request.args.get("fecha", ""),
    }
    return jsonify(filtrar_jobs(criterios))


@app.route("/api/jobs/<int:job_id>")
def get_job(job_id):
    job = db.session.get(Job, job_id)
    if job is None:
        return jsonify({"error": "Empleo no encontrado"}), 404
    return jsonify(job.to_dict())


@app.route("/api/jobs", methods=["POST"])
def create_job():
    datos = request.get_json(silent=True) or {}

    requeridos = ["title", "company", "province", "city", "category", "modality", "contract"]
    faltantes = [campo for campo in requeridos if not datos.get(campo)]
    if faltantes:
        return jsonify({"error": "Faltan campos obligatorios", "campos": faltantes}), 400

    # Ahora sí se guarda de verdad en SQLite.
    # TODO (Módulo 9): agregar estado de moderación (pending/approved/...)
    # antes de que estas ofertas aparezcan mezcladas con las reales.
    nuevo_job = Job(
        title=datos["title"],
        company=datos["company"],
        province=datos["province"],
        city=datos["city"],
        category=datos["category"],
        modality=datos["modality"],
        contract=datos["contract"],
        schedule=datos.get("horario", "manana"),
        description=datos.get("description", ""),
        source="EmpleAR",
        source_url="#",
        published_at=date.today().isoformat(),
        featured=False,
    )
    db.session.add(nuevo_job)
    db.session.commit()

    return jsonify(nuevo_job.to_dict()), 201


# ===================== UBICACIONES Y CATEGORÍAS =====================
# Provincia/Ciudad/Categoría/Fuente todavía son listas fijas (data.py),
# no tablas propias. Eso llega más adelante si hace falta que se
# administren dinámicamente — por ahora no cambian seguido.

@app.route("/api/provinces")
def get_provinces():
    return jsonify(list(LOCATIONS.keys()))


@app.route("/api/cities")
def get_cities():
    provincia = request.args.get("provincia")
    if provincia:
        return jsonify(LOCATIONS.get(provincia, []))
    todas = [ciudad for ciudades in LOCATIONS.values() for ciudad in ciudades]
    return jsonify(todas)


@app.route("/api/categories")
def get_categories():
    return jsonify(CATEGORIES)


@app.route("/api/sources")
def get_sources():
    return jsonify(SOURCES)


# ===================== CONTACTO =====================

@app.route("/api/contact", methods=["POST"])
def create_contact():
    datos = request.get_json(silent=True) or {}

    requeridos = ["nombre", "email", "motivo", "mensaje"]
    faltantes = [campo for campo in requeridos if not datos.get(campo)]
    if faltantes:
        return jsonify({"error": "Faltan campos obligatorios", "campos": faltantes}), 400

    # Todavía no se envía email de verdad ni se guarda (llega en el Módulo 15)
    return jsonify({"mensaje": "Consulta recibida. Te vamos a responder pronto."}), 201


if __name__ == "__main__":
    app.run(debug=True)
