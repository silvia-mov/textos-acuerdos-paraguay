# ACE 58 – MERCOSUR–Perú

Textos y tablas del Acuerdo de Complementación Económica N° 58, armados con `python/ace58_armar.py` a partir de los
archivos publicados por la ALADI (los PDF no se publican aquí). Casi todo el Acuerdo está escaneado: 31 de los 37
documentos se leyeron con OCR y pueden tener errores de lectura.

- `catalogo.csv/.xlsx`: 37 documentos (Acuerdo, Acta de Rectificación, Anexos I a X con sus apéndices, Protocolos 1 a 6).
- `textos/`: texto de cada documento.
- `tablas/paraguay_a_peru` (Apéndice I-B) y `tablas/peru_a_paraguay` (Apéndice II-B): cronograma de cada ítem
  NALADISA 96. Leídas por columnas (`python/ace58_listas.py`) y completadas con el OCR de texto corrido; se descartaron
  los códigos que no existen en la NALADISA 96. Cronogramas (Anexo II-B): A = desgravación inmediata; B3 (Paraguay) y
  B4 (Perú) = cronograma general, 100 % en 2012; C3a–C3h = patrimonio histórico (AAP.R N° 20), 100 % en 2012;
  D5 y D6 = 100 % en 2017.
- `tablas/preferencias_paraguay_peru`: une las dos listas (6.522 productos) con el año en que cada lado llega al 100 %.
  Queda sin cronograma una parte (≈ 900 de Perú y ≈ 600 de Paraguay): lectura fallida o productos con dos o más
  cronogramas, que están en los Apéndices VII y VIII (en `textos/`).

Para Paraguay: el Protocolo 4 precisa que la preferencia de Perú de 95 % con cupo anual de 60.000 toneladas es para el
maíz amarillo duro; el Anexo II-B deja en suspenso el programa entre Perú y Paraguay para los textiles (capítulos 50 a 63)
que no están en el Apéndice 2 del Anexo V (requisitos específicos de origen Paraguay–Perú).
