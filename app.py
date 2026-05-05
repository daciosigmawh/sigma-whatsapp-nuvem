from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# --- CONFIGURAÇÕES FIXAS ---
API_URL = "https://evolution-api-production-23a02.up.railway.app"
API_KEY = "03dfa2f521050f9d775d4893856245ef0444a9c57c676268e257166bbab09a35"
INSTANCE_NAME = "SigmaWhatsApp"

@app.route('/sigma_whats', methods=['POST', 'GET'])
def sigma_whats():
    # Tenta pegar os dados da URL (args) ou do formulário (form)
    # Isso garante que o nome do Vilson seja capturado
    cliente = request.args.get('cliente') or request.form.get('cliente') or "Cliente Sigma"
    evento = request.args.get('desc') or request.form.get('desc') or "Evento detectado"
    telefone = request.args.get('tel') or request.form.get('tel') or "5521991334576"

    # Limpeza de segurança no telefone
    num_limpo = ''.join(filter(str.isdigit, telefone))
    
    # Montagem da mensagem formatada
    mensagem = f"🔔 *ALERTA SIGMA*\n\n👤 *Cliente:* {cliente}\n📝 *Evento:* {evento}"

    endpoint = f"{API_URL}/message/sendText/{INSTANCE_NAME}"
    headers = {"apikey": API_KEY, "Content-Type": "application/json"}
    payload = {"number": num_limpo, "text": mensagem}

    try:
        # Envia para o WhatsApp
        res = requests.post(endpoint, json=payload, headers=headers)
        
        # RESPOSTA CRÍTICA: Retornamos um JSON puríssimo para o seu controle.py não travar
        response = jsonify({"status": "sucesso", "cliente": cliente})
        response.headers.add('Content-Type', 'application/json')
        return response, 200
    except Exception as e:
        print(f"Erro interno: {str(e)}")
        return jsonify({"status": "erro"}), 500

@app.route('/')
def home():
    return "OK", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
