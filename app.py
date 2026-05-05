from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# --- CONFIGURAÇÕES FIXAS ---
API_URL = "https://evolution-api-production-23a02.up.railway.app"
API_KEY = "03dfa2f521050f9d775d4893856245ef0444a9c57c676268e257166bbab09a35"
INSTANCE_NAME = "SigmaWhatsApp"

@app.route('/sigma_whats', methods=['POST', 'GET'])
def sigma_whats():
    # 1. Captura IMEDIATA dos dados da URL
    cliente = request.args.get('cliente', 'Cliente Sigma')
    evento = request.args.get('desc', 'Evento detectado')
    telefone = request.args.get('tel', '5521991334576')
    
    # 2. Limpeza do número
    num_limpo = ''.join(filter(str.isdigit, telefone))
    mensagem = f"🔔 *ALERTA SIGMA*\n\n👤 *Cliente:* {cliente}\n📝 *Evento:* {evento}"

    # 3. Preparação do disparo
    payload = {"number": num_limpo, "text": mensagem}
    headers = {"apikey": API_KEY, "Content-Type": "application/json"}

    try:
        # Enviamos para a API com um timeout curto para não travar seu PC
        requests.post(f"{API_URL}/message/sendText/{INSTANCE_NAME}", 
                      json=payload, headers=headers, timeout=2)
    except Exception as e:
        print(f"Log de envio: {e}")

    # 4. RESPOSTA FLASH (Isso aqui impede o erro no seu PowerShell)
    return jsonify({"status": "recebido", "cliente": cliente}), 200

@app.route('/')
def home():
    return "OK", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
