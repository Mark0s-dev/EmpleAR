# Variables: no se declara el tipo, Python lo infiere solo.
puesto = "Recepcionista"        # str (texto)
salario = 450000                # int (entero)
es_remoto = False                # bool (verdadero/falso)
calificacion = 4.5               # float (decimal)

# f-strings: la forma moderna de insertar variables en un texto
print(f"{puesto} - Remoto: {es_remoto}")

# type() te dice el tipo de cualquier variable
print(type(salario))   # <class 'int'>
