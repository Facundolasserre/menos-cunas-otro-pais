# Principios de diseño y análisis

Este documento convierte la bibliografía de la materia en reglas operativas
para **Menos cunas, otro país**. No reemplaza las fuentes originales: funciona
como guía de decisiones y como contrato de calidad del proyecto.

## 1. La sustancia precede a la forma

Una visualización eficaz combina contenido, estadística y diseño. Ningún recurso
gráfico puede rescatar datos pobres, una comparación inválida o una pregunta mal
definida. Primero se establece qué sabemos; después se decide cómo mostrarlo.

**Aplicación:** no fijar metáfora, paleta ni composición final antes de cerrar la
auditoría de datos y la tesis editorial.

## 2. Explorar y explicar son tareas distintas

El análisis exploratorio busca estructura, excepciones, relaciones y problemas
de calidad. La comunicación explicativa selecciona únicamente la evidencia
necesaria para que otra persona comprenda una idea.

**Aplicación:** conservar gráficos exploratorios en el registro de análisis, pero
no trasladarlos automáticamente a la obra final.

## 3. Seguir un pipeline explícito

Se adopta el proceso de Ben Fry:

1. **Acquire:** obtener datos y registrar su procedencia.
2. **Parse:** interpretar campos, códigos, unidades y formatos.
3. **Filter:** delimitar el universo relevante sin ocultar exclusiones.
4. **Mine:** buscar patrones y evaluar hipótesis.
5. **Represent:** elegir marcas y canales adecuados.
6. **Refine:** mejorar jerarquía, claridad y legibilidad.
7. **Interact:** incorporar interacción solo si mejora una tarea concreta.

Cada paso debe ser reproducible y dejar evidencia suficiente para auditarlo.

## 4. Respetar la escala de medición

Las variables nominales, ordinales, cuantitativas y temporales no admiten los
mismos tratamientos. La codificación visual debe preservar las relaciones que
existen en los datos y evitar inventar orden o distancia donde no los hay.

**Aplicación:**

- posición y longitud para magnitudes que requieren comparación precisa;
- orden explícito para edades y tiempo;
- color categórico para grupos sin orden;
- color secuencial o divergente solo con un punto de referencia justificable;
- área, volumen e íconos únicamente cuando no debiliten la comparación.

## 5. Preguntar siempre “¿comparado con qué?”

Una cantidad aislada rara vez constituye evidencia. Toda afirmación debe tener
una referencia adecuada: otro año, otra jurisdicción, una tasa, una distribución
o un grupo de comparación.

**Aplicación:** mostrar nacimientos junto con denominadores pertinentes. Separar
cantidad de nacimientos, tasa bruta de natalidad y medidas de fecundidad.

## 6. Diseñar según la pregunta analítica

El orden gráfico debe responder a la relación investigada. Una serie ordenada
por tiempo responde preguntas temporales; un ranking responde comparaciones; un
diagrama de dispersión permite evaluar asociación. El formato no es neutral.

**Aplicación:** si interesa el cambio provincial, ordenar por magnitud del cambio
o agrupar trayectorias; no conservar el orden alfabético por comodidad.

## 7. Controlar agregaciones y denominadores

La agregación temporal o geográfica puede crear, ocultar o invertir patrones.
Los conteos territoriales pueden repetir simplemente la distribución de la
población.

**Aplicación:**

- comparar resultados anuales con ventanas alternativas cuando corresponda;
- inspeccionar valores detallados antes de resumir;
- calcular tasas con denominadores documentados;
- señalar cambios de definición o cobertura;
- evitar conclusiones basadas únicamente en mapas de cantidades.

## 8. No confundir asociación, mecanismo y causalidad

Una secuencia temporal o correlación no demuestra una causa. Las explicaciones
alternativas y los casos contrarios fortalecen la credibilidad del trabajo.

**Aplicación:** describir patrones por edad, territorio y tiempo sin atribuirlos a
economía, políticas o preferencias individuales salvo que exista una estrategia
causal independiente.

## 9. Mostrar evidencia relevante, no evidencia seleccionada

Excluir silenciosamente observaciones, años sin el efecto esperado o categorías
sin especificar puede producir una historia engañosa.

**Aplicación:** documentar universo, exclusiones, faltantes y sensibilidad de los
hallazgos. Buscar activamente casos que contradigan la tesis inicial.

## 10. Integrar palabras, números y gráficos

La evidencia visual debe convivir con títulos informativos, anotaciones precisas
y fuentes legibles. El texto orienta la lectura; no debe repetir lo evidente ni
compensar un gráfico confuso.

**Aplicación:** cada panel debe tener una función y una frase que exprese el
hallazgo, con definiciones cercanas a los elementos que necesitan explicación.

## 11. Facilitar comparación y detalle

Una buena visualización permite captar primero la estructura general y luego
inspeccionar matices. Los pequeños múltiples, escalas compartidas y alineaciones
consistentes suelen comparar mejor que decoraciones o metáforas literales.

**Aplicación:** usar una arquitectura estable para las 24 jurisdicciones y
reservar cambios de forma o color para diferencias con significado analítico.

## 12. Minimizar ruido, no información

La economía gráfica busca eliminar elementos que compiten con la evidencia, no
reducir el contenido hasta volverlo superficial. La originalidad debe surgir de
la organización del argumento y no de ornamentos que dificultan medir.

**Aplicación:** cualquier ícono de cuna, bebé u objeto simbólico deberá superar
una prueba de comparación contra una alternativa más directa.

## 13. Documentar incertidumbre y responsabilidad

Fuentes, autores, definiciones, errores posibles y limitaciones forman parte de
la visualización. La claridad gráfica es también claridad intelectual.

**Aplicación:** registrar versiones de archivos, checksums, fechas de descarga,
diccionarios, reglas de limpieza y advertencias de calidad de la DEIS.

## 14. Diseñar para acceso real

- Contraste suficiente entre texto y fondo.
- Paleta interpretable con deficiencias de visión cromática.
- Tipografía legible al tamaño final de entrega.
- Ninguna distinción esencial dependiente únicamente del color.
- Fuentes, notas y unidades visibles sin ampliación extraordinaria.

## 15. Criterio de admisión específico del concurso

La IA puede asistir en exploración, limpieza, organización, categorización,
programación e ideación. No se utilizará para generar automáticamente la
visualización final ni para producir imágenes generativas decorativas. Toda
asistencia relevante quedará registrada y será declarada.

## Bibliografía de la materia utilizada

- *InfoVis 01-1*.
- *InfoVis - Antecedentes*.
- *InfoVis - exploratory, explanatory, ...*.
- *InfoVis - cs (acquire & parse) - data wrangling*.
- *Infovis - S. S. Stevens - Level of measurement - Escalas de Medición*.
- *Infovis - Visualization Pipelines*.
- Edward Tufte, *The Visual Display of Quantitative Information*, capítulo 1.
- Edward Tufte, *Visual and Statistical Thinking: Displays of Evidence for
  Making Decisions*.

