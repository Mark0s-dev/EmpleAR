"""
Seed: carga los datos mock (data.py) dentro de la base de datos SQLite.
Se corre UNA VEZ (o cada vez que quieras resetear los datos de prueba):

    python3 seed.py
"""

from datetime import datetime, timezone

from werkzeug.security import generate_password_hash

from app import app
from data import MOCK_JOBS
from models import Job, User, db

with app.app_context():
    db.create_all()  # crea las tablas si no existen (no borra si ya existen)

    if User.query.filter_by(email="admin@emplear.com").first() is None:
        admin = User(
            email="admin@emplear.com",
            password_hash=generate_password_hash("admin1234"),
            is_admin=True,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        db.session.add(admin)
        db.session.commit()
        print("Usuario admin creado: admin@emplear.com / admin1234 (cambiala en producción)")
    else:
        print("El usuario admin ya existía, no se tocó.")

    if Job.query.count() > 0:
        print(f"Ya hay {Job.query.count()} empleos en la base. No se cargó nada de nuevo.")
        print("Si querés resetear, borrá el archivo emplear.db y volvé a correr este script.")
    else:
        for datos in MOCK_JOBS:
            job = Job(
                title=datos["title"],
                company=datos["company"],
                province=datos["province"],
                city=datos["city"],
                category=datos["category"],
                modality=datos["modality"],
                contract=datos["contract"],
                schedule=datos["schedule"],
                description=datos["description"],
                source=datos["source"],
                source_url=datos["sourceUrl"],
                published_at=datos["publishedAt"],
                featured=datos["featured"],
                status="approved",  # los mock ya son ofertas "en vivo"
            )
            db.session.add(job)

        db.session.commit()
        print(f"Se cargaron {len(MOCK_JOBS)} empleos en la base de datos (emplear.db).")
