from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# --- CONFIGURAÇÕES ---
API_URL = "https://evolution-api-production-23a02.up.railway.app"
API_KEY = "03dfa2f521050f9d775d4893856245ef0444a9c57c676268e257166bbab09a35"
INSTANCE = "SigmaWhatsApp"

# Aceita tanto /enviar quanto /sigma_whats para não ter erro
@app.route('/enviar', methods=['POST', 'GET'])
@app.route('/sigma_whats', methods=['POST', 'GET'])
def disparar():
    # Pega os dados de onde vierem (URL ou Formulário)
    cliente = request.args.get('cliente') or request.form.get('cliente') or "Cliente Sigma"
    evento = request.args.get('desc') or request.form.get('desc') or "Alerta"
    telefone = request.args.get('tel') or request.form.get('tel') or "5521991334576"
    
    num_limpo = ''.join(filter(str.isdigit, telefone))
    mensagem = f"🔔 *ALERTA SIGMA*\n\n👤 *Cliente:* {cliente}\n📝 *Evento:* {evento}"

    try:
        # Envio para a Evolution API
        requests.post(
            f"{API_URL}/message/sendText/{INSTANCE}", 
            json={"number": num_limpo, "text": mensagem}, 
            headers={"apikey": API_KEY}, 
            timeout=5
        )
    except Exception as e:
        print(f"Erro no disparo: {e}")

    # Resposta rápida em JSON para o script local não travar
    return jsonify({"status": "ok", "recebido": cliente}), 200

@app.route('/')
def home():
    return "OK", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
