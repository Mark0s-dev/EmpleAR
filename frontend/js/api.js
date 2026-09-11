/* ===========================================================
   API — toda la comunicación con el backend Flask vive acá.
   Ningún otro archivo hace fetch() directamente: si el día de
   mañana cambia la URL del backend, o cómo se arman los
   pedidos, se toca UN solo lugar.
   =========================================================== */

const API_BASE = "http://127.0.0.1:5000";

/**
 * Wrapper sobre fetch(): arma la URL completa, manda JSON,
 * y convierte respuestas con error (400, 404, etc.) en una
 * excepción de JavaScript, para poder usar try/catch en vez
 * de revisar response.ok en cada función de arriba.
 */
async function apiFetch(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  const data = await response.json().catch(() => null);

  if (!response.ok) {
    throw new Error(data?.error || `Error ${response.status}`);
  }

  return data;
}

/** Convierte un objeto de criterios en "?clave=valor&..." salteando los vacíos */
function buildQuery(params) {
  const query = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value) query.set(key, value);
  });
  const qs = query.toString();
  return qs ? `?${qs}` : "";
}

async function apiGetJobs(criteria = {}) {
  return apiFetch(`/api/jobs${buildQuery(criteria)}`);
}

async function apiGetJob(id) {
  return apiFetch(`/api/jobs/${id}`);
}

async function apiCreateJob(payload) {
  return apiFetch("/api/jobs", { method: "POST", body: JSON.stringify(payload) });
}

async function apiGetProvinces() {
  return apiFetch("/api/provinces");
}

async function apiGetCities(provincia = "") {
  return apiFetch(`/api/cities${buildQuery({ provincia })}`);
}

async function apiGetCategories() {
  return apiFetch("/api/categories");
}

async function apiGetSources() {
  return apiFetch("/api/sources");
}

async function apiCreateContact(payload) {
  return apiFetch("/api/contact", { method: "POST", body: JSON.stringify(payload) });
}
