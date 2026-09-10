# Importar un módulo propio (helpers.py, en la misma carpeta)
from helpers import normalizar_texto

# Importar un módulo de la librería estándar de Python
from datetime import date

print(normalizar_texto("  Recepcionista  "))   # recepcionista
print(date.today())                             # fecha de hoy

# Excepciones: try/except evita que el programa se rompa
# ante un error esperable (ej: un dato mal formado).
def dias_desde_publicacion(fecha_texto):
    try:
        fecha = date.fromisoformat(fecha_texto)
        return (date.today() - fecha).days
    except ValueError:
        print(f"Fecha inválida: {fecha_texto}")
        return None

print(dias_desde_publicacion("2026-09-08"))  # un número
print(dias_desde_publicacion("08-09-2026"))  # None + mensaje (formato incorrecto)
