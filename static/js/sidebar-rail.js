/* =====================================================================
   sidebar-rail.js  ·  ayuda para el sidebar en modo rail (solo-iconos)
   - Secciones CON hijos (acordeón .nav-tree): al hacer hover muestran un
     FLYOUT con sus opciones navegables (como BootstrapMade).
   - Ítems sueltos (sin hijos): solo un tooltip nativo (title).
   Solo en desktop y cuando el sidebar NO está fijado abierto (body.nav-expanded).
   Compartido por los 3 sidebars. Limpieza a prueba de "se queda pegado".
   ===================================================================== */
(function () {
  "use strict";
  var sidebar = document.getElementById("sidebar");
  if (!sidebar) return;

  var fly = null;
  var timer = null;

  function railMode() {
    return window.innerWidth > 900 && !document.body.classList.contains("nav-expanded");
  }
  // Borra TODO flyout (incluye huérfanos) — clave para que nunca se quede pegado.
  function remove() {
    if (timer) { clearTimeout(timer); timer = null; }
    var nodes = document.querySelectorAll(".rail-flyout");
    for (var i = 0; i < nodes.length; i++) nodes[i].remove();
    fly = null;
  }
  function scheduleRemove() { if (timer) clearTimeout(timer); timer = setTimeout(remove, 160); }
  function cancelRemove() { if (timer) { clearTimeout(timer); timer = null; } }

  function textNoIcon(el) {
    var c = el.cloneNode(true);
    var ico = c.querySelector(".ico");
    if (ico) ico.remove();
    return c.textContent.trim();
  }

  // Tooltips nativos en TODOS los ítems (identificar el icono sin flyout).
  sidebar.querySelectorAll(".nav-tree__home, .nav-item").forEach(function (el) {
    var label = textNoIcon(el);
    if (label && !el.getAttribute("title")) el.setAttribute("title", label);
  });

  function showFlyout(tree) {
    remove();
    if (!railMode()) return;

    var items = tree.querySelectorAll(".nav-item");   // todos los hijos navegables
    if (!items.length) return;                        // sin hijos → no hay flyout

    fly = document.createElement("div");
    fly.className = "rail-flyout";

    var home = tree.querySelector(".nav-tree__home");
    var head = document.createElement("div");
    head.className = "rail-flyout__head";
    head.textContent = home ? textNoIcon(home) : "";
    if (home) head.addEventListener("click", function () { location.href = home.getAttribute("href"); });
    fly.appendChild(head);

    items.forEach(function (a) {
      var link = document.createElement("a");
      link.href = a.getAttribute("href") || "#";
      link.className = "rail-flyout__item" + (a.classList.contains("active") ? " active" : "");
      link.textContent = a.textContent.trim();
      fly.appendChild(link);
    });

    document.body.appendChild(fly);
    fly.addEventListener("mouseenter", cancelRemove);
    fly.addEventListener("mouseleave", scheduleRemove);

    var sb = sidebar.getBoundingClientRect();
    var r = tree.getBoundingClientRect();
    fly.style.left = (sb.right + 4) + "px";
    var top = Math.max(64, r.top);
    top = Math.min(top, window.innerHeight - fly.offsetHeight - 12);
    fly.style.top = top + "px";
  }

  // Hover sobre una sección del acordeón → flyout con sus hijos.
  sidebar.addEventListener("mouseover", function (e) {
    if (!railMode()) { remove(); return; }
    var tree = e.target.closest(".nav-tree");
    if (tree && tree.querySelector(".nav-item")) { cancelRemove(); showFlyout(tree); }
  });

  // Al salir del sidebar, quitar (con margen para poder cruzar al flyout).
  sidebar.addEventListener("mouseleave", scheduleRemove);
  // Cinturón: cualquier movimiento fuera de sidebar y flyout lo quita.
  document.addEventListener("mouseover", function (e) {
    if (fly && !sidebar.contains(e.target) && !fly.contains(e.target)) scheduleRemove();
  });
  window.addEventListener("scroll", remove, true);
  window.addEventListener("resize", remove);
})();
