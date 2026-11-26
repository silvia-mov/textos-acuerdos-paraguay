"""Sección «Qué tan protegido está el mercado de …» con los aranceles de la OMC (Tariff & Trade Data): arancel NMF
aplicado por subpartida de 6 dígitos y arancel consolidado. Muestra el promedio, cuántos productos entran libres,
dónde se concentran los aranceles altos (por capítulo del Sistema Armonizado) y el techo consolidado."""
import html
from pathlib import Path

import pandas as pd

DATOS = Path(__file__).resolve().parent / "datos" / "omc"
CAP = {"01": "Animales vivos", "02": "Carne", "03": "Pescado", "04": "Lácteos, huevos y miel", "05": "Otros productos animales",
       "06": "Plantas y flores", "07": "Hortalizas", "08": "Frutas", "09": "Café, té y especias", "10": "Cereales",
       "11": "Harinas y almidones", "12": "Semillas oleaginosas", "13": "Gomas y resinas", "14": "Materias trenzables",
       "15": "Grasas y aceites", "16": "Preparaciones de carne y pescado", "17": "Azúcar y confitería", "18": "Cacao",
       "19": "Preparaciones de cereales", "20": "Preparaciones de hortalizas y frutas", "21": "Preparaciones alimenticias diversas",
       "22": "Bebidas y alcohol", "23": "Residuos y alimentos para animales", "24": "Tabaco", "25": "Sal, piedras y cemento",
       "26": "Minerales metalíferos", "27": "Combustibles", "28": "Químicos inorgánicos", "29": "Químicos orgánicos",
       "30": "Medicamentos", "31": "Abonos", "32": "Tintas y pinturas", "33": "Perfumería y cosméticos", "34": "Jabones y ceras",
       "35": "Albúminas y colas", "36": "Explosivos y fósforos", "37": "Productos fotográficos", "38": "Productos químicos diversos",
       "39": "Plásticos", "40": "Caucho", "41": "Cueros", "42": "Artículos de cuero y bolsos", "43": "Peletería", "44": "Madera",
       "45": "Corcho", "46": "Cestería", "47": "Pasta de papel", "48": "Papel y cartón", "49": "Libros e impresos", "50": "Seda",
       "51": "Lana", "52": "Algodón", "53": "Otras fibras vegetales", "54": "Filamentos sintéticos", "55": "Fibras sintéticas",
       "56": "Guata y cordeles", "57": "Alfombras", "58": "Tejidos especiales", "59": "Tejidos técnicos", "60": "Tejidos de punto",
       "61": "Prendas de punto", "62": "Prendas que no son de punto", "63": "Otros artículos textiles", "64": "Calzado",
       "65": "Sombreros", "66": "Paraguas", "67": "Plumas y flores artificiales", "68": "Manufacturas de piedra",
       "69": "Cerámica", "70": "Vidrio", "71": "Joyería", "72": "Hierro y acero", "73": "Manufacturas de hierro y acero",
       "74": "Cobre", "75": "Níquel", "76": "Aluminio", "78": "Plomo", "79": "Cinc", "80": "Estaño", "81": "Otros metales",
       "82": "Herramientas", "83": "Manufacturas de metal diversas", "84": "Máquinas", "85": "Material eléctrico",
       "86": "Ferrocarriles", "87": "Vehículos", "88": "Aeronaves", "89": "Barcos", "90": "Instrumentos", "91": "Relojes",
       "92": "Instrumentos musicales", "93": "Armas", "94": "Muebles", "95": "Juguetes", "96": "Manufacturas diversas",
       "97": "Obras de arte"}
e = html.escape


def num(x, d=1):
    return f"{x:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def seccion(pais, socio, carpeta, docs, contexto=""):
    a = pd.read_csv(DATOS / f"{pais}_nmf_aplicado_2026.csv", dtype={"product_code": str})
    b = pd.read_csv(DATOS / f"{pais}_consolidado.csv", dtype={"product_code": str})
    v = a.value.dropna()
    libres, n = int((v == 0).sum()), len(v)
    altos = int((v >= 20).sum())
    techo = b.value.median()
    a["cap"] = a.product_code.str[:2]
    g = a.groupby("cap").value.agg(["mean", "count"]).query("count >= 5").sort_values("mean", ascending=False).head(8)
    mx = g["mean"].max()
    barras = "".join(f'<div class="gb"><div class="gt"><span><span class="chica">Cap. {c} ·</span> {e(CAP.get(c, c))}</span>'
                     f'<b>{num(r["mean"])} %</b></div><div class="gk"><div style="width:{100 * r["mean"] / mx:.0f}%"></div></div></div>'
                     for c, r in g.iterrows())
    out = a[["product_code", "value"]].rename(columns={"product_code": "SA_6_DIGITOS", "value": "NMF_APLICADO_2026"}).merge(
        b[["product_code", "value"]].rename(columns={"product_code": "SA_6_DIGITOS", "value": "CONSOLIDADO_OMC"}), on="SA_6_DIGITOS", how="outer")
    out["CONSOLIDADO_OMC"] = out.CONSOLIDADO_OMC.round(2)
    out["NMF_APLICADO_2026"] = out.NMF_APLICADO_2026.round(2)
    (docs / carpeta / "tablas").mkdir(exist_ok=True)
    out.sort_values("SA_6_DIGITOS").to_csv(docs / carpeta / "tablas" / f"aranceles_{pais}_omc.csv", index=False, encoding="utf-8-sig")
    tarjetas = [
        (f"{num(v.mean())} %", "Arancel general (NMF) promedio en 2026", f"Promedio simple de {num(n, 0)} subpartidas. Con el acuerdo, Paraguay entra con 0 %."),
        (f"{num(100 * libres / n, 0)} %", "Productos que entran libres para todos", f"{num(libres, 0)} subpartidas con arancel 0. En el resto, el acuerdo le da a Paraguay una ventaja frente a terceros."),
        (f"{num(100 * altos / n, 0)} %", "Productos con arancel de 20 % o más", f"{num(altos, 0)} subpartidas: ahí la preferencia del acuerdo vale más."),
        (f"{num(techo, 0)} %", "Techo consolidado en la OMC", "Lo máximo que puede cobrar a quienes no tienen acuerdo (valor más frecuente)."),
    ]
    cards = "".join(f'<div class="card"><div class="v">{v_}</div><h3>{h}</h3><p>{p}</p><div class="src">OMC, Tariff &amp; Trade Data</div></div>'
                    for v_, h, p in tarjetas)
    return (f'<h2>Qué tan protegido está el mercado de {socio}</h2>\n<p>{contexto}</p>\n<div class="disp">{cards}</div>\n'
            f'<h3>Dónde se concentran los aranceles altos</h3>\n<div class="card"><div class="grupos">{barras}</div>'
            '<p class="note">Arancel NMF aplicado promedio por capítulo del Sistema Armonizado (capítulos con 5 subpartidas o más). '
            f'Aranceles por subpartida: <a href="tablas/aranceles_{pais}_omc.csv" download>CSV</a> · <a href="tablas/aranceles_{pais}_omc.xlsx" download>Excel</a>. '
            'Fuente: OMC, Tariff &amp; Trade Data (descargado el 26/11/2026). El arancel aplicado de la OMC no incluye las preferencias de los acuerdos.</p></div>')
