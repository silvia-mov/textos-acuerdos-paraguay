"""ACE 58: listas de desgravación Paraguay–Perú (Anexo II-B, Apéndices I-B y II-B) leídas de un OCR con posiciones.

Cada página se pasó por tesseract en modo tsv después de borrar las líneas de la tabla. Las columnas se ubican con
los títulos «Cronograma» y «Margen/preferencia» de cada página; las filas empiezan en cada código NALADISA 96.
Uso: python3 ace58_listas.py <carpeta_tsv> <carpeta_salida>
"""
import csv
import re
import sys
from pathlib import Path

import pandas as pd

APENDICES = {"ACE_058_Anexo_002_B_Apen_001_B": ("paraguay_a_peru", "B3"),
             "ACE_058_Anexo_002_B_Apen_002_B": ("peru_a_paraguay", "B4")}
CODIGO = re.compile(r"^\d{8}$")


def pagina(ruta):
    try:
        d = pd.read_csv(ruta, sep="\t", quoting=3, dtype={"text": str}, keep_default_na=False)
    except pd.errors.EmptyDataError:
        return pd.DataFrame()
    d = d[(d.conf.astype(float) > -1) & (d.text.str.strip() != "")]
    return d[["left", "top", "width", "height", "text"]].astype({"left": int, "top": int, "width": int})


def columnas(d):
    """x donde empiezan las columnas de cronograma y de margen inicial. La de cronograma se ubica por las palabras
    que parecen categorías (A, B3, B4, C3a…, D5, D6) en la mitad derecha de la página."""
    ancho = int((d.left + d.width).max())
    cat = d[d.text.str.fullmatch(r"[|\[(.]?(A|B[34A-Za-z]{0,2}|C3\s?[a-h]?|D[56])[|\])o.]?") & (d.left > ancho * 0.55)]
    crono = int(cat.left.quantile(0.02)) - 30 if len(cat) >= 3 else int(ancho * 0.66)
    f = d[d.text.str.match(r"^(Margen|preferencia|inicial)")]
    margen = int(f.left.min()) - 60 if len(f) else crono + 450
    return crono, max(margen, crono + 250)


def categoria(texto, b):
    t = texto.replace("€", "C").replace("O", "0").replace(" ", "")
    m = re.findall(r"C3[a-hA-H]|D[56]|B[34A-Za-z]|A", t)
    if not m:
        return ""
    c = m[-1]
    if c.startswith("B"):
        return b
    return c[:2] + c[2:].lower()


def leer(carpeta, base, b):
    filas = []
    for ruta in sorted(Path(carpeta).glob(f"{base}_[0-9][0-9][0-9][0-9].tsv")):
        d = pagina(ruta)
        if d.empty:
            continue
        crono, margen = columnas(d)
        d["text"] = [re.sub(r"\D", "", t) if re.fullmatch(r"\W?\d{8}\W?", t) else t for t in d.text]
        cods = d[d.text.str.match(CODIGO) & (d.left < crono * 0.35)].sort_values("top")
        tops = list(cods.top) + [10 ** 6]
        for i, (_, c) in enumerate(cods.iterrows()):
            banda = d[(d.top + d.height / 2 >= tops[i] - 15) & (d.top + d.height / 2 < tops[i + 1] - 15)]
            desc = " ".join(banda[(banda.left > c.left + c.width) & (banda.left < crono)].text)
            desc = re.sub(r"\s+[|o_\-—.:;']+(?=\s|$)", "", " " + desc).strip(" |_-—.:;'")
            cr = " ".join(banda[(banda.left >= crono) & (banda.left < margen)].text)
            mg = re.findall(r"\d{1,3}", " ".join(banda[banda.left >= margen].text))
            filas.append({"NALADISA_96": c.text, "DESCRIPCION_OCR": desc, "CRONOGRAMA": categoria(cr, b),
                          "MARGEN_INICIAL": mg[0] if mg and b == "B4" and categoria(cr, b) in ("D5", "D6") else "", "PAGINA": int(ruta.stem[-4:])})
    return pd.DataFrame(filas)


def segunda_lectura(carpeta_txt, base, b):
    """Cronograma leído del OCR de texto corrido (primer pase), para completar los que faltan."""
    r = {}
    for ruta in sorted(Path(carpeta_txt).glob(f"{base}_[0-9][0-9][0-9][0-9].txt")):
        for linea in ruta.read_text(encoding="utf-8").splitlines():
            m = re.match(r"[\s|¡_\-.']*(\d{8})\b(.*)", linea)
            if m:
                c = categoria(m.group(2)[-25:], b)
                if c:
                    r.setdefault(m.group(1), c)
    return r


def main(carpeta, salida, carpeta_txt=None):
    for base, (nombre, b) in APENDICES.items():
        d = leer(carpeta, base, b)
        if d.empty:
            continue
        d = d.drop_duplicates("NALADISA_96")
        d["LECTURA"] = "columnas"
        if carpeta_txt:
            r = segunda_lectura(carpeta_txt, base, b)
            vacio = d.CRONOGRAMA == ""
            d.loc[vacio, "CRONOGRAMA"] = d.loc[vacio, "NALADISA_96"].map(r).fillna("")
            d.loc[vacio & (d.CRONOGRAMA != ""), "LECTURA"] = "texto corrido"
            faltan = sorted(set(r) - set(d.NALADISA_96))
            extra = pd.DataFrame({"NALADISA_96": faltan, "DESCRIPCION_OCR": "", "CRONOGRAMA": [r[c] for c in faltan],
                                  "MARGEN_INICIAL": "", "PAGINA": "", "LECTURA": "texto corrido"})
            d = pd.concat([d, extra]).sort_values("NALADISA_96")
        d["PAGINA"] = d.PAGINA.astype(str).str.replace(".0", "", regex=False)
        nomen = Path(__file__).resolve().parent.parent / "docs" / "ace72" / "tablas" / "colombia_otorga_al_mercosur.csv"
        validos = set(pd.read_csv(nomen, dtype=str).NALADISA_96.str.replace(".", "", regex=False))
        malos = ~d.NALADISA_96.isin(validos)
        print(nombre, "códigos que no existen en la NALADISA 96 (error de OCR, se descartan):", int(malos.sum()))
        d = d[~malos]
        d.to_csv(Path(salida) / f"{nombre}.csv", index=False, encoding="utf-8-sig", quoting=csv.QUOTE_MINIMAL)
        print(nombre, len(d), "productos;", (d.CRONOGRAMA == "").sum(), "sin cronograma;",
              d.CRONOGRAMA.value_counts().to_dict())
    unir(salida)


# Año en que el margen llega a 100% según el Anexo II-B (A = inmediata, al entrar en vigor el Acuerdo)
CIEN = {"A": "2006", "B3": "2012", "B4": "2012", "D5": "2017", "D6": "2017"}
CIEN.update({f"C3{x}": "2012" for x in "abcdefgh"})


def unir(salida):
    """Una fila por producto con lo que da cada país al otro."""
    s = Path(salida)
    pe = pd.read_csv(s / "peru_a_paraguay.csv", dtype=str).fillna("")
    py = pd.read_csv(s / "paraguay_a_peru.csv", dtype=str).fillna("")
    d = pe[["NALADISA_96", "DESCRIPCION_OCR", "CRONOGRAMA", "MARGEN_INICIAL"]].rename(columns={
        "CRONOGRAMA": "PERU_A_PARAGUAY", "MARGEN_INICIAL": "PERU_MARGEN_INICIAL"}).merge(
        py[["NALADISA_96", "DESCRIPCION_OCR", "CRONOGRAMA"]].rename(columns={
            "CRONOGRAMA": "PARAGUAY_A_PERU", "DESCRIPCION_OCR": "D2"}), on="NALADISA_96", how="outer").fillna("")
    d["DESCRIPCION_OCR"] = [a if len(a) >= len(b) else b for a, b in zip(d.DESCRIPCION_OCR, d.D2)]
    d["PERU_100_DESDE"] = d.PERU_A_PARAGUAY.map(CIEN).fillna("")
    d["PARAGUAY_100_DESDE"] = d.PARAGUAY_A_PERU.map(CIEN).fillna("")
    cap = d.NALADISA_96.str[:2].astype(int)
    d["NOTA"] = ["Textil: programa en suspenso entre Perú y Paraguay salvo los productos del Apéndice 2 del Anexo V"
                 if 50 <= c <= 63 else "" for c in cap]
    cols = ["NALADISA_96", "DESCRIPCION_OCR", "PERU_A_PARAGUAY", "PERU_MARGEN_INICIAL", "PERU_100_DESDE",
            "PARAGUAY_A_PERU", "PARAGUAY_100_DESDE", "NOTA"]
    d[cols].sort_values("NALADISA_96").to_csv(s / "preferencias_paraguay_peru.csv", index=False, encoding="utf-8-sig")
    print("preferencias_paraguay_peru:", len(d), "productos")


if __name__ == "__main__":
    main(*sys.argv[1:])
