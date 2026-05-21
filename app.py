from flask import Flask, request, jsonify
import urllib.parse
import requests
import os

app = Flask(__name__)

# --- CONFIGURAÇÕES ---
# O os.environ.get tenta ler o painel do Render. Se não achar nada, usa o padrão antigo.
API_URL = os.environ.get("EVOLUTION_URL", "https://evolution-api-production-23a02.up.railway.app")
API_KEY = os.environ.get("EVOLUTION_KEY", "03dfa2f521050f9d775d4893856245ef0444a9c57c676268e257166bbab09a35")
INSTANCE_NAME = os.environ.get("INSTANCE_NAME", "SigmaWhatsApp")

@app.route('/', methods=['GET'])
def home():
    return "Servidor Shomer Sigma-WhatsApp Integrado e Ativo!", 200

# 1. A ROTA QUE RECEBE OS ALARMES DO SIGMA (Trazida do seu PC para o Render)
@app.route('/sigma_whats', methods=['GET', 'POST'])
def escuta_sigma():
    tel = request.args.get('tel', '')
    cliente = urllib.parse.unquote_plus(request.args.get('cliente', ''))
    desc = urllib.parse.unquote_plus(request.args.get('desc', ''))
    id_user = request.args.get('id_user', '')
    nome_user = urllib.parse.unquote_plus(request.args.get('nome_user', ''))
    data_hora = urllib.parse.unquote_plus(request.args.get('data', ''))

    if cliente or desc:
        print(f"\n🚀 EVENTO RECEBIDO DO SIGMA NA NUVEM: {cliente} - {desc}")
        
        # Monta o pacote estruturado idêntico ao que o seu PC gerava
        pacote = {
            "tel": tel,
            "cliente": cliente,
            "desc": desc,
            "id_user": id_user,
            "nome_user": nome_user,
            "data": data_hora
        }

        # Executa o envio para o WhatsApp chamando a lógica localmente
        resultado, status_code = disparar_whatsapp(pacote)
        
        if resultado:
            print(f"✅ DISPARO EXECUTADO VIA EVOLUTION: {status_code}")
            return "PROCESSADO COM SUCESSO", 200
        else:
            print(f"❌ FALHA NO DISPARO DA EVOLUTION: {status_code}")
            return "ERRO NO DISPARO", 500
            
    return "OK", 200

# 2. A ROTA DE ENVIO DIRETO (Mantida para compatibilidade)
@app.route('/enviar', methods=['POST'])
def enviar():
    dados = request.get_json(silent=True)
    if not dados:
        return jsonify({"erro": "Nenhum dado recebido"}), 400
        
    resultado, status_code = disparar_whatsapp(dados)
    if resultado:
        return jsonify({"status": "sucesso", "codigo": status_code}), 200
    else:
        return jsonify({"status": "erro", "detalhe": status_code}), 500

# FUNÇÃO AUXILIAR QUE FAZ A PONTE COM A EVOLUTION API
def disparar_whatsapp(dados):
    url = f"{API_URL}/message/sendText/{INSTANCE_NAME}"
    headers = {
        "Content-Type": "application/json",
        "apikey": API_KEY
    }
    
    # Formatação da mensagem estruturada que vai para o WhatsApp
    texto_mensagem = f"🚨 *Alerta de Evento Sigma*\n\n🏢 *Cliente:* {dados.get('cliente')}\n📝 *Descrição:* {dados.get('desc')}\n👤 *Usuário:* {dados.get('nome_user')} (ID: {dados.get('id_user')})\n📅 *Data/Hora:* {dados.get('data')}"
    
    payload = {
        "number": dados.get("tel"),
        "options": {
            "delay": 1200,
            "presence": "composing"
        },
        "textMessage": {
            "text": texto_mensagem
        }
    }
    
    try:
        res = requests.post(url, json=payload, headers=headers, timeout=12)
        return res.status_code in [200, 201], res.status_code
    except Exception as e:
        return False, str(e)

if __name__ == '__main__':
    # O Render injeta a porta correta na variável PORT
    porta = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=porta)
