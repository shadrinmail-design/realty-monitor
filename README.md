# Система мониторинга недвижимости

Автоматическая система мониторинга новостроек с уведомлениями в Telegram.

## Что делает система

- Проверяет сайты застройщиков 2 раза в день (10:30 и 19:00 МСК)
- Отслеживает появление новых ЖК с кладовыми
- Отправляет уведомления в Telegram при обнаружении новых объектов
- Сохраняет историю в логах

## Структура проекта

```
/root/realty-monitor/
├── config.py              # Конфигурация системы
├── storage.py             # Модуль хранения данных
├── notifier.py            # Модуль уведомлений Telegram
├── monitor.py             # Основной скрипт мониторинга
├── run_monitor.sh         # Скрипт запуска для cron
├── parsers/
│   └── akvilon_parser.py  # Парсер для Аквилон
├── data/                  # Сохраненные состояния
└── logs/                  # Логи работы системы
```

## Текущие источники

1. **Аквилон - Кладовые**
   - URL: https://group-akvilon.ru/novostroyki/kladovye/
   - Статус: Активен
   - Текущих ЖК: 7

## Расписание

Система запускается автоматически:
- **10:30 МСК** (07:30 UTC)
- **19:00 МСК** (16:00 UTC)

## Управление

### Ручной запуск
```bash
cd /root/realty-monitor
./run_monitor.sh
```

### Просмотр логов
```bash
# Сегодняшний лог
tail -f /root/realty-monitor/logs/monitor_20251118.log

# Лог cron
tail -f /root/realty-monitor/logs/cron.log
```

### Просмотр сохраненных данных
```bash
cat /root/realty-monitor/data/akvilon_kladovye.json | python3 -m json.tool
```

### Проверка cron
```bash
crontab -l
```

### Тестовое уведомление
```bash
cd /root/realty-monitor
python3 -c from notifier import TelegramNotifier
