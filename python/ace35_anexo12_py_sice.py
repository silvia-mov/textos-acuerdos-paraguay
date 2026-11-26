"""ACE 35, Anexo 12 de Paraguay (Lista de Adecuación: arancel que Paraguay cobraba a Chile, 1996–2006), desde la copia
en texto del SICE (OEA). Uso: python3 ace35_anexo12_py_sice.py <PDF del SICE A_12PA.asp> <salida.csv>"""
import csv
import re
import sys

import pdfplumber

ANIOS = [str(a) for a in range(1996, 2007)]


def main(ruta, salida):
    filas = []
    with pdfplumber.open(ruta) as pdf:
        for p in pdf.pages:
            W = p.extract_words()
            cods = sorted((w for w in W if re.fullmatch(r"\d{4}\.\d{2}\.\d{2}", w["text"])), key=lambda w: w["top"])
            for i, c in enumerate(cods):
                y = c["top"]
                lo = (cods[i - 1]["top"] + y) / 2 if i else y - 30
                hi = (y + cods[i + 1]["top"]) / 2 if i + 1 < len(cods) else y + 30
                linea = sorted((w for w in W if abs(w["top"] - y) < 4), key=lambda w: w["x0"])
                n = next((w["text"] for w in linea if w["x1"] <= c["x0"] and w["text"].isdigit()), "")
                nums = [w for w in linea if w["x0"] > c["x1"] and re.fullmatch(r"\d+", w["text"])][-11:]
                valores = [w["text"] for w in nums]
                x_val = nums[0]["x0"] if nums else 1e9
                desc = " ".join(w["text"] for w in sorted((w for w in W if lo <= w["top"] < hi and c["x1"] < w["x0"] < x_val - 5),
                                                         key=lambda w: (round(w["top"]), w["x0"])))
                filas.append([n, c["text"], desc.replace("ï¿½", "?")] + valores)
    with open(salida, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.writer(fh)
        w.writerow(["N", "NALADISA_93", "DESCRIPCION"] + [f"ARANCEL_{a}" for a in ANIOS])
        w.writerows(filas)
    print(len(filas), "productos")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
