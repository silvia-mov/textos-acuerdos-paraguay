"""Imagen de la tarjeta de la portada (clara y oscura): de la firma de cada acuerdo al 100% de preferencia.
Uso: python python/grafico_tarjeta.py  -> docs/img/tarjeta_light.png y tarjeta_dark.png"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# (acuerdo, firma, año en que el último cronograma llegó a 100%) — fechas de los textos de la ALADI
A = [("ACE 35 Chile", 1996.48, 2014), ("ACE 36 Bolivia", 1996.96, 2014), ("ACE 58 Perú", 2005.91, 2017),
     ("ACE 72 Colombia", 2017.55, 2018)]
for modo, bg, fg, gr, c1, c2 in (("light", "#ffffff", "#222", "#ddd", "#774D78", "#8DB2AC"),
                                 ("dark", "#17141a", "#eee", "#333", "#AF8EB1", "#5E8F88")):
    f, a = plt.subplots(figsize=(12, 5.6), dpi=100); f.patch.set_facecolor(bg); a.set_facecolor(bg)
    for i, (n, ini, fin) in enumerate(reversed(A)):
        a.barh(i, fin - ini, left=ini, height=.5, color=c2)
        a.plot(ini, i, "o", ms=13, color=c1); a.plot(fin, i, "D", ms=11, color=c1)
        a.text(ini - .4, i, n, ha="right", va="center", color=fg, fontsize=14, fontweight="bold")
    a.set_xlim(1990, 2020); a.set_ylim(-.7, len(A) - .3); a.set_yticks([])
    a.set_title("Acuerdos comerciales de Paraguay: de la firma al libre comercio", loc="left", color=fg,
                fontsize=17, fontweight="bold", pad=34)
    a.text(0, 1.03, "Círculo: firma del acuerdo. Rombo: año en que el último cronograma llegó a 100% de preferencia.",
           transform=a.transAxes, color=fg, fontsize=11)
    a.tick_params(colors=fg, labelsize=12)
    for s in a.spines.values(): s.set_visible(False)
    a.xaxis.grid(True, color=gr); a.set_axisbelow(True)
    f.tight_layout(); f.savefig(f"docs/img/tarjeta_{modo}.png", facecolor=bg)
