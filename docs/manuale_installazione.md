# Manuale Operativo di Installazione e Avvio della Piattaforma Multi-Agente
## Guida Completa per Google Antigravity e Claude Code
### Progetto: Survey AI Human-in-the-Loop — Noto Sondaggi SRL & IUSS Pavia

> **Destinatari**: Ricercatori universitari, metodologi di indagine, sviluppatori e collaboratori tecnici di **Noto Sondaggi SRL** e **IUSS Pavia**.  
> **Oggetto**: Installazione da zero, configurazione dell'ambiente di lavoro, avvio su Google Antigravity e Claude Code, esecuzione dei comandi slash, formulazione dei prompt per l'orchestratore e protocollo Human-in-the-Loop.  
> **Versione Manuale**: 1.0 (Allineata all'Architettura Speculare v3.0)  
> **Architettura di Riferimento**: Doppia Specularità Integrale (`.agents/` per Google Antigravity, `.claude/` per Claude Code).

---

## Indice dei Contenuti
1. [Inquadramento e Principi Architetturali](#1-inquadramento-e-principi-architetturali)
2. [Prerequisiti di Sistema e Gestione Dipendenze](#2-prerequisiti-di-sistema-e-gestione-dipendenze)
3. [Installazione e Configurazione Passo-Passo da Zero](#3-installazione-e-configurazione-passo-passo-da-zero)
4. [Guida al Setup su Google Antigravity](#4-guida-al-setup-su-google-antigravity)
5. [Guida al Setup su Claude Code](#5-guida-al-setup-su-claude-code)
6. [Guida Operativa ai Prompt e all'Human-in-the-Loop](#6-guida-operativa-ai-prompt-e-allhuman-in-the-loop)
7. [Batteria di Smoke Test Post-Installazione](#7-batteria-di-smoke-test-post-installazione)
8. [Guida alla Risoluzione dei Problemi (Troubleshooting)](#8-guida-alla-risoluzione-dei-problemi-troubleshooting)
9. [Mappa Sinottica dei File e Riferimenti Rapidi](#9-mappa-sinottica-dei-file-e-riferimenti-rapidi)

---

## 1. Inquadramento e Principi Architetturali

La piattaforma **Noto Sondaggi Survey AI** è concepita come un ambiente di progettazione metodologica assistita, audit di conformità e preparazione alla rilevazione di indagini campionarie demoscopiche e sociali.

### 1.1 Principi Cardine di Governance e Metodologia
- **Human-in-the-Loop Obbligatorio**: Gli agenti artificiali operano esclusivamente come estensione tecnica del ricercatore umano; non prendono decisioni definitive, non avviano raccolte dati autonome e non generano risposte sintetiche per sostituire intervistati reali.
- **Doppia Architettura Speculare**: Il repository mantiene una struttura identica al 100% per operare senza alcuna modifica funzionale sia su **Google Antigravity** (sfruttando le specifiche `.agents/` e `AGENTS.md`) sia su **Claude Code** (sfruttando `.claude/` e `CLAUDE.md`).
- **Separazione Netta tra Orchestrazione ed Esecuzione**: Il supervisore (`ai-coordinator`) coordina il flusso, gestisce lo stato in `runs/<caso>/status.md` e interroga l'utente a ogni passaggio critico (STOP gate), delegando l'elaborazione agli agenti specialisti (`questionnaire-agent`, `methodology-agent`, `compliance-agent`, `reporting-agent`).
- **Standardizzazione delle Opzioni di Risposta**: Ogni domanda formulata o auditata adotta la codifica istituzionale per la mancata opinione:
  - `97 = Non applicabile` (fuori target / filtro)
  - `98 = Non so / Senza opinione` (autentica assenza di informazione)
  - `99 = Preferisco non rispondere / Rifiuta` (rifiuto esplicito a tutela della privacy)

---

## 2. Prerequisiti di Sistema e Gestione Dipendenze

### 2.1 Requisiti Software Fondamentali
Prima di procedere all'installazione, assicurarsi che la macchina host soddisfi i seguenti requisiti:

| Componente | Requisito Minimo | Note Operative |
| :--- | :--- | :--- |
| **Sistema Operativo** | Windows 10/11 (64-bit), macOS 12+, Ubuntu 20.04+ | Piena compatibilità multi-piattaforma. |
| **Python** | **Python >= 3.10** (raccomandato 3.11, 3.12 o 3.14, 64-bit) | Verificare aggiunta al `PATH` o disponibilità del launcher `py`. |
| **Git** | **Git >= 2.30** | Necessario per il clonaggio del repository e il controllo di versione. |
| **Node.js & npm** | **Node.js >= 18 LTS** (`node -v`, `npm -v`) | Prerequisito obbligatorio se si desidera eseguire Claude Code da CLI. |
| **Google Antigravity** | Installazione ufficiale / Estensione IDE | Piattaforma per workflow multi-agente basati su protocollo `.agents/`. |
| **Claude Code** | CLI ufficiale Anthropic (`npm install -g @anthropic-ai/claude-code`) | Interfaccia CLI o integrazione terminale per comandi `/` e agenti `.claude/`. |

### 2.2 Gestione dei Percorsi con Spazi su Windows (es. OneDrive)
In ambienti accademici e aziendali, i repository si trovano frequentemente sincronizzati all'interno di cartelle cloud aziendali contenenti spazi e caratteri accentati, quali ad esempio:
```text
C:\Users\<NomeUtente>\OneDrive - Università di Pavia\Developing\GitHub\NotoSondaggi_Agents4SurveyPlatform
```
Per evitare errori nei comandi CLI e negli script di automazione:
- **Racchiudere sempre i percorsi tra virgolette doppie** in PowerShell, Prompt dei Comandi (CMD) e Bash:
  ```powershell
  cd "C:\Users\<NomeUtente>\OneDrive - IUSS Pavia\Developing\GitHub\NotoSondaggi_Agents4SurveyPlatform"
  ```
- Negli script Python del repository, tutti i percorsi sono gestiti tramite la libreria nativa `pathlib.Path`, garantendo la massima resilienza anche in presenza di spazi, trattini e caratteri non-ASCII.

### 2.3 Architettura "Zero Dipendenze Obbligatorie" e Pacchetti Opzionali
Il nucleo fondamentale della piattaforma (`core`) è stato intenzionalmente progettato a **zero dipendenze esterne obbligatorie**. L'intera pipeline (validazione, export LimeSurvey TSV, generazione report AGCOM, linter metodologico, runner dei test) funziona nativamente utilizzando esclusivamente la **Python Standard Library** (`pathlib`, `re`, `json`, `sys`, `unittest`, `argparse`, `dataclasses`, `typing`, `csv`, `math`).

Tuttavia, per abilitare funzionalità documentali avanzate su formati proprietari di Microsoft Office e Adobe PDF, sono previsti due pacchetti opzionali:

1. **`python-docx`**:
   - *Funzione*: Esportazione binaria della Guida Intervistatore formattata in Word (.docx) tramite `scripts/generate_interviewer_guide.py` e lettura di vecchi questionari in formato `.docx` tramite `scripts/extract_survey_knowledge.py`.
   - *Comportamento difensivo*: Se non installato, il sistema non crasha ma esegue un fallback trasparente su file Markdown (.md) e HTML (.html) ad alta leggibilità.
2. **`pypdf`** (o `PyPDF2`):
   - *Funzione*: Lettura ed estrazione testuale da report storici e questionari in formato PDF (.pdf) tramite `scripts/extract_survey_knowledge.py`.
   - *Comportamento difensivo*: Se assente, l'estrattore notifica all'utente con un messaggio chiaro che è necessario installare la libreria per trattare file binari `.pdf`.

#### Installazione delle Dipendenze Opzionali
Per installare i pacchetti documentali opzionali, eseguire:
```bash
pip install python-docx pypdf
```

---

## 3. Installazione e Configurazione Passo-Passo da Zero

Seguire ordinatamente la seguente procedura per allestire l'ambiente locale partendo da un terminale pulito.

### Passo 1: Clonazione del Repository Git
Aprire la propria shell preferita (PowerShell o Git Bash) e posizionarsi nella cartella di sviluppo desiderata:

```bash
# Esempio su Windows / OneDrive
cd "C:\Users\<NomeUtente>\OneDrive - IUSS Pavia\Developing\GitHub"

# Clonare il repository ufficiale via HTTPS
git clone https://github.com/adelaide-bernardelli/NotoSondaggi_Agents4SurveyPlatform.git

# (Nota: se si lavora su un proprio fork personale, sostituire l'URL con quello del proprio account)

# Accedere alla cartella clonata
cd NotoSondaggi_Agents4SurveyPlatform
```

### Passo 2: Creazione del Virtual Environment Python
È fortemente raccomandato isolare le dipendenze creando un ambiente virtuale dedicato denominato `.venv` (già configurato nel file `.gitignore` per evitare tracciamento accidentale):

- **Su Windows (PowerShell o CMD standard)**:
  ```powershell
  python -m venv .venv
  ```
  *Nota Windows*: Se il comando `python` apre il Microsoft Store o restituisce errore di alias, utilizzare il launcher Windows:
  ```powershell
  py -3 -m venv .venv
  ```
- **Su macOS / Linux (Bash / Zsh)**:
  ```bash
  python3 -m venv .venv
  ```

### Passo 3: Attivazione del Virtual Environment
Attivare l'ambiente virtuale in base alla shell in uso:

- **Windows PowerShell**:
  ```powershell
  # Se compare un errore di ExecutionPolicy, vedi Sezione 8 (Troubleshooting)
  .\.venv\Scripts\Activate.ps1
  ```
- **Windows Prompt dei Comandi (CMD)**:
  ```cmd
  .\.venv\Scripts\activate.bat
  ```
- **Git Bash / macOS / Linux**:
  ```bash
  source .venv/bin/activate
  ```

Una volta attivato, il prompt visualizzerà il prefisso `(.venv)`.

### Passo 4: Verifica dell'Ambiente e Aggiornamento pip
Verificare che l'interprete Python attivo punti correttamente all'interno del virtual environment:

```powershell
# Verifica percorso interprete su Windows PowerShell
Get-Command python | Select-Object -ExpandProperty Source

# Aggiornamento gestore pacchetti pip
python -m pip install --upgrade pip
```

### Passo 5: (Opzionale) Installazione Librerie Documentali
Se si prevede di elaborare documenti `.docx` e questionari storici in `.pdf`, installare le estensioni:
```powershell
pip install python-docx pypdf
```

---

## 4. Guida al Setup su Google Antigravity

Google Antigravity sfrutta la cartella standard `.agents/` per il catalogo degli agenti, delle skill e dei workflow, oltre al file di istruzioni di contesto `AGENTS.md` posto nella radice del repository.

### 4.1 Caricamento del Workspace
1. Avviare **Google Antigravity**.
2. Selezionare **File -> Open Folder...** (o **Open Workspace**) e scegliere la radice del repository:
   ```text
   NotoSondaggi_Agents4SurveyPlatform
   ```
3. L'ambiente rileverà automaticamente:
   - `AGENTS.md`: contenente le regole globali di governance metodologica, deontologia e privacy;
   - La cartella `.agents/agents/`: definizioni YAML e ruoli operativi;
   - La cartella `.agents/skills/`: le 8 procedure operative specializzate;
   - La cartella `.agents/workflows/`: i flussi multi-fase preconfigurati.

### 4.2 Mappa dei Ruoli Agenti in Antigravity
I file descrittori in `.agents/agents/` utilizzano metadati specifici nel frontmatter YAML per garantire la corretta gerarchia operativa:

- **`ai-coordinator.md` (Main Agent)**:
  ```yaml
  ---
  name: ai-coordinator
  description: Supervisore e orchestratore del workflow survey...
  model: inherit
  mainAgent: true
  subagent: false
  commandExecutionPolicy: sandbox
  ---
  ```
  *Ruolo*: È l'unico agente con cui il ricercatore interagisce direttamente. Gestisce lo stato e delega le fasi.
- **Agenti Specialisti (Subagents)**:
  - `questionnaire-agent.md` (`mainAgent: false`, `subagent: true`)
  - `methodology-agent.md` (`mainAgent: false`, `subagent: true`)
  - `compliance-agent.md` (`mainAgent: false`, `subagent: true`)
  - `reporting-agent.md` (`mainAgent: false`, `subagent: true`)
  - `analysis-agent.md` e `dashboard-agent.md` (Modelli strutturati per il Modulo B)

### 4.3 Avvio della Sessione su Antigravity
1. Aprire il pannello di chat con l'agente principale (`ai-coordinator`).
2. Digitare un messaggio di avvio indicando il workflow o il caso di lavoro, ad esempio:
   > "Avvia il workflow nuova-indagine per il caso 'indagine-trasporti' usando il brief in source/brief_cliente.txt. Esegui la prima fase (brief) e fermati per la mia approvazione."
3. L'orchestratore inizializzerà `runs/indagine-trasporti/status.md`, invocherà il subagent `questionnaire-agent` tramite la skill `noto-brief-structuring` e presenterà il risultato nel thread di chat, arrestandosi in attesa della vostra revisione.

---

## 5. Guida al Setup su Claude Code

Claude Code opera principalmente da interfaccia a riga di comando (CLI) o estensione terminale, leggendo automaticamente la configurazione presente in `.claude/` e il file di regole `CLAUDE.md`.

### 5.1 Installazione e Avvio della CLI di Claude Code
Se Claude Code CLI non è ancora installato nell'ambiente globale (richiede Node.js >= 18 LTS):
```bash
npm install -g @anthropic-ai/claude-code
```

Posizionarsi nella radice del progetto nel proprio terminale attivo con l'ambiente virtuale ed eseguire:

```bash
claude
```

#### Primo Accesso e Autenticazione:
- **Autenticazione Web interattiva**: Al primo avvio, Claude Code richiederà l'autenticazione aprendo automaticamente il browser per collegare il proprio account Anthropic (con piano Claude Pro, Team o Enterprise, oppure account Anthropic Console).
- **Autenticazione via API Key (Server/Headless)**: Se si opera in un terminale privo di interfaccia grafica o si preferisce la fatturazione diretta via API token:
  - In PowerShell:
    ```powershell
    $env:ANTHROPIC_API_KEY = "sk-ant-api03-..."
    ```
  - In Prompt dei Comandi (CMD):
    ```cmd
    set ANTHROPIC_API_KEY=sk-ant-api03-...
    ```
  - In Bash / Zsh:
    ```bash
    export ANTHROPIC_API_KEY="sk-ant-api03-..."
    ```

Al caricamento, Claude Code scansiona la root del workspace e mappa automaticamente:
- `CLAUDE.md`: regole di condotta, tassonomia della non risposta e perimetro di compliance;
- `.claude/commands/`: i tre comandi slash eseguibili con prefisso `/`;
- `.claude/agents/`: i 7 subagent speculari a disposizione dell'orchestratore;
- `.claude/skills/`: le 8 skill richiamabili.

### 5.2 Mappa e Sintassi dei 3 Comandi Slash Nativi

| Comando Slash | File di Definizione | Sequenza Operativa Eseguita | Quando Utilizzarlo |
| :--- | :--- | :--- | :--- |
| **`/nuova-indagine`** | `.claude/commands/nuova-indagine.md` | `brief -> questionnaire -> methodology -> compliance -> final` | Progettazione integrale da zero partendo da un brief grezzo o appunti cliente. |
| **`/revisione-questionario`** | `.claude/commands/revisione-questionario.md` | `methodology -> compliance -> final` | Audit e miglioramento di un questionario preesistente o storico (salta brief e prima stesura). |
| **`/audit-singolo`** | `.claude/commands/audit-singolo.md` | `methodology` *oppure* `compliance` | Controllo mirato e circoscritto su una bozza o documento esterno senza completare l'intera pipeline. |

### 5.3 Esempi di Invocazione dei Comandi Slash

#### Caso A: Avvio di una Nuova Indagine
```text
/nuova-indagine caso-mobilita examples/brief_demo.md
```
*Cosa fa*: Claude Code crea la cartella `runs/caso-mobilita/source/`, copia il file sorgente, inizializza `runs/caso-mobilita/status.md` a partire da `templates/status_template.md`, elabora la fase 1 (`brief.md`) tramite `questionnaire-agent` e si arresta chiedendo l'approvazione in chat.

#### Caso B: Revisione di un Questionario Esistente
```text
/revisione-questionario revisione-customer examples/questionario_demo.md
```
*Cosa fa*: Inizializza il caso `runs/revisione-customer/`, salta le prime due fasi e delega direttamente a `methodology-agent` l'audit metodologico item-per-item in `runs/revisione-customer/methodology.md`.

#### Caso C: Audit Singolo (Solo Privacy o Solo Metodologia)
```text
/audit-singolo audit-privacy compliance examples/questionario_demo.md
```
*Cosa fa*: Esegue esclusivamente la verifica preliminare di conformità GDPR (Art. 9) e AI Act su quel file, producendo `compliance.md` senza alterare altre cartelle.

---

## 6. Guida Operativa ai Prompt e all'Human-in-the-Loop

La piattaforma adotta un'interazione strutturata e disciplinata: il ricercatore impartisce le direttive metodologiche, l'orchestratore le esegue tramite i subagent e richiede conferma esplicita prima di passare alla fase successiva.

### 6.1 Struttura Ottimale di un Prompt per l'Orchestratore
Quando si comunica con `ai-coordinator`, formulare il prompt includendo sempre tre elementi essenziali:
1. **Nome identificativo del caso** (es. `caso-sanita-2026`);
2. **File o percorso del documento sorgente** (es. `runs/caso-sanita-2026/source/brief.txt`);
3. **Istruzione esplicita di STOP al termine della fase**:
   > *"Inizializza il caso 'caso-sanita-2026' con il documento in source. Procedi esclusivamente con la fase 1 (brief) e fermati per la mia approvazione."*

### 6.2 Il Meccanismo dello STOP Gate
Al termine di ciascuna fase, l'orchestratore:
1. Esegue un controllo di qualità interno (verifica che il file prodotto rispetti le colonne, le sezioni e i codici standard `97/98/99` del rispettivo template in `templates/`);
2. Aggiorna la tabella di avanzamento in `runs/<caso>/status.md`, contrassegnando la fase come `IN ATTESA DI APPROVAZIONE`;
3. Mostra in chat una sintesi dei risultati salienti, delle lacune informative identificate o delle criticità rilevate;
4. **Si ferma tassativamente (STOP)** senza avviare la fase successiva.

### 6.3 Le 3 Opzioni di Risposta del Ricercatore Umano

A ogni STOP gate, il ricercatore risponde direttamente nel thread di chat scegliendo una tra le seguenti tre modalità:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                   DECISIONE DEL RICERCATORE AL GATE                   │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │
      ┌────────────────────────────┼────────────────────────────┐
      ▼                            ▼                            ▼
 [OPZIONE 1]                  [OPZIONE 2]                  [OPZIONE 3]
  APPROVATO             APPROVATO CON MODIFICHE             RIFIUTATO
(Avanzamento a          (Selezione puntuale A/B/C          (Rielaborazione
  fase successiva)      e prescrizioni vincolanti)         della stessa fase)
```

#### 1. Approvazione Piena (`APPROVATO`)
Usare questa risposta quando l'artefatto è completo e soddisfacente senza modifiche.
- *Esempio di Prompt*:
  > "Approvo il brief senza modifiche. Revisore: Dott.ssa Bernardelli. Data: 2026-11-06. Procedi con la fase questionnaire."
- *Azione dell'Agente*: Registra la validazione in `runs/<caso>/status.md` e sblocca la fase successiva delegando il `questionnaire-agent`.

#### 2. Approvazione con Modifiche o Selezione Alternative (`APPROVATO CON MODIFICHE`)
Tipica della fase metodologica (`methodology.md`), dove l'agente propone tre alternative per ogni domanda critica:
- *Opzione A*: Conservare la formulazione originale (a tutela delle serie storiche);
- *Opzione B*: Modifica minima (correzione ambiguità mantenendo il costrutto);
- *Opzione C*: Revisione sostanziale (ristrutturazione profonda del quesito).
- *Esempio di Prompt*:
  > "Approvo l'audit metodologico con le seguenti decisioni: per Q1 e Q3 adotta l'Opzione B (modifica minima); per Q2 mantieni l'Opzione A (conservare originale per serie storica); per Q4 accetta l'Opzione C. Per la compliance, applica il codice 99 obbligatorio. Procedi con il consolidamento finale."
- *Azione dell'Agente*: Registra puntualmente ogni singola selezione nella sezione decisioni di `runs/<caso>/status.md`. In fase `final`, il `questionnaire-agent` recepirà **esclusivamente** le opzioni espressamente approvate.

#### 3. Rifiuto o Riassegnazione Correttiva (`RIFIUTATO / DA REVISIONARE`)
Usare quando l'elaborato presenta lacune sostanziali o presupposti errati.
- *Esempio di Prompt*:
  > "Il questionario non può essere approvato: nella sezione 2 mancano le opzioni di uscita 'Non so' e la scala Likert è asimmetrica. Rielabora la fase questionnaire integrando le domande sui servizi digitali."
- *Azione dell'Agente*: Registra le note di rifiuto in `runs/<caso>/status.md`, mantiene la fase corrente e riassegna il compito allo specialista per la produzione di una nuova bozza emendata.

### 6.4 Il File di Stato (`runs/<caso>/status.md`)
Il file `status.md` rappresenta il **giornale di bordo immutabile** dell'indagine. Contiene:
- L'intestazione del caso, committente, target e periodo;
- La tabella sinottica delle 5 fasi del Modulo A (`NON INIZIATO`, `IN CORSO`, `IN ATTESA DI APPROVAZIONE`, `APPROVATO`);
- Il registro cronologico delle decisioni umane con data, nome del revisore e testo del riscontro in chat;
- La checklist dei blocchi pre-campo (es. approvazione formale DPO per dati sensibili o autorizzazione del committente per modifiche alle serie storiche).

---

## 7. Batteria di Smoke Test Post-Installazione

Per accertare la perfetta integrità del codice, dell'ambiente virtuale e della sincronizzazione dei file speculari, è disponibile una batteria di test automatici eseguibile con comandi standard da riga di comando.

### Smoke Test 1: Verifica della Sincronizzazione Speculare
Controlla la perfetta corrispondenza tra Google Antigravity e Claude Code (`AGENTS.md` vs `CLAUDE.md`, cartelle `.agents/` vs `.claude/`, tutti gli 8 template):

```bash
python scripts/check_mirror_sync.py
```
**Output Atteso**:
```text
=== Verifica Sincronizzazione Architetturale Noto Sondaggi ===
[OK] Regole Globali (AGENTS.md / CLAUDE.md): AGENTS.md e CLAUDE.md perfettamente sincronizzati
[OK] Agenti (.agents/agents vs .claude/agents): Tutti i 7 agenti sono allineati nel corpo operativo
[OK] Skill (.agents/skills vs .claude/skills): Tutte le 8 skill sono perfettamente identiche
[OK] Workflow / Comandi (.agents/workflows vs .claude/commands): Tutti i 3 flussi/comandi corrispondono per nome e contenuto
[OK] Template Obbligatori (templates/): Tutti gli 8 template obbligatori sono presenti

RISULTATO: Architettura speculare integra al 100%.
```

### Smoke Test 2: Suite dei Test Unitari di Regressione
Esegue l'intera suite di test automatizzati (oltre 130 verifiche unitarie che coprono validatori, export LimeSurvey, parsing storico e reportistica AGCOM):

```bash
python -m unittest discover tests/
```
**Output Atteso**:
```text
Ran 130 tests in ~2.5s
OK
```

> [!NOTE] **Interpretazione dei log `[ERRORE]` durante i test di regressione**  
> Durante l'esecuzione della suite di unittest, la presenza a video di log quali ad esempio `[ERRORE] File di input non trovato: .../non_existent.md` o `[ERRORE] Il file di input ... è vuoto` è del tutto **normale e attesa**. Si tratta di asserzioni di *negative testing* studiate appositamente per verificare che il software intercetti e gestisca con grazia input non validi, file assenti o documenti vuoti senza crash anomali.  
> L'unico indicatore determinante per il successo è la dicitura finale: **`Ran 130 tests ... OK`**.

### Smoke Test 3: Linter di Conformità Metodologica su Caso Demo
Esegue il validatore semantico e formale sul caso completo di riferimento `examples/demo_run_biblioteca`:

```bash
python scripts/validate_runs.py examples/demo_run_biblioteca
```
**Output Atteso**:
```text
--- Validazione Caso: demo_run_biblioteca ---
  [PASS] Tutti i file presenti risultano conformi agli standard metodologici.

Tutti i casi esaminati sono conformi.
```

### Smoke Test 4 (Opzionale): Test degli Esportatori
È possibile verificare sul campo gli esportatori verso LimeSurvey e Guida Intervistatore sul caso demo, indirizzando l'output verso la cartella `runs/` (già inclusa in `.gitignore` per mantenere pulito il repository):

```bash
# Test esportatore LimeSurvey TSV (14 colonne standard)
python scripts/export_limesurvey.py examples/demo_run_biblioteca/final.md -o runs/test_limesurvey_export.txt

# Test generatore Guida Intervistatore (Markdown / Word / HTML)
python scripts/generate_interviewer_guide.py examples/demo_run_biblioteca/final.md -f both -o runs/test_guida_intervistatore
```

---

## 8. Guida alla Risoluzione dei Problemi (Troubleshooting)

### 8.1 Errore di Esecuzione Script in PowerShell (`PSSecurityException`)
*Problema*: Tentando di eseguire `.\.venv\Scripts\Activate.ps1`, compare l'errore:
`File non può essere caricato perché l'esecuzione di script è disabilitata nel sistema.`  
*Soluzione*: Windows imposta per default una ExecutionPolicy restrittiva (`Restricted`). È possibile sbloccare l'esecuzione per la sessione corrente di PowerShell senza alterare le impostazioni globali del computer:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```
*Alternativa per macchine aziendali/universitarie con Group Policy bloccanti*:
Se la propria organizzazione impedisce l'uso del parametro `-Scope Process`, utilizzare una shell non vincolata da PowerShell ExecutionPolicy:
- **Prompt dei Comandi (CMD)**: `.\.venv\Scripts\activate.bat`
- **Git Bash**: `source .venv/bin/activate`

### 8.2 Percorsi Contenenti Spazi o Caratteri Non-ASCII
*Problema*: Errore di comando non trovato o sintassi non valida quando si fa riferimento a cartelle come `OneDrive - IUSS Pavia`.  
*Soluzione*:
1. Racchiudere sempre qualsiasi percorso contenente spazi all'interno di doppie virgolette `"..."`:
   ```powershell
   python scripts/validate_runs.py "C:\Users\Nome\OneDrive - IUSS Pavia\Developing\GitHub\NotoSondaggi_Agents4SurveyPlatform\examples\demo_run_biblioteca"
   ```
2. In PowerShell, se il percorso inizia con un carattere speciale, spazio o variabile, anteporre l'operatore di chiamata `&`:
   ```powershell
   & ".\.venv\Scripts\python.exe" scripts/check_mirror_sync.py
   ```

### 8.3 Errori di Encoding Caratteri UTF-8 su Shell Windows
*Problema*: Errori `UnicodeDecodeError` o visualizzazione scorretta di caratteri accentati (es. `à, è, é, ì, ò, ù`) durante l'output su terminali Windows predefiniti su codepage legacy (es. CP850 o CP1252).  
*Soluzione*:
1. Impostare la codepage del terminale su UTF-8 attivo:
   ```cmd
   chcp 65001
   ```
2. Impostare la variabile d'ambiente standard Python per forzare I/O UTF-8:
   - In PowerShell:
     ```powershell
     $env:PYTHONUTF8 = "1"
     ```
   - In Prompt dei Comandi (CMD):
     ```cmd
     set PYTHONUTF8=1
     ```
   - In Bash:
     ```bash
     export PYTHONUTF8=1
     ```

### 8.4 Windows apre il Microsoft Store digitando `python` (App Execution Alias)
*Problema*: Digitando `python` o `python3`, Windows 10/11 apre la finestra del Microsoft Store o restituisce `Python was not found; run without arguments to install from the Microsoft Store...`.  
*Causa*: Windows include collegamenti fittizi preattivati nelle impostazioni del sistema operativo.  
*Soluzione*:
1. **Opzione A (Risoluzione Definitiva)**: Aprire il menu Start -> digitare **Impostazioni** -> andare in **App** -> **Funzionalità avanzate dell'app** -> **Alias di esecuzione app** (*App execution aliases*). Disattivare i selettori per:
   - `Programma di installazione app: python.exe`
   - `Programma di installazione app: python3.exe`
2. **Opzione B (Uso del Launcher Ufficiale)**: Utilizzare il comando ufficiale Python Launcher per Windows, che ignora gli alias di sistema:
   ```powershell
   py -3 -m venv .venv
   ```

### 8.5 Assenza di `python-docx` e Gestione del Fallback
*Problema*: Durante la generazione della guida intervistatore compare l'avviso:
`[AVVISO] La libreria opzionale 'python-docx' non è installata nell'ambiente Python. Impossibile generare il file binario Word (.docx).`  
*Spiegazione*: Non si tratta di un bug o di un errore fatale. La piattaforma è concepita per continuare a funzionare regolarmente anche in assenza di pacchetti esterni: in questo caso produce automaticamente una guida in formato **Markdown (`.md`)** e **HTML (`.html`)** ad altissima leggibilità.  
*Risoluzione per ottenere il file `.docx`*:
```powershell
pip install python-docx
```

### 8.6 Disallineamento Rilevato da `check_mirror_sync.py`
*Problema*: Lo script `check_mirror_sync.py` segnala una discrepanza tra `.agents/` e `.claude/` oppure tra `AGENTS.md` e `CLAUDE.md`.  
*Causa*: Una modifica è stata apportata a una cartella senza aggiornare il rispettivo file nell'altra architettura.  
*Risoluzione*:
- Se è stato modificato `AGENTS.md`, copiare il medesimo testo su `CLAUDE.md` (o viceversa);
- Se è stato modificato un agente, assicurarsi che il corpo operativo sia identico tra `.agents/agents/<nome>.md` e `.claude/agents/<nome>.md`;
- Rieseguire `python scripts/check_mirror_sync.py` fino al conseguimento di: `Architettura speculare integra al 100%`.

---

## 9. Mappa Sinottica dei File e Riferimenti Rapidi

### 9.1 Matrice Agenti - Skill - Template - Artefatti

| Fase | Agente Delegato | Skill Invocata | Template Obbligatorio | File Prodotto in `runs/<caso>/` |
| :---: | :--- | :--- | :--- | :--- |
| **0** | `ai-coordinator` | `noto-survey-pipeline` | `templates/status_template.md` | `runs/<caso>/status.md` |
| **1** | `questionnaire-agent` | `noto-brief-structuring` | `templates/brief_template.md` | `runs/<caso>/brief.md` |
| **2** | `questionnaire-agent` | `noto-questionnaire-drafting` | `templates/questionnaire_template.md` | `runs/<caso>/questionnaire.md` |
| **3** | `methodology-agent` | `noto-methodology-audit` | `templates/methodology_template.md` | `runs/<caso>/methodology.md` |
| **4** | `compliance-agent` | `noto-compliance-check` | `templates/compliance_template.md` | `runs/<caso>/compliance.md` |
| **5** | `questionnaire-agent` | `noto-questionnaire-consolidation` | `templates/final_template.md` | `runs/<caso>/final.md`<br>`runs/<caso>/limesurvey_survey.txt` |
| **Hist**| `questionnaire-agent` | `noto-survey-extractor` | `templates/extracted_survey_template.md`| `runs/<caso>/extracted_survey.md` |
| **AGCOM**| `reporting-agent` | `noto-agcom-reporting` | `templates/agcom_template.md` | `runs/<caso>/scheda_agcom.md` |

### 9.2 Tooling CLI Ausiliario

| Script | Argomenti Principali | Descrizione |
| :--- | :--- | :--- |
| `scripts/check_mirror_sync.py` | *(nessuno)* | Verifica la simmetria tra Antigravity e Claude Code |
| `scripts/validate_runs.py` | `<cartella_caso>` | Valida la conformità metodologica e formale di tutti gli artefatti del caso |
| `scripts/export_limesurvey.py` | `<final.md> -o <output.txt>` | Esporta il questionario finale in formato TSV LimeSurvey a 14 colonne |
| `scripts/generate_interviewer_guide.py`| `<final.md> -f [md\|docx\|both\|html]` | Compila la guida per intervistatori con note tipografiche di regia |
| `scripts/generate_agcom_report.py` | `<cartella_caso> -o <scheda.md>` | Redige e calcola i parametri statistici per la Scheda Informativa AGCOM |
| `scripts/extract_survey_knowledge.py` | `<file_sorgente> -o <output.md>` | Estrae formulari e batterie storiche da documenti `.md`, `.txt`, `.docx`, `.pdf` |

### 9.3 Documentazione Ufficiale e Roadmap di Progetto

I 5 documenti ufficiali a presidio dell'architettura e dello sviluppo della piattaforma sono organizzati nella cartella `docs/`:

| Documento | File | Oggetto e Finalità |
| :--- | :--- | :--- |
| **Manuale di Installazione e Avvio** | [`docs/manuale_installazione.md`](manuale_installazione.md) | Setup ambiente, dipendenze, avvio su Google Antigravity e Claude Code, troubleshooting |
| **Guida Completa alle Funzionalità** | [`docs/guida_funzionalita.md`](guida_funzionalita.md) | Manuale enciclopedico di agenti, skill, workflow, CLI e knowledge base |
| **Piano di Test Umano (H1–H10)** | [`docs/piano_test_umani.md`](piano_test_umani.md) | 10 protocolli operativi di collaudo metodologico, deontologico e privacy per ricercatori |
| **Stato del Progetto (35 Task)** | [`docs/statoprogetto.md`](statoprogetto.md) | Rendicontazione accademica, censimento analitico dei 35 task e stato avanzamento (v3.1) |
| **Piano Operativo a Milestones** | [`docs/piano_operativo.md`](piano_operativo.md) | Roadmap incrementale a 13 milestone (M0–M12) su 6 track tematiche e commit atomici |

---
