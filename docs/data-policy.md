# Política de datos y seguridad del repositorio

## Decisión de formatos

Los archivos publicados por DEIS se conservan en CSV, sin modificaciones, como
fuente canónica. El proyecto usa Parquet solamente como formato local de
trabajo para unificar tipos, comprimir y acelerar lecturas repetidas.

El tamaño de los archivos de nacidos vivos no exige Parquet por rendimiento.
La ventaja principal es metodológica: un esquema explícito reduce errores al
combinar años y evita reinterpretar tipos en cada ejecución.

## Zonas de datos

| Zona | Contenido | Formato preferido | Git |
| --- | --- | --- | --- |
| `data/raw/` | Descargas oficiales inmutables | CSV/XLSX originales | No |
| `data/interim/` | Datos normalizados y unidos | Parquet | No |
| `data/processed/local/` | Tablas analíticas detalladas regenerables | Parquet/DuckDB | No |
| `data/processed/` | Agregados pequeños necesarios para la obra | CSV | Sí, tras revisión |

No se convierte el CSV original para reemplazarlo. El Parquet siempre se puede
regenerar desde las fuentes y scripts versionados.

## Qué se versiona

- Scripts de descarga, transformación, análisis y validación.
- Manifiesto de fuentes con URL, fecha de consulta, tamaño y checksum.
- Diccionario de variables y decisiones de normalización documentadas.
- Agregados pequeños, no sensibles y estrictamente necesarios para reproducir
  la visualización final.
- Exportaciones finales verificadas.

## Qué no se versiona

- CSV y XLSX originales descargados.
- Parquet, bases DuckDB y cachés de análisis.
- PDFs de la materia u otros materiales con restricciones de redistribución.
- Archivos `.env`, credenciales, tokens, claves o datos personales.
- Exploraciones descartables y exportaciones no verificadas.

## Publicación segura

Antes de cada commit se ejecuta `scripts/validation/check_repo_safety.sh`. El
control rechaza archivos prohibidos, archivos versionados mayores a 10 MiB,
credenciales con patrones conocidos y errores de whitespace en el área staged.
Además se revisan manualmente `git status` y el diff que se va a publicar.

Git no es la única barrera de seguridad. Si un secreto llegara a ser agregado,
debe revocarse aunque el commit no se haya enviado a GitHub.
