#!/bin/bash
# Скрипт запуска мониторинга с переменными окружения

export TELEGRAM_BOT_TOKEN='8263362924:AAFPPXdy0Z3Xex4EvqCDVQ_r9VJHqzveMlo'
export TELEGRAM_CHAT_ID='337790772'

cd /root/realty-monitor
/usr/bin/python3 /root/realty-monitor/monitor.py >> /root/realty-monitor/logs/cron.log 2>&1
