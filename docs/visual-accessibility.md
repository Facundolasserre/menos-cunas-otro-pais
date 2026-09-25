# Auditoría de accesibilidad visual

Fecha: 2026-09-25. Prototipo evaluado: v0.6.

## Resultado

La paleta supera el contraste AA de 4,5:1 para texto normal tanto en visión
estándar como en las simulaciones completas de protanopia, deuteranopia y
tritanopia. La diferencia entre acento y neutral permanece por encima de
ΔE76 = 10 en las tres simulaciones. El color no es el único canal: 2014 usa
puntos vacíos y 2024 puntos llenos, con años y valores etiquetados directamente.

| Condición | Fondo | Acento 2024 | Neutral 2014 | Acento/fondo | Neutral/fondo | ΔE76 |
| --- | --- | --- | --- | ---: | ---: | ---: |
| Visión estándar | `#F7F4EC` | `#0F6370` | `#6B665E` | 6.29:1 | 5.18:1 | 27.4 |
| Protanopia | `#F6F4EC` | `#595F71` | `#68665E` | 5.78:1 | 5.22:1 | 16.2 |
| Deuteranopia | `#F7F4EC` | `#4C5670` | `#6A675E` | 6.65:1 | 5.14:1 | 23.0 |
| Tritanopia | `#F9F3F2` | `#006867` | `#6D6464` | 6.02:1 | 5.23:1 | 30.1 |

## Escala de grises

La conversión por luminancia produce fondo `#F4F4F4`, acento
`#5A5A5A` y neutral `#676767`. Acento y neutral
quedan próximos en gris; por eso la lectura no depende de diferenciarlos por
tono. La redundancia de forma —vacío/lleno—, posición y etiqueta directa es un
requisito validado automáticamente.

## Método y alcance

Las simulaciones aplican a RGB lineal las matrices de severidad completa de
Machado, Oliveira y Fernandes (2009), vuelven a sRGB y calculan contraste WCAG
y distancia CIE76. Es una prueba técnica reproducible, no reemplaza una revisión
con personas ni la prueba impresa A3 al 100%.

Referencia: [A physiologically-based model for simulation of color vision
deficiency](https://doi.org/10.1109/TVCG.2009.113).
