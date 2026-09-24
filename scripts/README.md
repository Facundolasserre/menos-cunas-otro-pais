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
