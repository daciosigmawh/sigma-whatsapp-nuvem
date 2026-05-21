import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Configurações padrão apontando para a sua Evolution API na nuvem
EVOLUTION_API_URL = os.environ.get("EVOLUTION_API_URL", "https://evolution-api-shomer.onrender.com")
EVOLUTION_API_KEY = os.environ.get("EVOLUTION_API_KEY", "03dfa2f521050f9d775d4893856245ef0444a9c57c676268e257166bbab09a35")

# O nome real da instância extraído dos seus logs do Prisma
INSTANCE_NAME = "shomer"
# Seu número de WhatsApp configurado para receber os alertas
DESTINATION_NUMBER = "552121022109"

@app.route('/sigma_whats', methods=['POST'])
def webhook():
    try:
        # Tenta pegar os dados vindos no corpo da requisição (JSON)
        dados = request.get_json(force=True, silent=True)
        if not dados:
            # Caso venham como parâmetros na URL (?cliente=...&desc=...)
            dados = request.args.to_dict()
            
        if not dados:
            print("⚠️ Requisição recebida sem dados válidos.")
            return jsonify({"status": "error", "message": "No data found"}), 400

        # Captura a mensagem tratando as variações que o Sigma pode enviar
        mensagem_bruta = dados.get("msg", "") or dados.get("mensagem", "") or dados.get("desc", "")
        
        # Se vier estruturado por parâmetros separados, monta a mensagem amigável
        if not mensagem_bruta and "cliente" in dados:
            cliente = dados.get("cliente", "")
            desc = dados.get("desc", "")
            mensagem_bruta = f"Cliente: {cliente} - Evento: {desc}"

        if not mensagem_bruta:
            print(f"⚠️ Nenhuma mensagem estruturada encontrada nos dados: {dados}")
            return jsonify({"status": "error", "message": "No message content found"}), 400

        print(f"🚀 EVENTO RECEBIDO DO SIGMA NA NUVEM: {mensagem_bruta}")

        # Cabeçalhos de autenticação da Evolution API
        headers = {
            "Content-Type": "application/json",
            "apikey": EVOLUTION_API_KEY
        }

        # Corpo da mensagem padrão exigido pela API
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

        # ALINHADO: Rota v1 tradicional combinada com o nome de instância correto ('shomer')
        url_envio = f"{EVOLUTION_API_URL.rstrip('/')}/message/sendText/{INSTANCE_NAME}"

        # Faz o disparo para a API do WhatsApp
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
