# Revisión de impresión del prototipo v0.3

Fecha: 2026-09-25.

## Veredicto digital

La prueba digital queda aprobada para impresión A3 al 100%. El PDF conserva una
página vectorial de 297 × 420 mm, texto seleccionable, cuatro recursos de fuente
incrustados y ninguna imagen rasterizada. Sigue marcado como **NO PRESENTAR**:
la aprobación definitiva requiere observar una copia física y realizar la prueba
con lectores descrita en `docs/reader-test-protocol.md`.

## Mejoras de legibilidad

- El piso tipográfico subió de 7,5 a 8 puntos.
- Las etiquetas provinciales usan 8,2 puntos y las anotaciones de la serie,
  8,5 puntos.
- El lienzo se genera con dimensiones métricas exactas de A3.
- Se mantienen márgenes amplios y una única familia tipográfica incrustada.
- El PDF no contiene gráficos rasterizados; líneas, marcas y texto permanecen
  nítidos al ampliar o imprimir.
- Se verificó que todos los textos indispensables puedan extraerse del PDF.

## Defecto encontrado y corregido

La primera renderización mostró que el pie metodológico, al crecer a 8 puntos,
rozaba la línea de fuentes. Se reemplazó el ajuste automático por dos líneas
explícitas, se aumentó su separación y se desplazó la línea de enlaces. Una
segunda inspección del pie y de la página completa confirmó que no quedan
solapamientos ni cortes.

## Controles superados

- PDF de una página: 297,00 × 420,00 mm.
- `MediaBox` y `CropBox` coincidentes.
- Cuatro de cuatro recursos tipográficos incrustados.
- Cero imágenes rasterizadas dentro del PDF.
- Texto principal, valores, jurisdicciones, fuente y advertencias extraíbles.
- Tamaño mínimo de texto de 8 puntos validado en SVG.
- Render de control a 200 ppp inspeccionado completo y por zonas densas.
- Generación determinista: SVG, PNG, PDF y manifiesto repiten sus checksums.

## Impresión requerida

Imprimir `output/pdf/prototype-v0.3-print-proof.pdf` en A3 vertical, color y
escala **100% / tamaño real**. No usar “ajustar”, “encoger” ni “varias páginas por
hoja”. Revisar a una distancia aproximada de 60 cm y completar la lista de
control antes de iniciar la prueba con tres lectores.
