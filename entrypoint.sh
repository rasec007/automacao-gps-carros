#!/bin/bash
set -e

echo "==================================="
echo " Iniciando container de automacao  "
echo "==================================="
echo "Timezone: $(date +%Z) | $(date)"

# Iniciar o servico de cron em background
service cron start

echo "[OK] Cron iniciado. Script agendado para 06:00 diariamente."
echo "[OK] Logs disponíveis em: /var/log/importacao.log"

# Manter o container vivo (tail do log)
tail -f /var/log/importacao.log
