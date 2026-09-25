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

## 2026-09-24 - Tratamiento de anomalías

La limpieza no elimina ni imputa observaciones silenciosamente. Se conservan y
se señalan un tipo de parto vacío en 2017, seis casos con código de sexo 3 no
documentado en 2024 y 48 nacimientos con la combinación menos de 22 semanas y
2.500 gramos o más. Cada caso se excluye únicamente del análisis que afectaría,
manteniendo intactos los totales por año, territorio y edad.

## 2026-09-24 - Formato de la obra

La entrega se desarrollará como una Historia visual estática de una página, con
varios gráficos coordinados dentro de una única composición narrativa. Se
exportará en PDF y PNG. Las anomalías que afecten cifras o interpretación serán
visibles en la obra; las restantes quedarán en la metodología ampliada.

## 2026-09-24 - Diferenciación frente a antecedentes

El informe oficial *Natalidad y educación en Argentina. Perspectivas a futuro*
ya desarrolla la relación entre natalidad, matrícula y territorio. Para evitar
una réplica, el proyecto no centrará su aporte en proyectar escuelas ni copiará
su mapa. El eje original será el desplazamiento territorial de la composición
por edad materna, actualizado con DEIS hasta 2024. La educación se mantendrá
como consecuencia contextual respaldada por una fuente externa.

## 2026-09-24 - Denominadores poblacionales

Las proyecciones vigentes basadas en Censo 2022 comienzan en 2022; las series
anteriores se basan en Censo 2010 y fueron reemplazadas. No se construirá una
tasa 2014–2024 empalmando revisiones incompatibles. Las comparaciones principales
seguirán siendo conteos registrados y composiciones dentro de edades conocidas,
con esa limitación visible.

## 2026-09-25 - Storyboard

Se compararon tres arquitecturas: un corrimiento basado en posiciones alineadas,
una matriz de 24 perfiles completos y un flujo apilado que se angosta. Se eligió
**El corrimiento** porque combina impacto inicial, comparación precisa y
evidencia visible para las 24 jurisdicciones. El gráfico principal será un
dumbbell de la proporción de nacimientos de madres de 30 años o más, no un mapa.
La elección obtuvo 96/100 en una matriz ponderada por rigor, impacto,
originalidad, síntesis, evidencia territorial y riesgo de producción.

## 2026-09-25 - Prototipo visual v0.1

Se adoptó A3 vertical como formato de prueba, con SVG vectorial maestro y PNG a
240 ppp. La paleta usa fondo cálido, tinta oscura, neutral para 2014 y azul
petróleo para 2024. El acento supera contraste AA y evita el significado de
alarma asociado al rojo evaluado inicialmente. La proyección educativa se
mantiene en tinta para distinguir su fuente externa. El prototipo fue aceptado
como línea de base, pero conserva la marca “NO PRESENTAR” hasta superar pruebas
impresas, simulaciones cromáticas, revisión del título y reemplazo del seudónimo.

## 2026-09-25 - Endurecimiento visual v0.2

Se ratificó el título **Menos cunas, otro país** con 91/100 frente a tres
alternativas. Se mantuvo la escala territorial común: aun sin CABA, las otras
23 jurisdicciones ocupan suficiente ancho útil, mientras que aislar el valor
atípico escondería un hallazgo. El piso tipográfico subió a 7,5 puntos. La
paleta superó contraste AA y separación cromática bajo simulaciones completas
de protanopia, deuteranopia y tritanopia; en gris, la lectura se preserva con
forma, posición y etiquetado directo. La v0.2 sigue siendo un prototipo hasta
completar impresión, lectura externa, seudónimo y exportación final.
