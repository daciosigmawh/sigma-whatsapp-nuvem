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
    # Remove tudo o que não for número
    num_limpo = re.sub(r'\D', '', str(numero))
    return num_limpo

@app.route('/', methods=['GET'])
def home():
    return "Servidor de Alertas Sigma Online", 200

@app.route('/enviar', methods=['POST'])
def receber_e_disparar():
    dados = request.get_json()
    
    if not dados:
        return jsonify({"error": "Nenhum dado recebido"}), 400

    # Extrai as tags enviadas pelo gateway local
    tel_original = dados.get('tel', '')
    cliente = dados.get('cliente', '')
    desc = dados.get('desc', '')
    nome_user = dados.get('nome_user', '')

    # TRATAMENTO E REGRA DO TELEFONE RESERVA
    numero_limpo = limpar_numero(tel_original)
    
    if not numero_limpo:
        # Se estiver vazio ou nulo, envia APENAS para o número reserva
        numero_destino = "5521991334576"
    else:
        # Se tiver número, garante o código do país (55)
        if not numero_limpo.startswith("55"):
            numero_destino = f"55{numero_limpo}"
        else:
            numero_destino = numero_limpo

    # MONTAGEM DA MENSAGEM COM O VISUAL IDENTICO AO PRINT
    mensagem_formatada = (
        "🔔 *ALERTA TELESEGURANÇA*\n\n"
        "👤 *Cliente:* {cliente}\n"
        "📝 *Evento:* {desc}\n"
        "🔑 *Usuário:* {nome_user}"
    ).format(cliente=cliente, desc=desc, nome_user=nome_user)

    # MONTA O PAYLOAD PARA A EVOLUTION API V2
    headers = {
        "apikey": API_KEY,
        "Content-Type": "application/json"
    }
    
    payload = {
        "number": numero_destino,
        "text": mensagem_formatada
    }

    try:
        # Envia para a instância do WhatsApp rodando na nuvem
        resposta = requests.post(EVOLUTION_URL, json=payload, headers=headers, timeout=10)
        
        if response.status_code in [200, 201]:
            print(f"✅ Alerta enviado com sucesso para {numero_destino}")
            return jsonify({"status": "sucesso", "destino": numero_destino}), 200
        else:
            print(f"❌ Erro na Evolution API: {resposta.status_code} - {resposta.text}")
            return jsonify({"status": "erro_api", "detalhes": resposta.text}), response.status_code

    except Exception as e:
        print(f"💥 Falha catastrófica ao conectar na Evolution: {e}")
        return jsonify({"status": "erro_conexao", "mensagem": str(e)}), 500

if __name__ == '__main__':
    # Roda na porta padrão do Render
    app.run(host='0.0.0.0', port=10000)
