#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A2K Digital Studio - Telegram Bot Start Script (Vendedor ZYNC)
Flask server to keep Render web service alive + bot runner with DeepSeek
v5.1: registro de mensajes + ids con hora (fix lector de voz del laptop)
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
SYSTEM_PROMPT = """Eres "Kairo", el vendedor estrella senior de ZYNC Electronics en Telegram. Eres un profesional de ventas consultivo: educado, cercano, persuasivo y siempre honesto. Hablas español venezolano natural. Usas 1 a 3 emojis por mensaje y máximo 120 palabras.

TU MÉTODO DE VENTA (síguelo siempre, paso a paso):
1. ABRE la venta: saluda con calidez y haz UNA pregunta abierta para descubrir la necesidad ("¿qué andas buscando hoy?", "¿para quién es el regalo?").
2. DESCUBRE: pregunta para qué lo necesita o qué le gustaría lograr. Escucha ANTES de ofrecer.
3. PRESENTA beneficios, no características: conecta cada producto con lo que el cliente dijo ("para tus videos este micrófono te queda perfecto porque se escucha profesional").
4. CONVENCE con manejo de objeciones:
   - "Está caro" → NUNCA bajes el precio. Responde con valor: calidad importada, garantía y el ahorro real del ENVÍO GRATIS llevando 2 productos.
   - "Lo voy a pensar" → urgencia honesta: el stock vuela y los precios de importación suben; ofrece apartarlo ya.
   - "En otro lado es más barato" → barato sale caro: aquí tiene calidad garantizada y atención personalizada.
   - "Solo quiero información" → atiende con gusto y siempre sugiere el combo de 2 para envío gratis.
5. CIERRA asumiendo la compra: jamás preguntes "¿quieres comprar?". Pregunta "¿cómo prefieres pagar: Zelle, bolívares a tasa USDT o Binance?" o "¿lo enviamos hoy mismo?". Cada mensaje termina en una pregunta que avanza la venta.
6. POST-VENTA: confirma pedido, productos, total y envío; agradece e invita a recomprar.

REGLAS DE ORO:
- Usa SOLO los precios oficiales del catálogo. Nunca inventes precios ni productos.
- 2 productos o más = ENVÍO GRATIS. Si compra 1 solo producto, el envío va con COBRO A DESTINO (el cliente paga el flete al recibir, ~$5).
- Los bolívares se cobran a TASA USDT (P2P), jamás a tasa BCV.
- Entrega personal GRATIS en Ocumare del Tuy; menciónala si el cliente es de allá.
- El Cartucho de Repuesto y la Piedra Filtrante son repuestos del Filtro Purificador: ofrécelos como add-on a quien compre el filtro ("lleva también la piedra de repuesto y te quedas tranquilo un año").
- Si pide algo que no manejas o quiere hablar con una persona: asesor por WhatsApp wa.me/584164117331
- Preséntate siempre como ZYNC Electronics; nunca uses ni inventes otro nombre de tienda o firma.
- Nunca mientas sobre stock, tiempos ni garantías.

CATÁLOGO OFICIAL (USA SOLO ESTOS PRECIOS):
- 💧 Filtro Purificador de Agua: $11.62
- 🪨 Cartucho de Repuesto: $6.07
- ⚫ Piedra Filtrante (repuesto): $7.22
- 🔪 Combo de 2 Peladores: $7.87
- 🎙️ Micrófono K9 One: $9.65
- 🎙️ Micrófonos K9 Duos (2 unids): $12.94
- 🎧 Audífonos Airmax: $12.96
- ⌚ Reloj i30 Ultra 3 MAX: $25.99

MÉTODOS DE PAGO: Zelle, bolívares a tasa USDT, Binance (USDT/USDC), Zinli, Wally, Airtm, USDC, UgliCash, Belo, Mony, Mercantil Panamá, MyPal, Payoneer, Meru y transferencias Lead Bank (bancos de EE.UU.). Pide siempre comprobante."""

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
CATALOGO_TXT = (
    "🛒 *CATÁLOGO OFICIAL — ZYNC ELECTRONICS*\n\n"
    "💧 Filtro Purificador de Agua — $11.62\n"
    "🪨 Cartucho de Repuesto — $6.07\n"
    "⚫ Piedra Filtrante (repuesto) — $7.22\n"
    "🔪 Combo de 2 Peladores — $7.87\n"
    "🎙️ Micrófono K9 One — $9.65\n"
    "🎙️ Micrófonos K9 Duos (2 unids) — $12.94\n"
    "🎧 Audífonos Airmax — $12.96\n"
    "⌚ Reloj i30 Ultra 3 MAX — $25.99\n\n"
    "🚚 *¡Lleva 2 productos y el ENVÍO ES GRATIS!* (1 solo: cobro a destino)\n"
    "¿Cuál te gustaría apartar hoy? 😊"
)
ENVIOS_TXT = (
    "🚚 *ENVÍOS Y ENTREGAS*\n\n"
    "• *1 producto:* envío con *cobro a destino* (pagas el flete al recibir)\n"
    "• *2 o más productos:* ¡ENVÍO GRATIS! 🎉\n"
    "• *Ocumare del Tuy:* entrega personal GRATIS\n\n"
    "Enviamos a toda Venezuela por courier seguro. ¿De dónde eres? 😊"
)
PAGOS_TXT = (
    "💳 *MÉTODOS DE PAGO* — tenemos de todo:\n\n"
    "🇺🇸 Zelle\n"
    "💵 Binance (USDT / USDC)\n"
    "🇻🇪 Bolívares a *tasa USDT* (P2P)\n"
    "👛 Zinli · Wally · Belo · Mony\n"
    "🏦 Airtm · MyPal · Meru · Mercantil Panamá\n"
    "🌐 Payoneer · UgliCash\n"
    "🏛️ Transferencias Lead Bank (bancos de EE.UU.)\n\n"
    "¿Cuál te queda más fácil? Te paso los datos al momento 😊"
)
OFERTAS_TXT = (
    "🎁 *PROMOCIÓN ACTIVA*\n\n"
    "Llévate *2 productos o más* y el *ENVÍO ES GRATIS* 🚚✨\n\n"
    "Ejemplos que vuelan:\n"
    "💧 Filtro ($11.62) + ⚫ Piedra Filtrante ($7.22) = *$18.84 con envío gratis*\n"
    "🔪 Peladores ($7.87) + 🎙️ Micrófono K9 ($9.65) = *$17.52 con envío gratis*\n"
    "🎧 Airmax ($12.96) + 🎙️ K9 Duos ($12.94) = *$25.90 con envío gratis*\n\n"
    "¿Aprovechamos y apartas el tuyo hoy? 😊"
)
CONTACTO_TXT = (
    "👤 *ASESOR EN VIVO*\n\n"
    "Habla directo con nuestro equipo por WhatsApp:\n"
    "👉 https://wa.me/584164117331\n\n"
    "Te atendemos con gusto de inmediato. 🙌"
)

@bot.message_handler(commands=['start', 'hola'])
def send_welcome(message):
    nombre = ""
    if message.from_user and message.from_user.first_name:
        nombre = f" {message.from_user.first_name}"
    bot.reply_to(
        message,
        f"🚀 *¡Bienvenido a ZYNC Electronics{nombre}!*\n\n"
        "La tienda que trae la tecnología de USA y China directo a tu puerta en Venezuela 🇻🇪🛒\n\n"
        "🎧 Audífonos profesionales\n"
        "🎙️ Micrófonos para creadores\n"
        "⌚ Smartwatches y más\n\n"
        "*Todo original, con garantía y al mejor precio del mercado.*\n\n"
        "🎁 *HOY:* lleva *2 productos* y el *ENVÍO ES GRATIS*\n\n"
        "Dime: ¿qué estás buscando? Te lo consigo hoy mismo 😎\n\n"
        "_Tip: escribe /catalogo para ver todo con precios_",
        parse_mode='Markdown'
    )

@bot.message_handler(commands=['catalogo'])
def send_catalogo(message):
    bot.reply_to(message, CATALOGO_TXT, parse_mode='Markdown')

@bot.message_handler(commands=['precios'])
def send_precios(message):
    bot.reply_to(message, CATALOGO_TXT, parse_mode='Markdown')

@bot.message_handler(commands=['envios'])
def send_envios(message):
    bot.reply_to(message, ENVIOS_TXT, parse_mode='Markdown')

@bot.message_handler(commands=['pagos'])
def send_pagos(message):
    bot.reply_to(message, PAGOS_TXT, parse_mode='Markdown')

@bot.message_handler(commands=['ofertas'])
def send_ofertas(message):
    bot.reply_to(message, OFERTAS_TXT, parse_mode='Markdown')

@bot.message_handler(commands=['contacto'])
def send_contacto(message):
    bot.reply_to(message, CONTACTO_TXT, parse_mode='Markdown')

@bot.message_handler(content_types=['text'])
def handle_text(message):
    chat_id = message.chat.id
    text = message.text.strip()

    # Registrar la pregunta del cliente (para el altavoz del laptop)
    if not text.startswith('/'):
        # v5.1: id con hora en milisegundos — aunque Render se reinicie el id
        # nuevo siempre es mas grande, asi el lector de voz nunca pierde mensajes
        nuevo_id = int(time.time() * 1000)
        if nuevo_id <= msg_counter[0]:
            nuevo_id = msg_counter[0] + 1
        msg_counter[0] = nuevo_id
        clientes_mensajes.append({
            "id": nuevo_id,
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
