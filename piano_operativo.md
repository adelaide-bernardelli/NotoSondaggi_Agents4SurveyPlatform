# Piano Operativo di Implementazione e Roadmap a Milestones (Git Commit-Driven)
## Piattaforma Multi-Agente Human-in-the-Loop per Indagini Demoscopiche — Noto Sondaggi SRL

> **Documento Operativo di Sviluppo e Guida all'Implementazione Incrementale**  
> **Istituzione**: Università degli Studi di Pavia / IUSS Pavia  
> **Supervisione Accademica**: Prof.ssa Alessandra Amendola  
> **Committente / Partner Industriale**: Noto Sondaggi SRL  
> **Riferimento di Stato**: `statoprogetto.md` (Versione 3.0 — Censimento dei 35 Task)  
> **Principio Guida**: Massimizzazione dell'autonomia realizzativa del ricercatore, coerenza tematica modulare (divieto di frammentazione tra moduli non correlati), tracciabilità atomica (1 Milestone = 1 Commit Git) e perimetro Human-in-the-Loop rigoroso.

---

## 1. Architettura del Piano e Principi di Sviluppo

Il presente piano operativo traduce i 35 task censiti in `statoprogetto.md` in una roadmap esecutiva rigorosa, strutturata per consentire allo sviluppatore/ricercatore di procedere in maniera focalizzata, progressiva e verificabile.

### 1.1 Regole di Esecuzione delle Milestones
1. **Relazione Biunivoca Milestone-Commit (1 Milestone = 1 Commit Git)**:
   - Ogni milestone rappresenta un incremento funzionale atomico, completo e autocontenuto.
   - Non si effettuano commit parziali o "infranti" che lascino il repository in uno stato non funzionante o asimmetrico.
   - Il messaggio di commit deve seguire rigorosamente la convenzione *Conventional Commits* (`feat:`, `refactor:`, `test:`, `docs:`, `chore:`).
2. **Coerenza Modulare Sequenziale (No "salti di palo in frasca")**:
   - I compiti non vengono svolti in modo disgiunto o disordinato. Lo sviluppo procede per tracce logiche omogenee:
     - **Track 0**: Consolidamento baseline & QA tooling;
     - **Track 1**: Fieldwork Bridge (Esportatore nativo LimeSurvey);
     - **Track 2**: Ingestione della conoscenza storica e batterie standard (`noto-survey-extractor`);
     - **Track 3**: Guida di somministrazione per intervistatore e note di regia (CATI/CAWI);
     - **Track 4**: Reporting regolamentare AGCOM (Delibera 256/10/CSP — Modulo B autonomo);
     - **🛑 GATE DI STOP OBBLIGATORIO**: Sospensione formale dello sviluppo e allineamento con Noto Sondaggi SRL & DPO;
     - **Track 5**: Calibrazione post-feedback, conformità legale DPO e validazione end-to-end su indagine reale.
3. **Doppia Specularità Integrale Obbligatoria**:
   - Qualsiasi modifica o creazione di agenti (`.agents/agents/` vs `.claude/agents/`), skill (`.agents/skills/` vs `.claude/skills/`), workflow/comandi (`.agents/workflows/` vs `.claude/commands/`) e regole (`AGENTS.md` vs `CLAUDE.md`) deve avvenire simultaneamente in entrambi i rami speculari.
   - Nessun commit che tocchi l'architettura degli agenti può essere approvato senza il passaggio con esito positivo di `python scripts/check_mirror_sync.py`.
4. **Verificabilità Continua (Runnable Acceptance Criteria)**:
   - Ogni singola milestone include uno o più comandi di verifica eseguibili da terminale (PowerShell / Bash), comprendenti test unitari, linter e validazione degli artefatti.

---

## 2. Quadro Sinottico della Roadmap Operativa (13 Milestones, 6 Track)

| ID | Track Tematica | Titolo Funzionale | Conventional Commit Proposto | Dipendenza da Noto | Task statoprogetto.md | File Chiave Coinvolti | Comando di Verifica |
| :---: | :--- | :--- | :--- | :---: | :---: | :--- | :--- |
| **M0** | **Track 0: Baseline & QA** | Consolidamento baseline, QA validator, suite test e fixture demo biblioteca | `chore(core): consolidate baseline state, QA validators and demo run` | Nessuna (100% Autonomo) | #01, #02, #03, #04, #16, #17, #19 | `statoprogetto.md`, `scripts/check_mirror_sync.py`, `scripts/validate_runs.py`, `tests/test_qa_baseline.py`, `piano_operativo.md` | `python scripts/check_mirror_sync.py`<br>`python scripts/validate_runs.py examples/demo_run_biblioteca`<br>`python -m unittest tests/test_qa_baseline.py` |
| **M1** | **Track 1: Fieldwork Bridge** | Parser questionario ed esportatore nativo LimeSurvey TSV (14 colonne standard) | `feat(export): implement automated LimeSurvey TSV structure generator from final questionnaire` | Nessuna (100% Autonomo) | #26 | `scripts/export_limesurvey.py`, `tests/test_export_limesurvey.py`, `tests/__init__.py` | `python scripts/export_limesurvey.py examples/demo_run_biblioteca/final.md`<br>`python -m unittest tests/test_export_limesurvey.py` |
| **M2** | **Track 1: Fieldwork Bridge** | Integrazione export LimeSurvey nella pipeline multi-agente e specularità | `feat(pipeline): integrate LimeSurvey export into survey pipeline and update dual mirror specifications` | Nessuna (100% Autonomo) | #26, #15, #02 | `.agents/skills/noto-survey-pipeline/SKILL.md`, `.claude/skills/noto-survey-pipeline/SKILL.md`, `AGENTS.md`, `CLAUDE.md` | `python scripts/check_mirror_sync.py`<br>`python scripts/validate_runs.py examples/demo_run_biblioteca` |
| **M3** | **Track 2: Knowledge & Extractor** | Definizione speculare della skill specialistica `noto-survey-extractor` | `feat(extractor): implement dual mirrored noto-survey-extractor skill for historical questionnaire ingestion` | Nessuna (100% Autonomo) | #09, #22, #02 | `.agents/skills/noto-survey-extractor/SKILL.md`, `.claude/skills/noto-survey-extractor/SKILL.md`, agenti, `AGENTS.md`, `CLAUDE.md` | `python scripts/check_mirror_sync.py` |
| **M4** | **Track 2: Knowledge & Extractor** | Tool CLI di estrazione e libreria baseline socio-demografica (Istat) ed elettorale | `feat(knowledge): add survey extraction CLI and canonical demographic and political baseline batteries` | Nessuna (100% Autonomo) | #08, #09, #22 | `scripts/extract_survey_knowledge.py`, `knowledge/demographics_standard.json`, `knowledge/political_batteries_core.json` | `python scripts/extract_survey_knowledge.py --help`<br>`python -m unittest tests/test_survey_knowledge.py` |
| **M5** | **Track 3: Regia Intervistatore** | Generatore guida intervistatore CATI/CAPI con note di regia e formato Word/Markdown | `feat(interviewer): implement interviewer guide generator with typographical regia instructions and docx export` | Nessuna (100% Autonomo) | #27, #12 | `scripts/generate_interviewer_guide.py`, `tests/test_interviewer_guide.py` | `python scripts/generate_interviewer_guide.py examples/demo_run_biblioteca/final.md`<br>`python -m unittest tests/test_interviewer_guide.py` |
| **M6** | **Track 3: Regia Intervistatore** | Standardizzazione sintassi di regia nei template, nelle skill e nel linter | `refactor(drafting): standardize interviewer regia syntax across templates, skills and validator` | Nessuna (100% Autonomo) | #27, #07, #15, #17 | `templates/questionnaire_template.md`, `templates/final_template.md`, skill drafting/consolidation, `scripts/validate_runs.py` | `python scripts/check_mirror_sync.py`<br>`python scripts/validate_runs.py examples/demo_run_biblioteca` |
| **M7** | **Track 4: Reporting AGCOM** | Template normativo e generatore automatico Scheda AGCOM (Delibera 256/10/CSP) | `feat(agcom): add regulatory AGCOM survey disclosure template and automated report generator` | Nessuna (100% Autonomo) | #33 | `templates/agcom_template.md`, `scripts/generate_agcom_report.py`, `tests/test_agcom_report.py` | `python scripts/generate_agcom_report.py examples/demo_run_biblioteca`<br>`python -m unittest tests/test_agcom_report.py` |
| **M8** | **Track 4: Reporting AGCOM** | Attivazione controllata `reporting-agent` e skill speculare `noto-agcom-reporting` | `feat(reporting): activate reporting-agent for automated AGCOM disclosure with mirrored skill` | Nessuna (100% Autonomo) | #33, #02 (differito #28) | `.agents/skills/noto-agcom-reporting/SKILL.md`, `.claude/skills/noto-agcom-reporting/SKILL.md`, `reporting-agent.md`, `AGENTS.md`, `CLAUDE.md` | `python scripts/check_mirror_sync.py` |
| 🛑 | **STOP OBBLIGATORIO** | **Gate di Stop: Allineamento e Validazione Esterna con Noto Sondaggi SRL & DPO** | *Nessun commit — Sessione di lavoro esterna (riunione 20-25 min e riscontro scritto)* | **BLOCCANTE PER M9-M12** | #06, #08, #11, #12, #14, #23, #24, #25 | Documento di sintesi, demo dal vivo esportatori, checklist §5.1 di statoprogetto.md | Verbale di allineamento firmato o riscontro email formale Noto Sondaggi |
| **M9** | **Track 5: Post-Feedback Noto** | Integrazione standard socio-demografici e batterie politiche ufficiali Noto | `feat(noto-standards): integrate official Noto demographics, client taxonomy and calibrated historical batteries` | Sbloccato da Feedback Noto | #06, #08, #23 | `knowledge/noto_demographics_profile.json`, `knowledge/noto_historical_batteries.json`, `templates/brief_template.md` | `python scripts/check_mirror_sync.py`<br>`python -m unittest tests/test_survey_knowledge.py` |
| **M10** | **Track 5: Post-Feedback Noto** | Recepimento prescrizioni DPO/legale su Art. 9 GDPR e informativa di somministrazione | `refactor(compliance): incorporate DPO legal review feedback into Art 9 GDPR screening checklist and consent notices` | Sbloccato da Parere DPO | #13, #14 | `templates/compliance_template.md`, skill compliance speculari, `AGENTS.md`, `CLAUDE.md` | `python scripts/check_mirror_sync.py` |
| **M11** | **Track 5: Post-Feedback Noto** | Validazione end-to-end su studio di caso reale Noto Sondaggi (`runs/caso-reale-noto/`) | `test(validation): complete full end-to-end benchmark run on real Noto Sondaggi case study` | Sbloccato da Dati Reali Noto | #20, #22, #26, #27, #33 | `runs/caso-reale-noto/*` | `python scripts/validate_runs.py runs/caso-reale-noto` |
| **M12** | **Track 5: Post-Feedback Noto** | Chiusura Release v1.0.0, aggiornamento ufficiale `statoprogetto.md` e sintesi accademica | `docs(release): finalize v1.0.0 milestone with completed Modulo A and AGCOM reporting` | Sbloccato da Approvazione Finale | Tutti i 35 task riesaminati | `statoprogetto.md`, `README.md`, documentazione istituzionale | `python scripts/check_mirror_sync.py`<br>`python scripts/validate_runs.py examples/demo_run_biblioteca runs/caso-reale-noto`<br>`python -m unittest discover tests/` |

---

## 3. Schede Analitiche delle Milestones Autonome (Pre-Feedback Noto)

Di seguito vengono dettagliate le milestone appartenenti ai blocchi realizzabili in piena autonomia dal ricercatore prima di richiedere il confronto operativo con Noto Sondaggi SRL.

---

### Milestone M0: Consolidamento Baseline, QA Validators, Suite Test e Caso Demo
- **Track Tematica**: Track 0 — Consolidamento Baseline & QA Tooling
- **Task Correlati in statoprogetto.md**: #01, #02, #03, #04, #16, #17, #19
- **Condizione Operativa**: `ULTIMATO` / `Sviluppabile subito internamente` (Autonomia Totale).
- **Obiettivo**:
  Assicurare che il punto di partenza del repository sia rigorosamente tracciato e immutabile in git: aggiungere al version control gli script di validazione già funzionanti (`scripts/check_mirror_sync.py`, `scripts/validate_runs.py`), la prima suite di test automatizzati (`tests/test_qa_baseline.py`), il documento di censimento `statoprogetto.md`, il piano operativo `piano_operativo.md` e il caso di test end-to-end tracciato `examples/demo_run_biblioteca/`.
- **Messaggio di Commit Proposto**:
  ```bash
  git commit -m "chore(core): consolidate baseline state, QA validators and demo run"
  ```
- **File Toccati / Creati**:
  - `statoprogetto.md` (Documento di censimento ufficiale dei 35 task);
  - `piano_operativo.md` (La presente roadmap esecutiva);
  - `scripts/check_mirror_sync.py` (Script di verifica automatica specularità `.agents/` vs `.claude/`);
  - `scripts/validate_runs.py` (Linter metodologico degli artefatti in `runs/` ed `examples/`);
  - `tests/__init__.py` e `tests/test_qa_baseline.py` (Inizializzazione suite di test unitari);
  - `examples/demo_run_biblioteca/` (`status.md`, `questionnaire.md`, `methodology.md`, `compliance.md`, `final.md`).
- **Dettaglio Implementativo Passo-Passo**:
  1. Verificare che `scripts/check_mirror_sync.py` termini con esito zero;
  2. Verificare che `scripts/validate_runs.py examples/demo_run_biblioteca` validi il caso demo senza errori;
  3. Verificare che la suite unit test `python -m unittest tests/test_qa_baseline.py` superi tutti i 6 test di regressione;
  4. Aggiungere i file tracciati a git staging (`git add statoprogetto.md piano_operativo.md scripts/ tests/ examples/demo_run_biblioteca/`);
  5. Eseguire il commit atomico consolidando la baseline pulita.
- **Criteri di Accettazione e Verifica**:
  ```powershell
  python scripts/check_mirror_sync.py
  # Output atteso: [OK] per tutti i controlli, esito 0.
  python scripts/validate_runs.py examples/demo_run_biblioteca
  # Output atteso: [PASS] Tutti i file presenti risultano conformi agli standard metodologici.
  python -m unittest tests/test_qa_baseline.py
  # Output atteso: Ran 6 tests ... OK.
  git status
  # Output atteso: Working tree clean (o solo file binari docx ausiliari non tracciati).
  ```

---

### Milestone M1: Parser del Questionario Consolidato ed Esportatore LimeSurvey TSV (14 Colonne Standard)
- **Track Tematica**: Track 1 — Fieldwork Bridge (Integrazione Piattaforma di Rilevazione)
- **Task Correlati in statoprogetto.md**: #26 (Priorità Tecnica)
- **Condizione Operativa**: `Sviluppabile subito internamente` (Autonomia Totale — Noto impiega ordinariamente LimeSurvey).
- **Obiettivo**:
  Sviluppare un tool CLI Python autonomo (`scripts/export_limesurvey.py`) che prenda in ingresso un questionario consolidato conforme a `templates/final_template.md` (es. `examples/demo_run_biblioteca/final.md` o `runs/<caso>/final.md`) e produca il file di definizione indagine nativo tab-delimited (`.txt` TSV) importabile direttamente nell'interfaccia amministrativa di LimeSurvey, senza dipendenze esterne.
- **Messaggio di Commit Proposto**:
  ```bash
  git commit -m "feat(export): implement automated LimeSurvey TSV structure generator from final questionnaire"
  ```
- **File Toccati / Creati**:
  - `scripts/export_limesurvey.py` (Nuovo script CLI di parsing ed esportazione TSV standard);
  - `tests/test_export_limesurvey.py` (Suite di test unitari con fixture su casi reali e sintetici);
  - `tests/__init__.py`.
- **Dettaglio Implementativo Passo-Passo**:
  1. **Specifiche del formato LimeSurvey TSV (14 colonne standard)**:
     - Intestazione standard tab-delimited obbligatoria:
       ```tsv
       id	related_id	class	type/scale	name	relevance	text	help	language	validation	mandatory	other	default	same_default
       ```
     - Gerarchia formale delle classi di record generate:
       - **Record Indagine (`class = S`)**: definisce l'ID indagine, lo stato attivo, e la lingua di default (`it`);
       - **Record Impostazioni Lingua (`class = SL`)**: `text` contiene i testi localizzati (titolo indagine, descrizione, messaggi di benvenuto ed esito);
       - **Record Gruppo (`class = G`)**: mappati a partire dalle sezioni tematiche del questionario (`### Sezione A — ...`), con nome gruppo in `text` e descrizione in `help`;
       - **Record Domanda (`class = Q`)**: codice domanda in `name` (`Q01`, `Q02`), testo in `text`, note di regia/istruzioni in `help`, indicatore di obbligatorietà `mandatory` (`Y` o `N`), tipo domanda in `type/scale`:
         - `L` = Lista radio (scelta singola);
         - `M` = Scelta multipla;
         - `T` = Testo esteso / aperto;
         - `S` = Testo breve;
         - `N` = Numerico;
         - `F` = Matrice / Batteria;
         - `5` = Scelta a 5 punti;
       - **Record Sotto-Domanda (`class = SQ`)**: per batterie a matrice (`F`) o per opzioni di scelta multipla (`M`), con `related_id` collegato all'`id` della domanda padre;
       - **Record Risposte (`class = A`)**: opzioni di risposta per liste radio (`L`), con `name` = codice opzione, `text` = etichetta testuale, `type/scale = 0` (scala 0), `related_id` collegato all'`id` della domanda padre;
       - **Gestione codici standard di non risposta**:
         - `97` -> "Non applicabile"
         - `98` -> "Non so / Non conosco"
         - `99` -> "Preferisco non rispondere / Rifiuto"
       - **Relevance Equations**: traduzione automatica dei filtri condizionali in sintassi ExpressionScript (es. `Q01.NAOK == "1"` o `!is_empty(Q02)`).
  2. **Funzionalità CLI**:
     - Sintassi: `python scripts/export_limesurvey.py <path_to_final.md> [--output <path_output.txt>] [--lang it]`.
     - Output standard su file `.txt` codificato UTF-8 senza BOM (o UTF-8 conforme).
     - Validazione sintattica interna per prevenire record TSV malformati o riferimenti orfani.
  3. **Suite di Test**:
     - Test unitario che esegue l'esportazione su `examples/demo_run_biblioteca/final.md`;
     - Verifica della presenza di tutti i record `S`, `SL`, `G`, `Q`, `A` e della corretta inclusione dei codici `97`, `98` e `99`;
     - Verifica che il file generato contenga esattamente 14 colonne separate da tabulazione per ogni riga.
- **Criteri di Accettazione e Verifica**:
  ```powershell
  python scripts/export_limesurvey.py examples/demo_run_biblioteca/final.md --output examples/demo_run_biblioteca/limesurvey_survey.txt
  # Output atteso: File TSV generato correttamente con 14 colonne standard.
  python -m unittest tests/test_export_limesurvey.py
  # Output atteso: OK (tutti i test superati).
  ```

---

### Milestone M2: Integrazione Esportatore LimeSurvey nella Pipeline Multi-Agente
- **Track Tematica**: Track 1 — Fieldwork Bridge
- **Task Correlati in statoprogetto.md**: #26, #15, #02
- **Condizione Operativa**: `Sviluppabile subito internamente` (Autonomia Totale).
- **Obiettivo**:
  Integrare l'invocazione dell'esportatore LimeSurvey all'interno della skill di orchestrazione `noto-survey-pipeline` e nel contratto di `questionnaire-agent` al momento della finalizzazione di `final.md`, garantendo la perfetta simmetria tra Google Antigravity (`.agents/`) e Claude Code (`.claude/`).
- **Messaggio di Commit Proposto**:
  ```bash
  git commit -m "feat(pipeline): integrate LimeSurvey export into survey pipeline and update dual mirror specifications"
  ```
- **File Toccati / Creati**:
  - `.agents/skills/noto-survey-pipeline/SKILL.md` (Istruzione per generazione automatica del file TSV al consolidamento);
  - `.claude/skills/noto-survey-pipeline/SKILL.md` (Aggiornamento speculare identico);
  - `AGENTS.md` (Menzione dell'artefatto `runs/<caso>/limesurvey_survey.txt` tra gli output opzionali/derivati);
  - `CLAUDE.md` (Aggiornamento speculare identico);
  - `scripts/validate_runs.py` (Estensione del linter: se è presente `limesurvey_survey.txt`, ne verifica la formattazione a colonne TSV).
- **Dettaglio Implementativo Passo-Passo**:
  1. Modificare `SKILL.md` della pipeline in entrambe le cartelle per inserire lo step di esportazione LimeSurvey post-approvazione umana della fase `final`;
  2. Aggiornare `scripts/validate_runs.py` aggiungendo la funzione `validate_limesurvey_file(path)`;
  3. Eseguire `scripts/check_mirror_sync.py` per validare l'allineamento byte-per-byte tra `.agents/` e `.claude/`.
- **Criteri di Accettazione e Verifica**:
  ```powershell
  python scripts/check_mirror_sync.py
  # Output atteso: Architettura speculare integra al 100%.
  python scripts/validate_runs.py examples/demo_run_biblioteca
  # Output atteso: Conformità confermata.
  ```

---

### Milestone M3: Definizione Speculare della Skill `noto-survey-extractor`
- **Track Tematica**: Track 2 — Knowledge & Historical Extractor
- **Task Correlati in statoprogetto.md**: #09, #22, #02
- **Condizione Operativa**: `Sviluppabile subito internamente` (Autonomia Totale — Proposta architetturale formalizzata).
- **Obiettivo**:
  Formalizzare e implementare la nuova skill specialistica `noto-survey-extractor` per estrarre in modo strutturato formulari, scale, codici e metadati da questionari storici e report già disponibili internamente, inserendola nel registro delle skill con perfetta specularità.
- **Messaggio di Commit Proposto**:
  ```bash
  git commit -m "feat(extractor): implement dual mirrored noto-survey-extractor skill for historical questionnaire ingestion"
  ```
- **File Toccati / Creati**:
  - `.agents/skills/noto-survey-extractor/SKILL.md` (Nuova skill di estrazione per Google Antigravity);
  - `.claude/skills/noto-survey-extractor/SKILL.md` (Nuova skill di estrazione identica per Claude Code);
  - `.agents/agents/questionnaire-agent.md` e `.claude/agents/questionnaire-agent.md` (Abilitazione della skill nell'agente di redazione);
  - `AGENTS.md` e `CLAUDE.md` (Censimento della 7ª skill nel catalogo ufficiale del progetto);
  - `scripts/check_mirror_sync.py` (Aggiornamento per verificare l'esistenza e la specularità di tutte le 7 skill).
- **Dettaglio Implementativo Passo-Passo**:
  1. Creare la specifica di `noto-survey-extractor`:
     - Frontmatter YAML valido con descrizione, parametri e contesto;
     - Fasi operative:
       a. Parsing del documento in input (identificazione di sezioni, numeri domanda, testi, scale);
       b. Riconoscimento delle tipologie standard (Fiducia Leader, Voto Elettorale, Batterie di Gradimento, Dati Socio-Demografici);
       c. Estrazione della scala utilizzata (es. 1-10, 4 punti con etichette semantiche, dicotomica Si/No);
       d. Generazione del dizionario strutturato standardizzato;
  2. Aggiornare `questionnaire-agent.md` e il coordinatore;
  3. Modificare `scripts/check_mirror_sync.py` affinché conti 7 skill attive anziché 6;
  4. Verificare che l'architettura speculare superi il test.
- **Criteri di Accettazione e Verifica**:
  ```powershell
  python scripts/check_mirror_sync.py
  # Output atteso: Tutte le 7 skill sono perfettamente identiche. Architettura speculare integra al 100%.
  ```

---

### Milestone M4: Tooling di Estrazione e Libreria Baseline Socio-Demografica (Istat) ed Elettorale
- **Track Tematica**: Track 2 — Knowledge & Historical Extractor
- **Task Correlati in statoprogetto.md**: #08, #09, #22
- **Condizione Operativa**: `Sviluppabile subito internamente` (Autonomia Totale — Basato su standard Istat/Eurostat e questionari campione noti).
- **Obiettivo**:
  Sviluppare lo script CLI `scripts/extract_survey_knowledge.py` per automatizzare l'estrazione e formalizzare nella cartella `knowledge/` la libreria canonica di riferimento delle batterie socio-demografiche e delle formulazioni elettorali standard (utilizzabile dagli agenti in fase di drafting per garantire comparabilità storica).
- **Messaggio di Commit Proposto**:
  ```bash
  git commit -m "feat(knowledge): add survey extraction CLI and canonical demographic and political baseline batteries"
  ```
- **File Toccati / Creati**:
  - `scripts/extract_survey_knowledge.py` (Script CLI per parsing di questionari e generazione di dizionari JSON/MD);
  - `knowledge/demographics_standard.json` (Batterie anagrafiche Istat: Genere, Classi d'Età standard `18-24 / 25-34 / 35-44 / 45-54 / 55-64 / 65+`, Titolo di Studio, Condizione Lavorativa, Ripartizione NUTS-1, Ampiezza Comune);
  - `knowledge/political_batteries_core.json` (Fiducia nel Presidente del Consiglio, fiducia nei principali leader su scala 1-10 o 4 punti, intenzioni di voto politico con codici lista, giudizio sull'operato di governo);
  - `tests/test_survey_knowledge.py` (Test di conformità strutturale dei file knowledge e del parser).
- **Dettaglio Implementativo Passo-Passo**:
  1. Realizzare `scripts/extract_survey_knowledge.py`:
     - Legge file di testo/markdown/raw;
     - Riconosce pattern di domanda con espressioni regolari e segmentazione euristica;
     - Emette file strutturato JSON normalizzato con chiavi: `id_item`, `construct`, `question_text`, `response_options` (con codici `code` e `label`), `missing_codes` (con `97`, `98`, `99`), `scale_type`.
  2. Popolare `knowledge/demographics_standard.json` con lo standard ufficiale Istat/Eurostat adottato dal team;
  3. Popolare `knowledge/political_batteries_core.json` con i costrutti standard di monitoraggio politico ed elettorale;
  4. Scrivere test unitari che verifichino che ogni item del catalogo rispetti i codici obbligatori `97`, `98`, `99` e le convenzioni di polarità.
- **Criteri di Accettazione e Verifica**:
  ```powershell
  python scripts/extract_survey_knowledge.py --help
  python -m unittest tests/test_survey_knowledge.py
  # Output atteso: OK (tutti i test superati).
  ```

---

### Milestone M5: Generatore Guida Intervistatore CATI/CAPI con Istruzioni di Regia Tipografica
- **Track Tematica**: Track 3 — Regia Intervistatore e Formato di Somministrazione
- **Task Correlati in statoprogetto.md**: #27, #12
- **Condizione Operativa**: `Sviluppabile subito internamente` (Autonomia Totale).
- **Obiettivo**:
  Sviluppare un generatore automatico (`scripts/generate_interviewer_guide.py`) che trasformi il questionario finale (`final.md`) in una guida esecutiva per l'intervistatore della sala telefonica CATI o per somministrazione assistita CAPI. Il layout tipografico deve separare in modo netto il testo da pronunciare a voce alta dalle note di regia riservate all'operatore, garantendo funzionamento autonomo con zero dipendenze obbligatorie (output primario Markdown/HTML e supporto opzionale a `.docx` tramite `python-docx`).
- **Messaggio di Commit Proposto**:
  ```bash
  git commit -m "feat(interviewer): implement interviewer guide generator with typographical regia instructions and docx export"
  ```
- **File Toccati / Creati**:
  - `scripts/generate_interviewer_guide.py` (Script CLI per la generazione della guida in formato Markdown ad alta leggibilità, HTML renderizzato e documento Word `.docx` opzionale);
  - `tests/test_interviewer_guide.py` (Suite di test per verificare la correttezza della conversione tipografica e dei tag).
- **Dettaglio Implementativo Passo-Passo**:
  1. **Regole tipografiche della guida di somministrazione**:
     - *Testo per il rispondente*: formattazione evidente (grassetto o standard, maiuscoletto per l'avvio);
     - *Istruzioni di regia per l'intervistatore*: corsivo tra parentesi quadre con etichette visive dedicate:
       - `[REGIA: NON LEGGERE LE OPZIONI — ATTENDERE RISPOSTA SPONTANEA]`
       - `[REGIA: LEGGERE LE OPZIONI DI SEGUITO RALLENTANDO SULLE ALTERNATIVE]`
       - `[REGIA: AMMESSA UNA SOLA RISPOSTA]` / `[REGIA: AMMESSE FINO A 3 RISPOSTE]`
       - `[REGIA: RUOTARE L'ORDINE DI LETTURA DEGLI ITEM]`
     - *Istruzioni di filtro e salto*:
       - `[FILTRO: SE RISPOSTA = 1 PASSA A Q04; ALTRIMENTI PROCEDI CON Q02]`
     - *Codici di non risposta per l'operatore*:
       - `97 = Non applicabile (fuori target da filtro)`
       - `98 = Non so / Non risponde (registrare solo se spontaneo, non sollecitare)`
       - `99 = Rifiuto esplicito a rispondere`
  2. **Architettura di Esportazione e Dipendenze**:
     - Generazione nativa in Markdown e HTML leggibile mediante la sola libreria standard di Python;
     - Esportazione in formato Word (`.docx`) gestita con rilevamento dinamico: se `python-docx` è presente nell'ambiente Python, genera il file binario con stili tipografici dedicati (`Interviewer_Regia` in grigio corsivo e `Question_Text` in nero grassetto); in sua assenza, emette un avviso informativo e produce l'output in Markdown/HTML senza bloccare l'esecuzione né fallire il test.
- **Criteri di Accettazione e Verifica**:
  ```powershell
  python scripts/generate_interviewer_guide.py examples/demo_run_biblioteca/final.md --format md --output examples/demo_run_biblioteca/guida_intervistatore.md
  # Verifica test unitari:
  python -m unittest tests/test_interviewer_guide.py
  # Output atteso: OK (tutti i test superati).
  ```

---

### Milestone M6: Standardizzazione Sintassi Regia nei Template, Skill e Linter
- **Track Tematica**: Track 3 — Regia Intervistatore e Formato di Somministrazione
- **Task Correlati in statoprogetto.md**: #27, #07, #15, #17
- **Condizione Operativa**: `Sviluppabile subito internamente` (Autonomia Totale).
- **Obiettivo**:
  Uniformare la sintassi delle istruzioni di regia nei template obbligatori (`questionnaire_template.md` e `final_template.md`), aggiornare specularmente le skill di redazione e consolidamento (`noto-questionnaire-drafting`, `noto-questionnaire-consolidation`) ed estendere il linter `scripts/validate_runs.py` per verificare che ogni item contenga prescrizioni esplicite di regia per l'intervistatore/programmatore.
- **Messaggio di Commit Proposto**:
  ```bash
  git commit -m "refactor(drafting): standardize interviewer regia syntax across templates, skills and validator"
  ```
- **File Toccati / Creati**:
  - `templates/questionnaire_template.md` (Formalizzazione della sezione `Istruzioni per intervistatore / Note di regia`);
  - `templates/final_template.md` (Formalizzazione della voce `Istruzioni per intervistatore / programmazione CATI-CAWI-CAPI`);
  - `.agents/skills/noto-questionnaire-drafting/SKILL.md` e `.claude/skills/noto-questionnaire-drafting/SKILL.md`;
  - `.agents/skills/noto-questionnaire-consolidation/SKILL.md` e `.claude/skills/noto-questionnaire-consolidation/SKILL.md`;
  - `scripts/validate_runs.py` (Estensione controllo formale: verifica che le domande abbiano il campo note di regia valorizzato).
- **Dettaglio Implementativo Passo-Passo**:
  1. Aggiornare i template con indicazioni puntuali sulla valorizzazione dei tag `[REGIA]`;
  2. Aggiornare specularmente le skill in `.agents/` e `.claude/`;
  3. Modificare `validate_runs.py` per segnalare come warning/errore l'assenza di istruzioni per l'intervistatore nei questionari consolidati;
  4. Verificare specularità e validità su `examples/demo_run_biblioteca`.
- **Criteri di Accettazione e Verifica**:
  ```powershell
  python scripts/check_mirror_sync.py
  # Output atteso: Architettura speculare integra al 100%.
  python scripts/validate_runs.py examples/demo_run_biblioteca
  # Output atteso: Tutti i file presenti risultano conformi.
  ```

---

### Milestone M7: Template Normativo e Generatore Automatico Scheda Informativa AGCOM
- **Track Tematica**: Track 4 — Reporting Regolamentare AGCOM (Modulo B Autonomo)
- **Task Correlati in statoprogetto.md**: #33 (Deliverable obbligatorio per legge)
- **Condizione Operativa**: `Sviluppabile subito internamente` (Autonomia Totale — Basato sulla Delibera AGCOM n. 256/10/CSP e report storici noti).
- **Obiettivo**:
  Creare il template ufficiale `templates/agcom_template.md` e lo script di compilazione automatica `scripts/generate_agcom_report.py` per generare la Scheda Informativa AGCOM obbligatoria ai sensi della Delibera AGCOM n. 256/10/CSP per qualsiasi sondaggio destinato alla pubblicazione su media o canali editoriali.
- **Messaggio di Commit Proposto**:
  ```bash
  git commit -m "feat(agcom): add regulatory AGCOM survey disclosure template and automated report generator"
  ```
- **File Toccati / Creati**:
  - `templates/agcom_template.md` (Template conforme alla Delibera AGCOM n. 256/10/CSP);
  - `scripts/generate_agcom_report.py` (Script CLI che estrae metadati da `status.md`, testo integrale da `final.md` e parametri campionari);
  - `tests/test_agcom_report.py` (Suite di test unitari con verifica di conformità AGCOM).
- **Dettaglio Implementativo Passo-Passo**:
  1. **Struttura di `templates/agcom_template.md` (Delibera AGCOM 256/10/CSP)**:
     - *Dati identificativi*: Titolo indagine, Soggetto realizzatore (Noto Sondaggi SRL), Committente, Acquirente;
     - *Data e mezzo*: Data di esecuzione fieldwork, Mezzo di comunicazione di diffusione editoriale;
     - *Campione e popolazione*: Popolazione di riferimento (es. popolazione italiana maggiorenne residente), Estensione geografica, Metodo di campionamento (stratificato per quote o probabilistico), Numerosità campionaria pianificata ed effettiva;
     - *Tassi di contatto e risposta*:
       - Numero contatti tentati totali;
       - Interviste complete valide ($C$);
       - Rifiuti all'intervista (*unit nonresponse* $R$);
       - Mancati contatti / irreperibili ($M$);
       - Interviste parziali / abbandoni (*break-off* $B$);
       - Tasso di Risposta: $RR = \frac{C}{\text{Totale Contatti}}$;
       - Tasso di Rifiuto: $RefR = \frac{R}{\text{Totale Contatti}}$;
     - *Margine d'errore statistico teorico*:
       Formula al livello di confidenza del 95% ($z = 1.96$):
       $$e = \pm z \cdot \sqrt{\frac{p(1-p)}{n}} \cdot \sqrt{\frac{N-n}{N-1}}$$
       Assumendo massima dispersione prudenziale binaria ($p = 0.5$) e popolazione ampia ($N \to \infty$):
       $$e = \pm \frac{1.96 \cdot 0.5}{\sqrt{n}} = \pm \frac{0.98}{\sqrt{n}}$$
       (es. per $n=1000 \to e = \pm 3.10\%$; per $n=800 \to e = \pm 3.46\%$);
     - *Testo integrale delle domande*: Elenco sequenziale e integrale di ciascun quesito e delle relative modalità di risposta;
     - *Link di deposito*: Riferimento all'archivio istituzionale della Presidenza del Consiglio dei Ministri (www.sondaggipoliticoelettorali.it).
  2. **Implementazione di `scripts/generate_agcom_report.py`**:
     - Sintassi CLI: `python scripts/generate_agcom_report.py <cartella_caso> [--output <path_output.md>]`;
     - Estrae i metadati del caso da `status.md` e le domande da `final.md`, calcola automaticamente il margine d'errore teorico sulla numerosità dichiarata e compila la scheda AGCOM.
  3. **Suite di Test**:
     - Test unitario che esegue lo script sulla fixture `examples/demo_run_biblioteca` e controlla la presenza di tutti i 12 campi obbligatori della Delibera 256/10/CSP.
- **Criteri di Accettazione e Verifica**:
  ```powershell
  python scripts/generate_agcom_report.py examples/demo_run_biblioteca --output examples/demo_run_biblioteca/scheda_agcom.md
  python -m unittest tests/test_agcom_report.py
  # Output atteso: OK (tutti i test superati).
  ```

---

### Milestone M8: Attivazione Controllata di `reporting-agent` e Skill Speculare `noto-agcom-reporting`
- **Track Tematica**: Track 4 — Reporting Regolamentare AGCOM (Modulo B Autonomo)
- **Task Correlati in statoprogetto.md**: #33, #02 (differito #28)
- **Condizione Operativa**: `Sviluppabile subito internamente` (Autonomia Totale).
- **Obiettivo**:
  Attivare formalmente nel sistema il ruolo operativo di `reporting-agent` circoscritto alla produzione della Scheda AGCOM, implementando specularmente la nuova skill `noto-agcom-reporting` in `.agents/` e `.claude/`, aggiornando `AGENTS.md`, `CLAUDE.md` e lo script di verifica specularità (mantenendo differite le analisi statistiche complesse e la pesatura IPF di #28 e #30-#32).
- **Messaggio di Commit Proposto**:
  ```bash
  git commit -m "feat(reporting): activate reporting-agent for automated AGCOM disclosure with mirrored skill"
  ```
- **File Toccati / Creati**:
  - `.agents/skills/noto-agcom-reporting/SKILL.md` (Nuova skill per generazione Scheda AGCOM in Google Antigravity);
  - `.claude/skills/noto-agcom-reporting/SKILL.md` (Identica skill speculare per Claude Code);
  - `.agents/agents/reporting-agent.md` e `.claude/agents/reporting-agent.md` (Attivazione del ruolo da *In attesa di attivazione* a *Attivo per Reporting AGCOM*);
  - `templates/` (Inclusione di `templates/agcom_template.md` nella lista dei template standard);
  - `AGENTS.md` e `CLAUDE.md` (Censimento dell'8ª skill e aggiornamento tabella agenti);
  - `scripts/check_mirror_sync.py` (Aggiornamento: verifica delle 8 skill e dei 7 template).
- **Dettaglio Implementativo Passo-Passo**:
  1. Definire `noto-agcom-reporting/SKILL.md` con regole per la produzione di `scheda_agcom.md`;
  2. Aggiornare lo stato di `reporting-agent.md` mantenendo esplicitamente differite le analisi statistiche complesse e la pesatura IPF;
  3. Estendere `scripts/check_mirror_sync.py` affinché verifichi la presenza di `agcom_template.md` tra i template obbligatori e l'allineamento delle 8 skill;
  4. Eseguire la verifica di sincronizzazione.
- **Criteri di Accettazione e Verifica**:
  ```powershell
  python scripts/check_mirror_sync.py
  # Output atteso: Tutte le 8 skill sono perfettamente identiche. Tutti i 7 template sono presenti. Architettura speculare integra al 100%.
  ```

---

## 4. 🛑 GATE DI STOP OBBLIGATORIO — Attesa Riscontro Tecnico da Noto Sondaggi SRL & Referente DPO

> **ATTENZIONE METODOLOGICA E DEONTOLOGICA**:  
> Con il completamento della Milestone **M8**, il team universitario ha portato a compimento **il 100% delle funzionalità sviluppabili in totale autonomia**:
> - Architettura speculare e QA validators operativi;
> - Pipeline di esportazione nativa LimeSurvey (file TSV testato);
> - Ingestione storico e baseline anagrafica Istat/Eurostat ed elettorale;
> - Guida intervistatore con regia tipografica ed esportazione Word `.docx`;
> - Generatore normativo della Scheda AGCOM (Delibera 256/10/CSP).
>
> Procedere oltre questo punto senza un riscontro formale da Noto Sondaggi SRL comporterebbe la formulazione di assunzioni arbitrarie su processi proprietari, violando il principio Human-in-the-Loop e introducendo debito tecnico. **Lo sviluppo del codice SI ARRESTA fino all'esito della sessione di allineamento.**

### 4.1 Fabbisogno Informativo Analitico (I 4 Quesiti Tecnici di `statoprogetto.md` §5.1)

Il ricercatore sottopone a Noto Sondaggi SRL la seguente checklist operativa:

```markdown
### CHECKLIST DI ALLINEAMENTO TECNICO PER NOTO SONDAGGI SRL

1. CANALI DI RILEVAZIONE (Task #12, #24)
   [ ] Indagini gestite esclusivamente via Web CAWI (confermata piattaforma LimeSurvey)
   [ ] Indagini miste CAWI + CATI telefonico con operatore
       - Se CATI: la sala interviste usa LimeSurvey a schermo o un applicativo dedicato (es. dialer Cati)?
   [ ] Altro (CAPI / rilevazioni su campo assistite)

2. CONVENZIONI CLASSI D'ETÀ E STANDARD DEMOGRAFICI (Task #08, #23)
   [ ] Confermata adozione dello standard demografico Istat/Eurostat predisposto dal team:
       (18-24 / 25-34 / 35-44 / 45-54 / 55-64 / 65+ oppure domanda aperta su anno di nascita)
   [ ] Noto Sondaggi adotta partizioni anagrafiche proprietarie fisse (Specificare: ______________________)
   [ ] Eventuali convenzioni specifiche su condizione professionale o titolo di studio

3. FORMATO PER LA SALA INTERVISTE / RILEVATORI (Task #25, #27)
   [ ] Documento Word formattato con note di regia tipografiche (come generato da scripts/generate_interviewer_guide.py)
   [ ] Fruizione e somministrazione diretta a video su piattaforma LimeSurvey
   [ ] Altro formato (es. foglio di calcolo Excel per programmazione)

4. RACCORDO PRIVACY E GOVERNANCE ART. 9 GDPR (Task #14)
   - Nominativo / Canale di contatto del DPO o referente privacy di Noto: __________________________
   - Validazione della formula di informativa breve per interviste telefoniche e CAWI
   - Validazione della tutela delle categorie particolari di dati ex Art. 9 GDPR (orientamenti di voto)
```

### 4.2 Materiali da Presentare e Dimostrazione Live durante l'Incontro (20-25 min)
1. **Minuti 00-10 — Dimostrazione Operativa Live**:
   - Esecuzione del workflow di revisione ed esportazione del questionario con generazione automatica del file per LimeSurvey (`python scripts/export_limesurvey.py`) e della guida per l'intervistatore.
2. **Minuti 10-18 — Risoluzione dei 4 Quesiti Tecnici**:
   - Raccolta delle risposte puntuali alla checklist sopra riportata.
3. **Minuti 18-25 — Acquisizione Questionari Campione e Chiusura**:
   - Richiesta di 1 o 2 questionari storici reali di Noto Sondaggi per collaudare l'estrazione con `noto-survey-extractor`.

### 4.3 Criteri di Sblocco per le Successive Milestones
Lo stop viene rimosso e si passa alla Milestone M9 solo quando:
- È disponibile il verbale sintetico o riscontro scritto relativo ai 4 quesiti tecnici;
- Sono stati acquisiti i testi di 1-2 questionari storici di Noto per il test reale;
- È stato ricevuto il parere o il riscontro dal referente privacy/DPO sul trattamento dei dati politici.

---

## 5. Schede Analitiche delle Milestones Post-Feedback (Track 5: Calibrazione & Validazione Finale)

Le seguenti milestone vengono sbloccate ed eseguite a valle dell'incontro con Noto Sondaggi SRL e del riscontro del DPO.

---

### Milestone M9: Integrazione Standard Socio-Demografici e Batterie Politiche Ufficiali Noto
- **Track Tematica**: Track 5 — Post-Feedback Noto & Calibrazione Finale
- **Task Correlati in statoprogetto.md**: #06, #08, #23
- **Condizione Operativa**: `Serve Noto per revisionare ma si può già procedere allo sviluppo` -> Sbloccato da Feedback Noto.
- **Obiettivo**:
  Integrare nella knowledge base e nei template di redazione le convenzioni demografiche ufficiali concordate con Noto Sondaggi (partizioni anagrafiche, codifiche istruzione/professione) e processare i questionari storici forniti tramite la skill `noto-survey-extractor` per standardizzare le serie storiche dei leader politici.
- **Messaggio di Commit Proposto**:
  ```bash
  git commit -m "feat(noto-standards): integrate official Noto demographics, client taxonomy and calibrated historical batteries"
  ```
- **File Toccati / Creati**:
  - `knowledge/noto_demographics_profile.json` (Profilo anagrafico calibrato sulle specifiche di Noto);
  - `knowledge/noto_historical_batteries.json` (Formulazioni ufficiali Noto per fiducia leader, governo e voto);
  - `templates/brief_template.md` (Integrazione della tassonomia committenze: media, istituzioni, corporate — Task #06);
  - `.agents/skills/noto-brief-structuring/SKILL.md` e `.claude/skills/noto-brief-structuring/SKILL.md`.
- **Dettaglio Implementativo Passo-Passo**:
  1. Eseguire `scripts/extract_survey_knowledge.py` sui questionari storici ricevuti da Noto;
  2. Aggiornare la knowledge base con le scale e le formulazioni ufficiali di Noto Sondaggi;
  3. Allineare i template di brief e questionario per supportare la modalità di profilazione concordata;
  4. Eseguire `scripts/check_mirror_sync.py` per verificare l'integrità speculare.
- **Criteri di Accettazione e Verifica**:
  ```powershell
  python scripts/check_mirror_sync.py
  python -m unittest tests/test_survey_knowledge.py
  # Output atteso: OK (specularità 100%, test passati).
  ```

---

### Milestone M10: Recepimento Prescrizioni DPO/Legale su Art. 9 GDPR e Informativa
- **Track Tematica**: Track 5 — Post-Feedback Noto & Calibrazione Finale
- **Task Correlati in statoprogetto.md**: #13, #14
- **Condizione Operativa**: `Serve Noto per revisionare ma si può già procedere allo sviluppo` -> Sbloccato da Parere DPO.
- **Obiettivo**:
  Aggiornare la checklist preliminare del `compliance-agent` (`templates/compliance_template.md`) e le skill speculari con le indicazioni fornite dal DPO o dal consulente privacy di Noto Sondaggi, inserendo il testo validato dell'informativa di somministrazione (formula breve per interviste CATI, formula estesa con casella di consenso per CAWI).
- **Messaggio di Commit Proposto**:
  ```bash
  git commit -m "refactor(compliance): incorporate DPO legal review feedback into Art 9 GDPR screening checklist and consent notices"
  ```
- **File Toccati / Creati**:
  - `templates/compliance_template.md` (Checklist aggiornata con requisiti puntuali del Registro dei Trattamenti Noto);
  - `.agents/skills/noto-compliance-check/SKILL.md` e `.claude/skills/noto-compliance-check/SKILL.md`;
  - `AGENTS.md` e `CLAUDE.md` (Eventuale allineamento delle clausole di governance e deontologia).
- **Dettaglio Implementativo Passo-Passo**:
  1. Inserire in `templates/compliance_template.md` i controlli concordati con il DPO (base giuridica del consenso esplicito per dati elettorali ex Art. 9 GDPR, tempi di conservazione dei file di contatto, clausole di non identificabilità);
  2. Aggiornare le skill di compliance in entrambi i rami speculari;
  3. Verificare la piena sincronizzazione con `scripts/check_mirror_sync.py`.
- **Criteri di Accettazione e Verifica**:
  ```powershell
  python scripts/check_mirror_sync.py
  # Output atteso: Architettura speculare integra al 100%.
  ```

---

### Milestone M11: Validazione End-to-End su Caso Reale Noto Sondaggi
- **Track Tematica**: Track 5 — Post-Feedback Noto & Calibrazione Finale
- **Task Correlati in statoprogetto.md**: #20, #22, #26, #27, #33
- **Condizione Operativa**: Sbloccato dall'acquisizione di un'indagine reale da Noto Sondaggi.
- **Obiettivo**:
  Eseguire l'intero flusso operativo su un caso studio reale completo fornito da Noto Sondaggi (`runs/caso-reale-noto/`), validando sequenzialmente tutte le fasi (brief, questionario, audit metodologico, compliance screening, questionario consolidato, esportazione TSV per LimeSurvey, guida per l'intervistatore in Word e Scheda Informativa AGCOM).
- **Messaggio di Commit Proposto**:
  ```bash
  git commit -m "test(validation): complete full end-to-end benchmark run on real Noto Sondaggi case study"
  ```
- **File Toccati / Creati**:
  - `runs/caso-reale-noto/source/` (Documento di brief/input reale anonimizzato);
  - `runs/caso-reale-noto/status.md` (Registro decisioni umane con tutte le fasi approvate);
  - `runs/caso-reale-noto/brief.md`;
  - `runs/caso-reale-noto/questionnaire.md`;
  - `runs/caso-reale-noto/methodology.md`;
  - `runs/caso-reale-noto/compliance.md`;
  - `runs/caso-reale-noto/final.md`;
  - `runs/caso-reale-noto/limesurvey_survey.txt` (File TSV validato per LimeSurvey);
  - `runs/caso-reale-noto/guida_intervistatore.docx` (Guida di somministrazione con note di regia);
  - `runs/caso-reale-noto/scheda_agcom.md` (Scheda informativa regolamentare).
- **Dettaglio Implementativo Passo-Passo**:
  1. Inizializzare il caso reale tramite workflow `/nuova-indagine`;
  2. Simulare le risposte del ricercatore umano registrandole in `status.md`;
  3. Generare i deliverable derivati (LimeSurvey, Word, AGCOM);
  4. Eseguire `scripts/validate_runs.py runs/caso-reale-noto` per verificare la rigorosa conformità formale e metodologica.
- **Criteri di Accettazione e Verifica**:
  ```powershell
  python scripts/validate_runs.py runs/caso-reale-noto
  # Output atteso: [PASS] Tutti i file presenti risultano conformi agli standard metodologici.
  ```

---

### Milestone M12: Release v1.0.0, Chiusura Modulo A + AGCOM e Rendicontazione Finale
- **Track Tematica**: Track 5 — Post-Feedback Noto & Calibrazione Finale
- **Task Correlati in statoprogetto.md**: Tutti i 35 task riesaminati
- **Condizione Operativa**: Chiusura formale del Modulo A e della componente AGCOM del Modulo B.
- **Obiettivo**:
  Consolidare la versione definitiva di produzione v1.0.0 della piattaforma, aggiornare formalmente `statoprogetto.md` portando a `FATTO` tutti i task completati, redigere l'Executive Summary di chiusura per la supervisione accademica della Prof.ssa Alessandra Amendola e aggiornare il file `README.md` con la guida completa per ricercatori e sviluppatori.
- **Messaggio di Commit Proposto**:
  ```bash
  git commit -m "docs(release): finalize v1.0.0 milestone with completed Modulo A and AGCOM reporting"
  ```
- **File Toccati / Creati**:
  - `statoprogetto.md` (Aggiornamento tabellare dei task con quadratura statistica finale);
  - `README.md` (Documentazione completa di sistema, manuale di utilizzo dei comandi CLI e dei workflow multi-agente);
  - `piano_operativo.md` (Consolidamento dello stato di completamento di tutte le 13 milestone);
  - Tag di release Git: `v1.0.0-moduloA-agcom`.
- **Dettaglio Implementativo Passo-Passo**:
  1. Aggiornare le quote percentuali in `statoprogetto.md` riflettendo il completamento di tutti i task del Modulo A, dei fieldwork export e della scheda AGCOM;
  2. Verificare l'esecuzione dell'intera suite di QA (specularità, validazione runs, test unitari);
  3. Eseguire il commit e apporre il tag di versione `v1.0.0-moduloA-agcom`.
- **Criteri di Accettazione e Verifica**:
  ```powershell
  python scripts/check_mirror_sync.py
  python scripts/validate_runs.py examples/demo_run_biblioteca runs/caso-reale-noto
  python -m unittest discover tests/
  git tag -a v1.0.0-moduloA-agcom -m "Release v1.0.0: Modulo A consolidato, Esportatore LimeSurvey e Scheda AGCOM"
  # Output atteso: Suite completamente verde, release formalizzata.
  ```

---

## 6. Matrice di Quadratura tra i 35 Task di `statoprogetto.md` e le Milestones

La tabella sottostante dimostra analiticamente la copertura esaustiva di tutti i 35 task del progetto attraverso le milestone operative, evidenziando quali elementi vengono risolti in autonomia (M0-M8), quali richiedono l'allineamento con Noto (M9-M11) e quali rimangono differiti a fasi avanzate del Modulo B come stabilito in `statoprogetto.md`.

| # | Ambito / Task | Stato Iniziale | Milestone Associata | Esito a Fine Roadmap | Note Metodologiche & Tecniche |
| :-: | :--- | :--- | :---: | :---: | :--- |
| **01** | Regole deontologiche e GDPR/AI Act | `FATTO` | **M0** | `FATTO` | Consolidato in `AGENTS.md` e `CLAUDE.md`. |
| **02** | Specularità Antigravity e Claude | `FATTO` | **M0, M2, M3, M6, M8** | `FATTO` | Mantenuta e validata ad ogni milestone con `check_mirror_sync.py`. |
| **03** | Separazione ruoli coordinatore/subagenti | `FATTO` | **M0** | `FATTO` | Il coordinatore non redige mai direttamente i documenti. |
| **04** | Protocollo Human-in-the-Loop in chat | `FATTO` | **M0** | `FATTO` | Tracciamento in `status.md` con stop obbligatorio. |
| **05** | Skill `noto-brief-structuring` | `FATTO` | **M0, M9** | `FATTO` | Rifinito con le tipologie di committenza Noto in M9. |
| **06** | Mappatura committenze abituali Noto | `ABBOZZATO` | **M9** | `FATTO` | Formalizzato post-feedback Noto in `brief_template.md`. |
| **07** | Skill `noto-questionnaire-drafting` | `FATTO` | **M0, M6** | `FATTO` | Aggiornato con la sintassi di regia per intervistatore in M6. |
| **08** | Batterie socio-demografiche e classi età | `ABBOZZATO` | **M4, M9** | `FATTO` | Baseline standard Istat/Eurostat in M4; calibrazione Noto in M9. |
| **09** | Serie storiche elettorali & `extractor` | `ABBOZZATO` | **M3, M4, M9** | `FATTO` | Skill creata in M3, tool CLI in M4, validata con dati reali in M9. |
| **10** | Griglia audit 11 colonne / 12 campi | `FATTO` | **M0** | `FATTO` | Standard metodologico consolidato in `methodology_template.md`. |
| **11** | Calibrazione euristiche commerciali | `ABBOZZATO` | **Gate Stop, M9** | `FATTO` | Discusso nell'incontro e integrato nelle regole di audit. |
| **12** | Specificità CATI vs CAWI | `ABBOZZATO` | **M5, M6, Gate** | `FATTO` | Note di regia per operatore telefonico generate in M5 e M6. |
| **13** | Checklist privacy Art. 9 GDPR | `FATTO` | **M0, M10** | `FATTO` | Struttura attiva; raffinata con prescrizioni DPO in M10. |
| **14** | Interlocuzione DPO / privacy | `IPOTIZZATO` | **Gate Stop, M10** | `FATTO` | Incontro di raccordo e formalizzazione nel template in M10. |
| **15** | Skill `noto-questionnaire-consolidation` | `FATTO` | **M0, M2, M6** | `FATTO` | Integrata con trigger per LimeSurvey e note di regia. |
| **16** | Script `check_mirror_sync.py` | `FATTO` | **M0, M3, M8** | `FATTO` | Esteso per 8 skill e 7 template standard. |
| **17** | Linter `validate_runs.py` | `FATTO` | **M0, M2, M6** | `FATTO` | Esteso per verificare TSV LimeSurvey e note di regia. |
| **18** | CI su GitHub Actions | `POSSIBILE IN FUTURO` | Differito | `DIFFERITO` | Non bloccante per l'operatività; pianificabile post v1.0.0. |
| **19** | Caso demo biblioteca end-to-end | `FATTO` | **M0** | `FATTO` | Verificato ed archiviato in `examples/demo_run_biblioteca/`. |
| **20** | Studio caso reale archivio pubblico | `IPOTIZZATO` | **M11** | `FATTO` | Eseguito direttamente sul caso studio reale Noto Sondaggi in M11. |
| **21** | Benchmark multi-modello (CSV) | `ABBOZZATO` | Differito | `DIFFERITO` | Matrice CSV predisposta; sessioni comparative posticipate. |
| **22** | Integrazione analisi storiche pregresse | `ABBOZZATO` | **M4, M7, M11** | `FATTO` | Utilizzate per tarare le batterie in M4 e la scheda AGCOM in M7. |
| **23** | Batterie anagrafiche e politiche Noto | `IPOTIZZATO` | **M9** | `FATTO` | Integrate a valle del riscontro di Noto. |
| **24** | Verifica piattaforma LimeSurvey e CATI | `ABBOZZATO` | **M1, M2, Gate** | `FATTO` | LimeSurvey integrato in M1/M2; gestione CATI chiarita al Gate. |
| **25** | Formato consegna intervistatori | `NON PRESENTE` | **M5, Gate, M9** | `FATTO` | Generatore Word sviluppato in M5 e confermato da Noto al Gate. |
| **26** | Esportatore LimeSurvey (final.md -> TSV) | `ABBOZZATO` | **M1, M2** | `FATTO` | Priorità tecnica completata in autonomia totale. |
| **27** | Generatore Word (.docx) intervistatore | `IPOTIZZATO` | **M5, M6** | `FATTO` | Script operativo con distinzione grafica note di regia. |
| **28** | Contratti I/O `analysis-agent` | `ABBOZZATO` | Differito | `DIFFERITO` | Architettura predisposta; attivazione con Modulo B completo. |
| **29** | Skill e template analisi descrittiva | `IPOTIZZATO` | Differito | `DIFFERITO` | Differito per dare priorità alla Scheda AGCOM (Task #33). |
| **30** | Routine pesatura complessa IPF/Raking | `POSSIBILE IN FUTURO` | Differito | `DIFFERITO` | Formalmente differita per evitare sovra-ingegnerizzazione. |
| **31** | Trimming ed efficienza campionaria pesi | `POSSIBILE IN FUTURO` | Differito | `DIFFERITO` | Formalmente differita coerentemente con Task #30. |
| **32** | Convenzioni proprietarie pesatura Noto | `POSSIBILE IN FUTURO` | Differito | `DIFFERITO` | Formalmente differita coerentemente con Task #30. |
| **33** | Skill reporting Scheda AGCOM | `IPOTIZZATO` | **M7, M8** | `FATTO` | Sviluppo prioritario completato in autonomia con template e script. |
| **34** | Contratti I/O `dashboard-agent` | `ABBOZZATO` | Differito | `DIFFERITO` | Struttura architetturale predisposta. |
| **35** | Layout brand e veste grafica Noto | `POSSIBILE IN FUTURO` | Differito | `DIFFERITO` | Programmata a completamento della pipeline analitica. |

---

## 7. Guida Operativa per lo Sviluppatore

### 7.1 Flusso di Lavoro Giornaliero per Milestone
Per ogni milestone da sviluppare, lo sviluppatore segue il seguente ciclo standard:

1. **Creazione / Checkout del Branch**:
   ```bash
   # Esempio per Milestone M1
   git checkout -b feat/m1-limesurvey-exporter
   ```
2. **Sviluppo Focalizzato**:
   - Modificare ed implementare **esclusivamente** i file indicati nella scheda analitica della milestone;
   - Non apportare refactoring non correlati o modifiche ad altri moduli.
3. **Esecuzione dei Test e Validatori**:
   ```powershell
   # Esecuzione del test unitario della milestone
   python -m unittest tests/test_<nome_modulo>.py
   # Verifica specularità integrale (SE toccati agenti, skill, template o regole)
   python scripts/check_mirror_sync.py
   # Verifica linter casi
   python scripts/validate_runs.py examples/demo_run_biblioteca
   ```
4. **Commit Atomico**:
   ```bash
   git add <file_modificati>
   git commit -m "<messaggio_convenzionale_indicato_nella_scheda>"
   ```
5. **Merge nel Ramo Principale (`main`)**:
   ```bash
   git checkout main
   git merge --ff-only feat/m1-limesurvey-exporter
   git push origin main
   ```

### 7.2 Regola di Tutela della Specularità
Se viene aggiunta una nuova skill (es. Milestone M3 `noto-survey-extractor` o M8 `noto-agcom-reporting`):
1. Creare la directory in `.agents/skills/<skill-name>/` e inserire `SKILL.md`;
2. Creare la medesima directory in `.claude/skills/<skill-name>/` e copiare identico `SKILL.md`;
3. Se l'agente o il coordinatore devono richiamare la skill, aggiornare sia `.agents/agents/<agente>.md` sia `.claude/agents/<agente>.md`;
4. Aggiornare sia `AGENTS.md` sia `CLAUDE.md` mantenendoli perfettamente sincronizzati;
5. Eseguire sempre `python scripts/check_mirror_sync.py` prima del commit.

---

## 8. Riepilogo per la Direzione Scientifica e Accademica

Il presente piano operativo realizza un perfetto equilibrio tra **capacità realizzativa autonoma** e **rigore metodologico-relazionale**:
- **Massima produttività immediata**: Lo sviluppatore può realizzare e testare in totale indipendenza ben **8 Milestone (M0-M8)** comprendenti l'esportatore nativo LimeSurvey, l'ingestore storico, la guida intervistatore con regia tipografica e la Scheda AGCOM;
- **Zero dispersione**: Il lavoro è organizzato a blocchi compatti evitando salti disordinati tra i moduli;
- **Sicurezza deontologica garantita dal Gate di Stop**: Prima di toccare dati proprietari, classi anagrafiche commerciali o categorie particolari ex Art. 9 GDPR, il sistema si arresta per formalizzare l'allineamento con Noto Sondaggi SRL e il rispettivo DPO;
- **Tracciabilità accademica totale**: Ogni commit su GitHub corrisponde ad un passo certificato, verificabile con test automatici e rendicontabile alla Prof.ssa Alessandra Amendola.
