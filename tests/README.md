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
- `scripts/validation/check_repo_safety.sh`, que impide versionar datos locales,
  documentos privados, secretos o archivos demasiado grandes.

Se incorporarán pruebas unitarias cuando la etapa de indicadores añada lógica
analítica reutilizable.
