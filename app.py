import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Configurações vindas das variáveis de ambiente do Render
EVOLUTION_API_URL = os.environ.get("EVOLUTION_API_URL", "https://evolution-api-shomer.onrender.com")
EVOLUTION_API_KEY = os.environ.get("EVOLUTION_API_KEY", "03dfa2f521050f9d775d4893856245ef0444a9c57c676268e257166bbab09a35")

# Nome correto da instância identificado nos logs
INSTANCE_NAME = "shomer"
# Seu número de WhatsApp configurado para receber os alertas
DESTINATION_NUMBER = "552121022109"

# Rota corrigida para bater com o envio do Sigma (/sigma_whats)
@app.route('/sigma_whats', methods=['POST'])
def webhook():
    try:
        dados = request.get_json(force=True, silent=True)
        if not dados:
            dados = request.args.to_dict()
            
        if not dados:
            print("⚠️ Requisição recebida sem dados válidos.")
            return jsonify({"status": "error", "message": "No data found"}), 400

        # Captura a mensagem bruta vinda do Sigma
        mensagem_bruta = dados.get("msg", "") or dados.get("mensagem", "") or dados.get("desc", "")
        
        if not mensagem_bruta and "cliente" in dados:
            cliente = dados.get("cliente", "")
            desc = dados.get("desc", "")
            mensagem_bruta = f"Cliente: {cliente} - Evento: {desc}"

        if not mensagem_bruta:
            print(f"⚠️ Nenhuma mensagem estruturada encontrada nos dados: {dados}")
            return jsonify({"status": "error", "message": "No message content found"}), 400

        print(f"🚀 EVENTO RECEBIDO DO SIGMA NA NUVEM: {mensagem_bruta}")

        # Monta o cabeçalho de autenticação
        headers = {
            "Content-Type": "application/json",
            "apikey": EVOLUTION_API_KEY
        }

        # Monta o payload ajustado para a rota v2 da Evolution API
        payload = {
            "number": DESTINATION_NUMBER,
            "options": {
                "delay": 1200,
                "presence": "composing",
                "linkPreview": False
            },
            "textMessage": {
                "text": mensagem_bruta
            }
        }

        # CORREÇÃO DA ROTA V2: O nome da instância entra como parâmetro na URL (?instance=nome)
        url_envio = f"{EVOLUTION_API_URL.rstrip('/')}/message/sendText?instance={INSTANCE_NAME}"

        # Faz o repasse para a Evolution API
        resposta = requests.post(url_envio, json=payload, headers=headers, timeout=15)
        print(f"📡 Repassado para Evolution API: Status {resposta.status_code}")

        # Se a rota com parâmetro ainda falhar, tenta o formato alternativo com a instância no cabeçalho/payload
        if resposta.status_code == 404:
            print("🔄 Tentando rota alternativa v2...")
            url_envio_alt = f"{EVOLUTION_API_URL.rstrip('/')}/message/sendText"
            payload["instance"] = INSTANCE_NAME
            resposta = requests.post(url_envio_alt, json=payload, headers=headers, timeout=15)
            print(f"📡 Repassado para Evolution API (Alternativa): Status {resposta.status_code}")

        return jsonify({
            "status": "success",
            "sigma_received": True,
            "evolution_status": resposta.status_code
        }), 200

    except Exception as e:
        print(f"❌ Erro crítico no processamento do webhook: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
