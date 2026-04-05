#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A2K Digital Studio - Asistente de Ventas por Telegram v5.0
Bot experto en marketing conversacional que vende a través de charla humana.
Estilo venezolano, persuasivo, con flujo de venta profesional tipo WhatsApp.

Mejoras v5.0:
- Flujo conversacional tipo WhatsApp (Abi - experto en marketing)
- State machine avanzado por usuario
- 3 pitches de venta por cada app (27 totales)
- Manejo de objeciones con 5 categorías
- Cierres de venta persuasivos
- Tienda online integrada en TODA la conversación
- Detección de hora del día para saludos
- Detección de usuarios recurrentes
- Seguimiento de ventas/leads en ventas_telegram.txt
- Follow-ups de venta automáticos
- Enlaces BODEGA PRO (demo + licencia)
"""

import telebot
from telebot import types
import time
import random
import logging
import threading
import urllib.parse
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

# URLs
STORE_URL = 'https://tiendadigitalaipro.github.io/a2k-digital-studio/'
WHATSAPP_CONTACT = '584164117331'
BODEGA_PRO_DEMO_URL = 'https://tiendadigitalaipro.github.io/bodega-demo/formulario-demo-bodega.html'
BODEGA_PRO_LICENCIA_URL = 'https://tiendadigitalaipro.github.io/bodega-demo/formulario-licencia-pro-bodega.html'
VENTAS_FILE = 'ventas_telegram.txt'

# ==================== STATE MACHINE ====================

user_states = {}
user_interaction_counts = {}
user_last_responses = {}

def get_state(user_id):
    return user_states.get(user_id, {
        'flow': 'nuevo',
        'app_interes': None,
        'negocio': None,
        'interacciones': 0,
        'retorno': False,
        'ultima_objecion': None,
        'pitch_visto': {}
    })

def set_state(user_id, flow, **kwargs):
    state = get_state(user_id)
    state['flow'] = flow
    for key, val in kwargs.items():
        if key in state:
            state[key] = val
    user_states[user_id] = state

def track_interaction(user_id):
    user_interaction_counts[user_id] = user_interaction_counts.get(user_id, 0) + 1
    return user_interaction_counts[user_id]

def get_interaction_count(user_id):
    return user_interaction_counts.get(user_id, 0)

def is_returning_user(user_id):
    return user_interaction_counts.get(user_id, 0) > 1

def mark_pitch_seen(user_id, app_id):
    state = get_state(user_id)
    if 'pitch_visto' not in state:
        state['pitch_visto'] = {}
    state['pitch_visto'][app_id] = state['pitch_visto'].get(app_id, 0) + 1
    user_states[user_id] = state

def get_pitch_count(user_id, app_id):
    state = get_state(user_id)
    return state.get('pitch_visto', {}).get(app_id, 0)

def get_time_greeting():
    """Retorna saludo según la hora del día."""
    hour = datetime.now().hour
    if 6 <= hour < 12:
        return 'buenos_dia'
    elif 12 <= hour < 18:
        return 'buenas_tardes'
    elif 18 <= hour < 22:
        return 'buenas_noches'
    else:
        return 'buenas_noches'

# ==================== SEGUIMIENTO DE VENTAS ====================

def log_venta_lead(username, user_id, app_interes, mensaje, fase='descubrimiento'):
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = (
            f"[{timestamp}] | User: @{username or 'sin_username'} | "
            f"ID: {user_id} | App: {app_interes or 'general'} | "
            f"Fase: {fase} | Mensaje: {mensaje}\n"
        )
        with open(VENTAS_FILE, 'a', encoding='utf-8') as f:
            f.write(line)
        logger.info(f"LEAD - @{username}: {app_interes} [{fase}] - {mensaje}")
    except Exception as e:
        logger.error(f"Error guardando lead: {e}")

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
        'keywords': ['fruteria', 'frutería', 'frutas', 'verdura', 'verduría', 'hortaliza', 'fresh']
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
        'keywords': ['cloud', 'nube', 'bodega cloud', 'sincronizar', 'sincronización', 'online']
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

# ==================== PHASE 1: GREETING & DISCOVERY ====================

GREETINGS_MORNING = [
    "¡Buenos días! ☀️ Me llamo Abi y soy tu asistente de A2K Digital Studio. ¿Cómo amaneciste hoy? 😊",
    "¡Buenos días! 🌅 Soy Abi, de A2K Digital Studio. Qué gusto saludarte tan temprano. Cuéntame, ¿en qué te puedo ayudar?",
    "¡Buenos días hermano! ☀️ Aquí Abi, lista para ayudarte. ¿Tienes algún negocio? Seguro tengo algo que te va a servir 💪",
    "¡Muy buenos días! 😃 Abi te saluda desde A2K Digital Studio. ¿Qué necesitas hoy? Estoy para servirte.",
    "¡Buen día! ☀️ Soy Abi de A2K Digital Studio. Me alegra que me escribas. ¿A qué te dedicas? Quizás pueda ayudarte con tu negocio.",
]

GREETINGS_AFTERNOON = [
    "¡Buenas tardes! 😊 Soy Abi de A2K Digital Studio. ¿Cómo te va hoy?",
    "¡Buenas tardes! 🌤️ Aquí Abi, tu asistente de confianza en A2K Digital Studio. ¿Qué necesitas?",
    "¡Hey! Buenas tardes 😄 Soy Abi, ¿cómo está tu día? Si tienes un negocio, tengo justo lo que necesitas.",
    "¡Buenas tardes! 👋 Abi de A2K Digital Studio a tu servicio. ¿Tienes un negocio? Te tengo la solución ideal.",
    "¡Qué buenas tardes! 🤙 Soy Abi, tu experta en soluciones tecnológicas. Cuéntame, ¿en qué te puedo ayudar hoy?",
]

GREETINGS_EVENING = [
    "¡Buenas noches! 🌙 Soy Abi de A2K Digital Studio. ¿Cómo te fue hoy? Aún estoy aquí para ayudarte.",
    "¡Buenas noches! ✨ Soy Abi, de A2K Digital Studio. Sé que es tarde, pero si necesitas algo para tu negocio, aquí estoy.",
    "¡Buenas noches hermano! 🌜 Aquí Abi. ¿Necesitas algo para tu negocio? Estoy despierta y lista para ayudarte.",
    "¡Buenas noches! 😊 Soy Abi de A2K. ¿En qué te puedo ayudar? Si tienes dudas sobre algún sistema, ahora es buen momento.",
    "¡Buenas noches! 🌟 Abi te saluda. Sé que es tarde, pero tu negocio no espera. ¿Te cuento qué tenemos?",
]

GREETINGS_RETURNING = [
    "¡Qué gusto verte de vuelta! 😊 Ya te conozco, somos como viejos amigos jajaja. Soy Abi de A2K Digital Studio. ¿Qué tal está todo?",
    "¡Hey! Tú de nuevo por aquí! 👋 Me alegra mucho, aquí está Abi lista para ayudarte. ¿Qué novedades tienes?",
    "¡Hola de nuevo! 😄 Qué gusto que regreses. Soy Abi de A2K Digital Studio. ¿Ya tienes algo en mente o quieres que te muestre las novedades?",
    "¡Bienvenido de vuelta! 🙌 Me hace feliz verte otra vez. Abi está aquí para ti. ¿Qué necesitas hoy?",
    "¡Epa! Otra vez tú! 😆 Qué bueno que regreses. Aquí Abi, tu asistente de siempre en A2K Digital Studio.",
]

GREETINGS_GENERIC = [
    "¡Hola! 😊 Soy Abi, tu asistente de A2K Digital Studio. Estoy aquí para ayudarte a encontrar la solución perfecta para tu negocio.",
    "¡Hola! 👋 Soy Abi de A2K Digital Studio. ¿Tienes un negocio? Te tengo algo que te va a encantar.",
    "¡Saludos! 😄 Me llamo Abi y trabajo en A2K Digital Studio. Creamos sistemas que hacen que tu negocio trabaje solo.",
    "¡Hey! 😃 Bienvenido a A2K Digital Studio. Soy Abi, tu experta en soluciones para negocios. ¿En qué te puedo ayudar?",
    "¡Qué tal! ✨ Soy Abi de A2K Digital Studio. Si tienes un negocio, estoy segura de que tenemos algo para ti.",
]

def get_greeting(user_id):
    """Obtiene el saludo apropiado según hora y si es usuario recurrente."""
    if is_returning_user(user_id):
        return random.choice(GREETINGS_RETURNING)
    time_g = get_time_greeting()
    if time_g == 'buenos_dia':
        return random.choice(GREETINGS_MORNING)
    elif time_g == 'buenas_tardes':
        return random.choice(GREETINGS_AFTERNOON)
    else:
        return random.choice(GREETINGS_EVENING)

# ==================== PHASE 2: BUSINESS DISCOVERY ====================

PREGUNTAS_NEGOCIO = [
    'Cuéntame, ¿qué tipo de negocio tienes? Así te puedo recomendar la solución perfecta 💪',
    '¿Me cuentas qué tipo de negocio manejas? Tenemos sistemas para diferentes rubros 😊',
    'Dime, ¿a qué te dedicas? Quiero recomendarte algo que realmente te sirva 😄',
    '¿Qué tipo de negocio tienes? Mira, tenemos apps para barberías, ferreterías, bodegas, farmacias y más. Cuéntame y te digo cuál es la tuya 🎯',
    'Oye, ¿tienes un negocio propio? Si es así, dime de qué trata y te consigo la herramienta ideal para llevarlo al siguiente nivel 🚀',
    '¿Manejas algún negocio? En A2K Digital Studio tenemos 9 aplicaciones profesionales. Solo dime tu rubro y te recomiendo la perfecta 💡',
    'Si me dices qué tipo de negocio tienes, puedo ahorrarte horas de trabajo manual 😏 Te sorprendería lo que tenemos.',
    '¿Eres dueño de algún negocio? Cuenta conmigo, tengo la app perfecta esperándote 🏆',
    '¿A qué te dedicas profesionalmente? Quiero ayudarte a potenciar tu negocio con tecnología de verdad 🔥',
    '¿Tienes algún negocio o emprendimiento? Soy experta en encontrar la herramienta ideal para cada rubro. ¡Dime y te asesoro gratis! 😎',
]

PREGUNTAS_NEGOCIO_FOLLOWUP = [
    'Mmm, déjame entender mejor... ¿vendes productos, ofreces servicios, o ambas cosas? 🤔',
    'Ajá, y ¿es un negocio pequeño, mediano o ya tienes varias sucursales? Así te recomiendo mejor 💡',
    '¿Y cómo llevas el control actualmente? ¿Con cuaderno, Excel, o ya usas algún sistema? 😄',
    'Interesante... ¿y cuál es el mayor problema que tienes hoy con tu negocio? Tal vez pueda ayudarte con eso 🎯',
    '¿Y cuánto tiempo llevas con el negocio? Eso me ayuda a entender qué necesitas 📊',
    '¿Tienes empleados o lo manejas solo/a? Eso cambia un poco la recomendación 👥',
    'Mira, cuéntame más sobre tu día a día en el negocio. ¿Qué es lo que más te complica? ✨',
    '¿Y qué es lo primero que harías si pudieras automatizar algo de tu negocio? 🔧',
]

# ==================== PHASE 3: SALES PITCHES (3 por app) ====================

SALES_PITCHES = {
    'barberia': [
        # Pitch 1
        (
            '¡Perfecto! Tengo algo que te va a encantar 💈\n\n'
            '*Barbería Pro* es un sistema completo diseñado exclusivamente para barberos como tú. '
            'Imagínate tener todo esto:\n\n'
            '✅ *Turnos organizados* — nunca más se te cruza un cliente\n'
            '✅ *Historial completo de clientes* — sabes qué corte le hicieron la última vez\n'
            '✅ *Caja y reportes diarios* — sabes exactamente cuánto ganaste al día\n'
            '✅ *Facturas profesionales* — tu negocio se ve serio y profesional\n'
            '✅ *Modo oscuro incluido* — porque el estilo importa 💅\n\n'
            'Lo mejor es que más de 50 barberos ya lo usan en Venezuela y están encantados 💪\n\n'
            '¿Sabes lo que más les gusta? Que se pagó sola en el primer mes. '
            'Dejaron de perder clientes por desorganización y empezaron a ganar más.\n\n'
            '¿Te gustaría ver cómo funciona? 🎥'
        ),
        # Pitch 2
        (
            '¡Oye! Sé exactamente lo que necesitas para tu barbería 💈🔥\n\n'
            '¿Te pasa que los clientes llegan y no sabes quién sigue? '
            '¿O que al final del día no sabes cuánto ganaste de verdad? '
            'Eso se acaba con *Barbería Pro*.\n\n'
            'Esto es lo que hace por ti:\n\n'
            '📅 *Agenda inteligente* — cada cliente tiene su turno, sin confusiones\n'
            '💇 *Ficha de cada cliente* — nombre, corte favorito, fecha de última visita\n'
            '💰 *Caja cerrada* — entras, cobras, sales y sabes exactamente tu ganancia\n'
            '📊 *Reportes semanales* — ves si estás creciendo o estancado\n'
            '🧾 *Facturas automáticas* — para los clientes que las necesitan\n\n'
            'Más de 50 barberos ya confiaron en nosotros y sus negocios crecieron un 40% en promedio 📈\n\n'
            'Por solo *$25 USD*, una sola vez. Sin mensualidades. Sin letra pequeña.\n\n'
            '¿Te animas a probarla? 🎯'
        ),
        # Pitch 3
        (
            'Mira, voy a ser directa contigo porque sé que los barberos no pierden tiempo 💈😎\n\n'
            '*Barbería Pro* no es solo un software, es tu socio silencioso.\n\n'
            'Piensa en esto:\n\n'
            '❌ *Sin sistema:* Pierdes clientes porque no organizas bien los turnos, '
            'no sabes cuánto vendiste, y te pasas horas haciendo cuentas.\n\n'
            '✅ *Con Barbería Pro:* Automatizas turnos, llevas el control de cada cliente, '
            'cierras caja en 2 minutos y generas reportes con un clic.\n\n'
            '¿La inversión? *$25 USD*. Una. Sola. Vez.\n\n'
            'Un corte de barba cuesta entre $5 y $15. Con solo 2-3 clientes extras al mes '
            'que no perderías por mala organización, ya pagaste la app.\n\n'
            'Más de 50 barberos en Venezuela ya lo usan. ¿Vas a ser el último en modernizarte? 😏\n\n'
            'Da el paso, te lo vas a agradecer. ¿Vamos? 👇'
        ),
    ],
    'nail': [
        # Pitch 1
        (
            '¡Genial! Sé que el mundo de las uñas es competitivo y tú necesitas destacarte 💅✨\n\n'
            '*Nail Studio Pro* es el sistema que necesitan las profesionales como tú.\n\n'
            'Mira lo que incluye:\n\n'
            '📅 *Agenda inteligente* — tus clientas reservan y tú no pierdes ninguna cita\n'
            '👩 *Ficha completa de clientas* — sabes qué diseño le hicieron, qué materiales usaron y cuándo volver\n'
            '💅 *Catálogo de servicios* — organizas tus manicuras, pedicuras, diseños con precios claros\n'
            '📦 *Control de materiales* — nunca más te quedas sin esmalte a mitad del día\n'
            '💵 *Caja dual ($ y Bs)* — porque en Venezuela cobramos en ambas monedas\n'
            '📊 *Reportes por período* — sabes cuál es tu servicio más vendido\n\n'
            'Más de 50 nail studios ya confían en este sistema 💪\n\n'
            '¿Te gustaría ver la demo? Puedes probarla antes de decidir 🎥'
        ),
        # Pitch 2
        (
            '¡Amiga! Si tienes un nail studio, esto es para ti 💅🔥\n\n'
            'Sé los problemas que enfrentas:\n\n'
            '😰 Clientas que no vuelven porque no les das seguimiento\n'
            '😰 No sabes cuánto material gastas vs. cuánto cobras\n'
            '😰 La caja es un desastre entre dólares y bolívares\n'
            '😰 Pierdes tiempo buscando qué diseño le hiciste a cada clienta\n\n'
            '*Nail Studio Pro* resuelve TODO eso:\n\n'
            '✅ *Historial por clienta* — nombre, diseño, fecha, materiales usados\n'
            '✅ *Caja doble* — manejas dólares y bolívares sin volverte loca\n'
            '✅ *Inventario de materiales* — control exacto de lo que entra y sale\n'
            '✅ *Agenda organizada* — nunca más una clienta sin cita\n\n'
            'Por *$25 USD*, una sola vez. Tu inversión se recupera con 2-3 clientas nuevas 💰\n\n'
            'Más de 50 estudios de belleza ya lo usan. ¿Te quedas fuera? 😊'
        ),
        # Pitch 3
        (
            '¿Sabes cuál es la diferencia entre un nail studio que crece y uno que se estanca? '
            'La organización 💅🎯\n\n'
            '*Nail Studio Pro* fue diseñado por y para profesionales de la belleza. No es un '
            'programa genérico, es TU herramienta.\n\n'
            '¿Qué cambia cuando lo usas?\n\n'
            '📈 Tus clientas vuelven porque les das un servicio profesional con factura e historial\n'
            '📈 Dejas de perder dinero en materiales porque ahora llevas control\n'
            '📈 Sabes exactamente cuánto ganas en dólares y en bolívares\n'
            '📈 Tu agenda se llena porque nunca olvidas dar seguimiento\n\n'
            'Son *$25 USD*, un pago único. Piensa en esto: un set de gel cuesta $15-20. '
            'Por el precio de un set, tienes un sistema que te va a generar muchísimo más dinero 💎\n\n'
            'Más de 50 profesionales ya lo tienen. ¿Listas para unirte? 👇'
        ),
    ],
    'repuestos': [
        # Pitch 1
        (
            '¡Perfecto! Los negocios de repuestos de motos están en auge 🏍️💪\n\n'
            '*Repuestos de Motos Pro* es el sistema que te va a organizar la vida.\n\n'
            '¿Te suena esto?\n\n'
            '❌ Un cliente pregunta por una pieza y tardas 10 minutos en encontrarla\n'
            '❌ No sabes cuántas piezas tienes en stock hasta que se acaban\n'
            '❌ Al cierre del mes no tienes idea de cuánto vendiste realmente\n\n'
            'Con este sistema, todo eso cambia:\n\n'
            '🔍 *Catálogo completo de repuestos* — buscas en segundos, no en minutos\n'
            '📦 *Inventario en tiempo real* — sabes exactamente qué tienes y qué te falta\n'
            '🛒 *Ventas rápidas* — registras una venta en menos de 30 segundos\n'
            '📊 *Reportes de movimiento* — ves qué se vende más y qué se estanca\n'
            '👥 *Base de clientes y proveedores* — todo organizado\n\n'
            'Más de 50 tiendas de repuestos ya lo usan en Venezuela 🇻🇪\n\n'
            '¿Quieres ver cómo funciona? 🎥'
        ),
        # Pitch 2
        (
            '¡Qué bueno! El negocio de repuestos de motos es uno de los que más crece 🏍️🔥\n\n'
            'Pero oye, seré honesta: si no tienes un buen sistema, estás perdiendo dinero. '
            'Te lo digo con cariño 💪\n\n'
            '*Repuestos de Motos Pro* te da:\n\n'
            '✅ *Catálogo digital* — cada pieza con código, precio y stock actualizado\n'
            '✅ *Alertas de stock bajo* — te avisa antes de que se te acabe algo\n'
            '✅ *Ventas con búsqueda rápida* — escribes parte del nombre y aparece\n'
            '✅ *Control de proveedores* — sabes a quién le debes y quién te debe\n'
            '✅ *Reportes detallados* — al final del mes sabes exactamente tu ganancia\n'
            '✅ *Gestión de precios* — ajustas precios por mayor o detal\n\n'
            'Por *$25 USD*, una sola vez. Una sola pieza que vendas de más por tener '
            'buen stock y ya te pagaste el sistema 💰\n\n'
            '¿Te animas? 🎯'
        ),
        # Pitch 3
        (
            'Vamos a hablar de números, que es lo que importa 🏍️📊\n\n'
            '¿Cuántas ventas pierdes al mes porque no encuentras una pieza rápido? '
            '¿Cuántas veces un cliente se va a otra tienda porque tú no sabías si tenías stock?\n\n'
            '*Repuestos de Motos Pro* elimina ese problema completamente:\n\n'
            '⚡ *Búsqueda instantánea* — escribes y encuentras la pieza en 2 segundos\n'
            '⚡ *Stock preciso* — sabes al momento cuántas unidades tienes\n'
            '⚡ *Ventas en 30 segundos* — scan, cobras, listo\n'
            '⚡ *Reportes que te dan poder* — sabes qué negociar con proveedores\n\n'
            'Más de 50 comercios de motos ya modernizaron su operación. El promedio: '
            'aumentaron sus ventas un 30% en el primer mes por mejor atención al cliente 📈\n\n'
            'Todo por *$25 USD*. Una. Sola. Vez. Sin suscripciones.\n\n'
            'Tu negocio merece herramientas profesionales. ¿Estás listo? 👇'
        ),
    ],
    'ferreteria': [
        # Pitch 1
        (
            '¡Excelente! Las ferreterías son uno de los negocios más rentables si están bien organizados 🔧💰\n\n'
            '*Ferretería A2K Pro* fue creado para que tu ferretería funcione como una máquina.\n\n'
            'Esto es lo que te ofrece:\n\n'
            '📦 *Inventario completo* — cada tornillo, herramienta y material registrado\n'
            '🛒 *Punto de venta rápido* — facturas en segundos, no en minutos\n'
            '🧾 *Facturación profesional* — tus clientes te ven como un negocio serio\n'
            '🚚 *Control de proveedores* — sabes qué pedir, a quién y cuándo\n'
            '📊 *Reportes financieros* — ganancias, costos, utilidades claras\n'
            '👥 *Base de clientes* — para compras frecuentes y crédito\n\n'
            'Más de 50 ferreterías en Venezuela ya confían en nosotros 💪\n\n'
            '¿Te gustaría ver la demo? Estoy segura de que te va a gustar 🔥'
        ),
        # Pitch 2
        (
            '¿Sabías que la mayoría de las ferreterías pierden entre 10-15% de sus ganancias '
            'por mala gestión de inventario? 🔧😱\n\n'
            '*Ferretería A2K Pro* soluciona eso y más:\n\n'
            '✅ *No más productos perdidos* — cada artículo tiene su registro exacto\n'
            '✅ *No más ventas sin registro* — cada venta queda documentada\n'
            '✅ *No más confusiones con proveedores* — sabes qué pediste y qué recibiste\n'
            '✅ *No más cierres de mes dolorosos* — los reportes se generan solos\n\n'
            'Imagínate esto: al final del mes, con un clic, sabes:\n'
            '• Cuánto vendiste\n'
            '• Qué productos se venden más\n'
            '• Cuál es tu margen de ganancia\n'
            '• A qué proveedores les debes\n\n'
            'Todo por *$25 USD*. Tu ferretería vale más que eso. Invierte en ella 💎'
        ),
        # Pitch 3
        (
            'Hermano, si tienes una ferretería, necesitas escuchar esto 🔧💪\n\n'
            'Yo conozco el negocio. Sé que manejas cientos de productos diferentes, '
            'que tienes varios proveedores, y que el inventario puede ser una pesadilla.\n\n'
            '*Ferretería A2K Pro* nació para simplificarte la vida:\n\n'
            '🎯 *Vende más rápido* — buscas cualquier producto en segundos\n'
            '🎯 *Pierde menos* — control exacto de cada pieza en stock\n'
            '🎯 *Gana más* — reportes que te muestran dónde está tu dinero\n'
            '🎯 *Crece más* — con datos, tomas mejores decisiones\n\n'
            'Más de 50 ferreterías ya lo usan y el resultado es claro: '
            'menos errores, menos pérdidas, más ganancias 📈\n\n'
            'Son $25 USD. Una vez. Para siempre.\n\n'
            '¿Vas a dejar que la competencia se adelante? 😏'
        ),
    ],
    'bodega_descarga': [
        # Pitch 1
        (
            '¡Ahora sí estamos hablando! Las bodegas y abastos son el corazón de cada comunidad 📦💪\n\n'
            '*Bodega Descarga Pro* es el sistema más completo que hemos creado. '
            'Y tiene algo que ningún otro tiene: *funciona SIN internet* 📴\n\n'
            '¿Te suena esto?\n\n'
            '☔ Se va la luz y no puedes cobrar\n'
            '📵 Se cae el internet y tu punto de venta se bloquea\n'
            '❌ Los clientes se van porque no puedes facturar\n\n'
            'Con *Bodega Descarga Pro* eso NO pasa:\n\n'
            '✅ *Funciona OFFLINE* — sigue vendiendo sin internet ni luz (con UPS)\n'
            '✅ *Inventario inteligente* — control total de cada producto\n'
            '✅ *Todos los métodos de pago VE* — bolívares, dólares, punto de venta, pago móvil\n'
            '✅ *Gestión de fiados* — nunca más pierdes el registro de quién te debe\n'
            '✅ *Escáner de códigos* — agilizas las ventas al máximo\n'
            '✅ *Reportes detallados* — sabes exactamente cómo va tu negocio\n\n'
            'Más de 50 bodegas ya lo usan en Venezuela. ¿Te unes? 🎯'
        ),
        # Pitch 2
        (
            'Oye, si manejas una bodega o abasto, NECESITAS esto 📦🔥\n\n'
            'Sé lo difícil que es: cientos de productos, clientes que piden fiado, '
            'el internet que se va cuando más lo necesitas... 🤦\n\n'
            '*Bodega Descarga Pro* fue diseñado pensando en TI:\n\n'
            '📴 *OFFLINE primero* — funciona sin internet, sincroniza cuando vuelve\n'
            '💳 *Todos los pagos* — efectivo, tarjeta, pago móvil, Zelle, transferencia\n'
            '👥 *Fiados organizados* — sabes quién te debe y cuánto\n'
            '📦 *Stock en tiempo real* — nunca más vendes algo que no tienes\n'
            '🧾 *Facturas automáticas* — profesionales y rápidas\n'
            '📊 *Reportes completos* — diarios, semanales, mensuales\n\n'
            'Y lo mejor: *$25 USD*, un solo pago. Para siempre.\n\n'
            '¿Sabías que el 90% de nuestros clientes de bodegas recuperaron la inversión '
            'en la primera semana? Solo por dejar de perder ventas cuando se cae el internet 📈'
        ),
        # Pitch 3
        (
            '¡Hablemos de bodegas! 📦 Yo sé que ese negocio no perdona.\n\n'
            'Un día sin sistema es un día perdiendo dinero. Y en Venezuela, '
            '¿cuántas veces se te cae el internet? 📵\n\n'
            '*Bodega Descarga Pro* tiene la solución:\n\n'
            '⚡ *OFFLINE nativo* — no depende de internet para funcionar\n'
            '⚡ *Venta súper rápida* — escanea, cobra, factura en 10 segundos\n'
            '⚡ *Multi-método de pago* — todos los que existen en Venezuela\n'
            '⚡ *Control de fiados* — registro exacto de cada crédito\n'
            '⚡ *Inventario automático* — se actualiza con cada venta\n\n'
            'Los números hablan solos:\n'
            '• 50+ bodegas usándolo en Venezuela\n'
            '• 30% más ventas por tener sistema confiable\n'
            '• 0% de quejas por caídas del sistema\n\n'
            '*$25 USD*, un pago único. ¿Cuánto pierdes en un día sin poder cobrar? '
            'Esa es la respuesta a si vale la pena 💰\n\n'
            '¿Vamos? 👇'
        ),
    ],
    'mercado_logic': [
        # Pitch 1
        (
            '¡Wow! Si manejas un negocio de gran escala, necesitas herramientas de gran escala 🛒🏆\n\n'
            '*MERCADO LOGIC PRO* es nuestro sistema más avanzado. Es el Ferrari de los puntos de venta.\n\n'
            'Esto es lo que incluye:\n\n'
            '🔒 *Sistema IRON LOCK v2* — seguridad de nivel empresarial para tu licencia\n'
            '🛒 *Punto de venta industrial* — diseñado para alto volumen de transacciones\n'
            '📦 *Inventario multi-almacén* — controla varias sedes desde un solo lugar\n'
            '📊 *Reportes avanzados* — analíticas que te dan poder de decisión\n'
            '👥 *Multi-usuario y permisos* — cada empleado ve solo lo que debe ver\n'
            '💳 *Integración de pagos* — compatible con múltiples pasarelas\n'
            '📈 *Analíticas de ventas* — datos en tiempo real para decisiones inteligentes\n'
            '🔧 *Altamente personalizable* — se adapta a TU negocio, no al revés\n\n'
            '¿Te gustaría ver una demo? Este sistema impresiona al más exigente 🎥'
        ),
        # Pitch 2
        (
            'Si tienes un supermercado, mercado o negocio industrial, estás en el lugar correcto 🛒🔥\n\n'
            '*MERCADO LOGIC PRO* no es para principiantes. Es para quienes quieren ser los mejores.\n\n'
            '¿Por qué es diferente a todo lo demás?\n\n'
            '✅ *IRON LOCK v2* — tu licencia está protegida con la mejor tecnología\n'
            '✅ *Multi-almacén* — maneja 2, 5 o 20 sucursales desde un solo sistema\n'
            '✅ *Multi-usuario* — cajeros, supervisores, administradores con permisos distintos\n'
            '✅ *Miles de productos* — sin sacrificar velocidad\n'
            '✅ *Analíticas en vivo* — sabes lo que pasa en tu negocio a cada momento\n\n'
            'Empresas de gran escala ya lo usan y los resultados son impresionantes 📈\n\n'
            '*$25 USD*, un pago único. Sí, leíste bien. Toda esa potencia por ese precio.\n\n'
            '¿Estás listo para llevar tu negocio al siguiente nivel? 🚀'
        ),
        # Pitch 3
        (
            'Voy a ser directo: si tu negocio mueve mucho volumen y NO tienes un sistema profesional, '
            'estás dejando dinero sobre la mesa 🛒💯\n\n'
            '*MERCADO LOGIC PRO* es lo que usan los negocios que quieren crecer de verdad:\n\n'
            '🏢 *Escalabilidad total* — de 1 a 100 puntos de venta\n'
            '🔐 *Seguridad IRON LOCK v2* — imposible de piratear\n'
            '📊 *Datos que importan* — no solo ventas, sino tendencias, márgenes, productividad\n'
            '👥 *Equipo organizado* — cada persona con su rol y permisos\n'
            '⚙️ *Personalización extrema* — lo ajustamos a tu flujo de trabajo exacto\n\n'
            '¿Cuánto vale un sistema empresarial? Normalmente $200-500 al mes.\n'
            'Nosotros: *$25 USD*, una sola vez. Sin letra pequeña.\n\n'
            'Haces la matemática. Nosotros ya la hicimos por ti 💰\n\n'
            '¿Quieres verlo en acción? 👇'
        ),
    ],
    'farmacia': [
        # Pitch 1
        (
            '¡Perfecto! Las farmacias son negocios delicados que necesitan control preciso 💊🏥\n\n'
            '*Farmacia Pro Plus* fue diseñado con todo lo que una farmacia necesita:\n\n'
            '💊 *Control de medicamentos* — cada producto con su registro completo\n'
            '📦 *Inventario por lote* — controlas fechas de elaboración y vencimiento\n'
            '📅 *Alertas de vencimiento* — nunca más vendes un producto vencido\n'
            '🛒 *Punto de venta rápido* — porque en salud no hay tiempo que perder\n'
            '👥 *Historial de clientes* — sabes qué les recetaron y qué compraron antes\n'
            '📊 *Reportes regulatorios* — para cumplir con las exigencias legales\n\n'
            'Más de 50 farmacias ya lo usan en Venezuela 💪\n\n'
            '¿Te gustaría ver cómo funciona? En salud, la organización salva vidas y negocios 🎥'
        ),
        # Pitch 2
        (
            'Si manejas una farmacia, sabes que no puedes permitirte errores 💊⚠️\n\n'
            'Un medicamento vencido puede costarte la licencia. '
            'Un inventario desordenado puede costarte clientes. '
            'Una venta mal registrada puede costarte auditorías.\n\n'
            '*Farmacia Pro Plus* te da la tranquilidad que necesitas:\n\n'
            '✅ *Control total por lotes* — sabes exactamente qué vence y cuándo\n'
            '✅ *Alertas automáticas* — te avisa antes de que algo venza\n'
            '✅ *Historial de clientes* — para recetas y compras frecuentes\n'
            '✅ *Reportes para regulación* — cumple con los requisitos legales\n'
            '✅ *Ventas rápidas* — porque los clientes no esperan\n\n'
            'Por *$25 USD*, una sola vez. ¿Cuánto vale la tranquilidad de saber que tu '
            'inventario está perfecto? 💰\n\n'
            '¿Te animas a ver la demo? 💊'
        ),
        # Pitch 3
        (
            '¿Sabías que las farmacias que usan software de gestión tienen un 25% menos '
            'de pérdidas por vencimiento? 💊📊\n\n'
            '*Farmacia Pro Plus* hace la diferencia:\n\n'
            '🎯 *Lotes controlados* — cada entrada de producto queda registrada con fecha y lote\n'
            '🎯 *Vencimiento vigilado* — alertas automáticas antes de la fecha límite\n'
            '🎯 *Ventas seguras* — cada venta queda documentada con nombre del medicamento\n'
            '🎯 *Clientes fieles* — historial completo para mejor servicio\n'
            '🎯 *Cumplimiento legal* — reportes que cumplen con las normativas\n\n'
            'Más de 50 farmacias ya confían en este sistema. Y saben por qué: '
            'porque en el negocio de la salud, no hay margen para errores.\n\n'
            '*$25 USD*. Una inversión que previene pérdidas que pueden ser miles de dólares.\n\n'
            '¿Vas a arriesgarte a seguir operando sin sistema? 💊'
        ),
    ],
    'fruteria': [
        # Pitch 1
        (
            '¡Qué rico negocio! Las fruterías y verdulerías nunca pasan de moda 🍎🥬\n\n'
            '*Frutería Pro* viene con algo increíble: *74 productos pre-cargados* de fábrica.\n'
            '¡No necesitas configurar nada!\n\n'
            'Esto es lo que incluye:\n\n'
            '🍎 *74 productos pre-cargados* — listo para vender desde el día 1\n'
            '📦 *Control de inventario* — sabes cuánto tienes de cada fruta y verdura\n'
            '🛒 *Ventas rápidas* — porque la fruta no espera\n'
            '📊 *Reportes diarios* — al cierre sabes exactamente cuánto vendiste\n'
            '🏷️ *Gestión de precios* — ajustas según la temporada\n'
            '📅 *Control de fechas* — evitas pérdidas por productos vencidos\n\n'
            'Más de 50 fruterías ya lo usan en Venezuela 💪\n\n'
            '¿Quieres ver cómo funciona? Tu negocio merece este upgrade 🎥'
        ),
        # Pitch 2
        (
            'Si vendes frutas y verduras, sabes que el tiempo es oro 🍎⏰\n\n'
            'Cada hora que pasa, tus productos pierden frescura. Necesitas vender rápido '
            'y tener control exacto de lo que entra y sale.\n\n'
            '*Frutería Pro* es la solución:\n\n'
            '✅ *74 productos ya cargados* — plátano, tomate, lechuga, mango... ¡todo listo!\n'
            '✅ *Venta en segundos* — buscas, agregas, cobras. Fin.\n'
            '✅ *Inventario al día* — sabes qué reponer antes de que se acabe\n'
            '✅ *Control de mermas* — registras lo que se pierde y por qué\n'
            '✅ *Reportes que ayudan* — sabes qué fruta te deja más ganancia\n\n'
            'Por *$25 USD*, un solo pago. ¿Sabes cuánto pierdes en un día por no llevar '
            'control? Probablemente más de eso 💰\n\n'
            '¿Te animas a modernizar tu frutería? 🍊'
        ),
        # Pitch 3
        (
            'Mira, en el negocio de las frutas y verduras, la clave es ROTACIÓN 🍎🔄\n\n'
            '¿Cómo rotas rápido si no sabes qué tienes? ¿Cómo cobras rápido si buscas precios a mano?\n\n'
            '*Frutería Pro* te da la ventaja competitiva:\n\n'
            '⚡ *74 productos pre-cargados* — desde plátano hasta cambur, todo incluido\n'
            '⚡ *Venta express* — cobras en 5 segundos, no en 5 minutos\n'
            '⚡ *Stock visible* — ves al momento qué te falta y qué te sobra\n'
            '⚡ *Precios flexibles* — los ajustas según la oferta y demanda del día\n'
            '⚡ *Cierre de día automático* — un clic y sabes tu ganancia\n\n'
            'Más de 50 fruterías en Venezuela ya modernizaron su operación con esta app.\n'
            'El resultado: menos pérdidas, más ventas, clientes más felices 📈\n\n'
            'Todo por *$25 USD*. Una vez. Para siempre.\n\n'
            '¿Tu frutería merece mejor herramientas? Por supuesto que sí 👇'
        ),
    ],
    'bodega_cloud': [
        # Pitch 1
        (
            '¡La nube es el futuro! Y tu negocio también debería estar ahí ☁️🚀\n\n'
            '*Bodega Pro Cloud* es toda la potencia de nuestro sistema de bodegas, '
            'pero con sincronización en tiempo real desde cualquier lugar.\n\n'
            '¿Qué significa esto para ti?\n\n'
            '☁️ *Accede desde cualquier dispositivo* — celular, tablet, computadora\n'
            '📱 *Multi-dispositivo* — tú y tus empleados ven lo mismo al mismo tiempo\n'
            '📦 *Inventario en tiempo real* — si venden en una sucursal, se actualiza en todas\n'
            '📊 *Reportes en línea* — ve tus números desde tu casa o desde la playa\n'
            '🔒 *Respaldo automático* — tus datos seguros, sin miedo a perder nada\n'
            '👥 *Colaboración en equipo* — todos trabajan con la misma información\n\n'
            '¿Te gustaría ver la demo? El futuro ya llegó, no te quedes atrás ☁️'
        ),
        # Pitch 2
        (
            '¿Tienes varias sucursales o quieres revisar tu negocio desde casa? ☁️💡\n\n'
            '*Bodega Pro Cloud* es la evolución que tu negocio necesita:\n\n'
            '✅ *Todo en la nube* — sin servidores locales que mantener\n'
            '✅ *Sincronización instantánea* — lo que pasa en una tienda, las otras lo saben\n'
            '✅ *Acceso remoto* — revisa ventas, stock y reportes desde tu celular\n'
            '✅ *Seguridad total* — respaldo automático y cifrado de datos\n'
            '✅ *Multi-usuario* — cada empleado con su acceso y permisos\n'
            '✅ *Actualizaciones automáticas* — siempre tienes la última versión\n\n'
            'Por *$25 USD*, un solo pago. ¿Sabes cuánto cuesta un sistema en la nube? '
            'Normalmente $50-200 al mes. Nosotros te lo damos para siempre por $25 💰\n\n'
            '¿Estás listo para la nube? ☁️'
        ),
        # Pitch 3
        (
            'Déjame hacerte una pregunta: ¿cuántas veces has querido revisar cómo va tu negocio '
            'desde fuera y no pudiste? ☁️🤔\n\n'
            '*Bodega Pro Cloud* elimina esa limitación:\n\n'
            '🌐 *Tu negocio en tu bolsillo* — accedes desde cualquier lugar del mundo\n'
            '📊 *Datos en tiempo real* — no esperas a fin de mes para saber cómo vas\n'
            '🔄 *Sincronización automática* — sin configuraciones complicadas\n'
            '🛡️ *Respaldo en la nube* — si tu computadora se daña, tus datos están a salvo\n'
            '👥 *Equipo conectado* — todos los puntos de venta hablan entre sí\n\n'
            'Más de 50 negocios ya están en la nube con nosotros. Y sabes qué dicen? '
            '"No sé cómo operaba sin esto antes" 💪\n\n'
            '*$25 USD*, una sola vez. Tecnología empresarial a precio de emprendedor.\n\n'
            '¿Vamos a subir tu negocio a la nube? ☁️👇'
        ),
    ],
}

# ==================== PHASE 4: OBJECTION HANDLING ====================

OBJECIONES = {
    'caro': {
        'triggers': ['caro', 'mucha plata', 'no tengo', 'costoso', 'no puedo pagar',
                      'no reacha', 'muy costoso', 'mucho dinero', 'no da', 'no tengo dinero',
                      'sobra', 'fuera de presupuesto', 'muy alto'],
        'respuestas': [
            (
                'Entiendo perfectamente 💛 Pero oye, déjame ponerlo en perspectiva:\n\n'
                'Son *$25 USD*, un solo pago. Sin mensualidades. Para siempre.\n\n'
                '¿Sabes qué cuesta un sistema de punto de venta normal?\n'
                'Entre $30 y $100 al MES. En un año pagas $360-1,200. '
                'Con nosotros pagas $25 UNA VEZ y ya.\n\n'
                'Además, piensa en esto: ¿cuánto dinero pierdes al mes por no tener '
                'un buen sistema?Errores, ventas perdidas, mala organización... '
                'Eso seguro supera los $25 💰\n\n'
                '¿Qué te parece si primero ves la demo gratis y luego decides? 🎥'
            ),
            (
                'Te entiendo, el dinero hay que cuidarlo 💪 Pero escucha esto:\n\n'
                '*$25 USD* es literalmente lo que cuesta:\n'
                '• Un corte de cabello en una barbería decente\n'
                '• Una manicura básica\n'
                '• 2 pizzas grandes\n\n'
                'La diferencia es que nuestra app te VA A GENERAR dinero, no a costarte. '
                'Más de 50 negocios recuperaron la inversión en la primera semana 📈\n\n'
                'Y si no te convence, siempre puedes ver la demo gratis primero. Sin compromiso 🤝'
            ),
            (
                'Jaja, te voy a ser sincera: *$25 USD* por un sistema profesional '
                'NO es caro. Es una ganga 😄\n\n'
                'Otros sistemas cobran:\n'
                '• Odoo: $25-75 al MES\n'
                '• Sales Force: $25 al MES por usuario\n'
                '• Square: 2.6% de cada venta, siempre\n\n'
                'Nosotros: $25 una vez. Punto. Se acabó.\n\n'
                'Piensa en ello como una inversión, no como un gasto. '
                '¿Cuánto ganarías si pudieras vender más rápido, organizarte mejor '
                'y no perder clientes? Eso vale muchísimo más que $25 💎\n\n'
                '¿Quieres ver la demo para convencerte? 🎥'
            ),
            (
                'Hermano, sé que la situación en Venezuela es difícil, pero por eso mismo '
                'necesitas herramientas que te hagan más eficiente 💪\n\n'
                'Si un sistema de $25 USD te permite:\n'
                '✅ Vender más rápido\n'
                '✅ No perder clientes por desorganización\n'
                '✅ Tener control de tu dinero\n'
                '✅ Generar reportes para decisiones inteligentes\n\n'
                'Entonces no es un gasto, es la mejor inversión que puedes hacer en tu negocio. '
                'Se paga sola, te lo garantizo 📈\n\n'
                '¿Y si primero pruebas la demo sin compromiso? 🎥'
            ),
        ],
    },
    'dudar': {
        'triggers': ['no se', 'no estoy seguro', 'dudo', 'tengo dudas', 'es verdad',
                      'estafa', 'fraude', 'mentira', 'no creo', 'sera cierto', 'confiable',
                      'confia', 'engaño', 'truco'],
        'respuestas': [
            (
                'Te entiendo perfectamente, la desconfianza es buena cuando se trata de tu dinero 💡\n\n'
                'Pero oye, déjame decirte algo:\n\n'
                '✅ Somos *A2K Digital Studio*, empresa registrada: Inversiones 2K 3112 C.A (J-40632338-1)\n'
                '✅ Más de 50 negocios ya confían en nosotros\n'
                '✅ Tenemos ingeniero de soporte que te atiende directamente por WhatsApp\n'
                '✅ Puedes ver la demo ANTES de pagar\n'
                '✅ Tenemos tienda online oficial\n\n'
                'No tenemos nada que esconder 😊 De hecho, te invito a ver la demo gratis. '
                'Te muestro cómo funciona y tú decides. Sin compromiso 🤝\n\n'
                '¿Te parece justo? 🎥'
            ),
            (
                'Jaja, entiendo tu duda. Pero fíjate en algo: tienes todo para ganar y nada que perder 💪\n\n'
                '¿Por qué? Porque:\n\n'
                '1️⃣ *Puedes ver la demo gratis* — te mostramos todo antes de que desembolses un centavo\n'
                '2️⃣ *Soporte directo* — el ingeniero Abigail te atiende personalmente\n'
                '3️⃣ *Empresa legal* — Inversiones 2K 3112 C.A, registrada y con RIF\n'
                '4️⃣ *Más de 50 clientes satisfechos* — no estamos inventando nada\n'
                '5️⃣ *Un solo pago* — no hay trampa de suscripciones ocultas\n\n'
                'Si no te convence, no compras. Así de simple. Pero te aseguro que vas a quedar impresionado 😊\n\n'
                '¿Ves la demo? 🎥'
            ),
            (
                'Mira, la mejor prueba es verlo con tus propios ojos 🔍\n\n'
                'Más de 50 negocios en Venezuela ya usan nuestros sistemas. '
                '¿Crees que 50+ dueños de negocios habrían pagado si fuera una estafa? 🤔\n\n'
                'Además:\n'
                '🏢 Empresa formal: Inversiones 2K 3112 C.A\n'
                '👨‍💻 Ingeniero disponible por WhatsApp\n'
                '🛒 Tienda online oficial\n'
                '🎥 Demo gratis antes de comprar\n\n'
                'Te propongo algo: agrega al ingeniero en WhatsApp, pide la demo, '
                'mírala funcionar, y después decides. Si no te convence, no pasa nada. '
                'Si te convence, habrás encontrado una herramienta que vale oro 💎\n\n'
                '¿Te parece bien? 👇'
            ),
        ],
    },
    'pensar': {
        'triggers': ['voy a pensar', 'lo pienso', 'después', 'luego', 'te aviso',
                      'te digo', 'más tarde', 'otro día', 'ya ves', 'nada por ahora',
                      'quizás luego', 'ahora no'],
        'respuestas': [
            (
                'Claro, lo entiendo 💛 Es una decisión importante y merece pensarse bien.\n\n'
                'Solo te pido algo: no te olvides de nosotros 😄\n\n'
                'Aquí tienes un dato para pensar:\n'
                'Cada día que pasa sin un sistema de gestión, es un día que podrías estar '
                'perdiendo clientes por desorganización, o perdiendo dinero por mala gestión.\n\n'
                '¿Sabías que el promedio de tiempo que tardan nuestros clientes en decidir '
                'es de 2 días? Y todos dicen: "mejor lo hubiera hecho antes" 😅\n\n'
                'Te dejo el enlace a la tienda para que lo revises con calma:\n'
                '🛒 [A2K Digital Studio]({store})\n\n'
                'Cuando estés listo, aquí andamos. Yo no me canso 😊'
            ),
            (
                'Jajaja, claro, piénsalo bien 💪 Pero oye, un consejito:\n\n'
                '¿Sabes cuántos dueños de negocios me dicen "lo pienso" y vuelven '
                'una semana después? Muchísimos. Y todos me dicen lo mismo: '
                '"debería haberlo hecho antes"\n\n'
                'Mientras tanto, la competencia sigue avanzando, los sistemas siguen mejorando, '
                'y los precios... bueno, estos sí se mantienen por ahora 😏\n\n'
                'Te dejo la tienda para que la revises:\n'
                '🛒 [A2K Digital Studio]({store})\n\n'
                'Y si necesitas algo, ya sabes dónde encontrarme. Estoy aquí 24/7 ✨'
            ),
            (
                'No hay problema, es tu decisión y la respeto 💛\n\n'
                'Pero no te vayas sin esto: cada semana más negocios se automatizan. '
                'Los que no lo hacen, se quedan atrás. Es la realidad del mercado.\n\n'
                'Mi consejo: márcate la tienda, revisa la demo cuando tengas tiempo, '
                'y toma la decisión con información, no con dudas.\n\n'
                '🛒 [A2K Digital Studio - Tienda]({store})\n'
                '🎥 [Ver Demo]({store})\n\n'
                'Cuando estés listo, me escribes y lo cerramos en 5 minutos. ¿Trato? 🤝'
            ),
        ],
    },
    'otro_sistema': {
        'triggers': ['ya tengo', 'uso otro', 'tengo otro', 'otro sistema', 'ya uso',
                      'tengo uno', 'trabajo con', 'cuento con', 'mi sistema'],
        'respuestas': [
            (
                '¡Qué bueno que ya tienes un sistema! Eso dice mucho de ti 💪\n\n'
                'Pero oye, déjame preguntarte algo: ¿estás 100% satisfecho con él?\n\n'
                'Porque la mayoría de nuestros clientes también tenían sistema antes. '
                '¿Y por qué cambiaron?\n\n'
                '❌ El otro cobraba mensualidades — nosotros cobramos una vez\n'
                '❌ El otro no tenía soporte directo — nosotros tienes ingeniero por WhatsApp\n'
                '❌ El otro era complicado — el nuestro es fácil de usar\n'
                '❌ El otro no tenía las funciones que necesitaban — nosotros las tienen\n\n'
                'No te digo que cambies ahora. Solo te propongo algo: mira nuestra demo '
                'y compara. Si tu sistema actual es mejor, seguimos siendo amigos 😊\n\n'
                '¿Te parece justo? 🎥'
            ),
            (
                'Perfecto, me gusta que ya estés tecnificado 👏\n\n'
                'Solo una pregunta: ¿cuánto pagas al mes por tu sistema actual?\n\n'
                'Porque si pagas mensualidades, estás gastando de más. Con nuestros sistemas, '
                'pagas *$25 USD* una sola vez y listo.\n\n'
                'Además, ¿tu sistema actual tiene:\n'
                '• Soporte directo por WhatsApp?\n'
                '• Demo gratuita?\n'
                '• Actualizaciones sin costo?\n'
                '• Funciones específicas para TU tipo de negocio?\n\n'
                'Si la respuesta es no a alguna de esas, vale la pena mirarnos.\n'
                'Sin compromiso. Solo compara 💡\n\n'
                '¿Ves la demo? 🎥'
            ),
            (
                'Respeto mucho que ya tengas un sistema 💯 Eso significa que te importa tu negocio.\n\n'
                'Te cuento por qué muchos negocios cambiaron al nuestro:\n\n'
                '1️⃣ *Precio:* $25 USD una vez vs. $30-100 al mes en otros\n'
                '2️⃣ *Soporte:* Ingeniero directo por WhatsApp, no un chatbot\n'
                '3️⃣ *Funciones:* Diseñado específicamente para tu rubro, no genérico\n'
                '4️⃣ *Actualizaciones:* Gratis de por vida\n'
                '5️⃣ *Modo offline:* Nuestros sistemas funcionan sin internet\n\n'
                'No te pido que cambies a ciegas. Pide una demo, compáralo con lo que tienes, '
                'y decide con datos. Si tu sistema actual es mejor, ¡genial! 😊\n\n'
                'Pero si el nuestro es mejor... bueno, ya sabes qué hacer 👇'
            ),
        ],
    },
    'gratis': {
        'triggers': ['gratis', 'free', 'no quiero pagar', 'regalar', 'sin costo',
                      'gratuito', 'descarga gratis', 'pirata', 'crack', 'full gratis'],
        'respuestas': [
            (
                'Jajaja, te entiendo 😄 A todos nos gusta lo gratis. Pero oye, escúchame:\n\n'
                'No tenemos versión gratuita completa, PERO sí tenemos algo mejor: '
                'una *demo totalmente gratis* donde ves el sistema funcionando con todos sus detalles 🎥\n\n'
                '¿Por qué no es gratis? Porque detrás de cada sistema hay:\n'
                '👨‍💻 Un ingeniero que lo desarrolló (cientos de horas)\n'
                '🔧 Actualizaciones constantes\n'
                '💬 Soporte técnico personalizado\n'
                '🔒 Seguridad y estabilidad\n\n'
                'Todo eso tiene un costo. Por eso es $25 USD una sola vez.\n\n'
                'Pero la buena noticia es que puedes probar antes de decidir. '
                'La demo es 100% gratis y sin compromiso 💡\n\n'
                '¿Te animas a verla? 🎥'
            ),
            (
                'Te voy a ser honesta 💪\n\n'
                'Los sistemas gratis (crack, pirata, etc.) tienen problemas serios:\n\n'
                '❌ Sin soporte — si algo falla, estás solo\n'
                '❌ Sin actualizaciones — se quedan obsoletos rápido\n'
                '❌ Sin seguridad — pueden tener virus o robar tus datos\n'
                '❌ Ilegales — pueden causarte problemas\n'
                '❌ No tienen funciones completas — suelen ser versiones limitadas\n\n'
                'Por *$25 USD*, una sola vez, obtienes:\n'
                '✅ Soporte técnico de por vida\n'
                '✅ Actualizaciones gratis\n'
                '✅ Sistema seguro y estable\n'
                '✅ Todas las funciones incluidas\n\n'
                '¿Vale la pena arriesgarse con algo gratis cuando por el precio de una comida '
                'tienes algo profesional y seguro? 💰\n\n'
                'Prueba la demo gratis y decide tú mismo 🎥'
            ),
            (
                'Mira, la realidad es esta: un buen software cuesta dinero porque hay '
                'personas trabajando detrás 💪\n\n'
                'No somos una multinacional. Somos una empresa venezolana que desarrolla '
                'sistemas de calidad a precios justos.\n\n'
                '¿Sabes cuánto cuesta desarrollar un sistema como estos? Miles de dólares '
                'en horas de ingeniería. Y te lo ofrecemos a $25 USD porque queremos que '
                'los negocios venezolanos tengan acceso a herramientas profesionales.\n\n'
                'Lo que sí puedo ofrecerte gratis es:\n'
                '🎥 *Demo en vivo* — ves todo funcionando sin pagar un centavo\n'
                '💬 *Asesoría* — te ayudo a elegir la app correcta sin compromiso\n'
                '📊 *Información* — todos los detalles que necesites para decidir\n\n'
                '¿Vale la pena al menos ver la demo? Te prometo que te va a sorprender lo que '
                'ofrecemos por $25 😊'
            ),
        ],
    },
}

# ==================== PHASE 5: CLOSING ====================

CIERRES = [
    (
        '¡Excelente decisión! 🎉 Ese es el espíritu 💪\n\n'
        'El proceso de compra es súper rápido:\n\n'
        '1️⃣ Haz clic en "Comprar por WhatsApp" aquí abajo\n'
        '2️⃣ El ingeniero Abigail te atiende al toque\n'
        '3️⃣ Te da los datos de pago de tu preferencia\n'
        '4️⃣ Haces el pago y recibes tu licencia\n\n'
        'Todo en menos de 30 minutos ⏱️\n\n'
        '¿Listo/a? 👇'
    ),
    (
        '¡Me encanta tu decisión! 😍 Vamos a cerrar esto 💪\n\n'
        'Solo necesitas hacer clic en el botón de WhatsApp aquí abajo. '
        'El ingeniero te atiende directamente y te guía en todo.\n\n'
        'Después de comprar:\n'
        '✅ Recibes tu licencia inmediata\n'
        '✅ El ingeniero te instala y configura todo\n'
        '✅ Tienes soporte de por vida\n\n'
        'Tu negocio va a dar un salto gigante. ¡Vamos! 🚀\n\n'
        '👇 Haz clic aquí:'
    ),
    (
        '¡Esa es la actitud! 🔥 Nadie se arrepiente de invertir en su negocio.\n\n'
        'Te conecto directamente con el ingeniero para que cierre la compra. '
        'Es bien fácil: le escribes, eliges método de pago, haces el pago y listo.\n\n'
        'Recuerda que después de comprar también puedes visitar nuestra tienda '
        'para ver más productos:\n'
        '🛒 [A2K Digital Studio]({store})\n\n'
        '¡Vamos por ello! 👇'
    ),
    (
        '¡Increíble! Te vas a llevar una herramienta que va a transformar tu negocio 💎\n\n'
        'El proceso es directo y sin complicaciones:\n\n'
        '📲 Escribe al ingeniero por WhatsApp\n'
        '💳 Elige tu método de pago favorito\n'
        '✅ Recibe tu licencia y configuración\n'
        '🚀 Empieza a usar tu sistema hoy mismo\n\n'
        'No esperes más. Cada día sin sistema es un día perdiendo dinero.\n\n'
        '👇 Compra ahora:'
    ),
    (
        '¡Perfecto! 🎯 Hacemos esto rápido porque sé que tienes un negocio que atender.\n\n'
        'Solo haz clic en "Comprar por WhatsApp" y el ingeniero se encarga de todo. '
        'Te da datos de pago, confirmas, y en minutos tienes tu sistema funcionando.\n\n'
        'Visita nuestra tienda para más info:\n'
        '🛒 [A2K Digital Studio]({store})\n\n'
        '¿Vamos? 💪👇'
    ),
    (
        '¡Me parece perfecto! 💯 Ya mismo te conecto con el ingeniero.\n\n'
        'El proceso de compra es 100% transparente:\n'
        '• Sin letra pequeña\n'
        '• Sin costos ocultos\n'
        '• Sin sorpresas\n\n'
        'Solo pagas, recibes tu licencia y listo. Soporte incluido de por vida 🤝\n\n'
        '¿Listo/a para el siguiente nivel? 👇'
    ),
    (
        '¡Vamos! 🚀 No pierdas más tiempo. Cada minuto sin un sistema profesional '
        'es un minuto donde tu competencia te gana terreno.\n\n'
        'Haz clic abajo, habla con el ingeniero, y en menos de 30 minutos '
        'tienes tu sistema funcionando. Así de fácil.\n\n'
        '🛒 Tienda: [A2K Digital Studio]({store})\n\n'
        '¡Mano arriba si estás listo! 👇'
    ),
    (
        '¡Ya mismo! 🔥 Te lo prometo, es la mejor inversión que harás este año.\n\n'
        'Compra por WhatsApp aquí abajo. El ingeniero te atiende inmediatamente.\n'
        'Después de pagar, en minutos recibes todo:\n'
        '• Licencia completa\n'
        '• Configuración asistida\n'
        '• Tutorial de uso\n'
        '• Soporte de por vida\n\n'
        'Tu negocio te lo va a agradecer. ¡Vamos! 👇'
    ),
]

# ==================== OTHER RESPONSE VARIATIONS ====================

PRICE_VARIATIONS = [
    "Te cuento los precios 💰\n\nTodas nuestras aplicaciones cuestan **$25 USD**. Un solo pago. Para siempre.\n\n✅ Sin mensualidades\n✅ Sin suscripciones\n✅ Soporte incluido\n✅ Actualizaciones gratis\n\nTerminal adicional: +$5 USD\n\n🛒 *Tienda:* {store}\n\n¿Te interesa alguna en particular?".format(store=STORE_URL),
    "¡Excelente pregunta! 💸\n\nCualquiera de nuestras 9 apps: **$25 USD** (pago único)\nTerminal extra: **+$5 USD**\n\nCompara: otros sistemas cobran $30-50 al MES. Nosotros, una vez. Punto.\n\n🛒 *Tienda:* {store}\n\n¿Cuál te llama la atención?".format(store=STORE_URL),
    "Los precios son súper accesibles 🤑\n\n**$25 USD** por cualquier app. Eso es todo.\n\nIncluye licencia, soporte, actualizaciones y configuración.\n\n🛒 *Ver todos los productos:* {store}\n\n¿Empezamos? 🚀".format(store=STORE_URL),
    "Te lo resumo rápido 💡\n\n🔢 **$25 USD** = 1 app completa\n🔢 **$5 USD** = 1 terminal extra\n\nNada más. Sin letra pequeña. Sin sorpresas.\n\n🛒 *Tienda Online:* {store}\n\n¿Listo para invertir en tu negocio?".format(store=STORE_URL),
    "Aquí tienes los precios 📊\n\nTodas las apps: **$25 USD**\nExtra por terminal: **$5 USD**\n\nSe paga sola en el primer mes. Más de 50 negocios lo confirman 💪\n\n🛒 *Tienda:* {store}\n\n¿Quieres ver alguna app?".format(store=STORE_URL),
]

THANK_YOU_VARIATIONS = [
    "¡De nada! Para eso estamos 😊 No dudes en volver cuando quieras.\n\n🛒 *Tienda A2K:* {store}".format(store=STORE_URL),
    "¡Con mucho gusto! 😄 Fue un placer ayudarte. Recuerda que puedes visitar nuestra tienda cuando quieras.\n\n🛒 *Tienda:* {store}".format(store=STORE_URL),
    "¡Un placer! 👍 No dudes en escribirme. Estoy aquí 24/7.\n\n🛒 *Tienda A2K Digital Studio:* {store}".format(store=STORE_URL),
    "¡Para servirte! 🫡 Si necesitas algo más, me escribes. Ah, y no olvides visitar nuestra tienda online 💪\n\n🛒 *Tienda:* {store}".format(store=STORE_URL),
    "¡Gracias a ti por confiar en A2K! 💪 Estaré por aquí cuando me necesites.\n\n🛒 *Tienda Online:* {store}".format(store=STORE_URL),
    "¡No hay de qué! 🙏 Me alegra poder ayudarte. Visita nuestra tienda para ver más productos.\n\n🛒 *Tienda:* {store}".format(store=STORE_URL),
]

GOODBYE_VARIATIONS = [
    "¡Hasta luego! 👋 Fue un gusto. No dudes en volver. ¡Mucho éxito!\n\n🛒 *Tienda A2K:* {store}".format(store=STORE_URL),
    "¡Chao, parche! 🤙 Un placer. Vuelve cuando quieras. ¡Éxitos!\n\n🛒 *Tienda:* {store}".format(store=STORE_URL),
    "¡Nos pillemos luego! 😄 No olvides visitar nuestra tienda online.\n\n🛒 *Tienda:* {store}".format(store=STORE_URL),
    "¡Hasta pronto! 🙌 Que te vaya súper bien. Acuérdate que aquí andamos.\n\n🛒 *Tienda A2K:* {store}".format(store=STORE_URL),
    "¡Cuídate mucho! 👋 ¡Mucho éxito con tu negocio! 💼\n\n🛒 *Tienda Online:* {store}".format(store=STORE_URL),
    "¡Bye bye! 👋 Recuerda: A2K Digital Studio siempre está aquí para ti 🏆\n\n🛒 *Tienda:* {store}".format(store=STORE_URL),
]

UNKNOWN_VARIATIONS = [
    "Mm, no estoy segura de entender bien 🤔 Pero no te preocupes, cuéntame: ¿tienes un negocio? Si me dices qué tipo, te recomiendo la app perfecta 💡\n\n🛒 *Tienda A2K:* {store}".format(store=STORE_URL),
    "Jeje, creo que necesito un poco más de contexto 😅 Pero tranquilo, para eso estoy. Tenemos 9 apps para diferentes negocios. ¿Qué tipo de negocio tienes?\n\n🛒 *Tienda:* {store}".format(store=STORE_URL),
    "Ajá, entiendo... o creo que sí 😄 Mira, lo mejor es que me cuentes qué tipo de negocio manejas y te asesoro. ¿O prefieres ver el catálogo completo?\n\n🛒 *Tienda Online:* {store}".format(store=STORE_URL),
    "Vaya, eso es nuevo para mí 🤓 Pero hey, si tienes un negocio, tengo la herramienta ideal. ¿Me cuentas qué haces?\n\n🛒 *Tienda A2K:* {store}".format(store=STORE_URL),
    "Jajaja, me has pillado 🙈 A ver, empecemos de nuevo. ¿Tienes un negocio? Si me dices el rubro, te consigo la solución ideal.\n\n🛒 *Tienda:* {store}".format(store=STORE_URL),
]

DEMO_VARIATIONS = [
    "¡Buena idea! Probar antes de comprar siempre es lo mejor 🧪\n\nPuedes ver una demo en vivo por videollamada con el ingeniero Abigail. Te muestra todo funcionando y tú decides. ¡Sin compromiso!\n\n🛒 *Tienda:* {store}".format(store=STORE_URL),
    "¡Genial! Ver para creer 🧐\n\nAgenda tu demo gratis por WhatsApp. El ingeniero te lleva de la mano y te muestra cada función.\n\n🛒 *Tienda A2K:* {store}".format(store=STORE_URL),
    "¡Me parece perfecto! 🔍 Una demo vale más que mil palabras.\n\nEscribe al ingeniero por WhatsApp y coordina una videollamada. Totalmente gratis y sin compromiso.\n\n🛒 *Tienda:* {store}".format(store=STORE_URL),
    "¡Así se habla! 👏 Ver antes de comprar es de personas inteligentes.\n\nAgenda tu demo ahora y sorpréndete con lo que nuestras apps pueden hacer 🚀\n\n🛒 *Tienda A2K:* {store}".format(store=STORE_URL),
]

FOLLOW_UP_SELLING = [
    "Por cierto, esta app se paga sola en el primer mes 💡 Más de 50 negocios lo confirman.",
    "¿Sabías que puedes probarla antes de comprar? Solicita una demo gratis 🎥",
    "Dato real: nuestros clientes ahorran un promedio de 15 horas semanales ⏰",
    "Esta es una de nuestras apps más vendidas. ¡La gente la ama! ⭐⭐⭐⭐⭐",
    "Piénsalo así: son $25 USD una vez vs. horas que pierdes haciendo todo manual 📊",
    "No te quedes con la duda. Muchos negocios como el tuyo ya están automatizados 🔥",
    "Si compras hoy, puedes estar funcionando en menos de 30 minutos ⚡",
    "🛒 *Tienda A2K Digital Studio:* {store}".format(store=STORE_URL),
]

# ==================== ADDITIONAL RESPONSE VARIATIONS ====================

BUSINESS_TYPE_INTRO = [
    "¡Qué interesante! Parece que tienes un negocio de {tipo}. Déjame decirte que tenemos justo lo que necesitas 🎯",
    "¡Perfecto! Un negocio de {tipo} merece una herramienta profesional. Y adivina qué... ¡la tenemos! 😎",
    "¡Me encanta tu negocio de {tipo}! 🌟 Sabes qué, tengo la app ideal para ti. Déjame mostrarte...",
    "Un negocio de {tipo}, ¿eh? 💡 Conozco exactamente lo que necesitas para llevarlo al siguiente nivel.",
    "¡Wow! Los negocios de {tipo} están creciendo mucho últimamente 📈. Y nosotros tenemos la herramienta perfecta.",
    "¡Genial! El sector de {tipo} es uno de nuestros fuertes. Te tengo una solución que te va a encantar 🤩",
    "¡Interesante! Un/a {tipo} necesita buen software de gestión. ¡Y yo tengo el mejor! 😏",
    "¡Buenísimo! Si hay algo que me encanta es ayudar a negocios de {tipo}. ¡Tengo la app perfecta! 🏆",
]

RETURNING_USER_UPSELL = [
    "Oye, ya que estás de vuelta, ¿sabías que agregamos nuevas funciones a nuestras apps? 🆕",
    "¡Bienvenido de nuevo! ¿Ya tienes algo en mente o quieres ver las novedades? 😊",
    "Qué bueno verte otra vez. Si ya tienes una app nuestra, ¿quieres ver las actualizaciones? 🔄",
    "Hey! De vuelta por aquí. ¿Necesitas otra app para tu negocio o hay algo más que pueda hacer por ti? 💪",
    "Qué gusto! Ya te conozco, así que vamos directo al grano. ¿Qué necesitas? 🎯",
]

STORE_REMINDER_MESSAGES = [
    "\n\n💡 *Tip:* Visita nuestra tienda para ver todas las opciones:\n🛒 [A2K Digital Studio]({store})".format(store=STORE_URL),
    "\n\n🛒 *Recuerda:* Puedes explorar todo en nuestra tienda online:\n[A2K Digital Studio]({store})".format(store=STORE_URL),
    "\n\n📍 *Enlace de la tienda:* [A2K Digital Studio]({store})\nAllí encuentras todas las apps, descripciones y demos.".format(store=STORE_URL),
]

POST_SALE_MESSAGES = [
    "¡Felicidades por tu compra! 🎉 Ahora tu negocio va a dar un salto gigante. Recuerda que tienes soporte incluido de por vida.\n\n"
    "🛒 *Visita nuestra tienda* para ver más productos que podrían interesarte:\n"
    "[A2K Digital Studio]({store})".format(store=STORE_URL),
    "¡Bienvenido al club! 💎 Eres uno más de los +50 negocios que confían en A2K. El ingeniero te va a contactar para la configuración.\n\n"
    "🛒 *Tienda:* [A2K Digital Studio]({store})".format(store=STORE_URL),
    "¡Excelente elección! 🔥 Tu sistema está en camino. No olvides que tenemos soporte técnico de por vida.\n\n"
    "🛒 *Mira otros productos:* [A2K Digital Studio]({store})".format(store=STORE_URL),
]

APPS_CROSS_SELL = {
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

CROSS_SELL_MESSAGES = [
    "Oye, y no sabía si te interesa... también tenemos *{nombre}* {icono} que complementa perfecto a lo que viste 🤔",
    "Por cierto, si te gustó lo que viste, deberías echarle un ojo a *{nombre}* {icono}. Muchos clientes tienen ambas apps 💡",
    "Tip pro: combinar *{nombre}* {icono} con lo que viste te da control total de tu negocio. ¿Te interesa? 🔥",
]

# ==================== UTILITIES ====================

def get_whatsapp_buy_url(app_nombre):
    msg = f'Quiero comprar {app_nombre} - A2K Digital Studio'
    encoded = urllib.parse.quote(msg)
    return f'https://wa.me/{WHATSAPP_CONTACT}?text={encoded}'

def get_whatsapp_demo_url(app_nombre):
    msg = f'Quiero ver la demo de {app_nombre} - A2K Digital Studio'
    encoded = urllib.parse.quote(msg)
    return f'https://wa.me/{WHATSAPP_CONTACT}?text={encoded}'

def simulate_typing(chat_id, duration=None):
    if duration is None:
        duration = random.uniform(0.8, 2.0)
    try:
        bot.send_chat_action(chat_id, 'typing')
        time.sleep(duration)
    except Exception:
        pass

def smart_choice(options, user_id, category='default'):
    """Elige una opción aleatoria evitando repetir la última."""
    last = user_last_responses.get(f'{user_id}_{category}')
    available = [o for o in options if o != last]
    if not available:
        available = options
    choice = random.choice(available)
    user_last_responses[f'{user_id}_{category}'] = choice
    return choice

def find_app_by_keywords(text):
    text_lower = text.lower().strip()
    best_match = None
    best_score = 0
    for app in A2K_APPS:
        score = 0
        for kw in app['keywords']:
            if kw in text_lower:
                score += len(kw)
            if kw in text_lower.replace(' ', ''):
                score += len(kw) // 2
        if score > best_score:
            best_score = score
            best_match = app
    if best_score >= 3:
        return best_match
    return None

def recommend_app_for_business(text):
    text_lower = text.lower()
    best_match = None
    best_type_name = None
    best_score = 0

    business_map = {
        'barbería': {'app_id': 'barberia', 'tipo': 'barbería',
                     'keywords': ['barbería', 'barberia', 'barbero', 'barber shop', 'corte de cabello']},
        'nail': {'app_id': 'nail', 'tipo': 'nail studio / estética',
                 'keywords': ['nail', 'uñas', 'manicura', 'pedicura', 'estética', 'estetica', 'salón de belleza', 'salon de belleza']},
        'motos': {'app_id': 'repuestos', 'tipo': 'repuestos de motos',
                  'keywords': ['motos', 'repuestos de motos', 'taller mecánico', 'taller mecanico', 'motocicleta']},
        'ferretería': {'app_id': 'ferreteria', 'tipo': 'ferretería',
                       'keywords': ['ferretería', 'ferreteria', 'herramientas', 'construcción', 'construccion']},
        'bodega': {'app_id': 'bodega_descarga', 'tipo': 'bodega / abasto',
                   'keywords': ['bodega', 'abasto', 'despensa', 'almacén', 'almacen', 'mayorista']},
        'supermercado': {'app_id': 'mercado_logic', 'tipo': 'supermercado / mercado',
                         'keywords': ['supermercado', 'mercado', 'industrial', 'autoservicio']},
        'farmacia': {'app_id': 'farmacia', 'tipo': 'farmacia / droguería',
                     'keywords': ['farmacia', 'droguería', 'drogueria', 'medicamentos']},
        'frutería': {'app_id': 'fruteria', 'tipo': 'frutería / verdulería',
                     'keywords': ['frutería', 'fruteria', 'frutas', 'verdulería', 'verduleria']},
        'cloud': {'app_id': 'bodega_cloud', 'tipo': 'bodega en la nube',
                  'keywords': ['cloud', 'nube', 'sincronizar', 'sincronización', 'sincronizacion', 'online']},
    }

    for category, info in business_map.items():
        for kw in info['keywords']:
            if kw in text_lower:
                score = len(kw)
                if score > best_score:
                    best_score = score
                    best_match = info['app_id']
                    best_type_name = info['tipo']

    if best_match:
        app = next((a for a in A2K_APPS if a['id'] == best_match), None)
        return app, best_type_name
    return None, None

def detect_objection(text):
    """Detecta si el texto contiene una objeción. Returns (category, response) or (None, None)."""
    text_lower = text.lower()
    for category, data in OBJECIONES.items():
        for trigger in data['triggers']:
            if trigger in text_lower:
                return category
    return None

# ==================== INTENT DETECTION ====================

def is_greeting(text):
    greetings = [
        'hola', 'buenas', 'hey', 'buen dia', 'buenos dias', 'buenas tardes',
        'buenas noches', 'saludos', 'qué tal', 'que tal', 'como estas',
        'como andas', 'que hay', 'que hubo', 'epa', 'hello', 'hi', 'ey',
        'buenas tardess', 'que fue'
    ]
    text_lower = text.lower().strip()
    return any(g == text_lower or text_lower.startswith(g) for g in greetings)

def is_price_question(text):
    keywords = [
        'precio', 'cuanto cuesta', 'cuánto cuesta', 'cuanto vale', 'cuánto vale',
        'costo', 'tarifa', 'cuanto es', 'cuánto es', 'valor',
        'cuánto sale', 'cuanto sale', 'cuanto cobran'
    ]
    text_lower = text.lower().strip()
    return any(k in text_lower for k in keywords)

def is_demo_request(text):
    keywords = [
        'demo', 'probar', 'prueba', 'ver como funciona', 'testear',
        'mostrar', 'ver el sistema', 'ensayar', 'videollamada'
    ]
    text_lower = text.lower().strip()
    return any(k in text_lower for k in keywords)

def is_purchase_intent(text):
    keywords = [
        'comprar', 'quiero comprar', 'deseo', 'adquirir', 'me llevo', 'lo quiero',
        'cómo compro', 'como compro', 'donde compro', 'dónde compro', 'compra',
        'me interesa', 'oferta', 'quiero la', 'quiero el', 'quiero una',
        'dame', 'voy a comprar', 'listo para', 'me la llevo', 'cierro'
    ]
    text_lower = text.lower().strip()
    return any(k in text_lower for k in keywords)

def is_thank_you(text):
    keywords = [
        'gracias', 'muchas gracias', 'agradecido', 'te lo agradesco',
        'thanks', 'ty', 'thx', 'gracia', 'muy amable'
    ]
    text_lower = text.lower().strip()
    return any(k in text_lower for k in keywords)

def is_goodbye(text):
    keywords = [
        'adiós', 'adios', 'chao', 'chau', 'hasta luego', 'nos vemos',
        'bye', 'me voy', 'hasta pronto', 'suerte', 'hasta mañana'
    ]
    text_lower = text.lower().strip()
    return any(k in text_lower for k in keywords)

def is_contact_request(text):
    keywords = [
        'contacto', 'contactar', 'teléfono', 'telefono', 'whatsapp',
        'hablar', 'escribir', 'comunicar', 'ingeniero', 'abigail'
    ]
    text_lower = text.lower().strip()
    return any(k in text_lower for k in keywords)

def is_payment_request(text):
    keywords = [
        'pago', 'pagar', 'pagos', 'banco', 'bancos', 'transferencia',
        'deposito', 'depósito', 'zelle', 'paypal', 'método', 'metodo',
        'cómo pago', 'como pago', 'efectivo', 'pago móvil',
        'formas de pago', 'metodos de pago', 'métodos de pago',
        'cuenta bancaria', 'datos bancarios'
    ]
    text_lower = text.lower().strip()
    return any(k in text_lower for k in keywords)

def is_store_request(text):
    keywords = ['tienda', 'store', 'página', 'pagina', 'web', 'link', 'enlace', 'sitio']
    text_lower = text.lower().strip()
    return any(k in text_lower for k in keywords)

def is_business_description(text):
    keywords = [
        'tengo un negocio', 'tengo una', 'mi negocio', 'tengo un',
        'soy dueño', 'soy dueña', 'tengo mi', 'negocio de',
        'trabajo en un', 'trabajo en una', 'vendo', 'vende',
        'manejo un', 'manejo una', 'tengo una bodega', 'tengo una ferretería',
        'tengo una barbería', 'tengo un salón', 'tengo una farmacia',
        'tengo una frutería', 'tengo un taller', 'mi tienda', 'mi local'
    ]
    text_lower = text.lower().strip()
    return any(k in text_lower for k in keywords)

# ==================== KEYBOARDS ====================

def get_main_menu_keyboard():
    """Teclado principal persistente con tienda prominente."""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton('📋 Catálogo A2K'),
        types.KeyboardButton('🛒 Tienda Online'),
    )
    markup.add(
        types.KeyboardButton('💰 Precios'),
        types.KeyboardButton('💳 Métodos de Pago'),
    )
    markup.add(
        types.KeyboardButton('🎥 Ver Demo'),
        types.KeyboardButton('🛒 Otros Productos'),
    )
    markup.add(
        types.KeyboardButton('👤 Contacto'),
    )
    return markup

def get_catalog_inline_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=3)
    for app in A2K_APPS:
        markup.add(types.InlineKeyboardButton(
            f"{app['icono']} {app['nombre']}",
            callback_data=f"app_{app['id']}"
        ))
    markup.add(
        types.InlineKeyboardButton('🛒 Tienda Online', url=STORE_URL),
        types.InlineKeyboardButton('💳 Ver Pagos', callback_data='pagos'),
    )
    markup.add(types.InlineKeyboardButton('🔙 Volver al Menú', callback_data='main_menu'))
    return markup

def get_app_detail_keyboard(app):
    markup = types.InlineKeyboardMarkup(row_width=2)
    if app.get('demo'):
        markup.add(types.InlineKeyboardButton(
            '🎥 Ver Demo en Vivo',
            callback_data=f'demo_{app["id"]}'
        ))
    if app['id'] in ('bodega_descarga', 'mercado_logic'):
        markup.add(
            types.InlineKeyboardButton('📋 Demo Bodega Pro', url=BODEGA_PRO_DEMO_URL),
            types.InlineKeyboardButton('📄 Licencia Bodega Pro', url=BODEGA_PRO_LICENCIA_URL),
        )
    markup.add(
        types.InlineKeyboardButton('💬 Comprar por WhatsApp', url=get_whatsapp_buy_url(app['nombre'])),
        types.InlineKeyboardButton('🎬 Solicitar Demo', url=get_whatsapp_demo_url(app['nombre'])),
    )
    markup.add(types.InlineKeyboardButton('🛒 Ver en Tienda', url=STORE_URL))
    markup.add(types.InlineKeyboardButton('📋 Catálogo Completo', callback_data='catalog'))
    markup.add(types.InlineKeyboardButton('🔙 Volver al Menú', callback_data='main_menu'))
    return markup

def get_store_inline_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton('🛒 Abrir Tienda Online', url=STORE_URL),
        types.InlineKeyboardButton('💬 WhatsApp', url=f'https://wa.me/{WHATSAPP_CONTACT}'),
    )
    markup.add(types.InlineKeyboardButton('📋 Ver Catálogo', callback_data='catalog'))
    markup.add(types.InlineKeyboardButton('🔙 Volver al Menú', callback_data='main_menu'))
    return markup

def get_purchase_inline_keyboard(app=None):
    markup = types.InlineKeyboardMarkup(row_width=2)
    if app:
        markup.add(
            types.InlineKeyboardButton(f'💬 Comprar {app["nombre"]}', url=get_whatsapp_buy_url(app['nombre'])),
            types.InlineKeyboardButton('🎬 Ver Demo', url=get_whatsapp_demo_url(app['nombre'])),
        )
    else:
        markup.add(
            types.InlineKeyboardButton('💬 Comprar por WhatsApp', url=f'https://wa.me/{WHATSAPP_CONTACT}?text=Quiero%20comprar%20una%20app%20A2K'),
        )
    markup.add(types.InlineKeyboardButton('🛒 Tienda Online', url=STORE_URL))
    markup.add(types.InlineKeyboardButton('📋 Catálogo', callback_data='catalog'))
    return markup

def get_demo_inline_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton('🎬 Solicitar Demo por WhatsApp', url=f'https://wa.me/{WHATSAPP_CONTACT}?text=Quiero%20ver%20una%20demo%20A2K'),
    )
    markup.add(types.InlineKeyboardButton('🛒 Tienda Online', url=STORE_URL))
    markup.add(types.InlineKeyboardButton('📋 Ver Catálogo', callback_data='catalog'))
    return markup

# ==================== MESSAGE BUILDERS ====================

STORE_FOOTER = "\n\n🛒 *Tienda Online:* [A2K Digital Studio]({store})".format(store=STORE_URL)

def build_app_detail_message(app):
    features = "\n".join(f"   {f}" for f in app['caracteristicas'])
    demo_line = ""
    if app.get('demo'):
        demo_line = f"\n🎥 *Demo:* [Ver demo online]({app['demo']})"
    bodega_links = ""
    if app['id'] in ('bodega_descarga', 'mercado_logic'):
        bodega_links = (
            f"\n📋 *Demo Bodega Pro:* [Solicitar]({BODEGA_PRO_DEMO_URL})\n"
            f"📄 *Licencia Bodega Pro:* [Obtener]({BODEGA_PRO_LICENCIA_URL})"
        )
    return (
        "━━━━━━━━━━━━━━━━━━━━━━━\n"
        "{icono} *{nombre}*\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "{desc_larga}\n\n"
        "✨ *Características:*\n"
        "{features}\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n"
        "💰 *Precio: ${precio} USD* | ➕ Terminal: +$5\n"
        "✅ Un solo pago | Soporte incluido"
        "{demo_line}{bodega_links}\n\n"
        "🛒 *Ver en tienda:* [A2K Digital Studio]({store})"
    ).format(
        icono=app['icono'], nombre=app['nombre'],
        desc_larga=app['desc_larga'], features=features,
        precio=app['precio'], demo_line=demo_line,
        bodega_links=bodega_links, store=STORE_URL
    )

def build_catalog_message():
    apps_list = ""
    for i, app in enumerate(A2K_APPS, 1):
        apps_list += f"\n{i}. {app['icono']} *{app['nombre']}*\n   _{app['desc_corta']}_\n"
    return (
        "🛒 *CATÁLOGO COMPLETO - A2K Digital Studio*\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{apps_list}\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n"
        "💰 *Precio: $25 USD* | ➕ Terminal: +$5\n"
        "✅ Un solo pago | Sin mensualidades\n\n"
        "🛒 *Tienda:* [A2K Digital Studio]({store})\n\n"
        "👇 Toca cualquier app para ver más:"
    ).format(store=STORE_URL)

def build_pricing_message():
    return (
        "💰 *PLANES Y PRECIOS - A2K Digital Studio*\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🏷️ *Cada aplicación:* **$25 USD** (pago único)\n"
        "➕ *Terminal adicional:* **+$5 USD**\n\n"
        "✅ *¿Qué incluye?*\n"
        "   • Licencia completa sin restricciones\n"
        "   • Soporte técnico personalizado\n"
        "   • Actualizaciones futuras sin costo\n"
        "   • Tutorial de uso\n"
        "   • Configuración asistida\n\n"
        "🚫 *Nada de:* mensualidades, suscripciones, costos ocultos\n\n"
        "🛒 *Tienda:* [A2K Digital Studio]({store})"
    ).format(store=STORE_URL)

def build_payment_message():
    banks = "\n".join(f"   • {b['n']}" for b in BANCOS_NAC)
    intl = "\n".join(f"   • {b['n']}" for b in BANCOS_INT)
    return (
        "💳 *MÉTODOS DE PAGO - A2K Digital Studio*\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🏦 *Bancos Nacionales (Bs):*\n{banks}\n\n"
        f"💵 *Plataformas Internacionales (USD):*\n{intl}\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "📲 Para datos completos, contacta por WhatsApp.\n\n"
        "🛒 *Tienda:* [A2K Digital Studio]({store})"
    ).format(store=STORE_URL)

def build_payment_full_message():
    nac_lines = ""
    for b in BANCOS_NAC:
        nac_lines += f"\n🏦 *{b['n']}*\n   Cta: `{b['c']}`\n   Titular: {b['t']}\n   CI/RIF: {b['ci']}\n"
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
        f"🏦 *CUENTAS NACIONALES (Bs):*\n{nac_lines}\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"💵 *CUENTAS INTERNACIONALES (USD):*\n{int_lines}\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "⚠️ Envía comprobante por WhatsApp para procesar tu pedido.\n\n"
        f"📱 *WhatsApp:* +58 416-4117331\n\n"
        "🛒 *Tienda:* [A2K Digital Studio]({store})"
    ).format(store=STORE_URL)

def build_contact_message():
    return (
        "👤 *CONTACTO - A2K Digital Studio*\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "👨‍💻 *Ingeniero Abigail Rojas*\n\n"
        "📲 *WhatsApp:* +58 416-4117331\n"
        "📧 *Email:* abijose1158@gmail.com\n"
        "🏢 *Empresa:* Inversiones 2K 3112 C.A\n"
        "   RIF: J-40632338-1\n\n"
        "🛒 *Tienda Online:* [A2K Digital Studio]({store})\n\n"
        "⏰ Horario: Lunes a Sábado, 8:00 AM - 6:00 PM"
    ).format(store=STORE_URL)

def build_store_message():
    return (
        "🛒 *TIENDA ONLINE - A2K Digital Studio*\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "Visita nuestra tienda oficial:\n\n"
        "🔗 [A2K Digital Studio - Tienda Online]({store})\n\n"
        "En la tienda encontrarás:\n"
        "• Descripciones detalladas de cada app\n"
        "• Capturas de pantalla\n"
        "• Enlaces a demos interactivas\n"
        "• Precios actualizados\n\n"
        "🛒 *Enlace directo:* [Abrir Tienda]({store})"
    ).format(store=STORE_URL)

def build_welcome_message(first_name=None):
    name = first_name or "amigo/a"
    time_g = get_time_greeting()
    if time_g == 'buenos_dia':
        time_emoji = '☀️'
    elif time_g == 'buenas_tardes':
        time_emoji = '🌤️'
    else:
        time_emoji = '🌙'
    return (
        f"✨ *A2K Digital Studio*\n"
        f"━ *Soluciones Tecnológicas para tu Negocio*\n\n"
        f"¡Hola {name}! 👋 Bienvenido. Soy *Abi*, tu asistente experta en tecnología para negocios.\n\n"
        f"Creo soluciones que hacen que tu negocio trabaje solo {time_emoji}\n\n"
        f"📌 *¿Qué ofrecemos?*\n"
        f"• 9 aplicaciones profesionales\n"
        f"• Precio único: $25 USD por app\n"
        f"• Un solo pago, sin mensualidades\n"
        f"• Soporte técnico incluido\n"
        f"• Demo en vivo gratis\n\n"
        f"🛒 *Tienda Online:* [A2K Digital Studio]({store})\n\n"
        f"Dime, ¿tienes un negocio? Cuéntame y te recomiendo la app perfecta 😊"
    ).format(store=STORE_URL)

# ==================== FOLLOW-UP THREADING ====================

def send_selling_follow_up(chat_id, app):
    def _send():
        try:
            time.sleep(random.uniform(3, 6))
            msg = smart_choice(FOLLOW_UP_SELLING, chat_id, 'followup')
            bot.send_message(chat_id, msg, parse_mode='Markdown')
            markup = types.InlineKeyboardMarkup()
            markup.add(
                types.InlineKeyboardButton(f'💬 Comprar {app["nombre"]}', url=get_whatsapp_buy_url(app['nombre'])),
            )
            markup.add(types.InlineKeyboardButton('🛒 Tienda Online', url=STORE_URL))
            bot.send_message(chat_id, "👇 ¿Te animas?", reply_markup=markup, parse_mode='Markdown')
        except Exception:
            pass
    thread = threading.Thread(target=_send, daemon=True)
    thread.start()

# ==================== COMMAND HANDLERS ====================

@bot.message_handler(commands=['start'])
def cmd_start(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    username = message.from_user.username or "amigo"
    first_name = message.from_user.first_name

    set_state(user_id, 'nuevo', retorno=is_returning_user(user_id))
    track_interaction(user_id)

    logger.info(f"START - @{username} ({user_id}) Nombre: {first_name}")

    simulate_typing(chat_id, 1.5)

    # Welcome message with store
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton('🛒 Tienda Online', url=STORE_URL),
        types.InlineKeyboardButton('📋 Ver Catálogo', callback_data='catalog'),
    )
    markup.add(
        types.InlineKeyboardButton('🎥 Solicitar Demo', callback_data='demo_general'),
        types.InlineKeyboardButton('💳 Métodos de Pago', callback_data='pagos'),
    )
    markup.add(
        types.InlineKeyboardButton('💰 Ver Precios', callback_data='precios'),
        types.InlineKeyboardButton('👤 Contacto', callback_data='contacto'),
    )

    bot.send_message(
        chat_id, build_welcome_message(first_name),
        parse_mode='Markdown', reply_markup=markup,
        disable_web_page_preview=True
    )

    # Send reply keyboard
    bot.send_message(
        chat_id,
        "📱 *Usa el menú de abajo* para navegar rápido, o simplemente dime qué tipo de negocio tienes y te asesoro gratis 😊\n\n"
        "🛒 *Tienda:* [A2K Digital Studio]({store})".format(store=STORE_URL),
        parse_mode='Markdown',
        reply_markup=get_main_menu_keyboard(),
        disable_web_page_preview=True
    )

    set_state(user_id, 'descubrimiento')

@bot.message_handler(commands=['menu'])
def cmd_menu(message):
    cmd_start(message)

@bot.message_handler(commands=['catalogo', 'catalog'])
def cmd_catalogo(message):
    chat_id = message.chat.id
    set_state(message.from_user.id, 'menu')
    track_interaction(message.from_user.id)
    simulate_typing(chat_id, 1.0)
    bot.send_message(
        chat_id, build_catalog_message(),
        parse_mode='Markdown',
        reply_markup=get_catalog_inline_keyboard(),
        disable_web_page_preview=True
    )

@bot.message_handler(commands=['precios', 'precio', 'prices'])
def cmd_precios(message):
    chat_id = message.chat.id
    set_state(message.from_user.id, 'menu')
    track_interaction(message.from_user.id)
    simulate_typing(chat_id, 1.0)
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton('📋 Ver Catálogo', callback_data='catalog'),
        types.InlineKeyboardButton('🛒 Tienda Online', url=STORE_URL),
    )
    markup.add(types.InlineKeyboardButton('🔙 Menú Principal', callback_data='main_menu'))
    bot.send_message(
        chat_id, build_pricing_message(),
        parse_mode='Markdown', reply_markup=markup,
        disable_web_page_preview=True
    )

@bot.message_handler(commands=['demo'])
def cmd_demo(message):
    chat_id = message.chat.id
    set_state(message.from_user.id, 'demo_request')
    track_interaction(message.from_user.id)
    simulate_typing(chat_id, 1.0)
    msg = smart_choice(DEMO_VARIATIONS, message.from_user.id, 'demo')
    bot.send_message(chat_id, msg, parse_mode='Markdown', reply_markup=get_demo_inline_keyboard())

@bot.message_handler(commands=['pagos', 'pago'])
def cmd_pagos(message):
    chat_id = message.chat.id
    set_state(message.from_user.id, 'payment')
    track_interaction(message.from_user.id)
    simulate_typing(chat_id, 1.0)
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton('📋 Ver Datos Completos', callback_data='pagos_full'),
        types.InlineKeyboardButton('💬 WhatsApp', url=f'https://wa.me/{WHATSAPP_CONTACT}?text=Necesito%20datos%20de%20pago%20A2K'),
    )
    markup.add(types.InlineKeyboardButton('🛒 Tienda Online', url=STORE_URL))
    markup.add(types.InlineKeyboardButton('🔙 Menú', callback_data='main_menu'))
    bot.send_message(
        chat_id, build_payment_message(),
        parse_mode='Markdown', reply_markup=markup
    )

@bot.message_handler(commands=['contacto', 'contact'])
def cmd_contacto(message):
    chat_id = message.chat.id
    track_interaction(message.from_user.id)
    simulate_typing(chat_id, 1.0)
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton('💬 WhatsApp', url=f'https://wa.me/{WHATSAPP_CONTACT}'),
        types.InlineKeyboardButton('🛒 Tienda Online', url=STORE_URL),
    )
    markup.add(types.InlineKeyboardButton('🔙 Menú', callback_data='main_menu'))
    bot.send_message(
        chat_id, build_contact_message(),
        parse_mode='Markdown', reply_markup=markup,
        disable_web_page_preview=True
    )

@bot.message_handler(commands=['tienda', 'store'])
def cmd_tienda(message):
    chat_id = message.chat.id
    track_interaction(message.from_user.id)
    simulate_typing(chat_id, 1.0)
    bot.send_message(
        chat_id, build_store_message(),
        parse_mode='Markdown', reply_markup=get_store_inline_keyboard(),
        disable_web_page_preview=True
    )

@bot.message_handler(commands=['bodegapro'])
def cmd_bodegapro(message):
    chat_id = message.chat.id
    track_interaction(message.from_user.id)
    app = next((a for a in A2K_APPS if a['id'] == 'bodega_descarga'), None)
    if app:
        simulate_typing(chat_id, 1.5)
        bot.send_message(
            chat_id, build_app_detail_message(app),
            parse_mode='Markdown',
            reply_markup=get_app_detail_keyboard(app),
            disable_web_page_preview=True
        )

# ==================== CALLBACK QUERY HANDLER ====================

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    data = call.data
    username = call.from_user.username or 'unknown'

    logger.info(f"CALLBACK - @{username}: {data}")

    bot.answer_callback_query(call.id)

    if data == 'main_menu':
        simulate_typing(chat_id, 0.5)
        bot.send_message(
            chat_id,
            "📂 *Menú Principal*\n\n¿En qué te puedo ayudar? 😊\n\n"
            "🛒 *Tienda:* [A2K Digital Studio]({store})".format(store=STORE_URL),
            parse_mode='Markdown',
            reply_markup=get_main_menu_keyboard(),
            disable_web_page_preview=True
        )
        set_state(user_id, 'descubrimiento')

    elif data == 'catalog':
        simulate_typing(chat_id, 0.5)
        bot.send_message(
            chat_id, build_catalog_message(),
            parse_mode='Markdown',
            reply_markup=get_catalog_inline_keyboard(),
            disable_web_page_preview=True
        )
        set_state(user_id, 'menu')

    elif data.startswith('app_'):
        app_id = data.replace('app_', '')
        app = next((a for a in A2K_APPS if a['id'] == app_id), None)
        if app:
            simulate_typing(chat_id, 1.0)
            bot.send_message(
                chat_id, build_app_detail_message(app),
                parse_mode='Markdown',
                reply_markup=get_app_detail_keyboard(app),
                disable_web_page_preview=True
            )
            set_state(user_id, 'presentacion', app_interes=app['id'])
            log_venta_lead(username, user_id, app['nombre'], f"Callback: {data}", 'catalogo')

    elif data.startswith('demo_'):
        app_id = data.replace('demo_', '')
        app = next((a for a in A2K_APPS if a['id'] == app_id), None)
        if app:
            simulate_typing(chat_id, 0.5)
            msg = smart_choice(DEMO_VARIATIONS, user_id, 'demo')
            bot.send_message(chat_id, msg, parse_mode='Markdown')
            simulate_typing(chat_id, 0.5)
            markup = types.InlineKeyboardMarkup()
            markup.add(
                types.InlineKeyboardButton('🎬 Ver Demo', url=get_whatsapp_demo_url(app['nombre'])),
                types.InlineKeyboardButton('🛒 Tienda Online', url=STORE_URL),
            )
            bot.send_message(chat_id, "👇 Agenda tu demo ahora:", reply_markup=markup)

    elif data == 'precios':
        simulate_typing(chat_id, 0.5)
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton('📋 Catálogo', callback_data='catalog'),
            types.InlineKeyboardButton('🛒 Tienda Online', url=STORE_URL),
        )
        bot.send_message(
            chat_id, build_pricing_message(),
            parse_mode='Markdown', reply_markup=markup,
            disable_web_page_preview=True
        )

    elif data == 'pagos':
        simulate_typing(chat_id, 0.5)
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton('📋 Datos Completos', callback_data='pagos_full'),
            types.InlineKeyboardButton('💬 WhatsApp', url=f'https://wa.me/{WHATSAPP_CONTACT}?text=Datos%20de%20pago%20A2K'),
        )
        markup.add(types.InlineKeyboardButton('🛒 Tienda', url=STORE_URL))
        bot.send_message(chat_id, build_payment_message(), parse_mode='Markdown', reply_markup=markup)

    elif data == 'pagos_full':
        simulate_typing(chat_id, 0.5)
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('🔙 Volver', callback_data='pagos'))
        markup.add(types.InlineKeyboardButton('🛒 Tienda', url=STORE_URL))
        bot.send_message(chat_id, build_payment_full_message(), parse_mode='Markdown', reply_markup=markup)

    elif data == 'demo_general':
        simulate_typing(chat_id, 0.5)
        msg = smart_choice(DEMO_VARIATIONS, user_id, 'demo')
        bot.send_message(chat_id, msg, parse_mode='Markdown', reply_markup=get_demo_inline_keyboard())

    elif data == 'contacto':
        simulate_typing(chat_id, 0.5)
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton('💬 WhatsApp', url=f'https://wa.me/{WHATSAPP_CONTACT}'),
            types.InlineKeyboardButton('🛒 Tienda', url=STORE_URL),
        )
        bot.send_message(
            chat_id, build_contact_message(),
            parse_mode='Markdown', reply_markup=markup,
            disable_web_page_preview=True
        )

    elif data == 'otros_productos':
        simulate_typing(chat_id, 1.0)
        send_other_products(chat_id)

    elif data == 'tienda':
        simulate_typing(chat_id, 0.5)
        bot.send_message(
            chat_id, build_store_message(),
            parse_mode='Markdown', reply_markup=get_store_inline_keyboard(),
            disable_web_page_preview=True
        )

# ==================== OTHER PRODUCTS ====================

def send_other_products(chat_id):
    """Envía los productos de Amazon y AliExpress."""
    msg = (
        "🛒 *OTROS PRODUCTOS - A2K Digital Studio*\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🇪🇸 *Amazon España:*\n"
    )
    for cat, products in AMAZON_ES.items():
        for p in products:
            msg += f"   {p['nombre']} — [Ver]({p['link']})\n"
    msg += "\n🇺🇸 *Amazon USA:*\n"
    for cat, products in AMAZON_USA.items():
        for p in products:
            msg += f"   {p['nombre']} — [Ver]({p['link']})\n"
    msg += "\n🌍 *AliExpress:*\n"
    for p in ALIEXPRESS:
        msg += f"   {p['nombre']} — [Ver]({p['link']})\n"
    msg += f"\n🛒 *Tienda A2K:* [A2K Digital Studio]({STORE_URL})"

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('🛒 Tienda A2K', url=STORE_URL))
    markup.add(types.InlineKeyboardButton('📋 Catálogo A2K', callback_data='catalog'))
    markup.add(types.InlineKeyboardButton('🔙 Menú', callback_data='main_menu'))
    bot.send_message(chat_id, msg, parse_mode='Markdown', reply_markup=markup, disable_web_page_preview=True)

# ==================== MAIN TEXT HANDLER (STATE MACHINE) ====================

@bot.message_handler(func=lambda message: True, content_types=['text'])
def handle_smart_text(message):
    """Handler principal con state machine y flujo de marketing conversacional."""
    chat_id = message.chat.id
    user_id = message.from_user.id
    text = message.text.strip()
    text_lower = text.lower()
    username = message.from_user.username or 'unknown'

    logger.info(f"TEXTO - @{username} ({user_id}): {text}")

    state = get_state(user_id)
    flow = state.get('flow', 'nuevo')
    interaction_count = track_interaction(user_id)

    simulate_typing(chat_id, random.uniform(0.8, 2.0))

    # ====== BUTTON TEXT HANDLERS ======
    if text == '🛒 Tienda Online':
        bot.send_message(
            chat_id, build_store_message(),
            parse_mode='Markdown', reply_markup=get_store_inline_keyboard(),
            disable_web_page_preview=True
        )
        return

    if text == '📋 Catálogo A2K':
        bot.send_message(
            chat_id, build_catalog_message(),
            parse_mode='Markdown',
            reply_markup=get_catalog_inline_keyboard(),
            disable_web_page_preview=True
        )
        set_state(user_id, 'menu')
        return

    if text == '💰 Precios':
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton('📋 Catálogo', callback_data='catalog'),
            types.InlineKeyboardButton('🛒 Tienda Online', url=STORE_URL),
        )
        bot.send_message(
            chat_id, smart_choice(PRICE_VARIATIONS, user_id, 'precio'),
            parse_mode='Markdown', reply_markup=markup,
            disable_web_page_preview=True
        )
        return

    if text == '💳 Métodos de Pago':
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton('📋 Datos Completos', callback_data='pagos_full'),
            types.InlineKeyboardButton('💬 WhatsApp', url=f'https://wa.me/{WHATSAPP_CONTACT}?text=Datos%20de%20pago'),
        )
        markup.add(types.InlineKeyboardButton('🛒 Tienda', url=STORE_URL))
        bot.send_message(chat_id, build_payment_message(), parse_mode='Markdown', reply_markup=markup)
        return

    if text == '🎥 Ver Demo':
        msg = smart_choice(DEMO_VARIATIONS, user_id, 'demo')
        bot.send_message(chat_id, msg, parse_mode='Markdown', reply_markup=get_demo_inline_keyboard())
        return

    if text == '👤 Contacto':
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton('💬 WhatsApp', url=f'https://wa.me/{WHATSAPP_CONTACT}'),
            types.InlineKeyboardButton('🛒 Tienda', url=STORE_URL),
        )
        bot.send_message(
            chat_id, build_contact_message(),
            parse_mode='Markdown', reply_markup=markup,
            disable_web_page_preview=True
        )
        return

    if text == '🛒 Otros Productos':
        simulate_typing(chat_id, 1.0)
        send_other_products(chat_id)
        return

    # ====== PHASE 5: CLOSING — purchase intent ======
    if is_purchase_intent(text):
        app = find_app_by_keywords(text)
        app_interes = state.get('app_interes')
        if not app and app_interes:
            app = next((a for a in A2K_APPS if a['id'] == app_interes), None)

        app_name = app['nombre'] if app else 'app A2K'
        log_venta_lead(username, user_id, app_name, text, 'cierre')

        cierre = smart_choice(CIERRES, user_id, 'cierre')
        bot.send_message(chat_id, cierre, parse_mode='Markdown')

        simulate_typing(chat_id, 0.5)
        bot.send_message(
            chat_id,
            "👇 Elige tu opción:",
            reply_markup=get_purchase_inline_keyboard(app)
        )
        set_state(user_id, 'cierre', app_interes=app['id'] if app else None)
        return

    # ====== OBJECTION HANDLING ======
    objection = detect_objection(text)
    if objection:
        state['ultima_objecion'] = objection
        user_states[user_id] = state
        responses = OBJECIONES[objection]['respuestas']
        resp = smart_choice(responses, user_id, f'objecion_{objection}')

        log_venta_lead(username, user_id, state.get('app_interes', 'general'), text, f'objecion:{objection}')

        bot.send_message(chat_id, resp, parse_mode='Markdown')

        # After objection, follow up with relevant buttons
        simulate_typing(chat_id, 0.5)
        app_interes = state.get('app_interes')
        app = next((a for a in A2K_APPS if a['id'] == app_interes), None) if app_interes else None
        markup = types.InlineKeyboardMarkup()
        if app:
            markup.add(
                types.InlineKeyboardButton('🎬 Ver Demo', url=get_whatsapp_demo_url(app['nombre'])),
                types.InlineKeyboardButton('🛒 Tienda', url=STORE_URL),
            )
        else:
            markup.add(
                types.InlineKeyboardButton('🎬 Solicitar Demo', callback_data='demo_general'),
                types.InlineKeyboardButton('🛒 Tienda', url=STORE_URL),
            )
        markup.add(types.InlineKeyboardButton('📋 Catálogo', callback_data='catalog'))
        bot.send_message(chat_id, "👇 ¿Qué prefieres?", reply_markup=markup)
        return

    # ====== GOODBYE ======
    if is_goodbye(text) and len(text) < 40:
        resp = smart_choice(GOODBYE_VARIATIONS, user_id, 'goodbye')
        bot.send_message(chat_id, resp, parse_mode='Markdown', disable_web_page_preview=True)
        return

    # ====== THANK YOU ======
    if is_thank_you(text) and len(text) < 40:
        resp = smart_choice(THANK_YOU_VARIATIONS, user_id, 'thanks')
        bot.send_message(chat_id, resp, parse_mode='Markdown', disable_web_page_preview=True)
        return

    # ====== PAYMENT REQUEST ======
    if is_payment_request(text):
        bot.send_message(chat_id, "Te muestro las opciones de pago 💳", parse_mode='Markdown')
        simulate_typing(chat_id, 0.5)
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton('📋 Datos Completos', callback_data='pagos_full'),
            types.InlineKeyboardButton('💬 WhatsApp', url=f'https://wa.me/{WHATSAPP_CONTACT}?text=Datos%20de%20pago'),
        )
        markup.add(types.InlineKeyboardButton('🛒 Tienda', url=STORE_URL))
        bot.send_message(chat_id, build_payment_message(), parse_mode='Markdown', reply_markup=markup)
        return

    # ====== PRICE QUESTION ======
    if is_price_question(text):
        resp = smart_choice(PRICE_VARIATIONS, user_id, 'precio')
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton('📋 Catálogo', callback_data='catalog'),
            types.InlineKeyboardButton('🛒 Tienda', url=STORE_URL),
        )
        bot.send_message(chat_id, resp, parse_mode='Markdown', reply_markup=markup, disable_web_page_preview=True)
        return

    # ====== DEMO REQUEST ======
    if is_demo_request(text):
        msg = smart_choice(DEMO_VARIATIONS, user_id, 'demo')
        bot.send_message(chat_id, msg, parse_mode='Markdown', reply_markup=get_demo_inline_keyboard())
        return

    # ====== CONTACT REQUEST ======
    if is_contact_request(text):
        bot.send_message(chat_id, "Claro, aquí tienes los datos 👇", parse_mode='Markdown')
        simulate_typing(chat_id, 0.5)
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton('💬 WhatsApp', url=f'https://wa.me/{WHATSAPP_CONTACT}'),
            types.InlineKeyboardButton('🛒 Tienda', url=STORE_URL),
        )
        bot.send_message(
            chat_id, build_contact_message(),
            parse_mode='Markdown', reply_markup=markup,
            disable_web_page_preview=True
        )
        return

    # ====== STORE REQUEST ======
    if is_store_request(text):
        bot.send_message(chat_id, "¡Claro! Aquí tienes nuestra tienda 🛒", parse_mode='Markdown')
        simulate_typing(chat_id, 0.5)
        bot.send_message(
            chat_id, build_store_message(),
            parse_mode='Markdown', reply_markup=get_store_inline_keyboard(),
            disable_web_page_preview=True
        )
        return

    # ====== BUSINESS DETECTION + SALES PITCH ======
    app, tipo_negocio = recommend_app_for_business(text)
    if app:
        log_venta_lead(username, user_id, app['nombre'], text, 'descubrimiento')
        set_state(user_id, 'presentacion', app_interes=app['id'])

        # Select pitch variation (cycle through 3)
        pitch_count = get_pitch_count(user_id, app['id'])
        pitches = SALES_PITCHES.get(app['id'], [])
        if pitches:
            pitch = pitches[pitch_count % len(pitches)]
            mark_pitch_seen(user_id, app['id'])
        else:
            pitch = build_app_detail_message(app)

        # Context-aware intro
        if is_greeting(text) or 'tengo' in text_lower or 'mi negocio' in text_lower:
            intro = f"¡Qué bueno! Un negocio de *{tipo_negocio}*... 😊 Déjame mostrarte algo que te va a encantar:\n\n"
        else:
            intro = ""

        bot.send_message(chat_id, intro + pitch, parse_mode='Markdown')

        simulate_typing(chat_id, 1.0)
        bot.send_message(
            chat_id, build_app_detail_message(app),
            parse_mode='Markdown',
            reply_markup=get_app_detail_keyboard(app),
            disable_web_page_preview=True
        )

        # Send follow-up selling in background
        send_selling_follow_up(chat_id, app)
        return

    # ====== APP BY KEYWORDS ======
    app = find_app_by_keywords(text)
    if app:
        set_state(user_id, 'presentacion', app_interes=app['id'])
        log_venta_lead(username, user_id, app['nombre'], text, 'interes')

        bot.send_message(
            chat_id,
            f"¡Creo que te refieres a *{app['icono']} {app['nombre']}*! 🎯 Déjame mostrarte:",
            parse_mode='Markdown'
        )
        simulate_typing(chat_id, 1.0)
        bot.send_message(
            chat_id, build_app_detail_message(app),
            parse_mode='Markdown',
            reply_markup=get_app_detail_keyboard(app),
            disable_web_page_preview=True
        )

        send_selling_follow_up(chat_id, app)
        return

    # ====== PHASE 1: GREETING → Discovery ======
    if is_greeting(text) and len(text) < 40:
        state = get_state(user_id)
        if flow in ('nuevo', 'descubrimiento'):
            # First interaction: greet warmly, ask about business
            greeting = get_greeting(user_id)
            bot.send_message(chat_id, greeting, parse_mode='Markdown')

            simulate_typing(chat_id, random.uniform(1.0, 2.0))
            pregunta = smart_choice(PREGUNTAS_NEGOCIO, user_id, 'negocio')
            bot.send_message(
                chat_id,
                pregunta + "\n\n🛒 *O visita nuestra tienda:* [A2K Digital Studio]({store})".format(store=STORE_URL),
                parse_mode='Markdown',
                reply_markup=get_main_menu_keyboard(),
                disable_web_page_preview=True
            )
            set_state(user_id, 'descubrimiento')
        else:
            # Returning to conversation after seeing content
            greeting = get_greeting(user_id)
            bot.send_message(
                chat_id,
                greeting + "\n\n¿Quieres seguir viendo algo o te ayudo con otra cosa?\n\n"
                "🛒 *Tienda:* [A2K Digital Studio]({store})".format(store=STORE_URL),
                parse_mode='Markdown',
                disable_web_page_preview=True
            )
        return

    # ====== BUSINESS FOLLOWUP (when in discovery state) ======
    if flow == 'descubrimiento' and interaction_count >= 2:
        # User has been asked about business but hasn't specified
        # Try to be more helpful
        app, tipo_negocio = recommend_app_for_business(text)
        if app:
            # Already handled above
            pass
        else:
            # Ask followup business question
            followup = smart_choice(PREGUNTAS_NEGOCIO_FOLLOWUP, user_id, 'negocio_followup')
            bot.send_message(
                chat_id,
                followup + "\n\nO si prefieres, puedes ver todo lo que tenemos:\n\n"
                "🛒 *Tienda:* [A2K Digital Studio]({store})".format(store=STORE_URL),
                parse_mode='Markdown',
                disable_web_page_preview=True
            )
            return

    # ====== UNKNOWN MESSAGE ======
    resp = smart_choice(UNKNOWN_VARIATIONS, user_id, 'unknown')
    bot.send_message(chat_id, resp, parse_mode='Markdown', disable_web_page_preview=True)

    # Show helpful options
    simulate_typing(chat_id, 1.0)
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton('📋 Catálogo A2K', callback_data='catalog'),
        types.InlineKeyboardButton('🛒 Tienda Online', url=STORE_URL),
    )
    markup.add(types.InlineKeyboardButton('💰 Precios', callback_data='precios'))
    bot.send_message(chat_id, "👇 ¿Qué te gustaría hacer?", reply_markup=markup)


# ==================== ERROR HANDLER ====================

@bot.message_handler(func=lambda message: True, content_types=['photo', 'document', 'sticker', 'voice', 'video'])
def handle_non_text(message):
    chat_id = message.chat.id
    simulate_typing(chat_id, 1.0)
    bot.send_message(
        chat_id,
        "Jaja, gracias por enviar eso 😄 Pero soy mejor con texto. Cuéntame, "
        "¿tienes un negocio? Dime el tipo y te asesoro gratis 💪\n\n"
        "🛒 *Tienda:* [A2K Digital Studio]({store})".format(store=STORE_URL),
        parse_mode='Markdown',
        disable_web_page_preview=True
    )


# ==================== CROSS-SELL HELPER ====================

def get_cross_sell_message(user_id, current_app_id):
    """Genera un mensaje de cross-selling para una app relacionada."""
    related_ids = APPS_CROSS_SELL.get(current_app_id, [])
    if not related_ids:
        return None
    related_app = next((a for a in A2K_APPS if a['id'] == random.choice(related_ids)), None)
    if not related_app:
        return None
    msg_template = random.choice(CROSS_SELL_MESSAGES)
    return msg_template.format(nombre=related_app['nombre'], icono=related_app['icono'])

# ==================== STATE TRANSITION HELPERS ====================

def transition_to_discovery(user_id, chat_id):
    """Transición al estado de descubrimiento con pregunta de negocio."""
    pregunta = smart_choice(PREGUNTAS_NEGOCIO, user_id, 'negocio')
    bot.send_message(
        chat_id,
        pregunta + "\n\n🛒 *O visita nuestra tienda:* [A2K Digital Studio]({store})".format(store=STORE_URL),
        parse_mode='Markdown',
        reply_markup=get_main_menu_keyboard(),
        disable_web_page_preview=True
    )
    set_state(user_id, 'descubrimiento')

def transition_to_pitch(user_id, chat_id, app, tipo_negocio=None):
    """Transición al estado de presentación con pitch de venta."""
    username = 'user'
    log_venta_lead(username, user_id, app['nombre'], 'auto_pitch', 'presentacion')
    set_state(user_id, 'presentacion', app_interes=app['id'])

    pitches = SALES_PITCHES.get(app['id'], [])
    pitch_count = get_pitch_count(user_id, app['id'])
    if pitches:
        pitch = pitches[pitch_count % len(pitches)]
        mark_pitch_seen(user_id, app['id'])
    else:
        pitch = build_app_detail_message(app)

    intro = ""
    if tipo_negocio:
        intro = f"¡Qué bueno! Un negocio de *{tipo_negocio}*... 😊 Déjame mostrarte algo que te va a encantar:\n\n"

    bot.send_message(chat_id, intro + pitch, parse_mode='Markdown')

    simulate_typing(chat_id, 1.0)
    bot.send_message(
        chat_id, build_app_detail_message(app),
        parse_mode='Markdown',
        reply_markup=get_app_detail_keyboard(app),
        disable_web_page_preview=True
    )

    send_selling_follow_up(chat_id, app)

def transition_to_closing(user_id, chat_id, app=None):
    """Transición al estado de cierre de venta."""
    cierre = smart_choice(CIERRES, user_id, 'cierre')
    bot.send_message(chat_id, cierre, parse_mode='Markdown')

    simulate_typing(chat_id, 0.5)
    bot.send_message(
        chat_id, "👇 Elige tu opción:",
        reply_markup=get_purchase_inline_keyboard(app)
    )
    set_state(user_id, 'cierre', app_interes=app['id'] if app else None)

def handle_objection_with_followup(user_id, chat_id, objection_category, state):
    """Maneja una objeción y ofrece seguimiento."""
    responses = OBJECIONES[objection_category]['respuestas']
    resp = smart_choice(responses, user_id, f'objecion_{objection_category}')

    bot.send_message(chat_id, resp, parse_mode='Markdown')

    simulate_typing(chat_id, 0.5)
    app_interes = state.get('app_interes')
    app = next((a for a in A2K_APPS if a['id'] == app_interes), None) if app_interes else None

    markup = types.InlineKeyboardMarkup()
    if app:
        markup.add(
            types.InlineKeyboardButton('🎬 Ver Demo', url=get_whatsapp_demo_url(app['nombre'])),
            types.InlineKeyboardButton('🛒 Tienda', url=STORE_URL),
        )
    else:
        markup.add(
            types.InlineKeyboardButton('🎬 Demo', callback_data='demo_general'),
            types.InlineKeyboardButton('🛒 Tienda', url=STORE_URL),
        )
    markup.add(types.InlineKeyboardButton('📋 Catálogo', callback_data='catalog'))
    bot.send_message(chat_id, "👇 ¿Qué prefieres?", reply_markup=markup)

# ==================== BOT START ====================

if __name__ == '__main__':
    logger.info("=" * 50)
    logger.info("A2K Digital Studio - Telegram Bot v5.0")
    logger.info("Asistente de Ventas - Marketing Expert")
    logger.info("=" * 50)
    print("=" * 50)
    print("A2K Digital Studio - Telegram Bot v5.0")
    print("Marketing Expert - Conversational Sales Bot")
    print("=" * 50)
    try:
        bot.infinity_polling(timeout=60, long_polling_timeout=60)
    except Exception as e:
        logger.error(f"Error en infinity_polling: {e}")
        time.sleep(5)
        bot.infinity_polling(timeout=60, long_polling_timeout=60)
