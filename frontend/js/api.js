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
    ...options,
    // Merge real de headers: si options trae sus propios headers
    // (como X-Admin-Token), se suman al Content-Type por defecto
    // en vez de reemplazarlo (un ...options simple lo pisaría entero).
    headers: { "Content-Type": "application/json", ...options.headers },
  });

  const data = await response.json().catch(() => null);

  if (!response.ok) {
    const error = new Error(data?.error || `Error ${response.status}`);
    error.detalles = data?.detalles;
    throw error;
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

/* ===================== AUTENTICACIÓN ===================== */

async function apiRegister(email, password) {
  return apiFetch("/api/auth/register", { method: "POST", body: JSON.stringify({ email, password }) });
}

async function apiLogin(email, password) {
  return apiFetch("/api/auth/login", { method: "POST", body: JSON.stringify({ email, password }) });
}

async function apiLogout(token) {
  return apiFetch("/api/auth/logout", { method: "POST", headers: { Authorization: `Bearer ${token}` } });
}

async function apiMe(token) {
  return apiFetch("/api/auth/me", { headers: { Authorization: `Bearer ${token}` } });
}

/* ===================== ADMIN / MODERACIÓN ===================== */
/* Ahora sí requieren haber iniciado sesión como admin de verdad
   (Módulo 13) — antes usaban un token fijo compartido. */

async function apiGetAdminJobs(token, status = "pending") {
  return apiFetch(`/api/admin/jobs${buildQuery({ status })}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
}

async function apiModerateJob(token, jobId, status) {
  return apiFetch(`/api/admin/jobs/${jobId}`, {
    method: "PATCH",
    headers: { Authorization: `Bearer ${token}` },
    body: JSON.stringify({ status }),
  });
}

/* ===================== BÚSQUEDAS GUARDADAS ===================== */

async function apiGetSavedSearches(token) {
  return apiFetch("/api/saved-searches", { headers: { Authorization: `Bearer ${token}` } });
}

async function apiCreateSavedSearch(token, label, criteria) {
  return apiFetch("/api/saved-searches", {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
    body: JSON.stringify({ label, criteria }),
  });
}

async function apiDeleteSavedSearch(token, id) {
  return apiFetch(`/api/saved-searches/${id}`, {
    method: "DELETE",
    headers: { Authorization: `Bearer ${token}` },
  });
}
