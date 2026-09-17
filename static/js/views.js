/* =====================================================================
   views.js  ·  comportamiento compartido del shell (admin + público)
   - Conmutación de vistas
   - Fondo por categoría/vista (--bg-cat)
   - Sidebar colapsable (desktop) / drawer (móvil)
   - Toast de feedback
   ===================================================================== */
(function () {
  "use strict";

  var body    = document.body;
  var sidebar = document.getElementById("sidebar");
  var scrim   = document.getElementById("scrim");
  var bgLayer = document.querySelector(".bg-layer");
  var toggle  = document.getElementById("nav-toggle");

  // ---- Fondo por categoría --------------------------------------------
  // data-bg en la vista o en el nav-item → --bg-{clave}, resuelto por CSS var.
  function setBg(key) {
    if (key && bgLayer) bgLayer.style.setProperty("--bg-cat", "var(--bg-" + key + ")");
  }

  // ---- Conmutación de vistas ------------------------------------------
  var views    = document.querySelectorAll(".view");
  var navItems = document.querySelectorAll(".nav-item");

  function showView(name, bgKey) {
    var target = document.getElementById("view-" + name);
    if (!target) return;
    views.forEach(function (v) { v.classList.remove("active"); });
    target.classList.add("active");
    setBg(bgKey || target.getAttribute("data-bg") || "general");
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  function setActiveNav(el) {
    navItems.forEach(function (n) { n.classList.remove("active"); });
    if (el) el.classList.add("active");
  }

  function closeDrawer() {
    if (sidebar) sidebar.classList.remove("open");
    if (scrim) scrim.classList.remove("show");
  }

  navItems.forEach(function (item) {
    item.addEventListener("click", function (e) {
      var name = item.getAttribute("data-view");
      // Sin vista local (p. ej. otra app): deja navegar por href a otra página.
      if (!name || !document.getElementById("view-" + name)) return;
      e.preventDefault();
      setActiveNav(item);
      showView(name, item.getAttribute("data-bg"));
      closeDrawer();
    });
  });

  // Cards, botones y enlaces con data-nav
  document.querySelectorAll("[data-nav]").forEach(function (el) {
    el.addEventListener("click", function (e) {
      var target = el.getAttribute("data-nav");
      if (!document.getElementById("view-" + target)) return; // deja navegar por href
      e.preventDefault();
      showView(target);
      if (target === "home") setActiveNav(document.querySelector('.nav-item[data-view="home"]'));
      closeDrawer();
    });
  });

  // ---- Toggle del sidebar: colapsa (desktop) / drawer (móvil) ----------
  if (toggle) {
    toggle.addEventListener("click", function () {
      if (window.innerWidth <= 900) {
        if (sidebar) sidebar.classList.toggle("open");
        if (scrim) scrim.classList.toggle("show");
      } else {
        body.classList.toggle("nav-collapsed");
      }
    });
  }
  if (scrim) scrim.addEventListener("click", closeDrawer);

  // ---- Toggles genéricos (check-row) ----------------------------------
  document.querySelectorAll(".check-row .box").forEach(function (box) {
    box.addEventListener("click", function () {
      box.classList.toggle("on");
      box.setAttribute("aria-checked", box.classList.contains("on") ? "true" : "false");
    });
  });

  // ---- Toast -----------------------------------------------------------
  var toastEl, toastTimer;
  function toast(msg) {
    if (!toastEl) {
      toastEl = document.createElement("div");
      toastEl.className = "toast";
      document.body.appendChild(toastEl);
    }
    toastEl.innerHTML = '<span class="ok">✔</span> ' + msg;
    requestAnimationFrame(function () { toastEl.classList.add("show"); });
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { toastEl.classList.remove("show"); }, 2200);
  }
  document.querySelectorAll(".act, .btn-primary, .btn-save, .chip").forEach(function (b) {
    b.addEventListener("click", function () {
      var label = b.getAttribute("title") || b.textContent.trim();
      toast(label + " — acción de demostración");
    });
  });

  // ---- Panel de importación externa (Deezer/VNDB/Jikan) ---------------
  var launch = document.getElementById("import-launch");
  if (launch) {
    var prog = document.getElementById("import-progress");
    var bar = document.getElementById("import-bar");
    var pct = document.getElementById("import-pct");
    var log = document.getElementById("import-log");
    var cancelBtn = document.getElementById("import-cancel");
    var timer = null;

    function stopImport(msg, cls) {
      if (timer) { clearInterval(timer); timer = null; }
      if (log) log.insertAdjacentHTML("beforeend", '<div class="' + (cls || "") + '">' + msg + "</div>");
    }
    launch.addEventListener("click", function () {
      if (timer) return;
      if (prog) prog.classList.remove("hidden");
      if (log) log.innerHTML = '<div>› Iniciando importación…</div>';
      var p = 0;
      timer = setInterval(function () {
        p += 4 + Math.floor(Math.random() * 6);
        if (p >= 100) { p = 100; }
        if (bar) bar.style.width = p + "%";
        if (pct) pct.textContent = p + "%";
        if (p % 20 < 6 && log) log.insertAdjacentHTML("beforeend", "<div>› Lote procesado · " + p + "%</div>");
        if (p >= 100) stopImport('<span class="ok">✔ Importación completada</span>', "ok");
      }, 500);
    });
    if (cancelBtn) cancelBtn.addEventListener("click", function () {
      stopImport('<span class="warn">⊘ Cancelada por el usuario (TaskCancellation)</span>', "warn");
    });
  }

  // ---- Botón "subir" (aparece al hacer scroll) ------------------------
  var goTop = document.createElement("button");
  goTop.id = "go-top";
  goTop.type = "button";
  goTop.setAttribute("aria-label", "Volver arriba");
  goTop.textContent = "↑";
  document.body.appendChild(goTop);
  goTop.addEventListener("click", function () { window.scrollTo({ top: 0, behavior: "smooth" }); });
  window.addEventListener("scroll", function () {
    goTop.classList.toggle("show", window.scrollY > 300);
  }, { passive: true });

  // ---- DataTable client-side (paginación real, top + bottom) ----------
  var dt = document.getElementById("dt");
  if (dt && window.DT_ROWS) {
    var rows = window.DT_ROWS;
    var pageLen = window.DT_PAGELEN || 25;
    var page = 1, term = "";
    var tbody = dt.querySelector("tbody");
    var infos = document.querySelectorAll(".dt-info");   // top y bottom
    var pagers = document.querySelectorAll(".dt-pager");  // top y bottom
    var search = document.getElementById("dt-search");
    var lenSel = document.getElementById("dt-len");

    function dtFiltered() {
      if (!term) return rows;
      var t = term.toLowerCase();
      return rows.filter(function (r) { return r.text.toLowerCase().indexOf(t) !== -1; });
    }
    function dtWindow(cur, total) {
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
    function dtRender() {
      var data = dtFiltered();
      var total = data.length;
      var pages = Math.max(1, Math.ceil(total / pageLen));
      if (page > pages) page = pages;
      var start = (page - 1) * pageLen;
      var slice = data.slice(start, start + pageLen);
      tbody.innerHTML = slice.map(function (r) { return r.html; }).join("");
      var infoHtml = "Mostrando <b>" + (total ? start + 1 : 0) + "–" + (start + slice.length) + "</b> de <b>" + total + "</b>";
      infos.forEach(function (el) { el.innerHTML = infoHtml; });
      var pagerHtml =
        '<button data-p="prev"'+(page===1?' disabled':'')+'>‹</button>' +
        dtWindow(page, pages).map(function (p) {
          return p === "…" ? '<button disabled>…</button>'
            : '<button data-p="' + p + '"' + (p === page ? ' class="active"' : "") + ">" + p + "</button>";
        }).join("") +
        '<button data-p="next"'+(page===pages?' disabled':'')+'>›</button>';
      pagers.forEach(function (el) { el.innerHTML = pagerHtml; });
    }
    function dtGoto(p) {
      var pages = Math.max(1, Math.ceil(dtFiltered().length / pageLen));
      if (p === "prev") page = Math.max(1, page - 1);
      else if (p === "next") page = Math.min(pages, page + 1);
      else page = parseInt(p, 10);
      dtRender();
      dt.scrollIntoView({ behavior: "smooth", block: "start" });
    }
    pagers.forEach(function (pg) {
      pg.addEventListener("click", function (e) {
        var b = e.target.closest("button"); if (!b || b.disabled) return;
        dtGoto(b.getAttribute("data-p"));
      });
    });
    if (search) search.addEventListener("input", function () { term = this.value; page = 1; dtRender(); });
    if (lenSel) lenSel.addEventListener("change", function () { pageLen = parseInt(this.value, 10); page = 1; dtRender(); });
    dtRender();
  }

  // ---- Init: fondo de la vista activa al cargar -----------------------
  var initial = document.querySelector(".view.active");
  if (initial) setBg(initial.getAttribute("data-bg") || "general");

  // Exponer para navegación programática
  window.showView = showView;
})();
