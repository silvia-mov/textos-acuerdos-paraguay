"""Arma docs/ace36: ACE 36 (MERCOSUR–Bolivia), textos de la ALADI.
Uso: python python/ace36_armar.py <carpeta_con_los_PDF> <carpeta_ocr>"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from armar_comun import armar  # noqa: E402

ANEXOS = {
    "1": "Anexo 1 – Productos con desgravación desde 50 % (100 % en 2006)",
    "2_BO": "Anexo 2 – Patrimonio histórico (ACE 34): preferencias otorgadas por Bolivia",
    "2_MCS": "Anexo 2 – Patrimonio histórico (ACE 34): preferencias otorgadas por el MERCOSUR",
    "3": "Anexo 3 – Desgravación especial desde 15 % (100 % en 2006)",
    "4": "Anexo 4 – Desgravación especial desde 10 % (100 % en 2006)",
    "5": "Anexo 5 – Productos sensibles: desgravación desde 2005 (100 % en 2011)",
    "6": "Anexo 6 – Productos sensibles: desgravación desde 2005 (100 % en 2014)",
    "7": "Anexo 7 – Productos con 100 % de preferencia desde el inicio (1997)",
    "8_AR": "Anexo 8 – Régimen de Adecuación (aranceles residuales para Bolivia): Argentina",
    "8_BR": "Anexo 8 – Régimen de Adecuación (aranceles residuales para Bolivia): Brasil",
    "8_PY": "Anexo 8 – Régimen de Adecuación (aranceles residuales para Bolivia): Paraguay",
    "8_UY": "Anexo 8 – Régimen de Adecuación (aranceles residuales para Bolivia): Uruguay",
    "9": "Anexo 9 – Régimen de Origen",
    "9_Apendice_01": "Anexo 9, Apéndice 1 – Requisitos específicos de origen",
    "10": "Anexo 10 – Régimen de Salvaguardias",
    "11": "Anexo 11 – Régimen de Solución de Controversias",
    "PIF": "Protocolo de Integración Física",
}
LISTAS = {"1", "2_BO", "2_MCS", "3", "4", "5", "6", "7", "8_AR", "8_BR", "8_PY", "8_UY"}


def identificar(b):
    if b == "ACE_036_Acuerdo":
        return "acuerdo", "Texto del Acuerdo de Complementación Económica N° 36", "Acuerdo", False
    if b == "ACE_036_ACR_001":
        return "acta_rectificacion_1", "Acta de Rectificación N° 1 del Acuerdo", "Acuerdo", False
    m = re.fullmatch(r"ACE_036_Notas_Art(\d)", b)
    if m:
        return f"notas_art_{m.group(1)}", f"Notas complementarias al Artículo {m.group(1)}", "Acuerdo", False
    m = re.fullmatch(r"ACE_036_Anexo_(\w+)", b)
    if m:
        k = m.group(1)
        grupo = "Anexos del Programa de Liberación" if k in LISTAS else "Otros anexos"
        return f"anexo_{k.lower()}", ANEXOS[k], grupo, k in LISTAS
    m = re.fullmatch(r"ACE_036_0(\d\d)(?:_(Rectificado|ACR_00\d|Anexo_0\d))?", b)
    if m:
        n, resto = int(m.group(1)), m.group(2) or ""
        base, tit = f"protocolo_{n:02d}", f"Protocolo Adicional N° {n}"
        if not resto or resto == "Rectificado":
            return base, tit + (" (rectificado)" if resto else ""), "Protocolos adicionales", False
        k = resto[-1]
        if resto.startswith("ACR"):
            return f"{base}_acta_rectificacion_{k}", f"{tit}: Acta de Rectificación N° {k}", "Protocolos adicionales", False
        return f"{base}_anexo_{k}", f"{tit}: Anexo {k}", "Protocolos adicionales", False
    return None   # ficha de la ALADI y otros


if __name__ == "__main__":
    armar("ace36", "ACE_036_", identificar, sys.argv[1], sys.argv[2])
