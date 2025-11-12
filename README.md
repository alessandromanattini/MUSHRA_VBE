# MUSHRA Test Launcher 🎵

Una web interface completa per gestire test MUSHRA di qualità audio.

## Caratteristiche

✅ **Interface Web Intuitiva** - Avvia test con un click  
✅ **Link Automatici** - Genera automaticamente i link ngrok per i partecipanti  
✅ **Gestione Risultati** - Scarica e visualizza i risultati dei test  
✅ **Auto-Setup** - Installa automaticamente tutte le dipendenze necessarie

## Come Usare

### 1. Avvia il Launcher

```bash
python3 launcher.py
```

### 2. Apri il Browser

Vai su: **http://localhost:8080**

### 3. Workflow

1. **Avvia Test**: Clicca sul pulsante "🚀 Avvia Nuovo Test"
2. **Copia Link**: Copia il link dei partecipanti quando appare
3. **Condividi**: Invia il link ai partecipanti del test
4. **Monitora**: Usa il link admin per monitorare i progressi
5. **Scarica**: Quando hai finito, clicca "📥 Scarica Risultati"

## Gestione Risultati

I risultati vengono salvati in `db/webmushra.json` e contengono:

- **Risposte dei partecipanti** - Tutti i rating e commenti
- **Timestamp** - Quando ogni risposta è stata inviata
- **Metadata** - Informazioni sul browser, sessione, ecc.

### Scaricare i Risultati

**Opzione 1: Web Interface**
- Clicca "📥 Scarica Risultati" nella web interface
- Il file JSON verrà scaricato automaticamente

**Opzione 2: Visualizza nel Browser**
- Clicca "📊 Visualizza Risultati"
- I dati verranno mostrati in formato JSON leggibile

**Opzione 3: Manuale**
```bash
# Copia il file dei risultati
cp db/webmushra.json risultati_$(date +%Y%m%d).json
```

### Analizzare i Risultati

I risultati sono in formato JSON. Puoi analizzarli con Python:

```python
import json
import pandas as pd

# Carica i risultati
with open('db/webmushra.json', 'r') as f:
    data = json.load(f)

# Converti in DataFrame per analisi
df = pd.DataFrame(data['_default'])
print(df.head())

# Esempio: calcola statistiche per ogni condizione
# (la struttura esatta dipende dal tuo YAML)
```

## Struttura File

```
testMUSHRA/
├── launcher.py              # Web interface principale
├── test.py                  # Script originale (opzionale)
├── templates/
│   └── index.html          # Template web interface
├── db/
│   └── webmushra.json      # Database risultati
├── webmushra/              # Clone di webMUSHRA
└── src/
    └── pymushra/           # Clone di pymushra
```

## Configurazione Avanzata

### Cambiare Porta

Modifica in `launcher.py`:
```python
app.run(host='0.0.0.0', port=8080, debug=False)
```

### Cambiare File YAML

Modifica il file di configurazione in `configure_yaml()`:
```python
source_path = "webmushra/MUSHRA_COLAB/TUO_FILE.yaml"
```

E aggiorna il parametro URL:
```python
test_status['participant_url'] = f"{tunnel.public_url}/?config=TUO_FILE.yaml"
```

## Troubleshooting

### Il test non parte
- Verifica che la porta 5000 sia libera: `lsof -i :5000`
- Controlla i log nel terminale

### Link ngrok non funziona
- Verifica che il token ngrok sia corretto in `launcher.py`
- Controlla che non ci siano firewall che bloccano ngrok

### Risultati non si scaricano
- Verifica che `db/webmushra.json` esista
- Assicurati che almeno un partecipante abbia completato il test

## Note Importanti

⚠️ **Token Ngrok**: Il token nel file è quello fornito - cambiatelo se necessario  
⚠️ **Porta 5000**: Non avere altri servizi sulla porta 5000  
⚠️ **Backup Risultati**: Fai backup regolari di `db/webmushra.json`

## Script Originale

Lo script `test.py` è ancora disponibile per uso standalone:

```bash
python3 test.py
```

Ma il launcher web è il metodo raccomandato! 🚀
