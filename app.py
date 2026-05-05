from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# --- CONFIGURAÇÕES ---
API_URL = "https://evolution-api-production-23a02.up.railway.app"
API_KEY = "03dfa2f521050f9d775d4893856245ef0444a9c57c676268e257166bbab09a35"
INSTANCE_NAME = "SigmaWhatsApp" 
NUMERO_DESTINO = "5521991334576" 

@app.route('/enviar', methods=['POST'])
def enviar():
    # Coleta os dados REAIS que vêm do seu computador
    # O .get('cliente') pega o nome do cliente
    # O .get('desc') pega se foi Armado ou Desarmado
    cliente_real = request.args.get('cliente', 'Cliente não identificado')
    evento_real = request.args.get('desc', 'Evento não identificado')
    
    # Formata a mensagem com os dados dinâmicos
    mensagem = f"🔔 *ALERTA SIGMA*\n\n👤 *Cliente:* {cliente_real}\n📝 *Evento:* {evento_real}"

    endpoint = f"{API_URL}/message/sendText/{INSTANCE_NAME}"
    headers = {
        "apikey": API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "number": NUMERO_DESTINO,
        "text": mensagem
    }

    try:
        res = requests.post(endpoint, json=payload, headers=headers)
        return jsonify({"status": "sucesso", "origem": cliente_real}), 200
    except Exception as e:
        return jsonify({"status": "erro", "detalhes": str(e)}), 500

@app.route('/')
def home():
    return "Servidor Sigma Online", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
