/* ===========================================================
   UI — renderizado de tarjetas, secciones dinámicas,
   navbar con scroll, animaciones de aparición y menú mobile.
   Depende de MOCK_JOBS y CATEGORIES definidos en data.js
   (por eso data.js se carga antes que ui.js en el HTML).
   =========================================================== */

/**
 * Mapa de fuente → color de badge.
 * Si una fuente no está en el mapa, se usa un color genérico.
 * Esto evita "if/else" gigantes y hace fácil sumar fuentes nuevas.
 */
const SOURCE_COLORS = {
  "Computrabajo": "#3B82C4",
  "Bumeran": "#5E9C6C",
  "ZonaJobs": "#B15FC9",
  "Indeed": "#2E7DD1",
  "LinkedIn": "#3B7CB8",
  "Portal Empleo Argentina": "#5FB4E5",
  "Portal Trabajo Misiones": "#5FB4E5",
  "Jobrapido": "#C97A4A",
  "Empleos Clarín": "#C9435A"
};

/** Convierte "tiempo-completo" en "Tiempo completo" para mostrar */
function formatLabel(value) {
  return value
    .split("-")
    .map(w => w.charAt(0).toUpperCase() + w.slice(1))
    .join(" ");
}

/**
 * Crea el elemento DOM de una tarjeta de empleo a partir de un Job.
 * @param {Job} job
 * @returns {HTMLElement}
 */
function createJobCard(job) {
  const card = document.createElement("article");
  card.className = "job-card";

  const color = SOURCE_COLORS[job.source] || "#8A9BAE";

  card.innerHTML = `
    <h3>${job.title}</h3>
    <p class="empresa">${job.company}</p>
    <p class="ubicacion">${job.city}, ${job.province}</p>
    <div class="tags">
      <span class="tag">${formatLabel(job.modality)}</span>
      <span class="tag">${formatLabel(job.contract)}</span>
    </div>
    <p class="descripcion">${job.description}</p>
    <div class="card-footer">
      <span class="source-badge" style="--badge-color: ${color}">Fuente: ${job.source}</span>
      <a href="${job.sourceUrl}" class="btn btn-secondary" target="_blank" rel="noopener">Ver oferta</a>
    </div>
  `;

  return card;
}

/** Renderiza una lista de empleos dentro de un contenedor por id */
function renderJobList(containerId, jobs) {
  const container = document.getElementById(containerId);
  if (!container) return;

  container.innerHTML = "";
  jobs.forEach(job => container.appendChild(createJobCard(job)));
}

/** Renderiza los chips de "Explorar por categoría" */
function renderCategoryGrid() {
  const container = document.getElementById("categoryGrid");
  if (!container) return;

  container.innerHTML = CATEGORIES.map(cat => `
    <button type="button" class="chip-card">${cat}</button>
  `).join("");
}

/** Renderiza los chips de "Explorar por ubicación" (provincias únicas de los datos mock) */
function renderLocationGrid() {
  const container = document.getElementById("locationGrid");
  if (!container) return;

  const provinces = [...new Set(MOCK_JOBS.map(job => job.province))];

  container.innerHTML = provinces.map(prov => `
    <button type="button" class="chip-card">${prov}</button>
  `).join("");
}

/**
 * Navbar: agrega la clase "scrolled" cuando el usuario baja,
 * para que se vea más chica/opaca (definido en CSS).
 */
function initScrollNavbar() {
  const header = document.querySelector(".site-header");
  if (!header) return;

  window.addEventListener("scroll", () => {
    header.classList.toggle("scrolled", window.scrollY > 40);
  });
}

/** Menú hamburguesa mobile */
function initMobileMenu() {
  const toggle = document.getElementById("navToggle");
  const menu = document.getElementById("navMenu");
  if (!toggle || !menu) return;

  toggle.addEventListener("click", () => {
    const isOpen = menu.classList.toggle("open");
    toggle.setAttribute("aria-expanded", isOpen);
  });

  // Cierra el menú al tocar un link (mejor experiencia en mobile)
  menu.querySelectorAll("a").forEach(link => {
    link.addEventListener("click", () => {
      menu.classList.remove("open");
      toggle.setAttribute("aria-expanded", "false");
    });
  });
}

/**
 * Animación de aparición suave: las secciones empiezan con
 * opacity 0 (ver CSS) y se les agrega "visible" cuando entran
 * en pantalla. IntersectionObserver es más eficiente que
 * escuchar el evento "scroll" a mano.
 */
function initRevealOnScroll() {
  const targets = document.querySelectorAll(".reveal");
  if (!targets.length) return;

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add("visible");
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.15 });

  targets.forEach(el => observer.observe(el));
}

/* ===================== INICIALIZACIÓN ===================== */
document.addEventListener("DOMContentLoaded", () => {
  const featured = MOCK_JOBS.filter(job => job.featured);

  renderJobList("featuredList", featured);
  renderJobList("jobList", MOCK_JOBS);
  renderCategoryGrid();
  renderLocationGrid();

  initScrollNavbar();
  initMobileMenu();
  initRevealOnScroll();
});
