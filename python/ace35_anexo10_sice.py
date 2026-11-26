"""ACE 35, Anexo 10, «Preferencias otorgadas por Chile», desde la copia en texto del SICE (OEA): las filas que Chile
otorga a Paraguay con su margen de preferencia inicial (1996). Reemplaza la lectura por OCR del PDF de la ALADI.
Uso: python3 ace35_anexo10_sice.py <salida.csv> <PDF a_10ch_1> <PDF a_10ch_2> …"""
import csv
import re
import sys

import pdfplumber

MOJIBAKE = {"ï¿½": "�"}


def main(rutas, salida):
    filas = []
    for ruta in rutas:
      hdr0 = {}
      with pdfplumber.open(ruta) as pdf:
        for pn, p in enumerate(pdf.pages, 1):
            W = p.extract_words()
            hdr = {w["text"]: w["x0"] for w in W if w["text"] in ("GLOSA", "OBSERV", "TIPOOBS", "PORCAD")} or hdr0
            hdr0 = hdr                                   # las páginas siguientes no repiten el encabezado
            x_glosa, x_obs, x_tipo = hdr.get("GLOSA", 265) - 40, hdr.get("OBSERV", 358) - 25, hdr.get("TIPOOBS", 419) - 5
            anc = sorted((w for w in W if w["text"] == "AAP.CE35"), key=lambda w: w["top"])
            # observaciones: cada una empieza con «Preferencia» (salvo «PREVALECE PREFERENCIA…», que sigue a la anterior);
            # se asignan a la fila cuyo renglón está más cerca del centro del bloque
            ow = sorted((w for w in W if x_obs <= w["x0"] < x_tipo and w["top"] > (anc[0]["top"] - 40 if anc else 0)),
                        key=lambda w: (round(w["top"]), w["x0"]))
            bloques = []
            for k, w in enumerate(ow):
                nuevo = w["text"].upper() == "PREFERENCIA" and not (k and ow[k - 1]["text"].upper() == "PREVALECE")
                if nuevo or not bloques:
                    bloques.append([])
                bloques[-1].append(w)
            obs_de = {i: [] for i in range(len(anc))}
            for bl in bloques:
                if not anc:
                    break
                yc = (bl[0]["top"] + bl[-1]["top"]) / 2
                i = min(range(len(anc)), key=lambda i: abs(anc[i]["top"] - yc))
                obs_de[i] += [w["text"] for w in bl if not re.fullmatch(r"0[79]0", w["text"])]
            for i, a in enumerate(anc):
                y = a["top"]
                lo = (anc[i - 1]["top"] + y) / 2 if i else y - 28
                hi = (y + anc[i + 1]["top"]) / 2 if i + 1 < len(anc) else y + 28
                linea = [w for w in W if abs(w["top"] - y) < 4]
                cod = next((w["text"] for w in linea if re.fullmatch(r"\d{4}\.\d{2}\.\d{2}", w["text"])), "")
                pct = next((w["text"] for w in linea if re.fullmatch(r"\d+\.\d\d", w["text"]) and w["x0"] > x_tipo + 20), "")
                banda = sorted((w for w in W if lo <= w["top"] < hi), key=lambda w: (round(w["top"]), w["x0"]))
                obs = " ".join(obs_de[i])
                glosa = " ".join(w["text"] for w in banda if x_glosa <= w["x0"] < x_obs and abs(w["top"] - y) < 14)
                ot = next((w["text"] for w in linea if w["text"] in ("CH", "PA")), "")
                filas.append([cod, glosa.replace("ï¿½", "?"), pct, obs, pn, ot])
    # OT = CH: Chile otorga (a_10ch); OT = PA: los países del MERCOSUR otorgan a Chile (a_10ms)
    for ot, nombre in (("CH", salida), ("PA", salida.replace("chile_a_paraguay", "paraguay_a_chile"))):
        py = [f[:5] for f in filas if f[5] == ot and "PARAGUAY" in f[3].upper()]
        with open(nombre, "w", newline="", encoding="utf-8-sig") as fh:
            w = csv.writer(fh)
            w.writerow(["NALADISA_93", "DESCRIPCION_SICE", "MARGEN_INICIAL_1996", "OBSERVACION", "PAGINA_SICE"])
            w.writerows(py)
        print(ot, sum(f[5] == ot for f in filas), "filas;", len(py), "con Paraguay ->", nombre)


if __name__ == "__main__":
    main(sys.argv[2:], sys.argv[1])
