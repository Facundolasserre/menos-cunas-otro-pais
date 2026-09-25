# Scripts

La automatización se organizará en cuatro etapas:

- `download/`: descarga y checksums.
- `cleaning/`: normalización y controles de esquema.
- `analysis/`: indicadores, tablas y gráficos exploratorios.
- `validation/`: conciliación con anuarios y controles finales.

Los scripts deben ser deterministas, registrar errores de forma explícita y no
modificar los archivos crudos.

Antes de crear un commit se ejecuta:

```bash
bash scripts/validation/check_repo_safety.sh
```

La primera auditoría estructural de DEIS se ejecuta con:

```bash
python scripts/validation/audit_deis_nacidos_vivos.py
```

La normalización y su validación independiente se ejecutan con el entorno del
proyecto:

```bash
.venv/bin/python scripts/cleaning/normalize_deis_nacidos_vivos.py
.venv/bin/python scripts/validation/validate_normalized_data.py
```

La primera orden genera un Parquet local y no versionado. La segunda verifica
esquema, dominios, duplicados, sumas, texto, banderas de calidad y controles
oficiales de 2024; luego regenera los CSV pequeños de `data/processed/` y
`docs/data-quality.md`.

El primer análisis descriptivo y su validación se ejecutan con:

```bash
.venv/bin/python scripts/analysis/build_core_indicators.py
.venv/bin/python scripts/validation/validate_core_indicators.py
```

Generan cinco tablas pequeñas para las tendencias nacional, etaria y territorial,
además de `docs/exploratory-findings.md`.

El análisis territorial de la composición etaria y su validación se ejecutan con:

```bash
.venv/bin/python scripts/analysis/build_age_territory_indicators.py
.venv/bin/python scripts/validation/validate_age_territory_indicators.py
```

Generan tres tablas procesadas y `docs/age-territory-findings.md`. La validación
reconstruye los conteos desde el Parquet, comprueba 384 combinaciones de los años
extremos —incluidas dos celdas con cero— y verifica las 24 trayectorias.

Las cifras elegidas para el storyboard se controlan antes de cada prototipo con:

```bash
.venv/bin/python scripts/validation/validate_storyboard_claims.py
```

El control recalcula magnitudes, períodos, composición nacional, extremos
provinciales y excepciones modales, y comprueba que los valores redondeados
aparezcan en `design/storyboard.md`.

Los prototipos vectoriales se construyen y validan con:

```bash
.venv/bin/python scripts/design/build_storyboard_prototype.py
.venv/bin/python scripts/validation/validate_storyboard_prototype.py
.venv/bin/python scripts/validation/validate_visual_accessibility.py
.venv/bin/python scripts/validation/validate_print_proof.py
```

El constructor genera SVG, PNG y un manifiesto con dimensiones, paleta,
checksums y estado. El validador controla relación A3, integridad, contraste,
texto vectorial, etiquetas indispensables, piso tipográfico y ausencia de
imágenes incrustadas. La auditoría de accesibilidad simula tres deficiencias de
visión cromática y comprueba que la lectura en gris no dependa sólo del color.
El control de impresión verifica la página A3 exacta, texto extraíble, fuentes
incrustadas y ausencia de imágenes rasterizadas dentro del PDF.

El constructor también falla si la línea de la serie temporal invade el área
de una anotación directa, incluido un margen de seguridad alrededor del texto.
