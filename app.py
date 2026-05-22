import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Configurações oficiais da sua Evolution API no Render
EVOLUTION_API_URL = "https://evolution-api-shomer.onrender.com"
EVOLUTION_API_KEY = "03dfa2f521050f9d775d4893856245ef0444a9c57c676268e257166bbab09a35"

# Dados de destino
INSTANCE_NAME = "shomer"
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

        # Trata a mensagem vinda do Sigma
        mensagem_bruta = dados.get("msg", "") or dados.get("mensagem", "") or dados.get("desc", "")
        
        if not mensaje_bruta and "cliente" in dados:
            cliente = dados.get("cliente", "")
            desc = dados.get("desc", "")
            mensagem_bruta = f"Cliente: {cliente} - Evento: {desc}"

        if not mensagem_bruta:
            print(f"⚠️ Nenhuma mensagem estruturada encontrada nos dados: {dados}")
            return jsonify({"status": "error", "message": "No message content found"}), 400

        print(f"🚀 EVENTO RECEBIDO DO SIGMA NA NUVEM: {mensagem_bruta}")

        # NA V2 A INSTÂNCIA VAI NO CABEÇALHO (headers)
        headers = {
            "Content-Type": "application/json",
            "apikey": EVOLUTION_API_KEY,
            "instance": INSTANCE_NAME
        }

        # Corpo da requisição ajustado para a v2
        payload = {
            "number": DESTINATION_NUMBER,
            "text": mensagem_bruta,
            "delay": 1200,
            "presence": "composing"
        }

        # URL correta e limpa para envio de texto na v2
        url_envio = f"{EVOLUTION_API_URL.rstrip('/')}/message/sendTextMessage"

        resposta = requests.post(url_envio, json=payload, headers=headers, timeout=15)
        print(f"📡 Repassado para Evolution v2 no Render: Status {resposta.status_code}")
        print(f"📝 Resposta da API: {resposta.text}")

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
