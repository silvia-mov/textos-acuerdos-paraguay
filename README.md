# Textos de los acuerdos comerciales de Paraguay

Los textos de los acuerdos comerciales de Paraguay, reunidos, sin duplicados, pasados a texto y buscables.

**Página:** https://silvia-mov.github.io/textos-acuerdos-paraguay/

## Primer acuerdo: ACE 72, MERCOSUR–Colombia

- `docs/ace72/textos/`: un archivo de texto por documento (Acuerdo, 9 anexos y sus apéndices, Acta de Rectificación,
  4 protocolos adicionales, entendimientos y contingentes). Versión elegida: la de la ALADI, depositario oficial.
- `docs/ace72/catalogo.csv` (y `.xlsx`): los 155 archivos reunidos, con su estado (texto elegido, copia de otra
  versión, referencia o aparte) y el md5 de cada uno.
- `docs/ace72/tablas/`: las listas de preferencias pasadas a tablas (CSV y Excel). La principal es
  `preferencias_paraguay_colombia.csv`: una fila por código NALADISA 96, con la categoría que da Colombia a Paraguay,
  la que da Paraguay a Colombia, el detalle de los productos con contingentes o preferencias fijas y el requisito
  específico de origen bilateral.

## Cómo se arma

```
python python/ace72_armar.py <carpeta>
```

La carpeta tiene `inventario.tsv` y `txt/<md5>.txt` con el texto de cada PDF (`pdftotext -layout`, o OCR con
`tesseract -l spa` si el PDF era una imagen). Los PDF originales no se publican aquí. El catálogo a mano de cada
archivo está en `python/ace72_catalogo_fuente.py`; la lectura de las listas, en `python/ace72_preferencias.py`.

Las tablas salen de leer los PDF con un programa: ante cualquier duda, vale el texto original.

Proyecto independiente de datos abiertos. No representa ni cuenta con el respaldo de la ALADI, del MERCOSUR ni de
ningún gobierno. Código con licencia MIT.
