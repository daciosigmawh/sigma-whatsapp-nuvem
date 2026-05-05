from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# --- CONFIGURAÇÕES DA EVOLUTION API ---
API_URL = "https://evolution-api-production-23a02.up.railway.app"
API_KEY = "03dfa2f521050f9d775d4893856245ef0444a9c57c676268e257166bbab09a35"
INSTANCE_NAME = "SigmaWhatsApp" # Ou o nome que você deu na conexão
# O seu número particular para receber os alertas (ex: 5521991334576)
NUMERO_DESTINO = "5521991334576" 

@app.route('/sigma_whats', methods=['POST'])
def sigma_whats():
    # Coleta os dados que o seu PC enviou
    tel = request.args.get('tel')
    cliente = request.args.get('cliente')
    evento = request.args.get('evento')
    desc = request.args.get('desc')

    mensagem = f"🔔 *ALERTA SIGMA*\n\n👤 *Cliente:* {cliente}\n📝 *Evento:* {desc}\n📞 *Tel:* {tel}"

    # Monta a ordem de envio para a Evolution API
    endpoint = f"{API_URL}/message/sendText/{INSTANCE_NAME}"
    headers = {
        "apikey": API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "number": NUMERO_DESTINO,
        "text": mensagem,
        "delay": 1200,
        "linkPreview": False
    }

    try:
        response = requests.post(endpoint, json=payload, headers=headers)
        if response.status_code == 201 or response.status_code == 200:
            print(f"✅ Mensagem enviada para {cliente}")
            return jsonify({"status": "Sucesso", "whatsapp": "Enviado"}), 200
        else:
            print(f"❌ Erro na API: {response.text}")
            return jsonify({"status": "Erro na API", "detalhes": response.text}), 500
    except Exception as e:
        return jsonify({"status": "Erro no Servidor", "erro": str(e)}), 500

@app.route('/')
def home():
    return "<h1>🚀 Sistema Sigma-WhatsApp Ativo!</h1>", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
