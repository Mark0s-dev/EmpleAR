from datetime import date

from flask import Flask, jsonify, request
from flask_cors import CORS

from data import CATEGORIES, LOCATIONS, MOCK_JOBS, SOURCES

app = Flask(__name__)
app.json.ensure_ascii = False  # así "í", "ñ", etc. se ven legibles en las respuestas

# CORS = Cross-Origin Resource Sharing. El navegador, por seguridad,
# bloquea que una página (ej. http://127.0.0.1:5500, el frontend con
# Live Server) le pida datos a otro origen (http://127.0.0.1:5000,
# este backend) — un "origen" distinto es cualquier combinación
# diferente de protocolo+dominio+puerto. CORS(app) le agrega a cada
# respuesta un header que le dice al navegador "está permitido".
CORS(app)


@app.route("/")
def home():
    return "EmpleAR backend funcionando 🚀"


def _dias_desde(fecha_iso, referencia):
    return (referencia - date.fromisoformat(fecha_iso)).days


def _fecha_mas_reciente():
    """La fecha más nueva entre los mock jobs: la usamos como 'hoy'
    del demo, igual que hacíamos en filters.js con getMockToday()."""
    return max(date.fromisoformat(j["publishedAt"]) for j in MOCK_JOBS)


def filtrar_jobs(criterios):
    keyword = criterios.get("keyword", "").strip().lower()
    referencia = _fecha_mas_reciente()
    resultado = []

    for job in MOCK_JOBS:
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


@app.route("/api/jobs/<job_id>")
def get_job(job_id):
    job = next((j for j in MOCK_JOBS if j["id"] == job_id), None)
    if job is None:
        return jsonify({"error": "Empleo no encontrado"}), 404
    return jsonify(job)


@app.route("/api/jobs", methods=["POST"])
def create_job():
    datos = request.get_json(silent=True) or {}

    requeridos = ["title", "company", "province", "city", "category", "modality", "contract"]
    faltantes = [campo for campo in requeridos if not datos.get(campo)]
    if faltantes:
        return jsonify({"error": "Faltan campos obligatorios", "campos": faltantes}), 400

    # Todavía no hay base de datos (llega en el Módulo 6), así que
    # esto NO se guarda de verdad: solo confirmamos que llegó bien
    # y devolvemos cómo quedaría, con estado "pending" (moderación).
    nuevo_job = {**datos, "id": "job-preview", "status": "pending"}
    return jsonify(nuevo_job), 201


# ===================== UBICACIONES Y CATEGORÍAS =====================

@app.route("/api/provinces")
def get_provinces():
    return jsonify(list(LOCATIONS.keys()))


@app.route("/api/cities")
def get_cities():
    provincia = request.args.get("provincia")
    if provincia:
        return jsonify(LOCATIONS.get(provincia, []))
    # Sin provincia: todas las ciudades, sin repetir por provincia
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

    # Todavía no se envía email de verdad (llega en el Módulo 15)
    return jsonify({"mensaje": "Consulta recibida. Te vamos a responder pronto."}), 201


if __name__ == "__main__":
    app.run(debug=True)
