#!/usr/bin/env bash
set -euo pipefail

# Packaging script for PersuAId
# Creates a .skill bundle for Claude Desktop / Claude Web

SKILL_NAME="persuaid"
DIST_DIR="dist"
OUTPUT_FILE="${DIST_DIR}/${SKILL_NAME}.skill"

echo "📦 Packaging ${SKILL_NAME}..."

mkdir -p "${DIST_DIR}"
rm -f "${OUTPUT_FILE}"

# Package SKILL.md and references into a zip archive with .skill extension
zip -r "${OUTPUT_FILE}" SKILL.md references/ > /dev/null

echo "✓ Successfully created: ${OUTPUT_FILE}"
echo "You can import this file directly into Claude Desktop or Claude Web skills settings."
