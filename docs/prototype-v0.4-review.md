# Revisión de anotaciones del prototipo v0.4

Fecha: 2026-09-25.

## Problema observado

En v0.3 la línea de nacimientos atravesaba o rozaba las anotaciones de 2019 y
2024. Aunque las cifras eran recuperables, la interferencia reducía contraste,
obligaba a releer y debilitaba la jerarquía entre dato y explicación.

## Corrección

- Las etiquetas de 2019 y 2024 se desplazaron por encima de la serie.
- La etiqueta de 2020 se ubicó debajo del punto, lejos de la trayectoria y del
  eje temporal.
- Se añadieron líderes finos y neutrales entre las tres etiquetas y sus puntos.
- La etiqueta inicial de 2014 permanece sin líder porque su asociación es
  inmediata y no existe ambigüedad.
- No se redujo tipografía ni se cubrió la línea con cajas opacas.

## Prevención automática

El constructor calcula en coordenadas de pantalla el rectángulo de cada
anotación, añade un margen de seguridad y muestrea todos los segmentos de la
serie. La generación falla si la línea invade cualquiera de esos rectángulos.
Así, una futura actualización de datos u offsets no puede reintroducir
silenciosamente el defecto.

## Verificación

- Panel temporal inspeccionado a 200 ppp y en ampliación.
- Página completa inspeccionada después de la corrección.
- Tamaño mínimo de 8 puntos preservado.
- PDF A3 exacto, con texto extraíble, fuentes incrustadas y cero imágenes raster.
- SVG, PNG, PDF y manifiesto sometidos nuevamente a controles de integridad.

La v0.4 sustituye a v0.3 como prueba de impresión vigente. Continúa marcada como
**NO PRESENTAR** hasta completar la impresión física y la prueba con lectores.
