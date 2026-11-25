"""Arma la carpeta docs/ace72 a partir de los archivos reunidos del ACE 72 (MERCOSUR–Colombia).

Uso (desde la raíz del repositorio):
    python python/ace72_armar.py <carpeta_con_inventario>

La carpeta de entrada tiene inventario.tsv (md5, ruta, bytes, tipo, páginas, caracteres, inicio del texto) y txt/<md5>.txt
con el texto de cada PDF (pdftotext -layout, o OCR con tesseract si el PDF era una imagen). Los PDF originales no se
publican: quedan en el release privado; la página enlaza a las fuentes oficiales.
"""
import json
import re
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ace72_catalogo_fuente import C  # noqa: E402
import ace72_preferencias as pref  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
SALIDA = RAIZ / "docs" / "ace72"
TABLAS = ("anexo_2_ap", "anexo_4_ap_2", "anexo_4_ap_3", "protocolo_1_lista", "anexo_3", "anexo_4_ap_1")


def limpiar(texto, tabla):
    texto = texto.replace("\f", "\n")
    lineas = [l.rstrip() for l in texto.splitlines()]
    if not tabla:
        lineas = [re.sub(r"\s{2,}", " ", l).strip() for l in lineas]
        lineas = [l for l in lineas if not re.fullmatch(r"\d{1,4}", l)]       # números de página sueltos
    texto = "\n".join(lineas)
    return re.sub(r"\n{3,}", "\n\n", texto).strip() + "\n"


def main(entrada):
    entrada = Path(entrada)
    inv = pd.read_csv(entrada / "inventario.tsv", sep="\t", header=None, dtype=str,
                      names=["MD5", "RUTA", "BYTES", "TIPO", "PAGINAS", "CARACTERES", "INICIO"], quoting=3).fillna("")
    filas = []
    for _, r in inv.iterrows():
        id_, titulo, grupo, fecha, estado = C[r.MD5[:8]]
        filas.append({"ID": id_, "TITULO": titulo, "GRUPO": grupo, "FECHA": fecha, "ESTADO": estado,
                      "ARCHIVO_ORIGINAL": Path(r.RUTA).name, "PAGINAS": r.PAGINAS,
                      "LECTURA": "" if r.TIPO != "%PDF" else ("texto del PDF" if int(r.CARACTERES or 0) >= 50 else "OCR"),
                      "MD5": r.MD5})
    cat = pd.DataFrame(filas).sort_values(["GRUPO", "ID", "ESTADO"])
    (SALIDA / "textos").mkdir(parents=True, exist_ok=True)
    cat.to_csv(SALIDA / "catalogo.csv", index=False, encoding="utf-8-sig")
    textos = []
    for _, r in cat[cat.ESTADO == "texto"].drop_duplicates("ID").iterrows():
        bruto = (entrada / "txt" / f"{r.MD5}.txt").read_text(encoding="utf-8", errors="replace")
        t = limpiar(bruto, r.ID.startswith(TABLAS))
        (SALIDA / "textos" / f"{r.ID}.txt").write_text(t, encoding="utf-8")
        textos.append({"id": r.ID, "titulo": r.TITULO, "grupo": r.GRUPO, "fecha": r.FECHA, "paginas": r.PAGINAS,
                       "tabla": r.ID.startswith(TABLAS), "texto": t})
    # Para el buscador de la página van los textos corridos; las listas de productos se buscan en la tabla
    (SALIDA / "textos.json").write_text(json.dumps([t for t in textos if not t["tabla"]], ensure_ascii=False),
                                        encoding="utf-8")
    (SALIDA / "indice.json").write_text(json.dumps([{k: v for k, v in t.items() if k != "texto"} for t in textos],
                                                   ensure_ascii=False), encoding="utf-8")
    pref.armar_tablas(lambda i: SALIDA / "textos" / f"{i}.txt", SALIDA / "tablas")
    unir_paraguay(SALIDA / "tablas")
    (SALIDA / "estructura.json").write_text(json.dumps(estructura(SALIDA / "textos" / "acuerdo.txt"), ensure_ascii=False),
                                            encoding="utf-8")
    d = pd.read_csv(SALIDA / "tablas" / "preferencias_paraguay_colombia.csv", dtype=str).fillna("")
    (SALIDA / "preferencias.json").write_text(json.dumps(d.values.tolist(), ensure_ascii=False), encoding="utf-8")
    print(len(cat), "archivos;", len(textos), "textos")


def unir_paraguay(carpeta):
    """Una fila por producto: qué preferencia da Colombia a Paraguay, cuál da Paraguay a Colombia y el requisito de
    origen bilateral, si lo hay. Los productos con más de un cronograma muestran el detalle de los Apéndices 3.3 y 4.3."""
    co = pd.read_csv(carpeta / "colombia_otorga_al_mercosur.csv", dtype=str).fillna("")
    py = pd.read_csv(carpeta / "paraguay_otorga_a_colombia.csv", dtype=str).fillna("")
    v33 = pd.read_csv(carpeta / "colombia_a_paraguay_varios_cronogramas.csv", dtype=str).fillna("")
    v43 = pd.read_csv(carpeta / "paraguay_a_colombia_varios_cronogramas.csv", dtype=str).fillna("")
    reo = pd.read_csv(carpeta / "requisitos_origen_paraguay_colombia.csv", dtype=str).fillna("")

    def detalle(v):
        return v.assign(T=lambda x: (x.OBSERVACIONES + ": " + x.CRONOGRAMA + " " + x.NOTAS).str.strip(" :")) \
            .groupby("NALADISA_96")["T"].apply(lambda s: " | ".join(s)).to_dict()

    d33, d43 = detalle(v33), detalle(v43)
    d = co[["NALADISA_96", "DESCRIPCION", "CRONOGRAMA_PARAGUAY", "NOTA_PARAGUAY"]].rename(
        columns={"CRONOGRAMA_PARAGUAY": "COLOMBIA_A_PARAGUAY", "NOTA_PARAGUAY": "COLOMBIA_NOTA"})
    d = d.merge(py[["NALADISA_96", "CRONOGRAMA", "NOTA"]].rename(
        columns={"CRONOGRAMA": "PARAGUAY_A_COLOMBIA", "NOTA": "PARAGUAY_NOTA"}), on="NALADISA_96", how="outer")
    d["COLOMBIA_DETALLE"] = d.NALADISA_96.map(d33).fillna("")
    d["PARAGUAY_DETALLE"] = d.NALADISA_96.map(d43).fillna("")
    r = dict(zip(reo.NALADISA_96, reo.REQUISITO_ESPECIFICO))
    d["REQUISITO_ORIGEN_BILATERAL"] = [r.get(c) or r.get(c[:6]) or r.get(c[:4]) or "" for c in d.NALADISA_96]
    d.fillna("").to_csv(carpeta / "preferencias_paraguay_colombia.csv", index=False, encoding="utf-8-sig")



def estructura(ruta):
    """Títulos del Acuerdo con su nombre y sus artículos."""
    lineas = [l.strip() for l in Path(ruta).read_text(encoding="utf-8").splitlines()]
    tit, actual = [], None
    for i, l in enumerate(lineas):
        if re.fullmatch(r"T[ÍI]TULO [IVXLC]+", l):
            nombre = next((x for x in lineas[i + 1:i + 4] if x), "")
            actual = {"titulo": l.replace("TITULO", "TÍTULO"), "nombre": nombre.capitalize(), "articulos": []}
            tit.append(actual)
        m = re.match(r"Art[íi]culo (\d+)", l)
        if m and actual is not None:
            n = int(m.group(1))
            if not actual["articulos"] or n == max(actual["articulos"]) + 1:
                actual["articulos"].append(n)
        elif m and actual is None:
            actual = {"titulo": "TÍTULO I", "nombre": "Objetivos", "articulos": [int(m.group(1))]}
            tit.append(actual)
    return tit


if __name__ == "__main__":
    main(sys.argv[1])
