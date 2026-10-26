# ==============================================================================
# DOCTORIN — AUTOMATED DATABASE BACKUP & ROTATION SCRIPT (WINDOWS POWERSHELL)
# ==============================================================================

$BackupDir = "D:\DoctorIn\backups"
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$BackupFile = "$BackupDir\doctorin_backup_$Timestamp.sql"
$RetentionDays = 14

$ContainerName = "doctorin-postgres"
$PostgresUser = "doctorin_admin"
$PostgresDb = "doctorin_db"

if (!(Test-Path -Path $BackupDir)) {
    New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null
}

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "📦 DOCTORIN — STARTING DATABASE BACKUP: $Timestamp" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

try {
    # Run pg_dump from docker container
    docker exec $ContainerName pg_dump -U $PostgresUser -d $PostgresDb > $BackupFile
    Write-Host "✅ Database backup successful!" -ForegroundColor Green
    Write-Host "📁 Saved to: $BackupFile" -ForegroundColor Green
} catch {
    Write-Host "❌ Database backup failed: $_" -ForegroundColor Red
}

# Rotate old backups
$CutoffDate = (Get-Date).AddDays(-$RetentionDays)
Get-ChildItem -Path $BackupDir -Filter "doctorin_backup_*.sql" | Where-Object { $_.LastWriteTime -lt $CutoffDate } | Remove-Item -Force
Write-Host "✅ Backup rotation complete." -ForegroundColor Green
