# Este archivo es un "módulo": cualquier .py se puede importar desde otro.
# Así vamos a organizar EmpleAR más adelante: un archivo por responsabilidad.

def normalizar_texto(texto):
    return texto.strip().lower()
