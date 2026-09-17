/* notify.js · SweetAlert2 con estilo Artemisa: confirmar borrados + toasts.
   Requiere vendor/sweetalert2/sweetalert2.min.js cargado antes. */
(function () {
  "use strict";
  if (!window.Swal) return;

  window.artNotify = {
    confirm: function (opts) {
      return Swal.fire(Object.assign({
        icon: "warning",
        showCancelButton: true,
        reverseButtons: true,
        confirmButtonText: "Sí",
        cancelButtonText: "Cancelar",
      }, opts || {}));
    },
    toast: function (msg, icon) {
      return Swal.fire({
        toast: true, position: "top-end", timer: 2800,
        showConfirmButton: false, timerProgressBar: true,
        icon: icon || "success", title: msg,
      });
    },
    // «Trabajando…»: para lo que tarda (buscar en una API externa, encolar un lote). Sin botones, no se cierra
    // con clic ni Escape; lo cierra la navegacion que viene detras.
    working: function (title, text) {
      return Swal.fire({
        title: title || "Un momento…", text: text || "",
        allowOutsideClick: false, allowEscapeKey: false, showConfirmButton: false,
        didOpen: function () { Swal.showLoading(); },
      });
    },
  };

  // --- Espera al enviar (delegado): cualquier <form data-espera="Buscando en VNDB…" data-espera-texto="…">
  // muestra el «trabajando…» al enviarse. Sirve a GET y POST; si el navegador vuelve atras, se cierra solo.
  document.addEventListener("submit", function (e) {
    var f = e.target;
    if (!f.dataset || !f.dataset.espera) return;
    if (typeof f.checkValidity === "function" && !f.checkValidity()) return;   // deja que el navegador avise
    window.artNotify.working(f.dataset.espera, f.dataset.esperaTexto || "");
  });
  window.addEventListener("pageshow", function () { if (Swal.isVisible() && Swal.isLoading()) Swal.close(); });

  // --- Borrado con confirmación (delegado: sirve también para filas AJAX) ---
  // Cualquier <a class="js-delete" href="URL-de-borrado" data-name="…">.
  document.addEventListener("click", function (e) {
    var a = e.target.closest && e.target.closest(".js-delete");
    if (!a) return;
    e.preventDefault();
    var url = a.getAttribute("href");
    var name = a.dataset.name || "este registro";
    window.artNotify.confirm({
      title: "¿Eliminar?",
      html: "Se eliminará <b>«" + name + "»</b>.<br>Esta acción no se puede deshacer.",
      confirmButtonText: "Sí, eliminar",
      customClass: { confirmButton: "swal2-danger" },
    }).then(function (r) {
      if (r.isConfirmed) {
        var f = document.getElementById("delete-form");
        if (f) { f.action = url; f.submit(); }
        else { window.location.href = url; }  // fallback a la página de confirmación
      }
    });
  });

  // --- Acciones rápidas por POST (toggles: activar/desactivar, +18, staff…) ---
  // Cualquier <a class="js-post" href="URL"> con data-confirm opcional.
  document.addEventListener("click", function (e) {
    var a = e.target.closest && e.target.closest(".js-post");
    if (!a) return;
    e.preventDefault();
    var url = a.getAttribute("href");
    var msg = a.dataset.confirm;
    function go() {
      var f = document.getElementById("action-form");
      if (f) { f.action = url; f.submit(); }
      else { window.location.href = url; }
    }
    if (msg) {
      window.artNotify.confirm({ title: "¿Confirmar?", text: msg, confirmButtonText: "Sí, continuar" })
        .then(function (r) { if (r.isConfirmed) go(); });
    } else { go(); }
  });

  // --- Formularios con data-confirm (borrado en página de detalle, etc.) ---
  document.querySelectorAll("form[data-confirm]").forEach(function (f) {
    f.addEventListener("submit", function (e) {
      if (f.dataset.confirmed) return;
      e.preventDefault();
      window.artNotify.confirm({
        title: "¿Estás seguro?",
        text: f.dataset.confirm,
        confirmButtonText: "Sí, continuar",
      }).then(function (r) {
        if (r.isConfirmed) { f.dataset.confirmed = "1"; f.submit(); }
      });
    });
  });

  // --- Mensajes de Django → toasts ---
  if (window.DJ_MESSAGES && window.DJ_MESSAGES.length) {
    window.DJ_MESSAGES.forEach(function (m) {
      var icon = "info";
      if (m.tags.indexOf("success") !== -1) icon = "success";
      else if (m.tags.indexOf("error") !== -1) icon = "error";
      else if (m.tags.indexOf("warning") !== -1) icon = "warning";
      window.artNotify.toast(m.text, icon);
    });
  }
})();
