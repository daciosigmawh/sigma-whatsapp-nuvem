import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Configurações oficiais da sua Evolution API no Render
EVOLUTION_API_URL = "https://evolution-api-shomer.onrender.com"
EVOLUTION_API_KEY = "03dfa2f521050f9d775d4893856245ef0444a9c57c676268e257166bbab09a35"

# Seus dados de destino
INSTANCE_NAME = "shomer"
DESTINATION_NUMBER = "552121022109"

@app.route('/sigma_whats', methods=['POST'])
def webhook():
    try:
        dados = request.get_json(force=True, silent=True) or request.args.to_dict()
        mensagem_bruta = dados.get("msg", "") or dados.get("mensagem", "") or dados.get("desc", "")
        if not mensagem_bruta and "cliente" in dados:
            mensagem_bruta = f"Cliente: {dados.get('cliente', '')} - Evento: {dados.get('desc', '')}"
        if not mensagem_bruta:
            mensagem_bruta = "Teste de Alarme Sigma"

        print(f"🚀 [MODO DIAGNÓSTICO v2] Iniciando testes para o evento: {mensagem_bruta}")

        headers = {
            "Content-Type": "application/json",
            "apikey": EVOLUTION_API_KEY
        }

        # --- TESTE 0: Verificar se a instância 'shomer' realmente existe e está conectada ---
        url_status = f"{EVOLUTION_API_URL.rstrip('/')}/instance/connectionState/{INSTANCE_NAME}"
        try:
            res_status = requests.get(url_status, headers=headers, timeout=10)
            print(f"🔍 TESTE 0 (Status da Instância): URL: {url_status} | Status: {res_status.status_code} | Resposta: {res_status.text}")
        except Exception as e:
            print(f"❌ Falha ao tentar o TESTE 0: {str(e)}")

        # Payload padrão para os testes de envio
        payload = {
            "number": DESTINATION_NUMBER,
            "text": mensagem_bruta,
            "textMessage": {"text": mensagem_bruta},
            "options": {"delay": 1200, "presence": "composing", "linkPreview": False}
        }

        # --- TESTE 1: Rota tradicional v1/v2 com instância na URL ---
        url_t1 = f"{EVOLUTION_API_URL.rstrip('/')}/message/sendText/{INSTANCE_NAME}"
        res_t1 = requests.post(url_t1, json=payload, headers=headers, timeout=10)
        print(f"🔍 TESTE 1 (sendText com Instância na URL): Status: {res_t1.status_code} | Resposta: {res_t1.text}")

        # --- TESTE 2: Rota sendTextMessage com instância na URL ---
        url_t2 = f"{EVOLUTION_API_URL.rstrip('/')}/message/sendTextMessage/{INSTANCE_NAME}"
        res_t2 = requests.post(url_t2, json=payload, headers=headers, timeout=10)
        print(f"🔍 TESTE 2 (sendTextMessage com Instância na URL): Status: {res_t2.status_code} | Resposta: {res_t2.text}")

        # --- TESTE 3: Rota limpa mandando a instância no Header ---
        url_t3 = f"{EVOLUTION_API_URL.rstrip('/')}/message/sendText"
        headers_t3 = headers.copy()
        headers_t3["instance"] = INSTANCE_NAME
        res_t3 = requests.post(url_t3, json=payload, headers=headers_t3, timeout=10)
        print(f"🔍 TESTE 3 (sendText limpo com Instância no Header): Status: {res_t3.status_code} | Resposta: {res_t3.text}")

        return jsonify({
            "status": "diagnostico_completo_executado",
            "teste_0_status": res_status.status_code if 'res_status' in locals() else "falhou",
            "teste_1_status": res_t1.status_code,
            "teste_2_status": res_t2.status_code,
            "teste_3_status": res_t3.status_code
        }), 200

    except Exception as e:
        print(f"❌ Erro fatal no script de diagnóstico: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
