"""单用户主线存档和关卡成绩管理。"""

import json
from pathlib import Path
import sys


if getattr(sys, "frozen", False):
    # 打包后把进度写在 exe 所在目录，方便随游戏文件夹一起保存。
    DATA_DIR = Path(sys.executable).resolve().parent
else:
    DATA_DIR = Path(__file__).resolve().parent

SAVE_FILE = DATA_DIR / "savegame.json"
PROGRESS_FILE = DATA_DIR / "level_progress.json"
USERS_FILE = DATA_DIR / "users_data.json"


def _read_json(path, default):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


def _write_json(path, data):
    temp_file = path.with_suffix(".tmp")
    temp_file.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    temp_file.replace(path)


def migrate_current_user_data():
    """将最后登录玩家的数据迁回单用户文件，仅执行一次。"""
    data = _read_json(USERS_FILE, None)
    if not isinstance(data, dict) or not isinstance(data.get("users"), dict):
        return
    username = data.get("current_user")
    profile = data["users"].get(username)
    if not isinstance(profile, dict):
        return
    if not SAVE_FILE.exists() and isinstance(profile.get("saved_game"), dict):
        _write_json(SAVE_FILE, profile["saved_game"])
    if not PROGRESS_FILE.exists() and isinstance(profile.get("level_progress"), list):
        _write_json(PROGRESS_FILE, profile["level_progress"])


migrate_current_user_data()


def save_game(data):
    _write_json(SAVE_FILE, data)


def load_game():
    data = _read_json(SAVE_FILE, None)
    required = {
        "mode", "level", "remaining_arrows",
        "mistakes_left", "moves_count", "elapsed_ms",
    }
    if isinstance(data, dict) and required.issubset(data):
        return data
    return None


def clear_save():
    try:
        SAVE_FILE.unlink(missing_ok=True)
    except OSError:
        pass


def load_level_progress(level_count):
    raw = _read_json(PROGRESS_FILE, [])
    raw = raw if isinstance(raw, list) else []
    progress = []
    for index in range(level_count):
        item = raw[index] if index < len(raw) and isinstance(raw[index], dict) else {}
        best_time = item.get("best_time")
        progress.append(
            {
                "completed": bool(item.get("completed", False)),
                "stars": max(0, min(3, int(item.get("stars", 0)))),
                "best_time": (
                    max(1, int(best_time))
                    if isinstance(best_time, (int, float)) and best_time > 0
                    else None
                ),
            }
        )
    return progress


def save_level_progress(progress):
    _write_json(PROGRESS_FILE, progress)
