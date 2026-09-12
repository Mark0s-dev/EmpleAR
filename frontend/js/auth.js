/* ===========================================================
   AUTH — sesión del usuario visitante (no confundir con el login
   de admin en moderar.html, que es independiente). Se guarda en
   localStorage para que sobreviva a recargar la página o cerrar
   la pestaña — esto es un sitio real fuera de la conversación,
   no un artifact, así que localStorage funciona normalmente.
   =========================================================== */

const AUTH_KEY = "emplear_session";

function getSession() {
  try {
    return JSON.parse(localStorage.getItem(AUTH_KEY) || "null");
  } catch {
    return null;
  }
}

function setSession(session) {
  localStorage.setItem(AUTH_KEY, JSON.stringify(session));
}

function clearSession() {
  localStorage.removeItem(AUTH_KEY);
}

/** Actualiza el navbar según haya o no una sesión activa.
    Necesita un <li id="navAuth"> en el HTML para saber dónde
    dibujar el link — si no existe, no hace nada (página sin navbar). */
function initAuthNav() {
  const slot = document.getElementById("navAuth");
  if (!slot) return;

  const session = getSession();
  if (session) {
    slot.innerHTML = `<a href="cuenta.html">${session.user.email}</a>`;
  } else {
    slot.innerHTML = `<a href="cuenta.html">Ingresar</a>`;
  }
}
