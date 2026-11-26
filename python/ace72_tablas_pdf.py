"""Lee las listas del ACE 72 directamente de los PDF de la ALADI, celda por celda (pdfplumber usa los recuadros
dibujados en el PDF), en lugar de adivinar las columnas en el texto.

Uso: python python/ace72_tablas_pdf.py <carpeta_con_los_PDF_de_la_ALADI> <carpeta_salida>
"""
import re
import sys
from pathlib import Path

import pandas as pd
import pdfplumber

CODIGO = re.compile(r"^\d{4,8}$|^Cap[íi]tulo \d+$")


def limpio(x):
    return re.sub(r"\s+", " ", (x or "").replace("\n", " ")).strip()


def filas_de(pdf_path):
    """Todas las filas de todas las tablas del PDF, con el encabezado de cada página."""
    out = []
    with pdfplumber.open(pdf_path) as pdf:
        for n, p in enumerate(pdf.pages, start=1):
            for t in p.extract_tables():
                for f in t:
                    out.append((n, [limpio(c) for c in f]))
    return out


def tabla(pdf_path, columnas, n_cols):
    """Arma un DataFrame con las filas que empiezan con un código; las filas sin código continúan la anterior
    (una celda partida entre dos páginas)."""
    filas, prev = [], None
    for pag, f in filas_de(pdf_path):
        if len(f) != n_cols:
            continue
        if CODIGO.match(f[0]):
            prev = dict(zip(columnas, f), PAGINA=pag)
            filas.append(prev)
        elif prev is not None and not f[0] and any(f[1:]) and not any("NALADISA" in c or "Cronograma" in c for c in f):
            for c, v in zip(columnas[1:], f[1:]):
                if v:
                    prev[c] = (prev[c] + " " + v).strip()
    return pd.DataFrame(filas)


def apendice_1(pdf):
    cols = ["NALADISA_96", "DESCRIPCION"] + [f"{k}_{p}" for p in ("ARGENTINA", "BRASIL", "PARAGUAY", "URUGUAY")
                                             for k in ("CRONOGRAMA", "NOTA")]
    return tabla(pdf, cols, 10)


def apendice_2(pdf):
    """El orden de las columnas cambia según el país (Argentina y Uruguay ponen la nota antes de la descripción)."""
    with pdfplumber.open(pdf) as d:
        enc = [limpio(c) for c in d.pages[0].extract_tables()[0][0]]
    nombres = []
    for c in enc:
        nombres.append("NALADISA_96" if c.startswith("Código") else "DESCRIPCION" if c.startswith("Descripci")
                       else "CRONOGRAMA" if c.startswith("Cronograma") else "NOTA")
    return tabla(pdf, nombres, len(nombres))[["NALADISA_96", "DESCRIPCION", "CRONOGRAMA", "NOTA", "PAGINA"]]


def varios_cronogramas(pdf):
    return tabla(pdf, ["NALADISA_96", "DESCRIPCION", "OBSERVACIONES", "CRONOGRAMA", "NOTAS"], 5)


def requisitos(pdf):
    return tabla(pdf, ["NALADISA_96", "REQUISITO_ESPECIFICO"], 2)


def control(nombre, d, cols_crono):
    print(f"{nombre}: {len(d)} filas, {d.NALADISA_96.nunique()} códigos")
    for c in cols_crono:
        vac = (d[c] == "").sum()
        print(f"   {c}: vacíos {vac}; valores {d[c].value_counts().head(8).to_dict()}")


def main(carpeta, salida):
    carpeta, salida = Path(carpeta), Path(salida)
    salida.mkdir(parents=True, exist_ok=True)
    pdf = lambda n: next(carpeta.glob(n))
    a1 = apendice_1(pdf("02_Anexo_II_Ap_1.pdf"))
    control("Apéndice 1 (Colombia)", a1, [c for c in a1 if c.startswith("CRONOGRAMA")])
    a1.drop(columns="PAGINA").to_csv(salida / "colombia_otorga_al_mercosur.csv", index=False, encoding="utf-8-sig")
    for pais, arch in [("argentina", "03_Anexo_II_Ap_2_AR_CO.pdf"), ("brasil", "04_Anexo_II_Ap_2_BR_CO.pdf"),
                       ("paraguay", "05_Anexo_II_Ap_2_PY_CO.pdf"), ("uruguay", "06_Anexo_II_Ap_2_UY_CO.pdf")]:
        d = apendice_2(pdf(arch))
        control(f"Apéndice 2 ({pais})", d, ["CRONOGRAMA"])
        d.drop(columns="PAGINA").to_csv(salida / f"{pais}_otorga_a_colombia.csv", index=False, encoding="utf-8-sig")
    for nom, arch in [("colombia_a_paraguay_varios_cronogramas", "09_Anexo_II_Ap_3_3.pdf"),
                      ("paraguay_a_colombia_varios_cronogramas", "13_Anexo_II_Ap_4_3.pdf")]:
        d = varios_cronogramas(pdf(arch))
        control(nom, d, ["CRONOGRAMA"])
        d.drop(columns="PAGINA").to_csv(salida / f"{nom}.csv", index=False, encoding="utf-8-sig")
    r = requisitos(pdf("19_Anexo_IV_Ap_3_3.pdf"))
    print("Requisitos de origen Paraguay–Colombia:", len(r))
    r.drop(columns="PAGINA").to_csv(salida / "requisitos_origen_paraguay_colombia.csv", index=False, encoding="utf-8-sig")


if __name__ == "__main__":
    main(*sys.argv[1:3])
