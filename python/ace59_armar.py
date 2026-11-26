"""Arma docs/ace59: ACE 59 (MERCOSUR–Colombia, Ecuador y Venezuela), textos de la ALADI.
Se pasaron a texto el Acuerdo, sus anexos y todas las listas en las que participa Paraguay; las listas bilaterales entre
otros países quedan en el catálogo como «no transcripta».
Uso: python python/ace59_armar.py <carpeta_con_los_PDF> <carpeta_ocr>"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from armar_comun import armar  # noqa: E402

PAIS = {"AR": "Argentina", "BR": "Brasil", "PY": "Paraguay", "UY": "Uruguay", "CO": "Colombia", "EC": "Ecuador",
        "VE": "Venezuela", "Ar": "Argentina", "Br": "Brasil", "Py": "Paraguay", "Uy": "Uruguay", "Co": "Colombia",
        "Ec": "Ecuador", "Ve": "Venezuela"}
ANEXOS = {1: "Anexo I – Referido al Artículo 3 (acuerdos que se mantienen)",
          2: "Anexo II – Programa de Liberación Comercial (rectificado)",
          3: "Anexo III – Notas complementarias del Artículo 5 (gravámenes)",
          4: "Anexo IV – Régimen de Origen",
          5: "Anexo V – Régimen de Salvaguardias",
          6: "Anexo VI – Régimen transitorio de Solución de Controversias",
          7: "Anexo VII – Normas, reglamentos técnicos y evaluación de la conformidad",
          8: "Anexo VIII – Medidas sanitarias y fitosanitarias",
          9: "Anexo IX – Medidas especiales"}
ROM = {1: "i", 2: "ii", 3: "iii", 4: "iv", 5: "v", 6: "vi", 7: "vii", 8: "viii", 9: "ix"}


def identificar(b):
    if b == "ACE_059_Acuerdo_Texto":
        return "acuerdo", "Texto del Acuerdo de Complementación Económica N° 59", "Acuerdo", False
    if b == "ACE_059_ACR_001_pt":
        return "acta_rectificacion_1_pt", "Acta de Rectificación N° 1 (versión en portugués)", "Acuerdo", False
    m = re.fullmatch(r"ACE_059_00(\d)", b)
    if m:
        return f"protocolo_{m.group(1)}", f"Protocolo Adicional N° {m.group(1)}", "Protocolos adicionales", False
    m = re.fullmatch(r"ACE_059_Anexo_00(\d)(?:_Rectificado)?", b)
    if m:
        n = int(m.group(1))
        return f"anexo_{ROM[n]}", ANEXOS[n], "Anexos", False
    m = re.fullmatch(r"ACE_059_Anexo_002_Apen_001_(\w\w)", b)
    if m:
        p = PAIS[m.group(1)]
        return f"anexo_ii_ap_1_{m.group(1).lower()}", f"Anexo II, Apéndice 1: preferencias otorgadas por {p} al MERCOSUR", "Programa de Liberación", True
    m = re.fullmatch(r"ACE_059_Anexo_002_Apen_002_(\w\w)", b)
    if m:
        p = PAIS[m.group(1)]
        return f"anexo_ii_ap_2_{m.group(1).lower()}", f"Anexo II, Apéndice 2: preferencias otorgadas por {p} a Colombia, Ecuador y Venezuela", "Programa de Liberación", True
    m = re.fullmatch(r"ACE_059_Anexo_002_Apen_00([34])_0(\d\d)_(\w\w)_(\w\w)", b)
    if m:
        ap, k, a, c = m.groups()
        return (f"anexo_ii_ap_{ap}_{int(k)}", f"Anexo II, Apéndice {ap}.{int(k)}: {PAIS[a]} otorga a {PAIS[c]} (dos o más cronogramas)",
                "Programa de Liberación", True)
    m = re.fullmatch(r"ACE_059_Anexo_004_Apen_00([12])", b)
    if m:
        t = {"1": "Apéndice 1: certificado de origen", "2": "Apéndice 2: requisitos específicos de origen del sector automotor"}
        return f"anexo_iv_ap_{m.group(1)}", "Anexo IV, " + t[m.group(1)], "Anexos", False
    m = re.fullmatch(r"ACE_059_Anexo_004_Apen_003_0(\d\d)_(\w\w)_(\w\w)", b)
    if m:
        k, a, c = m.groups()
        return (f"anexo_iv_ap_3_{int(k)}", f"Anexo IV, Apéndice 3.{int(k)}: requisitos específicos de origen {PAIS[a]}–{PAIS[c]}",
                "Anexos", True)
    if b == "ACE_059_Guia_BR_Siscomex":
        return ("guia_brasil_siscomex", "Brasil (Siscomex): página del ACE 59 con Ecuador, resumen del Acuerdo y de sus protocolos "
                "(en portugués)", "Guías de otros países", False)
    return None


def main(carpeta_pdf, ocr, excluir):
    pdfs = [p.stem for p in Path(carpeta_pdf).glob("ACE_059_*.pdf")]
    sin = {b: "no transcripta: lista entre otros países (Paraguay no participa)" for b in pdfs if re.search(excluir, b)}
    armar("ace59", "ACE_059_", identificar, carpeta_pdf, ocr, sin, {"protocolo_1": "Establece el Régimen de Solución de "
          "Controversias del Acuerdo (negociaciones directas, Comisión Administradora y arbitraje)."},
          extras=["ACE_059_Guia_BR_Siscomex"])


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], Path(sys.argv[3]).read_text().strip())
