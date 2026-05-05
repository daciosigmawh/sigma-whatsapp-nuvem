from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# --- CONFIGURAÇÕES ---
API_URL = "https://evolution-api-production-23a02.up.railway.app"
API_KEY = "03dfa2f521050f9d775d4893856245ef0444a9c57c676268e257166bbab09a35"
INSTANCE_NAME = "SigmaWhatsApp" 

@app.route('/enviar', methods=['POST'])
def enviar():
    # Captura o JSON 'pacote' que vem do seu controle.py
    dados = request.get_json(silent=True)
    
    if not dados:
        return jsonify({"erro": "Nenhum dado recebido"}), 400

    # Pega as informações exatamente com os nomes que estão no seu script local
    cliente = dados.get('cliente', 'Cliente não identificado')
    desc = dados.get('desc', 'Sem descrição')
    quem = dados.get('quem', 'Não informado')
    tel_destino = dados.get('tel') or "5521991334576"

    # Limpa o telefone
    num_limpo = ''.join(filter(str.isdigit, str(tel_destino)))
    
    # Formata a mensagem com o "Quem" (quem armou/desarmou) para ficar mais completo
    mensagem = f"🔔 *ALERTA SIGMA*\n\n👤 *Cliente:* {cliente}\n📝 *Evento:* {desc}\n🔑 *Usuário:* {quem}"

    # Disparo para a API Evolution
    endpoint = f"{API_URL}/message/sendText/{INSTANCE_NAME}"
    headers = {"apikey": API_KEY, "Content-Type": "application/json"}
    payload = {"number": num_limpo, "text": mensagem}

    try:
        res = requests.post(endpoint, json=payload, headers=headers)
        return jsonify({"status": "sucesso", "whatsapp": res.status_code}), 200
    except Exception as e:
        return jsonify({"status": "erro", "detalhes": str(e)}), 500

@app.route('/')
def home():
    return "🚀 Servidor Sigma Online!", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
