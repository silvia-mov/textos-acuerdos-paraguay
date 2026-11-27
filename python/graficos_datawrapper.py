"""Dos gráficos de Datawrapper para la portada de los textos de los acuerdos:

1. Ventaja real: en cuántos productos el acuerdo no le da ninguna ventaja a Paraguay porque el socio ya cobra 0% a todos
   (arancel NMF aplicado 2026, OMC), contando el arancel completo y contando solo lo que Paraguay le vende (2023–2025).
2. Reloj de la desgravación con Perú (ACE 58): qué parte de los productos tenía 100% de preferencia cada año.

Uso: python python/graficos_datawrapper.py <carpeta con DNIT_<año>_exportacion.xlsx>
Escribe docs/tablas/ventaja_real_por_socio.csv/.xlsx y docs/tablas/desgravacion_peru.csv/.xlsx, y crea o actualiza los
gráficos (números en docs/datawrapper_ids.json). Necesita acceso a api.datawrapper.de con la clave configurada.
"""
import json
import os
import sys
from pathlib import Path

import pandas as pd
import requests

RAIZ = Path(__file__).resolve().parent.parent
TABLAS = RAIZ / "docs" / "tablas"
IDS = RAIZ / "docs" / "datawrapper_ids.json"
API = "https://api.datawrapper.de/v3"
H = {"Authorization": "Bearer " + os.environ.get("DATAWRAPPER_TOKEN", "proxy-injected")}
PUBLICAR = {"blocks": {"logo": {"enabled": False}, "embed": False, "download-pdf": False, "download-svg": False,
                       "get-the-data": True, "download-image": True}, "autoDarkMode": True}
SOCIOS = [("CHILE", "Chile", "chile", "ace35"), ("BOLIVIA", "Bolivia", "bolivia", "ace36"), ("PERU", "Perú", "peru", "ace58"),
          ("ECUADOR", "Ecuador", "ecuador", "ace59"), ("COLOMBIA", "Colombia", "colombia", "ace72")]


def guardar(df, nombre):
    df.to_csv(TABLAS / f"{nombre}.csv", index=False, encoding="utf-8-sig")
    df.to_excel(TABLAS / f"{nombre}.xlsx", index=False)


def grafico(clave, tipo, titulo, df, describe, visualize, notas="", datos=None):
    ids = json.loads(IDS.read_text()) if IDS.exists() else {}
    if clave not in ids:
        r = requests.post(f"{API}/charts", headers=H, json={"title": titulo, "type": tipo}, timeout=60)
        r.raise_for_status()
        ids[clave] = r.json()["id"]
        IDS.write_text(json.dumps(ids, indent=1, ensure_ascii=False))
    cid = ids[clave]
    requests.put(f"{API}/charts/{cid}/data", headers={**H, "Content-Type": "text/csv"},
                 data=df.to_csv(index=False).encode("utf-8"), timeout=60).raise_for_status()
    meta = {"describe": {"byline": "", **describe}, "annotate": {"notes": notas},
            "visualize": {"dark-mode-invert": True, "show-tooltips": True, **visualize}, "publish": PUBLICAR}
    if datos:
        meta["data"] = datos
    requests.patch(f"{API}/charts/{cid}", headers=H, timeout=60,
                   json={"title": titulo, "type": tipo, "language": "es-AR", "metadata": meta}).raise_for_status()
    requests.post(f"{API}/charts/{cid}/publish", headers=H, timeout=120).raise_for_status()
    print(clave, f"https://datawrapper.dwcdn.net/{cid}/")


def ventaja_real(carpeta_dnit):
    x = pd.concat([pd.read_excel(Path(carpeta_dnit) / f"DNIT_{a}_exportacion.xlsx",
                                 usecols=["SE_CUENTA", "PAIS ORIGEN", "PAIS PROCEDENCIA/DESTINO", "POSICION", "FOB DOLAR"])
                   for a in (2023, 2024, 2025)])
    x = x[(x["SE_CUENTA"] == "SI") & x["PAIS ORIGEN"].isin(["PARAGUAY", "PY - PARAGUAY"])]   # solo mercadería paraguaya
    x["SA6"] = x["POSICION"].str.replace(".", "", regex=False).str[:6]
    filas = []
    for clave, nombre, archivo, carpeta in SOCIOS:
        t = pd.read_csv(RAIZ / "docs" / carpeta / "tablas" / f"aranceles_{archivo}_omc.csv", encoding="utf-8-sig",
                        dtype={"SA_6_DIGITOS": str})
        col = [c for c in t.columns if c.startswith("NMF")][0]
        nmf = pd.to_numeric(t.set_index("SA_6_DIGITOS")[col], errors="coerce")
        e = x[x["PAIS PROCEDENCIA/DESTINO"] == clave].groupby("SA6")["FOB DOLAR"].sum()
        m = pd.DataFrame({"FOB": e}).join(nmf.rename("NMF")).dropna()
        filas.append({"SOCIO": nombre,
                      "PCT_ARANCEL_SIN_VENTAJA": round(100 * (nmf.dropna() == 0).mean(), 1),
                      "PCT_EXPORTADO_SIN_VENTAJA": round(100 * m.loc[m["NMF"] == 0, "FOB"].sum() / m["FOB"].sum(), 1),
                      "EXPORTADO_2023_2025_MILL_USD": round(m["FOB"].sum() / 1e6, 1),
                      "ARANCEL_PROMEDIO_PONDERADO_EXPORTADO": round((m["NMF"] * m["FOB"]).sum() / m["FOB"].sum(), 1)})
    d = pd.DataFrame(filas).sort_values("PCT_EXPORTADO_SIN_VENTAJA", ascending=False)
    guardar(d, "ventaja_real_por_socio")
    w = d.rename(columns={"SOCIO": "Socio", "PCT_ARANCEL_SIN_VENTAJA": "En todo su arancel",
                          "PCT_EXPORTADO_SIN_VENTAJA": "En lo que le vende Paraguay"})[["Socio", "En todo su arancel", "En lo que le vende Paraguay"]]
    col = d.set_index("SOCIO")
    grafico("ventaja_real", "d3-arrow-plot",
            f"Paraguay le vende a sus socios justo lo que ellos protegen: en Colombia, solo el "
            f"{col.loc['Colombia', 'PCT_EXPORTADO_SIN_VENTAJA']:.0f}% ya entraba libre sin el acuerdo", w,
            {"intro": "% de productos que el socio ya deja entrar con 0% a todos los países, así que el acuerdo no le da a Paraguay "
                      "ninguna ventaja. La flecha va de <b>todo el arancel del socio</b> a <b>lo que Paraguay le vende de verdad</b>. "
                      "Cuanto más a la izquierda termina, más vale el acuerdo.",
             "source-name": "OMC (arancel NMF aplicado 2026) y DNIT (exportaciones 2023–2025), cálculo propio",
             "source-url": "https://silvia-mov.github.io/textos-acuerdos-paraguay/", "number-format": "0.[0]", "number-append": "%"},
            {"range-extent": "custom", "custom-range": ["0", "100"], "x-grid-format": "0%", "show-color-key": True,
             "range-value-labels": "both", "label-first-range": True, "base-color": "#774d78", "thick": True},
            "Productos a 6 dígitos del Sistema Armonizado. Lo que vende Paraguay: exportaciones de origen paraguayo, ponderadas por "
            "su valor FOB. Con Chile casi todo paga 6%, así que el acuerdo vale en todo. Con Perú, más de la mitad de lo que vende "
            "Paraguay entraría libre igual.")
    return d


def desgravacion_peru():
    d = pd.read_csv(RAIZ / "docs" / "ace58" / "tablas" / "preferencias_paraguay_peru.csv", encoding="utf-8-sig", dtype=str)
    n = len(d)
    filas = []
    for a in range(2005, 2027):
        filas.append({"AÑO": a,
                      "PERU_A_PARAGUAY_PCT_100": round(100 * (pd.to_numeric(d["PERU_100_DESDE"], errors="coerce") <= a).sum() / n, 1),
                      "PARAGUAY_A_PERU_PCT_100": round(100 * (pd.to_numeric(d["PARAGUAY_100_DESDE"], errors="coerce") <= a).sum() / n, 1)})
    t = pd.DataFrame(filas)
    guardar(t, "desgravacion_peru")
    textil = d["NOTA"].fillna("").str.startswith("Textil").sum()
    w = t.rename(columns={"AÑO": "Año", "PERU_A_PARAGUAY_PCT_100": "Lo que Perú le abrió a Paraguay",
                          "PARAGUAY_A_PERU_PCT_100": "Lo que Paraguay le abrió a Perú"})
    w["Año"] = w["Año"].astype(str)
    fin = t.iloc[-1]
    grafico("desgravacion_peru", "d3-lines",
            f"Con Perú, el libre comercio tardó once años y todavía no llegó: el {100 - fin['PERU_A_PARAGUAY_PCT_100']:.0f}% "
            "de los productos sigue sin preferencia completa", w,
            {"intro": f"% de los {n:,} productos del ACE 58 (NALADISA 1996) con 100% de preferencia cada año. ".replace(",", ".")
                      + "La línea sube de golpe en 2006, 2012 y 2017, cuando vencían los cronogramas.",
             "source-name": "ACE 58, Anexo II-B (ALADI), leído con OCR; cálculo propio",
             "source-url": "https://silvia-mov.github.io/textos-acuerdos-paraguay/ace58/", "number-format": "0.[0]"},
            {"custom-colors": {"Lo que Perú le abrió a Paraguay": "#774d78", "Lo que Paraguay le abrió a Perú": "#5e8f88"},
             "lines": {k: {"width": "style2"} for k in ("Lo que Perú le abrió a Paraguay", "Lo que Paraguay le abrió a Perú")},
             "interpolation": "step-after", "labeling": "right", "label-colors": True, "label-margin": 170,
             "custom-range-y": ["0", "100"], "y-grid-format": "0%", "tooltip-number-format": "0.[0]%",
             "x-tick-format": "YYYY", "tooltip-x-format": "YYYY"},
            f"Lo que falta es sobre todo textil: {textil} productos con el programa en suspenso entre Perú y Paraguay "
            "(salvo el Apéndice 2 del Anexo V). Categorías: A inmediata (2006); B3 y B4 (2012); D5 y D6 (2017).")
    return t


if __name__ == "__main__":
    print(ventaja_real(sys.argv[1]).to_string())
    print(desgravacion_peru().tail(3).to_string())
