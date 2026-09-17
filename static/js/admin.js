/* =====================================================================
   admin.js  ·  comportamiento del panel de gestión
   - Toggle del sidebar (colapsar desktop / drawer móvil)
   - Botón "subir"
   ===================================================================== */
(function () {
  "use strict";

  var navToggle = document.getElementById("nav-toggle");
  var sidebar = document.getElementById("sidebar");
  var scrim = document.getElementById("scrim");

  // Restaurar si el usuario dejó el sidebar FIJADO abierto (por defecto = rail).
  try { if (localStorage.getItem("navExpanded") === "1") document.body.classList.add("nav-expanded"); } catch (e) {}

  function closeDrawer() {
    if (sidebar) sidebar.classList.remove("open");
    if (scrim) scrim.classList.remove("show");
  }
  if (navToggle) navToggle.addEventListener("click", function () {
    if (window.innerWidth <= 900) {
      if (sidebar) sidebar.classList.toggle("open");
      if (scrim) scrim.classList.toggle("show");
    } else {
      // Desktop: el toggle FIJA/DESFIJA el sidebar abierto (rail ↔ completo).
      var on = document.body.classList.toggle("nav-expanded");
      try { localStorage.setItem("navExpanded", on ? "1" : "0"); } catch (e) {}
    }
  });
  if (scrim) scrim.addEventListener("click", closeDrawer);

  // ---- Acordeón del sidebar: solo una SECCIÓN de primer nivel abierta a la vez.
  // Excluye los sub-menús (.nav-tree--sub: Satélite, Relacional, Estados…): esos
  // se abren/cierran libres como <details> nativos, sin cerrar a su padre.
  var trees = document.querySelectorAll(".nav-tree:not(.nav-tree--sub)");
  trees.forEach(function (d) {
    d.addEventListener("toggle", function () {
      if (d.open) {
        trees.forEach(function (o) { if (o !== d) o.open = false; });
      }
    });
  });

  var goTop = document.createElement("button");
  goTop.id = "go-top"; goTop.type = "button";
  goTop.setAttribute("aria-label", "Volver arriba"); goTop.innerHTML = '<i class="bi bi-arrow-up"></i>';
  document.body.appendChild(goTop);
  goTop.addEventListener("click", function () { window.scrollTo({ top: 0, behavior: "smooth" }); });
  window.addEventListener("scroll", function () {
    goTop.classList.toggle("show", window.scrollY > 300);
  }, { passive: true });
})();
