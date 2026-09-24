#!/usr/bin/env bash
set -euo pipefail

max_bytes=$((10 * 1024 * 1024))
failed=0

fail() {
  printf 'ERROR: %s\n' "$1" >&2
  failed=1
}

tracked_files="$(git ls-files)"

while IFS= read -r path; do
  [[ -z "$path" ]] && continue

  case "$path" in
    data/raw/.gitkeep|data/interim/.gitkeep|data/processed/local/.gitkeep|references/course-private/.gitkeep)
      ;;
    data/raw/*|data/interim/*|data/processed/local/*|references/course-private/*)
      fail "archivo local o privado versionado: $path"
      ;;
  esac

  case "$path" in
    .env|.env.*|*.pem|*.key|*.p12|*.pfx|*.parquet|*.duckdb|*.db)
      fail "formato o credencial prohibida en Git: $path"
      ;;
  esac

  if [[ -f "$path" ]]; then
    size="$(wc -c < "$path" | tr -d ' ')"
    if (( size > max_bytes )); then
      fail "archivo mayor a 10 MiB: $path ($size bytes)"
    fi
  fi
done <<< "$tracked_files"

secret_patterns='gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}|AKIA[0-9A-Z]{16}|BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY'
secret_files="$(git grep -I -l -E "$secret_patterns" -- . ':!scripts/validation/check_repo_safety.sh' || true)"
if [[ -n "$secret_files" ]]; then
  while IFS= read -r path; do
    [[ -n "$path" ]] && fail "posible secreto detectado en: $path"
  done <<< "$secret_files"
fi

if ! git diff --cached --check; then
  fail "el área staged contiene errores de whitespace"
fi

if (( failed != 0 )); then
  exit 1
fi

printf 'OK: control de seguridad del repositorio superado.\n'
