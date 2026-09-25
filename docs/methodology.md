# Metodología

Documento vivo. Registra sólo decisiones efectivamente implementadas.

## Unidades de análisis previstas

- Año de registro.
- Jurisdicción de residencia de la madre.
- Grupo de edad de la madre.
- Variables complementarias disponibles en los archivos DEIS.

## Medidas que deben mantenerse separadas

- **Nacimientos registrados:** conteo de registros en el universo publicado.
- **Tasa bruta de natalidad:** nacimientos por población total.
- **Tasa específica por edad:** nacimientos por población femenina del grupo de
  edad correspondiente, si los denominadores compatibles están disponibles.
- **Fecundidad:** concepto que no se inferirá automáticamente a partir de conteos.

## Pipeline implementado

1. Descargar archivos oficiales y registrar URL, fecha, tamaño y checksum.
2. Leer el diccionario antes de concatenar años.
3. Verificar nombres, códigos, categorías y cambios de esquema.
4. Conservar una copia cruda inmutable fuera de Git.
5. Generar una tabla Parquet tipada mediante un script reproducible, conservando
   una referencia a cada fila fuente.
6. Validar independientemente filas y sumas contra los CSV, y 41 controles
   contra las tablas 1, 2, 3, 5, 7 y 13 del Anuario DEIS 2024.
7. Auditar faltantes, categorías sin especificar, dominios, duplicados,
   codificación y combinaciones gestación-peso físicamente improbables.
8. Calcular indicadores y análisis de sensibilidad.
9. Exportar únicamente tablas derivadas necesarias para la obra.

Los pasos 1–7 están implementados. El detalle del esquema está en
`docs/normalized-schema.md` y los resultados en `docs/data-quality.md`.

## Decisiones de limpieza

- No se eliminan filas ni se imputan categorías en la normalización.
- Los cambios de educación y peso en 2024 se resuelven añadiendo campos
  armonizados, sin reemplazar los campos fuente.
- Un tipo de parto vacío, un código de sexo no documentado y las combinaciones
  gestación-peso improbables se conservan con banderas explícitas.
- Las exclusiones se aplican sólo en el análisis afectado, no en los totales
  nacionales, territoriales o por edad.

## Riesgos conocidos

- Diferencia entre año de registro y año de ocurrencia.
- Inscripciones tardías.
- Retrasos o problemas de cobertura jurisdiccional.
- Cambios en proyecciones de población utilizadas como denominadores.
- Comparaciones territoriales afectadas por distinto tamaño poblacional.
- Inferencias causales no identificadas por los datos observacionales.
