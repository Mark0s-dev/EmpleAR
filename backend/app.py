from datetime import date, timedelta
from functools import wraps
import os

from flask import Flask, jsonify, request
from flask_cors import CORS
from sqlalchemy import func, or_

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

# Token de administrador MUY simple, solo para no dejar los endpoints
# de moderación abiertos a cualquiera mientras no existe un sistema
# de usuarios real (eso es el Módulo 13, con login y roles de verdad).
# Se lee de una variable de entorno; si no está configurada, usa un
# valor de desarrollo — NUNCA usar ese valor por defecto en producción.
ADMIN_TOKEN = os.environ.get("EMPLEAR_ADMIN_TOKEN", "dev-admin-1234")


def require_admin(vista):
    """Decorador: envuelve una ruta y exige el header
    'X-Admin-Token' con el valor correcto antes de ejecutarla."""
    @wraps(vista)
    def envoltorio(*args, **kwargs):
        token = request.headers.get("X-Admin-Token")
        if token != ADMIN_TOKEN:
            return jsonify({"error": "No autorizado"}), 401
        return vista(*args, **kwargs)
    return envoltorio


@app.route("/")
def home():
    return "EmpleAR backend funcionando 🚀"


def _fecha_mas_reciente():
    """La fecha más nueva guardada en la tabla jobs (consultada con
    SQL, no calculada en Python): la usamos como 'hoy' del demo."""
    ultima = db.session.query(func.max(Job.published_at)).scalar()
    return date.fromisoformat(ultima) if ultima else date.today()


def filtrar_jobs(criterios):
    """Arma un SELECT ... WHERE ... agregando condiciones solo para
    los filtros que el usuario realmente eligió. SQLite es quien
    filtra — Python ya no recorre nada a mano."""
    # Solo se muestran ofertas aprobadas: las "pending" (recién
    # publicadas, sin revisar) y "rejected" no aparecen en la
    # búsqueda pública. El panel de moderación (Módulo 9) sí las
    # va a poder ver todas.
    query = Job.query.filter(Job.status == "approved")

    keyword = criterios.get("keyword", "").strip()
    if keyword:
        patron = f"%{keyword}%"
        # or_(): que matchee CUALQUIERA de las tres columnas.
        # ilike: como LIKE de SQL, pero sin importar mayúsculas/minúsculas.
        query = query.filter(or_(
            Job.title.ilike(patron),
            Job.company.ilike(patron),
            Job.description.ilike(patron),
        ))

    campo_por_criterio = {
        "provincia": Job.province,
        "ciudad": Job.city,
        "categoria": Job.category,
        "modalidad": Job.modality,
        "contrato": Job.contract,
        "horario": Job.schedule,
        "fuente": Job.source,
    }
    for criterio, columna in campo_por_criterio.items():
        valor = criterios.get(criterio)
        if valor:
            query = query.filter(columna == valor)

    rango = criterios.get("fecha")
    limite = {"24h": 1, "7d": 7, "30d": 30}.get(rango)
    if limite is not None:
        fecha_minima = _fecha_mas_reciente() - timedelta(days=limite)
        query = query.filter(Job.published_at >= fecha_minima.isoformat())

    # Las más nuevas primero — antes esto no estaba garantizado.
    return query.order_by(Job.published_at.desc()).all()


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
    return jsonify([job.to_dict() for job in filtrar_jobs(criterios)])


@app.route("/api/jobs/<int:job_id>")
def get_job(job_id):
    job = db.session.get(Job, job_id)
    if job is None:
        return jsonify({"error": "Empleo no encontrado"}), 404
    return jsonify(job.to_dict())


MODALIDADES_VALIDAS = {"presencial", "remoto", "hibrido"}
CONTRATOS_VALIDOS = {"tiempo-completo", "medio-tiempo", "temporal", "freelance"}
HORARIOS_VALIDOS = {"manana", "tarde", "noche", "rotativo"}


def validar_job(datos):
    """Devuelve un dict {campo: 'motivo del error'}. Vacío = todo bien.
    No permite datos claramente inválidos (ni vacíos, ni fuera de las
    opciones que el propio formulario ofrece, ni textos irrisoriamente
    cortos)."""
    errores = {}

    def requerido(campo, minimo=1):
        valor = (datos.get(campo) or "").strip()
        if len(valor) < minimo:
            errores[campo] = f"Debe tener al menos {minimo} caracteres."

    requerido("title", minimo=3)
    requerido("company", minimo=2)
    requerido("description", minimo=20)

    provincia = datos.get("province")
    if provincia not in LOCATIONS:
        errores["province"] = "Provincia inválida."
    elif datos.get("city") not in LOCATIONS[provincia]:
        errores["city"] = "Esa ciudad no pertenece a la provincia elegida."

    if datos.get("category") not in CATEGORIES:
        errores["category"] = "Categoría inválida."
    if datos.get("modality") not in MODALIDADES_VALIDAS:
        errores["modality"] = "Modalidad inválida."
    if datos.get("contract") not in CONTRATOS_VALIDOS:
        errores["contract"] = "Tipo de contrato inválido."
    if datos.get("horario") not in HORARIOS_VALIDOS:
        errores["horario"] = "Horario inválido."

    return errores


@app.route("/api/jobs", methods=["POST"])
def create_job():
    datos = request.get_json(silent=True) or {}

    errores = validar_job(datos)
    if errores:
        return jsonify({"error": "Revisá los datos del formulario", "detalles": errores}), 400

    nuevo_job = Job(
        title=datos["title"].strip(),
        company=datos["company"].strip(),
        province=datos["province"],
        city=datos["city"],
        category=datos["category"],
        modality=datos["modality"],
        contract=datos["contract"],
        schedule=datos["horario"],
        description=datos["description"].strip(),
        source="EmpleAR",
        source_url="#",
        published_at=date.today().isoformat(),
        featured=False,
        status="pending",
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


# ===================== MODERACIÓN (admin) =====================

ESTADOS_VALIDOS = {"pending", "approved", "rejected", "expired"}


@app.route("/api/admin/jobs")
@require_admin
def admin_list_jobs():
    """A diferencia de /api/jobs (público), esta ve TODOS los
    estados. ?status=pending para filtrar uno solo (por defecto)."""
    status = request.args.get("status", "pending")
    query = Job.query
    if status in ESTADOS_VALIDOS:
        query = query.filter(Job.status == status)

    jobs = query.order_by(Job.published_at.desc()).all()
    return jsonify([job.to_dict() for job in jobs])


@app.route("/api/admin/jobs/<int:job_id>", methods=["PATCH"])
@require_admin
def admin_update_job_status(job_id):
    job = db.session.get(Job, job_id)
    if job is None:
        return jsonify({"error": "Empleo no encontrado"}), 404

    datos = request.get_json(silent=True) or {}
    nuevo_status = datos.get("status")
    if nuevo_status not in ESTADOS_VALIDOS:
        return jsonify({"error": "Estado inválido", "validos": sorted(ESTADOS_VALIDOS)}), 400

    job.status = nuevo_status
    db.session.commit()
    return jsonify(job.to_dict())


if __name__ == "__main__":
    app.run(debug=True)
