from flask import Flask, request, jsonify
import urllib.parse
import requests
import os

app = Flask(__name__)

# Configurações da Evolution API que acabamos de colocar de pé no Neon
EVOLUTION_API_URL = "https://evolution-api-shomer.onrender.com"
EVOLUTION_API_KEY = "03dfa2f521050f9d775d4893856245ef0444a9c57c676268e257166bbab09a35"
# Substitua pelo nome da instância do WhatsApp que você criou na Evolution
INSTANCE_NAME = "shomer_sigma" 

@app.route('/', methods=['GET'])
def home():
    return "Servidor Shomer Centralizador Ativo na Nuvem!", 200

@app.route('/sigma_whats', methods=['GET', 'POST'])
def escuta_sigma_direto_na_nuvem():
    # Captura os parâmetros exatamente como o Sigma envia no webhook
    tel = request.args.get('tel', '')
    cliente = urllib.parse.unquote_plus(request.args.get('cliente', ''))
    desc = urllib.parse.unquote_plus(request.args.get('desc', ''))
    id_user = request.args.get('id_user', '')
    nome_user = urllib.parse.unquote_plus(request.args.get('nome_user', ''))
    data_hora = urllib.parse.unquote_plus(request.args.get('data', ''))

    if cliente or desc:
        print(f"\n🚀 EVENTO RECEBIDO DO SIGMA NA NUVEM: {cliente} - {desc}")
        
        # Monta o texto que vai pro WhatsApp do cliente
        mensagem_texto = f"⚠️ *Alerta Shomer* ⚠️\n\n*Cliente:* {cliente}\n*Evento:* {desc}\n*Usuário:* {nome_user} (ID: {id_user})\n*Data/Hora:* {data_hora}"
        
        # Prepara o disparo para a Evolution API
        url_disparo = f"{EVOLUTION_API_URL}/message/sendText/{INSTANCE_NAME}"
        headers = {
            "Content-Type": "application/json",
            "apikey": EVOLUTION_API_KEY
        }
        payload = {
            "number": tel,
            "options": {
                "delay": 1200,
                "presence": "composing",
                "linkPreview": False
            },
            "textMessage": {
                "text": str(mensagem_texto)
            }
        }
        
        try:
            # Faz o envio real pro WhatsApp através da nossa Evolution na nuvem
            resposta = requests.post(url_disparo, json=payload, headers=headers)
            print(f"📡 Repassado para Evolution API: Status {resposta.status_code}")
        except Exception as e:
            print(f"❌ Erro ao conectar na Evolution API: {e}")
            
        return "PROCESSADO NA NUVEM", 200
    
    return "OK", 200

if __name__ == '__main__':
    porta = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=porta)
