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
    
    print("🌐 Starting Flask server on port 5000...", flush=True)
    # Run WITHOUT debug mode and WITHOUT reloader
    service.app.run(debug=False, use_reloader=False, host='0.0.0.0', port=5000)
except Exception as e:
    print(f"❌ Error starting server: {e}", flush=True)
    import traceback
    traceback.print_exc()
    sys.exit(1)
