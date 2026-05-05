from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# --- CONFIGURAÇÕES DA EVOLUTION ---
API_URL = "https://evolution-api-production-23a02.up.railway.app"
API_KEY = "03dfa2f521050f9d775d4893856245ef0444a9c57c676268e257166bbab09a35"
INSTANCE_NAME = "SigmaWhatsApp" 
NUMERO_DESTINO = "5521991334576" # Seu WhatsApp particular com 55 + DDD

@app.route('/enviar', methods=['POST']) # Rota corrigida para /enviar
def enviar():
    # Coleta os dados que o seu PC envia
    cliente = request.args.get('cliente', 'Cliente Sigma')
    desc = request.args.get('desc', 'Alerta de Evento')
    
    # Formata a mensagem bonitinha
    mensagem = f"🔔 *ALERTA SIGMA*\n\n👤 *Cliente:* {cliente}\n📝 *Evento:* {desc}"

    # Prepara o disparo para a Evolution API
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
        print(f"Status da API: {res.status_code}")
        return jsonify({"status": "sucesso"}), 200
    except Exception as e:
        print(f"Erro ao enviar: {str(e)}")
        return jsonify({"status": "erro"}), 500

@app.route('/')
def home():
    return "Servidor Sigma Ativo!", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
