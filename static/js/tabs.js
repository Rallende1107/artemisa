/* Pestañas que FILTRAN en la página (componente templates/components/tabs.html).
   Cada `[data-tabs]` manda sobre los bloques `[data-group]` de su objetivo (`data-tabs-target`, por defecto el
   documento): al pulsar una pestaña se ven solo los de su grupo; la de clave vacía los muestra todos.
   La elegida queda en la dirección (#clave) para poder compartirla o recargar sin perderla. */
(function () {
  "use strict";

  function arrancar(barra) {
    var destino = barra.dataset.tabsTarget ? document.querySelector(barra.dataset.tabsTarget) : document;
    if (!destino) return;
    var botones = barra.querySelectorAll(".snav__item[data-tab]");
    if (!botones.length) return;
    var bloques = destino.querySelectorAll("[data-group]");

    function mostrar(clave, conHash) {
      bloques.forEach(function (b) { b.hidden = clave !== "" && b.dataset.group !== clave; });
      botones.forEach(function (b) { b.classList.toggle("on", b.dataset.tab === clave); });
      if (conHash) {
        history.replaceState(null, "", clave ? "#" + clave : location.pathname + location.search);
      }
    }

    barra.addEventListener("click", function (e) {
      var boton = e.target.closest(".snav__item[data-tab]");
      if (boton) mostrar(boton.dataset.tab, true);
    });

    var inicial = decodeURIComponent(location.hash.slice(1));
    if (inicial && barra.querySelector('[data-tab="' + inicial.replace(/"/g, "") + '"]')) mostrar(inicial, false);
  }

  document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll("[data-tabs]").forEach(arrancar);
  });
})();
