# Revisión del prototipo v0.2

Fecha: 2026-09-25.

## Veredicto

La v0.2 queda aprobada como prototipo visual endurecido. Conserva la arquitectura
de v0.1 y resuelve los riesgos digitales de accesibilidad, escala territorial,
título y piso tipográfico. Sigue marcada como **NO PRESENTAR** porque faltan la
prueba impresa A3, una lectura por terceros, el seudónimo y el cierre formal de
la declaración de IA.

## Decisiones cerradas

- Se mantiene **Menos cunas, otro país**, ganador de la evaluación de cuatro
  alternativas con 91/100. El subtítulo aporta la precisión literal.
- Se conserva una única escala territorial de 20% a 74%, sin corte ni recuadro.
  Entre las 23 jurisdicciones distintas de CABA, los valores 2014–2024 ocupan
  44% del ancho útil de la escala; hay espacio suficiente para leerlos.
- CABA no se trata como un defecto gráfico: su 69,2% en 2024 está 19,2 puntos
  por encima de Tierra del Fuego, la siguiente jurisdicción. Separarla ocultaría
  un resultado sustantivo y debilitaría la comparación común.
- El tamaño tipográfico mínimo sube de 7 a 7,5 puntos en SVG. El validador falla
  si cualquier texto de v0.2 queda por debajo de ese piso.
- Se mantiene la paleta. Supera AA bajo simulaciones completas de protanopia,
  deuteranopia y tritanopia; además, año, forma y posición redundan el color.

## Controles superados

- Cifras y afirmaciones reconstruidas desde los datos procesados.
- SVG vectorial sin imágenes incrustadas; PNG de 2.805 × 3.969 píxeles.
- Checksums y tamaños fijados en manifiesto.
- Contraste AA en visión estándar y tres simulaciones de deficiencia cromática.
- Diferencia de color ΔE76 mayor a 10 entre 2014 y 2024 en esas simulaciones.
- Lectura en escala de grises respaldada por puntos vacíos/llenos y etiquetas.
- Piso tipográfico automático de 7,5 puntos.
- Inspección visual en pantalla sin recortes, colisiones ni desbordes.

## Pendientes antes de una pieza candidata

1. Imprimir la página A3 al 100% y completar la lista de control física.
2. Realizar una prueba breve con al menos tres lectores ajenos al proyecto.
3. Incorporar ajustes surgidos de esas lecturas y congelar el texto final.
4. Elegir el seudónimo y sustituir todas las marcas de prototipo.
5. Exportar PDF/PNG de entrega y repetir controles sobre los archivos finales.
