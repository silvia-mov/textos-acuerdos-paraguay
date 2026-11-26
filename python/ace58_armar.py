"""Arma la carpeta docs/ace58 con los textos del ACE 58 (MERCOSUR–Perú) publicados por la ALADI.

Uso (desde la raíz del repositorio):
    python python/ace58_armar.py <carpeta_con_los_PDF> <carpeta_ocr> [<carpeta_tsv>]

<carpeta_ocr>: como en ace35_armar.py. <carpeta_tsv>: OCR con posiciones (tesseract tsv) de los Apéndices I-B, II-B,
VII y VIII, con las líneas de la tabla borradas, para leer las listas Paraguay–Perú por columnas.
"""
import json
import re
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ace35_armar import leer, limpiar, fecha, sintesis  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
SALIDA = RAIZ / "docs" / "ace58"
ROMANO = {1: "I", 2: "II", 3: "III", 4: "IV", 5: "V", 6: "VI", 7: "VII", 8: "VIII", 9: "IX", 10: "X"}
ANEXOS = {
    1: "Anexo I – Referido al segundo párrafo del Artículo 3 (acuerdos bilaterales que se mantienen)",
    2: "Anexo II – Programa de Liberación Comercial",
    3: "Anexo III – Gravámenes y cargas que afectan al comercio bilateral (notas al Artículo 5)",
    4: "Anexo IV – Gravámenes a las exportaciones (notas al Artículo 7)",
    5: "Anexo V – Régimen de Origen",
    6: "Anexo VI – Régimen de Salvaguardias",
    7: "Anexo VII – Régimen de Solución de Controversias",
    8: "Anexo VIII – Régimen de Normas, Reglamentos Técnicos y Evaluación de la Conformidad",
    9: "Anexo IX – Régimen de Medidas Sanitarias y Fitosanitarias",
    10: "Anexo X – Medidas Especiales",
}
PAREJA = {"A": "Argentina, Brasil y Perú", "B": "Paraguay y Perú", "C": "Uruguay y Perú"}
APENDICES_II = {
    "1_A": "Apéndice I-A: desgravación de Argentina y Brasil a Perú",
    "2_A": "Apéndice II-A: desgravación de Perú a Argentina y Brasil",
    "3": "Apéndice III: Argentina a Perú, con dos o más cronogramas",
    "4": "Apéndice IV: Perú a Argentina, con dos o más cronogramas",
    "5": "Apéndice V: Brasil a Perú, con dos o más cronogramas",
    "6": "Apéndice VI: Perú a Brasil, con dos o más cronogramas",
    "1_B": "Apéndice I-B: desgravación de Paraguay a Perú",
    "2_B": "Apéndice II-B: desgravación de Perú a Paraguay",
    "7": "Apéndice VII: Paraguay a Perú, con dos o más cronogramas",
    "8": "Apéndice VIII: Perú a Paraguay, con dos o más cronogramas",
    "1_C": "Apéndice I-C: desgravación de Uruguay a Perú",
    "2_C": "Apéndice II-C: desgravación de Perú a Uruguay",
    "9": "Apéndice IX: Uruguay a Perú, con dos o más cronogramas",
    "10": "Apéndice X: Perú a Uruguay, con dos o más cronogramas",
}
APENDICES_V = {1: "Apéndice 1: requisitos específicos de origen Argentina–Brasil–Perú",
               2: "Apéndice 2: requisitos específicos de origen Paraguay–Perú",
               3: "Apéndice 3: requisitos específicos de origen Uruguay–Perú"}


def identificar(b):
    if b == "ACE_058_Acuerdo_Texto":
        return "acuerdo", "Texto del Acuerdo de Complementación Económica N° 58", "Acuerdo"
    if b == "ACE_058_ACR_001":
        return "acta_rectificacion_1", "Acta de Rectificación N° 1 del Acuerdo (2006)", "Acuerdo"
    m = re.fullmatch(r"ACE_058_00(\d)", b)
    if m:
        return f"protocolo_{m.group(1)}", f"Protocolo Adicional N° {m.group(1)}", "Protocolos adicionales"
    m = re.fullmatch(r"ACE_058_Anexo_0(\d\d)", b)
    if m:
        n = int(m.group(1))
        return f"anexo_{ROMANO[n].lower()}", ANEXOS[n], "Anexos"
    m = re.fullmatch(r"ACE_058_Anexo_002_([ABC])", b)
    if m:
        return f"anexo_ii_{m.group(1).lower()}", f"Anexo II-{m.group(1)} – Cronogramas de desgravación {PAREJA[m.group(1)]}", "Programa de Liberación"
    m = re.fullmatch(r"ACE_058_Anexo_002_[ABC]_Apen_0(\d\d)(?:_([ABC]))?(_Rectificado)?", b)
    if m:
        k = str(int(m.group(1))) + (f"_{m.group(2)}" if m.group(2) else "")
        rect = " (rectificado)" if m.group(3) else ""
        return f"anexo_ii_apendice_{k.lower()}", "Anexo II, " + APENDICES_II[k] + rect, "Programa de Liberación"
    m = re.fullmatch(r"ACE_058_Anexo_005_Apen_00(\d)", b)
    if m:
        return f"anexo_v_apendice_{m.group(1)}", "Anexo V, " + APENDICES_V[int(m.group(1))], "Anexos"
    raise ValueError(b)


def main(carpeta_pdf, ocr, tsv=None):
    carpeta_pdf, ocr = Path(carpeta_pdf), Path(ocr)
    (SALIDA / "textos").mkdir(parents=True, exist_ok=True)
    (SALIDA / "tablas").mkdir(exist_ok=True)
    filas, textos = [], []
    for pdf in sorted(carpeta_pdf.glob("ACE_058_*.pdf")):
        id_, titulo, grupo = identificar(pdf.stem)
        bruto, lectura = leer(pdf.stem, ocr)
        tabla = "apendice" in id_ or id_ == "anexo_iv"
        t = limpiar(bruto, tabla)
        sin = sintesis(bruto) if grupo == "Protocolos adicionales" else ""
        if id_ == "protocolo_1":            # no tiene «CONVIENEN»: es el texto completo del régimen
            sin = "Establece el Régimen de Solución de Controversias del Acuerdo (consultas, Comisión Administradora y arbitraje)."
        paginas = bruto.count("\f") + 1
        filas.append({"ID": id_, "TITULO": titulo, "SINTESIS": sin, "GRUPO": grupo, "FECHA": fecha(bruto),
                      "ARCHIVO_ALADI": pdf.name, "PAGINAS": paginas, "LECTURA": lectura, "LISTA": "sí" if tabla else ""})
        (SALIDA / "textos" / f"{id_}.txt").write_text(t, encoding="utf-8")
        textos.append({"id": id_, "titulo": titulo, "sintesis": sin, "grupo": grupo, "fecha": fecha(bruto),
                       "paginas": paginas, "lectura": lectura, "tabla": tabla, "texto": t})
    cat = pd.DataFrame(filas).sort_values(["GRUPO", "ID"])
    cat.to_csv(SALIDA / "catalogo.csv", index=False, encoding="utf-8-sig")
    (SALIDA / "textos.json").write_text(json.dumps([t for t in textos if not t["tabla"]], ensure_ascii=False),
                                        encoding="utf-8")
    (SALIDA / "indice.json").write_text(json.dumps([{k: v for k, v in t.items() if k != "texto"} for t in textos],
                                                   ensure_ascii=False), encoding="utf-8")
    print(len(cat), "documentos;", (cat.LECTURA == "OCR").sum(), "con OCR")
    if tsv:
        import ace58_listas
        ace58_listas.main(tsv, SALIDA / "tablas", ocr / "pag")


if __name__ == "__main__":
    main(*sys.argv[1:])
