"""Pasa a tabla las preferencias del ACE 72 (MERCOSUR–Colombia) que importan a Paraguay.

Lee el texto de los apéndices del Anexo II (versión de la ALADI, pasada a texto con pdftotext -layout):
  - Apéndice 1: preferencias que otorga Colombia (una columna por país del MERCOSUR; se toma la de Paraguay).
  - Apéndice 2 Paraguay–Colombia: preferencias que otorga Paraguay a Colombia.
Escribe una fila por código NALADISA 96 con su categoría de cronograma y la nota explicativa, si tiene.

Uso: python python/ace72_preferencias.py <texto_apendice_1> <texto_apendice_2_PY_CO> <carpeta_salida>
"""
import re
import sys
from pathlib import Path

import pandas as pd

FILA = re.compile(r"^\s*(\d{8})\s+(.*?)\s{2,}(\S.*)$")


def columnas(resto):
    """Separa lo que queda después de la descripción en bloques (cronograma y nota)."""
    return [c for c in re.split(r"\s{2,}", resto.strip()) if c]


CRONO = re.compile(r"[A-E]|Ver Ap[ée]ndice.*|Ver Nota.*|Excluid.*")
PAISES = ["ARGENTINA", "BRASIL", "PARAGUAY", "URUGUAY"]


def unir_ver(cols):
    """Une "Ver Apéndice" con su número cuando quedaron separados."""
    res = []
    for c in cols:
        if res and re.fullmatch(r"\d+(\.\d+)?", c) and res[-1].startswith("Ver"):
            res[-1] += " " + c
        else:
            res.append(c)
    return res


def leer(ruta, n_paises):
    filas = []
    for linea in Path(ruta).read_text(encoding="utf-8", errors="replace").splitlines():
        m = FILA.match(linea)
        if not m:
            continue
        codigo, desc, resto = m.groups()
        filas.append((codigo, desc.strip(), columnas(resto), linea))
    return filas


def arreglar(d, cols):
    """Casos en que el cronograma quedó pegado a la descripción (un solo espacio entre ambos)."""
    pat = r"\s(Ver Ap[ée]ndice[\s\d.]*|Ver Nota|Bienes [Uu]sados\.?)\s*(\(\d+\))?\s*$"
    for i in d.index:
        if all(pd.isna(d.at[i, c]) or d.at[i, c] == "" for c in cols):
            m = re.search(pat, d.at[i, "DESCRIPCION"])
            if m:
                d.at[i, "DESCRIPCION"] = d.at[i, "DESCRIPCION"][:m.start()].strip()
                for c in cols:
                    d.at[i, c] = m.group(1).strip()
    return d


def main(ap1, ap2, salida):
    salida = Path(salida)
    salida.mkdir(parents=True, exist_ok=True)
    # Apéndice 1: Colombia → Argentina, Brasil, Paraguay y Uruguay, en ese orden. Las columnas cambian de lugar entre
    # páginas, así que se leen en orden: cada bloque que no es una nota "(n)" es el cronograma del país siguiente, y
    # las notas "(n)" van con el país anterior.
    out = []
    for codigo, desc, cols, _ in leer(ap1, 4):
        reg = {"NALADISA_96": codigo, "DESCRIPCION": desc}
        i = -1
        for c in unir_ver(cols):
            if re.fullmatch(r"(\(\d+\)\s*)+", c):
                if i >= 0:
                    k = f"NOTA_{PAISES[i]}"
                    reg[k] = (reg.get(k, "") + " " + c).strip()
            elif not CRONO.fullmatch(c):
                reg["DESCRIPCION"] += " " + c     # resto de la descripción, separado por espacios
            elif i < 3:
                i += 1
                reg[f"CRONOGRAMA_{PAISES[i]}"] = c
        out.append(reg)
    d1 = arreglar(pd.DataFrame(out), [f"CRONOGRAMA_{x}" for x in PAISES])
    d1["CRONOGRAMA_PARAGUAY"] = d1["CRONOGRAMA_PARAGUAY"].str.replace(r"^Ver Ap[ée]ndice.*", "Ver Apéndice 3.3", regex=True)
    d1.to_csv(salida / "colombia_otorga_al_mercosur.csv", index=False, encoding="utf-8-sig")
    # Apéndice 2 PY–CO: una sola columna de cronograma y la nota
    out2 = []
    for codigo, desc, cols, _ in leer(ap2, 1):
        cols = unir_ver(cols)
        while cols and not CRONO.fullmatch(cols[0]):
            desc += " " + cols.pop(0)
        out2.append({"NALADISA_96": codigo, "DESCRIPCION": desc, "CRONOGRAMA": cols[0] if cols else "",
                     "NOTA": " ".join(cols[1:])})
    d2 = arreglar(pd.DataFrame(out2), ["CRONOGRAMA"])
    d2.to_csv(salida / "paraguay_otorga_a_colombia.csv", index=False, encoding="utf-8-sig")
    print(len(d1), "filas Colombia →", len(d2), "filas Paraguay →")
    print(d1.filter(like="CRONOGRAMA").apply(lambda s: s.value_counts().head(8)).to_string())
    print("sin cronograma Paraguay:", d1["CRONOGRAMA_PARAGUAY"].isna().sum())
    print(d2["CRONOGRAMA"].value_counts().head(15).to_string())


if __name__ == "__main__":
    main(*sys.argv[1:4])


def leer_varios_cronogramas(ruta):
    """Apéndices 3.x y 4.x: un producto puede tener varias filas (por ejemplo, dentro y fuera de un contingente).
    Las columnas se ubican por la posición de los títulos, que cambian en cada página; las líneas sin código siguen
    la fila anterior."""
    filas, lim = [], None
    for linea in Path(ruta).read_text(encoding="utf-8", errors="replace").splitlines():
        if "Cronograma" in linea and "Descripci" in linea:
            lim = [linea.index("Descripci") - 2, linea.index("Observaciones") - 2,
                   linea.index("Cronograma") - 8, linea.index("Notas") - 4]
            continue
        if lim is None or not linea.strip():
            continue
        m = re.match(r"^\s*(\d{6,8})\s", linea)
        if m:
            filas.append({"NALADISA_96": m.group(1), "DESCRIPCION": "", "OBSERVACIONES": "", "CRONOGRAMA": "", "NOTAS": ""})
        elif not filas or re.match(r"^\s*(ANEXO|Anexo|Ap[ée]ndice|Desgravaci|Preferencias|\d+\s*$)", linea):
            continue
        for x in re.finditer(r"\S+(?: \S+)*", linea):
            a, t = x.start(), x.group()
            if m and a == m.start(1):
                continue
            col = ("DESCRIPCION" if a < lim[1] else "OBSERVACIONES" if a < lim[2] else
                   "CRONOGRAMA" if a < lim[3] else "NOTAS")
            if a < lim[0]:
                continue
            filas[-1][col] = (filas[-1][col] + " " + t).strip()
    return pd.DataFrame(filas)


def leer_requisitos(ruta):
    """Apéndice 3.x del Anexo IV: requisito específico de origen por código NALADISA."""
    filas = []
    for linea in Path(ruta).read_text(encoding="utf-8", errors="replace").splitlines():
        m = re.match(r"^\s*(\d{4,8}|Cap[íi]tulo \d+)\s{2,}(\S.*)$", linea)
        if m:
            filas.append({"NALADISA_96": m.group(1), "REQUISITO_ESPECIFICO": m.group(2).strip()})
        elif filas and linea.strip() and not re.search(r"Anexo IV|Art[íi]culo 5|Ap[ée]ndice|Requisitos bilaterales|NALADISA|REQUISITO", linea) \
                and linea.startswith(" " * 10):
            filas[-1]["REQUISITO_ESPECIFICO"] += " " + linea.strip()
    return pd.DataFrame(filas)


def ordenar_cronograma(d):
    """Deja en CRONOGRAMA solo la categoría (A a E o «Ver nota») y pasa el resto a NOTAS."""
    for i in d.index:
        m = re.match(r"^(Ver nota|[A-E])\b\s*(.*)$", d.at[i, "CRONOGRAMA"])
        if m:
            d.at[i, "CRONOGRAMA"] = m.group(1)
            d.at[i, "NOTAS"] = (m.group(2) + " " + d.at[i, "NOTAS"]).strip()
    d["REQ"] = 0
    return d.drop(columns="REQ")


def armar_tablas(txt, salida):
    """txt: función que devuelve la ruta del texto de un documento por su id."""
    salida = Path(salida)
    salida.mkdir(parents=True, exist_ok=True)
    main(txt("anexo_2_ap_1"), txt("anexo_2_ap_2_py"), salida)
    ordenar_cronograma(leer_varios_cronogramas(txt("anexo_2_ap_3_3"))).to_csv(
        salida / "colombia_a_paraguay_varios_cronogramas.csv", index=False, encoding="utf-8-sig")
    ordenar_cronograma(leer_varios_cronogramas(txt("anexo_2_ap_4_3"))).to_csv(
        salida / "paraguay_a_colombia_varios_cronogramas.csv", index=False, encoding="utf-8-sig")
    r = leer_requisitos(txt("anexo_4_ap_3_3"))
    r["REQUISITO_ESPECIFICO"] = r["REQUISITO_ESPECIFICO"].str.replace(r"\s+\d{4}$", "", regex=True)
    r.to_csv(salida / "requisitos_origen_paraguay_colombia.csv", index=False, encoding="utf-8-sig")
