# Esquema de la capa normalizada

Archivo local: `data/interim/nacidos_vivos_2014_2024.parquet`.

## Grano

Cada fila representa una combinación de categorías publicada por DEIS, no un
nacimiento individual. `count` indica cuántos nacimientos vivos registrados
representa esa combinación. La clave de trazabilidad es `source_file` más
`source_row`.

## Campos

| Campo | Tipo | Significado |
| --- | --- | --- |
| `year` | `int16` | Año de registro del archivo DEIS |
| `source_file` | `string` | CSV original |
| `source_row` | `int32` | Línea del CSV, con encabezado en la línea 1 |
| `province_code`, `province_label` | `string` | Residencia habitual de la madre |
| `residence_scope` | `string` | Provincia argentina, otro país o sin especificar |
| `birth_type_code`, `birth_type_label` | `int8?`, `string?` | Tipo de parto; admite el único blanco de 2017 |
| `sex_code`, `sex_label` | `int8`, `string` | Sexo según la fuente; el código 3 queda no documentado |
| `mother_age_code`, `mother_age_label` | `int8`, `string` | Intervalo de edad de la madre |
| `gestation_code`, `gestation_label` | `int8`, `string` | Intervalo de gestación en semanas |
| `education_source_code`, `education_source_label` | `int8`, `string` | Educación con la categorización de cada año |
| `education_harmonized_code`, `education_harmonized_label` | `int8`, `string` | Educación reducida al esquema histórico de cuatro grupos |
| `weight_source_code`, `weight_source_label` | `int8`, `string` | Peso con la categorización de cada año |
| `weight_harmonized_code`, `weight_harmonized_label` | `int8`, `string` | Peso reducido a menos de 2.500 g, 2.500 g o más, o sin especificar |
| `count` | `int64` | Nacimientos registrados representados por la fila |
| `flag_missing_birth_type` | `bool` | Tipo de parto vacío en la fuente |
| `flag_undocumented_sex` | `bool` | Código de sexo ausente del diccionario provisto |
| `flag_implausible_gestation_weight` | `bool` | Menos de 22 semanas y 2.500 g o más |
| `quality_flags` | `string?` | Nombres de las banderas activas separados por `|` |

## Armonizaciones

Los mapeos están versionados en `data/mappings/`. La normalización valida el
texto de cada etiqueta antes de aplicar un mapeo, de modo que un cambio futuro
en la fuente provoque un error explícito.

- Educación 2014–2023 conserva sus cuatro grupos. En 2024, sin instrucción y
  primaria incompleta o completa se agrupan en “Hasta primaria completa”;
  secundaria incompleta queda separada; secundaria completa y educación
  superior se agrupan en “Secundaria completa o más”.
- Peso 2014–2023 conserva sus tres grupos. Las nueve bandas de 2024 se agregan
  por debajo o desde 2.500 gramos, manteniendo “Sin especificar”.

Los campos fuente permanecen siempre disponibles. Una armonización permite una
comparación consistente, pero no recupera el detalle que los años anteriores no
publicaron.

## Reglas de análisis

- Sumar `count`, nunca contar filas, para obtener nacimientos registrados.
- Usar códigos para agrupar y etiquetas para presentar.
- No interpretar el año como cohorte pura de ocurrencia: DEIS incluye registros
  del año de referencia y del inmediatamente anterior inscriptos en ese año.
- Respetar las reglas de exclusión y sensibilidad de `docs/data-quality.md`.
- Mantener separados conteos, tasas y conceptos de fecundidad.

El Parquet usa compresión Zstandard y metadatos de fuente, cobertura, versión
del pipeline y grano. Es regenerable y está excluido de Git.
