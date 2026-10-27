#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A2K Digital Studio - Telegram Bot Start Script
Flask server to keep Render web service alive + bot runner
"""

import os
import threading
import logging
import runpy
from flask import Flask, jsonify

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/')
def health_check():
    return jsonify({
        "status": "ok",
        "service": "A2K Digital Studio - Telegram Bot",
        "version": "5.0"
    }), 200

@app.route('/health')
def health():
    return jsonify({"status": "healthy"}), 200

@app.route('/ping')
def ping():
    return "pong", 200

def run_bot():
    try:
        logger.info("Starting Telegram bot...")
        # Ejecuta el archivo del bot tal cual, como si lo llamaras desde la terminal
        runpy.run_path("telegram-bot-zync-v2.py", run_name="__main__")
    except Exception as e:
        logger.error(f"Bot error: {e}")

if __name__ == '__main__':
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    logger.info("Bot thread started")

    port = int(os.environ.get('PORT', 10000))
    logger.info(f"Starting Flask server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
