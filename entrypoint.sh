#!/bin/bash
set -e

echo "==================================="
echo " Iniciando container de automacao  "
echo "==================================="
echo "Timezone: $(date +%Z) | $(date)"

# Iniciar o servico de cron em background
service cron start

echo "[OK] Cron iniciado. Agendamentos configurados:"
echo "     - 06:00 -> Importação de Posições (importar_posicoes.py)"
echo "     - 07:00 -> Atualização de OBTs    (atualiza_obt.py)"
echo ""
echo "[OK] Logs disponíveis em:"
echo "     - /var/log/importacao.log"
echo "     - /var/log/atualiza_obt.log"

# Manter o container vivo monitorando ambos os logs
tail -f /var/log/importacao.log /var/log/atualiza_obt.log
