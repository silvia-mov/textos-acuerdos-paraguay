/* Botón Claro / Oscuro: la página recuerda la elección (si el navegador lo permite). */
(function () {
  var r = document.documentElement;
  var b = document.createElement("button");
  b.type = "button"; b.className = "boton-tema";
  var st = document.createElement("style");
  st.textContent = ".boton-tema{position:fixed;top:10px;right:12px;z-index:50;font:600 13px/1 'Source Sans 3',system-ui,sans-serif;padding:8px 12px;border-radius:99px;border:1px solid var(--line,#ccc);background:var(--panel,#fff);color:var(--text,#222);cursor:pointer;box-shadow:0 1px 4px rgba(0,0,0,.12)}@media print{.boton-tema{display:none}}@media (min-width:701px){.aviso-top{padding-right:150px!important;padding-left:150px!important}}@media (max-width:700px){.boton-tema{top:6px;right:8px;font-size:12px;padding:6px 9px}.aviso-top{padding-right:108px!important;text-align:left!important}}";
  document.head.appendChild(st);
  function sistema() { return matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light"; }
  function aplicar(t) {
    if (t) r.setAttribute("data-theme", t); else r.removeAttribute("data-theme");
    var ef = t || sistema();
    document.querySelectorAll('picture source[media*="prefers-color-scheme"], picture source[data-orig]').forEach(function (s) {
      if (!s.dataset.orig) s.dataset.orig = s.media;
      s.media = t ? (ef === "dark" ? "all" : "not all") : s.dataset.orig;
    });
    b.textContent = ef === "dark" ? "Modo claro" : "Modo oscuro";
    b.setAttribute("aria-label", ef === "dark" ? "Cambiar a modo claro" : "Cambiar a modo oscuro");
  }
  var guardado = null;
  try { guardado = localStorage.getItem("tema"); } catch (e) {}
  aplicar(guardado === "light" || guardado === "dark" ? guardado : null);
  b.addEventListener("click", function () {
    var nuevo = (r.getAttribute("data-theme") || sistema()) === "dark" ? "light" : "dark";
    try { localStorage.setItem("tema", nuevo); } catch (e) {}
    aplicar(nuevo);
  });
  document.body.appendChild(b);
})();

/* Datawrapper: alto automático y modo claro/oscuro sincronizado con el botón de la página */
(function () {
  window.addEventListener("message", function (e) {
    var h = e.data && e.data["datawrapper-height"]; if (!h) return;
    document.querySelectorAll("iframe.dw-embed").forEach(function (f) { if (f.contentWindow === e.source) for (var k in h) f.style.height = h[k] + "px"; });
  });
  var mq = window.matchMedia("(prefers-color-scheme: dark)");
  function oscuro() { var t = document.documentElement.getAttribute("data-theme"); return t ? t === "dark" : mq.matches; }
  function aplicar() {
    var d = oscuro();
    document.querySelectorAll("iframe.dw-embed").forEach(function (f) {
      var u = f.getAttribute("data-dw") + "?dark=" + d; if (f.getAttribute("src") !== u) f.setAttribute("src", u);
    });
  }
  new MutationObserver(aplicar).observe(document.documentElement, { attributes: true, attributeFilter: ["data-theme"] });
  if (mq.addEventListener) mq.addEventListener("change", aplicar);
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", aplicar); else aplicar();
})();
