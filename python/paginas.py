"""Genera las páginas de cada acuerdo (docs/aceNN/index.html), la portada (docs/index.html) y el sitemap.

El contenido que Google tiene que leer (resumen, fechas, disposiciones para Paraguay, lista de documentos) se escribe
en el HTML; los buscadores (texto y productos) cargan los JSON de cada carpeta.
Uso: python3 python/paginas.py   (la página del ACE 72 es aparte: docs/ace72/index.html)
"""
import html
import json
from pathlib import Path

import pandas as pd

import uso

RAIZ = Path(__file__).resolve().parent.parent
DOCS = RAIZ / "docs"
URL = "https://silvia-mov.github.io/textos-acuerdos-paraguay/"
e = html.escape


def productos_json():
    """JSON livianos para los buscadores de productos."""
    d = pd.read_csv(DOCS / "ace58/tablas/preferencias_paraguay_peru.csv", dtype=str).fillna("")
    (DOCS / "ace58/preferencias.json").write_text(json.dumps(d.values.tolist(), ensure_ascii=False), encoding="utf-8")
    g = pd.read_csv(DOCS / "ace35/tablas/requisitos_especificos_origen.csv", dtype=str).fillna("")
    p = pd.read_csv(DOCS / "ace35/tablas/origen_diferenciado_paraguay_a_chile.csv", dtype=str).fillna("")
    filas = [[r.NALADISA_2012, r.DESCRIPCION, r.OBSERVACIONES, r.REQUISITO_ESPECIFICO, "Todas las Partes (Apéndice 1)"]
             for r in g.itertuples()]
    filas += [[r.NALADISA_2012, r.DESCRIPCION, "", r.REQUISITO_DE_ORIGEN, "Paraguay a Chile (Apéndice 2)"]
              for r in p.itertuples() if r.REQUISITO_DE_ORIGEN]
    (DOCS / "ace35/origen.json").write_text(json.dumps(filas, ensure_ascii=False), encoding="utf-8")
    return len(d), len(filas)


def lista_documentos(carpeta, orden):
    cat = pd.read_csv(DOCS / carpeta / "catalogo.csv", dtype=str).fillna("")
    out = []
    for g in orden:
        ds = cat[cat.GRUPO == g]
        if ds.empty:
            continue
        li = []
        for r in ds.itertuples():
            meta = " · ".join(x for x in [r.FECHA, f"{r.PAGINAS} pág." if r.PAGINAS else "", "OCR" if r.LECTURA == "OCR" else "",
                                          "lista" if r.LISTA else ""] if x)
            if r.LECTURA.startswith("no transcripta"):
                li.append(f'<li><span>{e(r.TITULO)}</span><span class="m">no transcripta</span></li>')
                continue
            sin = f'<div class="det">{e(r.SINTESIS)}</div>' if r.SINTESIS else ""
            li.append(f'<li><span><a href="textos/{r.ID}.txt">{e(r.TITULO)}</a>{sin}</span><span class="m">{e(meta)}</span></li>')
        abierto = " open" if g == orden[0] else ""
        out.append(f'<details{abierto}><summary>{e(g)} ({len(ds)})</summary><ul class="docs">' + "".join(li) + "</ul></details>")
    return "\n".join(out)


def pagina(a):
    carpeta = a["carpeta"]
    kpis = "".join(f'<div class="kpi"><div class="v">{v}</div><div class="l">{l}</div></div>' for v, l in a["kpis"])
    tl = "".join(f'<li{" class=\"py\"" if py else ""}><div class="f">{f}</div>{t}</li>' for f, t, py in a["linea"])
    disp = "".join(f'<div class="card"><div class="v">{v}</div><h3>{h}</h3><p>{p}</p><div class="src">{s}</div></div>'
                   for v, h, p, s in a["disposiciones"])
    descargas = "".join(f'<li>{t}: <a href="{f}.csv" download>CSV</a> · <a href="{f}.xlsx" download>Excel</a></li>'
                        for t, f in a["descargas"])
    titulos = ""
    if (DOCS / carpeta / "estructura.json").exists():
        est = json.loads((DOCS / carpeta / "estructura.json").read_text(encoding="utf-8"))
        titulos = ('<h2>Qué dice el Acuerdo, título por título</h2><ul class="titulos">' +
                   "".join(f'<li><b>{e(t["titulo"].replace("TÍTULO ", ""))}.</b> {e(t["nombre"])}</li>' for t in est) + "</ul>")
    return f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(a["titulo"])}</title>
<meta name="description" content="{e(a["descripcion"])}">
<link rel="icon" href="../logo.svg" type="image/svg+xml">
<link rel="canonical" href="{URL}{carpeta}/">
<meta property="og:type" content="website">
<meta property="og:locale" content="es_PY">
<meta property="og:title" content="{e(a["titulo"])}">
<meta property="og:description" content="{e(a["descripcion"])}">
<meta property="og:url" content="{URL}{carpeta}/">
<meta property="og:image" content="{URL}img/tarjeta_light.png">
<meta name="twitter:card" content="summary_large_image">
<script>(function(){{try{{var x=localStorage.getItem("tema");if(x==="light"||x==="dark")document.documentElement.setAttribute("data-theme",x);}}catch(e){{}}}})();</script>
<link rel="stylesheet" href="../comun.css">
</head>
<body>
<div class="aviso-top">Proyecto independiente. No representa ni cuenta con el respaldo de la ALADI, del MERCOSUR ni de ningún gobierno.</div>
<header>
  <div class="wrap">
    <p class="migas"><a href="../">← Todos los acuerdos</a></p>
    <div class="marca"><img src="../logo.svg" alt=""><span><b>Textos de los acuerdos comerciales de Paraguay</b><br><small>Ordenados, sin duplicados y buscables</small></span></div>
    <h1>{a["h1"]}</h1>
    <p class="lead">{a["lead"]}</p>
    <div class="kpis">{kpis}</div>
  </div>
</header>
<main class="wrap">
{a.get("antes", "")}
<h2>De la firma al libre comercio</h2>
<ul class="tl">{tl}</ul>

<h2>Disposiciones especiales para Paraguay</h2>
<div class="disp">{disp}</div>
{a.get("uso", "")}
<p class="note">{uso.NOTA}</p>
{a.get("despues_uso", "")}
{a.get("aranceles", "")}
{a.get("productos", "")}
{titulos}
<h2>Buscá en el texto</h2>
<p class="chica">Busca en el Acuerdo, los anexos de texto corrido y los protocolos (no en las listas de productos).</p>
<input type="search" id="q-txt" placeholder="{e(a["ejemplo"])}" aria-label="Buscar en los textos">
<div id="r-txt" class="res"></div>

<h2>Los documentos</h2>
<p class="chica">Cada protocolo lleva su fecha y lo que dispone su primer artículo. Los marcados «OCR» estaban escaneados: su texto puede tener errores de lectura; ante cualquier duda, vale el original de la ALADI.</p>
{lista_documentos(carpeta, a["grupos"])}

<h2>Cómo se armó</h2>
<div class="card">{a["como"]}
<p class="note">Catálogo: <a href="catalogo.csv" download>CSV</a> · <a href="catalogo.xlsx" download>Excel</a>. Código en <a href="https://github.com/silvia-mov/textos-acuerdos-paraguay">GitHub</a>. Los PDF originales no se publican aquí: están en la ALADI ({e(a["sigla"])}).</p>
</div>

<h2>Descargas</h2>
<ul>{descargas}<li>Catálogo de documentos: <a href="catalogo.csv" download>CSV</a> · <a href="catalogo.xlsx" download>Excel</a></li></ul>
</main>
<footer>
  <div class="wrap">Fuente: ALADI (textos oficiales, {e(a["sigla"])}). Código con licencia MIT en <a href="https://github.com/silvia-mov/textos-acuerdos-paraguay">GitHub</a>. Proyecto independiente: no representa ni cuenta con el respaldo de la ALADI, del MERCOSUR ni de ningún gobierno. Más proyectos en <a href="https://silvia-mov.github.io/">silvia-mov.github.io</a>.</div>
</footer>
{a.get("script", "")}
<script src="../acuerdo.js"></script>
<script src="../tema.js"></script>
</body>
</html>
"""


BUSCA = """<h2>Buscá un producto</h2>
<p class="chica">{texto}</p>
<input type="search" id="q-prod" placeholder="Escribí un código o un nombre, por ejemplo: {ej}" aria-label="Buscar un producto">
<div class="tw"><table id="t-prod"></table></div>"""

def vigencia_ace35():
    d = pd.read_csv(Path(__file__).resolve().parent / "datos" / "ace35_vigencia_61_69.csv", dtype=str).fillna("")
    filas = "".join(f'<tr><td>{r.PROTOCOLO}</td><td>{e(r.SINTESIS)}</td><td>{e(r.VIGENCIA_PARAGUAY_CHILE)}</td><td class="chica">{e(r.NORMA_PARAGUAY)}</td><td class="chica">{e(r.OTRAS_VIGENCIAS)}</td></tr>'
                    for r in d.itertuples())
    return ('<h2>Los protocolos recientes: qué rige para Paraguay y desde cuándo</h2>\n'
            '<p class="chica">Fichas de la ALADI de los Protocolos 61 a 69: fecha de entrada en vigor entre Paraguay y Chile y norma con la que Paraguay lo incorporó. '
            '«No corresponde»: el protocolo rige solo entre Chile y otro país.</p>\n'
            '<div class="tw"><table><thead><tr><th>Protocolo</th><th>Qué dispone</th><th>Vigente entre Paraguay y Chile</th><th>Norma de Paraguay</th><th>Otros países</th></tr></thead><tbody>'
            + filas + "</tbody></table></div>")


VIG35 = vigencia_ace35()
ARANCELES_CHILE = """<h2>Qué tan protegido está el mercado de Chile</h2>
<p>Chile tiene uno de los aranceles más bajos y parejos de la región: casi todo paga lo mismo, así que no hay sectores con picos. Con el ACE 35, Paraguay entra con 0 % donde otros países pagan 6 %.</p>
<div class="disp">
<div class="card"><div class="v">6 %</div><h3>Arancel general (NMF) en 2026</h3><p>Lo paga el 99,4 % de los productos (5.572 de 5.604 subpartidas). Promedio simple: 5,98 %.</p><div class="src">OMC, base de datos integrada, SA 2022</div></div>
<div class="card"><div class="v">0 %</div><h3>Las pocas excepciones</h3><p>Solo 32 subpartidas pagan menos de 6 %: sobre todo aeronaves, drones y barcos, y algunos libros e impresos.</p><div class="src">OMC, base de datos integrada</div></div>
<div class="card"><div class="v">31,5 %</div><h3>Techo consolidado en la OMC</h3><p>Chile puede subir hasta 25 % casi todo y hasta 31,5 % lácteos, trigo, harina y semillas oleaginosas, entre otros. Hoy aplica mucho menos.</p><div class="src">OMC, lista de concesiones de Chile</div></div>
<div class="card"><div class="v">98 %</div><h3>Azúcar: el techo más alto</h3><p>Para el azúcar (partida 1701) el techo es 98 %, por el sistema de bandas de precios, que el Artículo 24 del ACE 35 congeló para el MERCOSUR.</p><div class="src">OMC; ACE 35, Artículo 24</div></div>
</div>
<p class="note">Aranceles por subpartida de 6 dígitos (aplicado 2026 y consolidado): <a href="tablas/aranceles_chile_omc.csv" download>CSV</a> · <a href="tablas/aranceles_chile_omc.xlsx" download>Excel</a>. Fuente: OMC, Tariff &amp; Trade Data (descargado el 26/11/2026). El arancel aplicado de la OMC no incluye las preferencias del ACE 35.</p>"""


ACUERDOS = [
    dict(
        carpeta="ace35", uso=uso.seccion("CL", "Chile", 2011, texto_extra=" Los datos de la DNIT empiezan en 2011. La caída de 2012 también aparece en el BCP "
                    "(USD 192 millones): ese año la carne paraguaya tuvo mercados cerrados por la fiebre aftosa."), sigla="ALADI/AAP.CE/35", nombre="MERCOSUR–Chile", socio="Chile",
        titulo="ACE 35 MERCOSUR–Chile: texto completo, protocolos y régimen de origen para Paraguay",
        descripcion="El ACE 35 (MERCOSUR–Chile) ordenado y buscable: texto del Acuerdo, 14 anexos, 69 protocolos adicionales, "
                    "el régimen de origen de 2025 y la lista especial de origen para las exportaciones de Paraguay a Chile.",
        h1="ACE 35: el acuerdo del MERCOSUR con <em>Chile</em>, completo y en un solo lugar",
        lead="El texto del Acuerdo de 1996, sus anexos y los 69 protocolos adicionales, tomados de la ALADI y pasados a texto, incluido el "
             "Acuerdo Comercial Chile–Paraguay de 2021. Y un buscador con el régimen de origen vigente, que tiene una lista propia para lo que Paraguay le vende a Chile.",
        kpis=[("25/06/1996", "firmado en Potrero de los Funes (Argentina)"), ("1/10/1996", "empezó la desgravación"),
              ("2014", "último cronograma: desde entonces todo tiene 100 % de preferencia"), ("139", "documentos ordenados")],
        linea=[("25/06/1996", "Firma del Acuerdo.", False),
               ("1/10/1996", "Empiezan las preferencias para todo el universo de productos.", False),
               ("2003", "Protocolo 37: trato Chile–Paraguay de las autopartes del Anexo 4 (100 % en 2006; un listado, en 2008).", True),
               ("2004", "100 % para el cronograma general y el Anexo 1.", False),
               ("2006", "100 % para los Anexos 2 y 3.", False),
               ("2011 y 2012", "100 % para los productos sensibles (Anexos 6 y 8).", False),
               ("2014", "100 % para el Anexo 9: termina el Programa de Liberación.", False),
                              ("05/11/2019", "Protocolo 63: entra en vigor un nuevo Régimen de Origen (Paraguay: Decreto N° 1.274/2019).", True),
               ("1/12/2021", "Paraguay y Chile firman en Santiago un Acuerdo Comercial bilateral de 19 capítulos.", True),
               ("15/02/2022", "Protocolo 66: ese Acuerdo Comercial Chile–Paraguay se incorpora al ACE 35 (rige solo entre los dos países).", True),
               ("24/01/2024", "Entran en vigor entre Paraguay y Chile los Protocolos 67 (drawback) y 68 (origen diferenciado hasta 2038).", True),
               ("14/02/2024", "Entra en vigor el Acuerdo Comercial Chile–Paraguay (Protocolo 66; Paraguay: Decreto N° 9.560/2023).", True),
               ("24/11/2025", "Entra en vigor entre Paraguay y Chile el Protocolo 69, con el Régimen de Origen actual (Paraguay: Decreto N° 4.638/2025).", True)],
        disposiciones=[
            ("19", "capítulos del Acuerdo Comercial Chile–Paraguay", "Facilitación del comercio, buenas prácticas regulatorias, medidas sanitarias, obstáculos técnicos, servicios, comercio electrónico, competencia, mipymes, cadenas de valor, asuntos laborales, medio ambiente, género, cooperación, transparencia y anticorrupción, administración y solución de controversias.", "Protocolo 66, vigente desde el 14/02/2024"),
            ("194", "productos con origen diferenciado", "Para lo que Paraguay exporta a Chile hay requisitos de origen propios (Apéndice 2 del Régimen de Origen), en general salto de partida o 50 % de contenido regional.", "Protocolos 68 y 69"),
            ("2038", "plazo del origen diferenciado", "Vence el 31/12/2038 y se extiende de a cinco años, salvo que Paraguay o Chile avisen con nueve meses de anticipación.", "Protocolo 69, Anexo, art. 4.7"),
            ("Puertos", "valor de los materiales para Paraguay", "Para calcular el valor de los materiales no originarios, Paraguay puede tomar como destino cualquier puerto marítimo o fluvial de las Partes, incluidos depósitos y zonas francas.", "Protocolo 69, Anexo, definiciones"),
            ("Autopartes", "trato Chile–Paraguay del Anexo 4", "Cronograma propio: 100 % en 2006 y, para un listado de autopartes, en 2008.", "Protocolo 37 (2003)"),
            ("Carne", "cupos de Chile a Paraguay", "Cupos de carne bovina en el Anexo 7, ajustados por los Protocolos 2 (1997) y 29 (2002, 3.500 toneladas de carne congelada).", "Protocolos 2 y 29"),
            ("298", "productos con arancel residual de Paraguay", "Paraguay cobraba a Chile un arancel propio (Lista de Adecuación) para 298 productos, por ejemplo 27 % para la carne en 1996; bajó año a año hasta 0 % en 2006.", "Anexo 12, Paraguay"),
            ("50 %", "márgenes iniciales de 1996", "En el Anexo 10, Chile dio a Paraguay márgenes iniciales (muchos de 50 %) para aves, huevos, tomates, avena y otros. Hoy esos productos tienen 100 %.", "Anexo 10")],
        despues_uso=VIG35, aranceles=ARANCELES_CHILE,
        productos=BUSCA.format(texto="Requisitos específicos de origen del régimen vigente (Protocolo 69): los que valen para todas las Partes y los especiales para lo que Paraguay exporta a Chile.", ej="soja, 3923, prendas"),
        script="""<script>
window.PRODUCTOS = {archivo: "origen.json", columnas: ["Código", "Producto", "Lista", "Requisito de origen"],
  fila: r => [r[0], esc(r[1]) + (r[2] ? `<div class="det">${esc(r[2])}</div>` : ""), `<span class="chica">${esc(r[4])}</span>`, esc(r[3])]};
</script>""",
        ejemplo="Por ejemplo: drawback, certificado de origen, salvaguardia, Paraguay",
        grupos=["Acuerdo", "Anexos del Programa de Liberación", "Origen y controversias", "Protocolos adicionales", "Guías de otros países"],
        descargas=[("Requisitos específicos de origen (805)", "tablas/requisitos_especificos_origen"),
                   ("Origen diferenciado Paraguay a Chile (194 productos)", "tablas/origen_diferenciado_paraguay_a_chile"),
                   ("Vigencia de los Protocolos 61 a 69 y normas de Paraguay", "tablas/vigencia_protocolos_61_69"),
                   ("Márgenes iniciales de Chile a Paraguay en 1996 (Anexo 10; SICE hasta la partida 8308, el resto con OCR)", "tablas/chile_a_paraguay_margenes_iniciales_1996"),
                   ("Lista de Adecuación de Paraguay: arancel para Chile año por año, 1996–2006 (Anexo 12, 298 productos)", "tablas/paraguay_lista_adecuacion_anexo12"),
                   ("Nomenclatura NALADISA 2012 del Protocolo 60 con la preferencia de Chile: 6.811 códigos, todos con 100 % (planilla de Brasil, descripciones en portugués)", "tablas/naladisa_2012_preferencias_chile")],
        como="<p>Se tomaron los 131 archivos que publica la <b>ALADI</b> para el ACE 35, sin copias repetidas. 88 tienen texto y se leyeron con <code>pdftotext</code>; 43 eran imágenes escaneadas (casi todo lo de 1996 a 1998: 2.942 páginas) y se leyeron con OCR (<code>tesseract</code>). Las tablas del Régimen de Origen se leyeron celda por celda (<code>pdfplumber</code>): los 805 requisitos del Apéndice 1 están numerados del 1 al 805 sin huecos.</p>"
             "<p>Se sumaron después el Anexo 9 y el Protocolo sobre Integración Física (escaneados, con OCR), las 72 fichas de la ALADI (que solo llegan hasta el Protocolo 60) y las páginas de la Aduana de Chile y del Ministerio de Relaciones Exteriores de Paraguay. Dos anexos del Protocolo 30 (Anexos II y V) dan error 404 en la ALADI; se usaron copias que ya estaban reunidas.</p><p>Siete documentos se tomaron del <b>SICE de la OEA</b>, que los publica como texto y no como imagen: el Anexo 4 (autopartes de Paraguay), las listas de Adecuación del Anexo 12 de los cuatro países, las notas complementarias de Paraguay y el Anexo 15, que no está en la ALADI (hay además una copia escaneada en portugués). La lista del Anexo 10 de Chile a Paraguay se tomó del SICE hasta la partida 8308 (203 productos); los 16 restantes (capítulos 84 a 96) siguen leídos con OCR y conviene verificarlos.</p><p>De la página del ACE 35 en Siscomex (Brasil) se sumaron la ficha técnica y el manual del régimen de origen (en portugués), la Decisión N° 02/2024 de la Comisión Administradora del Acuerdo de Libre Comercio Brasil–Chile (escaneada, con OCR) y la planilla de preferencias en NALADISA 2012, que confirma que los 6.811 códigos tienen 100 %.</p><p>El Anexo 15 Lista las normas del MERCOSUR sobre transporte vigentes en 1996; la Comisión Administradora debía identificar cuáles aplicar también con Chile (Artículo 38 del Acuerdo). Los textos base de los Protocolos 21, 31, 39, 52 y 53 tampoco, pero sí sus versiones rectificadas, que son las vigentes.</p>"),
    dict(
        carpeta="ace58", uso=uso.seccion("PE", "Perú", 2011, texto_extra=" Los datos de la DNIT empiezan en 2011."), sigla="ALADI/AAP.CE/58", nombre="MERCOSUR–Perú", socio="Perú",
        titulo="ACE 58 MERCOSUR–Perú: texto completo y preferencias producto por producto para Paraguay",
        descripcion="El ACE 58 (MERCOSUR–Perú) ordenado y buscable: texto del Acuerdo, 10 anexos, 6 protocolos y un buscador "
                    "con el cronograma de desgravación de cada producto entre Paraguay y Perú.",
        h1="ACE 58: el acuerdo del MERCOSUR con <em>Perú</em>, completo y en un solo lugar",
        lead="El texto del Acuerdo de 2005, sus 10 anexos y los 6 protocolos adicionales, tomados de la ALADI y pasados a texto. "
             "Y un buscador para ver, producto por producto, cuándo llegó al 100 % la preferencia entre Paraguay y Perú.",
        kpis=[("30/11/2005", "firmado en Montevideo"), ("6.522", "productos en las listas Paraguay–Perú"),
              ("2012 y 2017", "años en que casi todo llegó al 100 %"), ("37", "documentos ordenados")],
        linea=[("30/11/2005", "Firma del Acuerdo; se protocoliza en la ALADI el 7/12/2005. Reemplaza al AAP.R N° 20.", False),
               ("Inicio", "Desgravación inmediata para los productos de categoría A.", False),
               ("2007", "Protocolo 4: Perú confirma a Paraguay 95 % de preferencia para el maíz amarillo duro, con cupo anual de 60.000 toneladas.", True),
               ("1/1/2012", "100 % para el cronograma general (B3 de Paraguay, B4 de Perú) y el patrimonio histórico (C3).", True),
               ("1/1/2017", "100 % para los cronogramas más largos (D5 y D6).", True),
               ("2018", "Protocolo 6: cambios en el cronograma entre Perú y Brasil.", False)],
        disposiciones=[
            ("95 %", "maíz amarillo duro", "Perú da a Paraguay 95 % de preferencia con un cupo anual de 60.000 toneladas (ítem 1005.90.20).", "Protocolo 4 (2007)"),
            ("Textiles", "programa en suspenso", "Entre Perú y Paraguay, el programa no se aplica a los textiles (capítulos 50 a 63) que no tienen requisito específico de origen en el Apéndice 2 del Anexo V.", "Anexo II-B"),
            ("D5 y D6", "márgenes fijos", "Los productos de estas categorías mantienen su margen inicial hasta que el cronograma lo alcanza; llegan a 100 % en 2017.", "Anexo II-B"),
            ("Zonas francas", "fuera del programa", "El Programa de Liberación no comprende las mercaderías elaboradas en zonas francas o áreas aduaneras especiales.", "Anexo II-B"),
            ("Origen", "requisitos Paraguay–Perú", "El Anexo V tiene un apéndice propio con los requisitos específicos de origen entre Paraguay y Perú.", "Anexo V, Apéndice 2"),
            ("Medidas", "especiales", "Las Partes pueden suspender o reducir la preferencia si las importaciones de ciertos productos crecen mucho o llegan a precios muy bajos.", "Anexo X")],
        antes="""<h2>Qué tan rápido llegó cada lado al 100 %</h2>
<div class="card"><div class="barras" id="barras"></div><div class="ley" id="ley"></div>
<p class="note">Categorías del Anexo II-B: A = inmediata; B = cronograma general (100 % en 2012); C3 = patrimonio histórico (2012); D5 y D6 = 100 % en 2017. «Sin dato»: no se pudo leer o el producto tiene dos o más cronogramas (Apéndices VII y VIII).</p></div>""",
        productos=BUSCA.format(texto="Cronograma de cada producto en las listas del Anexo II-B (NALADISA 96). Leídas con OCR: ante cualquier duda, vale el original.", ej="maíz, 1005, carne"),
        script="""<script>
const GC = {A:"var(--s1)", B:"var(--s4)", C:"var(--s3)", D:"var(--s2)", N:"var(--line)"};
const NG = {A:"A: inmediata", B:"B: 100 % en 2012", C:"C3: patrimonio histórico", D:"D5 y D6: 100 % en 2017", N:"Sin dato"};
const gr = c => c ? c[0] : "N";
const cat = (c, y) => c ? `<span class="cat" style="background:${GC[gr(c)]};color:#1d1a1c">${esc(c)}</span> <span class="chica">${y ? "100 % desde " + y : ""}</span>` : '<span class="chica">sin dato</span>';
window.PRODUCTOS = {archivo: "preferencias.json", columnas: ["Código", "Producto", "Perú da a Paraguay", "Paraguay da a Perú"],
  fila: r => [r[0], esc(r[1]) + (r[7] ? `<div class="det">${esc(r[7])}</div>` : ""), cat(r[2], r[4]) + (r[3] ? `<div class="det">margen inicial ${esc(r[3])} %</div>` : ""), cat(r[5], r[6])],
  listo: d => {
    const host = document.getElementById("barras");
    [["Perú a Paraguay", 2], ["Paraguay a Perú", 5]].forEach(([nom, k]) => {
      const n = {A:0, B:0, C:0, D:0, N:0}; d.forEach(r => n[gr(r[k])]++);
      const tot = d.length;
      host.insertAdjacentHTML("beforeend", `<div class="barra"><div class="t"><b>${nom}</b><span>${Math.round(100 * n.A / tot)} % inmediata · ${fmt(tot)} productos</span></div><div class="pila">` +
        ["A","B","C","D","N"].map(g => `<span style="width:${100 * n[g] / tot}%;background:${GC[g]}" title="${NG[g]}: ${fmt(n[g])}"></span>`).join("") + "</div></div>");
    });
    document.getElementById("ley").innerHTML = ["A","B","C","D","N"].map(g => `<span><i style="background:${GC[g]}"></i>${NG[g]}</span>`).join("");
  }};
</script>""",
        ejemplo="Por ejemplo: zona franca, medidas especiales, certificado de origen",
        grupos=["Acuerdo", "Programa de Liberación", "Anexos", "Protocolos adicionales"],
        descargas=[("Preferencias Paraguay–Perú, una fila por producto", "tablas/preferencias_paraguay_peru"),
                   ("Lista de Paraguay a Perú (Apéndice I-B)", "tablas/paraguay_a_peru"),
                   ("Lista de Perú a Paraguay (Apéndice II-B)", "tablas/peru_a_paraguay")],
        como="<p>Se tomaron los 37 archivos que publica la <b>ALADI</b> para el ACE 58. Casi todo está escaneado: 31 documentos (1.946 páginas) se leyeron con OCR (<code>tesseract</code>).</p>"
             "<p>Las listas Paraguay–Perú se leyeron dos veces: primero borrando las líneas de las tablas y separando las columnas por su posición en la página, y después con el texto corrido para completar lo que faltaba. Se descartaron los códigos que no existen en la NALADISA 96 (errores de lectura). Quedan sin cronograma cerca de 900 productos del lado de Perú y 600 del de Paraguay: lecturas fallidas o productos con dos o más cronogramas, que están como texto en los Apéndices VII y VIII.</p>"),
    dict(
        carpeta="ace36", uso=uso.seccion("BO", "Bolivia", 2011, texto_extra=" Los datos de la DNIT empiezan en 2011."), sigla="ALADI/AAP.CE/36", nombre="MERCOSUR–Bolivia", socio="Bolivia",
        titulo="ACE 36 MERCOSUR–Bolivia: texto completo, anexos y protocolos",
        descripcion="El ACE 36 (MERCOSUR–Bolivia) ordenado y buscable: texto del Acuerdo, 11 anexos, el Protocolo de "
                    "Integración Física y 34 protocolos adicionales, con fecha y síntesis de cada uno.",
        h1="ACE 36: el acuerdo del MERCOSUR con <em>Bolivia</em>, completo y en un solo lugar",
        lead="El texto del Acuerdo de 1996, sus 11 anexos, el Protocolo de Integración Física y los 34 protocolos adicionales, tomados de la ALADI y pasados a texto.",
        kpis=[("17/12/1996", "firmado en Fortaleza (Brasil)"), ("28/02/1997", "empezó la desgravación"),
              ("2014", "último cronograma: desde entonces todo tiene 100 % de preferencia"), ("66", "documentos ordenados")],
        linea=[("17/12/1996", "Firma del Acuerdo.", False),
               ("28/02/1997", "Empiezan las preferencias; el Anexo 7 tiene 100 % desde el inicio.", False),
               ("2004", "Protocolo 19: Argentina, Brasil y Paraguay suman productos con 100 % para Bolivia (Anexo 7).", True),
               ("2006", "100 % para el cronograma general y los Anexos 1, 3 y 4.", False),
               ("2011", "100 % para los productos sensibles del Anexo 5.", False),
               ("2014", "100 % para el Anexo 6: termina el Programa de Liberación.", False),
               ("2024", "Protocolo 34: los productos con insumos en admisión temporal o drawback pierden la preferencia desde el 8/8/2028.", False)],
        disposiciones=[
            ("Anexo 8", "Régimen de Adecuación de Paraguay", "Lista de aranceles residuales que Paraguay aplicaba a Bolivia mientras avanzaba la desgravación.", "Anexo 8, Paraguay"),
            ("100 %", "productos de Paraguay para Bolivia", "Paraguay, junto con Argentina y Brasil, sumó productos al Anexo 7 (100 % de preferencia).", "Protocolo 19 (2004)"),
            ("8/8/2028", "fin de la preferencia con drawback", "Desde esa fecha, los productos con insumos importados temporalmente o con drawback no tienen preferencia.", "Protocolo 34 (2024)"),
            ("Hidrovía", "objetivo del Acuerdo", "Entre sus objetivos está facilitar la navegación por la Hidrovía Paraná–Paraguay (Puerto Cáceres–Puerto Nueva Palmira); el Protocolo de Integración Física lo desarrolla.", "Acuerdo, Artículo 1")],
        ejemplo="Por ejemplo: drawback, hidrovía, certificado de origen, salvaguardia",
        grupos=["Acuerdo", "Anexos del Programa de Liberación", "Otros anexos", "Protocolos adicionales"],
        descargas=[],
        como="<p>Se tomaron los 66 archivos que publica la <b>ALADI</b> para el ACE 36. 38 tienen texto y se leyeron con <code>pdftotext</code>; 28 eran imágenes escaneadas (1.594 páginas) y se leyeron con OCR (<code>tesseract</code>).</p>"
             "<p>Las listas de productos de 1996 (Anexos 1 a 8) quedan como texto: no se pasaron a tablas porque sus cronogramas terminaron (el último, en 2014).</p>"),
    dict(
        carpeta="ace59", uso=uso.seccion("EC", "Ecuador", 2011, texto_extra=" Los datos de la DNIT empiezan en 2011.") + "\n" +
            uso.seccion("VE", "Venezuela", 2011, titulo="Y para venderle a Venezuela") + "\n" +
            uso.seccion("CO", "Colombia", 2011, hasta=2018, titulo="Colombia, mientras regía el ACE 59 (2011–2018)",
                        texto_extra="Desde 2019, el comercio con Colombia se rige por el ACE 72 (ver su página)."), sigla="ALADI/AAP.CE/59", nombre="MERCOSUR–Colombia, Ecuador y Venezuela", socio="Ecuador",
        titulo="ACE 59 MERCOSUR–Colombia, Ecuador y Venezuela: texto completo y listas de Paraguay",
        descripcion="El ACE 59 (MERCOSUR–Comunidad Andina) ordenado y buscable: texto del Acuerdo, 9 anexos, 9 protocolos y "
                    "todas las listas de preferencias y de origen en las que participa Paraguay.",
        h1="ACE 59: el acuerdo del MERCOSUR con <em>Colombia, Ecuador y Venezuela</em>",
        lead="El texto del Acuerdo de 2004, sus 9 anexos, los 9 protocolos adicionales y todas las listas en las que participa Paraguay, tomados de la ALADI y pasados a texto.",
        kpis=[("18/10/2004", "firmado en Montevideo"), ("9", "protocolos adicionales"),
              ("35", "documentos pasados a texto (de 65)"), ("ACE 72", "rige hoy la relación de Paraguay con Colombia")],
        linea=[("18/10/2004", "Firma del Acuerdo.", False),
               ("2005", "Protocolo 1: Régimen de Solución de Controversias.", False),
               ("2006", "Protocolo 4: cambia las notas de los capítulos 61 a 63 en las listas entre Ecuador y Paraguay.", True),
               ("2008 y 2010", "Protocolos 5 a 8: prórroga de requisitos de origen transitorios y preferencias de Brasil.", False),
               ("2011", "Protocolo 9: cambia el nombre del Acuerdo.", False),
               ("29/01/2019", "Entre Paraguay y Colombia rige el ACE 72.", True)],
        disposiciones=[
            ("Listas", "Paraguay con cada país andino", "Paraguay tiene listas propias de preferencias para Colombia, Ecuador y Venezuela (Apéndice 2) y listas bilaterales con dos o más cronogramas (Apéndices 4.7, 4.8 y 4.9).", "Anexo II"),
            ("Recibe", "preferencias para Paraguay", "Colombia, Ecuador y Venezuela tienen listas propias para Paraguay (Apéndices 3.3, 3.7 y 3.11), además de su lista para el MERCOSUR (Apéndice 1).", "Anexo II"),
            ("Origen", "requisitos bilaterales", "Requisitos específicos de origen de Paraguay con Colombia, Ecuador y Venezuela (Apéndices 3.7, 3.8 y 3.9).", "Anexo IV"),
            ("Textiles", "Ecuador–Paraguay", "El Protocolo 4 cambia las notas de los capítulos 61, 62 y 63 en las listas entre Ecuador y Paraguay.", "Protocolo 4 (2006)")],
        ejemplo="Por ejemplo: medidas especiales, certificado de origen, salvaguardia",
        grupos=["Acuerdo", "Anexos", "Programa de Liberación", "Protocolos adicionales"],
        descargas=[],
        como="<p>Se tomaron los 65 archivos que publica la <b>ALADI</b> para el ACE 59. Se pasaron a texto el Acuerdo, sus anexos, los protocolos y todas las listas en las que participa Paraguay (24 con OCR, 1.695 páginas). Las 30 listas entre otros países (por ejemplo, Colombia–Argentina) figuran en el catálogo como «no transcriptas».</p>"
             "<p>Las listas quedan como texto: todavía no se pasaron a tablas.</p>"),
]


def portada():
    tarjetas = [("ace72", "ACE 72", "MERCOSUR–Colombia", "Texto, preferencias producto por producto, contingentes y uso del acuerdo.", "Completo"),
                ("ace35", "ACE 35", "MERCOSUR–Chile", "Texto, 69 protocolos y el régimen de origen con la lista especial de Paraguay.", "Texto y origen"),
                ("ace58", "ACE 58", "MERCOSUR–Perú", "Texto y cronograma de cada producto entre Paraguay y Perú.", "Texto y preferencias"),
                ("ace36", "ACE 36", "MERCOSUR–Bolivia", "Texto, anexos y 34 protocolos.", "Texto"),
                ("ace59", "ACE 59", "MERCOSUR–Colombia, Ecuador y Venezuela", "Texto y las listas en las que participa Paraguay.", "Texto")]
    cards = "".join(f'<a class="card" href="{c}/"><div class="n">{n}</div><h3>{t}</h3><p>{d}</p><span class="est">{s}</span></a>'
                    for c, n, t, d, s in tarjetas)
    return f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Textos de los acuerdos comerciales de Paraguay</title>
<meta name="description" content="Los acuerdos comerciales de Paraguay en la ALADI (ACE 72, 35, 58, 36 y 59), ordenados, sin duplicados y buscables: texto completo, protocolos, preferencias y régimen de origen.">
<link rel="icon" href="logo.svg" type="image/svg+xml">
<link rel="canonical" href="{URL}">
<meta property="og:type" content="website">
<meta property="og:locale" content="es_PY">
<meta property="og:title" content="Textos de los acuerdos comerciales de Paraguay">
<meta property="og:description" content="Texto completo, protocolos, preferencias y régimen de origen de los acuerdos de Paraguay, ordenados y buscables.">
<meta property="og:url" content="{URL}">
<meta property="og:image" content="{URL}img/tarjeta_light.png">
<meta name="twitter:card" content="summary_large_image">
<script>(function(){{try{{var x=localStorage.getItem("tema");if(x==="light"||x==="dark")document.documentElement.setAttribute("data-theme",x);}}catch(e){{}}}})();</script>
<link rel="stylesheet" href="comun.css">
</head>
<body>
<div class="aviso-top">Proyecto independiente. No representa ni cuenta con el respaldo de la ALADI, del MERCOSUR ni de ningún gobierno.</div>
<header>
  <div class="wrap">
    <div class="marca"><img src="logo.svg" alt=""><span><b>Textos de los acuerdos comerciales de Paraguay</b><br><small>Ordenados, sin duplicados y buscables</small></span></div>
    <h1>Los acuerdos comerciales de Paraguay, <em>completos y en un solo lugar</em></h1>
    <p class="lead">Cada acuerdo con su texto, sus anexos y protocolos, tomados de la ALADI y pasados a texto, con buscadores y lo que tiene de especial para Paraguay.</p>
  </div>
</header>
<main class="wrap">
<h2>Los acuerdos</h2>
<div class="acuerdos">{cards}</div>
<h2>Cómo se arma cada acuerdo</h2>
<div class="card"><p>Se reúnen los archivos oficiales de la <b>ALADI</b> (el depositario de los acuerdos), se quitan las copias repetidas y se pasan a texto: con <code>pdftotext</code> los que tienen texto y con OCR (<code>tesseract</code>) los escaneados. Las listas de productos se leen como tablas cuando hace falta para Paraguay. Los PDF originales no se publican aquí; cada página indica la fuente.</p>
<p class="note">Código en <a href="https://github.com/silvia-mov/textos-acuerdos-paraguay">GitHub</a>. Datos de comercio y uso de los acuerdos: <a href="https://silvia-mov.github.io/comercio-exterior-paraguay-acuerdos/">Comercio exterior de Paraguay y acuerdos comerciales</a>.</p></div>
</main>
<footer>
  <div class="wrap">Fuente: ALADI (textos oficiales). Código con licencia MIT en <a href="https://github.com/silvia-mov/textos-acuerdos-paraguay">GitHub</a>. Proyecto independiente: no representa ni cuenta con el respaldo de la ALADI, del MERCOSUR ni de ningún gobierno. Más proyectos en <a href="https://silvia-mov.github.io/">silvia-mov.github.io</a>.</div>
</footer>
<script src="tema.js"></script>
</body>
</html>
"""


def uso_ace72():
    p = DOCS / "ace72" / "index.html"
    h = p.read_text(encoding="utf-8")
    i = h.index("<h2>Paraguay usa poco el acuerdo")
    j = h.index("</p>", h.index('<p class="note">', i)) + 4
    nuevo = (uso.seccion("CO", "Colombia", 2019, titulo="Paraguay usa poco el acuerdo para venderle a Colombia",
                         texto_extra=" El acuerdo rige entre Paraguay y Colombia desde el 29/01/2019; el cambio de 2019 se compara con 2018, "
                                     "cuando regía el ACE 59.")
             + '\n<p class="note">' + uso.NOTA + " Las importaciones desde Colombia con el ACE 72 fueron USD 30,2 millones en 2025.</p>")
    p.write_text(h[:i] + nuevo + h[j:], encoding="utf-8")


def grafico_cupo(d, g, cupo, titulo, unidad_cupo):
    """Barras apiladas por año (con ACE 72 / sin acuerdo) y una línea con el cupo: lo vendido frente a la referencia."""
    x = d[d.CONTINGENTE == g].set_index("AÑO")
    anios = list(x.index)
    con = x.CON_ACE72_T
    sin = x.SIN_ACUERDO_T + x.OTRO_O_SIN_DATO_T
    bruto = max(max(cupo(a) for a in anios), (con + sin).max()) * 1.12
    paso = next(p for p in (1, 2, 5, 10, 20, 25, 50, 100, 200, 250, 500, 1000, 2000, 2500, 5000) if bruto / p <= 4)
    tope = paso * -(-bruto // paso)
    W, H, iz, ab, ar = 440, 220, 44, 24, 16
    ancho = (W - iz - 10) / len(anios)
    y = lambda v: ar + (H - ar - ab) * (1 - v / tope)
    partes = []
    for k in [paso * n for n in range(int(tope // paso) + 1)]:            # líneas guía suaves, en números redondos
        partes.append(f'<line x1="{iz}" x2="{W - 10}" y1="{y(k):.1f}" y2="{y(k):.1f}" stroke="var(--line)"/>'
                      f'<text x="{iz - 6}" y="{y(k) + 4:.1f}" text-anchor="end" font-size="12" fill="var(--text2)">{uso.num(k, 0)}</text>')
    for i, a in enumerate(anios):
        x0 = iz + i * ancho + ancho * 0.22
        w = ancho * 0.56
        c, s = float(con[a]), float(sin[a])
        if s:
            partes.append(f'<rect x="{x0:.1f}" y="{y(c + s):.1f}" width="{w:.1f}" height="{y(c) - y(c + s):.1f}" fill="var(--s4)" rx="2"><title>{a}: {uso.num(s, 0)} t sin acuerdo</title></rect>')
        if c:
            partes.append(f'<rect x="{x0:.1f}" y="{y(c):.1f}" width="{w:.1f}" height="{y(0) - y(c):.1f}" fill="var(--s3)" rx="2"><title>{a}: {uso.num(c, 0)} t con el ACE 72</title></rect>')
        tot = c + s
        if tot or max(cupo(b) for b in anios) / tope > 0.1:      # el 0 no se escribe si taparía la línea del cupo
            partes.append(f'<text x="{x0 + w / 2:.1f}" y="{y(tot) - 5:.1f}" text-anchor="middle" font-size="12.5" font-weight="{700 if tot else 400}" fill="var({"--text" if tot else "--text2"})">{uso.num(tot, 0)}</text>')
        partes.append(f'<text x="{x0 + w / 2:.1f}" y="{H - 8}" text-anchor="middle" font-size="12" fill="var(--text2)">{str(a)[2:] if W < 500 else a}{"*" if a == uso.PARCIAL else ""}</text>')
    pts = " ".join(f"{iz + i * ancho + ancho / 2:.1f},{y(cupo(a)):.1f}" for i, a in enumerate(anios))
    partes.append(f'<polyline points="{pts}" fill="none" stroke="var(--text)" stroke-width="2" stroke-dasharray="6 4"/>')
    partes.append(f'<text x="{iz + ancho * 0.2:.1f}" y="{y(cupo(anios[0])) - 8:.1f}" text-anchor="start" font-size="13" font-weight="700" fill="var(--text)">cupo: {unidad_cupo}</text>')
    return (f'<figure class="graf"><figcaption>{titulo}</figcaption><svg viewBox="0 0 {W} {H}" role="img" aria-label="{e(titulo)}">'
            + "".join(partes) + "</svg></figure>")


def contingentes_ace72():
    """Contingentes del ACE 72 y lo que vendió Paraguay (datos de la DNIT, python/contingentes_ace72.py)."""
    d = pd.read_csv(DOCS / "ace72/tablas/contingentes_ventas_paraguay.csv")
    G = ["Carne bovina deshuesada, despojos, carne salada y tripas", "Leche y nata en polvo",
         "Preparaciones y conservas de carne", "Leche maternizada"]
    t = lambda x: uso.num(x, 0)
    def tot(g):
        x = d[d.CONTINGENTE == g]
        return float(x.CON_ACE72_T.sum()), float((x.SIN_ACUERDO_T + x.OTRO_O_SIN_DATO_T).sum())
    cc, cs = tot(G[0]); pc, ps = tot(G[2])
    tarjetas = [
        (f"{uso.num(100 * cc / (cc + cs), 0)} %", "Carne bovina deshuesada, despojos, carne salada y tripas",
         f"Vendió {t(cc + cs)} t a Colombia entre 2019 y 2026 y solo {t(cc)} t con el acuerdo.",
         "Cupo de 3.299 t, con 2 % más por año (unas 3.789 t en 2026), compartido con todo el MERCOSUR. Fuera del cupo: 25 % de preferencia fija."),
        ("100 %", "Preparaciones y conservas de carne",
         f"Vendió {t(pc + ps)} t entre 2023 y 2025, todas con el acuerdo: mucho más que el cupo.",
         "Cupo de 4.538 kg por año, solo para Paraguay. Lo que pasa del cupo entra con 70 % de preferencia fija."),
        ("—", "Cortes finos de carne bovina",
         "No tienen código propio en la NCM: se cuentan con la carne deshuesada.",
         "Cupo de 5.294 t para todo el MERCOSUR, pero son categoría C: 100 % desde 2018, así que el cupo ya no limita."),
        ("0 t", "Leche en polvo y leche maternizada",
         "Paraguay no le vendió estos productos a Colombia entre 2019 y 2026.",
         "Leche en polvo: 303 t por año, solo Paraguay, sin rebaja fuera del cupo. Leche maternizada: 300 t, todo el MERCOSUR, categoría C.")]
    cards = "".join(f'<div class="card"><div class="v">{v}</div><h3>{h}</h3><p>{p}</p><div class="src">{s}</div></div>'
                    for v, h, p, s in tarjetas)
    cupo_carne = lambda a: 3299 * 1.02 ** (a - 2019)
    graf1 = grafico_cupo(d, G[0], cupo_carne, "Carne bovina, despojos y tripas vendidos a Colombia (toneladas)", "unas 3.800 t")
    graf2 = grafico_cupo(d, G[2], lambda a: 4.538, "Conservas de carne vendidas a Colombia (toneladas)", "4,5 t")
    ley = ('<div class="ley"><span><i style="background:var(--s3)"></i>Con el ACE 72</span><span><i style="background:var(--s4)"></i>Sin acuerdo</span>'
           '<span><i style="background:none;border-top:2px dashed var(--text);border-radius:0;height:0;width:18px;vertical-align:3px"></i>Cupo</span></div>')
    html_ = ('<h2>Los contingentes: Paraguay casi no usa los de carne</h2>\n'
             '<p>Colombia da a Paraguay rebaja total para una cantidad fija por año (Paraguay no da contingentes a Colombia). '
             'El de carne alcanzaba de sobra para todo lo vendido, pero casi todo se vendió pagando el arancel completo. '
             'Las conservas de carne, en cambio, usan el acuerdo y pasan el cupo.</p>\n'
             f'<div class="disp dos">{cards}</div>\n'
             f'<div class="card">{ley}{graf1}{graf2}'
             '<p class="note">* Enero a octubre. Toneladas netas de los despachos de exportación definitivos de la DNIT con destino a Colombia, '
             'según el acuerdo que declaró el exportador (en 2025, 28 t de despojos figuran sin el dato). Solo datos de Paraguay: la DNIT no muestra cuánto del cupo asignó Colombia '
             'a cada despacho ni lo que usaron los otros países del MERCOSUR. Carne: NCM 0201.30, 0202.30, 0206.10, 0206.21, 0206.22, 0206.29, 0210.20 '
             'y 0504.00 (la partida 0504 incluye tripas de otras especies). Conservas: 1602.10, 1602.49, 1602.50 y 1602.90. Leche en polvo: 0402. '
             'Leche maternizada: 1901.10. Cupos: Anexo II, Apéndice 3.3 (el de carne, calculado con el 2 % anual). Datos: '
             '<a href="tablas/contingentes_ventas_paraguay.csv" download>CSV</a> · <a href="tablas/contingentes_ventas_paraguay.xlsx" download>Excel</a>.</p></div>\n\n')
    p = DOCS / "ace72" / "index.html"
    h = p.read_text(encoding="utf-8")
    i = h.index("<h2>Los contingentes")
    j = h.index("<h2>Paraguay usa poco el acuerdo")
    p.write_text(h[:i] + html_ + h[j:], encoding="utf-8")


def main():
    uso_ace72()
    contingentes_ace72()
    print("JSON de productos:", productos_json())
    for a in ACUERDOS:
        (DOCS / a["carpeta"] / "index.html").write_text(pagina(a), encoding="utf-8")
    (DOCS / "index.html").write_text(portada(), encoding="utf-8")
    urls = [URL] + [f"{URL}{c}/" for c in ["ace72", "ace35", "ace58", "ace36", "ace59"]]
    (DOCS / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
                                      "".join(f"  <url><loc>{u}</loc></url>\n" for u in urls) + "</urlset>\n", encoding="utf-8")
    (DOCS / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {URL}sitemap.xml\n", encoding="utf-8")
    print("páginas listas")


if __name__ == "__main__":
    main()
