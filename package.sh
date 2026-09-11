#!/usr/bin/env bash
set -euo pipefail

# Packaging script for PersuAId (this repo root)
# Creates a clean .skill bundle for Claude Desktop / Claude Web upload.

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "${ROOT}"

SKILL_NAME="persuaid"
DIST_DIR="dist"
OUTPUT_FILE="${DIST_DIR}/${SKILL_NAME}.skill"
LOCAL_SKILL_DIR="${HOME}/.agents/skills/${SKILL_NAME}"

echo "Packaging ${SKILL_NAME} from ${ROOT}..."

if [[ ! -f SKILL.md ]]; then
  echo "ERROR: SKILL.md not found at repo root" >&2
  exit 1
fi

mkdir -p "${DIST_DIR}"
rm -f "${OUTPUT_FILE}"

find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true

INCLUDE=(SKILL.md references/ scripts/ engine/)
[[ -d assets ]] && INCLUDE+=(assets/)
for f in requirements.txt requirements-server.txt package.json pyproject.toml; do
  [[ -f "$f" ]] && INCLUDE+=("$f")
done

zip -r "${OUTPUT_FILE}" "${INCLUDE[@]}" \
  -x "*/__pycache__/*" -x "*.pyc" -x "*.DS_Store" -x "*/node_modules/*" \
  > /dev/null

SIZE="$(du -h "${OUTPUT_FILE}" | awk '{print $1}')"
echo "Created: ${OUTPUT_FILE} (${SIZE})"
unzip -l "${OUTPUT_FILE}" | head -40

# Optional local install (best-effort; upload still works without this)
if [[ -d "${HOME}/.agents/skills" ]]; then
  if mkdir -p "${LOCAL_SKILL_DIR}" 2>/dev/null; then
    cp -R SKILL.md references scripts engine "${LOCAL_SKILL_DIR}/"
    cp "${OUTPUT_FILE}" "${LOCAL_SKILL_DIR}/"
    echo "Local skill updated: ${LOCAL_SKILL_DIR}"
  else
    echo "Skipped local sync (no permission to ${LOCAL_SKILL_DIR})."
  fi
fi

echo "Upload ${OUTPUT_FILE} to Claude Desktop / Claude Web Custom Skills."
