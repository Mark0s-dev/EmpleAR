"""
Modelos de base de datos, con SQLAlchemy (a través de Flask-SQLAlchemy).
"""

import json

from flask_sqlalchemy import SQLAlchemy

# db es el objeto que va a "conectar" estos modelos con la app Flask.
# Se inicializa acá (sin la app todavía) y se conecta de verdad en
# app.py con db.init_app(app), para evitar imports circulares.
db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.String(30), nullable=False)

    def to_dict(self):
        # OJO: nunca devolvemos password_hash acá, ni por accidente.
        return {"id": self.id, "email": self.email, "isAdmin": self.is_admin}


class Session(db.Model):
    """Una fila = una sesión activa (un login). El token es lo que
    el frontend guarda y manda en cada pedido para probar quién es.
    user_id es nuestra primera FOREIGN KEY real: apunta al id de
    la tabla users — la relación que veníamos posponiendo desde
    el Módulo 6."""
    __tablename__ = "sessions"

    token = db.Column(db.String(64), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.String(30), nullable=False)

    # relationship() no crea una columna: es un atajo de Python para
    # navegar la relación. session.user te da el User completo sin
    # tener que hacer vos el JOIN a mano.
    user = db.relationship("User", backref="sessions")


class SavedSearch(db.Model):
    """Una búsqueda guardada por un usuario. Guardamos los criterios
    como JSON en una sola columna (Text) en vez de una columna por
    filtro — como los criterios ya son un dict en Python/JS, es más
    simple serializarlo entero que armar 9 columnas casi todas NULL."""
    __tablename__ = "saved_searches"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    label = db.Column(db.String(120), nullable=False)
    criteria_json = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.String(30), nullable=False)

    user = db.relationship("User", backref="saved_searches")

    def to_dict(self):
        return {
            "id": self.id,
            "label": self.label,
            "criteria": json.loads(self.criteria_json),
            "createdAt": self.created_at,
        }


class Job(db.Model):
    __tablename__ = "jobs"

    # Primary key: SQLAlchemy arma el "id INTEGER PRIMARY KEY" solo.
    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(120), nullable=False)
    company = db.Column(db.String(120), nullable=False)
    province = db.Column(db.String(80), nullable=False)
    city = db.Column(db.String(80), nullable=False)
    category = db.Column(db.String(80), nullable=False)
    modality = db.Column(db.String(20), nullable=False)
    contract = db.Column(db.String(30), nullable=False)
    schedule = db.Column(db.String(20), nullable=False)
    description = db.Column(db.Text, nullable=False)
    source = db.Column(db.String(80), nullable=False)
    source_url = db.Column(db.String(300), default="#")
    published_at = db.Column(db.String(10), nullable=False)  # "YYYY-MM-DD"
    featured = db.Column(db.Boolean, default=False)

    # pending | approved | rejected | expired (moderación real en el Módulo 9)
    status = db.Column(db.String(20), default="pending", nullable=False)

    # Huella digital para detectar duplicados entre corridas del scraper
    # (Módulo 11). None para las ofertas cargadas a mano por el formulario.
    external_hash = db.Column(db.String(64), unique=True, nullable=True)

    def to_dict(self):
        """Convierte la fila de la base de datos al mismo formato
        de diccionario que ya usaba el frontend (JS espera 'sourceUrl'
        y 'publishedAt' en camelCase, no 'source_url'/'published_at')."""
        return {
            "id": self.id,
            "title": self.title,
            "company": self.company,
            "province": self.province,
            "city": self.city,
            "category": self.category,
            "modality": self.modality,
            "contract": self.contract,
            "schedule": self.schedule,
            "description": self.description,
            "source": self.source,
            "sourceUrl": self.source_url,
            "publishedAt": self.published_at,
            "featured": self.featured,
            "status": self.status,
        }
