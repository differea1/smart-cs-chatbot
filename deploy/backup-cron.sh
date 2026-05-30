#!/bin/bash
# ============================================
# 极米智能售后助手 - 定时备份脚本
# ============================================
# 通过 crontab 定时执行：
#   0 3 * * * /opt/xgimi-cs-chatbot/deploy/backup-cron.sh >> /var/log/xgimi-backup.log 2>&1
# ============================================

APP_DIR="/opt/xgimi-cs-chatbot"

cd "$APP_DIR" || exit 1

echo "======== $(date '+%Y-%m-%d %H:%M:%S') 开始备份 ========"

# 执行容器内备份
docker compose -f docker-compose.yml -f docker-compose.prod.yml exec -T backend python scripts/backup.py --prune

# 可选：将备份文件同步到远程存储（如阿里云 OSS / S3）
# BACKUP_DIR="$APP_DIR/data/backups"
# rclone sync "$BACKUP_DIR" remote:xgimi-backups/

echo "======== $(date '+%Y-%m-%d %H:%M:%S') 备份完成 ========"
