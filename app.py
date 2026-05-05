from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# --- CONFIGURAÇÕES DA EVOLUTION ---
API_URL = "https://evolution-api-production-23a02.up.railway.app"
API_KEY = "03dfa2f521050f9d775d4893856245ef0444a9c57c676268e257166bbab09a35"
INSTANCE_NAME = "SigmaWhatsApp" 

@app.route('/sigma_whats', methods=['POST', 'GET']) # Rota idêntica ao seu print
def sigma_whats():
    # Pega os dados exatamente como aparecem no seu PowerShell
    cliente = request.args.get('cliente', 'Cliente Sigma')
    evento = request.args.get('desc', 'Evento detectado')
    telefone = request.args.get('tel', '5521991334576') # Se não vier, manda pra você

    # Limpa o telefone para garantir que só tenha números
    num_limpo = ''.join(filter(str.isdigit, telefone))
    
    # Formata a mensagem
    mensagem = f"🔔 *ALERTA SIGMA*\n\n👤 *Cliente:* {cliente}\n📝 *Evento:* {evento}"

    endpoint = f"{API_URL}/message/sendText/{INSTANCE_NAME}"
    headers = {
        "apikey": API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "number": num_limpo,
        "text": mensagem
    }

    try:
        res = requests.post(endpoint, json=payload, headers=headers)
        # Retorna a resposta que o seu script local espera para não dar erro de JSON
        return jsonify({"status": "sucesso", "origem": cliente}), 200
    except Exception as e:
        return jsonify({"status": "erro", "erro": str(e)}), 500

@app.route('/')
def home():
    return "🚀 Servidor Sigma Online!", 200

if __name__ == '__main__':
    # O Render exige que a porta seja 10000 ou lida do ambiente
    app.run(host='0.0.0.0', port=10000)
