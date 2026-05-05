from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# --- CONFIGURAÇÕES FIXAS ---
API_URL = "https://evolution-api-production-23a02.up.railway.app"
API_KEY = "03dfa2f521050f9d775d4893856245ef0444a9c57c676268e257166bbab09a35"
INSTANCE = "SigmaWhatsApp"

# Aceita todas as rotas que seu script local tentou usar
@app.route('/sigma_whats', methods=['POST', 'GET'])
@app.route('/enviar', methods=['POST', 'GET'])
def disparar():
    # Captura os dados exatamente como aparecem no seu PowerShell
    cliente = request.args.get('cliente', 'Cliente Sigma')
    evento = request.args.get('desc', 'Alerta de Evento')
    telefone = request.args.get('tel', '5521991334576')
    
    num_limpo = ''.join(filter(str.isdigit, telefone))
    mensagem = f"🔔 *ALERTA SIGMA*\n\n👤 *Cliente:* {cliente}\n📝 *Evento:* {evento}"

    try:
        # Envio para a Evolution API com timeout curto para liberar seu PC rápido
        requests.post(
            f"{API_URL}/message/sendText/{INSTANCE}", 
            json={"number": num_limpo, "text": mensagem}, 
            headers={"apikey": API_KEY}, 
            timeout=2
        )
    except:
        pass # Ignora erros de envio para garantir a resposta ao seu PC

    # RESPOSTA CRÍTICA: JSON puríssimo para evitar o erro de 'char 0' no seu PC
    return jsonify({"status": "sucesso", "recebido": cliente}), 200

@app.route('/')
def home():
    return "OK", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
