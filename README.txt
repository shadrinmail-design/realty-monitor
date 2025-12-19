=== СИСТЕМА МОНИТОРИНГА НЕДВИЖИМОСТИ ===

ОПИСАНИЕ:
- Проверяет сайты застройщиков 2 раза в день (10:30 и 19:00 МСК)
- Отслеживает появление новых ЖК с кладовыми
- Отправляет уведомления в Telegram

СТРУКТУРА:
/root/realty-monitor/
  config.py - Конфигурация
  storage.py - Хранение данных
  notifier.py - Уведомления Telegram
  monitor.py - Основной скрипт
  run_monitor.sh - Запуск для cron
  parsers/ - Парсеры застройщиков
  data/ - Сохраненные состояния
  logs/ - Логи

ИСТОЧНИКИ:
1. Аквилон - Кладовые
   https://group-akvilon.ru/novostroyki/kladovye/

РАСПИСАНИЕ:
- 10:30 МСК (07:30 UTC)
- 19:00 МСК (16:00 UTC)

КОМАНДЫ:

Ручной запуск:
  cd /root/realty-monitor && ./run_monitor.sh

Просмотр логов:
  tail -f /root/realty-monitor/logs/monitor_$(date +%Y%m%d).log
  tail -f /root/realty-monitor/logs/cron.log

Просмотр данных:
  cat /root/realty-monitor/data/akvilon_kladovye.json

Проверка cron:
  crontab -l

Тест уведомления:
  cd /root/realty-monitor
  python3 -c "from notifier import TelegramNotifier; TelegramNotifier().send_message('Тест')"

TELEGRAM:
  Бот: @Keller2025_bot
  Chat ID: 337790772
