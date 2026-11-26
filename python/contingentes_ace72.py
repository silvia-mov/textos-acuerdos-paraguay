"""Lo que Paraguay le vendió a Colombia de cada producto con contingente en el ACE 72, por año, según los despachos de
exportación de la DNIT (régimen definitivo, SE_CUENTA = SI), separado por el acuerdo que declaró el exportador.
Uso: python3 python/contingentes_ace72.py <carpeta con DNIT_<año>_exportacion.xlsx>
Los Excel anuales están en el repositorio dnit-datos-anuales. Salida: docs/ace72/tablas/contingentes_ventas_paraguay.csv"""
import sys
from pathlib import Path

import pandas as pd
from openpyxl import load_workbook

RAIZ = Path(__file__).resolve().parent.parent
# Posiciones NCM de cada contingente del Apéndice 3.3 (los cortes finos no tienen código propio en la NCM)
GRUPOS = {
    "Carne bovina deshuesada, despojos, carne salada y tripas": ("0201.30", "0202.30", "0206.10", "0206.21", "0206.22",
                                                                  "0206.29", "0210.20", "0504.00"),
    "Leche y nata en polvo": ("0402.",),
    "Preparaciones y conservas de carne": ("1602.10", "1602.49", "1602.50", "1602.90"),
    "Leche maternizada": ("1901.10",),
}


def grupo(pos):
    return next((g for g, pref in GRUPOS.items() if str(pos).startswith(pref)), None)


def main(carpeta):
    filas = []
    for ruta in sorted(Path(carpeta).glob("DNIT_*_exportacion.xlsx")):
        anio = int(ruta.stem.split("_")[1])
        if anio < 2019:
            continue
        it = load_workbook(ruta, read_only=True)["Datos"].iter_rows(values_only=True)
        h = next(it)
        for r in it:
            r = dict(zip(h, r))
            g = grupo(r["POSICION"])
            if g and r["PAIS PROCEDENCIA/DESTINO"] == "COLOMBIA" and r["SE_CUENTA"] == "SI":
                filas.append({"AÑO": anio, "CONTINGENTE": g, "ACUERDO": r["ACUERDO"], "KG": float(r["KILO NETO"] or 0),
                              "FOB_USD": float(r["FOB DOLAR"] or 0)})
    d = pd.DataFrame(filas)
    d["COLUMNA"] = d.ACUERDO.map(lambda a: "CON_ACE72" if a == "MERCOSURCOLOMBIA" else ("SIN_ACUERDO" if a == "SIN ACUERDO" else "OTRO_O_SIN_DATO"))
    t = d.pivot_table(index=["AÑO", "CONTINGENTE"], columns="COLUMNA", values="KG", aggfunc="sum", fill_value=0) / 1000
    v = d.groupby(["AÑO", "CONTINGENTE"]).FOB_USD.sum() / 1e6
    anios = range(2019, max(int(p.stem.split("_")[1]) for p in Path(carpeta).glob("DNIT_*_exportacion.xlsx")) + 1)
    idx = pd.MultiIndex.from_product([anios, list(GRUPOS)], names=["AÑO", "CONTINGENTE"])
    t = t.reindex(idx, fill_value=0)
    for c in ("CON_ACE72", "SIN_ACUERDO", "OTRO_O_SIN_DATO"):
        if c not in t:
            t[c] = 0.0
    t = t[["CON_ACE72", "SIN_ACUERDO", "OTRO_O_SIN_DATO"]].rename(columns=lambda c: c + "_T")
    t["FOB_MILLONES_USD"] = v.reindex(idx, fill_value=0)
    t = t.round(3).reset_index()
    t.to_csv(RAIZ / "docs/ace72/tablas/contingentes_ventas_paraguay.csv", index=False, encoding="utf-8-sig")
    print(t.to_string())


if __name__ == "__main__":
    main(sys.argv[1])
