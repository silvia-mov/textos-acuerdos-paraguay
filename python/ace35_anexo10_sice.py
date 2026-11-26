"""ACE 35, Anexo 10, «Preferencias otorgadas por Chile», desde la copia en texto del SICE (OEA): las filas que Chile
otorga a Paraguay con su margen de preferencia inicial (1996). Reemplaza la lectura por OCR del PDF de la ALADI.
Uso: python3 ace35_anexo10_sice.py <PDF del SICE a_10ch_1.asp> <salida.csv>"""
import csv
import re
import sys

import pdfplumber

MOJIBAKE = {"ï¿½": "�"}


def main(ruta, salida):
    filas = []
    with pdfplumber.open(ruta) as pdf:
        for pn, p in enumerate(pdf.pages, 1):
            W = p.extract_words()
            hdr = {w["text"]: w["x0"] for w in W if w["text"] in ("GLOSA", "OBSERV", "TIPOOBS", "PORCAD")}
            x_glosa, x_obs, x_tipo = hdr.get("GLOSA", 265) - 40, hdr.get("OBSERV", 358) - 20, hdr.get("TIPOOBS", 419) - 5
            anc = sorted((w for w in W if w["text"] == "AAP.CE35"), key=lambda w: w["top"])
            for i, a in enumerate(anc):
                y = a["top"]
                lo = (anc[i - 1]["top"] + y) / 2 if i else y - 28
                hi = (y + anc[i + 1]["top"]) / 2 if i + 1 < len(anc) else y + 28
                linea = [w for w in W if abs(w["top"] - y) < 4]
                cod = next((w["text"] for w in linea if re.fullmatch(r"\d{4}\.\d{2}\.\d{2}", w["text"])), "")
                pct = next((w["text"] for w in linea if re.fullmatch(r"\d+\.\d\d", w["text"]) and w["x0"] > x_tipo + 20), "")
                banda = sorted((w for w in W if lo <= w["top"] < hi), key=lambda w: (round(w["top"]), w["x0"]))
                obs = " ".join(w["text"] for w in banda if x_obs <= w["x0"] < x_tipo)
                glosa = " ".join(w["text"] for w in banda if x_glosa <= w["x0"] < x_obs and abs(w["top"] - y) < 14)
                filas.append([cod, glosa.replace("ï¿½", "?"), pct, obs, pn])
    py = [f for f in filas if "PARAGUAY" in f[3].upper()]
    with open(salida, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.writer(fh)
        w.writerow(["NALADISA_93", "DESCRIPCION_SICE", "MARGEN_INICIAL_1996", "OBSERVACION", "PAGINA_SICE"])
        w.writerows(py)
    print(len(filas), "filas de Chile en el PDF;", len(py), "para Paraguay")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
