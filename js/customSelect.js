/* ===========================================================
   CUSTOM SELECT — componente reutilizable e independiente.
   Reemplaza visualmente cualquier <select> por un dropdown
   propio, animado y con estilo glass, sin depender de qué
   página lo use ni de qué datos tenga adentro.

   El <select> original NO se elimina: queda oculto y sigue
   siendo la "fuente de verdad" (su .value es lo que se lee
   con FormData en filters.js). Esto se llama "mejora
   progresiva": la funcionalidad base ya existía, acá solo le
   cambiamos la piel visual.

   No depende de data.js ni de ui.js — por eso puede ir antes
   que ambos en el HTML.
   =========================================================== */

/** Convierte un <select> en un dropdown personalizado */
function enhanceSelect(select) {
  if (select._cs) return; // ya mejorado, no lo dupliques

  const wrapper = document.createElement("div");
  wrapper.className = "custom-select";

  const trigger = document.createElement("button");
  trigger.type = "button";
  trigger.className = "cs-trigger";
  trigger.setAttribute("aria-haspopup", "listbox");
  trigger.setAttribute("aria-expanded", "false");
  trigger.innerHTML = `
    <span class="cs-value"></span>
    <svg class="cs-chevron" viewBox="0 0 20 20" fill="none" aria-hidden="true">
      <path d="M5 7.5L10 12.5L15 7.5" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
  `;

  const panel = document.createElement("ul");
  panel.className = "cs-panel";
  panel.setAttribute("role", "listbox");

  select.insertAdjacentElement("afterend", wrapper);
  wrapper.append(select, trigger, panel);

  select.style.display = "none";
  select.tabIndex = -1;

  // Asocia la <label> existente al botón, así sigue siendo accesible
  const label = document.querySelector(`label[for="${select.id}"]`);
  if (label) {
    if (!label.id) label.id = `${select.id}-label`;
    trigger.setAttribute("aria-labelledby", label.id);
    label.addEventListener("click", (e) => {
      e.preventDefault();
      trigger.click();
    });
  }

  select._cs = { wrapper, trigger, panel, activeIndex: 0 };

  trigger.addEventListener("click", () => toggleCustomSelect(select));
  trigger.addEventListener("keydown", (e) => handleSelectKeydown(e, select));
  document.addEventListener("click", (e) => {
    if (!wrapper.contains(e.target)) closeCustomSelect(select);
  });

  refreshCustomSelect(select);
}

/** Reconstruye las opciones del dropdown a partir del <select> actual.
    Se llama al iniciar y cada vez que filters.js repuebla un <select>
    (por ejemplo, ciudad al cambiar de provincia). */
function refreshCustomSelect(select) {
  if (!select._cs) return;

  const { trigger, panel } = select._cs;
  const options = Array.from(select.options);

  panel.innerHTML = "";
  options.forEach((opt, index) => {
    const li = document.createElement("li");
    li.className = "cs-option";
    li.id = `${select.id}-opt-${index}`;
    li.setAttribute("role", "option");
    li.dataset.value = opt.value;
    li.textContent = opt.textContent;
    li.setAttribute("aria-selected", opt.value === select.value ? "true" : "false");

    li.addEventListener("click", () => commitSelectValue(select, opt.value));
    panel.appendChild(li);
  });

  const selected = select.options[select.selectedIndex];
  trigger.querySelector(".cs-value").textContent = selected ? selected.textContent : "";
  select._cs.activeIndex = select.selectedIndex;
}

/** Aplica un valor elegido: actualiza el select real y dispara "change"
    para que filters.js (que escucha ese evento) reaccione igual que
    si el usuario hubiese usado un <select> nativo. */
function commitSelectValue(select, value) {
  select.value = value;
  select.dispatchEvent(new Event("change", { bubbles: true }));
  refreshCustomSelect(select);
  closeCustomSelect(select);
  select._cs.trigger.focus();
}

function setActiveOption(select, index) {
  const { panel, trigger } = select._cs;
  const options = panel.querySelectorAll(".cs-option");
  const clamped = Math.max(0, Math.min(options.length - 1, index));

  select._cs.activeIndex = clamped;
  options.forEach((li, i) => li.classList.toggle("active", i === clamped));
  options[clamped]?.scrollIntoView({ block: "nearest" });
  trigger.setAttribute("aria-activedescendant", options[clamped]?.id || "");
}

function openCustomSelect(select) {
  closeAllCustomSelects();
  select._cs.wrapper.classList.add("open");
  select._cs.trigger.setAttribute("aria-expanded", "true");
  setActiveOption(select, select.selectedIndex);
}

function closeCustomSelect(select) {
  select._cs.wrapper.classList.remove("open");
  select._cs.trigger.setAttribute("aria-expanded", "false");
}

function toggleCustomSelect(select) {
  select._cs.wrapper.classList.contains("open") ? closeCustomSelect(select) : openCustomSelect(select);
}

function closeAllCustomSelects() {
  document.querySelectorAll(".custom-select.open").forEach(w => {
    w.classList.remove("open");
    w.querySelector(".cs-trigger")?.setAttribute("aria-expanded", "false");
  });
}

/** Navegación por teclado: flechas mueven el resaltado, Enter confirma,
    Escape cierra sin cambiar nada — el mismo patrón que un <select> nativo. */
function handleSelectKeydown(e, select) {
  const isOpen = select._cs.wrapper.classList.contains("open");
  const options = Array.from(select.options);

  if (["ArrowDown", "ArrowUp", "Enter", " ", "Escape"].includes(e.key)) e.preventDefault();

  if (!isOpen) {
    if (["ArrowDown", "ArrowUp", "Enter", " "].includes(e.key)) openCustomSelect(select);
    return;
  }

  if (e.key === "ArrowDown") setActiveOption(select, select._cs.activeIndex + 1);
  else if (e.key === "ArrowUp") setActiveOption(select, select._cs.activeIndex - 1);
  else if (e.key === "Enter") commitSelectValue(select, options[select._cs.activeIndex].value);
  else if (e.key === "Escape") closeCustomSelect(select);
}

/** Mejora todos los <select> presentes en la página actual */
function initCustomSelects() {
  document.querySelectorAll("select").forEach(enhanceSelect);
}
