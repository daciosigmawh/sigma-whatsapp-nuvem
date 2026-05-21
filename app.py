import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

EVOLUTION_API_URL = "https://evolution-api-shomer.onrender.com"
EVOLUTION_API_KEY = "03dfa2f521050f9d775d4893856245ef0444a9c57c676268e257166bbab09a35"
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
            mensagem_bruta = "Teste de Evento do Sigma"

        print(f"🚀 EVENTO RECEBIDO: {mensagem_bruta}")

        headers = {"Content-Type": "application/json", "apikey": EVOLUTION_API_KEY}
        
        # TESTE 1: Verificar se a instância existe e o status dela
        url_status = f"{EVOLUTION_API_URL.rstrip('/')}/instance/connectionState/{INSTANCE_NAME}"
        try:
            res_status = requests.get(url_status, headers=headers, timeout=10)
            print(f"🔍 TESTE 1 (Status Instância): Rota: {url_status} | Resposta: {res_status.status_code} - {res_status.text}")
        except Exception as e:
            print(f"❌ Falha no TESTE 1: {str(e)}")

        # TESTE 2: Tentar enviar o texto usando a rota padrão v1
        payload = {
            "number": DESTINATION_NUMBER,
            "options": {"delay": 1200, "presence": "composing", "linkPreview": False},
            "textMessage": {"text": mensagem_bruta}
        }
        url_v1 = f"{EVOLUTION_API_URL.rstrip('/')}/message/sendText/{INSTANCE_NAME}"
        res_v1 = requests.post(url_v1, json=payload, headers=headers, timeout=10)
        print(f"📡 TESTE 2 (Rota v1): Resposta: {res_v1.status_code}")

        return jsonify({"status": "diagnostico_rodado", "v1_status": res_v1.status_code}), 200

    except Exception as e:
        print(f"❌ Erro crítico: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
