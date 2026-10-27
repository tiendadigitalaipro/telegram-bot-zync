#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A2K Digital Studio - Telegram Bot Start Script
Flask server to keep Render web service alive + bot runner
"""

import os
import threading
import logging
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
    """Health check endpoint for Render and UptimeRobot"""
    return jsonify({
        "status": "ok",
        "service": "A2K Digital Studio - Telegram Bot",
        "version": "5.0"
    }), 200

@app.route('/health')
def health():
    """Additional health endpoint"""
    return jsonify({"status": "healthy"}), 200

@app.route('/ping')
def ping():
    """Simple ping endpoint"""
    return "pong", 200

def run_bot():
    """Import and run the Telegram bot in a separate thread"""
    try:
        import telegram_bot_zync_v2
        logger.info("Starting Telegram bot...")
        telegram_bot_zync_v2.bot.infinity_polling(
            timeout=60,
            long_polling_timeout=60
        )
    except Exception as e:
        logger.error(f"Bot error: {e}")

if __name__ == '__main__':
    # Start bot in background thread
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    logger.info("Bot thread started")

    # Run Flask app (this blocks - Render expects this)
    port = int(os.environ.get('PORT', 10000))
    logger.info(f"Starting Flask server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
