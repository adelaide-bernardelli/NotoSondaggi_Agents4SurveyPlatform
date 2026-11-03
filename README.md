# Noto Sondaggi SRL — Survey AI Platform (Architettura Speculare Antigravity + Claude)

## 1. A cosa serve questo repository
Questo progetto fornisce un'architettura multi-agente **human-in-the-loop** in lingua italiana progettata per **Noto Sondaggi SRL**, utilizzabile in modo nativo e speculare sia su **Google Antigravity** sia su **Claude Code**.

Il sistema supporta i ricercatori nel **Modulo A** del ciclo di ricerca demoscopica:
1. **Strutturazione del Brief** (`brief.md`) a partire da appunti, documenti del cliente o trascrizioni autorizzate;
2. **Stesura della Bozza del Questionario** (`questionnaire.md`) con tutela delle serie storiche e codifica distinta delle opzioni di non risposta;
3. **Audit Metodologico Item-per-Item** (`methodology.md`) con diagnosi dei rischi cognitivi e tre alternative di riformulazione per domanda;
4. **Screening Preliminare Privacy (GDPR Art. 9) e AI Act** (`compliance.md`);
5. **Consolidamento della Versione Finale Candidata** (`final.md`) sulla base delle sole modifiche approvate dal ricercatore umano.

Include inoltre le schede predisposte per i 3 agenti del **Modulo B** (*In attesa di attivazione*: analisi dati, reporting e dashboard).
Non include integrazioni automatiche con LimeSurvey, non raccoglie dati sul campo e non prende decisioni metodologiche o legali al posto del ricercatore.

---

## 2. Struttura Speculare del Progetto (Antigravity + Claude)

Ogni componente è mantenuto **specularmente** nelle due architetture:

```text
NotoSondaggi_Agents4SurveyPlatform/
├── AGENTS.md                                      # Regole globali e mappa architettura (Google Antigravity)
├── CLAUDE.md                                      # Regole globali e mappa architettura (Claude Code)
├── README.md                                      # Guida operativa del progetto
├── .agents/                                       # Architettura Google Antigravity
│   ├── agents/
│   │   ├── ai-coordinator.md                      # Supervisore e orchestratore (Modulo A)
│   │   ├── questionnaire-agent.md                 # Redattore brief, questionario e versione finale (Modulo A)
│   │   ├── methodology-agent.md                   # Revisore metodologico item-per-item (Modulo A)
│   │   ├── compliance-agent.md                    # Revisore preliminare GDPR Art. 9 / AI Act (Modulo A)
│   │   ├── analysis-agent.md                      # [In attesa di attivazione - Modulo B]
│   │   ├── reporting-agent.md                     # [In attesa di attivazione - Modulo B]
│   │   └── dashboard-agent.md                     # [In attesa di attivazione - Modulo B]
│   ├── skills/
│   │   ├── noto-survey-pipeline/SKILL.md          # Orchestrazione del caso e gestione runs/<caso>/status.md
│   │   ├── noto-brief-structuring/SKILL.md        # Strutturazione runs/<caso>/brief.md
│   │   ├── noto-questionnaire-drafting/SKILL.md   # Stesura runs/<caso>/questionnaire.md
│   │   ├── noto-methodology-audit/SKILL.md        # Audit runs/<caso>/methodology.md
│   │   ├── noto-compliance-check/SKILL.md         # Screening runs/<caso>/compliance.md
│   │   └── noto-questionnaire-consolidation/SKILL.md # Consolidamento runs/<caso>/final.md
│   └── workflows/
│       ├── nuova-indagine.md                      # Percorso completo: brief -> questionnaire -> methodology -> compliance -> final
│       ├── revisione-questionario.md              # Revisione: methodology -> compliance -> final
│       └── audit-singolo.md                       # Esecuzione mirata di methodology oppure compliance
├── .claude/                                       # Architettura Claude Code (speculare a .agents/)
│   ├── agents/*.md                                # 7 Agenti con frontmatter Claude Code
│   ├── skills/*/SKILL.md                          # 6 Skill speculari
│   └── commands/*.md                              # 3 Comandi slash (/nuova-indagine, /revisione-questionario, /audit-singolo)
├── templates/                                     # Template obbligatori per tutti gli artefatti
│   ├── status_template.md                         # Modello per runs/<caso>/status.md
│   ├── brief_template.md                          # Modello per runs/<caso>/brief.md
│   ├── questionnaire_template.md                  # Modello per runs/<caso>/questionnaire.md
│   ├── methodology_template.md                    # Modello per runs/<caso>/methodology.md
│   ├── compliance_template.md                     # Modello per runs/<caso>/compliance.md
│   └── final_template.md                          # Modello per runs/<caso>/final.md
├── examples/                                      # Materiali fittizi per test e confronto modelli
│   ├── brief_demo.md
│   ├── questionario_demo.md
│   └── confronto_modelli.csv
└── runs/                                          # Cartelle dei singoli casi di lavoro (ignorate da git)
```

---

## 3. Separazione dei Ruoli, Mappa Componenti e Flusso di Approvazione in Chat

Il sistema separa nettamente **supervisione** ed **esecuzione**:
- **`ai-coordinator`** agisce esclusivamente da supervisore: inizializza la cartella del caso `runs/<caso>/`, crea e aggiorna `runs/<caso>/status.md`, delega **una singola fase alla volta** allo specialista competente (`questionnaire-agent`, `methodology-agent`, `compliance-agent`), controlla che l'output rispetti il relativo template in `templates/` e si ferma per chiedere l'approvazione al ricercatore umano.
- **L'approvazione umana avviene direttamente in chat**: non occorre eseguire alcuno script da terminale. A ogni gate, il ricercatore umano risponde in chat approvando la fase, selezionando le alternative desiderate (es. Opzione A, B o C nell'audit metodologico) o chiedendo modifiche. `ai-coordinator` registra revisore, data, decisioni e note in `runs/<caso>/status.md`.

### 3.1 I 7 Agenti Speculari (`.agents/agents/` e `.claude/agents/`)
Ogni agente dispone di istruzioni operative strutturate (Identità, Riferimenti a Skill e Template, Contratto I/O, Procedura passo-passo, Checklist di autoverifica):

| Agente | Google Antigravity | Claude Code | Ruolo, Responsabilità e Artefatti Prodotti |
| :--- | :--- | :--- | :--- |
| **`ai-coordinator`** | `.agents/agents/ai-coordinator.md` | `.claude/agents/ai-coordinator.md` | **Puro Supervisore/Orchestratore**: inizializza e aggiorna `runs/<caso>/status.md`, delega una fase alla volta agli specialisti, verifica la conformità ai template e chiede approvazione umana in chat. Non redige mai direttamente gli artefatti specialistici. |
| **`questionnaire-agent`** | `.agents/agents/questionnaire-agent.md` | `.claude/agents/questionnaire-agent.md` | Redige `runs/<caso>/brief.md`, `runs/<caso>/questionnaire.md` e `runs/<caso>/final.md` tramite le 3 rispettive skill, garantendo codici distinti (`97=Non applicabile`, `98=Non so`, `99=Preferisco non rispondere`) e continuità delle serie storiche. |
| **`methodology-agent`** | `.agents/agents/methodology-agent.md` | `.claude/agents/methodology-agent.md` | Esegue l'audit metodologico item-per-item in `runs/<caso>/methodology.md` con griglia a 11 colonne e schede analitiche a 12 campi (con le 3 opzioni: *A: Conservare*, *B: Modifica minima*, *C: Revisione sostanziale*). |
| **`compliance-agent`** | `.agents/agents/compliance-agent.md` | `.claude/agents/compliance-agent.md` | Esegue lo screening preliminare GDPR (Art. 9) e AI Act in `runs/<caso>/compliance.md`, segnalando i punti bloccanti per DPO/consulente legale. |
| **`analysis-agent`** | `.agents/agents/analysis-agent.md` | `.claude/agents/analysis-agent.md` | *Scheda strutturata — In attesa di attivazione (Modulo B)*: verifica dati raccolti, pesatura e analisi descrittive riproducibili su piano statistico approvato. |
| **`reporting-agent`** | `.agents/agents/reporting-agent.md` | `.claude/agents/reporting-agent.md` | *Scheda strutturata — In attesa di attivazione (Modulo B)*: stesura di resoconti descrittivi e verificabili a partire esclusivamente da tavole statistiche validate. |
| **`dashboard-agent`** | `.agents/agents/dashboard-agent.md` | `.claude/agents/dashboard-agent.md` | *Scheda strutturata — In attesa di attivazione (Modulo B)*: progettazione di specifiche grafiche e layout descrittivi con metadati completi, senza pubblicazione autonoma. |

### 3.2 Le 6 Skill Speculari (`.agents/skills/` e `.claude/skills/`)
Richiamabili sia dagli agenti durante un workflow sia direttamente dal supervisore umano:

| Skill | Google Antigravity | Claude Code | Agente Associato | Funzione Operativa |
| :--- | :--- | :--- | :--- | :--- |
| **`noto-survey-pipeline`** | `.agents/skills/noto-survey-pipeline/SKILL.md` | `.claude/skills/noto-survey-pipeline/SKILL.md` | `ai-coordinator` | Orchestrazione del ciclo di vita del caso, gestione dei gate umani in chat e aggiornamento di `runs/<caso>/status.md`. |
| **`noto-brief-structuring`** | `.agents/skills/noto-brief-structuring/SKILL.md` | `.claude/skills/noto-brief-structuring/SKILL.md` | `questionnaire-agent` | Analisi dei documenti in `runs/<caso>/source/`, individuazione delle lacune informative e stesura di `runs/<caso>/brief.md`. |
| **`noto-questionnaire-drafting`** | `.agents/skills/noto-questionnaire-drafting/SKILL.md` | `.claude/skills/noto-questionnaire-drafting/SKILL.md` | `questionnaire-agent` | Progettazione e stesura di `runs/<caso>/questionnaire.md` a partire dal brief approvato, con codici `97/98/99`, filtri e tutela serie storiche. |
| **`noto-methodology-audit`** | `.agents/skills/noto-methodology-audit/SKILL.md` | `.claude/skills/noto-methodology-audit/SKILL.md` | `methodology-agent` | Audit metodologico item-per-item in `runs/<caso>/methodology.md` (e tracciamento comparativo opzionale in `examples/confronto_modelli.csv`). |
| **`noto-compliance-check`** | `.agents/skills/noto-compliance-check/SKILL.md` | `.claude/skills/noto-compliance-check/SKILL.md` | `compliance-agent` | Screening preliminare privacy (GDPR Art. 9) e governance AI Act in `runs/<caso>/compliance.md`. |
| **`noto-questionnaire-consolidation`** | `.agents/skills/noto-questionnaire-consolidation/SKILL.md` | `.claude/skills/noto-questionnaire-consolidation/SKILL.md` | `questionnaire-agent` | Recepimento delle sole modifiche approvate dal ricercatore in `runs/<caso>/status.md` e consolidamento di `runs/<caso>/final.md`. |

### 3.3 I 3 Workflow / Comandi Speculari (`.agents/workflows/` e `.claude/commands/`)
Percorsi guidati multi-fase invocabili tramite comando `/` dal supervisore umano o eseguiti da `ai-coordinator`:

| Workflow / Comando | Google Antigravity | Claude Code | Sequenza delle Fasi | Caso d'Uso |
| :--- | :--- | :--- | :--- | :--- |
| **`/nuova-indagine`** | `.agents/workflows/nuova-indagine.md` | `.claude/commands/nuova-indagine.md` | `brief -> questionnaire -> methodology -> compliance -> final` | Creazione completa di una nuova indagine a partire da appunti, brief cliente o trascrizione autorizzata. |
| **`/revisione-questionario`** | `.agents/workflows/revisione-questionario.md` | `.claude/commands/revisione-questionario.md` | `methodology -> compliance -> final` | Audit e consolidamento di un questionario già redatto o storico copiato in `runs/<caso>/source/`. |
| **`/audit-singolo`** | `.agents/workflows/audit-singolo.md` | `.claude/commands/audit-singolo.md` | `methodology` *oppure* `compliance` | Esecuzione rapida e mirata del solo audit metodologico o del solo screening di conformità su un documento. |

### 3.4 I 6 Template Obbligatori (`templates/`)
Ogni artefatto generato nella cartella `runs/<caso>/` deve seguire fedelmente la struttura del relativo template:

| Template | Artefatto Target in `runs/<caso>/` | Agente Responsabile | Skill Associata | Contenuto Strutturale Principale |
| :--- | :--- | :--- | :--- | :--- |
| `templates/status_template.md` | `runs/<caso>/status.md` | `ai-coordinator` | `noto-survey-pipeline` | Metadati del caso, tabella avanzamento delle 5 fasi del Modulo A, registro cronologico delle decisioni umane in chat, blocchi pre-campo. |
| `templates/brief_template.md` | `runs/<caso>/brief.md` | `questionnaire-agent` | `noto-brief-structuring` | Inquadramento e fonti (`[DA VERIFICARE]`), obiettivi e costrutti, disegno proposto o `DA DEFINIRE`, vincoli e domande per il ricercatore. |
| `templates/questionnaire_template.md` | `runs/<caso>/questionnaire.md` | `questionnaire-agent` | `noto-questionnaire-drafting` | Metadati, introduzione, domande per sezione con codici distinti (`97=Non applicabile`, `98=Non so`, `99=Preferisco non rispondere`), filtri/*skip*, serie storiche. |
| `templates/methodology_template.md` | `runs/<caso>/methodology.md` | `methodology-agent` | `noto-methodology-audit` | Metodo e limiti, griglia a 11 colonne, schede analitiche a 12 campi con le 3 opzioni (*A: Conservare*, *B: Modifica minima*, *C: Revisione sostanziale*), bozza riformulata, piano *pretest/pilot*. |
| `templates/compliance_template.md` | `runs/<caso>/compliance.md` | `compliance-agent` | `noto-compliance-check` | Perimetro dati, griglia di screening domanda-per-domanda (Art. 9 GDPR, identificazione indiretta, *"Preferisco non rispondere"*), checklist GDPR/AI Act, blocchi per DPO/legale. |
| `templates/final_template.md` | `runs/<caso>/final.md` | `questionnaire-agent` | `noto-questionnaire-consolidation` | Metadati di consolidamento, registro modifiche accettate/scartate, prescrizioni compliance recepite, testo definitivo con codici `97/98/99`, mappa filtri, piano validazione empirica. |

---

## 4. Come iniziare (Guida Rapida)

### Apertura del Progetto
- **Su Google Antigravity**: apri la cartella del progetto come Workspace. Antigravity caricherà automaticamente `AGENTS.md`, gli agenti in `.agents/agents/`, le skill in `.agents/skills/` e i workflow in `.agents/workflows/`.
- **Su Claude Code**: apri il terminale o l'estensione IDE nella cartella del progetto. Claude Code caricherà automaticamente `CLAUDE.md`, i subagent in `.claude/agents/`, le skill in `.claude/skills/` e i comandi slash in `.claude/commands/`.

### Scenario A — Avviare una Nuova Indagine (`nuova-indagine`)
Sequenza: `brief -> questionnaire -> methodology -> compliance -> final`

1. Scrivi in chat:
   > `Avvia il workflow /nuova-indagine per il caso "esempio-biblioteca" usando come input examples/brief_demo.md. Esegui la prima fase (brief) e fermati per la mia approvazione.`
2. `ai-coordinator` creerà `runs/esempio-biblioteca/source/brief_demo.md`, inizializzerà `runs/esempio-biblioteca/status.md` e delegherà a `questionnaire-agent` (tramite la skill `noto-brief-structuring`) la creazione di `runs/esempio-biblioteca/brief.md`.
3. Esamina `runs/esempio-biblioteca/brief.md` e rispondi direttamente in chat, ad esempio:
   > `Approvo il brief (revisore: Adelaide). Come modalità confermo CAWI, 8 domande complessive. Procedi con la fase questionnaire.`
4. `ai-coordinator` registrerà l'approvazione e le tue indicazioni in `runs/esempio-biblioteca/status.md` e delegherà la fase successiva. Ripeti il controllo in chat fino alla generazione di `runs/esempio-biblioteca/final.md`.

### Scenario B — Revisionare un Questionario Esistente (`revisione-questionario`)
Sequenza: `methodology -> compliance -> final`

1. Scrivi in chat:
   > `Avvia il workflow /revisione-questionario per il caso "prova-revisione" a partire da examples/questionario_demo.md.`
2. Il coordinatore salterà `brief` e `questionnaire`, copierà il file originale in `runs/prova-revisione/source/` e delegherà subito a `methodology-agent` l'audit metodologico in `runs/prova-revisione/methodology.md`.
3. Rispondi in chat indicando per ogni domanda (`Q1`-`Q5`) quale alternativa approvi (*Opzione A: Conservare*, *Opzione B: Modifica minima*, *Opzione C: Revisione sostanziale*), quindi prosegui con `compliance` e `final`.

### Scenario C — Eseguire un Audit Singolo o Invocare una Singola Skill (`audit-singolo`)
Puoi anche richiedere un controllo puntuale usando `/audit-singolo` oppure invocando direttamente una delle 6 skill:
- `/noto-brief-structuring` — per strutturare solo un brief;
- `/noto-questionnaire-drafting` — per redigere solo una bozza di questionario;
- `/noto-methodology-audit` — per eseguire solo l'audit metodologico;
- `/noto-compliance-check` — per eseguire solo lo screening preliminare GDPR Art. 9 / AI Act;
- `/noto-questionnaire-consolidation` — per consolidare la versione finale;
- `/noto-survey-pipeline` — per orchestrare e verificare lo stato in `runs/<caso>/status.md`.

---

## 5. Confronto Scientifico tra Modelli e Sicurezza
- **Modelli diversi != agenti diversi**: i ruoli specializzati e il modello LLM sottostante (`model: inherit`) sono due assi distinti. Per confrontare diversi modelli a parità di caso e di input, avvia casi separati in `runs/` e registra le metriche nel tracciato `examples/confronto_modelli.csv`.
- **Sicurezza e rigore metodologico**: questo sistema opera esclusivamente su file locali autorizzati. Non inserire dati personali identificativi o microdati reali di rispondenti nei prompt. Ricorda che l'impatto delle riformulazioni sulla non risposta è sempre un'**ipotesi da verificare empiricamente** tramite *pretest*, *cognitive interview* o *split ballot*.
