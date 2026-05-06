from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# --- CONFIGURAÇÕES ---
API_URL = "https://evolution-api-production-23a02.up.railway.app"
API_KEY = "03dfa2f521050f9d775d4893856245ef0444a9c57c676268e257166bbab09a35"
INSTANCE_NAME = "SigmaWhatsApp" 

@app.route('/enviar', methods=['POST'])
def enviar():
    dados = request.get_json(silent=True)
    if not dados:
        return jsonify({"erro": "Sem dados"}), 400

    cliente = dados.get('cliente', 'Cliente não identificado')
    desc_bruta = dados.get('desc', 'Evento não identificado')
    quem_bruto = dados.get('quem', '').strip()
    tel_destino = dados.get('tel') or "5521991334576"

    # Lógica para desembolar Usuário e Evento
    # Se o evento contiver "POR" ou "USUÁRIO", tentamos separar as informações
    evento = desc_bruta
    usuario = quem_bruto if quem_bruto and quem_bruto != "Não identificado" else "Não identificado"

    if " - " in desc_bruta:
        partes = desc_bruta.split(" - ", 1)
        evento = partes[0]
        if usuario == "Não identificado":
            usuario = partes[1]
    elif " PELO USUÁRIO - " in desc_bruta:
        partes = desc_bruta.split(" PELO USUÁRIO - ", 1)
        evento = partes[0]
        if usuario == "Não identificado":
            usuario = partes[1]

    num_limpo = ''.join(filter(str.isdigit, str(tel_destino)))
    
    # Mensagem formatada e organizada
    mensagem = (
        f"🔔 *ALERTA SIGMA*\n\n"
        f"👤 *Cliente:* {cliente}\n"
        f"📝 *Evento:* {evento}\n"
        f"🔑 *Usuário:* {usuario}"
    )

    endpoint = f"{API_URL}/message/sendText/{INSTANCE_NAME}"
    headers = {"apikey": API_KEY, "Content-Type": "application/json"}
    payload = {"number": num_limpo, "text": mensagem}

    try:
        res = requests.post(endpoint, json=payload, headers=headers)
        return jsonify({"status": "sucesso"}), 200
    except Exception as e:
        return jsonify({"status": "erro", "detalhes": str(e)}), 500

@app.route('/')
def home():
    return "🚀 Servidor Sigma Online!", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
