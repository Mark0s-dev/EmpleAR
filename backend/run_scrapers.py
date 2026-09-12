"""
Corre todos los scrapers de scrapers/SCRAPERS, detecta duplicados
y guarda en la base de datos los que sean nuevos.

    python3 run_scrapers.py

Se puede correr las veces que quieras: las ofertas que ya estén
cargadas (mismo hash) no se van a duplicar.
"""

import hashlib

from app import app
from models import Job, db
from scrapers import SCRAPERS


def calcular_hash(empleo):
    """Combina los campos que identifican a una oferta como 'la
    misma' (sin importar mayúsculas ni espacios de más) y calcula
    un hash. Si dos ofertas generan el mismo hash, son la misma
    oferta publicada más de una vez."""
    clave = "|".join([
        empleo["title"].strip().lower(),
        empleo["company"].strip().lower(),
        empleo["city"].strip().lower(),
        empleo["province"].strip().lower(),
    ])
    return hashlib.sha256(clave.encode("utf-8")).hexdigest()


def run():
    with app.app_context():
        nuevos = 0
        duplicados = 0

        for modulo in SCRAPERS:
            empleos = modulo.obtener_empleos()
            print(f"{modulo.NOMBRE_FUENTE}: {len(empleos)} ofertas encontradas en la fuente")

            vistos_en_esta_corrida = set()

            for datos in empleos:
                hash_externo = calcular_hash(datos)

                # Duplicado DENTRO de esta misma corrida (la fuente
                # publicó la misma oferta dos veces en la página).
                if hash_externo in vistos_en_esta_corrida:
                    duplicados += 1
                    continue
                vistos_en_esta_corrida.add(hash_externo)

                # Duplicado respecto a lo que YA está guardado
                # (de una corrida anterior de este mismo scraper).
                ya_existe = Job.query.filter_by(external_hash=hash_externo).first()
                if ya_existe:
                    duplicados += 1
                    continue

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
                    featured=False,
                    # Las de fuentes externas se consideran confiables y
                    # entran directo (a diferencia de las publicadas a
                    # mano por el formulario, que sí pasan por moderación).
                    status="approved",
                    external_hash=hash_externo,
                )
                db.session.add(job)
                nuevos += 1

        db.session.commit()
        print(f"Listo: {nuevos} ofertas nuevas, {duplicados} duplicados detectados y salteados.")


if __name__ == "__main__":
    run()
