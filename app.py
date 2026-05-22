from flask import Flask, request, jsonify
import requests
import re

app = Flask(__name__)

# CONFIGURAÇÕES DA EVOLUTION API V2 NO RENDER
EVOLUTION_URL = "https://evolution-api-shomer.onrender.com/message/sendText/shomer"
API_KEY = "03dfa2f521050f9d775d4893856245ef0444a9c57c676268e257166bbab09a35"

def limpar_numero(numero):
    if not numero:
        return ""
    return re.sub(r'\D', '', str(numero))

@app.route('/', methods=['GET'])
def home():
    return "Servidor de Alertas Sigma Online", 200

@app.route('/enviar', methods=['POST'])
def receber_e_disparar():
    dados = request.get_json()
    
    if not dados:
        return jsonify({"error": "Nenhum dado recebido"}), 400

    # Extrai exatamente as chaves que o teu controle.py envia
    tel_original = dados.get('tel', '')
    cliente = dados.get('cliente', '')
    desc = dados.get('desc', '')
    nome_user = dados.get('nome_user', '')
    data_hora = dados.get('data', '')

    # TRATAMENTO E REGRA DO TELEFONE RESERVA
    numero_limpo = limpar_numero(tel_original)
    
    if not numero_limpo:
        numero_destino = "5521991334576"
    else:
        if not numero_limpo.startswith("55"):
            numero_destino = f"55{numero_limpo}"
        else:
            numero_destino = numero_limpo

    # MONTAGEM DA MENSAGEM IGUALZINHA AO TEU PRINT
    mensagem_formatada = (
        "🔔 *ALERTA TELESEGURANÇA*\n\n"
        "👤 *Cliente:* {cliente}\n"
        "📝 *Evento:* {desc}\n"
        "🔑 *Usuário:* {nome_user}\n"
        "📅 *Data/Hora:* {data}"
    ).format(cliente=cliente, desc=desc, nome_user=nome_user, data=data_hora)

    # ENVIO PARA A EVOLUTION
    headers = {
        "apikey": API_KEY,
        "Content-Type": "application/json"
    }
    
    payload = {
        "number": numero_destino,
        "text": mensagem_formatada
    }

    try:
        resposta = requests.post(EVOLUTION_URL, json=payload, headers=headers, timeout=10)
        
        if resposta.status_code in [200, 201]:
            print(f"✅ Alerta enviado para {numero_destino}")
            return jsonify({"status": "sucesso", "destino": numero_destino}), 200
        else:
            print(f"❌ Erro na Evolution API: {resposta.status_code} - {resposta.text}")
            return jsonify({"status": "erro_api", "detalhes": resposta.text}), resposta.status_code

    except Exception as e:
        print(f"💥 Falha ao conectar na Evolution: {e}")
        return jsonify({"status": "erro_conexao", "mensagem": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
