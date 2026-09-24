# Menos cunas, otro país

Proyecto para la categoría **Historia visual** del Concurso Nacional de
Visualización de Datos 2026, "Contar con Datos".

## Pregunta central

¿Cómo cambiaron los nacimientos registrados en Argentina entre 2014 y 2024,
en cantidad, territorio y edad de las madres, y qué anticipa esa transformación
sobre la estructura demográfica del país?

## Estado

Fase inicial: preparación metodológica y auditoría de fuentes. El título es
provisorio y toda afirmación permanece como hipótesis hasta ser validada con los
datos oficiales.

## Principios de trabajo

- Reproducibilidad desde la descarga hasta la exportación final.
- Separación explícita entre exploración, inferencia y comunicación.
- Comparaciones con denominadores apropiados: cantidades y tasas no se tratan
  como equivalentes.
- Registro de fuentes, transformaciones, limitaciones y decisiones editoriales.
- Diseño al servicio de la pregunta; no se elige una forma visual antes de
  conocer la estructura de los datos.
- Uso de IA limitado a los usos permitidos por las bases y documentado en
  `docs/ai-usage-log.md`.

## Estructura

```text
data/          Datos crudos locales y tablas procesadas reproducibles
design/        Bocetos, componentes y archivos de diseño
docs/          Brief, metodología, fuentes, hallazgos y decisiones
output/        Exportaciones verificadas para entrega
references/    Índice de referencias; originales privados fuera de Git
scripts/       Descarga, limpieza, análisis y validación
tests/         Controles automáticos de integridad
```

## Fuentes iniciales

- [DEIS - Nacidos vivos](https://www.argentina.gob.ar/salud/deis/datos/nacidosvivos)
- [DEIS - Estadísticas vitales 2024](https://www.argentina.gob.ar/sites/default/files/serie_5_nro_68_anuario_vitales_v4_revisada_ok.pdf)
- [INDEC - Censo 2022](https://www.indec.gob.ar/indec/web/Nivel4-Tema-2-41-165)
- [INDEC - Proyecciones](https://censo.gob.ar/index.php/proyecciones/)
- [Concurso Contar con Datos](https://www.udesa.edu.ar/contar-con-datos)

## Flujo de cambios

Un cambio se publica únicamente después de revisar su diff, ejecutar los
controles aplicables y verificar visualmente cualquier salida gráfica. Los hitos
se etiquetarán como `v0.1-data-audit`, `v0.2-storyboard` y `v1.0-submission`.

## Entorno local

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Las descargas permanecen fuera de Git:

```bash
python scripts/download/download_deis_nacidos_vivos.py
python scripts/validation/audit_deis_nacidos_vivos.py
```
