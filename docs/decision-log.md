# Registro de decisiones

## 2026-09-24 - Tema

Se seleccionó la transformación de los nacimientos registrados en Argentina
entre 2014 y 2024. La decisión prioriza actualidad, relevancia pública, calidad
de las fuentes, claridad narrativa, novedad respecto de ganadores anteriores y
factibilidad dentro del plazo del concurso.

## 2026-09-24 - Categoría primaria

Se prioriza Historia visual. El plazo disponible y la fuerza de una afirmación
central favorecen concentrar el esfuerzo en análisis, síntesis y terminación
gráfica antes que en infraestructura interactiva.

## 2026-09-24 - Materiales de la materia

Los PDFs originales permanecen fuera de Git por tamaño y posibles restricciones
de redistribución. Se versionan principios derivados, referencias y controles.

## 2026-09-24 - Política de datos

Los archivos crudos e intermedios no se versionan. El repositorio contendrá
scripts de descarga y transformación, metadatos y tablas derivadas pequeñas que
sean necesarias para reproducir la visualización.

## 2026-09-24 - Formatos de almacenamiento

Los CSV oficiales se conservan sin cambios en `data/raw/`. La capa normalizada
se almacena localmente en Parquet para fijar el esquema y simplificar lecturas
repetidas. Solo los agregados finales pequeños se versionan, preferentemente en
CSV por su legibilidad y facilidad de revisión en Git.

## 2026-09-24 - Revisión del material correcto de la materia

Se revisaron las versiones locales definitivas de los ocho documentos de
Visualización de la Información, con 241 páginas en total. La revisión confirmó
la guía operativa ya documentada: separar exploración y explicación, estructurar
el pipeline completo, respetar escalas de medición, privilegiar comparaciones
controladas y auditar agregaciones, fuentes, errores y explicaciones alternativas.
