# Validación de la capa normalizada

## Resultado

La capa Parquet conserva las 133.716 filas
agregadas y los 6.722.956 nacimientos
registrados de los once CSV originales. Las diferencias por año son cero. Los
41 controles extraídos del Anuario DEIS 2024 también tienen diferencia
cero. Una segunda lectura de los archivos crudos reproduce fila por fila todos
los códigos, etiquetas fuente, frecuencias y armonizaciones del Parquet.

No se detectaron conteos nulos o negativos, combinaciones dimensionales duplicadas,
códigos fuera de los dominios admitidos, etiquetas incompatibles con sus códigos,
caracteres de control ni indicios de texto mal decodificado. El Parquet tiene un
esquema tipado y metadatos de procedencia.

El detalle adicional de peso publicado en 2024 permitió seis controles de
plausibilidad predefinidos. Cinco no tienen casos. El restante recupera el único
registro ya señalado de menos de 22 semanas y 2.500 g o más
(1 nacimiento). Estas reglas son un tamiz conservador, no una certificación clínica
de cada registro.

## Hallazgos preservados y señalados

| Hallazgo | Año | Filas | Nacimientos | Tratamiento |
| --- | ---: | ---: | ---: | --- |
| Código de tipo de parto vacío en la fuente | 2017 | 1 | 10 | Conservar; excluir sólo del análisis por tipo de parto |
| Código de sexo 3 ausente del diccionario DEIS provisto | 2024 | 6 | 6 | Conservar separado; agrupar con no especificado sólo al conciliar el anuario 2024 |
| Gestación menor de 22 semanas con peso de 2500 g o más | 2014 | 19 | 20 | Conservar; excluir del análisis conjunto gestación-peso o mostrar sensibilidad |
| Gestación menor de 22 semanas con peso de 2500 g o más | 2017 | 15 | 19 | Conservar; excluir del análisis conjunto gestación-peso o mostrar sensibilidad |
| Gestación menor de 22 semanas con peso de 2500 g o más | 2018 | 8 | 8 | Conservar; excluir del análisis conjunto gestación-peso o mostrar sensibilidad |
| Gestación menor de 22 semanas con peso de 2500 g o más | 2024 | 1 | 1 | Conservar; excluir del análisis conjunto gestación-peso o mostrar sensibilidad |

Estas observaciones no se borraron ni se imputaron. Los 48 nacimientos con una
combinación gestación-peso físicamente muy improbable permanecen en totales por
año, territorio y edad. No deben utilizarse sin advertencia en un análisis conjunto
de gestación y peso.

El código de sexo `3` no aparece en el diccionario entregado por DEIS. En 2024,
sus 6 nacimientos más los 29 con código `9` reproducen exactamente los 35 casos
publicados como “sin especificar” en la tabla 13. Esta conciliación es evidencia
para agruparlos al reproducir esa tabla, pero **no define el significado propio del
código 3**; por eso se conserva por separado.

## Faltantes y comparabilidad

Los valores no especificados se reportan en `missingness_by_year.csv`; no se tratan
como registros inválidos. Hay saltos que pueden afectar comparaciones: el tipo de
parto no especificado llega a 18.232 casos
(2.92%) en 2019, y el sexo no especificado a
4.469 (0.63%) en 2017 y
6.242 (0.91%) en 2018.

Educación y peso cambiaron de categorización en 2024. La capa mantiene las
categorías originales y añade versiones armonizadas hacia el esquema histórico;
nunca reemplaza los códigos fuente.

## Alcance del control externo

La conciliación 2024 usa las tablas 1, 2, 3, 5, 7 y 13 del
[Anuario de Estadísticas Vitales 2024](https://www.argentina.gob.ar/sites/default/files/serie_5_nro_68_anuario_vitales_v4_revisada_ok.pdf).
El propio anuario advierte demoras o dificultades provinciales en el procesamiento
y envío de información, y un cambio de proyecciones poblacionales basado en el
Censo 2022. Esas advertencias se mantendrán al interpretar cobertura o tasas.

## Regla de uso

- `count` es una frecuencia de nacimientos registrados, no una fila individual.
- El registro sin tipo de parto se excluye sólo de análisis por tipo de parto.
- El código de sexo 3 se mantiene separado salvo conciliación explícita con la
  categoría publicada “sin especificar”.
- Las combinaciones gestación-peso señaladas se excluyen del cruce entre ambas
  variables o se incluyen únicamente con un análisis de sensibilidad.
- Ningún hallazgo autoriza por sí solo una interpretación causal.
