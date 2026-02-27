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

# Configurar cron para rodar às 06:00 (horário de Fortaleza/Brasília-3)
RUN echo "0 6 * * * root cd /app && python execution/importar_posicoes.py >> /var/log/importacao.log 2>&1" \
    > /etc/cron.d/importacao

# Dar permissão ao arquivo de cron
RUN chmod 0644 /etc/cron.d/importacao

# Criar arquivo de log
RUN touch /var/log/importacao.log

# Script de entrada
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

CMD ["/entrypoint.sh"]
