"""ACE 35: tablas del Régimen de Origen vigente (Anexo 13 reemplazado por el
Protocolo 69, 2025). Apéndice 1 = requisitos específicos (todas las Partes);
Apéndice 2 = régimen diferenciado Paraguay -> Chile.
Uso: python3 ace35_tablas_pdf.py <ACE_035_069.pdf> <carpeta_salida>"""
import sys, csv, re, pdfplumber

def limpia(x):
    return re.sub(r"\s+", " ", (x or "").replace("\n", " ")).strip()

def tabla(pdf, desde, hasta, n):
    filas = []
    for p in pdf.pages[desde - 1:hasta]:
        for t in p.extract_tables():
            for f in t:
                f = [limpia(c) for c in f]
                if len(f) != n or f[0] in ("N", "NALADISA 2012") or not any(f):
                    continue
                # fila de continuación (sin número ni código): se pega a la anterior
                clave = f[0] if n == 3 else f[1]
                if not clave and filas:
                    filas[-1] = [limpia(a + " " + b) for a, b in zip(filas[-1], f)]
                else:
                    filas.append(f)
    return filas

def main(pdf_path, salida):
    with pdfplumber.open(pdf_path) as pdf:
        ap1 = tabla(pdf, 23, 82, 5)
        ap2 = tabla(pdf, 83, 92, 3)
    nums = [int(f[0]) for f in ap1 if f[0].isdigit()]
    assert nums == list(range(1, len(nums) + 1)) and len(nums) == len(ap1), "Ap. 1 con huecos"
    with open(f"{salida}/requisitos_especificos_origen.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh); w.writerow(["N", "NALADISA_2012", "DESCRIPCION", "OBSERVACIONES", "REQUISITO_ESPECIFICO"]); w.writerows(ap1)
    with open(f"{salida}/origen_diferenciado_paraguay_a_chile.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh); w.writerow(["NALADISA_2012", "DESCRIPCION", "REQUISITO_DE_ORIGEN"]); w.writerows(ap2)
    print("Ap.1:", len(ap1), "filas; Ap.2:", len(ap2), "filas,", sum(1 for f in ap2 if f[2]), "con requisito")

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
