/* =====================================================================
   public.js  ·  comportamiento de la cara pública
   - Age gate (+18): confirma edad → revela portadas adultas (blur off)
   - Botón "subir"
   ===================================================================== */
(function () {
  "use strict";

  // ---- Age gate --------------------------------------------------------
  var gate = document.getElementById("agegate");
  if (gate) {
    var yes = document.getElementById("ag-yes");
    var no = document.getElementById("ag-no");
    if (yes) yes.addEventListener("click", function () {
      document.body.classList.add("adult-ok");
      gate.classList.add("hidden");
    });
    if (no) no.addEventListener("click", function () {
      document.body.classList.remove("adult-ok");
      gate.classList.add("hidden");
    });
  }

  // ---- Índice (TOC) de páginas legales ---------------------------------
  var toc = document.querySelector(".legal__toc");
  if (toc) {
    toc.querySelectorAll("a").forEach(function (link) {
      link.addEventListener("click", function (e) {
        e.preventDefault();
        var t = document.querySelector(link.getAttribute("href"));
        if (t) t.scrollIntoView({ behavior: "smooth", block: "start" });
        toc.querySelectorAll("a").forEach(function (a) { a.classList.remove("active"); });
        link.classList.add("active");
      });
    });
  }

  // ---- Explorar: grid paginado (client-side) --------------------------
  var grid = document.getElementById("exploreGrid");
  if (grid && window.EXPLORE_ROWS) {
    var rows = window.EXPLORE_ROWS;
    var pageLen = window.EXPLORE_PAGELEN || 24;
    var page = 1;
    var infos = document.querySelectorAll(".ex-info");
    var pagers = document.querySelectorAll(".ex-pager");
    var lenSel = document.getElementById("ex-len");

    function exWin(cur, total) {
      var arr = [];
      if (total <= 7) { for (var i = 1; i <= total; i++) arr.push(i); return arr; }
      arr.push(1);
      var s = Math.max(2, cur - 1), e = Math.min(total - 1, cur + 1);
      if (s > 2) arr.push("…");
      for (var j = s; j <= e; j++) arr.push(j);
      if (e < total - 1) arr.push("…");
      arr.push(total);
      return arr;
    }
    function exRender() {
      var total = rows.length;
      var pages = Math.max(1, Math.ceil(total / pageLen));
      if (page > pages) page = pages;
      var start = (page - 1) * pageLen;
      var slice = rows.slice(start, start + pageLen);
      grid.innerHTML = slice.join("");
      var infoHtml = "Mostrando <b>" + (total ? start + 1 : 0) + "–" + (start + slice.length) + "</b> de <b>" + total + "</b>";
      infos.forEach(function (el) { el.innerHTML = infoHtml; });
      var pagerHtml =
        '<button data-p="prev"' + (page === 1 ? " disabled" : "") + ">‹</button>" +
        exWin(page, pages).map(function (p) {
          return p === "…" ? "<button disabled>…</button>"
            : '<button data-p="' + p + '"' + (p === page ? ' class="active"' : "") + ">" + p + "</button>";
        }).join("") +
        '<button data-p="next"' + (page === pages ? " disabled" : "") + ">›</button>";
      pagers.forEach(function (el) { el.innerHTML = pagerHtml; });
    }
    pagers.forEach(function (pg) {
      pg.addEventListener("click", function (e) {
        var b = e.target.closest("button"); if (!b || b.disabled) return;
        var p = b.getAttribute("data-p");
        var pages = Math.max(1, Math.ceil(rows.length / pageLen));
        if (p === "prev") page = Math.max(1, page - 1);
        else if (p === "next") page = Math.min(pages, page + 1);
        else page = parseInt(p, 10);
        exRender();
        grid.scrollIntoView({ behavior: "smooth", block: "start" });
      });
    });
    if (lenSel) lenSel.addEventListener("change", function () { pageLen = parseInt(this.value, 10); page = 1; exRender(); });
    exRender();
  }

  // ---- Sidebar: colapsar (desktop) / drawer con scrim (móvil) ----------
  var navToggle = document.getElementById("nav-toggle");
  var sidebar = document.getElementById("sidebar");
  var scrim = document.getElementById("scrim");
  // Restaurar si el sidebar quedó FIJADO abierto (por defecto = rail solo-iconos).
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
      // Desktop: FIJA/DESFIJA el sidebar abierto (rail ↔ completo).
      var on = document.body.classList.toggle("nav-expanded");
      try { localStorage.setItem("navExpanded", on ? "1" : "0"); } catch (e) {}
    }
  });
  if (scrim) scrim.addEventListener("click", closeDrawer);

  // ---- Botón "subir" ---------------------------------------------------
  var goTop = document.createElement("button");
  goTop.id = "go-top"; goTop.type = "button";
  goTop.setAttribute("aria-label", "Volver arriba"); goTop.innerHTML = '<i class="bi bi-arrow-up"></i>';
  document.body.appendChild(goTop);
  goTop.addEventListener("click", function () { window.scrollTo({ top: 0, behavior: "smooth" }); });
  window.addEventListener("scroll", function () {
    goTop.classList.toggle("show", window.scrollY > 300);
  }, { passive: true });

  // ---- Modales nativos <dialog>: [data-open-modal="id"] abre; [data-close-modal]
  //      o clic en el fondo cierra. (Ej.: requisitos de contraseña.) --------------
  document.querySelectorAll("[data-open-modal]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var d = document.getElementById(btn.getAttribute("data-open-modal"));
      if (d && d.showModal) d.showModal();
    });
  });
  document.querySelectorAll("dialog.modal").forEach(function (d) {
    d.addEventListener("click", function (e) { if (e.target === d) d.close(); });  // clic en el backdrop
    d.querySelectorAll("[data-close-modal]").forEach(function (b) {
      b.addEventListener("click", function () { d.close(); });
    });
  });

  // ---- "Ver contraseña": ojo en TODOS los campos de contraseña (login,
  //      registro, cambiar/restablecer clave). Se auto-instala: envuelve el
  //      input y agrega el botón; sin tocar los HTML. ----------------------
  document.querySelectorAll('input[type="password"]').forEach(function (inp) {
    if (inp.closest(".pwd-wrap")) return;
    var wrap = document.createElement("div");
    wrap.className = "pwd-wrap";
    inp.parentNode.insertBefore(wrap, inp);
    wrap.appendChild(inp);
    var btn = document.createElement("button");
    btn.type = "button";
    btn.className = "pwd-toggle";
    btn.tabIndex = -1;   // no roba el tab entre campos
    btn.setAttribute("aria-label", "Mostrar contraseña");
    btn.innerHTML = '<i class="bi bi-eye"></i>';
    btn.addEventListener("click", function () {
      var ver = inp.type === "password";
      inp.type = ver ? "text" : "password";
      btn.innerHTML = ver ? '<i class="bi bi-eye-slash"></i>' : '<i class="bi bi-eye"></i>';
      btn.setAttribute("aria-label", ver ? "Ocultar contraseña" : "Mostrar contraseña");
      inp.focus();
    });
    wrap.appendChild(btn);
  });
})();
