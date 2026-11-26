# ACE 35 – MERCOSUR–Chile

Textos y tablas del Acuerdo de Complementación Económica N° 35, armados con `python/ace35_armar.py` a partir de los
archivos publicados por la ALADI (los PDF no se publican aquí).

- `catalogo.csv/.xlsx`: 133 documentos (Acuerdo, notas, 4 actas de rectificación, Anexos 1–14, Protocolo sobre Integración Física, Protocolos
  Adicionales 1 a 69 y 64.1, con sus anexos y apéndices). Cada protocolo tiene fecha y síntesis (su primer artículo).
- `textos/`: texto de cada documento. 43 se leyeron con OCR (eran imágenes escaneadas): pueden tener errores de lectura.
- `estructura.json`: los 26 títulos del Acuerdo (57 artículos).
- `tablas/requisitos_especificos_origen`: Apéndice 1 del Régimen de Origen vigente (Protocolo 69, 2025): 805 requisitos.
- `tablas/origen_diferenciado_paraguay_a_chile`: Apéndice 2 del mismo régimen: requisitos especiales para las
  exportaciones de Paraguay a Chile (194 productos), vigentes hasta el 31/12/2038 y prorrogables de a 5 años.
- `tablas/chile_a_paraguay_margenes_iniciales_1996`: Anexo 10, márgenes de preferencia **iniciales** (1996) que Chile
  otorgó a Paraguay (160 productos). Leída con OCR: verificar códigos y descripciones contra el PDF. Hoy esos productos
  tienen 100 % de preferencia, como todo el universo del Programa de Liberación (el último cronograma terminó en 2014).

El Anexo 9 y el Protocolo sobre Integración Física se sumaron del release `chile` (26/11/2026). Falta el Anexo 15 (acuerdos del Cono Sur), que la ALADI no publica.
El Protocolo 66 (15/02/2022) incorpora el Acuerdo Comercial Chile–Paraguay (19 capítulos, firmado el 1/12/2021).
Los textos base de los Protocolos 21, 31, 39, 52 y 53 no están, pero sí sus versiones rectificadas, que son las vigentes.
