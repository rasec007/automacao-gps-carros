import requests
import time
import json
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

def importar_posicao_placa(data_inicio, data_final, placa, tentativa=1, timeout=420):
    url = "https://integrapsjapi.sda.ce.gov.br/api/servicoautomatizado/ImportarPosicoesIntervaloAsync"
    
    payload = {
        "dataInicio": data_inicio,
        "dataFinal": data_final,
        "placas": [placa]
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    # Timeout configurável: 420s na 1ª tentativa, 540s na 2ª (placas com alto volume)
    TIMEOUT = timeout
    
    try:
        prefixo = f"[*] [Tentativa {tentativa}]" if tentativa > 1 else "[*]"
        print(f"{prefixo} Processando placa: {placa}...")
        
        response = requests.post(url, json=payload, headers=headers, timeout=TIMEOUT)
        
        if response.status_code in [200, 202]:
            try:
                resp_text = response.text
                total_inserido = 0
                
                if "totalInserido =" in resp_text:
                    parts = resp_text.split("totalInserido =")
                    if len(parts) > 1:
                        val_str = parts[1].split(",")[0].split("}")[0].strip()
                        total_inserido = int(val_str)
                
                print(f"[+] Sucesso para placa {placa}: {resp_text}")
                return True, total_inserido, "Sucesso"
            except Exception as e:
                return True, 0, f"Erro no parse: {str(e)}"
        else:
            msg_erro = f"HTTP {response.status_code}"
            print(f"[-] Erro para placa {placa} ({msg_erro}): {response.text}")
            return False, 0, msg_erro
            
    except requests.exceptions.Timeout:
        print(f"[!] Timeout (>{TIMEOUT}s) para placa {placa}")
        return False, 0, "Timeout"
    except Exception as e:
        print(f"[!] Erro para placa {placa}: {str(e)}")
        return False, 0, str(e)

def executar_fluxo_placas(data_inicio, data_final, lista_placas, delay):
    resultados = {}
    for placa in lista_placas:
        sucesso, inseridos, status = importar_posicao_placa(data_inicio, data_final, placa)
        resultados[placa] = {"sucesso": sucesso, "inseridos": inseridos, "status": status, "tentativas": 1}
        
        if placa != lista_placas[-1]:
            time.sleep(delay)
    return resultados

def enviar_whatsapp(texto):
    url = os.getenv("WHATSAPP_API_URL")
    apikey = os.getenv("WHATSAPP_API_KEY")
    number = os.getenv("NOTIFY_NUMBER")
    
    if not all([url, apikey, number]):
        print("[!] Erro: Credenciais de WhatsApp não configuradas no .env")
        return False
        
    payload = {
        "number": number,
        "text": texto
    }
    
    headers = {
        "Content-Type": "application/json",
        "apikey": apikey
    }
    
    try:
        print("[*] Enviando relatório via WhatsApp...")
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code in [200, 201]:
            print("[+] Relatório enviado com sucesso para o WhatsApp!")
            return True
        else:
            print(f"[-] Erro ao enviar WhatsApp (Status {response.status_code}): {response.text}")
            return False
    except Exception as e:
        print(f"[!] Erro de conexão ao enviar WhatsApp: {str(e)}")
        return False

def main():
    ontem = datetime.now() - timedelta(days=1)
    data_formatada = ontem.strftime("%Y%m%d")
    
    data_inicio = data_formatada
    data_final = data_formatada
    
    print(f"[*] Período de importação: {data_formatada} (Timeout 1ª: 420s | Retentativa: 540s)")
    
    placas_original = [
        "THP2G70","THP2H90","THQ7I90","THR6C10","THR6D40","THR6D60","THR6G10","THR6H10","THR7A50","THR7A60","THR7E30","THU3C20","THU4A70","THU4H30","THU5B30","THV4G30","THV6I60","THV7I30","THV8C80","THV8J40","THY1C50","THY2E30","THY5C20","THY6D80","TIF7I20","TIG0A20","TIG2A10","TIG3C20","TIG3F00","TIG3H20","TIG3J80","TIG7A90","TIH5J00","TII2J80","TII3B20","TII3C50","TII3F10","TIM8B50"
    ]
    
    delay_segundos = 2
    
    # Primeira Passada
    print("\n--- INICIANDO PRIMEIRA PASSADA ---")
    resultados = executar_fluxo_placas(data_inicio, data_final, placas_original, delay_segundos)
    
    # Identificar placas para Retentativa (Zeros ou Erros/Timeouts)
    placas_para_retry = [p for p, res in resultados.items() if not res["sucesso"] or res["inseridos"] == 0]
    
    if placas_para_retry:
        print(f"\n--- INICIANDO RETENTATIVA PARA {len(placas_para_retry)} PLACAS (ZEROS OU TIMEOUTS) ---")
        time.sleep(5) # Pausa extra antes do retry
        
        for placa in placas_para_retry:
            # Dobrar o timeout na 2ª tentativa: placas com alto volume (800+ registros)
            # precisam de mais tempo para que a API conclua a importação completa
            sucesso, inseridos, status = importar_posicao_placa(
                data_inicio, data_final, placa, tentativa=2, timeout=540
            )
            
            # Atualizamos os resultados com os dados da 2ª tentativa (seja sucesso ou falha)
            # Mas mantemos o total de inseridos anterior se ele for maior (caso a 2ª dê erro)
            novo_inseridos = max(inseridos, resultados[placa]["inseridos"])
            resultados[placa] = {
                "sucesso": sucesso, 
                "inseridos": novo_inseridos, 
                "status": status, 
                "tentativas": 2
            }
            
            if placa != placas_para_retry[-1]:
                time.sleep(delay_segundos)

    # Construção do Relatório Texto para WhatsApp
    data_relatorio = ontem.strftime("%d/%m/%Y")
    relatorio_txt =  "📊 *RELATÓRIO DE IMPORTAÇÃO*\n"
    relatorio_txt += f"📅 *DATA:* {data_relatorio}\n"
    relatorio_txt += "==============================\n"
    relatorio_txt += f"✅ *Total Placas:* {len(placas_original)}\n"
    relatorio_txt += "------------------------------\n"
    
    total_geral_inserido = 0
    placas_com_sucesso = 0
    
    for placa in placas_original:
        res = resultados[placa]
        tent_str = " (2ª 🔄)" if res['tentativas'] > 1 else ""
        
        if res["sucesso"]:
            icon = "✅"
            status_msg = f"{res['inseridos']}"
        else:
            icon = "❌"
            status_msg = f"{res['status']}"
        
        relatorio_txt += f"🚗 *{placa}:* {status_msg} {icon}{tent_str}\n"
        
        total_geral_inserido += res['inseridos']
        if res["sucesso"]: placas_com_sucesso += 1
        
    relatorio_txt += "------------------------------\n"
    relatorio_txt += f"🏆 *TOTAL INSERIDO:* {total_geral_inserido}\n"
    relatorio_txt += f"📈 *SUCESSO:* {placas_com_sucesso}/{len(placas_original)}\n"
    relatorio_txt += "=============================="

    # Exibe no console
    print("\n" + relatorio_txt)
    
    # Envia para o WhatsApp
    enviar_whatsapp(relatorio_txt)

if __name__ == "__main__":
    main()
