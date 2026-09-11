"""
Datos mock de EmpleAR, en Python.
Es el mismo contenido que js/data.js, pero ahora vive acá porque
el backend va a ser la fuente real de los datos (el frontend deja
de tener su propia copia una vez que conectemos fetch() en la
parte 2 de este módulo).
"""

CATEGORIES = [
    "Administración", "Gastronomía", "Hotelería", "Ventas",
    "Logística", "Tecnología", "Atención al cliente",
    "Construcción", "Salud", "Educación"
]

SOURCES = [
    "Computrabajo", "Bumeran", "ZonaJobs", "Indeed", "LinkedIn",
    "Portal Empleo Argentina", "Portal Trabajo Misiones",
    "Jobrapido", "Empleos Clarín"
]

LOCATIONS = {
    "Misiones": ["Puerto Iguazú", "Posadas", "Eldorado", "Oberá"],
    "Córdoba": ["Córdoba", "Villa Carlos Paz", "Río Cuarto"],
    "Buenos Aires": ["CABA", "La Plata", "Mar del Plata"],
    "Santa Fe": ["Rosario", "Santa Fe"],
}

MOCK_JOBS = [
    {
        "id": "job-001", "title": "Recepcionista", "company": "Hotel Cataratas",
        "province": "Misiones", "city": "Puerto Iguazú", "category": "Hotelería",
        "modality": "presencial", "contract": "tiempo-completo", "schedule": "manana",
        "description": "Atención al huésped, check-in/check-out y manejo de reservas.",
        "source": "Portal Trabajo Misiones", "sourceUrl": "#", "publishedAt": "2026-09-08", "featured": True,
    },
    {
        "id": "job-002", "title": "Camarero/a", "company": "Restaurante El Litoral",
        "province": "Misiones", "city": "Puerto Iguazú", "category": "Gastronomía",
        "modality": "presencial", "contract": "tiempo-completo", "schedule": "rotativo",
        "description": "Atención de mesas en restaurante turístico, turno rotativo.",
        "source": "Computrabajo", "sourceUrl": "#", "publishedAt": "2026-09-07", "featured": True,
    },
    {
        "id": "job-003", "title": "Administrativo/a", "company": "Grupo Sur SA",
        "province": "Córdoba", "city": "Córdoba", "category": "Administración",
        "modality": "hibrido", "contract": "tiempo-completo", "schedule": "manana",
        "description": "Gestión de facturación, atención a proveedores y archivo.",
        "source": "Bumeran", "sourceUrl": "#", "publishedAt": "2026-09-06", "featured": True,
    },
    {
        "id": "job-004", "title": "Desarrollador/a Frontend", "company": "NovaTech",
        "province": "Buenos Aires", "city": "CABA", "category": "Tecnología",
        "modality": "remoto", "contract": "tiempo-completo", "schedule": "manana",
        "description": "React y JavaScript. Equipo distribuido, trabajo 100% remoto.",
        "source": "LinkedIn", "sourceUrl": "#", "publishedAt": "2026-09-08", "featured": True,
    },
    {
        "id": "job-005", "title": "Vendedor/a de salón", "company": "Tienda Andina",
        "province": "Misiones", "city": "Posadas", "category": "Ventas",
        "modality": "presencial", "contract": "medio-tiempo", "schedule": "tarde",
        "description": "Atención al cliente y venta en local de indumentaria.",
        "source": "ZonaJobs", "sourceUrl": "#", "publishedAt": "2026-09-05", "featured": False,
    },
    {
        "id": "job-006", "title": "Chofer de reparto", "company": "Distribuidora Iguazú",
        "province": "Misiones", "city": "Puerto Iguazú", "category": "Logística",
        "modality": "presencial", "contract": "tiempo-completo", "schedule": "manana",
        "description": "Reparto de mercadería en zona urbana. Carnet B1 excluyente.",
        "source": "Portal Empleo Argentina", "sourceUrl": "#", "publishedAt": "2026-09-04", "featured": False,
    },
    {
        "id": "job-007", "title": "Enfermero/a", "company": "Clínica del Parque",
        "province": "Córdoba", "city": "Villa Carlos Paz", "category": "Salud",
        "modality": "presencial", "contract": "tiempo-completo", "schedule": "manana",
        "description": "Turno mañana. Cuidado de pacientes internados.",
        "source": "Indeed", "sourceUrl": "#", "publishedAt": "2026-09-03", "featured": False,
    },
    {
        "id": "job-008", "title": "Auxiliar de obra", "company": "Construcciones Paraná",
        "province": "Misiones", "city": "Eldorado", "category": "Construcción",
        "modality": "presencial", "contract": "temporal", "schedule": "manana",
        "description": "Ayudante para obra en construcción residencial.",
        "source": "Jobrapido", "sourceUrl": "#", "publishedAt": "2026-09-02", "featured": False,
    },
    {
        "id": "job-009", "title": "Docente de nivel inicial", "company": "Instituto San Martín",
        "province": "Buenos Aires", "city": "La Plata", "category": "Educación",
        "modality": "presencial", "contract": "tiempo-completo", "schedule": "tarde",
        "description": "Sala de 4 años, turno tarde. Título docente excluyente.",
        "source": "Empleos Clarín", "sourceUrl": "#", "publishedAt": "2026-09-01", "featured": False,
    },
    {
        "id": "job-010", "title": "Representante de atención al cliente", "company": "SoporteYa",
        "province": "Santa Fe", "city": "Rosario", "category": "Atención al cliente",
        "modality": "remoto", "contract": "tiempo-completo", "schedule": "rotativo",
        "description": "Atención por chat y teléfono. Se requiere conexión estable a internet.",
        "source": "Bumeran", "sourceUrl": "#", "publishedAt": "2026-08-30", "featured": False,
    },
]
