/* ===========================================================
   FILTERS — orquesta el buscador y los formularios.
   Ya no filtra nada acá: le pide todo al backend a través de
   api.js. Depende de customSelect.js (refreshCustomSelect) y
   de api.js (apiGetJobs, apiGetProvinces, etc).
   =========================================================== */

/**
 * Llena un <select> con una lista de valores, agregando siempre
 * una opción vacía primero.
 */
function populateSelect(select, values, emptyLabel) {
  if (!select) return;
  const current = select.value;
  select.innerHTML = `<option value="">${emptyLabel}</option>` +
    values.map(v => `<option value="${v}">${v}</option>`).join("");
  if (values.includes(current)) select.value = current;

  // Si este <select> ya fue reemplazado por el dropdown personalizado,
  // le avisamos para que reconstruya su lista visual con los datos nuevos.
  if (typeof refreshCustomSelect === "function") refreshCustomSelect(select);
}

/**
 * Pobla provincia con /api/provinces y ciudad con /api/cities,
 * y conecta el cambio de provincia para repoblar ciudad filtrada.
 */
async function setupLocationCascade(provinciaSelect, ciudadSelect, emptyLabel) {
  if (!provinciaSelect || !ciudadSelect) return;

  try {
    const [provincias, ciudades] = await Promise.all([
      apiGetProvinces(),
      apiGetCities(),
    ]);
    populateSelect(provinciaSelect, provincias, emptyLabel);
    populateSelect(ciudadSelect, ciudades, emptyLabel);
  } catch (err) {
    console.error("No se pudieron cargar provincia/ciudad:", err);
  }

  provinciaSelect.addEventListener("change", async () => {
    try {
      const cities = await apiGetCities(provinciaSelect.value);
      populateSelect(ciudadSelect, cities, emptyLabel);
    } catch (err) {
      console.error("No se pudieron cargar las ciudades:", err);
    }
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
    fecha: data.get("fecha") || "",
  };
}

/**
 * Ejecuta la búsqueda: muestra "Buscando…", le pide los
 * resultados a GET /api/jobs, y los renderiza. Si el backend
 * no responde (por ejemplo, no está corriendo), lo avisa en
 * vez de romper la página.
 */
async function runSearch(form) {
  const status = document.getElementById("resultsStatus");
  const criteria = readSearchCriteria(form);

  if (status) status.textContent = "Buscando…";

  try {
    const results = await apiGetJobs(criteria);
    renderJobList("jobList", results);

    if (status) {
      status.textContent = results.length
        ? `${results.length} resultado${results.length === 1 ? "" : "s"} encontrado${results.length === 1 ? "" : "s"}.`
        : "No se encontraron ofertas con esos filtros. Probá ampliar la búsqueda.";
    }
  } catch (err) {
    console.error(err);
    if (status) status.textContent = "No se pudo conectar con el servidor. ¿Está corriendo el backend (python3 app.py)?";
  }

  document.getElementById("resultados")?.scrollIntoView({ behavior: "smooth", block: "start" });
}

/**
 * Conecta un formulario a una función de la API real (apiCreateJob
 * o apiCreateContact). Ya no es una simulación: si el backend
 * responde 400, el usuario ve el error real.
 */
function initFormSubmit(formId, submitFn, successMessage) {
  const form = document.getElementById(formId);
  if (!form) return;

  form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const button = form.querySelector("button[type='submit']");
    const originalText = button.textContent;
    button.disabled = true;
    button.textContent = "Enviando…";

    try {
      const payload = Object.fromEntries(new FormData(form).entries());
      await submitFn(payload);
      alert(successMessage);
      form.reset();
    } catch (err) {
      // Si el backend mandó errores por campo (err.detalles), los
      // listamos; si no, mostramos el mensaje genérico.
      const detalle = err.detalles
        ? "\n" + Object.entries(err.detalles).map(([campo, motivo]) => `• ${campo}: ${motivo}`).join("\n")
        : "";
      alert(`No se pudo enviar: ${err.message}${detalle}`);
    } finally {
      button.disabled = false;
      button.textContent = originalText;
    }
  });
}

/**
 * Guarda la búsqueda actual del formulario (requiere sesión).
 * Solo permite guardar si hay al menos un filtro elegido — no
 * tiene sentido guardar "todo, sin filtrar nada".
 */
async function guardarBusquedaActual(form) {
  const session = getSession();
  if (!session) {
    if (confirm("Necesitás una cuenta para guardar búsquedas. ¿Ir a iniciar sesión?")) {
      window.location.href = "cuenta.html";
    }
    return;
  }

  const criterios = readSearchCriteria(form);
  if (!Object.values(criterios).some(Boolean)) {
    alert("Elegí al menos un filtro antes de guardar la búsqueda.");
    return;
  }

  const label = prompt("¿Cómo querés llamar a esta búsqueda?", "");
  if (!label) return;

  try {
    await apiCreateSavedSearch(session.token, label, criterios);
    alert("✓ Búsqueda guardada. La vas a encontrar en tu cuenta.");
  } catch (err) {
    alert(`No se pudo guardar: ${err.message}`);
  }
}

/**
 * Si la URL trae criterios (ej: index.html?provincia=Misiones,
 * como arma cuenta.html al reabrir una búsqueda guardada),
 * precarga el formulario con esos valores y busca automáticamente.
 */
function aplicarCriteriosDesdeURL(form) {
  const params = new URLSearchParams(window.location.search);
  if ([...params.keys()].length === 0) return;

  params.forEach((valor, clave) => {
    const campo = form.elements.namedItem(clave);
    if (campo) {
      campo.value = valor;
      if (typeof refreshCustomSelect === "function") refreshCustomSelect(campo);
    }
  });

  runSearch(form);
}

/* ===================== INICIALIZACIÓN ===================== */
document.addEventListener("DOMContentLoaded", async () => {
  await setupLocationCascade(
    document.getElementById("provincia"),
    document.getElementById("ciudad"),
    "Todas"
  );
  await setupLocationCascade(
    document.getElementById("publishProvincia"),
    document.getElementById("publishCiudad"),
    "Seleccionar..."
  );

  try {
    const categorias = await apiGetCategories();
    populateSelect(document.getElementById("categoria"), categorias, "Todas");
    populateSelect(document.getElementById("publishCategoria"), categorias, "Seleccionar...");
  } catch (err) {
    console.error("No se pudieron cargar las categorías:", err);
  }

  try {
    const fuentes = await apiGetSources();
    populateSelect(document.getElementById("fuente"), fuentes, "Todas");
  } catch (err) {
    console.error("No se pudieron cargar las fuentes:", err);
  }

  const searchForm = document.getElementById("searchForm");
  if (searchForm) {
    searchForm.addEventListener("submit", (event) => {
      event.preventDefault();
      runSearch(searchForm);
    });

    searchForm.querySelectorAll("select").forEach(select => {
      select.addEventListener("change", () => runSearch(searchForm));
    });

    aplicarCriteriosDesdeURL(searchForm);
  }

  const saveBtn = document.getElementById("saveSearchBtn");
  if (saveBtn) {
    saveBtn.addEventListener("click", () => guardarBusquedaActual(searchForm));
  }

  initFormSubmit(
    "publishForm",
    // El formulario usa nombres en español (así están los <label> y
    // name="" del HTML). El backend espera las claves del modelo Job
    // en inglés (así quedó armado desde data.js/data.py). Traducimos acá,
    // en el único lugar donde el frontend "habla" con la API.
    (payload) => apiCreateJob({
      title: payload.puesto,
      company: payload.empresa,
      province: payload.provincia,
      city: payload.ciudad,
      category: payload.categoria,
      modality: payload.modalidad,
      contract: payload.contrato,
      horario: payload.horario,
      description: payload.descripcion,
    }),
    "✓ Oferta recibida, queda pendiente de moderación. (Todavía no hay moderación real: eso llega en el Módulo 9.)"
  );
  initFormSubmit(
    "contactForm",
    apiCreateContact,
    "✓ Consulta enviada. Te vamos a responder a marcos20as04@gmail.com."
  );
});
