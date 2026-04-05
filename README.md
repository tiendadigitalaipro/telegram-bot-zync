# 🤖 A2K Digital Studio - Bot de Ventas por Telegram v4.0

Bot profesional de ventas para Telegram diseñado para **A2K Digital Studio**, especializado en la comercialización de sistemas POS y aplicaciones de gestión empresarial.

---

## 📋 Descripción

Asistente virtual conversacional con estilo venezolano que automatiza el proceso de ventas de 9 aplicaciones de gestión empresarial. El bot detecta intenciones del usuario, recomienda aplicaciones según el tipo de negocio, realiza seguimiento de leads y cierra ventas redirigiendo a WhatsApp.

### Características Principales

- 🧠 **Motor de Recomendación de Negocios** — Detecta el tipo de negocio del usuario (barbería, ferretería, farmacia, etc.) y recomienda la app ideal automáticamente
- 📊 **Seguimiento de Ventas/Leads** — Registra todas las intenciones de compra e interés en un archivo `ventas_telegram.txt`
- 💬 **Detección Inteligente de Intenciones** — 12 niveles de prioridad sin conflictos entre detectores
- 🎯 **Follow-ups de Venta Automáticos** — Mensajes persuasivos enviados con delay de 3-5 segundos
- 📈 **Contexto Conversacional** — Seguimiento de interacciones por usuario; push de venta en la 3ra+ interacción
- 🛒 **Catálogo Completo** — 9 aplicaciones, productos Amazon ES/USA y AliExpress
- 💳 **Métodos de Pago** — 9 bancos nacionales + 10 plataformas internacionales
- 🔗 **Enlaces Bodega Pro** — Formularios específicos de demo y licencia
- 👤 **Bienvenida Personalizada** — Usa el nombre del usuario del perfil de Telegram
- 🎨 **Variaciones de Respuesta** — 8+ variaciones por tipo de respuesta para sentirse humano
- ⌨️ **Teclado Persistente** — Menú siempre visible para navegación rápida

---

## 🏪 Aplicaciones en Catálogo

| # | App | Icono | Precio |
|---|-----|-------|--------|
| 1 | Barbería Pro | 💈 | $25 USD |
| 2 | Nail Studio Pro | 💅 | $25 USD |
| 3 | Repuestos de Motos Pro | 🏍️ | $25 USD |
| 4 | Ferretería A2K Pro | 🔧 | $25 USD |
| 5 | Bodega Descarga Pro | 📦 | $25 USD |
| 6 | MERCADO LOGIC PRO | 🛒 | $25 USD |
| 7 | Farmacia Pro Plus | 💊 | $25 USD |
| 8 | Frutería Pro | 🍎 | $25 USD |
| 9 | Bodega Pro Cloud | ☁️ | $25 USD |

---

## 🔧 Instalación

### Requisitos

- Python 3.7+
- Cuenta de Telegram con Bot Token

### Pasos

```bash
# 1. Clonar o copiar el proyecto
cd telegram-bot-zync/

# 2. Crear entorno virtual (recomendado)
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 3. Instalar dependencias
pip install pyTelegramBotAPI

# 4. Configurar el token (editar telegram-bot-zync-v2.py o usar variable de entorno)
# El token ya está configurado en el archivo

# 5. Ejecutar el bot
python telegram-bot-zync-v2.py
```

---

## ⚙️ Configuración

### Variables principales (al inicio del archivo)

| Variable | Descripción | Valor por defecto |
|----------|-------------|-------------------|
| `BOT_TOKEN` | Token del bot de Telegram | Configurado |
| `STORE_URL` | URL de la tienda online | `https://tiendadigitalaipro.github.io/a2k-digital-studio/` |
| `WHATSAPP_CONTACT` | Número de WhatsApp para ventas | `584164117331` |
| `VENTAS_FILE` | Archivo de seguimiento de leads | `ventas_telegram.txt` |
| `BODEGA_PRO_DEMO_URL` | Formulario demo Bodega Pro | Configurado |
| `BODEGA_PRO_LICENCIA_URL` | Formulario licencia Bodega Pro | Configurado |

---

## 🚀 Despliegue

### Local

```bash
python telegram-bot-zync-v2.py
```

### Servidor / VPS (con systemd)

Crear archivo `/etc/systemd/system/a2k-bot.service`:

```ini
[Unit]
Description=A2K Digital Studio Telegram Bot
After=network.target

[Service]
Type=simple
User=tu_usuario
WorkingDirectory=/ruta/al/proyecto
ExecStart=/ruta/al/venv/bin/python telegram-bot-zync-v2.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable a2k-bot
sudo systemctl start a2k-bot
sudo systemctl status a2k-bot
```

### Con Docker (opcional)

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY telegram-bot-zync-v2.py .
RUN pip install pyTelegramBotAPI
CMD ["python", "telegram-bot-zync-v2.py"]
```

---

## 📁 Estructura del Proyecto

```
telegram-bot-zync/
├── telegram-bot-zync-v2.py   # Bot principal (archivo único)
├── ventas_telegram.txt        # Seguimiento de leads (se crea automáticamente)
└── README.md                  # Este archivo
```

---

## 🗂️ Flujo del Bot

```
Usuario envía /start o "hola"
    │
    ├─→ Bienvenida personalizada con nombre
    │
    ├─→ Describe su negocio ("tengo una barbería")
    │       │
    │       └─→ Motor de recomendación detecta tipo
    │               │
    │               └─→ Muestra app ideal + detalles + follow-up de venta
    │
    ├─→ Pregunta precio
    │       │
    │       └─→ Muestra planes y precios con variaciones
    │
    ├─→ Quiere comprar
    │       │
    │       ├─→ Registra lead en ventas_telegram.txt
    │       └─→ Redirige a WhatsApp con mensaje pre-llenado
    │
    ├─→ Explora catálogo
    │       │
    │       └─→ 9 apps inline → detalle → compra/demo
    │
    ├─→ Otros productos
    │       │
    │       └─→ Amazon ES / Amazon USA / AliExpress
    │
    └─→ 3+ interacciones sin comprar
            │
            └─→ Push de venta ("soporte prioritario", etc.)
```

---

## 📊 Seguimiento de Ventas

El archivo `ventas_telegram.txt` registra automáticamente:

```
[2025-01-15 14:30:22] | User: @juan_perez | ID: 123456789 | App: Barbería Pro | Mensaje: tengo una barbería
[2025-01-15 14:31:05] | User: @juan_perez | ID: 123456789 | App: Barbería Pro | Mensaje: quiero comprar
[2025-01-15 14:35:00] | User: @maria_garcia | ID: 987654321 | App: general | Mensaje: necesito información
```

---

## 🛠️ Stack Tecnológico

| Tecnología | Versión | Uso |
|------------|---------|-----|
| Python | 3.7+ | Lenguaje principal |
| pyTelegramBotAPI | latest | Librería del bot de Telegram |
| threading | stdlib | Follow-ups asíncronos |
| logging | stdlib | Registro de eventos |
| datetime | stdlib | Timestamps |

---

## 📝 Comandos Disponibles

| Comando | Descripción |
|---------|-------------|
| `/start` | Mensaje de bienvenida |
| `/menu` | Menú principal |
| `/catalogo` | Catálogo completo de apps |
| `/precios` | Planes y precios |
| `/demo` | Solicitar demo en vivo |
| `/pagos` | Métodos de pago |
| `/contacto` | Datos de contacto |
| `/tienda` | Link a tienda online |
| `/bodegapro` | Info directa de Bodega Pro |

---

## 🔄 Historial de Versiones

### v4.0 (Actual)
- Motor de recomendación de negocios
- Seguimiento de ventas/leads
- Detección de intenciones sin conflictos
- Follow-ups de venta automáticos
- Enlaces Bodega Pro (demo + licencia)
- Bienvenida personalizada
- Seguimiento de contexto conversacional
- Variaciones de respuesta ampliadas (8+ por tipo)
- Push de venta para usuarios recurrentes

### v3.0
- Catálogo completo 9 apps
- Amazon ES/USA y AliExpress
- Teclado persistente
- Callback handlers completos

---

## 👨‍💻 Desarrollado por

**Ingeniero Abigail Rojas**  
📧 abijose1158@gmail.com  
🏢 Inversiones 2K 3112 C.A — RIF: J-40632338-1  
🌐 [A2K Digital Studio](https://tiendadigitalaipro.github.io/a2k-digital-studio/)

---

## 📄 Licencia

Software propietario. Todos los derechos reservados © Inversiones 2K 3112 C.A
