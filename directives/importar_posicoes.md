# Diretiva: Importar Posições por Intervalo

## Objetivo
Executar a importação de posições de veículos de forma sequencial (uma placa por vez) para garantir a integridade dos dados e evitar sobrecarga no servidor.

## Entradas
- `dataInicio`: String no formato YYYYMMDD.
- `dataFinal`: String no formato YYYYMMDD.
- `placas`: Lista de strings contendo as placas dos veículos.

## Ferramentas/Scripts
- `execution/importar_posicoes.py`: Script Python que realiza a chamada ao endpoint.

## Fluxo de Execução
1. Ler a lista de placas.
2. Para cada placa na lista:
    a. Preparar o payload JSON com `dataInicio`, `dataFinal` e a placa atual (como uma lista de um único elemento).
    b. Realizar a requisição POST para o endpoint.
    c. Aguardar a resposta de sucesso.
    d. Se houver erro, logar e decidir se interrompe ou continua (estratégia de retentativa).
    e. Adicionar um pequeno atraso (delay) entre as requisições para segurança.

## Saída Esperada
- Logs detalhados de cada execução por placa.
- Relatório final de sucesso/falha por placa.
