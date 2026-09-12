"""
Scraper de ejemplo. En vez de bajar una página real de internet,
lee un archivo HTML local (fixtures/fuente_demo_sample.html) —
así podemos probar todo el flujo (parseo, normalización, detección
de duplicados) sin depender de un sitio externo real todavía.

Cuando conectemos una fuente de verdad, el patrón es el mismo:
conseguir el HTML con requests.get(url).text en vez de leer un
archivo, y parsearlo con BeautifulSoup exactamente igual que acá.
"""

from pathlib import Path

from bs4 import BeautifulSoup

NOMBRE_FUENTE = "Portal Demo Empleos"
FIXTURE = Path(__file__).parent / "fixtures" / "fuente_demo_sample.html"

# La fuente escribe "Tiempo Completo", "Turno Tarde", etc. — acá los
# traducimos a los mismos valores que ya usa el resto de EmpleAR
# (data.py), para que quede todo NORMALIZADO en un solo vocabulario.
CONTRATOS = {
    "tiempo completo": "tiempo-completo",
    "medio tiempo": "medio-tiempo",
    "temporal": "temporal",
    "freelance": "freelance",
}
HORARIOS = {
    "turno mañana": "manana",
    "turno tarde": "tarde",
    "turno noche": "noche",
    "rotativo": "rotativo",
}


def _texto(elemento):
    """.get_text(strip=True) sca los espacios/saltos de línea de
    más que suele traer el HTML de verdad (a propósito, el fixture
    tiene varios ejemplos de esto)."""
    return elemento.get_text(strip=True) if elemento else ""


def obtener_empleos():
    """Devuelve una lista de dicts, TODOS con las mismas claves que
    espera Job (models.py) — el "formato normalizado" del Módulo 10.
    Cualquier otra fuente que agreguemos después tiene que devolver
    exactamente esta misma forma."""
    html = FIXTURE.read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")

    empleos = []
    for card in soup.select(".job-card"):
        contrato_texto = _texto(card.select_one(".job-contract")).lower()
        horario_texto = _texto(card.select_one(".job-schedule")).lower()
        link = card.select_one("a")

        empleos.append({
            "title": _texto(card.select_one(".job-title")),
            "company": _texto(card.select_one(".job-company")),
            "province": _texto(card.select_one(".job-province")),
            "city": _texto(card.select_one(".job-city")),
            "category": _texto(card.select_one(".job-category")),
            "modality": card.get("data-modality", "presencial"),
            "contract": CONTRATOS.get(contrato_texto, "tiempo-completo"),
            "schedule": HORARIOS.get(horario_texto, "manana"),
            "description": _texto(card.select_one(".job-description")),
            "source": NOMBRE_FUENTE,
            "sourceUrl": link["href"] if link else "#",
            "publishedAt": card.get("data-published", ""),
            "featured": False,
        })

    return empleos
