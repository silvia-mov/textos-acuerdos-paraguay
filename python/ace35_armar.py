"""Arma la carpeta docs/ace35 con los textos del ACE 35 (MERCOSUR–Chile) publicados por la ALADI.

Uso (desde la raíz del repositorio):
    python python/ace35_armar.py <carpeta_con_los_PDF> <carpeta_ocr>

<carpeta_ocr> tiene <archivo>.txt (pdftotext -layout, PDF con texto) o pag/<archivo>_NNNN.txt (OCR con tesseract,
una página por archivo, PDF escaneados). Los PDF no se publican: la página enlaza a la ALADI.
"""
import json
import re
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ace35_tablas_pdf as tpdf  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
SALIDA = RAIZ / "docs" / "ace35"

ANEXOS = {
    "1": "Anexo 1 – Preferencias del patrimonio histórico (márgenes que suben hasta 100 % en 2004)",
    "2": "Anexo 2 – Productos con desgravación especial a 10 años (desde 30 %)",
    "3": "Anexo 3 – Productos con desgravación especial a 10 años (desde 0 %)",
    "4": "Anexo 4 – Lista de autopartes de Paraguay (comercio Chile–Paraguay)",
    "5": "Anexo 5 – Productos con tratamiento especial a 10 años (cupos)",
    "6": "Anexo 6 – Productos sensibles: desgravación del año 10 al 15 (100 % en 2011)",
    "7": "Anexo 7 – Productos con tratamiento especial a 15 años (cupos)",
    "8": "Anexo 8 – Productos sensibles: desgravación del año 11 al 16 (100 % en 2012)",
    "9": "Anexo 9 – Productos de incorporación diferida: trigo y harina de trigo (100 % desde el 1/1/2014)",
    "P": "Protocolo sobre Integración Física",
    "15_pt": "Anexo 15 – Acuerdos del MERCOSUR sobre transporte (Artículo 38; versión en portugués)",
    "15": "Anexo 15 – Acuerdos del MERCOSUR sobre transporte (Artículo 38)",
    "10": "Anexo 10 – Productos con márgenes de preferencia iniciales propios",
    "11": "Anexo 11 – Aranceles máximos de Argentina para productos de Chile",
    "12_AR": "Anexo 12 – Aranceles residuales para Chile: Argentina",
    "12_BR": "Anexo 12 – Aranceles residuales para Chile: Brasil",
    "12_PY": "Anexo 12 – Aranceles residuales para Chile: Paraguay",
    "12_UY": "Anexo 12 – Aranceles residuales para Chile: Uruguay",
    "13": "Anexo 13 – Régimen de Origen (texto original de 1996; reemplazado por el Protocolo 69)",
    "14": "Anexo 14 – Régimen de Solución de Controversias",
}
MESES = "enero febrero marzo abril mayo junio julio agosto setiembre septiembre octubre noviembre diciembre".split()


def identificar(b):
    """Nombre del archivo de la ALADI -> (id, título base, grupo)."""
    if b == "ACE_035_Acuerdo":
        return "acuerdo", "Texto del Acuerdo de Complementación Económica N° 35", "Acuerdo"
    m = re.fullmatch(r"ACE_035_Anexo_(\w+)", b)
    if m:
        k = m.group(1)
        grupo = "Anexos del Programa de Liberación" if k not in ("13", "14", "P", "15_pt", "15") else "Origen y controversias"
        return f"anexo_{k.lower()}", ANEXOS[k], grupo
    if b == "ACE_035_064_01_Decision_CA_02_2024":
        return ("protocolo_64_1_decision_02_2024", "Decisión N° 02/2024 de la Comisión Administradora del Acuerdo de Libre Comercio "
                "Brasil–Chile: cosméticos (base del Protocolo 64.1)", "Protocolos adicionales")
    if b == "ACE_035_Ley_PY_1038_1997":
        return "ley_py_1038_1997", "Paraguay, Ley N° 1.038/1997: aprueba el Acuerdo y el Protocolo sobre Integración Física", "Normas de Paraguay"
    if b == "ACE_035_Guia_BR_Ficha_Tecnica":
        return "guia_brasil_ficha_tecnica", "Brasil (MDIC): Ficha técnica del régimen de origen del ACE 35, 2025 (en portugués)", "Guías de otros países"
    if b == "ACE_035_Guia_BR_Manual_Origen":
        return "guia_brasil_manual_origen", "Brasil (MDIC): Manual del Régimen de Origen del ACE 35 (en portugués)", "Guías de otros países"
    if b == "ACE_035_Notas_PY":
        return "notas_paraguay", "Notas complementarias de Paraguay (Artículos 5, 6 y 7)", "Acuerdo"
    m = re.fullmatch(r"ACE_035_Notas_Art(\d)", b)
    if m:
        return f"notas_art_{m.group(1)}", f"Notas complementarias al Artículo {m.group(1)}", "Acuerdo"
    m = re.fullmatch(r"ACE_035_ACR_00(\d)", b)
    if m:
        return f"acta_rectificacion_{m.group(1)}", f"Acta de Rectificación N° {m.group(1)} del Acuerdo", "Acuerdo"
    m = re.fullmatch(r"ACE_035_0(\d\d)(?:_(Rectificado(?:_002)?|ACR_00\d|Anexo_0\d|Ap_\d\d|An\d|\d\d))?", b)
    if m:
        n, resto = int(m.group(1)), m.group(2) or ""
        base, tit = f"protocolo_{n:02d}", f"Protocolo Adicional N° {n}"
        if resto.startswith("Rectificado") or not resto:
            return base, tit, "Protocolos adicionales"
        if resto.startswith("ACR"):
            return f"{base}_acta_rectificacion_{resto[-1]}", f"{tit}: Acta de Rectificación N° {resto[-1]}", "Protocolos adicionales"
        k = int(re.sub(r"\D", "", resto))
        if resto.startswith("Ap"):
            return f"{base}_apendice_{k}", f"{tit}: Apéndice {k}", "Protocolos adicionales"
        if resto.startswith(("Anexo", "An")):
            return f"{base}_anexo_{k}", f"{tit}: Anexo {k}", "Protocolos adicionales"
        return f"{base}_{k}", f"Protocolo Adicional al Protocolo N° {n} (N° {n}.{k})", "Protocolos adicionales"
    raise ValueError(b)


SICE = Path(__file__).resolve().parent / "datos" / "sice"
OTROS = Path(__file__).resolve().parent / "datos" / "otros"     # documentos de otras fuentes (Brasil)


def leer(b, ocr):
    """Prefiere la copia en texto del SICE (OEA) cuando existe; si no, el texto del PDF o el OCR."""
    p = SICE / f"{b}.txt"
    if p.exists():
        return p.read_text(encoding="utf-8"), "texto del SICE"
    p = OTROS / f"{b}.txt"
    if p.exists():
        return p.read_text(encoding="utf-8"), ("OCR" if "Decision" in b else "texto del documento")
    p = ocr / f"{b}.txt"
    if p.exists():
        return p.read_text(encoding="utf-8", errors="replace"), "texto del PDF"
    pags = sorted((ocr / "pag").glob(f"{b}_[0-9][0-9][0-9][0-9].txt"))
    if not pags:
        return None, ""
    return "\n\f".join(x.read_text(encoding="utf-8", errors="replace") for x in pags), "OCR"


def limpiar(texto, tabla):
    lineas = [l.rstrip() for l in texto.replace("\f", "\n").splitlines()]
    if not tabla:
        lineas = [re.sub(r"\s{2,}", " ", l).strip() for l in lineas]
        lineas = [l for l in lineas if not re.fullmatch(r"[-–_ ]*\d{1,4}[-–_ ]*", l)]   # números de página sueltos
    return re.sub(r"\n{3,}", "\n\n", "\n".join(lineas)).strip() + "\n"


def fecha(texto):
    t = re.sub(r"\s+", " ", texto[:1500])
    m = re.search(r"(\d{1,2})\s*[°º]?\s+de\s+(%s)\s+de\s+(\d{4})" % "|".join(MESES), t, re.I)
    if not m:
        return ""
    mes = MESES.index(m.group(2).lower()) + 1
    mes = mes if mes <= 9 else mes - 1        # «setiembre» y «septiembre» son el mes 9
    return f"{m.group(3)}-{mes:02d}-{int(m.group(1)):02d}"


def sintesis(texto):
    """Primer artículo del protocolo (lo que dispone), recortado."""
    t = re.sub(r"\s+", " ", texto)
    m = re.search(r"CONVIENEN\s*:?\s*(.*?)(?=Art[íi]culo\s*2\s*\S?\s*\.?\s*[-–]|EN FE DE LO CUAL|$)", t, re.I)
    if not m:
        return ""
    s = re.sub(r"^\W{0,3}(Art[íi]culo\W{0,2})?(1|[uú]nico)?\s*\S{0,2}\s*\.?\s*[-–]\s*", "", m.group(1).strip(), flags=re.I)
    s = re.sub(r"^.{0,6}?\.-\s*", "", s)          # restos del OCR de «Artículo 1°.-»
    return s[:280].rsplit(" ", 1)[0] + "…" if len(s) > 280 else s


def es_tabla(id_, texto):
    if re.fullmatch(r"anexo_(\d+|12_\w\w)", id_) and id_ not in ("anexo_13", "anexo_14", "anexo_9"):
        return True
    lineas = [l for l in texto.splitlines() if l.strip()]
    codigos = sum(1 for l in lineas if re.match(r"\s*[:|]?\s*\d{4}(\.\d{2}){0,3}\b", l))
    return len(lineas) > 150 and codigos / len(lineas) > 0.2


def main(carpeta_pdf, ocr):
    carpeta_pdf, ocr = Path(carpeta_pdf), Path(ocr)
    (SALIDA / "textos").mkdir(parents=True, exist_ok=True)
    filas, textos = [], []
    nombres = sorted({p.stem for p in carpeta_pdf.glob("ACE_035_*.pdf")} | {p.stem for p in SICE.glob("ACE_035_*.txt")}
                     | {p.stem for p in OTROS.glob("ACE_035_*.txt")})
    for b in nombres:
        pdf = carpeta_pdf / f"{b}.pdf"
        id_, titulo, grupo = identificar(b)
        bruto, lectura = leer(b, ocr)
        if bruto is None:
            print("sin texto todavía:", b)
            continue
        tabla = es_tabla(id_, bruto)
        t = limpiar(bruto, tabla)
        f = fecha(bruto)
        sin = sintesis(bruto) if grupo == "Protocolos adicionales" and "_" not in id_[10:] else ""
        paginas = len(re.findall(r"\f", bruto)) + 1 if lectura == "OCR" else bruto.count("\f") or 1
        filas.append({"ID": id_, "TITULO": titulo, "SINTESIS": sin, "GRUPO": grupo, "FECHA": f,
                      "ARCHIVO_ALADI": pdf.name if pdf.exists() else ("(solo SICE)" if (SICE / f"{b}.txt").exists() else "(Siscomex, Brasil)"), "PAGINAS": paginas, "LECTURA": lectura, "LISTA": "sí" if tabla else ""})
        (SALIDA / "textos" / f"{id_}.txt").write_text(t, encoding="utf-8")
        textos.append({"id": id_, "titulo": titulo, "sintesis": sin, "grupo": grupo, "fecha": f, "paginas": paginas,
                       "lectura": lectura, "tabla": tabla, "texto": t})
    cat = pd.DataFrame(filas).sort_values(["GRUPO", "ID"])
    cat.to_csv(SALIDA / "catalogo.csv", index=False, encoding="utf-8-sig")
    (SALIDA / "textos.json").write_text(json.dumps([t for t in textos if not t["tabla"]], ensure_ascii=False),
                                        encoding="utf-8")
    (SALIDA / "indice.json").write_text(json.dumps([{k: v for k, v in t.items() if k != "texto"} for t in textos],
                                                   ensure_ascii=False), encoding="utf-8")
    (SALIDA / "tablas").mkdir(exist_ok=True)
    tpdf.main(str(carpeta_pdf / "ACE_035_069.pdf"), str(SALIDA / "tablas"))
    n = anexo10_paraguay(SALIDA / "textos" / "anexo_10.txt", SALIDA / "tablas" / "chile_a_paraguay_margenes_iniciales_1996.csv")
    print("Anexo 10, Chile -> Paraguay:", n, "productos")
    print(len(cat), "documentos;", sum(t["tabla"] for t in textos), "listas;", (cat.LECTURA == "OCR").sum(), "con OCR")


def anexo10_paraguay(ruta, salida):
    """Anexo 10, «Preferencias otorgadas por Chile»: márgenes de preferencia iniciales (1996) que Chile dio a
    Paraguay. Se lee del OCR, así que códigos y descripciones pueden tener errores de lectura."""
    L = Path(ruta).read_text(encoding="utf-8").splitlines()
    ini = next(i for i, l in enumerate(L) if "OTORGADAS POR CHILE" in l)
    cod = desc = pref = None
    filas = []
    for l in L[ini:]:
        m = re.match(r"\W{0,3}[:;¡]?\s*[DO]?(\d{4}(?:[.,]\d{2}){0,3})\s*[:;¡¿]\s*(.*)", l)
        if m:
            cod = m.group(1).replace(",", ".")
            desc = re.split(r"\s[:;]\s|\s[:;]$", m.group(2))[0]
            desc = re.split(r"\s(?:[—_\-=]{2,}|[A-Z]{1,3}(?:\s[A-Z]{1,3}){2,}|\(?[0-9A-Z]{0,2}[Cc][O0]?n?t)", desc)[0].strip(" :;.+")
            pref = None
            continue
        m = re.search(r"[:;]\s*=?(\d{1,3})\s*[:;Ñ*y]?\s*$", l)
        if m:
            pref = m.group(1)
            continue
        if cod and pref and re.search(r"P\W*[AÁÑ]+\W*R+\W*[AÁ]+\W*G\W*U\W*A\W*Y", l, re.I):
            filas.append({"NALADISA_93": cod, "DESCRIPCION_OCR": desc, "MARGEN_INICIAL_1996": pref})
            pref = None
    d = pd.DataFrame(filas).drop_duplicates()
    d["FUENTE"] = "OCR de la ALADI (verificar)"
    sice = SICE / "anexo10_chile_a_paraguay_sice.csv"
    if sice.exists():       # la copia del SICE (a_10ch_1 a 7) está completa: reemplaza al OCR
        d = pd.read_csv(sice, dtype=str).rename(columns={"DESCRIPCION_SICE": "DESCRIPCION"})
        d["MARGEN_INICIAL_1996"] = d.MARGEN_INICIAL_1996.astype(float).astype(int).astype(str)
        d = d[["NALADISA_93", "DESCRIPCION", "MARGEN_INICIAL_1996", "OBSERVACION"]]
        d["FUENTE"] = "SICE (texto)"
        v = pd.read_csv(SICE / "anexo10_paraguay_a_chile_sice.csv", dtype=str).rename(columns={"DESCRIPCION_SICE": "DESCRIPCION"})
        v["MARGEN_INICIAL_1996"] = v.MARGEN_INICIAL_1996.astype(float).astype(int).astype(str)
        v[["NALADISA_93", "DESCRIPCION", "MARGEN_INICIAL_1996", "OBSERVACION"]].to_csv(
            Path(salida).parent / "paraguay_a_chile_margenes_iniciales_1996.csv", index=False, encoding="utf-8-sig")
    d.to_csv(salida, index=False, encoding="utf-8-sig")
    return len(d)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
