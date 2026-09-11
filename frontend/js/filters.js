/* ===========================================================
   FILTERS — buscar y filtrar sobre los datos mock.
   Depende de MOCK_JOBS, LOCATIONS, CATEGORIES, SOURCES
   (data.js) y de renderJobList/createJobCard (ui.js).
   =========================================================== */

/**
 * Llena un <select> con una lista de valores, agregando siempre
 * una opción vacía primero. La usamos para provincia, ciudad,
 * categoría y fuente en vez de escribir <option> a mano.
 */
function populateSelect(select, values, emptyLabel) {
  if (!select) return;
  const current = select.value;
  select.innerHTML = `<option value="">${emptyLabel}</option>` +
    values.map(v => `<option value="${v}">${v}</option>`).join("");
  // Si el valor anterior sigue siendo válido, lo mantenemos
  // (útil cuando repoblamos ciudad al cambiar de provincia).
  if (values.includes(current)) select.value = current;

  // Si este <select> ya fue reemplazado por el dropdown personalizado
  // (ui.js), le avisamos para que reconstruya su lista visual.
  if (typeof refreshCustomSelect === "function") refreshCustomSelect(select);
}

/** Todas las ciudades de LOCATIONS, sin repetir provincia por provincia */
function allCities() {
  return Object.values(LOCATIONS).flat();
}

/**
 * Conecta un <select> de provincia con uno de ciudad: al cambiar
 * la provincia, la ciudad se repuebla solo con las suyas.
 */
function setupLocationCascade(provinciaSelect, ciudadSelect, emptyLabel) {
  if (!provinciaSelect || !ciudadSelect) return;

  populateSelect(provinciaSelect, Object.keys(LOCATIONS), emptyLabel);
  populateSelect(ciudadSelect, allCities(), emptyLabel);

  provinciaSelect.addEventListener("change", () => {
    const provincia = provinciaSelect.value;
    const cities = provincia ? LOCATIONS[provincia] : allCities();
    populateSelect(ciudadSelect, cities, emptyLabel);
  });
}

/** Fecha más reciente entre los datos mock: la usamos como "hoy" del demo,
    para que el filtro de fecha tenga sentido sin depender de la fecha real. */
function getMockToday() {
  const timestamps = MOCK_JOBS.map(job => new Date(job.publishedAt).getTime());
  return new Date(Math.max(...timestamps));
}

function passesDateFilter(job, range, refDate) {
  if (!range) return true;
  const days = (refDate - new Date(job.publishedAt)) / (1000 * 60 * 60 * 24);
  if (range === "24h") return days <= 1;
  if (range === "7d") return days <= 7;
  if (range === "30d") return days <= 30;
  return true;
}

/**
 * Filtra MOCK_JOBS según los criterios del formulario de búsqueda.
 * Cada "matches" es independiente: si un filtro viene vacío, no excluye nada.
 */
function filterJobs(criteria) {
  const refDate = getMockToday();
  const keyword = criteria.keyword.trim().toLowerCase();

  return MOCK_JOBS.filter(job => {
    const matchesKeyword = !keyword ||
      job.title.toLowerCase().includes(keyword) ||
      job.company.toLowerCase().includes(keyword) ||
      job.description.toLowerCase().includes(keyword);

    return matchesKeyword &&
      (!criteria.provincia || job.province === criteria.provincia) &&
      (!criteria.ciudad || job.city === criteria.ciudad) &&
      (!criteria.categoria || job.category === criteria.categoria) &&
      (!criteria.modalidad || job.modality === criteria.modalidad) &&
      (!criteria.contrato || job.contract === criteria.contrato) &&
      (!criteria.horario || job.schedule === criteria.horario) &&
      (!criteria.fuente || job.source === criteria.fuente) &&
      passesDateFilter(job, criteria.fecha, refDate);
  });
}

/** Lee los valores actuales del formulario de búsqueda */
function readSearchCriteria(form) {
  const data = new FormData(form);
  return {
    keyword: data.get("keyword") || "",
    provincia: data.get("provincia") || "",
    ciudad: data.get("ciudad") || "",
    categoria: data.get("categoria") || "",
    modalidad: data.get("modalidad") || "",
    contrato: data.get("contrato") || "",
    horario: data.get("horario") || "",
    fuente: data.get("fuente") || "",
    fecha: data.get("fecha") || ""
  };
}

/**
 * Ejecuta la búsqueda: muestra un estado de "cargando" breve
 * (simulado, porque todavía no hay backend real), filtra, y
 * renderiza resultados o un mensaje de "sin resultados".
 */
function runSearch(form) {
  const status = document.getElementById("resultsStatus");
  const criteria = readSearchCriteria(form);

  if (status) status.textContent = "Buscando…";

  window.setTimeout(() => {
    const results = filterJobs(criteria);
    renderJobList("jobList", results);

    if (status) {
      status.textContent = results.length
        ? `${results.length} resultado${results.length === 1 ? "" : "s"} encontrado${results.length === 1 ? "" : "s"}.`
        : "No se encontraron ofertas con esos filtros. Probá ampliar la búsqueda.";
    }

    document.getElementById("resultados")?.scrollIntoView({ behavior: "smooth", block: "start" });
  }, 300);
}

/** Mock de envío para publicar/contacto: no hay backend todavía */
function initMockFormSubmit(formId, successMessage) {
  const form = document.getElementById(formId);
  if (!form) return;

  form.addEventListener("submit", (event) => {
    event.preventDefault();

    const button = form.querySelector("button[type='submit']");
    const originalText = button.textContent;
    button.disabled = true;
    button.textContent = "Enviando…";

    window.setTimeout(() => {
      button.disabled = false;
      button.textContent = originalText;
      alert(successMessage);
      form.reset();
    }, 500);
  });
}

/* ===================== INICIALIZACIÓN ===================== */
document.addEventListener("DOMContentLoaded", () => {
  // Poblar los <select> de ubicación en el buscador y en publicar
  setupLocationCascade(
    document.getElementById("provincia"),
    document.getElementById("ciudad"),
    "Todas"
  );
  setupLocationCascade(
    document.getElementById("publishProvincia"),
    document.getElementById("publishCiudad"),
    "Seleccionar..."
  );

  populateSelect(document.getElementById("categoria"), CATEGORIES, "Todas");
  populateSelect(document.getElementById("publishCategoria"), CATEGORIES, "Seleccionar...");
  populateSelect(document.getElementById("fuente"), SOURCES, "Todas");

  const searchForm = document.getElementById("searchForm");
  if (searchForm) {
    searchForm.addEventListener("submit", (event) => {
      event.preventDefault();
      runSearch(searchForm);
    });

    // "Cambiar filtros" también dispara una nueva búsqueda automáticamente
    searchForm.querySelectorAll("select").forEach(select => {
      select.addEventListener("change", () => runSearch(searchForm));
    });
  }

  initMockFormSubmit("publishForm", "✓ Oferta recibida (demo). Todavía no hay backend: en el Módulo 8 esto se va a guardar de verdad y quedará pendiente de moderación.");
  initMockFormSubmit("contactForm", "✓ Consulta enviada (demo). Te vamos a responder a marcos20as04@gmail.com apenas conectemos el envío de emails.");
});
