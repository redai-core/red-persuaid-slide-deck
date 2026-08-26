#!/usr/bin/env bash
set -euo pipefail

# Packaging script for PersuAId
# Creates a clean .skill bundle for Claude Desktop / Claude Web and syncs to local ~/.agents/skills/

SKILL_NAME="persuaid"
DIST_DIR="dist"
OUTPUT_FILE="${DIST_DIR}/${SKILL_NAME}.skill"
LOCAL_SKILL_DIR="${HOME}/.agents/skills/${SKILL_NAME}"

echo "📦 Packaging ${SKILL_NAME}..."

mkdir -p "${DIST_DIR}"
rm -f "${OUTPUT_FILE}"

# Clean any existing local pycaches
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true

# Package SKILL.md, references, scripts, and engine into a clean zip archive with .skill extension
zip -r "${OUTPUT_FILE}" SKILL.md references/ scripts/ engine/ -x "*/__pycache__/*" -x "*.pyc" -x "*.DS_Store" > /dev/null

echo "✓ Successfully created: ${OUTPUT_FILE}"

# Synchronize directly to ~/.agents/skills/persuaid/
if [ -d "${HOME}/.agents/skills" ]; then
  echo "🔄 Syncing to local skill directory: ${LOCAL_SKILL_DIR}..."
  mkdir -p "${LOCAL_SKILL_DIR}"
  cp -r SKILL.md references scripts engine "${LOCAL_SKILL_DIR}/"
  cp "${OUTPUT_FILE}" "${LOCAL_SKILL_DIR}/"
  echo "✓ Local skill updated!"
fi

echo "Ready to use in Claude Desktop, Claude Web, and local agents."
