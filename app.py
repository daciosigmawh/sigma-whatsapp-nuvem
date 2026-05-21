import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# URL correta da sua Evolution API hospedada no Railway
EVOLUTION_API_URL = "https://evolution-api-production-23a0.up.railway.app"
# Sua chave global de autenticação
EVOLUTION_API_KEY = "03dfa2f521050f9d775d4893856245ef0444a9c57c676268e257166bbab09a35"

# Nome exato da instância que está ativa no seu painel do Railway
INSTANCE_NAME = "SigmaWhatsApp"
# Seu número de WhatsApp que vai receber os alertas
DESTINATION_NUMBER = "552121022109"

@app.route('/sigma_whats', methods=['POST'])
def webhook():
    try:
        dados = request.get_json(force=True, silent=True)
        if not dados:
            dados = request.args.to_dict()
            
        if not dados:
            print("⚠️ Requisição recebida sem dados válidos.")
            return jsonify({"status": "error", "message": "No data found"}), 400

        # Captura a mensagem tratando as variações do Sigma
        mensagem_bruta = dados.get("msg", "") or dados.get("mensagem", "") or dados.get("desc", "")
        
        if not mensagem_bruta and "cliente" in dados:
            cliente = dados.get("cliente", "")
            desc = dados.get("desc", "")
            mensagem_bruta = f"Cliente: {cliente} - Evento: {desc}"

        if not mensagem_bruta:
            print(f"⚠️ Nenhuma mensagem estruturada encontrada nos dados: {dados}")
            return jsonify({"status": "error", "message": "No message content found"}), 400

        print(f"🚀 EVENTO RECEBIDO DO SIGMA NA NUVEM: {mensagem_bruta}")

        headers = {
            "Content-Type": "application/json",
            "apikey": EVOLUTION_API_KEY
        }

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

        # Rota v1 apontando para a URL do Railway e para a instância SigmaWhatsApp
        url_envio = f"{EVOLUTION_API_URL.rstrip('/')}/message/sendText/{INSTANCE_NAME}"

        resposta = requests.post(url_envio, json=payload, headers=headers, timeout=15)
        print(f"📡 Repassado para Evolution API no Railway: Status {resposta.status_code}")

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
