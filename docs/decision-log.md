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

## 2026-09-25 - Prueba de impresión v0.3

Se elevó el piso tipográfico a 8 puntos, con 8,2 para jurisdicciones y 8,5 para
anotaciones de la serie. Se incorporó un PDF vectorial A3 exacto, con fuentes
incrustadas y texto extraíble. La inspección del primer render detectó un roce en
el pie metodológico; se corrigió con saltos controlados y mayor separación. La
pieza sólo avanzará después de imprimir al 100% y superar una prueba estructurada
con tres lectores externos.

## 2026-09-25 - Separación entre anotaciones y serie v0.4

Se aceptó la observación de que la línea temporal interfería con etiquetas de
2019 y 2024. Se descartó resolverlo con texto más pequeño o cajas que ocultaran
la serie. Las etiquetas se desplazaron a zonas libres y se conectaron mediante
líderes finos y neutrales; 2020 quedó debajo de su punto. El constructor ahora
falla automáticamente si la serie entra en el rectángulo ampliado de cualquier
anotación. La v0.4 reemplaza a v0.3 como prueba de impresión.

## 2026-09-25 - Seudónimo y paquete de inscripción v0.5

Se seleccionó **Umbral Sur** con 98/100 frente a tres alternativas, priorizando
anonimato, distinción, afinidad temática y tono profesional. No revela identidad,
ciudad, institución ni profesión. La metodología para el formulario quedó en
178 palabras e incluye procedencia, tratamiento, decisiones visuales y la
declaración obligatoria de OpenAI Codex. Un control automático verifica el
límite, las fuentes abiertas, el seudónimo y la ausencia del nombre real. La
v0.5 incorpora el seudónimo, pero mantiene “NO PRESENTAR” hasta la prueba física.

## 2026-09-25 - Separación de la flecha principal v0.6

La revisión en pantalla detectó que los extremos de la flecha principal quedaban
demasiado próximos a 777.012 y 413.135. Se descartó una corrección basada en
coordenadas fijas: el constructor ahora mide el ancho renderizado de ambos
números, reserva 12 puntos ópticos por lado y falla si la separación efectiva
baja de ocho puntos. La v0.6 reemplaza a v0.5 como prueba de impresión.

## 2026-09-25 - Kit de validación externa

Se convirtió el protocolo de lectura en un PDF A4 de cuatro páginas: guía del
facilitador y tres fichas anónimas. El guion separa exposiciones de 5 segundos,
30 segundos y 2 minutos, incluye respuestas esperadas sólo para quien facilita
y aplica una regla de aprobación previa. Un validador controla tamaño, páginas,
fuentes incrustadas, texto extraíble, seudónimo y ausencia de identidad personal.
