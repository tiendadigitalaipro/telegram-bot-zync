#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A2K Digital Studio - Telegram Bot Start Script (Vendedor ZYNC)
Flask server to keep Render web service alive + bot runner with DeepSeek
v5: registro de mensajes de clientes (/mensajes) + bot auto-reparable
"""

import os
import time
import threading
import logging
import telebot
import requests
from flask import Flask, jsonify, request
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Configuración (Busca BOT_TOKEN que es como está en Render)
TELEGRAM_TOKEN = os.environ.get('BOT_TOKEN')
DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY')
NOTIF_KEY = os.environ.get('NOTIF_KEY', '')

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# --- REGISTRO DE MENSAJES DE CLIENTES (para la voz del laptop) ---
clientes_mensajes = []
msg_counter = [0]
BOT_THREAD = None

# --- FLASK (Para que Render no lo duerma) ---
app = Flask(__name__)

@app.route('/')
@app.route('/health')
def health():
    # Auto-reparacion: si el hilo del bot murio, lo revivimos al instante
    global BOT_THREAD
    bot_activo = bool(BOT_THREAD and BOT_THREAD.is_alive())
    if not bot_activo:
        try:
            logger.warning("Hilo del bot inactivo — reiniciando automaticamente...")
            iniciar_bot()
            bot_activo = True
        except Exception as e:
            logger.error(f"Fallo el reinicio del bot: {e}")
    return jsonify({"status": "ok", "service": "ZYNC Telegram Bot", "bot_activo": bot_activo}), 200

@app.route('/mensajes')
def mensajes():
    # Canal protegido: el laptop consulta aqui las preguntas nuevas de los clientes
    if not NOTIF_KEY or request.args.get('key') != NOTIF_KEY:
        return jsonify({"ok": False, "error": "no autorizado"}), 403
    after = request.args.get('after', 0, type=int)
    nuevos = [m for m in clientes_mensajes if m['id'] > after]
    return jsonify({
        "ok": True,
        "bot_activo": bool(BOT_THREAD and BOT_THREAD.is_alive()),
        "mensajes": nuevos
    })

def run_web():
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)

# --- CEREBRO DE DEEPSEEK (El mismo de WhatsApp) ---
SYSTEM_PROMPT = """Eres el vendedor estrella de ZYNC Electronics. Atiendes por Telegram.
- Amable, cercano y entusiasta. Usa emojis (1 a 3 por mensaje).
- Respuestas cortas (máximo 120 palabras).
- Regla de oro: Si el cliente dice que está caro, ofrécele llevar 2 productos para que el ENVÍO sea GRATIS. No bajes los precios.

CATÁLOGO OFICIAL (USA SOLO ESTOS PRECIOS):
- 💧 Filtro Purificador de Agua: $11.62
- 🪨 Cartucho de Repuesto: $6.07
- 🔪 Combo de 2 Peladores: $7.87
- 🎙️ Micrófono K9 One: $9.65
- 🎙️ Micrófonos K9 Duos (2 unids): $12.94
- 🎧 Audífonos Airmax: $12.96
- ⌚ Reloj i30 Ultra 3 MAX: $25.99

REGLAS DE ENVÍO Y ENTREGA:
1. El ENVÍO ES GRATIS solo a partir de 2 productos. Si compra 1 solo, cobra $5 de envío.
2. Hacemos ENTREGAS PERSONALES en Ocumare del Tuy. Si el cliente es de ahí, ofrécele entrega personal."""

conversations = {}
bot = telebot.TeleBot(TELEGRAM_TOKEN)

def ask_deepseek(chat_id, user_text):
    history = conversations.get(chat_id, [])
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + history + [{"role": "user", "content": user_text}]

    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek-chat",
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 300
    }

    try:
        res = requests.post("https://api.deepseek.com/v1/chat/completions", json=payload, headers=headers, timeout=45)
        if res.status_code == 200:
            answer = res.json()['choices'][0]['message']['content'].strip()
            history.append({"role": "user", "content": user_text})
            history.append({"role": "assistant", "content": answer})
            conversations[chat_id] = history[-16:]
            return answer
        return "😓 Tuve un problemita técnico. ¿Podrías repetirme tu mensaje, por favor? 🙏"
    except Exception as e:
        logger.error(f"Error DeepSeek: {e}")
        return "😓 Tuve un problemita técnico. ¿Podrías repetirme tu mensaje, por favor? 🙏"

# --- MANEJADORES DE MENSAJES ---
@bot.message_handler(commands=['start', 'hola'])
def send_welcome(message):
    bot.reply_to(message, "¡Hola! 👋 Bienvenido a *ZYNC Electronics*. Soy tu asistente virtual. ¿Qué producto te gustaría llevar hoy? 🛒\n\nRecuerda: *¡Lleva 2 productos y el envío es GRATIS!* 🚚", parse_mode='Markdown')

@bot.message_handler(content_types=['text'])
def handle_text(message):
    chat_id = message.chat.id
    text = message.text.strip()

    # Registrar la pregunta del cliente (para el altavoz del laptop)
    if not text.startswith('/'):
        msg_counter[0] += 1
        clientes_mensajes.append({
            "id": msg_counter[0],
            "usuario": (message.from_user.first_name or "Cliente")[:30],
            "texto": text[:500],
            "hora": datetime.now().strftime('%H:%M:%S')
        })
        del clientes_mensajes[:-100]  # conservar solo las ultimas 100

    bot.send_chat_action(chat_id, 'typing')
    answer = ask_deepseek(chat_id, text)
    bot.reply_to(message, answer, parse_mode='Markdown')

@bot.message_handler(content_types=['voice', 'audio'])
def handle_audio(message):
    bot.reply_to(message, "¡Hola! 😊 Por el momento no puedo escuchar notas de voz, pero si me escribes tu consulta por aquí te atenderé de inmediato. 🎁 ¡Recuerda que el ENVÍO es GRATIS si llevas 2 productos! 🚚")

def run_bot():
    logger.info("Iniciando Bot de Telegram ZYNC (Vendedor)...")
    while True:
        try:
            bot.infinity_polling(timeout=60, long_polling_timeout=60)
        except Exception as e:
            logger.error(f"El polling cayo, reiniciando en 5 segundos: {e}")
            time.sleep(5)

def iniciar_bot():
    global BOT_THREAD
    BOT_THREAD = threading.Thread(target=run_bot, daemon=True)
    BOT_THREAD.start()

if __name__ == '__main__':
    iniciar_bot()
    run_web()
