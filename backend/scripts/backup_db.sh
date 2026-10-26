#!/usr/bin/env bash
# ==============================================================================
# DOCTORIN — AUTOMATED DATABASE BACKUP & ROTATION SCRIPT (LINUX / BASH)
# ==============================================================================
set -euo pipefail

BACKUP_DIR="${BACKUP_DIR:-/var/backups/doctorin}"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${BACKUP_DIR}/doctorin_backup_${TIMESTAMP}.sql.gz"
RETENTION_DAYS=14

POSTGRES_CONTAINER="${POSTGRES_CONTAINER:-doctorin-postgres-prod}"
POSTGRES_USER="${POSTGRES_USER:-doctorin_admin}"
POSTGRES_DB="${POSTGRES_DB:-doctorin_db}"

mkdir -p "${BACKUP_DIR}"

echo "============================================================"
echo "📦 DOCTORIN — STARTING DATABASE BACKUP: ${TIMESTAMP}"
echo "============================================================"

# Execute pg_dump inside container and compress with gzip
if docker exec "${POSTGRES_CONTAINER}" pg_dump -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" | gzip > "${BACKUP_FILE}"; then
    FILESIZE=$(du -h "${BACKUP_FILE}" | cut -f1)
    echo "✅ Database backup successful!"
    echo "📁 Saved to: ${BACKUP_FILE} (${FILESIZE})"
else
    echo "❌ Database backup failed!"
    exit 1
fi

# Cleanup old backups exceeding retention period
echo "🧹 Cleaning up backups older than ${RETENTION_DAYS} days..."
find "${BACKUP_DIR}" -type f -name "doctorin_backup_*.sql.gz" -mtime +${RETENTION_DAYS} -exec rm -f {} \;
echo "✅ Backup rotation complete."
