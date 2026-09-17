/* forms.js · inicializa flatpickr en los campos .js-date (degrada a <input type=date>) */
(function () {
  "use strict";
  if (!window.flatpickr) return;  // si no cargó, el input date nativo sigue funcionando
  if (window.flatpickr.l10ns && window.flatpickr.l10ns.es) {
    flatpickr.localize(flatpickr.l10ns.es);
  }
  document.querySelectorAll(".js-date").forEach(function (el) {
    // Edad mínima (p.ej. nacimiento con data-min-age="12"): bloquea las fechas de
    // menos de N años → el usuario no puede elegir una que dispare el error de
    // validación, y el calendario abre cerca de esa fecha límite.
    var maxDate = "today";   // por defecto: no futuras
    var minAge = parseInt(el.dataset.minAge || "", 10);
    if (minAge > 0) {
      var d = new Date();
      d.setFullYear(d.getFullYear() - minAge);
      maxDate = d;
    }
    flatpickr(el, {
      dateFormat: "Y-m-d",     // valor REAL que se envía (ISO; Django lo parsea)
      altInput: true,
      altFormat: "d-m-Y",      // lo que VE el usuario: día-mes-año (13-08-2026)
      monthSelectorType: "static",  // mes como texto + flechas (sin el <select> blanco nativo)
      maxDate: maxDate,
      disableMobile: true,    // usa flatpickr también en móvil (estilo consistente)
    });
  });

  // Select2 en los <select> de los formularios (FK/M2M).
  if (window.jQuery && window.jQuery.fn && window.jQuery.fn.select2) {
    window.jQuery(".form-card select").each(function () {
      var $s = window.jQuery(this);
      var url = $s.attr("data-ajax-url");
      var multiple = $s.prop("multiple");
      var opts = {
        width: "100%",
        placeholder: multiple ? "Buscar y elegir varios…" : "—",
        allowClear: !$s.prop("required") && !multiple,
        // En los múltiples (géneros, temas…) NO cerrar tras cada elección:
        // así se pueden encadenar varias seguidas sin reabrir el desplegable.
        closeOnSelect: !multiple,
      };
      if (url) {
        // Búsqueda en el SERVIDOR (no carga toda la tabla): escala a millones de filas.
        opts.minimumInputLength = 0;
        opts.ajax = {
          url: url, dataType: "json", delay: 250, cache: true,
          data: function (params) { return { q: params.term || "", page: params.page || 1 }; },
          processResults: function (data, params) {
            params.page = params.page || 1;
            return { results: data.results, pagination: { more: !!(data.pagination && data.pagination.more) } };
          },
        };
      }
      $s.select2(opts);
    });
  }
})();

/* ---- Campo IMAGEN (_campo_imagen.html): la miniatura muestra SIEMPRE la
   actual. Elegir archivo solo suma la nueva al lightbox (Ver imagen → 2/2 =
   antes/después). «Eliminar la actual» conmuta el checkbox -clear oculto. ---- */
(function () {
  document.addEventListener("change", function (e) {
    var inp = e.target.closest && e.target.closest(".js-img-input");
    if (!inp) return;
    var w = inp.closest(".img-field"); if (!w) return;
    var nueva = w.querySelector("[data-img-nueva]");
    var f = inp.files && inp.files[0];
    if (nueva && f && f.type.indexOf("image/") === 0) {
      nueva.src = URL.createObjectURL(f);
      nueva.classList.add("shot");   // entra a la galería del lightbox (sigue oculta en la página)
    } else if (nueva) {
      nueva.classList.remove("shot");
      nueva.removeAttribute("src");
    }
  });
  document.addEventListener("click", function (e) {
    var btn = e.target.closest && e.target.closest(".js-img-ver, .js-img-clear");
    if (!btn) return;
    var w = btn.closest(".img-field"); if (!w) return;
    if (btn.classList.contains("js-img-ver")) {
      var actual = w.querySelector("[data-img-actual]");
      if (actual) actual.click();   // abre el lightbox (con nueva elegida: 2 fotos)
      return;
    }
    var chk = w.querySelector('.img-controls input[type="checkbox"]');
    if (!chk) return;
    chk.checked = !chk.checked;
    btn.classList.toggle("on", chk.checked);
    btn.innerHTML = chk.checked
      ? '<i class="bi bi-arrow-counterclockwise"></i> Se eliminará al guardar — conservar'
      : '<i class="bi bi-trash"></i> Eliminar la actual';
    w.classList.toggle("js-clearing", chk.checked);
  });
})();
