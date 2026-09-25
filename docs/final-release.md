# Candidato final de inscripción

Fecha: 2026-09-25.

## Archivo para cargar

`output/pdf/menos-cunas-otro-pais-umbral-sur.pdf`

No cargar ningún otro archivo visual. En particular, no cargar prototipos, PNG,
SVG, manifiestos, código ni el kit de lectura.

## Estado técnico

- Categoría: Historia visual.
- Título: Menos cunas, otro país.
- Seudónimo visible y en metadatos: UMBRAL SUR.
- Formato: PDF 1.4, una página A3 vertical.
- Dimensiones: 297,00 × 420,00 mm.
- Peso: menos de 10 MB.
- Tipografía mínima: 8 puntos.
- Fuentes: 4 de 4 incrustadas.
- Contenido: vectorial, sin imágenes rasterizadas.
- Texto: extraíble.
- Seguridad: sin cifrado, JavaScript ni formularios.
- Anonimato: sin nombre real en texto o metadatos.
- Marcas de prototipo: ausentes.

La comparación píxel a píxel con v0.6 localizó todas las diferencias en una
franja superior de sólo 0,655% de la altura: corresponde exclusivamente a la
eliminación de la advertencia de prototipo. La composición de datos no cambió.

## Sustitución de la prueba física

No se realizó impresión A3. El participante confirmó la legibilidad y autorizó
continuar. Como sustitución se inspeccionó el render completo a 200 dpi y los
sectores de mayor densidad a 300 dpi, además de los controles geométricos,
tipográficos y de página. Esta limitación queda registrada y no se presenta como
una prueba física superada.

## Integridad

SHA-256 del PDF:

`8e61e6cfab1e207da001c00b6d380507bb0f5afb84eddd3a4fa55e76e143df73`

El hash también se conserva en
`design/exports/menos-cunas-otro-pais-umbral-sur-manifest.json`.

## Regla previa a la carga

Ejecutar:

```bash
.venv/bin/python scripts/validation/validate_submission_artifact.py
.venv/bin/python scripts/validation/validate_submission_package.py
bash scripts/validation/check_repo_safety.sh
```

La carga sólo continúa si los tres controles terminan correctamente y el PDF
mantiene el hash registrado.
