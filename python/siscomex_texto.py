"""Texto de una página del Siscomex (Brasil) impresa a PDF: quita encabezados del navegador y menús del portal.
Uso: python python/siscomex_texto.py <pdf> <salida.txt>"""
import re
import subprocess
import sys

t = subprocess.run(["pdftotext", sys.argv[1], "-"], capture_output=True, text=True).stdout
titulo = t.splitlines()[0].strip()
lin = []
for l in t.replace("\f", "\n").splitlines():
    s = l.strip()
    if s == titulo or re.fullmatch(r"\d+ de \d+", s) or s.startswith("https://www.gov.br") \
            or re.fullmatch(r"\d\d/\d\d/\d{4}, \d{1,2}:\d\d", s) or not s.strip("    "):
        continue
    lin.append(s)
txt = "\n".join(lin)
i = txt.find("\nPublicado em")
txt = txt[txt.rfind("\n", 0, i - 1) + 1:] if i > 0 else txt
j = txt.rfind("Compartilhe:")
txt = txt[:j] if j > len(txt) // 2 else txt
txt = txt.replace("Compartilhe:\n", "")
open(sys.argv[2], "w", encoding="utf-8").write(f"{titulo}\nFuente: https://www.gov.br/siscomex (página impresa el 26/11/2026)\n\n" + txt.strip() + "\n")
