from datetime import date, datetime, timedelta, timezone
from functools import wraps
import json
import secrets

from flask import Flask, jsonify, request
from flask_cors import CORS
from sqlalchemy import func, or_
from werkzeug.security import check_password_hash, generate_password_hash

from data import CATEGORIES, HORARIOS_VALIDOS, CONTRATOS_VALIDOS, LOCATIONS, MODALIDADES_VALIDAS, SOURCES
from models import Job, SavedSearch, Session, User, db

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


def usuario_actual():
    """Lee el header 'Authorization: Bearer <token>', busca la sesión
    en la base y devuelve el User dueño, o None si no hay token
    válido. No es JWT (no vamos a firmar nada): el token es solo un
    identificador al azar guardado en la tabla sessions — más simple
    de entender, y suficiente para este proyecto."""
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None
    token = auth.removeprefix("Bearer ")
    sesion = db.session.get(Session, token)
    return sesion.user if sesion else None


def require_login(vista):
    """Corta la ejecución con 401 si no hay una sesión válida.
    Deja al usuario disponible en request.current_user."""
    @wraps(vista)
    def envoltorio(*args, **kwargs):
        usuario = usuario_actual()
        if usuario is None:
            return jsonify({"error": "No autenticado"}), 401
        request.current_user = usuario
        return vista(*args, **kwargs)
    return envoltorio


def require_admin(vista):
    """Como require_login, pero además exige is_admin=True."""
    @wraps(vista)
    def envoltorio(*args, **kwargs):
        usuario = usuario_actual()
        if usuario is None:
            return jsonify({"error": "No autenticado"}), 401
        if not usuario.is_admin:
            return jsonify({"error": "No autorizado"}), 403
        request.current_user = usuario
        return vista(*args, **kwargs)
    return envoltorio


@app.route("/")
def home():
    return "EmpleAR backend funcionando 🚀"


# ===================== AUTENTICACIÓN =====================

@app.route("/api/auth/register", methods=["POST"])
def register():
    datos = request.get_json(silent=True) or {}
    email = (datos.get("email") or "").strip().lower()
    password = datos.get("password") or ""

    if "@" not in email or "." not in email:
        return jsonify({"error": "Email inválido"}), 400
    if len(password) < 6:
        return jsonify({"error": "La contraseña debe tener al menos 6 caracteres"}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Ya existe una cuenta con ese email"}), 400

    usuario = User(
        email=email,
        # generate_password_hash NUNCA guarda la contraseña en texto
        # plano — guarda un hash: si alguien roba la base de datos,
        # no puede leer las contraseñas originales.
        password_hash=generate_password_hash(password),
        is_admin=False,
        created_at=datetime.now(timezone.utc).isoformat(),
    )
    db.session.add(usuario)
    db.session.commit()

    return jsonify(usuario.to_dict()), 201


@app.route("/api/auth/login", methods=["POST"])
def login():
    datos = request.get_json(silent=True) or {}
    email = (datos.get("email") or "").strip().lower()
    password = datos.get("password") or ""

    usuario = User.query.filter_by(email=email).first()
    # check_password_hash compara el hash, nunca la contraseña en
    # texto plano. El mensaje de error es el MISMO si el email no
    # existe o si la contraseña está mal — así no le confirmamos a
    # un atacante "che, este email sí existe" probando al azar.
    if usuario is None or not check_password_hash(usuario.password_hash, password):
        return jsonify({"error": "Email o contraseña incorrectos"}), 401

    token = secrets.token_hex(32)
    sesion = Session(token=token, user_id=usuario.id, created_at=datetime.now(timezone.utc).isoformat())
    db.session.add(sesion)
    db.session.commit()

    return jsonify({"token": token, "user": usuario.to_dict()})


@app.route("/api/auth/logout", methods=["POST"])
@require_login
def logout():
    auth = request.headers.get("Authorization", "")
    token = auth.removeprefix("Bearer ")
    sesion = db.session.get(Session, token)
    if sesion:
        db.session.delete(sesion)
        db.session.commit()
    return jsonify({"mensaje": "Sesión cerrada"})


@app.route("/api/auth/me")
@require_login
def me():
    return jsonify(request.current_user.to_dict())



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


# ===================== BÚSQUEDAS GUARDADAS =====================

@app.route("/api/saved-searches", methods=["GET"])
@require_login
def list_saved_searches():
    searches = SavedSearch.query.filter_by(user_id=request.current_user.id) \
        .order_by(SavedSearch.created_at.desc()).all()
    return jsonify([s.to_dict() for s in searches])


@app.route("/api/saved-searches", methods=["POST"])
@require_login
def create_saved_search():
    datos = request.get_json(silent=True) or {}
    criterios = datos.get("criteria") or {}
    label = (datos.get("label") or "").strip()

    if not label:
        return jsonify({"error": "La búsqueda necesita un nombre"}), 400
    if not any(criterios.values()):
        return jsonify({"error": "Elegí al menos un filtro antes de guardar la búsqueda"}), 400

    nueva = SavedSearch(
        user_id=request.current_user.id,
        label=label,
        criteria_json=json.dumps(criterios),
        created_at=datetime.now(timezone.utc).isoformat(),
    )
    db.session.add(nueva)
    db.session.commit()
    return jsonify(nueva.to_dict()), 201


@app.route("/api/saved-searches/<int:search_id>", methods=["DELETE"])
@require_login
def delete_saved_search(search_id):
    busqueda = db.session.get(SavedSearch, search_id)
    if busqueda is None or busqueda.user_id != request.current_user.id:
        # 404 en vez de 403: no le confirmamos a otro usuario que
        # ese id "existe pero no es tuyo" — simplemente no existe para él.
        return jsonify({"error": "Búsqueda no encontrada"}), 404

    db.session.delete(busqueda)
    db.session.commit()
    return jsonify({"mensaje": "Búsqueda eliminada"})


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
