/* ===========================================================
   DATOS MOCK — EmpleAR
   -----------------------------------------------------------
   Estos datos son FICTICIOS, solo para poder construir y
   probar la interfaz antes de tener un backend real.

   La forma de cada objeto (Job) ya está pensada para el
   futuro: cuando conectemos la API en el Módulo 5, la función
   que llame al backend va a devolver objetos con esta MISMA
   forma, así no hay que tocar el resto del código.
   =========================================================== */

const CATEGORIES = [
  "Administración", "Gastronomía", "Hotelería", "Ventas",
  "Logística", "Tecnología", "Atención al cliente",
  "Construcción", "Salud", "Educación"
];

/**
 * @typedef {Object} Job
 * @property {string} id
 * @property {string} title        - Puesto
 * @property {string} company      - Empresa
 * @property {string} province
 * @property {string} city
 * @property {string} category
 * @property {string} modality     - "presencial" | "remoto" | "hibrido"
 * @property {string} contract     - "tiempo-completo" | "medio-tiempo" | "temporal" | "freelance"
 * @property {string} description
 * @property {string} source       - Sitio de origen (Computrabajo, Bumeran, etc.)
 * @property {string} sourceUrl    - Placeholder por ahora, será la URL real de la oferta
 * @property {string} publishedAt  - Fecha ISO (YYYY-MM-DD)
 * @property {boolean} featured    - Si aparece en "Ofertas destacadas"
 */

/** @type {Job[]} */
const MOCK_JOBS = [
  {
    id: "job-001",
    title: "Recepcionista",
    company: "Hotel Cataratas",
    province: "Misiones",
    city: "Puerto Iguazú",
    category: "Hotelería",
    modality: "presencial",
    contract: "tiempo-completo",
    description: "Atención al huésped, check-in/check-out y manejo de reservas.",
    source: "Portal Trabajo Misiones",
    sourceUrl: "#",
    publishedAt: "2026-09-08",
    featured: true
  },
  {
    id: "job-002",
    title: "Camarero/a",
    company: "Restaurante El Litoral",
    province: "Misiones",
    city: "Puerto Iguazú",
    category: "Gastronomía",
    modality: "presencial",
    contract: "tiempo-completo",
    description: "Atención de mesas en restaurante turístico, turno rotativo.",
    source: "Computrabajo",
    sourceUrl: "#",
    publishedAt: "2026-09-07",
    featured: true
  },
  {
    id: "job-003",
    title: "Administrativo/a",
    company: "Grupo Sur SA",
    province: "Córdoba",
    city: "Córdoba",
    category: "Administración",
    modality: "hibrido",
    contract: "tiempo-completo",
    description: "Gestión de facturación, atención a proveedores y archivo.",
    source: "Bumeran",
    sourceUrl: "#",
    publishedAt: "2026-09-06",
    featured: true
  },
  {
    id: "job-004",
    title: "Desarrollador/a Frontend",
    company: "NovaTech",
    province: "Buenos Aires",
    city: "CABA",
    category: "Tecnología",
    modality: "remoto",
    contract: "tiempo-completo",
    description: "React y JavaScript. Equipo distribuido, trabajo 100% remoto.",
    source: "LinkedIn",
    sourceUrl: "#",
    publishedAt: "2026-09-08",
    featured: true
  },
  {
    id: "job-005",
    title: "Vendedor/a de salón",
    company: "Tienda Andina",
    province: "Misiones",
    city: "Posadas",
    category: "Ventas",
    modality: "presencial",
    contract: "medio-tiempo",
    description: "Atención al cliente y venta en local de indumentaria.",
    source: "ZonaJobs",
    sourceUrl: "#",
    publishedAt: "2026-09-05",
    featured: false
  },
  {
    id: "job-006",
    title: "Chofer de reparto",
    company: "Distribuidora Iguazú",
    province: "Misiones",
    city: "Puerto Iguazú",
    category: "Logística",
    modality: "presencial",
    contract: "tiempo-completo",
    description: "Reparto de mercadería en zona urbana. Carnet B1 excluyente.",
    source: "Portal Empleo Argentina",
    sourceUrl: "#",
    publishedAt: "2026-09-04",
    featured: false
  },
  {
    id: "job-007",
    title: "Enfermero/a",
    company: "Clínica del Parque",
    province: "Córdoba",
    city: "Villa Carlos Paz",
    category: "Salud",
    modality: "presencial",
    contract: "tiempo-completo",
    description: "Turno mañana. Cuidado de pacientes internados.",
    source: "Indeed",
    sourceUrl: "#",
    publishedAt: "2026-09-03",
    featured: false
  },
  {
    id: "job-008",
    title: "Auxiliar de obra",
    company: "Construcciones Paraná",
    province: "Misiones",
    city: "Eldorado",
    category: "Construcción",
    modality: "presencial",
    contract: "temporal",
    description: "Ayudante para obra en construcción residencial.",
    source: "Jobrapido",
    sourceUrl: "#",
    publishedAt: "2026-09-02",
    featured: false
  },
  {
    id: "job-009",
    title: "Docente de nivel inicial",
    company: "Instituto San Martín",
    province: "Buenos Aires",
    city: "La Plata",
    category: "Educación",
    modality: "presencial",
    contract: "tiempo-completo",
    description: "Sala de 4 años, turno tarde. Título docente excluyente.",
    source: "Empleos Clarín",
    sourceUrl: "#",
    publishedAt: "2026-09-01",
    featured: false
  },
  {
    id: "job-010",
    title: "Representante de atención al cliente",
    company: "SoporteYa",
    province: "Santa Fe",
    city: "Rosario",
    category: "Atención al cliente",
    modality: "remoto",
    contract: "tiempo-completo",
    description: "Atención por chat y teléfono. Se requiere conexión estable a internet.",
    source: "Bumeran",
    sourceUrl: "#",
    publishedAt: "2026-08-30",
    featured: false
  }
];
