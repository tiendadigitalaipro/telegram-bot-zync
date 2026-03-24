import telebot
from telebot import types
import json
from datetime import datetime

# ==================== CONFIGURACIÓN ====================

BOT_TOKEN = '8351227479:AAG66TOA8LosFHwmKwPsC3wZA0Tn8v_HhB0'
bot = telebot.TeleBot(BOT_TOKEN)

# Estados de usuarios
user_states = {}

# ==================== PRODUCTOS ====================

ZYNC = [
    {
        'id': 1,
        'nombre': '🎧 Headphones K9',
        'precio': 15,
        'desc': 'Audio HD inalámbrico con graves profundos. Batería de 20 horas. Cancelación de ruido.'
    },
    {
        'id': 2,
        'nombre': '⌚ Smartwatch Inteligente',
        'precio': 25,
        'desc': 'Monitor de salud 24/7: ritmo cardíaco, oxígeno, presión. GPS. Notificaciones. Batería 7 días.'
    },
    {
        'id': 3,
        'nombre': '🎤 Micrófono K9 Pro',
        'precio': 15,
        'desc': 'Calidad profesional. Perfecto para streaming, gaming, podcasts. Plug & Play.'
    }
]

AMAZON_ES = {
    'tech': [
        {'nombre': '💨 Limpiador Aire PC', 'link': 'https://amzn.to/4cCQkHF'},
        {'nombre': '📱 Catálogo Tecnología', 'link': 'https://amzn.to/4kMFBwp'}
    ],
    'belleza': [
        {'nombre': '💇 Cepillo Secador', 'link': 'https://amzn.to/4cE3e8b'},
        {'nombre': '🌡️ Cepillo Aire Caliente', 'link': 'https://amzn.to/4kMqROb'}
    ],
    'hogar': [
        {'nombre': '🌟 Proyector Astronauta', 'link': 'https://amzn.to/3OnMw2Z'},
        {'nombre': '📹 Cámara Seguridad 360°', 'link': 'https://amzn.to/3MVT1D5'}
    ],
    'fitness': [
        {'nombre': '💪 Pistola Masajes RENPHO', 'link': 'https://amzn.to/4b27qOi'},
        {'nombre': '💧 Botella Motivacional 1L', 'link': 'https://amzn.to/4s3aVtk'}
    ]
}

AMAZON_USA = {
    'tech': [
        {'nombre': '📱 Gimbal COMITOK', 'link': 'https://amzn.to/3ZOIX8w'},
        {'nombre': '🔋 CyberPower Sistema', 'link': 'https://amzn.to/4b7pyFd'}
    ],
    'hogar': [
        {'nombre': '💧 Filtro Brita Cromado', 'link': 'https://amzn.to/40kesHG'},
        {'nombre': '💨 Ventilador Techo', 'link': 'https://amzn.to/3MH9Ec8'}
    ],
    'fitness': [
        {'nombre': '💆 Almohadilla Lifepro', 'link': 'https://amzn.to/4tMXT4H'},
        {'nombre': '🏃 Walking Pad', 'link': 'https://amzn.to/4aLiGNx'}
    ],
    'cocina': [
        {'nombre': '🔪 Fullstar Picador', 'link': 'https://amzn.to/40kFa2T'}
    ],
    'belleza': [
        {'nombre': '💄 Limpiador Brochas', 'link': 'https://amzn.to/4awV5kE'}
    ]
}

ALIEXPRESS = [
    {'nombre': '📽️ Proyector 4K', 'link': 'https://s.click.aliexpress.com/e/_c3IG0O6R'},
    {'nombre': '🎧 Lenovo GM2 Pro', 'link': 'https://s.click.aliexpress.com/e/_c3VeH5PH'},
    {'nombre': '🎮 Game Stick Retro', 'link': 'https://s.click.aliexpress.com/e/_c4461eEX'},
    {'nombre': '🎮 Consola Retro M8', 'link': 'https://s.click.aliexpress.com/e/_c3QeEMWn'}
]

# ==================== BANCOS ====================

BANCOS_NAC = [
    {'n': 'Mercantil', 'c': '0105-0191-1981-9100-5433', 't': 'Abigail Jose Rojas', 'ci': 'V-11558392'},
    {'n': 'Provincial', 'c': '0108-0134-6101-0008-0442', 't': 'Abigail Jose Rojas', 'ci': 'V-11558392'},
    {'n': 'Venezuela', 'c': '0102-0456-9500-0001-9004', 't': 'Abigail Rojas', 'ci': 'V-11558392'},
    {'n': 'Banesco', 'c': '0134-0059-8105-9304-0991', 't': 'Abigail Jose Rojas', 'ci': 'V-11558392'},
    {'n': 'Tesoro Personal', 'c': '0163-0209-1020-9500-6416', 't': 'Abigail Jose Rojas', 'ci': 'V-11558392'},
    {'n': 'Tesoro Jurídica', 'c': '0163-0209-1120-9300-9911', 't': 'Inversiones 2k 3112 C.A', 'ci': 'J-40632338-1'},
    {'n': 'BDT', 'c': '0175-0525-4000-7219-9833', 't': 'Abigail Jose Rojas', 'ci': 'V-11558392'},
    {'n': 'Exterior', 'c': '0115-0034-0110-0617-7575', 't': 'Abigail Jose Rojas', 'ci': 'V-11558392'},
    {'n': 'R4', 'c': '0169-0001-0110-0146-4751', 't': 'Abigail Jose Rojas', 'ci': 'V-11558392'}
]

BANCOS_INT = [
    {'n': 'Zinli', 'd': 'abijose1158@gmail.com'},
    {'n': 'Wally Tech', 'd': '+584126148666'},
    {'n': 'Payoneer', 'd': 'inversiones2k3112@hotmail.com'},
    {'n': 'Binance', 'd': 'abijose1158@hotmail.com'},
    {'n': 'Global66', 'd': 'ABIROJ4'},
    {'n': 'Facebank', 'd': '56110079352', 'routing': '021502189'},
    {'n': 'Pipol Pay', 'd': 'servirefri2k@gmail.com'},
    {'n': 'Citibank', 'd': '70588270001777164', 'aba': '031100209', 'swift': 'CITIUS33'},
    {'n': 'Mercantil Panamá', 'd': '639897225'},
    {'n': 'Barking Circles', 'iban': 'LU194080000056238058', 'bic': 'BICIRLULL'}
]

# ==================== COMANDOS ====================

@bot.message_handler(commands=['start', 'menu'])
def send_welcome(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton('🎧 ZYNC Local', callback_data='zync')
    btn2 = types.InlineKeyboardButton('🇪🇸 Amazon España', callback_data='amazon_es')
    btn3 = types.InlineKeyboardButton('🇺🇸 Amazon USA', callback_data='amazon_usa')
    btn4 = types.InlineKeyboardButton('🇨🇳 AliExpress', callback_data='aliexpress')
    btn5 = types.InlineKeyboardButton('💳 Métodos de Pago', callback_data='pagos')
    btn6 = types.InlineKeyboardButton('🔥⭐ BODEGA PRO v2.0 ⭐🔥', callback_data='bodega')
    btn7 = types.InlineKeyboardButton('👤 Contacto Ingeniero', url='https://wa.me/584164117331')
    
    markup.add(btn1, btn2, btn3, btn4, btn5)
    markup.add(btn6)
    markup.add(btn7)
    
    bot.send_message(
        message.chat.id,
        "🚀 *¡Bienvenido a ZYNC Electronics!*\n\n"
        "Somos tu tienda de confianza en tecnología de calidad para los Valles del Tuy.\n\n"
        "📦 *Selecciona una opción:*",
        parse_mode='Markdown',
        reply_markup=markup
    )

@bot.message_handler(commands=['bodegapro'])
def bodega_pro_info(message):
    show_bodega_pro(message.chat.id)

# ==================== MANEJO DE MENSAJES DE TEXTO ====================

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    # Respuesta por defecto
    bot.send_message(message.chat.id, "Escribe /start para ver el menú 🚀")

# ==================== CALLBACKS ====================

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    
    # ZYNC LOCAL
    if call.data == 'zync':
        markup = types.InlineKeyboardMarkup(row_width=1)
        for p in ZYNC:
            btn = types.InlineKeyboardButton(
                f"{p['nombre']} - ${p['precio']}",
                callback_data=f"producto_{p['id']}"
            )
            markup.add(btn)
        markup.add(types.InlineKeyboardButton('🔙 Volver', callback_data='menu'))
        
        bot.edit_message_text(
            "🎧 *CATÁLOGO ZYNC ELECTRONICS*\n\n"
            "Tecnología de calidad para los Valles del Tuy\n\n"
            "🚚 Envío GRATIS en Ocumare\n"
            "📦 Entrega 24-48 horas\n"
            "✅ Garantía de calidad",
            chat_id,
            call.message.message_id,
            parse_mode='Markdown',
            reply_markup=markup
        )
    
    # PRODUCTO ESPECÍFICO
    elif call.data.startswith('producto_'):
        pid = int(call.data.split('_')[1])
        p = next((x for x in ZYNC if x['id'] == pid), None)
        if p:
            markup = types.InlineKeyboardMarkup()
            markup.add(
                types.InlineKeyboardButton('💬 Comprar por WhatsApp', url='https://wa.me/584164117331'),
                types.InlineKeyboardButton('🔙 Volver', callback_data='zync')
            )
            bot.edit_message_text(
                f"✨ *{p['nombre']}*\n\n"
                f"{p['desc']}\n\n"
                f"💰 Precio: ${p['precio']} USD\n\n"
                f"🚚 Envío GRATIS en Ocumare del Tuy\n"
                f"📦 Entrega 24-48 horas\n"
                f"✅ Garantía de satisfacción",
                chat_id,
                call.message.message_id,
                parse_mode='Markdown',
                reply_markup=markup
            )
    
    # AMAZON ESPAÑA
    elif call.data == 'amazon_es':
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton('📱 Tecnología', callback_data='aes_tech'),
            types.InlineKeyboardButton('💄 Belleza', callback_data='aes_belleza'),
            types.InlineKeyboardButton('🏠 Hogar', callback_data='aes_hogar'),
            types.InlineKeyboardButton('💪 Fitness', callback_data='aes_fitness'),
            types.InlineKeyboardButton('🔙 Volver', callback_data='menu')
        )
        bot.edit_message_text(
            "🇪🇸 *AMAZON ESPAÑA*\n\nSelecciona una categoría:",
            chat_id,
            call.message.message_id,
            parse_mode='Markdown',
            reply_markup=markup
        )
    
    elif call.data.startswith('aes_'):
        cat = call.data.split('_')[1]
        productos = AMAZON_ES.get(cat, [])
        texto = f"🇪🇸 *PRODUCTOS DISPONIBLES*\n\n"
        for p in productos:
            texto += f"{p['nombre']}\n{p['link']}\n\n"
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('🔙 Volver', callback_data='amazon_es'))
        bot.edit_message_text(texto, chat_id, call.message.message_id, parse_mode='Markdown', reply_markup=markup)
    
    # AMAZON USA
    elif call.data == 'amazon_usa':
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton('📱 Tech', callback_data='aus_tech'),
            types.InlineKeyboardButton('🏠 Hogar', callback_data='aus_hogar'),
            types.InlineKeyboardButton('💪 Fitness', callback_data='aus_fitness'),
            types.InlineKeyboardButton('🍽️ Cocina', callback_data='aus_cocina'),
            types.InlineKeyboardButton('💄 Belleza', callback_data='aus_belleza'),
            types.InlineKeyboardButton('🔙 Volver', callback_data='menu')
        )
        bot.edit_message_text(
            "🇺🇸 *AMAZON USA*\n\nSelecciona una categoría:",
            chat_id,
            call.message.message_id,
            parse_mode='Markdown',
            reply_markup=markup
        )
    
    elif call.data.startswith('aus_'):
        cat = call.data.split('_')[1]
        productos = AMAZON_USA.get(cat, [])
        texto = f"🇺🇸 *PRODUCTOS DISPONIBLES*\n\n"
        for p in productos:
            texto += f"{p['nombre']}\n{p['link']}\n\n"
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('🔙 Volver', callback_data='amazon_usa'))
        bot.edit_message_text(texto, chat_id, call.message.message_id, parse_mode='Markdown', reply_markup=markup)
    
    # ALIEXPRESS
    elif call.data == 'aliexpress':
        texto = "🇨🇳 *ALIEXPRESS*\n\n"
        for p in ALIEXPRESS:
            texto += f"{p['nombre']}\n{p['link']}\n\n"
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('🔙 Volver', callback_data='menu'))
        bot.edit_message_text(texto, chat_id, call.message.message_id, parse_mode='Markdown', reply_markup=markup)
    
    # MÉTODOS DE PAGO
    elif call.data == 'pagos':
        texto = "💳 *MÉTODOS DE PAGO DISPONIBLES*\n\n"
        texto += "*🏦 NACIONALES (Bs):*\n"
        for b in BANCOS_NAC:
            texto += f"• {b['n']}\n"
        texto += "\n*💵 INTERNACIONALES (USD):*\n"
        for b in BANCOS_INT:
            texto += f"• {b['n']}\n"
        texto += "\nContacta por WhatsApp para datos completos 👇"
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton('💬 WhatsApp', url='https://wa.me/584164117331'),
            types.InlineKeyboardButton('🔙 Volver', callback_data='menu')
        )
        bot.edit_message_text(texto, chat_id, call.message.message_id, parse_mode='Markdown', reply_markup=markup)
    
    # BODEGA PRO
    elif call.data == 'bodega':
        show_bodega_pro(chat_id, call.message.message_id)
    
    elif call.data == 'bodega_info':
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton('🎥 Solicitar Demo', callback_data='bodega_demo'),
            types.InlineKeyboardButton('💎 Comprar Ahora', url='https://wa.me/584164117331?text=Quiero%20comprar%20BODEGA%20PRO'),
            types.InlineKeyboardButton('🔙 Volver', callback_data='bodega')
        )
        bot.edit_message_text(
            "💎 *BODEGA PRO v2.0 - INFO COMPLETA*\n\n"
            "🎯 *Para quién es:*\n"
            "Bodegas, Abastos, Tecnología, Farmacias, Ferreterías, Repuestos\n\n"
            "💰 *Precio: $25 USD*\n"
            "✅ Un solo pago\n"
            "✅ Plan PREMIUM\n"
            "✅ Actualizaciones gratis\n"
            "✅ Soporte incluido\n\n"
            "📱 *Entrega:* Directa por WhatsApp\n"
            "🎥 *Demo:* Video llamada en vivo\n"
            "🚀 *Sin internet. Sin mensualidades.*",
            chat_id,
            call.message.message_id,
            parse_mode='Markdown',
            reply_markup=markup
        )
    
    elif call.data == 'bodega_demo':
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton('📋 Llenar Formulario', url='https://tiendadigitalaipro.github.io/bodega-demo/formulario-demo-bodega.html'),
            types.InlineKeyboardButton('📱 Ver Info Completa', url='https://tiendadigitalaipro.github.io/bodega-demo/bodega-pro-descarga.html'),
            types.InlineKeyboardButton('🔙 Volver', callback_data='bodega')
        )
        bot.edit_message_text(
            "🎥 *DEMO GRATIS 5 DÍAS - BODEGA PRO*\n\n"
            "Para solicitar tu demo:\n\n"
            "1️⃣ *Llena el formulario* con tus datos:\n"
            "   • Nombre y documento (Cédula/RIF)\n"
            "   • Nombre de tu bodega\n"
            "   • Teléfono de contacto\n\n"
            "2️⃣ *Conoce el sistema completo* (características, precios, requisitos)\n\n"
            "✅ Después de completar el formulario, el Ingeniero Abigail te contactará con tu licencia demo de 5 días.",
            chat_id,
            call.message.message_id,
            parse_mode='Markdown',
            reply_markup=markup
        )
        print(f"📋 Demo solicitada por: @{call.from_user.username}")
    
    # VOLVER AL MENÚ
    elif call.data == 'menu':
        send_welcome(call.message)

# ==================== FUNCIONES ====================

def show_bodega_pro(chat_id, message_id=None):
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton('📋 Info Completa', callback_data='bodega_info'),
        types.InlineKeyboardButton('🎥 Demo en Vivo', callback_data='bodega_demo'),
        types.InlineKeyboardButton('💎 Comprar ($25)', url='https://wa.me/584164117331?text=Quiero%20comprar%20BODEGA%20PRO'),
        types.InlineKeyboardButton('🔙 Volver', callback_data='menu')
    )
    
    texto = (
        "🛒 *BODEGA PRO v2.0*\n"
        "_by A2K DIGITAL STUDIO_\n\n"
        "*El Sistema POS que tu Negocio Necesitaba* 💎\n\n"
        "⚡ *CARACTERÍSTICAS:*\n\n"
        "🏪 Punto de Venta completo\n"
        "💳 Todos los pagos de Venezuela\n"
        "📦 Inventario inteligente\n"
        "📊 Fórmula 50/30/20\n"
        "👥 Gestión de fiados\n"
        "💰 Control de caja\n"
        "📈 Reportes profesionales\n"
        "↩️ Devoluciones\n"
        "📷 Escáner QR/Barras\n"
        "🔐 Anti-reventa\n"
        "🌙 Modo oscuro\n\n"
        "💰 *$25 USD - Un solo pago*\n"
        "✅ Plan PREMIUM\n"
        "✅ Sin mensualidades"
    )
    
    if message_id:
        bot.edit_message_text(texto, chat_id, message_id, parse_mode='Markdown', reply_markup=markup)
    else:
        bot.send_message(chat_id, texto, parse_mode='Markdown', reply_markup=markup)

# ==================== INICIAR ====================

if __name__ == '__main__':
    print("=" * 50)
    print("✅ BOT TELEGRAM ZYNC ELECTRONICS v2.0 ACTIVO")
    print("=" * 50)
    print("📦 Productos ZYNC:", len(ZYNC))
    print("🇪🇸 Amazon España: Categorías OK")
    print("🇺🇸 Amazon USA: Categorías OK")
    print("🇨🇳 AliExpress:", len(ALIEXPRESS))
    print("🛒 BODEGA PRO v2.0: Incluido")
    print("💳 Métodos de pago:", len(BANCOS_NAC) + len(BANCOS_INT))
    print("=" * 50)
    print("Esperando mensajes...")
    print("=" * 50)
    
    bot.polling(none_stop=True)
