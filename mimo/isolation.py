"""
Изоляция MiMo от trading_bot.
Версия 2.0 — полная блокировка доступа.
"""
import os
import sys

MIMO_ROOT = os.path.abspath(r"C:\Projects\mimo")
TRADING_BOT_ROOT = os.path.abspath(r"C:\Projects\trading_bot")

# Единственный разрешённый путь для записи (мост)
BRIDGE_PATH = os.path.join(MIMO_ROOT, "output", "signals.json")


def assert_isolated():
    """
    Проверяет, что MiMo работает в изолированном окружении.
    Вызывать в начале каждого скрипта MiMo.
    """
    cwd = os.path.abspath(os.getcwd())
    
    if not cwd.startswith(MIMO_ROOT):
        raise RuntimeError(
            f"ISOLATION VIOLATION: MiMo должен работать в {MIMO_ROOT}\n"
            f"Текущая директория: {cwd}"
        )


def block_trading_bot_access():
    """
    Блокирует импорт модулей из trading_bot.
    Вызывать в начале каждого скрипта MiMo.
    """
    if TRADING_BOT_ROOT in sys.path:
        sys.path.remove(TRADING_BOT_ROOT)
    
    import builtins
    original_import = builtins.__import__
    
    def guarded_import(name, *args, **kwargs):
        if "trading_bot" in name or "tradesignal" in name or "auto_signal" in name:
            raise ImportError(
                f"ISOLATION VIOLATION: import '{name}' blocked for MiMo."
            )
        return original_import(name, *args, **kwargs)
    
    builtins.__import__ = guarded_import


def write_signal(signal_data: dict):
    """
    Записывает сигнал в唯一的 мост (signals.json).
    MiMo может ТОЛЬКО писать сюда.
    """
    import json
    
    abs_path = os.path.abspath(BRIDGE_PATH)
    
    if not abs_path.startswith(MIMO_ROOT):
        raise PermissionError("WRITE DENIED: мост вне MiMo")
    
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    
    with open(abs_path, "w") as f:
        json.dump(signal_data, f, indent=2)


def read_bridge() -> dict:
    """
    Читает данные из моста (только output/signals.json).
    """
    import json
    
    abs_path = os.path.abspath(BRIDGE_PATH)
    
    if not os.path.exists(abs_path):
        return {}
    
    with open(abs_path, "r") as f:
        return json.load(f)
