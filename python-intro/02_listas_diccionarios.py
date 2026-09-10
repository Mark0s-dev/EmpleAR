# Lista: colección ordenada, se accede por posición (empieza en 0)
provincias = ["Misiones", "Córdoba", "Buenos Aires", "Santa Fe"]
print(provincias[0])          # Misiones
print(len(provincias))        # 4 (cantidad de elementos)

# Diccionario: pares clave-valor (así vamos a representar un Job en Python)
job = {
    "titulo": "Recepcionista",
    "empresa": "Hotel Cataratas",
    "provincia": "Misiones",
    "modalidad": "presencial"
}
print(job["titulo"])          # Recepcionista
print(job.get("horario"))     # None (no existe esa clave, no rompe)

# Lista de diccionarios: así vamos a guardar TODOS los empleos
mock_jobs = [
    {"titulo": "Recepcionista", "provincia": "Misiones"},
    {"titulo": "Camarero/a", "provincia": "Misiones"},
    {"titulo": "Desarrollador/a", "provincia": "Buenos Aires"},
]

# List comprehension: filtrar en una sola línea (el equivalente
# Python del .filter() de JavaScript que ya usamos en filters.js)
misiones = [j["titulo"] for j in mock_jobs if j["provincia"] == "Misiones"]
print(misiones)   # ['Recepcionista', 'Camarero/a']
