"""
Modelos de base de datos, con SQLAlchemy (a través de Flask-SQLAlchemy).
Por ahora solo Job — el resto de las tablas (User, Company,
SavedSearch, etc.) se van a ir agregando en módulos siguientes.
"""

from flask_sqlalchemy import SQLAlchemy

# db es el objeto que va a "conectar" estos modelos con la app Flask.
# Se inicializa acá (sin la app todavía) y se conecta de verdad en
# app.py con db.init_app(app), para evitar imports circulares.
db = SQLAlchemy()


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
