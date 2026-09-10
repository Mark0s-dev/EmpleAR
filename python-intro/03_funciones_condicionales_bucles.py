# Función: como en JS, pero sin llaves — la indentación (4 espacios) define el bloque
def formatear_puesto(titulo, mayusculas=False):
    """Docstring: describe qué hace la función."""
    if mayusculas:
        return titulo.upper()
    return titulo.strip().capitalize()

print(formatear_puesto("  recepcionista "))          # Recepcionista
print(formatear_puesto("mozo", mayusculas=True))      # MOZO

# Condicionales: if / elif / else (sin paréntesis obligatorios, dos puntos en vez de {})
def clasificar_salario(monto):
    if monto < 300000:
        return "bajo"
    elif monto < 700000:
        return "medio"
    else:
        return "alto"

print(clasificar_salario(450000))   # medio

# Bucle for: recorre listas directamente (no hace falta un índice)
provincias = ["Misiones", "Córdoba", "Buenos Aires"]
for p in provincias:
    print(f"Provincia: {p}")

# enumerate() da índice + valor a la vez, cuando lo necesitás
for i, p in enumerate(provincias):
    print(i, p)

# Bucle while: se repite mientras la condición sea verdadera
intentos = 0
while intentos < 3:
    print(f"Intento {intentos + 1}")
    intentos += 1   # Python no tiene ++, se usa +=
