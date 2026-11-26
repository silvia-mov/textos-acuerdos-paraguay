"""Tabla de uso del acuerdo para cada página: exportaciones de Paraguay al socio y cuánto usó una preferencia, con la
variación respecto del año anterior. Datos: utilizacion_por_socio.csv del repositorio comercio-exterior-paraguay-acuerdos
(despachos definitivos de la DNIT, FOB, 2011 en adelante; el último año es parcial)."""
from pathlib import Path

import pandas as pd

DATOS = Path(__file__).resolve().parent / "datos" / "utilizacion_por_socio.csv"
PARCIAL = 2026          # año con datos parciales (enero a septiembre)


def num(x, d=1):
    return f"{x:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def flecha(v, unidad):
    if v is None:
        return '<span class="chica">—</span>'
    if abs(v) < 0.5:
        return f'<span class="chica">= {num(abs(v), 0)} {unidad}</span>'
    s, c = ("▲", "var(--s1)") if v > 0 else ("▼", "var(--s3)")
    return f'<span style="color:{c};font-weight:700">{s}</span> {num(abs(v), 0)} {unidad}'


def serie(codigo, desde, hasta=9999):
    d = pd.read_csv(DATOS)
    s = d[d.CODIGO_PAIS == codigo].sort_values("AÑO").set_index("AÑO")
    return s, [a for a in s.index if desde <= a <= hasta]


def tabla(codigo, socio, desde, hasta=9999):
    """HTML de la tabla y un resumen (último año completo)."""
    s, anios = serie(codigo, desde, hasta)
    filas = []
    for a in anios:
        r = s.loc[a]
        exp, con = r.DNIT_EXPORTADO_USD / 1e6, r.DNIT_CON_ACUERDO_USD / 1e6
        pct = 100 * con / exp if exp else 0
        ve = vp = None
        if a - 1 in s.index and a != PARCIAL:
            p = s.loc[a - 1]
            pe = p.DNIT_EXPORTADO_USD / 1e6
            ve = 100 * (exp - pe) / pe if pe else None
            vp = pct - 100 * p.DNIT_CON_ACUERDO_USD / p.DNIT_EXPORTADO_USD if p.DNIT_EXPORTADO_USD else None
        filas.append(f"<tr><td>{a}{'*' if a == PARCIAL else ''}</td><td>{num(exp)}</td><td>{flecha(ve, '%')}</td>"
                     f"<td>{num(con)}</td><td>{num(pct, 0)} %</td><td>{flecha(vp, 'pts.')}</td></tr>")
    return (f'<div class="tw"><table class="num"><thead><tr><th>Año</th><th>Exportado a {socio}<br>(mill. USD)</th><th>Cambio</th>'
            f'<th>Con preferencia<br>(mill. USD)</th><th>% con preferencia</th><th>Cambio</th></tr></thead><tbody>'
            + "".join(filas) + "</tbody></table></div>")


def resumen(codigo, desde):
    s, anios = serie(codigo, desde)
    ult = max(a for a in anios if a != PARCIAL)
    r = s.loc[ult]
    return ult, r.DNIT_EXPORTADO_USD / 1e6, 100 * r.DNIT_CON_ACUERDO_USD / r.DNIT_EXPORTADO_USD


NOTA = ("Cambio: frente al año anterior. * Enero a septiembre: no se compara con el año anterior, que está completo. FOB, despachos definitivos de la DNIT; "
        "▲ sube, ▼ baja; el cambio del porcentaje se mide en puntos. «Con preferencia»: exportaciones que usaron algún acuerdo "
        "comercial con ese socio. Datos y método: <a href=\"https://silvia-mov.github.io/comercio-exterior-paraguay-acuerdos/\">"
        "Comercio exterior de Paraguay y acuerdos comerciales</a>. Una parte de lo que no usa el acuerdo puede no tener rebaja o no "
        "cumplir las reglas de origen.")


def seccion(codigo, socio, desde, titulo=None, hasta=9999, texto_extra=""):
    ult, exp, pct = resumen(codigo, desde) if hasta == 9999 else (None, None, None)
    t = titulo or f"Cuánto usa Paraguay el acuerdo para venderle a {socio}"
    intro = (f"<p>En {ult}, Paraguay exportó a {socio} USD {num(exp)} millones según los despachos de la DNIT, y el "
             f"<b>{num(pct, 0)} %</b> usó una preferencia.{texto_extra}</p>") if ult else f"<p>{texto_extra}</p>"
    return f"<h2>{t}</h2>\n{intro}\n{tabla(codigo, socio, desde, hasta)}"
