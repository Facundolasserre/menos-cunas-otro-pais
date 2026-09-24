# Metodología

Documento vivo. Se completará con las decisiones efectivamente implementadas.

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

## Pipeline previsto

1. Descargar archivos oficiales y registrar URL, fecha, tamaño y checksum.
2. Leer el diccionario antes de concatenar años.
3. Verificar nombres, códigos, categorías y cambios de esquema.
4. Conservar una copia cruda inmutable fuera de Git.
5. Generar una tabla normalizada mediante scripts reproducibles.
6. Validar totales contra anuarios oficiales.
7. Auditar faltantes y categorías sin especificar.
8. Calcular indicadores y análisis de sensibilidad.
9. Exportar únicamente tablas derivadas necesarias para la obra.

## Riesgos conocidos

- Diferencia entre año de registro y año de ocurrencia.
- Inscripciones tardías.
- Retrasos o problemas de cobertura jurisdiccional.
- Cambios en proyecciones de población utilizadas como denominadores.
- Comparaciones territoriales afectadas por distinto tamaño poblacional.
- Inferencias causales no identificadas por los datos observacionales.

