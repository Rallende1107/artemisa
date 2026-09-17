/* datatable.js · inicializa DataTables server-side + toggle cards/lista con persistencia.
   Requiere jQuery + DataTables (+ buttons/responsive) cargados antes.
   El template define: window.DT_NCOLS, window.DT_ENTITY, window.CARDS_ENABLED.
   Opcionales (las listas PÚBLICAS las usan; el panel no las toca):
     DT_PAGE_LENGTH (15) · DT_LENGTH_CHANGE=false (sin «Mostrar N filas») ·
     DT_SEARCH_SLOT (selector: mueve el buscador de DataTables a ese hueco de la barra) ·
     DT_CARD_DEFAULT_IMG (imagen de tarjeta cuando no hay portada) · row.card_sub (subtítulo) ·
     DT_PAGING_TOP_BOTTOM=true (info + paginación arriba y abajo) · DT_CARDS_INSIDE=true
     (las tarjetas dentro del contenedor, entre la tabla y los controles de abajo). */
(function () {
  "use strict";
  var $ = window.jQuery;
  var tableEl = document.getElementById("dt");
  if (!$ || !tableEl) return;

  var ncols = window.DT_NCOLS || 0;
  var ths = tableEl.querySelectorAll("thead th");
  var bulk = window.DT_BULK === true;   // selector de filas: la lista pinta un <th class="th-sel"> DELANTE
  var conId = window.DT_ID === true;    // panel: columna Id (pk) visible y exportable, tras el selector
  var desfase = (bulk ? 1 : 0) + (conId ? 1 : 0);   // …así que la cabecera de la columna c0 va después
  var columns = [];
  for (var i = 0; i < ncols; i++) {
    var col = { data: "c" + i };
    // La clase la decide el <th> que pintó la vista (p. ej. col-stat en las
    // booleanas: Activo, Staff…) y se propaga a las celdas de esa columna.
    var th = ths[i + desfase];
    if (th && th.className) col.className = th.className;
    // Prioridad responsive declarada en la Data (`priority`): sin JS por entidad, como quería Poseidón
    if (th && th.dataset.priority) col.responsivePriority = parseInt(th.dataset.priority, 10);
    if (th && th.dataset.orderable === "false") col.orderable = false;   // celdas compuestas sin campo (la Data: no_order)
    columns.push(col);
  }
  // Columna de acciones: la página la apaga con window.DT_NO_ACTIONS (p. ej. Mi
  // actividad, donde no hay nada que hacer por fila y solo dejaba espacio muerto).
  if (window.DT_NO_ACTIONS !== true) {
    columns.push({ data: "acciones", orderable: false, searchable: false, className: "td-actions", responsivePriority: 1 });   // nunca se pliega
  }
  // Id (pk): VISIBLE siempre en las listas de gestión, manda el orden inicial y SIEMPRE se exporta.
  if (conId) {
    columns.unshift({ data: "id", searchable: false, className: "td-id", responsivePriority: 2 });   // siempre visible: no se pliega antes que los datos
  }
  // Selector de filas (acción masiva): columna de checkboxes delante de todo.
  if (bulk) {
    columns.unshift({ data: "id", orderable: false, searchable: false, className: "td-sel", responsivePriority: 1, render: function (id) {
      return '<input type="checkbox" class="dt-sel" value="' + id + '" aria-label="Seleccionar">';
    } });
  }

  var L = window.DT_LANG || {};
  var table = $("#dt").DataTable({
    serverSide: true,
    processing: true,
    responsive: true,
    // Panel de filtros (#dt-filtros, lo pinta list.html): sus valores van en cada petición al endpoint.
    ajax: { url: tableEl.dataset.url, data: function (d) {
      var form = document.getElementById("dt-filtros");
      if (!form) return;
      new FormData(form).forEach(function (v, k) { if (v) d[k] = v; });   // multi = "1,5,9" (lo arma la mini-lista)
    } },
    columns: columns,
    // Orden inicial: en el panel por Id DESCENDENTE (lo último creado arriba); sin Id, la primera columna
    // de datos ascendente. La página puede fijar otro con window.DT_ORDER.
    order: window.DT_ORDER || (conId ? [[bulk ? 1 : 0, "desc"]] : [[desfase, "asc"]]),
    pagingType: "full_numbers",
    pageLength: window.DT_PAGE_LENGTH || 15,
    lengthChange: window.DT_LENGTH_CHANGE !== false,
    lengthMenu: [10, 15, 25, 50, 100],
    // Textos: los pone la plantilla en window.DT_LANG (traducidos con {% trans %});
    // si no vienen, quedan los de abajo en español.
    language: {
      processing: L.processing || "Procesando…",
      search: L.search || "Buscar:",
      searchPlaceholder: L.searchPlaceholder || "Buscar…",
      lengthMenu: L.lengthMenu || "Mostrar _MENU_ filas",
      info: L.info || "Mostrando _START_–_END_ de _TOTAL_",
      infoEmpty: L.infoEmpty || "Sin registros",
      infoFiltered: L.infoFiltered || "(filtrado de _MAX_)",
      zeroRecords: L.zeroRecords || "Sin coincidencias",
      emptyTable: L.emptyTable || "Sin registros todavía",
      paginate: { first: "«", previous: "‹", next: "›", last: "»" },
      // Aviso de «Copiar» (Buttons): en español; el estilo lo pone .dt-button-info (datatables-theme.css)
      buttons: {
        copyTitle: "Copiado al portapapeles",
        copySuccess: { _: "%d filas copiadas", 1: "1 fila copiada" },
        copyKeys: "Pulsa Ctrl o ⌘ + C para copiar la tabla al portapapeles.<br><br>Para cancelar, haz clic en este aviso o pulsa Esc.",
      },
    },
    layout: (function () {
      var topEnd = null;
      // «Mostrar N filas»: junto a los botones de la lista (Copiar, CSV…); si no hay botones, junto a Buscar
      var conLength = window.DT_LENGTH_CHANGE !== false;
      if (conLength && window.DT_BUTTONS === false) topEnd = { pageLength: {} };
      var layout = {
        topStart: { search: {} },  // 2ª fila arriba: el buscador a la IZQUIERDA (sin el «Mostrar N filas» suelto)
        topEnd: topEnd,
        top1Start: null,           // 1ª fila arriba: botones (Copiar, CSV…) a la izquierda + paginación a la derecha
        top1End: { paging: {} },   // («Mostrando x de N» solo abajo, con su paginación)
      };
      // Botones de exportación (Copiar/CSV/Excel/…): solo si la página no los
      // apaga (las listas del USUARIO ponen window.DT_BUTTONS = false).
      if (window.DT_BUTTONS !== false) {
        layout.top1Start = {
          // Exportar: SIN el selector de filas ni la columna Acciones; el Id va SIEMPRE, aunque esté oculto en pantalla.
          buttons: [
            // Solo icono (el texto va en el tooltip) para ahorrar espacio; «Columnas» y «Mostrar» conservan el texto.
            { extend: "copy", text: '<i class="bi bi-clipboard"></i> ' + (L.copy || "Copiar"), titleAttr: L.copy || "Copiar", exportOptions: { columns: ".td-id, :visible:not(.td-actions):not(.td-sel)" } },
            // CSV para Excel en español: BOM (si no, «Sí» sale «SÃ­») y punto y coma como separador (si no, toda la fila cae en la columna A).
            { extend: "csv", text: '<i class="bi bi-filetype-csv"></i> CSV', titleAttr: "CSV", bom: true, charset: "utf-8", fieldSeparator: ";", extension: ".csv",
              exportOptions: { columns: ".td-id, :visible:not(.td-actions):not(.td-sel)" } },
            { extend: "excel", text: '<i class="bi bi-file-earmark-spreadsheet"></i> Excel', titleAttr: "Excel", exportOptions: { columns: ".td-id, :visible:not(.td-actions):not(.td-sel)" } },
            { extend: "pdfHtml5", text: '<i class="bi bi-file-earmark-pdf"></i> PDF', titleAttr: "PDF", orientation: "landscape", pageSize: "A4",
              exportOptions: { columns: ".td-id, :visible:not(.td-actions):not(.td-sel)" },
              customize: function (doc) {   // tabla a todo el ancho, cabecera con el acento y filas alternas suaves
                doc.defaultStyle.fontSize = 9; doc.styles.tableHeader.fontSize = 9; doc.styles.tableHeader.fillColor = "#0b6e7a"; doc.styles.tableHeader.color = "#ffffff";
                var t = doc.content[doc.content.length - 1].table; if (t) { t.widths = t.body[0].map(function () { return "*"; }); }
              } },
            { extend: "print", text: '<i class="bi bi-printer"></i> ' + (L.print || "Imprimir"), titleAttr: L.print || "Imprimir", exportOptions: { columns: ".td-id, :visible:not(.td-actions):not(.td-sel)" } },
            { extend: "colvis", text: '<i class="bi bi-layout-three-columns"></i> ' + (L.colvis || "Columnas"), columns: ":not(.td-actions):not(.td-sel)" },
          ],
        };
        // «Mostrar N filas» como UN botón más de la barra (estándar con los demás), no un <select> suelto
        if (conLength) layout.top1Start.buttons.push({ extend: "pageLength", text: '<i class="bi bi-list-ol"></i> ' + (L.show || "Mostrar") });
        // «Tipo»: lista «by» por tipo (ByTypeMixin). Un botón más de la barra; al abrirlo, un buscador filtra los tipos.
      } else {
        // Modo público / usuario (sin exportación): el BUSCADOR a la izquierda de la 2ª fila,
        // como en gestión; la info + paginación abajo (DataTables fusiona con sus defaults,
        // así que hay que anular los slots duplicados explícitamente).
        layout.topStart = { search: {} };
        if (window.DT_PAGING_TOP_BOTTOM !== true) {   // público: info + paginación también arriba
          layout.top1Start = null;
          layout.top1End = null;
        }
      }
      return layout;
    })(),
  });

  // Botón «Filtros»: muestra u oculta el panel (como en las listas públicas); recuerda tu elección
  // por entidad y se abre solo si la página llegó con filtros en la URL.
  // Recargar (↻), JUSTO ANTES del buscador, en gestión y en público: la MISMA página, orden, búsqueda y filtros
  // aplicados (ajax.reload sin volver a la página 1).
  var btnRecargar = document.createElement("button");
  btnRecargar.type = "button"; btnRecargar.className = "btn-recargar"; btnRecargar.title = "Recargar datos";
  btnRecargar.setAttribute("aria-label", "Recargar datos");
  btnRecargar.innerHTML = '<i class="bi bi-arrow-clockwise"></i>';
  var cajaBuscar = table.table().container().querySelector(".dt-search");
  if (cajaBuscar) cajaBuscar.insertBefore(btnRecargar, cajaBuscar.firstChild);
  var recargar = function () {
    btnRecargar.classList.add("girando");
    table.ajax.reload(function () { btnRecargar.classList.remove("girando"); }, false);
  };
  btnRecargar.addEventListener("click", recargar);

  // Auto-recarga (window.DT_AUTORECARGA = segundos): tras cada respuesta, si la Data dice que hay trabajo en curso
  // («activas» > 0, p. ej. Tareas en cola o corriendo) se programa otra; cuando no queda nada, se detiene sola.
  var cadaSeg = parseInt(window.DT_AUTORECARGA || 0, 10), temporizador = null;
  if (cadaSeg > 0) {
    table.on("xhr.dt", function (e, settings, json) {
      clearTimeout(temporizador);
      var activas = json && typeof json.activas === "number" ? json.activas : 0;
      btnRecargar.classList.toggle("en-vivo", activas > 0);
      btnRecargar.title = activas > 0 ? "Actualizando cada " + cadaSeg + " s (" + activas + " en curso)" : "Recargar datos";
      if (activas > 0 && !document.hidden) temporizador = setTimeout(recargar, cadaSeg * 1000);
    });
    document.addEventListener("visibilitychange", function () { if (!document.hidden && btnRecargar.classList.contains("en-vivo")) recargar(); });
  }

  var panel = document.getElementById("panel-filtros");
  var btnPanel = document.getElementById("btn-panel-filtros");
  var layout = document.querySelector(".list-layout");
  if (panel && btnPanel) {
    var PKEY = "dt-filtros:" + (window.DT_ENTITY || "");
    var abierto = window.DT_FILTROS_ABIERTO === true;
    try { var g = localStorage.getItem(PKEY); if (g !== null) abierto = g === "1" || abierto; } catch (e) {}
    var pintar = function (abre) {
      panel.hidden = !abre;
      if (layout) layout.classList.toggle("list-layout--solo", !abre);
      btnPanel.classList.toggle("f-activos", abre);
    };
    pintar(abierto);
    btnPanel.addEventListener("click", function () {
      var abre = panel.hidden;
      pintar(abre);
      try { localStorage.setItem(PKEY, abre ? "1" : "0"); } catch (e) {}
    });
  }

  // Panel de filtros: al cambiar, recarga la tabla y deja los filtros en la URL (para compartirla).
  var filtrosForm = document.getElementById("dt-filtros");
  if (filtrosForm) {
    // Cada filtro es colapsable (<details>): en su cabecera va el RESUMEN de lo elegido (nombre de la opción,
    // «2 ✓»…), para leer el panel de un vistazo sin abrir nada.
    var TODO_TXT = "Todo";
    var resumir = function () {
      filtrosForm.querySelectorAll(".fl-item").forEach(function (it) {
        var res = it.querySelector(".fl-resumen"); if (!res) return;
        var sel = it.querySelector("select"), dd = it.querySelector(".fl-dd");
        if (sel) { res.textContent = sel.value ? sel.options[sel.selectedIndex].textContent : ""; }
        else if (dd) { var t = dd.querySelector(".fl-dd__texto").textContent; res.textContent = dd.classList.contains("fl-dd--activo") ? t : ""; }
      });
    };
    // Desplegables multi (países, géneros, años…): cerrado muestra lo elegido; abierto, buscador + casillas.
    // Las casillas marcadas se juntan en su hidden como "1,5,9"; el buscador solo oculta opciones.
    var dds = filtrosForm.querySelectorAll(".fl-dd");
    var TODO = (document.querySelector(".fl-dd__texto") || {}).textContent || "Todo";
    dds.forEach(function (dd) {
      var btn = dd.querySelector(".fl-dd__btn"), menu = dd.querySelector(".fl-dd__menu");
      var texto = dd.querySelector(".fl-dd__texto"), hidden = dd.querySelector('input[type="hidden"]');
      var buscar = dd.querySelector(".fl-dd__buscar");
      var pintar = function () {
        var marcados = [], etiquetas = [];
        dd.querySelectorAll('input[type="checkbox"]:checked').forEach(function (c) {
          marcados.push(c.value); etiquetas.push(c.parentNode.querySelector("span").textContent);
        });
        hidden.value = marcados.join(",");
        texto.textContent = etiquetas.length === 0 ? TODO : etiquetas.length <= 2 ? etiquetas.join(", ") : etiquetas.length + " ✓";
        dd.classList.toggle("fl-dd--activo", marcados.length > 0);
        resumir();
      };
      pintar();
      btn.addEventListener("click", function () {
        var abre = menu.hidden;
        dds.forEach(function (o) { o.querySelector(".fl-dd__menu").hidden = true; o.querySelector(".fl-dd__btn").setAttribute("aria-expanded", "false"); });
        menu.hidden = !abre; btn.setAttribute("aria-expanded", abre ? "true" : "false");
        if (abre) { buscar.value = ""; buscar.dispatchEvent(new Event("input")); buscar.focus(); }
      });
      dd.addEventListener("change", function (ev) {
        if (ev.target.type !== "checkbox") return;
        pintar();
      });
      buscar.addEventListener("input", function () {
        var q = buscar.value.trim().toLowerCase();
        dd.querySelectorAll(".fl-dd__op").forEach(function (op) { op.hidden = q !== "" && op.textContent.toLowerCase().indexOf(q) < 0; });
      });
    });
    filtrosForm.addEventListener("change", function (ev) { if (ev.target.tagName === "SELECT") resumir(); });
    resumir();
    document.addEventListener("click", function (ev) {   // clic fuera → se cierran
      dds.forEach(function (dd) { if (!dd.contains(ev.target)) { dd.querySelector(".fl-dd__menu").hidden = true; dd.querySelector(".fl-dd__btn").setAttribute("aria-expanded", "false"); } });
    });
    // Filtrado INMEDIATO: al marcar una casilla o elegir en un select se recarga la tabla (sin botón «Filtrar»).
    // Los filtros NO se escriben en la URL de la página: viajan solo en la petición al DataView.
    // «Quitar filtros» aparece solo si hay algo puesto; el panel muestra cuántas filas quedaron.
    var btnQuitar = document.getElementById("btn-quitar-filtros"), cuentaEl = document.getElementById("fl-resultados");
    var aplicados = false;
    var hayValores = function () {
      var hay = false; new FormData(filtrosForm).forEach(function (v) { if (v) hay = true; }); return hay;
    };
    var pintarQuitar = function () { if (btnQuitar) btnQuitar.hidden = !aplicados; };
    aplicados = hayValores(); pintarQuitar();   // la página puede llegar con filtros (vistas «por»)
    // TIPO (navegación): uno marcado → esa lista «por» (URL + fondo); dos o más → lista general con ?campo=a,b
    // (fondo genérico, el filtro lo aplica la Data); ninguno → «Todos». Devuelve true si hubo que navegar.
    var navegarTipo = function () {
      var enPor = !!(window.DT_TIPO_ACTUAL);
      var salir = null;
      filtrosForm.querySelectorAll(".fl-nav").forEach(function (nav) {
        var marcados = Array.prototype.filter.call(nav.querySelectorAll('input[type="checkbox"]'), function (c) { return c.checked; });
        var hidden = nav.querySelector('input[type="hidden"]');
        var actual = enPor && window.DT_TIPO_ACTUAL.tipo === nav.dataset.nav ? window.DT_TIPO_ACTUAL.valor : "";
        if (marcados.length === 1) {
          hidden.value = "";
          if (marcados[0].value !== actual) salir = salir || marcados[0].dataset.href;
        } else if (marcados.length === 0) {
          hidden.value = "";
          if (actual) salir = salir || nav.dataset.lista;
        } else {
          var valores = marcados.map(function (c) { return c.value; }).join(",");
          if (actual) salir = salir || (nav.dataset.lista + "?" + nav.dataset.campo + "=" + encodeURIComponent(valores));
          hidden.value = valores;
        }
      });
      if (salir) { window.location.href = salir; return true; }
      return false;
    };
    var esperar = null;
    var aplicar = function () {                 // se llama al cambiar cualquier filtro; agrupa cambios seguidos
      clearTimeout(esperar);
      esperar = setTimeout(function () {
        if (navegarTipo()) return;              // TIPO: una sola opción lleva a su lista «por»
        aplicados = hayValores(); pintarQuitar(); table.ajax.reload();
      }, 250);
    };
    filtrosForm.addEventListener("change", aplicar);
    // «N resultados» del panel: lo que devuelve la Data en cada respuesta
    table.on("xhr.dt", function (e, settings, json) {
      if (!cuentaEl || !json) return;
      var n = json.recordsFiltered;
      cuentaEl.textContent = n === 1 ? "1 resultado" : n.toLocaleString("es") + " resultados";
    });
    // Valores que llegan por la URL (?type=OP,ED) al volver de una «por»: los manda al DataView desde el arranque
    filtrosForm.querySelectorAll(".fl-nav").forEach(function (nav) {
      var marcados = Array.prototype.filter.call(nav.querySelectorAll('input[type="checkbox"]'), function (c) { return c.checked; });
      if (marcados.length >= 2) nav.querySelector('input[type="hidden"]').value = marcados.map(function (c) { return c.value; }).join(",");
    });
    if (btnQuitar) btnQuitar.addEventListener("click", function () {
      filtrosForm.querySelectorAll("select").forEach(function (s) { s.value = ""; });
      filtrosForm.querySelectorAll('.fl-dd input[type="checkbox"]').forEach(function (c) { c.checked = false; });
      filtrosForm.querySelectorAll('.fl-dd input[type="hidden"]').forEach(function (h) { h.value = ""; });
      filtrosForm.querySelectorAll(".fl-dd").forEach(function (dd) {   // repintar el texto de cada desplegable
        var c = dd.querySelector('input[type="checkbox"]'); if (c) c.dispatchEvent(new Event("change", { bubbles: true }));
      });
      resumir(); aplicados = false; pintarQuitar(); table.ajax.reload();
      if (cuentaEl) cuentaEl.classList.remove("cargando");
    });
  }

  window.DT_TABLE = table;   // la página puede actuar sobre la tabla (p. ej. cantidad por página)

  // --- Selección de filas + barra masiva («N seleccionadas · acción · Aplicar») ---
  if (bulk) {
    var sel = {};                      // id → true (sobrevive a cambiar de página)
    var form = document.getElementById("bulk-form");
    var nEl = document.getElementById("bulk-n");
    var idsEl = document.getElementById("bulk-ids");
    var all = document.getElementById("dt-sel-all");
    function boxes() { return Array.prototype.slice.call(tableEl.querySelectorAll("tbody .dt-sel")); }
    function count() { return Object.keys(sel).length; }
    function paint() {
      var n = count();
      if (nEl) nEl.textContent = n;
      if (form) form.hidden = n === 0;
      if (idsEl) idsEl.value = Object.keys(sel).join(",");
      if (all) { var b = boxes(); all.checked = b.length > 0 && b.every(function (x) { return sel[x.value]; }); }
    }
    tableEl.addEventListener("change", function (e) {
      var b = e.target.closest && e.target.closest(".dt-sel");
      if (!b) return;
      if (b.checked) sel[b.value] = true; else delete sel[b.value];
      paint();
    });
    if (all) all.addEventListener("change", function () {
      boxes().forEach(function (b) { b.checked = all.checked; if (all.checked) sel[b.value] = true; else delete sel[b.value]; });
      paint();
    });
    table.on("draw", function () { boxes().forEach(function (b) { b.checked = !!sel[b.value]; }); paint(); });
    var clear = document.getElementById("bulk-clear");
    if (clear) clear.addEventListener("click", function () { sel = {}; boxes().forEach(function (b) { b.checked = false; }); paint(); });
    if (form) form.addEventListener("submit", function (e) {
      var acc = document.getElementById("bulk-accion");
      if (form.dataset.ok === "1" || !acc || acc.value !== "eliminar" || !window.artNotify) return;
      e.preventDefault();
      window.artNotify.confirm({ title: "¿Eliminar " + count() + " registro(s)?", text: "Esta acción no se puede deshacer.", confirmButtonText: "Sí, eliminar" })
        .then(function (r) { if (r.isConfirmed) { form.dataset.ok = "1"; form.submit(); } });
    });
  }

  // ---- Buscador en la BARRA de la página (listas públicas): se muda el control de
  // DataTables al hueco indicado; sigue siendo la búsqueda server-side de siempre.
  if (window.DT_SEARCH_SLOT) {
    var slot = document.querySelector(window.DT_SEARCH_SLOT);
    var buscador = document.querySelector(".dt-search");
    if (slot && buscador) slot.appendChild(buscador);
  }

  // ---- Selector de acciones por fila (menú ⋯) ----
  function closeMenus(except) {
    document.querySelectorAll(".row-menu.open").forEach(function (m) {
      if (m !== except) {
        m.classList.remove("open");
        var b = m.querySelector(".row-menu__btn");
        if (b) b.setAttribute("aria-expanded", "false");
      }
    });
  }
  function placeMenu(menu, btn) {
    var list = menu.querySelector(".row-menu__list");
    if (!list) return;
    var r = btn.getBoundingClientRect();
    var w = list.offsetWidth, h = list.offsetHeight, gap = 4;
    var left = r.right - w;                       // alineado a la derecha del botón
    if (left < 8) left = 8;
    var top = r.bottom + gap;                     // por defecto: abajo
    if (top + h > window.innerHeight - 8) {       // no cabe abajo → arriba
      var up = r.top - gap - h;
      if (up >= 8) top = up;
      else top = Math.max(8, window.innerHeight - h - 8);
    }
    list.style.left = Math.round(left) + "px";
    list.style.top = Math.round(top) + "px";
  }
  document.addEventListener("click", function (e) {
    var btn = e.target.closest ? e.target.closest(".row-menu__btn") : null;
    if (btn) {
      e.preventDefault();
      var menu = btn.parentNode;
      var willOpen = !menu.classList.contains("open");
      closeMenus(menu);
      menu.classList.toggle("open", willOpen);
      btn.setAttribute("aria-expanded", willOpen ? "true" : "false");
      if (willOpen) placeMenu(menu, btn);         // posicionar tras mostrar (ya tiene tamaño)
      return;
    }
    if (!(e.target.closest && e.target.closest(".row-menu__list"))) closeMenus(null);
  });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape") closeMenus(null); });
  // el menú es fixed: al desplazar/redimensionar quedaría desfasado → cerrarlo
  window.addEventListener("scroll", function () { closeMenus(null); }, true);
  window.addEventListener("resize", function () { closeMenus(null); });

  // ---- Toggle cards/lista ----
  var cardsGrid = document.getElementById("cards-grid");
  var btnTable = document.getElementById("view-table");
  var btnCards = document.getElementById("view-cards");
  if (!window.CARDS_ENABLED || !cardsGrid || !btnTable || !btnCards) return;

  var STORE = "dt-view-" + (window.DT_ENTITY || "x");
  if (window.DT_CARDS_INSIDE === true) {
    // público: la cuadrícula de tarjetas va DENTRO del contenedor, justo tras la tabla,
    // para que la info y la paginación de abajo queden debajo de las tarjetas.
    tableEl.parentNode.insertBefore(cardsGrid, tableEl.nextSibling);
  }

  function buildCard(row) {
    var a = document.createElement("a");
    a.className = "card"; a.href = row.detail_url || "#";
    var ic = document.createElement("div"); ic.className = "card-image-container";
    if (row.card_image || window.DT_CARD_DEFAULT_IMG) {
      var img = document.createElement("img");
      img.src = row.card_image || window.DT_CARD_DEFAULT_IMG; img.alt = row.card_title || ""; img.loading = "lazy";
      ic.appendChild(img);
    } else {
      var b = document.createElement("div"); b.className = "card-initial-badge";
      b.textContent = (row.card_title || "?").replace(/&[^;]+;/g, "").charAt(0).toUpperCase();
      ic.appendChild(b);
    }
    var t = document.createElement("div"); t.className = "card-title";
    t.innerHTML = row.card_title || "";     // ya viene escapado del server
    a.appendChild(ic); a.appendChild(t);
    if (row.card_sub) {
      var sb = document.createElement("div"); sb.className = "card-sub"; sb.textContent = row.card_sub;
      a.appendChild(sb);
    }
    if (row.card_actions) {
      // Pie de ACCIONES de la tarjeta (HTML del server: estado, enlaces…). Los clics
      // dentro no deben abrir la ficha: la tarjeta entera es un <a>.
      var f = document.createElement("div"); f.className = "card-actions";
      f.innerHTML = row.card_actions;
      // preventDefault evita que la <a> de la tarjeta navegue; el evento sigue subiendo
      // para que los manejadores de la página (estado en línea, modal de enlaces) actúen.
      f.addEventListener("click", function (e) {
        // solo navegan los enlaces DEL PIE (p. ej. Editar); la <a> de la tarjeta no
        var a = e.target.closest("a[href]");
        if (!a || !f.contains(a)) e.preventDefault();
      });
      a.appendChild(f);
    }
    return a;
  }

  function renderCards(data) {
    cardsGrid.innerHTML = "";
    (data || []).forEach(function (r) { cardsGrid.appendChild(buildCard(r)); });
  }

  var wrap = tableEl.closest(".dt-container") || tableEl.parentNode;
  function applyMode(mode) {
    if (mode === "cards") {
      tableEl.style.display = "none"; cardsGrid.style.display = "grid";
      btnCards.classList.add("active"); btnTable.classList.remove("active");
    } else {
      tableEl.style.display = ""; cardsGrid.style.display = "none";
      btnTable.classList.add("active"); btnCards.classList.remove("active");
    }
    // En tarjetas los botones de exportar/columnas no tienen sentido: solo queda «Mostrar» (CSS)
    if (wrap) wrap.classList.toggle("dt-container--cards", mode === "cards");
    try { localStorage.setItem(STORE, mode); } catch (e) {}
  }

  table.on("draw", function () {
    var j = table.ajax.json();
    renderCards(j && j.data);
  });
  btnTable.addEventListener("click", function () { applyMode("table"); });
  btnCards.addEventListener("click", function () { applyMode("cards"); });

  var saved = "table";
  try { saved = localStorage.getItem(STORE) || window.DT_VIEW_DEFAULT || "table"; } catch (e) {}
  applyMode(saved);
})();

// Buscador dentro del desplegable «Tipo» (se inyecta al abrir la colección)
document.addEventListener("click", function (e) {
  var btn = e.target.closest && e.target.closest(".dt-type");
  if (!btn) return;
  setTimeout(function () {
    var col = document.querySelector(".dt-button-collection");
    if (!col || col.querySelector(".dt-type-search")) return;
    var inp = document.createElement("input");
    inp.type = "search"; inp.className = "dt-type-search"; inp.placeholder = "Buscar tipo…"; inp.autocomplete = "off";
    col.insertBefore(inp, col.firstChild); inp.focus();
    inp.addEventListener("input", function () {
      var q = inp.value.toLowerCase();
      col.querySelectorAll(".dt-button").forEach(function (b) { b.style.display = b.textContent.toLowerCase().indexOf(q) >= 0 ? "" : "none"; });
    });
    inp.addEventListener("click", function (ev) { ev.stopPropagation(); });
  }, 0);
});
