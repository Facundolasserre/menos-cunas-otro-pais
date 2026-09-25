# Controles

Los controles automáticos verificarán, como mínimo:

- esquema esperado por año;
- unicidad o granularidad declarada;
- categorías y códigos conocidos;
- rangos válidos;
- conciliación de totales con fuentes oficiales;
- tratamiento explícito de faltantes;
- coherencia de indicadores derivados.

Los controles de datos ya implementados son:

- `scripts/validation/audit_deis_nacidos_vivos.py`, que verifica los archivos
  crudos y sus checksums;
- `scripts/validation/validate_normalized_data.py`, que valida el Parquet y
  falla ante cualquier diferencia con las fuentes o los controles oficiales;
- `scripts/validation/validate_core_indicators.py`, que reconcilia las tablas
  nacional, etaria y territorial y recalcula cambios, participaciones y rangos;
- `scripts/validation/validate_age_territory_indicators.py`, que reconcilia las
  distribuciones etarias provinciales, sus ceros explícitos, participaciones,
  grupos modales y cambios 2014–2024;
- `scripts/validation/validate_storyboard_claims.py`, que recalcula desde los
  indicadores cada cifra seleccionada para la narrativa y comprueba su presencia
  en el storyboard;
- `scripts/validation/validate_storyboard_prototype.py`, que verifica archivos,
  checksums, dimensiones, contraste, texto vectorial, piso tipográfico y
  etiquetas de todas las versiones del prototipo;
- `scripts/validation/validate_visual_accessibility.py`, que simula protanopia,
  deuteranopia y tritanopia, y verifica la codificación redundante en gris;
- `scripts/validation/validate_print_proof.py`, que verifica tamaño físico A3,
  página única, texto extraíble, fuentes incrustadas, contenido vectorial y
  ausencia de identidad personal en texto y metadatos;
- `scripts/validation/validate_submission_package.py`, que verifica el límite de
  palabras, fuentes, declaración de IA, seudónimo y ausencia del nombre real;
- `scripts/validation/validate_reader_test_kit.py`, que verifica las cuatro
  páginas A4, sus fuentes, contenido obligatorio y anonimato;
- `scripts/validation/validate_submission_artifact.py`, que verifica el PDF,
  PNG, SVG y manifiesto exactos de la entrega, incluidos anonimato, dimensiones,
  integridad vectorial y ausencia de marcas de prototipo;
- el constructor del prototipo, que rechaza solapamientos entre la línea temporal
  y los rectángulos ampliados de sus anotaciones, y exige separación entre la
  flecha principal y ambos números destacados;
- `scripts/validation/check_repo_safety.sh`, que impide versionar datos locales,
  documentos privados, secretos o archivos demasiado grandes.

Se incorporarán pruebas unitarias cuando la etapa de indicadores añada lógica
analítica reutilizable.
