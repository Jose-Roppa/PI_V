from flask import Flask, request
import json
from zapi import send_message, send_image, send_group_message
from gemini_api import ask_gemini
from sessions import set_human_attending, is_human_attending
from config import GROUP_ID, ESTABELECIMENTO_INFO

app = Flask(__name__)

CONFIG_FILE = 'lojas_config.json'

# Utilitário para carregar configurações das lojas
def load_config():
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    connected_phone = data.get('connectedPhone')
    cliente_phone = data.get('phone')
    message = data.get('message', '').lower()
    config = load_config()
    loja = next((l for l in config['lojas'] if l['connected_phone'] == connected_phone), None)
    if not loja:
        return 'Loja não encontrada', 404

    # Exemplo: enviar mensagem para o grupo de avisos da loja correta
    # send_group_message(loja['zapi_url'], loja['grupo_aviso'], f"Mensagem de teste para o grupo da loja {loja['nome']}")

    # Exemplo de lógica adaptável por tipo de loja
    if loja['tipo'] == 'restaurante':
        if 'reserva' in message or 'reservar' in message:
            send_group_message(loja['zapi_url'], loja['grupo_aviso'], f"Cliente {cliente_phone} deseja fazer uma reserva: '{message}'")
            send_message(loja['zapi_url'], cliente_phone, "Vou pedir para um atendente humano finalizar sua reserva. Aguarde um momento, por favor!")
            return 'Reserva encaminhada', 200
        if 'cardápio' in message or 'menu' in message:
            if loja.get('menu_img'):
                send_image(loja['zapi_url'], cliente_phone, f"static/{loja['menu_img']}", "Aqui está nosso cardápio digital!")
            else:
                send_message(loja['zapi_url'], cliente_phone, "Nosso cardápio: " + ', '.join(loja['menu']))
            return 'Cardápio enviado', 200
        # Outras lógicas de restaurante...
    elif loja['tipo'] == 'boutique':
        if 'catálogo' in message or 'produto' in message:
            if loja.get('menu_img'):
                send_image(loja['zapi_url'], cliente_phone, f"static/{loja['menu_img']}", "Aqui está nosso catálogo digital!")
            else:
                send_message(loja['zapi_url'], cliente_phone, "Nosso catálogo: " + ', '.join(loja['menu']))
            return 'Catálogo enviado', 200
        # Outras lógicas de boutique...

    # Resposta padrão
    send_message(loja['zapi_url'], cliente_phone, f"Olá! Você está falando com o assistente da loja {loja['nome']}. Como posso ajudar?")
    return 'Respondido', 200

if __name__ == '__main__':
    app.run(port=5000) 