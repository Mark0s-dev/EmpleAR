"""
Paquete de scrapers. Cada archivo fuente_X.py expone una función
obtener_empleos() que devuelve una lista de diccionarios, TODOS con
las mismas claves (el "formato normalizado" del que habla el
Módulo 10) — así el resto del sistema no necesita saber de qué
sitio vino cada oferta para poder procesarla.

SCRAPERS junta todas las fuentes en un solo lugar, para que
run_scrapers.py (o más adelante, APScheduler en el Módulo 12) las
recorra sin tener que importarlas una por una a mano.
"""

from . import fuente_demo

SCRAPERS = [
    fuente_demo,
]
