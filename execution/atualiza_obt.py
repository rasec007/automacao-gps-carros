import requests
import time
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

# =====================================================
# Fluxo: Atualiza OBTs
# Agendamento: diariamente às 07:00
# Independente do fluxo de Importação de Posições
# =====================================================

URL_OBT = "https://integrapsjapi.sda.ce.gov.br/api/ServicoEparceria/ConsumirGetComAutenticacaoAsyncMonitoramentoObt/sda/dWNhcFALfpLfXhygv94/0"

# Timeout progressivo: a cada tentativa, o tempo dobra
# 1ª tentativa: 180s | 2ª: 360s | 3ª: 540s
TIMEOUTS_PROGRESSIVOS = [180, 360, 540]
MAX_TENTATIVAS = len(TIMEOUTS_PROGRESSIVOS)
DELAY_ENTRE_TENTATIVAS = 10  # segundos de espera entre tentativas


def executar_atualizacao_obt(tentativa, timeout):
    """Dispara a requisição de atualização de OBTs com timeout configurável."""
    headers = {"Content-Type": "application/json"}
    
    prefixo = f"[Tentativa {tentativa}/{MAX_TENTATIVAS}]"
    print(f"{prefixo} Executando atualização de OBTs (timeout: {timeout}s)...")
    
    try:
        inicio = time.time()
        response = requests.post(URL_OBT, headers=headers, timeout=timeout)
        duracao = round(time.time() - inicio, 1)
        
        if response.status_code in [200, 201, 202]:
            print(f"[+] Sucesso! ({duracao}s) Status: {response.status_code}")
            print(f"[+] Resposta: {response.text[:300]}")
            return True, response.status_code, response.text, duracao
        else:
            msg = f"HTTP {response.status_code}"
            print(f"[-] Falha ({msg}): {response.text[:200]}")
            return False, response.status_code, msg, duracao
            
    except requests.exceptions.Timeout:
        duracao = timeout
        print(f"[!] Timeout após {timeout}s na tentativa {tentativa}")
        return False, 0, f"Timeout ({timeout}s)", duracao
    except Exception as e:
        print(f"[!] Erro inesperado: {str(e)}")
        return False, 0, str(e), 0


def enviar_whatsapp(texto):
    """Envia uma mensagem de texto via Evolution API."""
    url = os.getenv("WHATSAPP_API_URL")
    apikey = os.getenv("WHATSAPP_API_KEY")
    number = os.getenv("NOTIFY_NUMBER")

    if not all([url, apikey, number]):
        print("[!] Credenciais de WhatsApp não configuradas no .env")
        return False

    payload = {"number": number, "text": texto}
    headers = {"Content-Type": "application/json", "apikey": apikey}

    try:
        print("[*] Enviando relatório via WhatsApp...")
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        if response.status_code in [200, 201]:
            print("[+] Relatório enviado com sucesso!")
            return True
        else:
            print(f"[-] Erro ao enviar WhatsApp ({response.status_code}): {response.text}")
            return False
    except Exception as e:
        print(f"[!] Erro de conexão ao enviar WhatsApp: {str(e)}")
        return False


def main():
    agora = datetime.now()
    data_exibicao = agora.strftime("%d/%m/%Y %H:%M")
    
    print("=" * 55)
    print("FLUXO: ATUALIZAÇÃO DE OBTs")
    print(f"Início: {data_exibicao}")
    print(f"Timeouts progressivos: {TIMEOUTS_PROGRESSIVOS}")
    print("=" * 55)

    sucesso = False
    status_code = 0
    resposta = ""
    duracao_total = 0
    tentativa_final = 0

    for tentativa, timeout in enumerate(TIMEOUTS_PROGRESSIVOS, start=1):
        tentativa_final = tentativa
        ok, codigo, resp, dur = executar_atualizacao_obt(tentativa, timeout)
        duracao_total += dur

        if ok:
            sucesso = True
            status_code = codigo
            resposta = resp
            break
        else:
            status_code = codigo
            resposta = resp
            if tentativa < MAX_TENTATIVAS:
                print(f"[*] Aguardando {DELAY_ENTRE_TENTATIVAS}s antes da próxima tentativa...")
                time.sleep(DELAY_ENTRE_TENTATIVAS)

    # Montar relatório para WhatsApp
    icon = "✅" if sucesso else "❌"
    status_txt = "SUCESSO" if sucesso else "FALHA"
    
    relatorio = f"🔄 *ATUALIZAÇÃO DE OBTs*\n"
    relatorio += f"📅 *Data:* {data_exibicao}\n"
    relatorio += f"==============================\n"
    relatorio += f"{icon} *Status:* {status_txt}\n"
    relatorio += f"🔁 *Tentativas:* {tentativa_final}/{MAX_TENTATIVAS}\n"
    relatorio += f"⏱️ *Tempo total:* {round(duracao_total)}s\n"
    
    if not sucesso:
        relatorio += f"⚠️ *Motivo:* {resposta[:100]}\n"
    
    relatorio += f"=============================="

    print("\n" + relatorio)
    enviar_whatsapp(relatorio)


if __name__ == "__main__":
    main()
