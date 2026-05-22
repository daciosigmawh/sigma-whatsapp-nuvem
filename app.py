@app.route('/enviar', methods=['POST'])
def enviar():
    dados = request.get_json(silent=True)
    if not dados: return jsonify({"erro": "Sem dados"}), 400

    cliente = dados.get('cliente', 'Não informado')
    desc_bruta = dados.get('desc', 'Evento não identificado')
    id_user = str(dados.get('id_user', '')).strip()
    nome_user = dados.get('nome_user', '').strip()
    tel_destino = dados.get('tel') or "5521991334576"

    # --- LÓGICA DE LIMPEZA DO EVENTO ---
    # Se o nome do usuário estiver dentro da descrição, a gente remove
    evento_limpo = desc_bruta
    if nome_user and nome_user in desc_bruta:
        # Remove o nome e possíveis hifens ou espaços que sobram
        evento_limpo = desc_bruta.replace(nome_user, "").replace(" - ", "").strip()
    
    # --- LÓGICA DO USUÁRIO ---
    usuario_final = "Sistema"
    if nome_user and nome_user != "Não identificado":
        usuario_final = nome_user
    elif id_user and id_user != "0":
        usuario_final = f"Senha {id_user}"

    num_limpo = ''.join(filter(str.isdigit, str(tel_destino)))
    
    mensagem = (
        f"🔔 *ALERTA TELESEGURANÇA*\n\n"
        f"👤 *Cliente:* {cliente}\n"
        f"📝 *Evento:* {evento_limpo}\n"
        f"🔑 *Usuário:* {usuario_final}"
    )

    # ... restante do código de envio (endpoint, payload, requests...)
