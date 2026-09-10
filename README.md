# EmpleAR

Plataforma web para buscar y publicar ofertas de empleo en toda Argentina, centralizando ofertas de distintas fuentes (Computrabajo, Bumeran, ZonaJobs, portales provinciales, etc.) en un solo lugar.

Proyecto de aprendizaje: se construye por módulos, documentando cada paso.

## Estado actual

- ✅ **Módulo 1 — Frontend visual**: estructura HTML semántica, estilo "Liquid Glass" (blanco predominante + vidrio esmerilado, inspirado en apple.com), datos mock, buscador con filtros funcionales sobre los datos de prueba, dropdown personalizado animado, formularios de publicar/contacto (simulados, sin backend).
- ✅ **Módulo 2 — Organización del frontend**: separación en páginas (`index.html`, `publicar.html`, `contacto.html`) y en componentes JS (`data.js`, `customSelect.js`, `filters.js`, `ui.js`).
- 🔜 **Módulo 3 — Python**: en curso (ejercicios en `python-intro/`, todavía no integrados al proyecto).
- ⬜ Módulo 4 en adelante: Flask, base de datos, scrapers, usuarios, notificaciones, producción.

## Estructura del proyecto

```
emplear/
├── frontend/
│   ├── index.html          → Home: hero, buscador, resultados, categorías, ubicaciones
│   ├── publicar.html        → Formulario para publicar una oferta
│   ├── contacto.html        → Formulario de publicidad / contacto
│   ├── css/
│   │   ├── variables.css    → Paleta de colores, tipografía, espaciado (design tokens)
│   │   ├── base.css         → Reset, fondo, accesibilidad básica
│   │   └── components.css   → Navbar, cards, formularios, dropdown, animaciones
│   └── js/
│       ├── data.js          → Datos mock (MOCK_JOBS, CATEGORIES, LOCATIONS, SOURCES)
│       ├── customSelect.js  → Componente de dropdown reutilizable (sin dependencias)
│       ├── filters.js       → Búsqueda/filtrado sobre los datos mock + envío de formularios
│       └── ui.js            → Renderizado de tarjetas, navbar con scroll, menú mobile
├── python-intro/            → Ejercicios sueltos de Python (Módulo 3, aún no integrados)
└── README.md
```

## Cómo correrlo

1. Abrir la carpeta `frontend/` en VS Code.
2. Clic derecho sobre `index.html` → **Open with Live Server**.

No requiere instalar nada (todavía): es HTML/CSS/JS plano, sin backend ni build step.

## Stack

Por ahora: HTML5, CSS3, JavaScript vanilla (sin frameworks ni librerías).
Más adelante: Python + Flask, SQLAlchemy, SQLite → PostgreSQL, APScheduler, Requests/BeautifulSoup.

## Notas

- Los datos de empleos son **ficticios** (`js/data.js`), solo para maquetar la interfaz.
- Los formularios de "Publicar empleo" y "Publicidad / Contacto" simulan el envío (`alert()`) porque todavía no hay backend — se conectan de verdad en el Módulo 8.
- El email de contacto de EmpleAR es `marcos20as04@gmail.com`.
