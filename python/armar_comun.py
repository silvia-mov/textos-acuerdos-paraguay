"""Parte común para armar docs/<acuerdo>: catálogo, textos (texto del PDF u OCR), índice y textos.json.

Cada acuerdo tiene su script (ace36_armar.py, ace59_armar.py…) con una función identificar(nombre_de_archivo) que
devuelve (id, título, grupo, es_lista) o None para omitir el archivo.
"""
import json
from pathlib import Path

import pandas as pd

from ace35_armar import leer, limpiar, fecha, sintesis

RAIZ = Path(__file__).resolve().parent.parent


def armar(carpeta, prefijo, identificar, carpeta_pdf, ocr, sin_transcribir=None, sintesis_fija=None):
    """sin_transcribir: {nombre_de_archivo: motivo} para los archivos que están en la carpeta pero no se pasaron a
    texto (por ejemplo, listas entre otros países). Quedan en el catálogo con su motivo."""
    salida = RAIZ / "docs" / carpeta
    (salida / "textos").mkdir(parents=True, exist_ok=True)
    (salida / "tablas").mkdir(exist_ok=True)
    carpeta_pdf, ocr = Path(carpeta_pdf), Path(ocr)
    sin_transcribir = sin_transcribir or {}
    filas, textos = [], []
    for pdf in sorted(carpeta_pdf.glob(f"{prefijo}*.pdf")):
        r = identificar(pdf.stem)
        if r is None:
            continue
        id_, titulo, grupo, lista = r
        if pdf.stem in sin_transcribir:
            filas.append({"ID": id_, "TITULO": titulo, "SINTESIS": "", "GRUPO": grupo, "FECHA": "",
                          "ARCHIVO_ALADI": pdf.name, "PAGINAS": "", "LECTURA": sin_transcribir[pdf.stem], "LISTA": "sí"})
            continue
        bruto, lectura = leer(pdf.stem, ocr)
        if bruto is None:
            print("sin texto:", pdf.stem)
            continue
        t = limpiar(bruto, lista)
        sin = sintesis(bruto) if grupo == "Protocolos adicionales" and id_.count("_") == 1 else ""
        sin = (sintesis_fija or {}).get(id_, sin)
        f = fecha(bruto)
        paginas = bruto.count("\f") + 1
        filas.append({"ID": id_, "TITULO": titulo, "SINTESIS": sin, "GRUPO": grupo, "FECHA": f,
                      "ARCHIVO_ALADI": pdf.name, "PAGINAS": paginas, "LECTURA": lectura, "LISTA": "sí" if lista else ""})
        (salida / "textos" / f"{id_}.txt").write_text(t, encoding="utf-8")
        textos.append({"id": id_, "titulo": titulo, "sintesis": sin, "grupo": grupo, "fecha": f, "paginas": paginas,
                       "lectura": lectura, "tabla": lista, "texto": t})
    cat = pd.DataFrame(filas).sort_values(["GRUPO", "ID"])
    cat["PAGINAS"] = cat.PAGINAS.astype(str).str.replace(".0", "", regex=False).replace("nan", "")
    cat.to_csv(salida / "catalogo.csv", index=False, encoding="utf-8-sig")
    (salida / "textos.json").write_text(json.dumps([t for t in textos if not t["tabla"]], ensure_ascii=False),
                                        encoding="utf-8")
    (salida / "indice.json").write_text(json.dumps([{k: v for k, v in t.items() if k != "texto"} for t in textos],
                                                   ensure_ascii=False), encoding="utf-8")
    print(carpeta, len(cat), "documentos;", (cat.LECTURA == "OCR").sum(), "con OCR;", len(sin_transcribir),
          "sin transcribir")
    return cat
