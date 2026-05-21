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

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        dados = request.get_json(force=True, silent=True)
        if not dados:
            print("⚠️ Requisição recebida sem dados JSON válidos.")
            return jsonify({"status": "error", "message": "Invalid JSON"}), 400

        # Captura a mensagem bruta vinda do Sigma
        mensagem_bruta = dados.get("msg", "") or dados.get("mensagem", "")
        
        if not mensagem_bruta:
            print(f"⚠️ Nenhuma mensagem encontrada nos dados: {dados}")
            return jsonify({"status": "error", "message": "No message field found"}), 400

        print(f"🚀 EVENTO RECEBIDO DO SIGMA NA NUVEM: {mensagem_bruta}")

        # Monta o cabeçalho de autenticação para a Evolution API
        headers = {
            "Content-Type": "application/json",
            "apikey": EVOLUTION_API_KEY
        }

        # Monta o corpo da requisição exatamente como a Evolution exige
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

        # Constrói a URL de envio apontando para a instância correta (shomer)
        url_envio = f"{EVOLUTION_API_URL.rstrip('/')}/message/sendText/{INSTANCE_NAME}"

        # Faz o repasse para a Evolution API
        resposta = requests.post(url_envio, json=payload, headers=headers, timeout=15)
        print(f"📡 Repassado para Evolution API: Status {resposta.status_code}")

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
