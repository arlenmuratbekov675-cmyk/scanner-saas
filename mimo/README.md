# MiMo Research Environment

**Статус:** Research system (не production)
**Версия изоляции:** 2.0

## Правила (строгие)

1. MiMo работает ТОЛЬКО в `C:\Projects\mimo`
2. MiMo НЕ может изменять файлы в `C:\Projects\trading_bot`
3. MiMo НЕ может импортировать модули из trading_bot
4. Связь с trading_bot ТОЛЬКО через `output/signals.json`

## Использование

Каждый скрипт MiMo ДОЛЖЕН начинаться с:

```python
from isolation import assert_isolated, block_trading_bot_access

assert_isolated()          # Проверка что мы в mimo/
block_trading_bot_access() # Блокировка импорта trading_bot
```

Запись сигналов:

```python
from isolation import write_signal

write_signal({
    "symbol": "EURUSD",
    "action": "buy",
    "price": 1.0850,
    "timestamp": "2026-06-14T08:00:00Z"
})
```

## Структура

```
mimo/
├── config.yaml          # Конфигурация MiMo
├── isolation.py         # Модуль изоляции (ОБЯЗАТЕЛЕН)
├── output/
│   └── signals.json     # Единственный мост к trading_bot
└── research/            # Research код
```

## Запрещено

- Импорт модулей из trading_bot
- Запись в директорию trading_bot
- Доступ к .env файлам trading_bot
- Запуск процессов trading_bot
- Relative paths (../)
- Доступ к C:\Users, C:\Windows, /tmp, /var

## Мост (signals.json)

Формат:

```json
{
  "symbol": "EURUSD",
  "action": "buy|sell|hold",
  "price": 1.0850,
  "confidence": 0.85,
  "timestamp": "2026-06-14T08:00:00Z",
  "reason": "FVG + OB confluence"
}
```

trading_bot читает ТОЛЬКО отсюда.
