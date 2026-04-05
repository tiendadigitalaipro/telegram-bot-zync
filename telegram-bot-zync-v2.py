#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A2K Digital Studio - Asistente de Ventas por Telegram
Bot profesional para la venta de sistemas POS y aplicaciones de gestión.
Diseñado con un enfoque conversacional humano y estilo venezolano.
"""

import telebot
from telebot import types
import time
import random
import logging
from datetime import datetime

# ==================== CONFIGURACIÓN ====================

BOT_TOKEN = '8351227479:AAG66TOA8LosFHwmKwPsC3wZA0Tn8v_HhB0'
bot = telebot.TeleBot(BOT_TOKEN)

# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# URL de la tienda
STORE_URL = 'https://tiendadigitalaipro.github.io/a2k-digital-studio/'
WHATSAPP_CONTACT = '584164117331'

# ==================== ESTADOS DE CONVERSACIÓN ====================

user_states = {}

def get_state(user_id):
    return user_states.get(user_id, {'flow': 'menu', 'data': None})

def set_state(user_id, flow, data=None):
    user_states[user_id] = {'flow': flow, 'data': data}

# ==================== CATÁLOGO COMPLETO A2K (9 APPS) ====================

A2K_APPS = [
    {
        'id': 'barberia',
        'nombre': 'Barbería Pro',
        'icono': '💈',
        'precio': 25,
        'desc_corta': 'Sistema POS profesional para barberías',
        'desc_larga': (
            'Sistema POS profesional diseñado específicamente para barberías. '
            'Gestiona turnos, servicios, clientes, caja, reportes y facturas todo en un solo lugar.'
        ),
        'caracteristicas': [
            '📅 Gestión de turnos y citas',
            '💇 Registro de servicios',
            '👥 Base de datos de clientes',
            '💰 Control de caja diario',
            '📊 Reportes detallados',
            '🧾 Generación de facturas',
            '🌙 Modo oscuro incluido'
        ],
        'demo': 'https://tiendadigitalaipro.github.io/barberia-pro/',
        'keywords': ['barberia', 'barbería', 'barbero', 'barber', 'corte', 'peluqueria', 'peluquería']
    },
    {
        'id': 'nail',
        'nombre': 'Nail Studio Pro',
        'icono': '💅',
        'precio': 25,
        'desc_corta': 'Sistema POS para nail studios',
        'desc_larga': (
            'Sistema completo para la gestión de nail studios y salones de belleza. '
            'Agenda, clientas, servicios, materiales, y caja dual en dólares y bolívares.'
        ),
        'caracteristicas': [
            '📅 Agenda de citas',
            '👩 Base de datos de clientas',
            '💅 Catálogo de servicios',
            '📦 Control de materiales',
            '💵 Caja dual ($ / Bs)',
            '📊 Reportes por período'
        ],
        'demo': 'https://tiendadigitalaipro.github.io/nail-studio-pro/',
        'keywords': ['nail', 'uñas', 'manicura', 'pedicura', 'studio', 'belleza', 'salon', 'salón']
    },
    {
        'id': 'repuestos',
        'nombre': 'Repuestos de Motos Pro',
        'icono': '🏍️',
        'precio': 25,
        'desc_corta': 'Ventas e inventarios de repuestos de motos',
        'desc_larga': (
            'Sistema integral para la gestión de tiendas de repuestos de motos. '
            'Catálogo completo, inventario en tiempo real, ventas y reportes de gestión.'
        ),
        'caracteristicas': [
            '🔍 Catálogo de repuestos',
            '📦 Control de inventario',
            '🛒 Registro de ventas',
            '📊 Reportes de movimiento',
            '🏷️ Gestión de precios',
            '👥 Clientes y proveedores'
        ],
        'demo': 'https://tiendadigitalaipro.github.io/Repuestos-de-motos-pro-/',
        'keywords': ['repuestos', 'motos', 'motocicleta', 'moto', 'taller', 'mecanica', 'mecánica']
    },
    {
        'id': 'ferreteria',
        'nombre': 'Ferretería A2K Pro',
        'icono': '🔧',
        'precio': 25,
        'desc_corta': 'Inventario y ventas para ferreterías',
        'desc_larga': (
            'Sistema de gestión diseñado para ferreterías. '
            'Maneja inventario, ventas, facturación, proveedores y reportes de manera profesional.'
        ),
        'caracteristicas': [
            '📦 Gestión de inventario',
            '🛒 Punto de venta rápido',
            '🧾 Facturación profesional',
            '🚚 Control de proveedores',
            '📊 Reportes financieros',
            '👥 Base de clientes'
        ],
        'demo': 'https://tiendadigitalaipro.github.io/ferreteriaa2kDiitalStudioPro/',
        'keywords': ['ferreteria', 'ferretería', 'herramientas', 'construccion', 'construcción', 'tornillos', 'ferretero']
    },
    {
        'id': 'bodega_descarga',
        'nombre': 'Bodega Descarga Pro',
        'icono': '📦',
        'precio': 25,
        'desc_corta': 'Gestión comercial para bodegas con modo OFFLINE',
        'desc_larga': (
            'Sistema de gestión comercial completo para bodegas y abastos. '
            'Inventario, ventas, facturación y reportes. ¡Funciona SIN internet!'
        ),
        'caracteristicas': [
            '📦 Inventario inteligente',
            '🛒 Punto de venta completo',
            '🧾 Facturación automática',
            '📊 Reportes detallados',
            '📴 Funciona OFFLINE',
            '💳 Todos los métodos de pago VE',
            '👥 Gestión de fiados',
            '📷 Escáner QR/Código de barras'
        ],
        'demo': 'https://tiendadigitalaipro.github.io/bodega-pro-descarga.html/',
        'keywords': ['bodega', 'abasto', 'descarga', 'almacen', 'almacén', 'mayorista', 'grocery']
    },
    {
        'id': 'mercado_logic',
        'nombre': 'MERCADO LOGIC PRO',
        'icono': '🛒',
        'precio': 25,
        'desc_corta': 'Sistema Punto de Venta Industrial - El más avanzado',
        'desc_larga': (
            'El sistema Punto de Venta más avanzado de A2K Digital Studio. '
            'Incluye licencias con sistema IRON LOCK v2 para máxima seguridad. '
            'Ideal para negocios de gran escala.'
        ),
        'caracteristicas': [
            '🔒 Sistema IRON LOCK v2',
            '🛒 Punto de venta industrial',
            '📦 Inventario multi-almacén',
            '📊 Reportes avanzados',
            '👥 Multi-usuario y permisos',
            '💳 Integración de pagos',
            '📈 Analíticas de ventas',
            '🔧 Altamente personalizable'
        ],
        'demo': 'https://tiendadigitalaipro.github.io/mercado-logic-pro/',
        'keywords': ['mercado', 'logic', 'supermercado', 'industrial', 'iron lock', 'avanzado', 'escala']
    },
    {
        'id': 'farmacia',
        'nombre': 'Farmacia Pro Plus',
        'icono': '💊',
        'precio': 25,
        'desc_corta': 'Sistema de gestión para farmacias',
        'desc_larga': (
            'Sistema de gestión diseñado especialmente para farmacias. '
            'Control de ventas, inventario de medicamentos, fechas de vencimiento y más.'
        ),
        'caracteristicas': [
            '💊 Control de medicamentos',
            '📦 Inventario por lote',
            '📅 Alertas de vencimiento',
            '🛒 Punto de venta rápido',
            '👥 Historial de clientes',
            '📊 Reportes regulatorios'
        ],
        'demo': None,
        'keywords': ['farmacia', 'medicamentos', 'drogueria', 'droguería', 'salud', 'farmaceutico', 'farmacéutico', 'botica']
    },
    {
        'id': 'fruteria',
        'nombre': 'Frutería Pro',
        'icono': '🍎',
        'precio': 25,
        'desc_corta': 'Sistema POS para fruterías con 74 productos pre-cargados',
        'desc_larga': (
            'Sistema POS diseñado para fruterías y verdulerías. '
            'Viene con 74 productos pre-cargados, inventario, ventas y control total de tu negocio.'
        ),
        'caracteristicas': [
            '🍎 74 productos pre-cargados',
            '📦 Control de inventario',
            '🛒 Ventas rápidas',
            '📊 Reportes diarios',
            '🏷️ Gestión de precios',
            '📅 Control de fechas'
        ],
        'demo': None,
        'keywords': ['fruteria', 'frutería', 'frutas', 'verdura', 'verduría', 'hortaliza', 'mercado', 'fresh']
    },
    {
        'id': 'bodega_cloud',
        'nombre': 'Bodega Pro Cloud',
        'icono': '☁️',
        'precio': 25,
        'desc_corta': 'Bodega Pro con sincronización en tiempo real en la nube',
        'desc_larga': (
            'Toda la potencia de Bodega Pro pero con sincronización en tiempo real. '
            'Tus datos seguros en la nube, accesibles desde cualquier dispositivo y ubicación.'
        ),
        'caracteristicas': [
            '☁️ Sincronización en la nube',
            '📦 Inventario en tiempo real',
            '📱 Multi-dispositivo',
            '📊 Reportes en línea',
            '🔒 Respaldo automático',
            '🛒 Punto de venta completo',
            '👥 Colaboración en equipo'
        ],
        'demo': None,
        'keywords': ['cloud', 'nube', 'bodega cloud', 'sincronizar', 'sincronización', 'online', 'real time']
    }
]

# ==================== PRODUCTOS SECUNDARIOS (Amazon/AliExpress) ====================

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

# ==================== DATOS BANCARIOS ====================

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

# ==================== UTILIDADES ====================

# Variaciones de respuestas humanas
GREETINGS_VARIATIONS = [
    "¡Hola! ¿Cómo estás? 😊 Me alegra que me escribas. Soy el asistente de A2K Digital Studio y estoy aquí para ayudarte con lo que necesites.",
    "¡Buenas! ¿Qué tal? 👋 Qué gusto saludarte. Te cuento, en A2K Digital Studio tenemos las mejores aplicaciones para tu negocio.",
    "¡Hey! ¿Cómo va todo? 😄 Bienvenido a A2K Digital Studio. Dime, ¿en qué te puedo ayudar hoy?",
    "¡Saludos! ¿Cómo te va? 🙌 Me da gusto tenerte por acá. Soy tu asistente virtual de A2K Digital Studio.",
    "¡Qué bueno verte por aquí! 👋 Soy el asistente de A2K Digital Studio. ¿Qué necesitas saber?",
]

PRICE_VARIATIONS = [
    "Claro que sí, te paso los precios 📋\n\n💰 Todas nuestras aplicaciones tienen un precio especial de **$25 USD**.\n\n✅ Un solo pago, tuya para siempre\n✅ Sin mensualidades escondidas\n✅ Soporte técnico incluido\n\nSi necesitas terminal adicional son **$5 USD extra** por cada una.\n\n¿Te interesa alguna en particular?",
    "Con gusto te cuento los precios 💰\n\n💡 El precio de cualquiera de nuestras apps es de **$25 USD**.\n\nEso incluye:\n• Licencia completa\n• Actualizaciones gratis\n• Soporte por WhatsApp\n• Un solo pago, sin suscripciones\n\nTerminal extra: **+$5 USD**\n\n¿Quieres ver el catálogo completo?",
    "Te explico lo de los precios 🤓\n\nCada aplicación de A2K cuesta **$25 USD** y es un pago único.\n\nVamos, es una inversión que se paga sola 📈\n\nExtra por terminal: **$5 USD**\n\n¿Cuál te llama la atención?",
]

THANK_YOU_VARIATIONS = [
    "¡De nada! Para eso estamos 😊 Si necesitas algo más, aquí andamos. ¡Éxitos con tu negocio!",
    "Un placer ayudarte! 👍 No dudes en escribirme cuando quieras. Estoy disponible 24/7.",
    "¡Igualmente! Qué gusto atenderte ✨ Recuerda que puedes escribirme cuando necesites. ¡Buen día!",
    "¡No hay de qué! 🙏 Me alegra poder ayudarte. Si surge alguna duda, ya sabes dónde encontrarme.",
    "¡Con mucho gusto! 😄 Espero verte pronto. Ah, y no olvides visitar nuestra tienda online. ¡Abrazo!",
]

PURCHASE_VARIATIONS = [
    "¡Excelente decisión! 🎉 Te guío para que puedas adquirir tu aplicación:\n\n1️⃣ Haz clic en el botón de abajo para ir a WhatsApp\n2️⃣ El ingeniero Abigail te atenderá personalmente\n3️⃣ Te comparte los datos de pago\n4️⃣ Haces el pago y ¡listo! Te entrega tu licencia\n\nEs súper rápido, te lo prometo 💪",
    "¡Qué buena elección! 😍 Vamos a hacer esto fácil para ti:\n\n👇 Dale al botón de \"Comprar por WhatsApp\" y el ingeniero se encarga de todo. Te orienta paso a paso, te da los datos de pago y en poco tiempo tienes tu sistema funcionando.\n\n¿Listo para automatizar tu negocio? 💼",
    "¡Me parece perfecto! 🔥 Comprar es muy sencillo:\n\nSolo necesitas contactarnos por WhatsApp. El ingeniero Abigail te atiende directamente y te guía con todo el proceso.\n\nNo te preocupes, somos 100% confiables ✅",
]

UNKNOWN_VARIATIONS = [
    "Mm, no estoy seguro de entender bien lo que dices 🤔 Pero no te preocupes, déjame ayudarte.\n\nAquí en A2K Digital Studio creamos sistemas profesionales para negocios. Puedo mostrarte nuestro catálogo, precios, o ayudarte a comprar.\n\n¿Qué te gustaría ver?",
    "Jeje, creo que necesito un poco más de contexto 😅 Pero tranquilo, para eso estoy.\n\nTe cuento rápido: tenemos 9 aplicaciones de gestión para diferentes negocios, todas a $25 USD.\n\n¿Quieres que te muestre el catálogo? 👇",
    "Ajá, entiendo... o creo que sí 😄 Mira, lo mejor es que te muestre las opciones que tenemos disponibles.\n\nTenemos sistemas para barberías, ferreterías, bodegas, farmacias y más.\n\nDime, ¿qué tipo de negocio tienes? Así te recomiendo la app ideal 💡",
]

FOLLOW_UP_VARIATIONS = [
    "Por cierto, ¿sabías que también tenemos otras aplicaciones que podrían interesarte? 🤔",
    "Oye, y no olvides que puedes probar antes de comprar con nuestra demo en vivo 🎥",
    "Ah, y si necesitas algo personalizado, el ingeniero Abigail siempre está disponible por WhatsApp 💬",
    "Tip: muchas veces combinar dos aplicaciones da mejores resultados. Por ejemplo, Bodega Descarga Pro + Farmacia Pro Plus 💡",
]

GOODBYE_VARIATIONS = [
    "¡Hasta luego! 👋 Fue un gusto atenderte. No dudes en volver cuando quieras. ¡Mucho éxito!",
    "¡Nos vemos! 😊 Espero haberte ayudado. Estaré por aquí cuando me necesites. ¡Cuidate!",
    "¡Chao, parche! 🤙 Un placer. Vuelve cuando quieras, la puerta está abierta. ¡Éxitos!",
]

DEMO_VARIATIONS = [
    "¡Buena idea! Probar antes de comprar siempre es lo mejor 🧪\n\nTe cuento cómo funciona:\n\n🎥 Puedes ver una demo en vivo por videollamada con el ingeniero Abigail. Te muestra el sistema funcionando, responde todas tus dudas y tú decides si es lo que necesitas.\n\n¡Sin compromiso! 👇",
    "Me gusta que quieras verlo antes 🎯 Es la mejor forma de convencerte.\n\nTenemos demos disponibles para varias de nuestras apps. Solo escribe al ingeniero por WhatsApp y coordina una videollamada.\n\nTe aseguro que vas a quedar impresionado 😎👇",
    "Perfecto, ¡vamos a agendar tu demo! 📅\n\nSolo tienes que contactar al ingeniero Abigail por WhatsApp. Él te programa una sesión en vivo donde ves el sistema en acción.\n\nTotalmente gratis y sin compromiso ✅👇",
]

def get_whatsapp_buy_url(app_nombre):
    """Genera URL de WhatsApp para compra con mensaje pre-llenado."""
    import urllib.parse
    msg = f'Quiero comprar {app_nombre} - A2K Digital Studio'
    encoded = urllib.parse.quote(msg)
    return f'https://wa.me/{WHATSAPP_CONTACT}?text={encoded}'

def get_whatsapp_demo_url(app_nombre):
    """Genera URL de WhatsApp para solicitar demo."""
    import urllib.parse
    msg = f'Quiero ver la demo de {app_nombre} - A2K Digital Studio'
    encoded = urllib.parse.quote(msg)
    return f'https://wa.me/{WHATSAPP_CONTACT}?text={encoded}'

def simulate_typing(chat_id, duration=1.5):
    """Simula que el bot está escribiendo para sentirse más humano."""
    bot.send_chat_action(chat_id, 'typing')
    time.sleep(duration)

def find_app_by_keywords(text):
    """Busca una app por keywords en el texto del usuario."""
    text_lower = text.lower().strip()
    best_match = None
    best_score = 0

    for app in A2K_APPS:
        score = 0
        for kw in app['keywords']:
            if kw in text_lower:
                score += len(kw)  # Prioriza matches más largos
            # Also check partial matches for flexibility
            if kw in text_lower.replace(' ', ''):
                score += len(kw) // 2
        if score > best_score:
            best_score = score
            best_match = app

    # Only return if there's a meaningful match
    if best_score >= 3:
        return best_match
    return None

def is_greeting(text):
    """Detecta si el texto es un saludo."""
    greetings = [
        'hola', 'buenas', 'hey', 'buen dia', 'buenos dias', 'buenas tardes',
        'buenas noches', 'saludos', 'qué tal', 'que tal', 'como estas',
        'como andas', 'que hay', 'que hubo', 'epa', 'hello', 'hi', 'ey'
    ]
    text_lower = text.lower().strip()
    return any(g in text_lower for g in greetings)

def is_price_question(text):
    """Detecta si el usuario pregunta por precios."""
    keywords = [
        'precio', 'cuanto cuesta', 'cuánto cuesta', 'cuanto vale', 'cuánto vale',
        'costo', 'tarifa', 'planes', 'plan', 'pagar', 'cuanto es', 'cuánto es',
        'dinero', 'valor'
    ]
    text_lower = text.lower().strip()
    return any(k in text_lower for k in keywords)

def is_demo_request(text):
    """Detecta si el usuario pide una demo."""
    keywords = [
        'demo', 'probar', 'prueba', 'ver como funciona', 'testear', 'vista previa',
        'video', 'mostrar', 'ver el sistema', 'ensayar'
    ]
    text_lower = text.lower().strip()
    return any(k in text_lower for k in keywords)

def is_purchase_intent(text):
    """Detecta si el usuario quiere comprar."""
    keywords = [
        'comprar', 'quiero', 'deseo', 'adquirir', 'me llevo', 'lo quiero',
        'cómo compro', 'como compro', 'donde compro', 'dónde compro', 'compra',
        'pagar', 'pago', 'necesito', 'me interesa', 'oferta'
    ]
    text_lower = text.lower().strip()
    return any(k in text_lower for k in keywords)

def is_thank_you(text):
    """Detecta si el usuario está agradeciendo."""
    keywords = [
        'gracias', 'muchas gracias', 'genial', 'perfecto', 'excelente',
        'chamo', 'ere un cracking', 'eres la zona', 'buen trabajo', 'muy amable',
        'agradecido', 'te lo agradesco', 'thanks'
    ]
    text_lower = text.lower().strip()
    return any(k in text_lower for k in keywords)

def is_goodbye(text):
    """Detecta si el usuario se despide."""
    keywords = [
        'adiós', 'adios', 'chao', 'chau', 'hasta luego', 'nos vemos',
        'bye', 'me voy', 'hasta pronto', 'suerte', 'buenas noches'
    ]
    text_lower = text.lower().strip()
    return any(k in text_lower for k in keywords)

def is_contact_request(text):
    """Detecta si el usuario pide contacto."""
    keywords = [
        'contacto', 'contactar', 'teléfono', 'telefono', 'whatsapp',
        'hablar', 'escribir', 'comunicar', 'ingeniero', 'abigail'
    ]
    text_lower = text.lower().strip()
    return any(k in text_lower for k in keywords)

def is_payment_request(text):
    """Detecta si el usuario pregunta por métodos de pago."""
    keywords = [
        'pago', 'pagar', 'pagos', 'banco', 'bancos', 'transferencia',
        'deposito', 'depósito', 'zelle', 'paypal', 'método', 'metodo',
        'cómo pago', 'como pago', 'efectivo', 'pago móvil'
    ]
    text_lower = text.lower().strip()
    return any(k in text_lower for k in keywords)

def is_store_request(text):
    """Detecta si el usuario pide la tienda."""
    keywords = [
        'tienda', 'store', 'página', 'pagina', 'web', 'link', 'enlace',
        'sitio', 'catálogo', 'catalogo'
    ]
    text_lower = text.lower().strip()
    return any(k in text_lower for k in keywords)

# ==================== KEYBOARDS ====================

def get_main_menu_keyboard():
    """Teclado principal persistente."""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton('📋 Catálogo A2K'),
        types.KeyboardButton('💰 Precios'),
    )
    markup.add(
        types.KeyboardButton('🎥 Ver Demo'),
        types.KeyboardButton('💳 Métodos de Pago'),
    )
    markup.add(
        types.KeyboardButton('🛒 Otros Productos'),
        types.KeyboardButton('👤 Contacto'),
    )
    return markup

def get_catalog_inline_keyboard():
    """Teclado inline del catálogo principal."""
    markup = types.InlineKeyboardMarkup(row_width=3)
    for app in A2K_APPS:
        markup.add(types.InlineKeyboardButton(
            f"{app['icono']} {app['nombre']}",
            callback_data=f"app_{app['id']}"
        ))
    markup.add(
        types.InlineKeyboardButton('🏪 Tienda Online', url=STORE_URL),
        types.InlineKeyboardButton('💳 Ver Pagos', callback_data='pagos'),
    )
    markup.add(types.InlineKeyboardButton('🔙 Volver al Menú', callback_data='main_menu'))
    return markup

def get_app_detail_keyboard(app):
    """Teclado inline para detalle de una app específica."""
    markup = types.InlineKeyboardMarkup(row_width=2)
    if app.get('demo'):
        markup.add(types.InlineKeyboardButton(
            '🎥 Ver Demo en Vivo',
            callback_data=f'demo_{app["id"]}'
        ))
    markup.add(
        types.InlineKeyboardButton(
            '💬 Comprar por WhatsApp',
            url=get_whatsapp_buy_url(app['nombre'])
        ),
        types.InlineKeyboardButton(
            '🎬 Solicitar Demo',
            url=get_whatsapp_demo_url(app['nombre'])
        ),
    )
    markup.add(types.InlineKeyboardButton('📋 Catálogo Completo', callback_data='catalog'))
    markup.add(types.InlineKeyboardButton('🔙 Volver al Menú', callback_data='main_menu'))
    return markup

def get_suggested_apps_keyboard(current_app_id, count=2):
    """Sugiere apps relacionadas."""
    related_map = {
        'barberia': ['nail', 'ferreteria'],
        'nail': ['barberia', 'farmacia'],
        'repuestos': ['ferreteria', 'mercado_logic'],
        'ferreteria': ['repuestos', 'mercado_logic'],
        'bodega_descarga': ['bodega_cloud', 'mercado_logic'],
        'mercado_logic': ['bodega_descarga', 'bodega_cloud'],
        'farmacia': ['nail', 'mercado_logic'],
        'fruteria': ['mercado_logic', 'bodega_descarga'],
        'bodega_cloud': ['bodega_descarga', 'mercado_logic'],
    }
    suggested_ids = related_map.get(current_app_id, ['bodega_descarga', 'mercado_logic'])[:count]
    markup = types.InlineKeyboardMarkup(row_width=2)
    for sid in suggested_ids:
        app = next((a for a in A2K_APPS if a['id'] == sid), None)
        if app:
            markup.add(types.InlineKeyboardButton(
                f"➡️ {app['icono']} {app['nombre']}",
                callback_data=f'app_{app["id"]}'
            ))
    markup.add(types.InlineKeyboardButton('📋 Todo el Catálogo', callback_data='catalog'))
    return markup

# ==================== MENSAJES ====================

def build_welcome_message():
    """Construye el mensaje de bienvenida."""
    return (
        "✨ *A2K Digital Studio*\n"
        "━ *Soluciones Tecnológicas para tu Negocio*\n\n"
        "¡Hola! 👋 Bienvenido al asistente virtual de A2K Digital Studio.\n\n"
        "Somos especialistas en crear sistemas de gestión profesional para todo tipo de negocios. "
        "Desde barberías hasta supermercados, tenemos la solución ideal para ti.\n\n"
        "📌 *¿Qué ofrecemos?*\n"
        "• 9 aplicaciones profesionales\n"
        "• Precio único: $25 USD por app\n"
        "• Un solo pago, sin mensualidades\n"
        "• Soporte técnico incluido\n"
        "• Demo en vivo gratis\n\n"
        "🛒 *Tienda Online:* {store}\n\n"
        "Selecciona una opción del menú o simplemente dime qué necesitas y yo te ayudo 😊"
    ).format(store=STORE_URL)

def build_catalog_message():
    """Construye el mensaje del catálogo completo."""
    apps_list = ""
    for i, app in enumerate(A2K_APPS, 1):
        apps_list += (
            f"\n{i}. {app['icono']} *{app['nombre']}*\n"
            f"   _{app['desc_corta']}_\n"
        )

    return (
        "🛒 *CATÁLOGO COMPLETO - A2K Digital Studio*\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{apps_list}\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n"
        "💰 *Precio: $25 USD* cada aplicación\n"
        "➕ Terminal adicional: +$5 USD\n"
        "✅ Un solo pago | Sin mensualidades\n\n"
        "🛒 *Tienda:* {store}\n\n"
        "👇 Toca cualquier app para ver más detalles:"
    ).format(store=STORE_URL)

def build_app_detail_message(app):
    """Construye el mensaje de detalle de una app."""
    features = "\n".join(f"   {f}" for f in app['caracteristicas'])

    demo_line = ""
    if app.get('demo'):
        demo_line = f"\n🎥 *Demo:* [Ver demo online]({app['demo']})\n"

    return (
        "━━━━━━━━━━━━━━━━━━━━━━━\n"
        "{icono} *{nombre}*\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "{desc_larga}\n\n"
        "✨ *Características principales:*\n"
        "{features}\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n"
        "💰 *Precio: ${precio} USD*\n"
        "➕ Terminal extra: +$5 USD\n"
        "✅ Un solo pago | Soporte incluido"
        "{demo_line}\n"
        "👇 ¿Qué quieres hacer?"
    ).format(
        icono=app['icono'],
        nombre=app['nombre'],
        desc_larga=app['desc_larga'],
        features=features,
        precio=app['precio'],
        demo_line=demo_line,
    )

def build_pricing_message():
    """Construye el mensaje de precios."""
    return (
        "💰 *PLANES Y PRECIOS - A2K Digital Studio*\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🏷️ *Plan Estándar:*\n"
        "   • 1 licencia por aplicación: **$25 USD**\n"
        "   • Soporte por WhatsApp\n"
        "   • Actualizaciones gratis\n"
        "   • Un solo pago, tuya para siempre\n\n"
        "➕ *Terminal Adicional:*\n"
        "   • Cada terminal extra: **+$5 USD**\n"
        "   • Ideal para negocios con múltiples puntos de venta\n\n"
        "✅ *¿Qué incluye?*\n"
        "   • Licencia completa sin restricciones\n"
        "   • Soporte técnico personalizado\n"
        "   • Actualizaciones futuras sin costo\n"
        "   • Tutorial de uso\n"
        "   • Configuración asistida\n\n"
        "🚫 *Nada de:*\n"
        "   • Mensualidades\n"
        "   • Suscripciones\n"
        "   • Costos ocultos\n\n"
        "🛒 *Tienda:* {store}\n\n"
        "¿Listo para automatizar tu negocio? 👇"
    ).format(store=STORE_URL)

def build_payment_message():
    """Construye el mensaje de métodos de pago."""
    banks = ""
    for b in BANCOS_NAC:
        banks += f"   • {b['n']}\n"

    intl = ""
    for b in BANCOS_INT:
        intl += f"   • {b['n']}\n"

    return (
        "💳 *MÉTODOS DE PAGO - A2K Digital Studio*\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🏦 *Bancos Nacionales (Bs):*\n"
        "{banks}\n"
        "💵 *Plataformas Internacionales (USD):*\n"
        "{intl}\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "📲 Para recibir los datos completos de la cuenta que prefieras, "
        "contacta directamente por WhatsApp.\n\n"
        "✅ Aceptamos pagos en bolívares y dólares."
    ).format(banks=banks, intl=intl)

def build_payment_full_message():
    """Mensaje completo con todos los datos bancarios."""
    nac_lines = ""
    for b in BANCOS_NAC:
        nac_lines += (
            f"\n🏦 *{b['n']}*\n"
            f"   Cta: `{b['c']}`\n"
            f"   Titular: {b['t']}\n"
            f"   CI/RIF: {b['ci']}\n"
        )

    int_lines = ""
    for b in BANCOS_INT:
        line = f"\n💳 *{b['n']}*\n"
        if 'd' in b:
            line += f"   Datos: `{b['d']}`\n"
        if 'routing' in b:
            line += f"   Routing: `{b['routing']}`\n"
        if 'aba' in b:
            line += f"   ABA: `{b['aba']}`\n"
        if 'swift' in b:
            line += f"   SWIFT: `{b['swift']}`\n"
        if 'iban' in b:
            line += f"   IBAN: `{b['iban']}`\n"
        if 'bic' in b:
            line += f"   BIC: `{b['bic']}`\n"
        int_lines += line

    return (
        "💳 *DATOS BANCARIOS COMPLETOS*\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🏦 *CUENTAS NACIONALES (Bs):*\n"
        "{nac}\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "💵 *CUENTAS INTERNACIONALES (USD):*\n"
        "{intl}\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "⚠️ *Importante:* Envía el comprobante de pago por WhatsApp "
        "para procesar tu pedido rápidamente.\n\n"
        "📱 *WhatsApp:* @{wa}".format(wa=WHATSAPP_CONTACT)
    ).format(nac=nac_lines, intl=int_lines)

def build_contact_message():
    """Construye el mensaje de contacto."""
    return (
        "👤 *CONTACTO - A2K Digital Studio*\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "👨‍💻 *Ingeniero Abigail Rojas*\n"
        "   Desarrollador principal\n\n"
        "📲 *WhatsApp:* +58 416-4117331\n"
        "📧 *Email:* abijose1158@gmail.com\n"
        "🏢 *Empresa:* Inversiones 2K 3112 C.A\n"
        "   RIF: J-40632338-1\n\n"
        "🛒 *Tienda Online:* {store}\n\n"
        "⏰ Horario de atención: Lunes a Sábado, 8:00 AM - 6:00 PM\n\n"
        "👇 Escríbenos directamente por WhatsApp:"
    ).format(store=STORE_URL)

def build_store_message():
    """Construye el mensaje de la tienda."""
    return (
        "🛒 *TIENDA ONLINE - A2K Digital Studio*\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "Visita nuestra tienda oficial donde puedes explorar todas nuestras aplicaciones:\n\n"
        "🔗 [A2K Digital Studio - Tienda Online]({store})\n\n"
        "En la tienda encontrarás:\n"
        "• Descripciones detalladas de cada app\n"
        "• Capturas de pantalla\n"
        "• Enlaces a demos interactivas\n"
        "• Precios actualizados\n\n"
        "¿Prefieres atención personalizada? Escríbenos por WhatsApp 👇"
    ).format(store=STORE_URL)

# ==================== HANDLERS DE COMANDOS ====================

@bot.message_handler(commands=['start'])
def cmd_start(message):
    """Comando /start - Mensaje de bienvenida."""
    chat_id = message.chat.id
    user_id = message.from_user.id
    username = message.from_user.username or "amigo"

    set_state(user_id, 'menu')
    logger.info(f"START - Usuario: @{username} ({user_id})")

    simulate_typing(chat_id, 1.5)

    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton('📋 Ver Catálogo', callback_data='catalog'),
        types.InlineKeyboardButton('💰 Ver Precios', callback_data='precios'),
    )
    markup.add(
        types.InlineKeyboardButton('🎥 Solicitar Demo', callback_data='demo_general'),
        types.InlineKeyboardButton('💳 Métodos de Pago', callback_data='pagos'),
    )
    markup.add(
        types.InlineKeyboardButton('🛒 Tienda Online', url=STORE_URL),
        types.InlineKeyboardButton('👤 Contacto', callback_data='contacto'),
    )
    markup.add(
        types.InlineKeyboardButton('🛒 Otros Productos', callback_data='otros_productos'),
    )

    bot.send_message(
        chat_id,
        build_welcome_message(),
        parse_mode='Markdown',
        reply_markup=markup,
        disable_web_page_preview=True
    )

    # Enviar teclado persistente
    bot.send_message(
        chat_id,
        "📱 *Usa el menú de abajo* para navegar más rápido, o simplemente escríbeme lo que necesitas y yo te ayudo 😊",
        parse_mode='Markdown',
        reply_markup=get_main_menu_keyboard()
    )


@bot.message_handler(commands=['menu'])
def cmd_menu(message):
    """Comando /menu - Menú principal."""
    cmd_start(message)


@bot.message_handler(commands=['catalogo', 'catalog'])
def cmd_catalogo(message):
    """Comando /catalogo - Catálogo completo."""
    chat_id = message.chat.id
    user_id = message.from_user.id
    set_state(user_id, 'catalog')

    simulate_typing(chat_id, 1.0)

    bot.send_message(
        chat_id,
        build_catalog_message(),
        parse_mode='Markdown',
        reply_markup=get_catalog_inline_keyboard(),
        disable_web_page_preview=True
    )


@bot.message_handler(commands=['precios', 'precio', 'prices'])
def cmd_precios(message):
    """Comando /precios - Información de precios."""
    chat_id = message.chat.id
    user_id = message.from_user.id
    set_state(user_id, 'menu')

    simulate_typing(chat_id, 1.0)

    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton('📋 Ver Catálogo', callback_data='catalog'),
        types.InlineKeyboardButton('💬 Comprar por WhatsApp', url=f'https://wa.me/{WHATSAPP_CONTACT}?text=Quiero%20info%20de%20precios%20A2K'),
    )
    markup.add(types.InlineKeyboardButton('🔙 Menú Principal', callback_data='main_menu'))

    bot.send_message(
        chat_id,
        build_pricing_message(),
        parse_mode='Markdown',
        reply_markup=markup,
        disable_web_page_preview=True
    )


@bot.message_handler(commands=['demo'])
def cmd_demo(message):
    """Comando /demo - Solicitar demo."""
    chat_id = message.chat.id
    user_id = message.from_user.id
    set_state(user_id, 'demo_request')

    simulate_typing(chat_id, 1.0)
    bot.send_message(chat_id, random.choice(DEMO_VARIATIONS), parse_mode='Markdown')


@bot.message_handler(commands=['pagos', 'pago'])
def cmd_pagos(message):
    """Comando /pagos - Métodos de pago."""
    chat_id = message.chat.id
    user_id = message.from_user.id
    set_state(user_id, 'payment')

    simulate_typing(chat_id, 1.0)

    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton('📋 Ver Datos Completos', callback_data='pagos_full'),
        types.InlineKeyboardButton('💬 WhatsApp para Pagos', url=f'https://wa.me/{WHATSAPP_CONTACT}?text=Necesito%20datos%20de%20pago%20A2K'),
    )
    markup.add(types.InlineKeyboardButton('🔙 Menú Principal', callback_data='main_menu'))

    bot.send_message(
        chat_id,
        build_payment_message(),
        parse_mode='Markdown',
        reply_markup=markup
    )


@bot.message_handler(commands=['contacto', 'contact'])
def cmd_contacto(message):
    """Comando /contacto - Información de contacto."""
    chat_id = message.chat.id

    simulate_typing(chat_id, 1.0)

    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton('💬 WhatsApp', url=f'https://wa.me/{WHATSAPP_CONTACT}'),
        types.InlineKeyboardButton('🛒 Tienda Online', url=STORE_URL),
    )
    markup.add(types.InlineKeyboardButton('🔙 Menú Principal', callback_data='main_menu'))

    bot.send_message(
        chat_id,
        build_contact_message(),
        parse_mode='Markdown',
        reply_markup=markup,
        disable_web_page_preview=True
    )


@bot.message_handler(commands=['tienda', 'store'])
def cmd_tienda(message):
    """Comando /tienda - Link de la tienda."""
    chat_id = message.chat.id

    simulate_typing(chat_id, 1.0)

    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton('🛒 Abrir Tienda', url=STORE_URL),
        types.InlineKeyboardButton('💬 WhatsApp', url=f'https://wa.me/{WHATSAPP_CONTACT}'),
    )
    markup.add(types.InlineKeyboardButton('🔙 Menú Principal', callback_data='main_menu'))

    bot.send_message(
        chat_id,
        build_store_message(),
        parse_mode='Markdown',
        reply_markup=markup,
        disable_web_page_preview=True
    )


@bot.message_handler(commands=['bodegapro'])
def cmd_bodegapro(message):
    """Comando /bodegapro - Info directa de Bodega Pro."""
    chat_id = message.chat.id
    app = next((a for a in A2K_APPS if a['id'] == 'bodega_descarga'), None)
    if app:
        simulate_typing(chat_id, 1.5)
        bot.send_message(
            chat_id,
            build_app_detail_message(app),
            parse_mode='Markdown',
            reply_markup=get_app_detail_keyboard(app),
            disable_web_page_preview=True
        )

# ==================== HANDLER INTELIGENTE DE TEXTO ====================

@bot.message_handler(func=lambda message: True, content_types=['text'])
def handle_smart_text(message):
    """Handler inteligente que interpreta cualquier texto del usuario."""
    chat_id = message.chat.id
    user_id = message.from_user.id
    text = message.text.strip()
    text_lower = text.lower()

    logger.info(f"TEXTO - @{message.from_user.username or 'unknown'}: {text}")

    state = get_state(user_id)

    simulate_typing(chat_id, random.uniform(0.8, 1.8))

    # === 1. Detectar saludo ===
    if is_greeting(text) and len(text) < 30:
        bot.send_message(chat_id, random.choice(GREETINGS_VARIATIONS), parse_mode='Markdown',
                         reply_markup=get_main_menu_keyboard())
        set_state(user_id, 'menu')
        return

    # === 2. Detectar despedida ===
    if is_goodbye(text) and len(text) < 30:
        bot.send_message(chat_id, random.choice(GOODBYE_VARIATIONS), parse_mode='Markdown')
        set_state(user_id, 'menu')
        return

    # === 3. Detectar agradecimiento ===
    if is_thank_you(text) and len(text) < 40:
        resp = random.choice(THANK_YOU_VARIATIONS)
        # Add a follow-up sometimes
        if random.random() > 0.5:
            resp += "\n\n" + random.choice(FOLLOW_UP_VARIATIONS)
        bot.send_message(chat_id, resp, parse_mode='Markdown')
        return

    # === 4. Detectar pregunta de precio ===
    if is_price_question(text):
        bot.send_message(
            chat_id,
            random.choice(PRICE_VARIATIONS),
            parse_mode='Markdown'
        )
        set_state(user_id, 'menu')
        return

    # === 5. Detectar solicitud de demo ===
    if is_demo_request(text):
        bot.send_message(chat_id, random.choice(DEMO_VARIATIONS), parse_mode='Markdown')
        set_state(user_id, 'demo_request')

        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton('🎬 Solicitar Demo por WhatsApp', url=f'https://wa.me/{WHATSAPP_CONTACT}?text=Quiero%20ver%20una%20demo%20A2K'),
        )
        markup.add(types.InlineKeyboardButton('📋 Ver Catálogo', callback_data='catalog'))
        bot.send_message(chat_id, "👇 agenda tu demo ahora:", reply_markup=markup)
        return

    # === 6. Detectar intención de compra ===
    if is_purchase_intent(text):
        bot.send_message(
            chat_id,
            random.choice(PURCHASE_VARIATIONS),
            parse_mode='Markdown'
        )

        # Check if they mention a specific app
        app = find_app_by_keywords(text)
        if app:
            markup = types.InlineKeyboardMarkup()
            markup.add(
                types.InlineKeyboardButton(
                    f'💬 Comprar {app["nombre"]}',
                    url=get_whatsapp_buy_url(app['nombre'])
                )
            )
            markup.add(types.InlineKeyboardButton('📋 Ver Catálogo', callback_data='catalog'))
            bot.send_message(chat_id, f"Vi que te interesa **{app['icono']} {app['nombre']}**. ¡Excelente elección! 👇",
                             parse_mode='Markdown', reply_markup=markup)
        else:
            markup = types.InlineKeyboardMarkup()
            markup.add(
                types.InlineKeyboardButton('💬 Comprar por WhatsApp', url=f'https://wa.me/{WHATSAPP_CONTACT}?text=Quiero%20comprar%20una%20app%20A2K'),
            )
            markup.add(types.InlineKeyboardButton('📋 Ver Catálogo', callback_data='catalog'))
            bot.send_message(chat_id, "👇 Elige tu opción:", reply_markup=markup)

        set_state(user_id, 'purchase')
        return

    # === 7. Detectar petición de contacto ===
    if is_contact_request(text):
        bot.send_message(chat_id, "Claro que sí, aquí tienes los datos de contacto 👇", parse_mode='Markdown')
        simulate_typing(chat_id, 0.5)
        cmd_contacto(message)
        return

    # === 8. Detectar petición de métodos de pago ===
    if is_payment_request(text):
        bot.send_message(chat_id, "Te muestro las opciones de pago que tenemos disponibles 💳", parse_mode='Markdown')
        simulate_typing(chat_id, 0.5)
        cmd_pagos(message)
        return

    # === 9. Detectar petición de tienda ===
    if is_store_request(text):
        bot.send_message(chat_id, "¡Claro! Aquí tienes nuestra tienda online 🛒", parse_mode='Markdown')
        simulate_typing(chat_id, 0.5)
        cmd_tienda(message)
        return

    # === 10. Buscar app por keywords en el texto ===
    app = find_app_by_keywords(text)
    if app:
        bot.send_message(
            chat_id,
            f"¡Creo que te refieres a **{app['icono']} {app['nombre']}**! 🎯 Déjame mostrarte todos los detalles:",
            parse_mode='Markdown'
        )
        simulate_typing(chat_id, 1.0)
        bot.send_message(
            chat_id,
            build_app_detail_message(app),
            parse_mode='Markdown',
            reply_markup=get_app_detail_keyboard(app),
            disable_web_page_preview=True
        )
        set_state(user_id, 'app_detail', app['id'])

        # Sugerir apps relacionadas después de un momento
        suggest_related_apps(chat_id, app)
        return

    # === 11. Mensaje no reconocido - respuesta amigable ===
    resp = random.choice(UNKNOWN_VARIATIONS)
    bot.send_message(chat_id, resp, parse_mode='Markdown')

    # Mostrar opciones
    simulate_typing(chat_id, 1.0)
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton('📋 Catálogo A2K', callback_data='catalog'),
        types.InlineKeyboardButton('💰 Precios', callback_data='precios'),
    )
    markup.add(
        types.InlineKeyboardButton('🎥 Demo', callback_data='demo_general'),
        types.InlineKeyboardButton('👤 Contacto', callback_data='contacto'),
    )
    bot.send_message(
        chat_id,
        "O si prefieres, puedes usar los botones del menú de abajo 👇",
        reply_markup=markup
    )

    set_state(user_id, 'menu')


def suggest_related_apps(chat_id, app):
    """Sugiere apps relacionadas después de un delay."""
    try:
        time.sleep(3)
        suggestion = random.choice(FOLLOW_UP_VARIATIONS)
        bot.send_message(chat_id, suggestion, parse_mode='Markdown')
        bot.send_message(
            chat_id,
            f"¿Te puede interesar alguna de estas? 👇",
            parse_mode='Markdown',
            reply_markup=get_suggested_apps_keyboard(app['id'])
        )
    except Exception:
        pass  # Don't crash if the suggestion fails


# ==================== CALLBACK QUERY HANDLERS ====================

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    """Maneja todos los callbacks de botones inline."""
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    data = call.data

    logger.info(f"CALLBACK - @{call.from_user.username or 'unknown'}: {data}")

    # Always answer the callback
    try:
        bot.answer_callback_query(call.id)
    except Exception:
        pass

    # ========== MENÚ PRINCIPAL ==========
    if data == 'main_menu':
        set_state(user_id, 'menu')
        simulate_typing(chat_id, 0.5)
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton('📋 Ver Catálogo', callback_data='catalog'),
            types.InlineKeyboardButton('💰 Ver Precios', callback_data='precios'),
        )
        markup.add(
            types.InlineKeyboardButton('🎥 Solicitar Demo', callback_data='demo_general'),
            types.InlineKeyboardButton('💳 Métodos de Pago', callback_data='pagos'),
        )
        markup.add(
            types.InlineKeyboardButton('🛒 Tienda Online', url=STORE_URL),
            types.InlineKeyboardButton('👤 Contacto', callback_data='contacto'),
        )
        markup.add(types.InlineKeyboardButton('🛒 Otros Productos', callback_data='otros_productos'))

        bot.edit_message_text(
            chat_id=chat_id,
            message_id=call.message.message_id,
            text=(
                "🏠 *Menú Principal - A2K Digital Studio*\n\n"
                "¿En qué te puedo ayudar hoy? Selecciona una opción 👇"
            ),
            parse_mode='Markdown',
            reply_markup=markup
        )
        return

    # ========== CATÁLOGO ==========
    elif data == 'catalog':
        set_state(user_id, 'catalog')
        try:
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=call.message.message_id,
                text=build_catalog_message(),
                parse_mode='Markdown',
                reply_markup=get_catalog_inline_keyboard(),
                disable_web_page_preview=True
            )
        except Exception:
            bot.send_message(
                chat_id,
                build_catalog_message(),
                parse_mode='Markdown',
                reply_markup=get_catalog_inline_keyboard(),
                disable_web_page_preview=True
            )
        return

    # ========== DETALLE DE APP ==========
    elif data.startswith('app_'):
        app_id = data[4:]
        app = next((a for a in A2K_APPS if a['id'] == app_id), None)
        if app:
            set_state(user_id, 'app_detail', app_id)
            try:
                bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=call.message.message_id,
                    text=build_app_detail_message(app),
                    parse_mode='Markdown',
                    reply_markup=get_app_detail_keyboard(app),
                    disable_web_page_preview=True
                )
            except Exception:
                bot.send_message(
                    chat_id,
                    build_app_detail_message(app),
                    parse_mode='Markdown',
                    reply_markup=get_app_detail_keyboard(app),
                    disable_web_page_preview=True
                )
        return

    # ========== DEMO GENERAL ==========
    elif data == 'demo_general':
        set_state(user_id, 'demo_request')
        try:
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=call.message.message_id,
                text=random.choice(DEMO_VARIATIONS),
                parse_mode='Markdown',
                reply_markup=types.InlineKeyboardMarkup()
            )
        except Exception:
            bot.send_message(chat_id, random.choice(DEMO_VARIATIONS), parse_mode='Markdown')

        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton('🎬 Solicitar Demo por WhatsApp', url=f'https://wa.me/{WHATSAPP_CONTACT}?text=Quiero%20ver%20una%20demo%20A2K'),
        )
        markup.add(types.InlineKeyboardButton('📋 Ver Catálogo', callback_data='catalog'))
        markup.add(types.InlineKeyboardButton('🔙 Menú Principal', callback_data='main_menu'))
        bot.send_message(chat_id, "👇 Agenda tu demo gratis ahora:", reply_markup=markup)
        return

    # ========== DEMO DE APP ESPECÍFICA ==========
    elif data.startswith('demo_'):
        app_id = data[5:]
        app = next((a for a in A2K_APPS if a['id'] == app_id), None)
        if app:
            set_state(user_id, 'demo_request', app_id)

            demo_msg = (
                f"🎥 *Demo - {app['icono']} {app['nombre']}*\n\n"
                f"¡Excelente! Quieres ver {app['nombre']} en acción 🎯\n\n"
            )

            if app.get('demo'):
                demo_msg += f"🌐 *Demo online:* [Probar ahora]({app['demo']})\n\n"

            demo_msg += (
                "📞 También puedes solicitar una demo en vivo por videollamada "
                "con el ingeniero Abigail. Te muestra todo el sistema, responde tus dudas "
                "y tú decides si es lo que necesitas.\n\n"
                "✅ Totalmente gratis\n"
                "✅ Sin compromiso\n\n"
                "👇 agenda tu demo ahora:"
            )

            try:
                bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=call.message.message_id,
                    text=demo_msg,
                    parse_mode='Markdown',
                    reply_markup=types.InlineKeyboardMarkup(),
                    disable_web_page_preview=True
                )
            except Exception:
                bot.send_message(chat_id, demo_msg, parse_mode='Markdown', disable_web_page_preview=True)

            markup = types.InlineKeyboardMarkup()
            markup.add(
                types.InlineKeyboardButton(
                    f'🎬 Demo {app["nombre"]} por WhatsApp',
                    url=get_whatsapp_demo_url(app['nombre'])
                )
            )
            if app.get('demo'):
                markup.add(types.InlineKeyboardButton('🌐 Ver Demo Online', url=app['demo']))
            markup.add(types.InlineKeyboardButton('📋 Catálogo', callback_data='catalog'))
            markup.add(types.InlineKeyboardButton('🔙 Menú', callback_data='main_menu'))
            bot.send_message(chat_id, "👇 Elige cómo prefieres ver la demo:", reply_markup=markup)
        return

    # ========== PRECIOS ==========
    elif data == 'precios':
        set_state(user_id, 'menu')
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton('📋 Catálogo', callback_data='catalog'),
            types.InlineKeyboardButton('💬 Comprar', url=f'https://wa.me/{WHATSAPP_CONTACT}?text=Quiero%20info%20de%20precios%20A2K'),
        )
        markup.add(types.InlineKeyboardButton('🔙 Menú Principal', callback_data='main_menu'))
        try:
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=call.message.message_id,
                text=build_pricing_message(),
                parse_mode='Markdown',
                reply_markup=markup,
                disable_web_page_preview=True
            )
        except Exception:
            bot.send_message(chat_id, build_pricing_message(), parse_mode='Markdown', reply_markup=markup,
                             disable_web_page_preview=True)
        return

    # ========== PAGOS ==========
    elif data == 'pagos':
        set_state(user_id, 'payment')
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton('📋 Datos Completos', callback_data='pagos_full'),
            types.InlineKeyboardButton('💬 WhatsApp', url=f'https://wa.me/{WHATSAPP_CONTACT}?text=Necesito%20datos%20de%20pago'),
        )
        markup.add(types.InlineKeyboardButton('🔙 Menú Principal', callback_data='main_menu'))
        try:
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=call.message.message_id,
                text=build_payment_message(),
                parse_mode='Markdown',
                reply_markup=markup
            )
        except Exception:
            bot.send_message(chat_id, build_payment_message(), parse_mode='Markdown', reply_markup=markup)
        return

    elif data == 'pagos_full':
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton('💬 WhatsApp', url=f'https://wa.me/{WHATSAPP_CONTACT}?text=Comprobante%20de%20pago%20enviado'),
        )
        markup.add(types.InlineKeyboardButton('🔙 Resumen', callback_data='pagos'))
        bot.send_message(
            chat_id,
            build_payment_full_message(),
            parse_mode='Markdown',
            reply_markup=markup
        )
        return

    # ========== CONTACTO ==========
    elif data == 'contacto':
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton('💬 WhatsApp', url=f'https://wa.me/{WHATSAPP_CONTACT}'),
            types.InlineKeyboardButton('🛒 Tienda Online', url=STORE_URL),
        )
        markup.add(types.InlineKeyboardButton('🔙 Menú Principal', callback_data='main_menu'))
        try:
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=call.message.message_id,
                text=build_contact_message(),
                parse_mode='Markdown',
                reply_markup=markup,
                disable_web_page_preview=True
            )
        except Exception:
            bot.send_message(chat_id, build_contact_message(), parse_mode='Markdown', reply_markup=markup,
                             disable_web_page_preview=True)
        return

    # ========== OTROS PRODUCTOS (Amazon/AliExpress) ==========
    elif data == 'otros_productos':
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton('🇪🇸 Amazon España', callback_data='amazon_es'),
            types.InlineKeyboardButton('🇺🇸 Amazon USA', callback_data='amazon_usa'),
            types.InlineKeyboardButton('🇨🇳 AliExpress', callback_data='aliexpress'),
        )
        markup.add(types.InlineKeyboardButton('🔙 Menú Principal', callback_data='main_menu'))
        try:
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=call.message.message_id,
                text=(
                    "🛒 *Otros Productos*\n\n"
                    "Además de nuestras aplicaciones de gestión, también ofrecemos "
                    "productos seleccionados a través de nuestras tiendas asociadas:\n\n"
                    "🇪🇸 Amazon España - Envío desde España\n"
                    "🇺🇸 Amazon USA - Envío desde Estados Unidos\n"
                    "🇨🇳 AliExpress - Mejores precios directos\n\n"
                    "👇 Selecciona una tienda:"
                ),
                parse_mode='Markdown',
                reply_markup=markup
            )
        except Exception:
            bot.send_message(chat_id, "🛒 *Otros Productos*\n\nSelecciona una tienda 👇",
                             parse_mode='Markdown', reply_markup=markup)
        return

    # ========== AMAZON ESPAÑA ==========
    elif data == 'amazon_es':
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton('📱 Tecnología', callback_data='aes_tech'),
            types.InlineKeyboardButton('💄 Belleza', callback_data='aes_belleza'),
            types.InlineKeyboardButton('🏠 Hogar', callback_data='aes_hogar'),
            types.InlineKeyboardButton('💪 Fitness', callback_data='aes_fitness'),
        )
        markup.add(types.InlineKeyboardButton('🔙 Volver', callback_data='otros_productos'))
        try:
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=call.message.message_id,
                text="🇪🇸 *AMAZON ESPAÑA*\n\nSelecciona una categoría:",
                parse_mode='Markdown',
                reply_markup=markup
            )
        except Exception:
            bot.send_message(chat_id, "🇪🇸 *AMAZON ESPAÑA*\n\nSelecciona una categoría:",
                             parse_mode='Markdown', reply_markup=markup)
        return

    elif data.startswith('aes_'):
        cat = data[4:]
        productos = AMAZON_ES.get(cat, [])
        cat_names = {'tech': '📱 Tecnología', 'belleza': '💄 Belleza', 'hogar': '🏠 Hogar', 'fitness': '💪 Fitness'}
        cat_name = cat_names.get(cat, '📦 Productos')

        texto = f"🇪🇸 *{cat_name} - Amazon España*\n\n"
        for p in productos:
            texto += f"• {p['nombre']}\n  🔗 [Ver producto]({p['link']})\n\n"

        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('🔙 Volver a categorías', callback_data='amazon_es'))
        markup.add(types.InlineKeyboardButton('🔙 Menú Principal', callback_data='main_menu'))
        try:
            bot.edit_message_text(texto, chat_id, call.message.message_id, parse_mode='Markdown', reply_markup=markup,
                                  disable_web_page_preview=True)
        except Exception:
            bot.send_message(chat_id, texto, parse_mode='Markdown', reply_markup=markup,
                             disable_web_page_preview=True)
        return

    # ========== AMAZON USA ==========
    elif data == 'amazon_usa':
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton('📱 Tech', callback_data='aus_tech'),
            types.InlineKeyboardButton('🏠 Hogar', callback_data='aus_hogar'),
            types.InlineKeyboardButton('💪 Fitness', callback_data='aus_fitness'),
            types.InlineKeyboardButton('🍽️ Cocina', callback_data='aus_cocina'),
            types.InlineKeyboardButton('💄 Belleza', callback_data='aus_belleza'),
        )
        markup.add(types.InlineKeyboardButton('🔙 Volver', callback_data='otros_productos'))
        try:
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=call.message.message_id,
                text="🇺🇸 *AMAZON USA*\n\nSelecciona una categoría:",
                parse_mode='Markdown',
                reply_markup=markup
            )
        except Exception:
            bot.send_message(chat_id, "🇺🇸 *AMAZON USA*\n\nSelecciona una categoría:",
                             parse_mode='Markdown', reply_markup=markup)
        return

    elif data.startswith('aus_'):
        cat = data[4:]
        productos = AMAZON_USA.get(cat, [])
        cat_names = {'tech': '📱 Tecnología', 'hogar': '🏠 Hogar', 'fitness': '💪 Fitness',
                     'cocina': '🍽️ Cocina', 'belleza': '💄 Belleza'}
        cat_name = cat_names.get(cat, '📦 Productos')

        texto = f"🇺🇸 *{cat_name} - Amazon USA*\n\n"
        for p in productos:
            texto += f"• {p['nombre']}\n  🔗 [Ver producto]({p['link']})\n\n"

        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('🔙 Volver a categorías', callback_data='amazon_usa'))
        markup.add(types.InlineKeyboardButton('🔙 Menú Principal', callback_data='main_menu'))
        try:
            bot.edit_message_text(texto, chat_id, call.message.message_id, parse_mode='Markdown', reply_markup=markup,
                                  disable_web_page_preview=True)
        except Exception:
            bot.send_message(chat_id, texto, parse_mode='Markdown', reply_markup=markup,
                             disable_web_page_preview=True)
        return

    # ========== ALIEXPRESS ==========
    elif data == 'aliexpress':
        texto = "🇨🇳 *ALIEXPRESS - Ofertas Directas*\n\n"
        for p in ALIEXPRESS:
            texto += f"• {p['nombre']}\n  🔗 [Ver producto]({p['link']})\n\n"

        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('🔙 Volver', callback_data='otros_productos'))
        markup.add(types.InlineKeyboardButton('🔙 Menú Principal', callback_data='main_menu'))
        try:
            bot.edit_message_text(texto, chat_id, call.message.message_id, parse_mode='Markdown', reply_markup=markup,
                                  disable_web_page_preview=True)
        except Exception:
            bot.send_message(chat_id, texto, parse_mode='Markdown', reply_markup=markup,
                             disable_web_page_preview=True)
        return

    # ========== VOLVER AL CATÁLOGO ==========
    elif data == 'back_to_catalog':
        set_state(user_id, 'catalog')
        try:
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=call.message.message_id,
                text=build_catalog_message(),
                parse_mode='Markdown',
                reply_markup=get_catalog_inline_keyboard(),
                disable_web_page_preview=True
            )
        except Exception:
            bot.send_message(
                chat_id,
                build_catalog_message(),
                parse_mode='Markdown',
                reply_markup=get_catalog_inline_keyboard(),
                disable_web_page_preview=True
            )
        return

    # ========== CALLBACK NO RECONOCIDO ==========
    else:
        logger.warning(f"Callback no reconocido: {data} de @{call.from_user.username}")
        bot.send_message(
            chat_id,
            "Hmm, ese botón ya no está disponible 🤔 Pero no te preocupes, aquí tienes el menú principal 👇",
            parse_mode='Markdown'
        )
        simulate_typing(chat_id, 0.5)
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton('📋 Catálogo', callback_data='catalog'),
            types.InlineKeyboardButton('🏠 Menú', callback_data='main_menu'),
        )
        bot.send_message(chat_id, "¿Qué prefieres?", reply_markup=markup)


# ==================== ERROR HANDLER ====================

@bot.message_handler(func=lambda message: True, content_types=['photo', 'video', 'audio', 'document', 'sticker', 'voice'])
def handle_non_text(message):
    """Maneja mensajes que no son texto."""
    chat_id = message.chat.id
    user_id = message.from_user.id

    logger.info(f"NO_TEXTO - @{message.from_user.username or 'unknown'}: tipo={message.content_type}")

    simulate_typing(chat_id, 1.0)

    responses = [
        "Jeje, me encanta que me mandes eso 😄 pero soy un bot de texto por ahora. "
        "Dime, ¿qué necesitas? ¿Quieres ver el catálogo, precios, o alguna app en particular? 💡",
        "¡Bueno! Por ahora solo puedo procesar texto, pero no te preocupes 🤓. "
        "Pregúntame lo que quieras sobre nuestras aplicaciones A2K y con gusto te ayudo.",
        "Mm, no puedo procesar eso todavía 😅 Pero cuéntame, ¿buscas alguna app en específico? "
        "Tengo sistemas para barberías, ferreterías, bodegas y más 🛒",
    ]

    bot.send_message(chat_id, random.choice(responses), parse_mode='Markdown',
                     reply_markup=get_main_menu_keyboard())


def error_handler(exception):
    """Manejo global de errores."""
    logger.error(f"Error: {exception}", exc_info=True)


bot.register_error_handler(error_handler)

# ==================== INICIO ====================

if __name__ == '__main__':
    print("=" * 55)
    print("  ✨ A2K DIGITAL STUDIO - BOT TELEGRAM v3.0 ✨")
    print("  Asistente de Ventas Profesional")
    print("=" * 55)
    print(f"  📱 Apps en catálogo: {len(A2K_APPS)}")
    print(f"  💰 Precio estándar: $25 USD")
    print(f"  🛒 Tienda: {STORE_URL}")
    print(f"  💬 WhatsApp: +{WHATSAPP_CONTACT}")
    print(f"  🏦 Bancos Nacionales: {len(BANCOS_NAC)}")
    print(f"  🏦 Bancos Internacionales: {len(BANCOS_INT)}")
    print(f"  🇪🇸 Amazon España: {sum(len(v) for v in AMAZON_ES.values())} productos")
    print(f"  🇺🇸 Amazon USA: {sum(len(v) for v in AMAZON_USA.values())} productos")
    print(f"  🇨🇳 AliExpress: {len(ALIEXPRESS)} productos")
    print("=" * 55)
    print("  ⏰ Iniciado: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("  🟢 Estado: ACTIVO - Esperando mensajes...")
    print("=" * 55)

    try:
        bot.infinity_polling(
            timeout=60,
            long_polling_timeout=60,
            none_stop=True
        )
    except KeyboardInterrupt:
        print("\n  ⏹️  Bot detenido manualmente.")
        print("=" * 55)
    except Exception as e:
        logger.critical(f"Error crítico: {e}", exc_info=True)
        print(f"\n  ❌ Error crítico: {e}")
        print("=" * 55)
