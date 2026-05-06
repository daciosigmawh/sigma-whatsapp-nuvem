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
        return jsonify({"erro": "Nenhum dado recebido"}), 400

    # Pega os dados que o seu controle.py local enviou
    cliente = dados.get('cliente', 'Não informado')
    desc = dados.get('desc', 'Evento não identificado')
    id_user = str(dados.get('id_user', '')).strip()
    nome_user = dados.get('nome_user', '').strip()
    tel_destino = dados.get('tel') or "5521991334576"

    # --- LÓGICA DO USUÁRIO (O "Pulo do Gato") ---
    # Prioridade 1: Nome do usuário se existir no cadastro
    # Prioridade 2: ID da senha (ex: 02) se não tiver nome
    # Prioridade 3: Se for comando via app/software, indica "Sistema"
    
    usuario_final = "Sistema"
    
    if nome_user and nome_user != "Não identificado":
        usuario_final = nome_user
    elif id_user and id_user != "0":
        usuario_final = f"Senha {id_user}"
    elif "REMOTAMENTE" in desc.upper():
        usuario_final = "Comando Remoto"

    # Limpa o telefone para a Evolution API
    num_limpo = ''.join(filter(str.isdigit, str(tel_destino)))
    
    # MENSAGEM FORMATADA TELESEGURANÇA
    mensagem = (
        f"🔔 *ALERTA TELESEGURANÇA*\n\n"
        f"👤 *Cliente:* {cliente}\n"
        f"📝 *Evento:* {desc}\n"
        f"🔑 *Usuário:* {usuario_final}"
    )

    endpoint = f"{API_URL}/message/sendText/{INSTANCE_NAME}"
    headers = {"apikey": API_KEY, "Content-Type": "application/json"}
    payload = {"number": num_limpo, "text": mensagem}

    try:
        res = requests.post(endpoint, json=payload, headers=headers)
        return jsonify({"status": "sucesso", "api_code": res.status_code}), 200
    except Exception as e:
        return jsonify({"status": "erro", "detalhes": str(e)}), 500

@app.route('/')
def home():
    return "🚀 API TELESEGURANÇA ONLINE!", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
