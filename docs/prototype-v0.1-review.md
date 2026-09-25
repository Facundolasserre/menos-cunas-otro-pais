# Revisión del prototipo v0.1

Fecha: 2026-09-25.

## Veredicto

El prototipo queda aprobado como línea de base visual y **no** como archivo de
presentación. La arquitectura sostiene la tesis en tres velocidades de lectura,
mantiene escalas comparables y muestra las 24 jurisdicciones sin recurrir a un
mapa. Conserva de forma visible la marca “NO PRESENTAR”.

## Decisiones aprobadas

- Página A3 vertical con SVG como fuente maestra y PNG como render de revisión.
- Fondo cálido, tinta casi negra y un único acento azul petróleo.
- 2014 se representa con puntos vacíos; 2024, con puntos llenos y acento.
- Una serie temporal, un dumbbell por edad y un dumbbell territorial ordenado.
- Etiquetas directas para evitar leyendas distantes.
- Cierre educativo separado y rotulado como proyección externa.
- Ninguna afirmación causal sobre pandemia, economía o decisiones individuales.

## Correcciones realizadas durante la inspección

1. Se reemplazó el rojo inicial por azul petróleo para evitar una lectura
   alarmista o valorativa.
2. La proyección educativa pasó a tinta negra para no confundirla con los datos
   DEIS de 2024.
3. La frase “la pandemia aceleró” se eliminó por sugerir causalidad. La versión
   vigente dice “La caída ya estaba en marcha antes de 2020”.
4. Se explicitó que la proyección equivale a 1,17 millones de estudiantes menos.
5. Se aumentó el tamaño mínimo de notas y valores provinciales a 7 puntos.
6. Se separaron por color y forma las claves 2014 y 2024.

## Controles superados

- Todas las cifras del storyboard reconcilian con los CSV procesados.
- Las 24 direcciones provinciales y las excepciones modales fueron verificadas.
- PNG de 2.805 × 3.969 píxeles con proporción A3.
- SVG sin imágenes rasterizadas incrustadas y con texto editable.
- Checksums y tamaños registrados en manifiesto.
- Contraste: tinta 14,16:1; acento 6,29:1; neutral 5,18:1 sobre el fondo.
- Inspección visual completa sin desbordes, cortes ni solapamientos.
- Archivos marcados explícitamente como prototipo.

## Riesgos que pasan a v0.2

- Comprobar el tamaño tipográfico mediante una impresión A3 al 100%.
- Simular protanopia, deuteranopia, tritanopia y escala de grises.
- Evaluar si el valor atípico de CABA comprime demasiado las otras 23 líneas. La
  escala común se mantendrá salvo que una prueba de lectura demuestre lo contrario.
- Revisar el título provisorio frente a alternativas menos metafóricas.
- Sustituir el seudónimo pendiente y cerrar la declaración de uso de IA.
- Contrastar el texto educativo una vez más contra la página exacta del informe
  antes de exportar la entrega.
