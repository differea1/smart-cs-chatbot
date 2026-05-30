"""
数据库和知识库备份脚本

用法:
  python scripts/backup.py                     # 手动执行一次备份
  python scripts/backup.py --prune             # 备份并清理超过7天的旧备份

通过 crontab 定时执行：
  0 3 * * * cd /app && python scripts/backup.py --prune    # 每天凌晨3点备份
"""

import os
import sys
import shutil
import argparse
from datetime import datetime, timedelta
from pathlib import Path


# 备份目录
BACKUP_DIR = Path(os.environ.get("BACKUP_DIR", "/app/data/backups"))
# 数据库文件
DB_PATH = Path(os.environ.get("DATABASE_URL", "").replace("sqlite:///", "") or "/app/data/chatbot.db")
# RAG 知识库
CHROMA_PATH = Path(os.environ.get("CHROMA_PATH", "/app/chroma_data"))
# 保留天数
RETENTION_DAYS = int(os.environ.get("BACKUP_RETENTION_DAYS", "7"))


def ensure_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)


def backup_file(src: Path, dst_dir: Path, prefix: str):
    """将文件备份到目标目录，使用时间戳命名"""
    if not src.exists():
        print(f"[WARN] 文件不存在，跳过: {src}")
        return None

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dst_name = f"{prefix}_{timestamp}{src.suffix}"
    dst = dst_dir / dst_name
    shutil.copy2(src, dst)
    print(f"[OK] 备份完成: {dst}")
    return dst


def backup_directory(src: Path, dst_dir: Path, prefix: str):
    """将目录打包备份"""
    if not src.exists():
        print(f"[WARN] 目录不存在，跳过: {src}")
        return None

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dst_name = f"{prefix}_{timestamp}"
    dst = dst_dir / dst_name
    shutil.make_archive(str(dst), "zip", src)
    print(f"[OK] 目录备份完成: {dst}.zip")
    return dst


def prune_old_backups(backup_dir: Path, days: int):
    """删除超过指定天数的旧备份"""
    cutoff = datetime.now() - timedelta(days=days)
    count = 0

    for f in backup_dir.iterdir():
        if f.is_file() and f.stat().st_mtime < cutoff.timestamp():
            f.unlink()
            count += 1
            print(f"[DEL] 已删除旧备份: {f.name}")

    # Also prune .zip archives
    for f in backup_dir.iterdir():
        if f.is_file() and f.suffix == ".zip" and f.stat().st_mtime < cutoff.timestamp():
            f.unlink()
            count += 1
            print(f"[DEL] 已删除旧备份: {f.name}")

    if count == 0:
        print("[OK] 没有需要清理的旧备份")
    else:
        print(f"[OK] 共清理 {count} 个旧备份")


def main():
    parser = argparse.ArgumentParser(description="极米售后助手 - 数据备份工具")
    parser.add_argument("--prune", action="store_true", help="清理超过保留期的旧备份")
    args = parser.parse_args()

    print(f"======== 极米售后助手 数据备份 ========")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"备份目录: {BACKUP_DIR}")
    print(f"数据库路径: {DB_PATH}")
    print(f"知识库路径: {CHROMA_PATH}")
    print(f"保留天数: {RETENTION_DAYS}")
    print()

    ensure_dir(BACKUP_DIR)

    # 备份 SQLite 数据库
    backup_file(DB_PATH, BACKUP_DIR, "chatbot_db")

    # 备份 Chroma 知识库（documents.json）
    chroma_doc = CHROMA_PATH / "documents.json"
    if chroma_doc.exists():
        backup_file(chroma_doc, BACKUP_DIR, "chroma_documents")
    else:
        # 备份整个 chroma_data 目录
        backup_directory(CHROMA_PATH, BACKUP_DIR, "chroma_data")

    # 清理旧备份
    if args.prune:
        print()
        prune_old_backups(BACKUP_DIR, RETENTION_DAYS)

    print()
    print("======== 备份完成 ========")


if __name__ == "__main__":
    main()
