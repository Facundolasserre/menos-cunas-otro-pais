# Datos

## Política

`raw/` contiene descargas originales e inmutables y está ignorado por Git.
`interim/` contiene resultados temporales regenerables y está ignorado por Git.
`processed/` contendrá únicamente tablas derivadas pequeñas, documentadas y
necesarias para reproducir la obra.

Los CSV oficiales se preservan como fuente. La capa normalizada de trabajo se
guarda localmente en Parquet y no se versiona. Los agregados finales que sí se
publiquen usan CSV para facilitar la inspección y revisión de cambios.

Cada script de descarga deberá registrar origen, fecha, tamaño y checksum. Cada
tabla procesada deberá poder regenerarse desde las fuentes crudas.

La política completa está en `docs/data-policy.md`.

`source-catalog.csv` contiene las URL oficiales necesarias para reproducir la
descarga. `scripts/download/download_deis_nacidos_vivos.py` guarda los archivos
en `raw/` y genera allí un manifiesto local con tamaño y SHA-256.

## Capa normalizada

`scripts/cleaning/normalize_deis_nacidos_vivos.py` crea localmente
`interim/nacidos_vivos_2014_2024.parquet`. Se eligió Parquet porque mantiene
tipos, metadatos y compresión, y evita releer once CSV con dos formatos distintos.
El archivo es regenerable, pesa aproximadamente 1 MB y permanece ignorado por
Git.

`mappings/` contiene reglas pequeñas y auditables para armonizar educación y
peso, además de los controles transcritos del anuario 2024. `processed/`
contiene únicamente reportes de validación pequeños, aptos para revisión en Git.

Las tablas `national_trend.csv`, `age_trend.csv`,
`age_change_2014_2024.csv`, `residence_trend.csv` y
`province_change_2014_2024.csv` son la primera capa analítica de la historia.
Separan conteos, participaciones, cambios y contribuciones para evitar que una
misma medida cumpla funciones incompatibles.

Las tablas `province_age_composition_trend.csv`,
`province_age_distribution_2014_2024.csv` y
`province_age_shift_2014_2024.csv` forman la segunda capa. Completan
explícitamente con cero las combinaciones provincia–edad sin casos, separan edad
desconocida de los denominadores y permiten auditar el desplazamiento etario en
cada jurisdicción.

Ningún archivo de `raw/`, `interim/` ni `processed/local/` debe versionarse.
