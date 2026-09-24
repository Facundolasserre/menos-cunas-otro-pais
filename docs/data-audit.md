# Primera auditoría de datos DEIS

Fecha de verificación: 2026-09-24.

Fuente: [DEIS – Nacidos vivos](https://www.argentina.gob.ar/salud/deis/datos/nacidosvivos).

## Resultado

Los archivos 2014–2024 tienen las mismas ocho columnas y no presentan
combinaciones dimensionales duplicadas. Las categorías de jurisdicción y edad
de la madre son estables en los once años. Por lo tanto, el eje principal
año–territorio–edad puede normalizarse sin una recodificación sustantiva.

## Totales y formato

| Año | Filas agregadas | Nacimientos registrados | Formato | Blancos ponderados |
| ---: | ---: | ---: | --- | ---: |
| 2014 | 12.411 | 777.012 | coma, Windows-1252 | 0 |
| 2015 | 12.046 | 770.040 | coma, Windows-1252 | 0 |
| 2016 | 11.869 | 728.035 | coma, Windows-1252 | 0 |
| 2017 | 12.308 | 704.609 | coma, Windows-1252 | 10 |
| 2018 | 11.863 | 685.394 | coma, Windows-1252 | 0 |
| 2019 | 11.288 | 625.441 | coma, Windows-1252 | 0 |
| 2020 | 10.846 | 533.299 | punto y coma, UTF-8 con BOM | 0 |
| 2021 | 10.072 | 529.794 | punto y coma, UTF-8 con BOM | 0 |
| 2022 | 9.693 | 495.295 | punto y coma, UTF-8 con BOM | 0 |
| 2023 | 9.354 | 460.902 | punto y coma, UTF-8 con BOM | 0 |
| 2024 | 21.966 | 413.135 | punto y coma, UTF-8 con BOM | 0 |

Entre 2014 y 2024, el total publicado pasa de 777.012 a
413.135: una caída de 363.877
(46,8%).
Es un resultado de control, todavía no una explicación causal.

## Cambios de esquema que requieren tratamiento

- Los CSV de 2014–2019 usan comas y codificación Windows-1252. Los de
  2020–2024 usan punto y coma y UTF-8 con BOM. El diccionario XLSX todavía
  describe únicamente el formato antiguo con comas.
- En 2024, `IMINSTRUC` pasa de 4 a 8 categorías. Puede armonizarse hacia las
  cuatro categorías históricas, pero no debe compararse categoría por categoría
  sin esa transformación.
- En 2024, `IPESONAC` pasa de 3 a 9 categorías. Las nuevas bandas pueden
  reagruparse en menos de 2.500 g, 2.500 g o más y sin especificar.
- La mayor cantidad de filas en 2024 se debe a esas desagregaciones nuevas, no
  a una mayor cantidad de nacimientos.
- En 2024 aparece el código de sexo 3, ausente del
  diccionario provisto. Representa 6 nacimientos y se mantendrá sin etiqueta
  hasta encontrar una definición oficial.
- En 2017 existe una combinación sin código de tipo de parto, con `CUENTA=10`.
  Corresponde además a jurisdicción, sexo, edad, gestación, instrucción y peso
  sin especificar. No se imputará silenciosamente.

## Controles aprobados

- 11 años presentes, de 2014 a 2024.
- 26 códigos de residencia en cada año, incluidos otro país y no especificado.
- 9 grupos de edad de la madre, idénticos en todos los años.
- `CUENTA` contiene enteros positivos.
- Ningún duplicado en la combinación de las siete dimensiones.
- Los checksums coinciden con `data/source-catalog.csv`.

## Decisión

La próxima capa usará Parquet local con tipos y códigos separados de sus
etiquetas. Preservará todas las filas, añadirá el año como columna y producirá
controles de suma antes y después de cualquier armonización. Los agregados para
la obra se calcularán desde esa capa, no directamente desde los CSV.
