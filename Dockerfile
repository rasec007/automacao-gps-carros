# Imagem base Python 3.12
FROM python:3.12-slim

# Instalar cron e timezone
RUN apt-get update && apt-get install -y cron tzdata && \
    rm -rf /var/lib/apt/lists/*

# Definir timezone para America/Fortaleza (UTC-3)
ENV TZ=America/Fortaleza
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Diretório de trabalho
WORKDIR /app

# Copiar dependências e instalar
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código do projeto
COPY . .

# Configurar crons:
# 06:00 - Importação de Posições
# 07:00 - Atualização de OBTs
RUN echo "30 6 * * * root cd /app && /usr/local/bin/python execution/importar_posicoes.py >> /var/log/importacao.log 2>&1" \
    > /etc/cron.d/importacao && \
    echo "30 7 * * * root cd /app && /usr/local/bin/python execution/atualiza_obt.py >> /var/log/atualiza_obt.log 2>&1" \
    >> /etc/cron.d/importacao

# Dar permissão ao arquivo de cron
RUN chmod 0644 /etc/cron.d/importacao

# Criar arquivos de log para ambos os fluxos
RUN touch /var/log/importacao.log && touch /var/log/atualiza_obt.log

# Script de entrada
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

CMD ["/entrypoint.sh"]
