"""
MUSHRA Test Launcher - Web Interface
Provides a web interface to start/stop MUSHRA tests and download results
"""
import os
import sys
import subprocess
import threading
import json
from flask import Flask, render_template, jsonify, send_file, request
from pyngrok import ngrok
import time
from datetime import datetime

app = Flask(__name__)

# Global state
test_status = {
    'running': False,
    'ngrok_url': None,
    'participant_url': None,
    'admin_url': None,
    'start_time': None,
    'process': None
}

NGROK_AUTH_TOKEN = "35L9KVSgq2mFnuharcKkU8ea50v_44VvwumxAFKtDswqY3bp"


def setup_environment():
    """Setup directories and clone repositories if needed"""
    print("📂 Setting up environment...")
    os.makedirs("db", exist_ok=True)
    
    if not os.path.exists("webmushra"):
        print("Cloning webMUSHRA...")
        subprocess.run("git clone -q https://github.com/audiolabs/webMUSHRA.git webmushra", shell=True)
    
    if not os.path.exists("pymushra"):
        print("Cloning pymushra...")
        subprocess.run("git clone -q https://github.com/nils-werner/pymushra.git pymushra", shell=True)
    
    # Install dependencies
    print("Installing dependencies...")
    subprocess.run(f"{sys.executable} -m pip install -q pyngrok gdown flask", shell=True)
    subprocess.run(f"{sys.executable} -m pip install -q -e git+https://github.com/nils-werner/pymushra.git#egg=pymushra", shell=True)


def download_and_prepare_assets():
    """Download test assets if not already present"""
    if os.path.exists("webmushra/MUSHRA_COLAB"):
        print("Assets already present, skipping download...")
        return
    
    print("📦 Downloading assets...")
    id_file_zip = "1iglOAekwR9_3C1xus-EFvCzhjVwsgGlh"
    subprocess.run(f"{sys.executable} -m gdown --id \"{id_file_zip}\" -O assets_test.zip", shell=True, check=True)
    subprocess.run("unzip -q -o assets_test.zip", shell=True, check=True)
    
    if os.path.exists("webmushra/MUSHRA_COLAB"):
        subprocess.run("rm -rf webmushra/MUSHRA_COLAB", shell=True)
    subprocess.run("mv MUSHRA_COLAB webmushra/", shell=True, check=True)


def configure_yaml():
    """Configure YAML file"""
    print("📝 Configuring YAML...")
    source_path = "webmushra/MUSHRA_COLAB/VBE_Test_drive.yaml"
    dest_path = "webmushra/configs"
    
    subprocess.run(f"rm -f {dest_path}/*.yaml", shell=True)
    subprocess.run(f"cp \"{source_path}\" \"{dest_path}/VBE_Test_drive.yaml\"", shell=True, check=True)


def start_pymushra_server():
    """Start the pymushra server in a separate process"""
    # Run pymushra server as a subprocess using our wrapper script
    proc = subprocess.Popen(
        [sys.executable, 'start_server.py'],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        bufsize=1,
        universal_newlines=True,
        cwd=os.getcwd()
    )
    
    # Start a thread to read and print output
    def log_output():
        for line in proc.stdout:
            print(f"[PyMUSHRA] {line.strip()}", flush=True)
    
    import threading
    log_thread = threading.Thread(target=log_output, daemon=True)
    log_thread.start()
    
    return proc


def start_test():
    """Start the MUSHRA test"""
    global test_status
    
    try:
        # Setup
        setup_environment()
        download_and_prepare_assets()
        configure_yaml()
        
        # Start ngrok tunnel
        print("🔗 Starting ngrok tunnel...")
        ngrok.set_auth_token(NGROK_AUTH_TOKEN)
        tunnel = ngrok.connect(5000)
        
        test_status['ngrok_url'] = tunnel.public_url
        test_status['participant_url'] = f"{tunnel.public_url}/?config=VBE_Test_drive.yaml"
        test_status['admin_url'] = f"{tunnel.public_url}/admin"
        test_status['start_time'] = datetime.now().isoformat()
        
        print(f"✅ Test ready at: {test_status['participant_url']}")
        
        # Start pymushra server in a separate process
        proc = start_pymushra_server()
        test_status['process'] = proc
        
        # Wait a moment for server to start
        time.sleep(3)
        
        test_status['running'] = True
        
        return True
    except Exception as e:
        print(f"❌ Error starting test: {e}")
        import traceback
        traceback.print_exc()
        test_status['running'] = False
        return False


@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')


@app.route('/api/status')
def get_status():
    """Get current test status"""
    # Return status without the process object (not JSON serializable)
    status_copy = {k: v for k, v in test_status.items() if k != 'process'}
    return jsonify(status_copy)


@app.route('/api/start', methods=['POST'])
def api_start_test():
    """Start a new test"""
    if test_status['running']:
        return jsonify({'error': 'Test already running'}), 400
    
    # Start test in background thread
    thread = threading.Thread(target=start_test, daemon=True)
    thread.start()
    
    # Wait a bit for initialization
    time.sleep(2)
    
    return jsonify({'message': 'Test starting...', 'status': test_status})


@app.route('/api/stop', methods=['POST'])
def api_stop_test():
    """Stop the current test"""
    global test_status
    
    if not test_status['running']:
        return jsonify({'error': 'No test running'}), 400
    
    # Kill the pymushra process
    if test_status.get('process'):
        try:
            test_status['process'].terminate()
            test_status['process'].wait(timeout=5)
        except:
            test_status['process'].kill()
    
    # Stop ngrok tunnels
    ngrok.kill()
    
    test_status['running'] = False
    test_status['ngrok_url'] = None
    test_status['participant_url'] = None
    test_status['admin_url'] = None
    test_status['process'] = None
    
    return jsonify({'message': 'Test stopped'})


@app.route('/api/results')
def get_results():
    """Get test results from database"""
    db_path = "db/webmushra.json"
    
    if not os.path.exists(db_path):
        return jsonify({'error': 'No results found'}), 404
    
    try:
        with open(db_path, 'r') as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/results/download')
def download_results():
    """Download results as JSON file"""
    db_path = "db/webmushra.json"
    
    if not os.path.exists(db_path):
        return jsonify({'error': 'No results found'}), 404
    
    return send_file(
        db_path,
        mimetype='application/json',
        as_attachment=True,
        download_name=f'mushra_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    )


if __name__ == '__main__':
    print("="*60)
    print("🎵 MUSHRA Test Launcher")
    print("="*60)
    print("\n📱 Open your browser at: http://localhost:8080")
    print("\n💡 Use the web interface to:")
    print("   - Start/stop MUSHRA tests")
    print("   - Get participant links")
    print("   - Download results")
    print("\n" + "="*60 + "\n")
    
    app.run(host='0.0.0.0', port=8080, debug=False)
