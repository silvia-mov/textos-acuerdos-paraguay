/* Común a las páginas de cada acuerdo: buscador en los textos (textos.json) y buscador de productos (opcional). */
const esc = s => String(s).replace(/[&<>"]/g, c => ({"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;"}[c]));
const sinT = s => s.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();
const fmt = n => n.toLocaleString("es-PY");

(function () {
  const q = document.getElementById("q-txt");
  if (!q) return;
  let T = [], t0;
  fetch("textos.json").then(r => r.json()).then(d => { T = d; });
  q.addEventListener("input", e => { clearTimeout(t0); t0 = setTimeout(() => buscar(e.target.value), 200); });
  function buscar(v) {
    const out = document.getElementById("r-txt"), qq = sinT(v.trim());
    if (qq.length < 3) { out.innerHTML = ""; return; }
    const res = [];
    T.forEach(d => {
      const plano = sinT(d.texto); let i = plano.indexOf(qq), n = 0; const frag = [];
      while (i >= 0 && n < 50) { if (frag.length < 3) frag.push(i); n++; i = plano.indexOf(qq, i + qq.length); }
      if (n) res.push({d, n, frag});
    });
    res.sort((a, b) => b.n - a.n);
    out.innerHTML = res.length ? `<p class="chica">${res.length} documentos.</p>` + res.slice(0, 15).map(({d, n, frag}) =>
      `<div class="r"><a href="textos/${d.id}.txt"><b>${esc(d.titulo)}</b></a> <span class="chica">· ${n}${n === 50 ? "+" : ""} veces</span>` +
      frag.map(i => {
        const a = Math.max(0, i - 110), s = d.texto.slice(a, i + qq.length + 110).replace(/\s+/g, " ");
        const p = sinT(s).indexOf(qq);
        return `<div class="det">…${esc(s.slice(0, p))}<mark>${esc(s.slice(p, p + qq.length))}</mark>${esc(s.slice(p + qq.length))}…</div>`;
      }).join("") + "</div>").join("") : '<p class="chica">No aparece en los textos.</p>';
  }
})();

/* Buscador de productos: window.PRODUCTOS = {archivo, columnas: [títulos], fila: r => [celdas HTML]}; código en r[0], descripción en r[1]. */
(function () {
  const cfg = window.PRODUCTOS, q = document.getElementById("q-prod");
  if (!cfg || !q) return;
  let P = [], t0;
  fetch(cfg.archivo).then(r => r.json()).then(d => { P = d; if (cfg.listo) cfg.listo(d); });
  q.addEventListener("input", e => { clearTimeout(t0); t0 = setTimeout(() => buscar(e.target.value), 150); });
  function buscar(v) {
    const t = document.getElementById("t-prod"), qq = sinT(v.trim());
    if (qq.length < 3) { t.innerHTML = ""; return; }
    const dig = qq.replace(/\D/g, ""), esCod = /^\d[\d.\s]*$/.test(qq);
    const res = P.filter(r => esCod ? r[0].replace(/\D/g, "").startsWith(dig) : sinT(r[1]).includes(qq)).slice(0, 80);
    t.innerHTML = res.length ? "<thead><tr>" + cfg.columnas.map(c => `<th>${c}</th>`).join("") + "</tr></thead><tbody>" +
      res.map(r => "<tr>" + cfg.fila(r).map((c, i) => `<td${i === 0 ? ' class="cod"' : ""}>${c}</td>`).join("") + "</tr>").join("") + "</tbody>"
      : '<tbody><tr><td class="chica">No hay productos con esa búsqueda.</td></tr></tbody>';
    if (res.length === 80) t.insertAdjacentHTML("beforeend", '<caption class="chica" style="caption-side:bottom;text-align:left">Se muestran los primeros 80. Escribí algo más preciso.</caption>');
  }
})();
