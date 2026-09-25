# Sistema visual del prototipo

## Formato

El prototipo usa una página A3 vertical de 297 × 420 mm. El SVG es la fuente
maestra por conservar texto y geometría vectorial; el PNG de 2.805 × 3.969
píxeles a 240 ppp sirve para revisión, comparación y difusión interna. Ninguno
es todavía material de presentación.

La página se organiza en cinco escenas alineadas a los mismos márgenes:
magnitud, trayectoria, composición nacional, comparación territorial y
consecuencia pública. Los separadores son reglas finas, no contenedores.

## Paleta

| Rol | Color | Uso | Contraste sobre fondo |
| --- | --- | --- | ---: |
| Fondo | `#F7F4EC` | Superficie cálida de baja fatiga | — |
| Tinta | `#1C252B` | Texto y evidencia principal | 14,16:1 |
| Acento | `#0F6370` | 2024 y transformación destacada | 6,29:1 |
| Neutral | `#6B665E` | 2014, notas y estructura secundaria | 5,18:1 |
| Grilla | `#D8D2C7` | Guías sin contenido textual | No aplica |

El azul petróleo evita presentar la caída como éxito o fracaso. El acento nunca
actúa solo: 2024 también se distingue por puntos llenos, mientras que 2014 usa
puntos vacíos. La proyección educativa queda en tinta, para no confundirla con
la serie principal DEIS.

## Tipografía

Se usa DejaVu Sans porque es libre, reproducible y está disponible junto con el
motor de gráficos. Una sola familia sostiene la jerarquía mediante tamaño y
peso. Los números permanecen alineados y ningún texto baja de 7,5 puntos en el
prototipo A3. El piso se controla sobre el SVG; la prueba impresa determinará si
debe crecer nuevamente.

## Escalas y marcas

- Serie temporal: línea y posición; el eje parte en 375 mil porque no es un
  gráfico de barras y muestra unidades y referencias explícitas.
- Edad nacional: puntos emparejados sobre una escala común de 0% a 28%.
- Jurisdicciones: dumbbells sobre una escala común de 20% a 74%, ordenados por
  el valor 2024. La escala no empieza en cero porque se comparan posiciones y
  cambios, no longitudes desde una base.
- No se usa mapa: la pregunta es cuánto cambió cada jurisdicción, y la posición
  alineada permite comparar mejor que el área geográfica.
- No se usan pictogramas, fotografías, degradados, sombras ni 3D.

## Jerarquía de lectura

1. En cinco segundos: 777.012 → 413.135 y −46,8%.
2. En treinta segundos: tendencia previa a 2020, corrimiento modal y 24 de 24.
3. En dos minutos: valores provinciales, denominadores, fuente externa y límites.

## Accesibilidad y estado

Los validadores automáticos controlan relación de aspecto, checksums, presencia
de texto vectorial, piso tipográfico y contrastes WCAG. La paleta fue simulada
con protanopia, deuteranopia y tritanopia; la escala de grises se sostiene por
la redundancia entre forma, posición y etiquetas directas. Todavía faltan la
impresión a tamaño real, una revisión de lectura por terceros y la sustitución
del seudónimo pendiente. Por eso el archivo mantiene visible la marca
“PROTOTIPO 0.2 · NO PRESENTAR”.
