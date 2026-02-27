# Diretiva: Atualiza OBTs (Objetos de Benefício Tributário)

## Objetivo
Executar diariamente, às 07:00, a sincronização dos dados de OBTs via API parceira.
Este é um fluxo **independente** do fluxo de importação de posições.

## Endpoint

```
POST https://integrapsjapi.sda.ce.gov.br/api/ServicoEparceria/ConsumirGetComAutenticacaoAsyncMonitoramentoObt/sda/dWNhcFALfpLfXhygv94/0
```

- **Método**: POST
- **Body**: Sem body (requisição vazia)
- **Autenticação**: Embutida na URL (`sda/dWNhcFALfpLfXhygv94/0`)

## Comportamento Esperado

Este endpoint é assíncrono e pode demorar bastante para responder dependendo do volume de dados.
O script lida com isso através de **timeout progressivo**:

| Tentativa | Timeout |
|-----------|---------|
| 1ª        | 180s    |
| 2ª        | 360s    |
| 3ª        | 540s    |

## Fluxo de Execução

1. Disparar a requisição POST para o endpoint
2. Aguardar a resposta dentro do timeout configurado
3. Em caso de timeout, aguardar 10 segundos e tentar novamente com o dobro do tempo
4. Após máximo de 3 tentativas, registrar falha e encerrar
5. Enviar notificação via WhatsApp com o resultado final

## Notificação WhatsApp

Ao final da execução (sucesso ou falha), enviar relatório via Evolution API:
- URL, API Key e número configurados no `.env`
- Formato: texto com emoji e status da atualização

## Agendamento

Cron: `0 7 * * *` → Diariamente às **07:00 (UTC-3)**
