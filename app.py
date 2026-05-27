from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# CONFIGURAÇÕES DA SUA EVOLUTION API (CONFORME SEU SCRIPT LOCAL)
URL_API_NUVEM = "https://evolution-api-v1-8-2-1110.onrender.com"
API_KEY_GLOBAL = "03dfa2f521050f9d775d4893856245ef0444a9c57c676268e257166bbab09a35"
NOME_INSTANCIA = "shomer"

@app.route('/')
def home():
    return "Servidor de Tratamento de Alertas Online!", 200

@app.route('/enviar', methods=['POST'])
def tratar_e_enviar():
    dados = request.get_json()
    
    if not dados:
        return jsonify({"status": "erro", "mensagem": "Nenhum dado recebido"}), 400

    # Extrai as variáveis que vieram do seu script local
    telefone = dados.get('tel', '')
    cliente = dados.get('cliente', '')
    evento = dados.get('desc', '')
    nome_usuario = dados.get('nome_user', '')

    # Se não tiver telefone ou cliente, nem tenta enviar
    if not telefone or not cliente:
        return jsonify({"status": "erro", "mensagem": "Campos obrigatorios faltando"}), 400

    # Monta a mensagem exatamente igual ao print (com quebras de linha e negritos)
    mensagem_formatada = (
        "🔔 *ALERTA TELESEGURANÇA*\n\n"
        f"👤 *Cliente:* {cliente}\n"
        f"📝 *Evento:* {evento}\n"
        f"🔑 *Usuário:* {nome_usuario}"
    )

    # Prepara a requisição para a Evolution API v1.8.2 (Rota de envio de texto)
    url_evolution = f"{URL_API_NUVEM}/message/sendText/{NOME_INSTANCIA}"
    
    headers = {
        "Content-Type": "application/json",
        "apikey": API_KEY_GLOBAL
    }
    
    payload = {
        "number": telefone,
        "options": {
            "delay": 1200,
            "presence": "composing"
        },
        "textMessage": {
            "text": mensagem_formatada
        }
    }

    try:
        # Faz o disparo real para o WhatsApp via Evolution API
        resposta = requests.post(url_evolution, json=payload, headers=headers, timeout=20)
        
        if resposta.status_code in [200, 201]:
            return jsonify({"status": "sucesso", "detalhes": resposta.json()}), 200
        else:
            return jsonify({"status": "erro_api", "codigo": resposta.status_code, "resposta": resposta.text}), 400
            
    except Exception as e:
        return jsonify({"status": "erro_conexao", "detalhes": str(e)}), 500

if __name__ == '__main__':
    # O Render define a porta automaticamente pela variável de ambiente PORT
    import os
    porta = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=porta)
