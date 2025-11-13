#!/usr/bin/env python3
"""
Wrapper to start pymushra server without debug/reloader
"""
import sys
import os

print("🚀 Starting pymushra server wrapper...", flush=True)

try:
    print("📦 Importing pymushra modules...", flush=True)
    # Import and modify pymushra to disable debug
    from pymushra import service
    from tinydb import TinyDB

    print("⚙️ Configuring Flask app...", flush=True)
    # Configure the app
    service.app.config['webmushra_dir'] = os.path.join(os.getcwd(), 'webmushra')
    service.app.config['admin_allowlist'] = ('127.0.0.1',)

    print("💾 Opening database...", flush=True)
    # Open database (don't use 'with' statement - let it stay open)
    db = TinyDB('db/webmushra.json', create_dirs=True)
    service.app.config['db'] = db

    # Determine port for the MUSHRA server. Use START_SERVER_PORT if set,
    # otherwise default to 5000. This lets the launcher run on Render's $PORT
    # while the MUSHRA server listens on an internal port.
    start_port = int(os.environ.get('START_SERVER_PORT', 5000))
    print(f"🌐 Starting Flask server on port {start_port}...", flush=True)
    # Run WITHOUT debug mode and WITHOUT reloader
    service.app.run(debug=False, use_reloader=False, host='0.0.0.0', port=start_port)
except Exception as e:
    print(f"❌ Error starting server: {e}", flush=True)
    import traceback
    traceback.print_exc()
    sys.exit(1)
