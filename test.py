import subprocess
import sys
import os


# Funzione helper per eseguire comandi shell in modo sicuro
def run_command(command):
    """Esegue un comando shell e controlla se ci sono errori."""
    try:
        print(f"▶️ Eseguo: {command}")
        # Usiamo shell=True per interpretare comandi complessi, ma fai attenzione con input non fidati
        subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Errore durante l'esecuzione del comando: {command}", file=sys.stderr)
        print(f"Output: {e.stdout}", file=sys.stderr)
        print(f"Errore: {e.stderr}", file=sys.stderr)
        sys.exit(1)

# ===================================================================
# NGROK: preferisci impostare il token tramite variabile d'ambiente
# Es. in macOS / zsh:
#   export NGROK_AUTH_TOKEN="<your-token>"
# If the env var is not set, the script will skip creating an ngrok tunnel
# and will use local URLs (http://localhost:5000/...).
# ===================================================================
NGROK_AUTH_TOKEN = os.environ.get("NGROK_AUTH_TOKEN")

# Proteggi il codice di setup dal reload di Flask
# Flask's reloader imposta WERKZEUG_RUN_MAIN quando riavvia
if __name__ == "__main__" and not os.environ.get('WERKZEUG_RUN_MAIN'):
    # 1. Installazione dipendenze
    print("⚙️ 1. Installazione dipendenze...")
    # Non installiamo 'gdown' e non scarichiamo asset qui: gli audio sono presi da GitHub
    run_command(f"{sys.executable} -m pip install -q pyngrok")
    run_command(f"{sys.executable} -m pip install -q -e git+https://github.com/nils-werner/pymushra.git#egg=pymushra")
    from pyngrok import ngrok
    # 2. Setup delle cartelle e download
    print("📂 2. Download e setup dei file...")
    os.makedirs("db", exist_ok=True)
    if not os.path.exists("webmushra"):
        run_command("git clone -q https://github.com/audiolabs/webMUSHRA.git webmushra")
    if not os.path.exists("pymushra"):
        run_command("git clone -q https://github.com/nils-werner/pymushra.git pymushra")

    # # 3. Download e preparazione degli assets del test
    # print("📦 3. Preparazione degli assets...")
    # id_file_zip = "1iglOAekwR9_3C1xus-EFvCzhjVwsgGlh"
    # run_command(f"{sys.executable} -m gdown --id \"{id_file_zip}\" -O assets_test.zip")
    # # Estrae nella cartella corrente e sovrascrive
    # run_command("unzip -q -o assets_test.zip") 
    # # Sposta la cartella estratta dentro webmushra (rimuovi prima se esiste)
    # if os.path.exists("webmushra/MUSHRA_COLAB"):
    #     run_command("rm -rf webmushra/MUSHRA_COLAB")
    # run_command("mv MUSHRA_COLAB webmushra/")

    # # 4. Configurazione del test
    # print("📝 4. Configurazione del file YAML...")
    # # I percorsi sono ora relativi, non più /content/
    # source_path_yaml = "webmushra/MUSHRA_COLAB/VBE_Test_drive.yaml"
    # destination_path = "webmushra/configs"

    # # Pulizia e copia
    # run_command(f"rm -f {destination_path}/*.yaml")
    # run_command(f"cp \"{source_path_yaml}\" \"{destination_path}/VBE_Test_drive.yaml\"")
    # print(f"File VBE_Test_drive.yaml copiato in {destination_path}")

    # 5. Avvio Ngrok e STAMPA DEGLI URL (se presente il token)
    print("🔗 5. Avvio del tunnel Ngrok... (se NGROK_AUTH_TOKEN è impostato)")
    if NGROK_AUTH_TOKEN:
        try:
            ngrok.set_auth_token(NGROK_AUTH_TOKEN)
            ngrok_tunnel = ngrok.connect(5000)
            participant_url = f"{ngrok_tunnel.public_url}/?config=VBE_Test_drive.yaml"
            admin_url = f"{ngrok_tunnel.public_url}/admin"
        except Exception as e:
            # If ngrok fails (invalid token, network), fall back to local URLs
            print(f"⚠️ ngrok failed to start: {e}")
            participant_url = "http://localhost:5000/?config=VBE_Test_drive.yaml"
            admin_url = "http://localhost:5000/admin"
    else:
        print("⚠️ NGROK_AUTH_TOKEN non impostato: salto il tunnel ngrok e uso gli URL locali.")
        participant_url = "http://localhost:5000/?config=VBE_Test_drive.yaml"
        admin_url = "http://localhost:5000/admin"

    print("\n" + "="*60)
    print("🚀 IL TUO TEST È PRONTO! 🚀")
    print("\nQuesto è il link da inviare ai partecipanti:")
    print(f"👉   {participant_url}")
    print("\n(Questo è il link per la pagina di amministrazione):")
    print(f"👉   {admin_url}")
    print("="*60 + "\n")

    # 6. Avvio del server MUSHRA (COME ULTIMA COSA)
    print("🖥️ 6. Avvio del server pymushra... (I log appariranno qui sotto)")
    print("Il server è ora attivo agli URL stampati sopra.")
    print("Non chiudere questa finestra del terminale.")

# Questo comando è bloccante e manterrà lo script in esecuzione
# Avviamo il wrapper start_server.py usando lo stesso interprete Python
# in modo da evitare problemi con il reloader di Flask e segnali/non-main-thread
if __name__ == "__main__":
    # Usa lo stesso Python che ha eseguito questo script per avviare il server
    subprocess.run([sys.executable, "start_server.py"], check=True)