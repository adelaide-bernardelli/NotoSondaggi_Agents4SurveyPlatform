# Guida Completa alle Funzionalità della Piattaforma Multi-Agente
## Manuale di Riferimento per Metodologia, Agenti, Skill, Workflow, Tooling CLI e Knowledge Base
### Progetto: Survey AI Human-in-the-Loop — Noto Sondaggi SRL & IUSS Pavia

> **Destinatari**: Ricercatori universitari, metodologi di indagine demoscopica, responsabili di campo (CATI/CAWI/CAPI), analisti politici e data scientist di **Noto Sondaggi SRL** e **IUSS Pavia**.  
> **Oggetto**: Guida esaustiva e sistematica a tutti i componenti della piattaforma: principi di governance e tassonomia della non risposta, catalogo dei 7 agenti specializzati, catalogo delle 8 skill operative, guida ai 3 workflow (/nuova-indagine, /revisione-questionario, /audit-singolo), manuale operativo delle 6 CLI in `scripts/`, documentazione dei moduli di knowledge base canonica e scenari d'uso pratici end-to-end.  
> **Versione Manuale**: 1.0 (Allineata all'Architettura Speculare v3.0)  
> **Riferimento Architetturale**: Doppia Specularità Integrale (`.agents/` per Google Antigravity, `.claude/` per Claude Code, `AGENTS.md` e `CLAUDE.md`).

---

## Indice dei Contenuti

1. [Inquadramento, Principi Metodologici e Governance](#1-inquadramento-principi-metodologici-e-governance)
   - 1.1 [Il Paradigma Human-in-the-Loop](#11-il-paradigma-human-in-the-loop)
   - 1.2 [Divieto Assoluto di Rispondenti Sintetici e Dati Fittizi](#12-divieto-assoluto-di-rispondenti-sintetici-e-dati-fittizi)
   - 1.3 [Tassonomia Rigorosa a 6 Codici della Non Risposta](#13-tassonomia-rigorosa-a-6-codici-della-non-risposta)
   - 1.4 [Tutela delle Serie Storiche e Comparabilità Longitudinale](#14-tutela-delle-serie-storiche-e-comparabilità-longitudinale)
   - 1.5 [Doppia Architettura Speculare](#15-doppia-architettura-speculare)
2. [Catalogo dei 7 Agenti della Piattaforma](#2-catalogo-dei-7-agenti-della-piattaforma)
   - 2.1 [`ai-coordinator` (Supervisore e Orchestratore — Main Agent)](#21-ai-coordinator-supervisore-e-orchestratore--main-agent)
   - 2.2 [`questionnaire-agent` (Specialista Questionario, Brief ed Estrazione — Subagent)](#22-questionnaire-agent-specialista-questionario-brief-ed-estrazione--subagent)
   - 2.3 [`methodology-agent` (Revisore Metodologico — Subagent)](#23-methodology-agent-revisore-metodologico--subagent)
   - 2.4 [`compliance-agent` (Revisore Preliminare Privacy & AI Act — Subagent)](#24-compliance-agent-revisore-preliminare-privacy--ai-act--subagent)
   - 2.5 [`reporting-agent` (Specialista Reporting Regolamentare e Scheda AGCOM — Subagent)](#25-reporting-agent-specialista-reporting-regolamentare-e-scheda-agcom--subagent)
   - 2.6 [`analysis-agent` (Analisi Statistica e Post-Rilevazione — Modulo B, In Attesa)](#26-analysis-agent-analisi-statistica-e-post-rilevazione--modulo-b-in-attesa)
   - 2.7 [`dashboard-agent` (Visualizzazione e Layout — Modulo B, In Attesa)](#27-dashboard-agent-visualizzazione-e-layout--modulo-b-in-attesa)
   - 2.8 [Tabella Sinottica Comparativa dei 7 Agenti](#28-tabella-sinottica-comparativa-dei-7-agenti)
3. [Catalogo delle 8 Skill Speculari](#3-catalogo-delle-8-skill-speculari)
   - 3.1 [`noto-survey-pipeline`](#31-noto-survey-pipeline)
   - 3.2 [`noto-brief-structuring`](#32-noto-brief-structuring)
   - 3.3 [`noto-questionnaire-drafting`](#33-noto-questionnaire-drafting)
   - 3.4 [`noto-methodology-audit`](#34-noto-methodology-audit)
   - 3.5 [`noto-compliance-check`](#35-noto-compliance-check)
   - 3.6 [`noto-questionnaire-consolidation`](#36-noto-questionnaire-consolidation)
   - 3.7 [`noto-survey-extractor`](#37-noto-survey-extractor)
   - 3.8 [`noto-agcom-reporting`](#38-noto-agcom-reporting)
   - 3.9 [Mappa di Relazione Agenti-Skill-Template-Artefatti](#39-mappa-di-relazione-agenti-skill-template-artefatti)
4. [Guida ai 3 Workflow Guidati e Comandi Slash](#4-guida-ai-3-workflow-guidati-e-comandi-slash)
   - 4.1 [`/nuova-indagine` (Percorso Completo da Brief a Versione Finale)](#41-nuova-indagine-percorso-completo-da-brief-a-versione-finale)
   - 4.2 [`/revisione-questionario` (Audit e Consolidamento di Questionario Esistente)](#42-revisione-questionario-audit-e-consolidamento-di-questionario-esistente)
   - 4.3 [`/audit-singolo` (Verifica Specialistica Mirata: Metodologia o Compliance)](#43-audit-singolo-verifica-specialistica-mirata-metodologia-o-compliance)
   - 4.4 [Protocollo dei Gate di Stop (STOP Gate) e Scelte Decisionali](#44-protocollo-dei-gate-di-stop-stop-gate-e-scelte-decisionali)
5. [Manuale Operativo delle 6 CLI in `scripts/`](#5-manuale-operativo-delle-6-cli-in-scripts)
   - 5.1 [`scripts/export_limesurvey.py`](#51-scriptsexport_limesurveypy)
   - 5.2 [`scripts/extract_survey_knowledge.py`](#52-scriptsextract_survey_knowledgepy)
   - 5.3 [`scripts/generate_interviewer_guide.py`](#53-scriptsgenerate_interviewer_guidepy)
   - 5.4 [`scripts/generate_agcom_report.py`](#54-scriptsgenerate_agcom_reportpy)
   - 5.5 [`scripts/validate_runs.py`](#55-scriptsvalidate_runspy)
   - 5.6 [`scripts/check_mirror_sync.py`](#56-scriptscheck_mirror_syncpy)
6. [I Moduli della Knowledge Base Canonica](#6-i-moduli-della-knowledge-base-canonica)
   - 6.1 [`knowledge/demographics_standard.json`](#61-knowledgedemographics_standardjson)
   - 6.2 [`knowledge/political_batteries_core.json`](#62-knowledgepolitical_batteries_corejson)
   - 6.3 [Integrazione della Knowledge Base nella Pipeline Redazionale](#63-integrazione-della-knowledge-base-nella-pipeline-redazionale)
7. [Casi d'Uso Pratici End-to-End](#7-casi-duse-pratici-end-to-end)
   - 7.1 [Scenario A: Dalla Richiesta Grezza alla Somministrazione e Diffusione (Caso Biblioteca)](#71-scenario-a-dalla-richiesta-grezza-alla-somministrazione-e-diffusione-caso-biblioteca)
   - 7.2 [Scenario B: Ingestione di Questionari Storici e Salvaguardia di Serie Elettorali](#72-scenario-b-ingestione-di-questionari-storici-e-salvaguardia-di-serie-elettorali)
8. [Mappa Sinottica dei File e Sintassi Rapida](#8-mappa-sinottica-dei-file-e-sintassi-rapida)

---

## 1. Inquadramento, Principi Metodologici e Governance

La piattaforma multi-agente **Noto Sondaggi Survey AI** è un ambiente integrato progettato per assistere i ricercatori di **Noto Sondaggi SRL** e del dipartimento di ricerca di **IUSS Pavia** nella progettazione concettuale, nell'audit metodologico, nella verifica preliminare di conformità normativa e nella preparazione tecnica alla rilevazione di indagini campionarie demoscopiche, istituzionali, elettorali e di mercato.

### 1.1 Il Paradigma Human-in-the-Loop

La piattaforma adotta un'architettura **rigorosamente Human-in-the-Loop (HITL)**. Gli agenti di intelligenza artificiale non agiscono in autonomia decisionale: operano come consulenti specialistici e strumenti di supporto avanzato per il ricercatore umano.

```
       [ Input Ricercatore / Committente ]
                       │
                       ▼
              ┌─────────────────┐
              │ ai-coordinator  │◄──── Inizializza runs/<caso>/status.md
              └────────┬────────┘
                       │ Delega fase
                       ▼
         ┌───────────────────────────┐
         │ Agente Specialista        │──── Genera runs/<caso>/<fase>.md
         └─────────────┬─────────────┘
                       │ Output
                       ▼
              ┌─────────────────┐
              │ ai-coordinator  │──── Verifica conformità template
              └────────┬────────┘
                       │ Presentazione sintesi
                       ▼
          🛑 STOP GATE OBBLIGATORIO 🛑
         ┌───────────────────────────┐
         │     Ricercatore Umano     │──── APPROVATO / CON MODIFICHE / RIFIUTATO
         └─────────────┬─────────────┘
                       │ Decisione registrata in status.md
                       ▼
         [ Avanzamento alla fase successiva ]
```

I vincoli inderogabili di governance includono:
1. **Natura di proposta**: Ogni documento generato (`brief.md`, `questionnaire.md`, `methodology.md`, `compliance.md`, `final.md`, `scheda_agcom.md`) è una proposta tecnica soggetta a convalida formale del ricercatore responsabile.
2. **Nessun avvio automatico del fieldwork**: La piattaforma non è autorizzata a contattare intervistati, non invia email o SMS di invito, non avvia chiamate CATI e non pubblica risultati sui media o sul web.
3. **Divieto di upload non presidiato**: I file di esportazione (es. `limesurvey_survey.txt` o `scheda_agcom.md`) vengono generati in locale e devono essere caricati nelle rispettive piattaforme esclusivamente dall'operatore umano autorizzato.

---

### 1.2 Divieto Assoluto di Rispondenti Sintetici e Dati Fittizi

Un pilastro deontologico essenziale di Noto Sondaggi SRL e della ricerca scientifica IUSS è il **rifiuto totale dei rispondenti sintetici**:

> [!WARNING] **Principio Deontologico Fondamentale**
> **È severamente vietato generare risposte fittizie, simulare campioni di elettori o cittadini tramite Large Language Models (LLM) o sostituire intervistati reali con rispondenti sintetici.**  
> Nessun dato empirico può essere surrogato da stime sintetiche o simulazioni probabilistiche non osservate sul campo.

In fase di pre-campo, tutti i parametri numerici a consuntivo (consistenza campionaria realizzata, tassi di risposta, tassi di rifiuto, contatti effettuati, percentuali di distribuzione delle risposte) **DEVONO** recare la marcatura:
```text
[DA VERIFICARE SUL CAMPO]
```
Qualsiasi tentativo di popolare tali campi con valori arbitrari o presunti costituisce una violazione metodologica rilevata dal linter `scripts/validate_runs.py`.

---

### 1.3 Tassonomia Rigorosa a 6 Codici della Non Risposta

Nelle scienze sociali e nella metodologia demoscopica, la non risposta non è un fenomeno monolitico. Confondere l'assenza di opinione con il rifiuto o con un difetto di filtro distorce gravemente la stima campionaria. La piattaforma impone una **tassonomia standard a 6 codici**:

| Codice / Categoria | Definizione Metodologica | Codifica Piattaforma | Gestione nei Questionari |
| :--- | :--- | :---: | :--- |
| **1. Unit Nonresponse** | Mancata partecipazione dell'unità campionaria all'intera indagine (mancato contatto, irreperibilità, rifiuto iniziale a farsi intervistare). | Consuntivo Fieldwork | Rilevata a consuntivo del campo; documentata nella Scheda AGCOM ($R, M$). |
| **2. Item Nonresponse** | Mancata risposta a uno specifico quesito da parte di un intervistato che sta collaborando all'indagine, dovuta ad ambiguità lessicale, difficoltà o affaticamento. | Audit Metodologico | Oggetto di audit in `methodology.md`; da minimizzare con formulazioni chiare. |
| **3. Rifiuto Esplicito** | Scelta consapevole del rispondente di non dichiarare la propria opinione o dato, tutelata dall'Art. 9 GDPR (es. voto segreto, reddito, salute). | **Codice `99`** | Etichetta obbligatoria: `"Preferisco non rispondere / Rifiuta"`. **Mai accorpare con il Non so.** |
| **4. Autentico "Non so"** | Legittima assenza di conoscenza o di opinione strutturata su un tema, personaggio, norma o servizio (*non-attitudine*). | **Codice `98`** | Etichetta obbligatoria: `"Non so / Non conosce / Senza opinione"`. **Divieto di probing pressante o forzatura.** |
| **5. Non Applicabile** | Rispondente che non deve ricevere la domanda poiché logicamente o strutturalmente fuori dal sotto-target definito dal quesito filtro (*skip logic*). | **Codice `97`** | Etichetta obbligatoria: `"Non applicabile (fuori target / filtro)"`. Assegnato automaticamente dai salti logici. |
| **6. Abbandono (*Break-off*)** | Interruzione anticipata dell'intervista durante la somministrazione (per eccessiva lunghezza, noia o domande invasive). | Consuntivo Fieldwork ($B$) | Monitorato nei test di durata; prevenuto limitando il *respondent burden*. |

> [!IMPORTANT] **La Regola Aurea del "Non so"**
> Non eliminare né nascondere forzatamente le opzioni *"Non so"* o *"Preferisco non rispondere"* per ridurre artificialmente i dati mancanti. Costringere un intervistato a scegliere un'opzione sostantiva quando non possiede un'opinione genera **pseudo-opinioni** (*measurement error*), inquinando la validità scientifica della ricerca.

---

### 1.4 Tutela delle Serie Storiche e Comparabilità Longitudinale

Per un istituto come Noto Sondaggi SRL, la comparabilità longitudinale (*time-series analysis*) dei barometri politici, dei trend di gradimento dei leader e degli indicatori economici è un asset strategico irrinunciabile:
- **Divieto di alterazione silenziosa**: Nessun agente può modificare autonomamente la formulazione testuale, il polo della domanda, l'ampiezza della scala (es. da 4 a 10 punti) o il periodo temporale di riferimento di una domanda storica.
- **Le 3 Opzioni di Audit**: L'agente metodologico non impone riscritture, ma articola sempre 3 alternative documentate:
  - **Opzione A — Conservare l'originale**: Preserva l'assoluta comparabilità con le rilevazioni passate a costo di tollerare piccoli difetti formali noti.
  - **Opzione B — Modifica minima**: Corregge ambiguità evidenti o refusi preservando la metrica e la polarità della scala storica.
  - **Opzione C — Revisione sostanziale**: Riformula integralmente l'item secondo i migliori standard accademici moderni, richiedendo un piano di raccordo empirico (*split ballot*) per non spezzare la serie.
- **Marcatura delle fonti esterne**: Dati contingenti, importi, leggi o atti amministrativi citati nelle premesse vanno sempre marcati con `[DA VERIFICARE]`.

---

### 1.5 Doppia Architettura Speculare

La piattaforma garantisce parità operativa assoluta tra due ambienti di esecuzione:
- **Google Antigravity**: Basato su `.agents/agents/`, `.agents/skills/`, `.agents/workflows/` e regolato da `AGENTS.md`.
- **Claude Code**: Basato su `.claude/agents/`, `.claude/skills/`, `.claude/commands/` e regolato da `CLAUDE.md`.

Ogni aggiornamento ai file di sistema viene validato dallo script `scripts/check_mirror_sync.py`, assicurando che nessun agente o procedura differisca tra le due piattaforme.

---

## 2. Catalogo dei 7 Agenti della Piattaforma

La piattaforma articola la cooperazione multi-agente separando rigorosamente le responsabilità di coordinamento da quelle specialistiche:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        ai-coordinator (Orchestratore)                  │
└───────┬─────────────────┬────────────────────┬──────────────────┬──────┘
        │                 │                    │                  │
        ▼                 ▼                    ▼                  ▼
┌───────────────┐ ┌───────────────┐  ┌───────────────────┐ ┌───────────────┐
│ questionnaire │ │  methodology  │  │ compliance-agent  │ │reporting-agent│
│    -agent     │ │    -agent     │  │ (Privacy & AI Act)│ │(Scheda AGCOM) │
└───────────────┘ └───────────────┘  └───────────────────┘ └───────────────┘
  [Brief, Bozza,   [Audit item-by-    [Screening Art. 9,    [Delibera AGCOM
   Final, Export]   item, 3 Opzioni]   DPIA, Blocchi DPO]    256/10/CSP]

        ────────────────────────────────────────────────────────
        MODULO B (In attesa di attivazione post-rilevazione):
        ┌─────────────────────────┐    ┌─────────────────────────┐
        │     analysis-agent      │    │     dashboard-agent     │
        │(Analisi Dati Empirici)  │    │ (Visualizzazione Grafica)│
        └─────────────────────────┘    └─────────────────────────┘
```

---

### 2.1 `ai-coordinator` (Supervisore e Orchestratore — Main Agent)

- **Ruolo**: Main Agent supervisore e custode dello stato dell'indagine. Governa il flusso operativo, delega le fasi agli specialisti, esegue controlli qualità preventivi e gestisce il dialogo con il ricercatore.
- **Responsabilità**:
  - Inizializzazione della cartella `runs/<caso>/` e salvaguardia del file originale in `runs/<caso>/source/`;
  - Redazione e costante aggiornamento del registro di avanzamento `runs/<caso>/status.md`;
  - Controllo di conformità degli artefatti prodotti dagli specialisti rispetto ai template ufficiali in `templates/`;
  - Interruzione del processo a ogni gate di fase (**STOP Gate**) per richiedere la decisione esplicita del ricercatore umano in chat.
- **Compiti Ammessi**:
  - Inizializzare la struttura di directory del caso (`runs/<caso>/` e `runs/<caso>/source/`);
  - Aggiornare lo stato delle 5 fasi del Modulo A in `runs/<caso>/status.md`;
  - Delegare ciascuna fase analitica o di redazione a un singolo subagent specialista per volta;
  - Presentare al ricercatore umano in chat la sintesi degli output e le opzioni decisionali;
  - Registrare puntualmente nel registro delle decisioni umane in `status.md` le indicazioni ricevute in chat.
- **Compiti Vietati**:
  - **NON redige mai direttamente** gli artefatti tecnici specialistici (`brief.md`, `questionnaire.md`, `methodology.md`, `compliance.md`, `final.md`, `extracted_survey.md`, `scheda_agcom.md`);
  - **NON avanza alla fase successiva** senza formale approvazione umana registrata in chat;
  - **NON approva autonomamente** le opzioni di modifica metodologica o di compliance.
- **Contratto di Input/Output**:
  - *Input*: Comando slash utente (`/nuova-indagine`, `/revisione-questionario`, `/audit-singolo`), file sorgente, decisioni umane espresse in chat.
  - *Output*: Cartella `runs/<caso>/`, file `runs/<caso>/status.md`, messaggi di sintesi e domande di decisione al ricercatore in chat.
- **Checklist Operativa**:
  - [ ] Ho delegato la fase allo specialista senza redigere direttamente l'artefatto?
  - [ ] Ho verificato che l'artefatto rispetti tutte le sezioni del relativo template?
  - [ ] Mi sono fermato dopo la singola fase presentando chiaramente le scelte aperte all'utente?
  - [ ] Ho annotato nel registro decisioni di `status.md` l'esito formale e le risposte fornite in chat?

---

### 2.2 `questionnaire-agent` (Specialista Questionario, Brief ed Estrazione — Subagent)

- **Ruolo**: Subagent specialista nella progettazione concettuale, redazione testuale del questionario, estrazione da archivi storici e consolidamento tecnico.
- **Responsabilità**:
  - Fase `brief`: Analizza documenti grezzi ed estrae obiettivi conoscitivi e costrutti senza inventare dati mancanti;
  - Fase `questionnaire`: Redige la bozza completa con sezioni logiche, tipi di quesito, filtri e codici standard di non risposta;
  - Fase `final`: Consolida la versione definitiva recependo **esclusivamente** le modifiche approvate dal ricercatore in `status.md`;
  - Estrazione storica: Estrae e normalizza formulari storici tramite `noto-survey-extractor`;
  - Fieldwork Bridge: Richiama `scripts/export_limesurvey.py` per generare `runs/<caso>/limesurvey_survey.txt`.
- **Compiti Ammessi**:
  - Strutturare il brief di ricerca (`brief.md`) evidenziando lacune informative e quesiti per il ricercatore;
  - Redigere la bozza strutturata del questionario (`questionnaire.md`) con codici standard `97`, `98`, `99` e note di regia;
  - Consolidare il questionario finale (`final.md`) integrando solo ed esclusivamente le scelte approvate in chat dal ricercatore;
  - Eseguire l'esportazione automatica nel formato nativo LimeSurvey TSV a 14 colonne standard;
  - Normalizzare formulari e batterie storiche secondo `templates/extracted_survey_template.md`.
- **Compiti Vietati**:
  - **NON approva le proprie bozze**;
  - **NON inventa parametri campionari o metodologici** non presenti nella documentazione d'origine (usare `DA DEFINIRE`);
  - **NON accetta o scarta modifiche metodologiche di propria iniziativa** durante il consolidamento finale;
  - **NON valuta la conformità legale o privacy**.
- **Contratto di Input/Output**:
  - *Input*: Documento in `source/` per il brief; brief approvato per la bozza; questionario, audit metodologico, screening compliance e decisioni in `status.md` per il consolidamento.
  - *Output*: `runs/<caso>/brief.md`, `runs/<caso>/questionnaire.md`, `runs/<caso>/final.md`, `runs/<caso>/limesurvey_survey.txt`, `runs/<caso>/extracted_survey.md`.
- **Checklist Operativa**:
  - [ ] Ho impostato come `DA DEFINIRE` qualsiasi parametro non esplicitato nella fonte?
  - [ ] Tutti i fatti esterni contingenti sono marcati `[DA VERIFICARE]`?
  - [ ] Ogni quesito include istruzioni di regia tipografiche e codici distinti per `97`, `98` e `99`?
  - [ ] In `final.md` sono state integrate solo le opzioni approvate dal ricercatore in `status.md`?

---

### 2.3 `methodology-agent` (Revisore Metodologico — Subagent)

- **Ruolo**: Subagent revisore metodologico indipendente. Esegue l'audit analitico item-per-item e dell'intero flusso del questionario.
- **Responsabilità**:
  - Individuazione di distorsioni cognitive: domande orientanti (*leading*), doppie domande (*double-barreled*), asimmetrie nelle scale, premesse non verificate;
  - Compilazione della **Griglia a 11 colonne standard** e delle **Schede analitiche a 12 campi** con le 3 alternative (*Opzione A: Conservare*, *Opzione B: Modifica minima*, *Opzione C: Revisione sostanziale*);
  - Diagnostica specifica della non risposta (distinzione tra Rifiuto, Autentico Non so, Non applicabile, Item nonresponse, Break-off);
  - Formulazione degli effetti attesi sempre come **ipotesi da testare empiricamente** (pretest, cognitive interview, split ballot).
- **Compiti Ammessi**:
  - Esaminare ogni singolo item rilevando bias cognitivi, formulazioni ambigue o problemi di filtro;
  - Compilare la griglia a 11 colonne e le schede analitiche a 12 campi secondo `templates/methodology_template.md`;
  - Formulare le tre opzioni operative per ciascun item problematico (Conservare / Modifica minima / Revisione sostanziale);
  - Proporre una bozza di questionario riformulato e il piano di pretest/validazione empirica;
  - Segnalare rischi trasversali di affaticamento o abbandono (*break-off*).
- **Compiti Vietati**:
  - **NON dichiara certezze causali non provate** (es. vietato scrivere *"questa modifica riduce la non risposta del 5%"*);
  - **NON elimina o nasconde le opzioni di uscita** (*Non so* o *Rifiuta*);
  - **NON approva le modifiche proposte** (la colonna `Decisione umana` deve rimanere `DA CONFERMARE`);
  - **NON modifica direttamente i questionari originali**.
- **Contratto di Input/Output**:
  - *Input*: Questionario (`questionnaire.md` o file sorgente in `source/`), eventuale brief approvato e note in `status.md`.
  - *Output*: `runs/<caso>/methodology.md` (conforme a `templates/methodology_template.md`).
- **Checklist Operativa**:
  - [ ] La griglia riepilogativa contiene esattamente le 11 colonne prescritte?
  - [ ] Ogni singola scheda include tutti i 12 campi e articola chiaramente le Opzioni A, B e C?
  - [ ] È stata evitata qualsiasi promessa assertiva di miglioramento empirico dei dati?
  - [ ] Tutte le serie storiche sono state identificate e tutelate?

---

### 2.4 `compliance-agent` (Revisore Preliminare Privacy & AI Act — Subagent)

- **Ruolo**: Subagent specialista nella verifica preliminare di protezione dati (GDPR) e governance dell'intelligenza artificiale (AI Act).
- **Responsabilità**:
  - Censimento del perimetro dei dati trattati (testi neutri, dati aggregati, microdati, dati personali comuni);
  - Rilevazione mirata delle categorie particolari di dati ex **Art. 9 GDPR** (opinioni politiche, intenzioni di voto, appartenenza sindacale, orientamento religioso);
  - Valutazione del rischio di re-identificazione indiretta (*singling out*) derivante dall'incrocio di variabili anagrafiche e geografiche granulari;
  - Verifica della presenza obbligatoria dell'opzione *"Preferisco non rispondere"* con codice `99`;
  - Screening preliminare AI Act (scopo previsto, assenza di pratiche manipolatorie, trasparenza, sorveglianza umana);
  - Identificazione dei punti bloccanti da sottoporre formalmente al DPO o al consulente legale umano.
- **Compiti Ammessi**:
  - Effettuare la checklist preliminare di screening privacy domanda-per-domanda secondo `templates/compliance_template.md`;
  - Rilevare il trattamento di opinioni politiche e categorie particolari ex Art. 9 GDPR prescrivendo la tutela del codice `99`;
  - Esaminare il rischio di re-identificazione derivante dall'incrocio di variabili demografiche e territoriali;
  - Segnalare raccomandazioni e requisiti bloccanti per l'informativa di somministrazione;
  - Rimandare formalmente al DPO o consulente legale umano la validazione giuridica definitiva.
- **Compiti Vietati**:
  - **NON rilascia pareri legali formali né certificazioni di conformità** (es. vietato scrivere *"questo questionario è certificato conforme al GDPR"*);
  - **NON autorizza autonomamente il trattamento di dati particolari ex Art. 9 GDPR**;
  - **NON accede a elenchi anagrafici reali o dati personali di contatto**.
- **Contratto di Input/Output**:
  - *Input*: Questionario in esame, eventuale brief, audit metodologico e note in `status.md`.
  - *Output*: `runs/<caso>/compliance.md` (conforme a `templates/compliance_template.md`).
- **Checklist Operativa**:
  - [ ] Ho chiarito in premessa la natura di screening preliminare non vincolante legalmente?
  - [ ] Ho censito ogni quesito relativo a opinioni politiche o dati sensibili verificando l'opzione `99`?
  - [ ] Ho valutato il rischio di incrocio anagrafico raccomandando classi aggregate per età e comuni?
  - [ ] Ho lasciato lo stato `Approvazione dell'esperto umano: IN ATTESA` per i punti bloccanti?

---

### 2.5 `reporting-agent` (Specialista Reporting Regolamentare e Scheda AGCOM — Subagent)

- **Ruolo**: Subagent specialista nella rendicontazione regolamentare istituzionale e nella reportistica descrittiva trasparente.
- **Responsabilità**:
  - Redazione e validazione formale della **Scheda Informativa del Sondaggio** ai sensi dell'art. 5 della **Delibera AGCOM n. 256/10/CSP** e del relativo deposito sul portale governativo `www.sondaggipoliticoelettorali.it`;
  - Calcolo matematico rigoroso del **margine d'errore statistico teorico** al 95% di livello di confidenza ($z = 1.96$) con formula proporzionale bernoulliana e correzione per popolazione finita ove applicabile;
  - Trascrizione fedele e integrale di tutti i quesiti somministrati con opzioni complete e codici `97`, `98`, `99`;
  - Applicazione rigorosa della marcatura `[DA VERIFICARE SUL CAMPO]` a tutti i dati di contatto e consuntivi non ancora disponibili.
- **Compiti Ammessi**:
  - Compilare la Scheda Informativa AGCOM a 7 sezioni e 12 campi obbligatori secondo `templates/agcom_template.md`;
  - Calcolare il margine d'errore campionario teorico al 95% di confidenza a partire dalla numerosità $n$;
  - Trascrivere integralmente i testi di tutti i quesiti e le opzioni con codici standard `97/98/99`;
  - Marcare sistematicamente come `[DA VERIFICARE SUL CAMPO]` tutti i consuntivi di campo non ancora raccolti;
  - Eseguire controlli di conformità formale sulla scheda tramite `scripts/generate_agcom_report.py --check-only`.
- **Compiti Vietati**:
  - **NON genera rispondenti sintetici né dati simulati**;
  - **NON inventa consuntivi di contatto, tassi di risposta o percentuali di esito**;
  - **NON diffonde o pubblica schede senza la previa approvazione del ricercatore responsabile di Noto Sondaggi SRL**.
- **Contratto di Input/Output**:
  - *Input*: Questionario consolidato (`final.md` o `questionnaire.md`), metadati del caso in `status.md`, brief di ricerca (`brief.md`).
  - *Output*: `runs/<caso>/scheda_agcom.md` (conforme a `templates/agcom_template.md`).
- **Checklist Operativa**:
  - [ ] Il soggetto realizzatore è indicato esattamente come `"Noto Sondaggi SRL"`?
  - [ ] Sono presenti tutte le 7 sezioni e i 12 campi obbligatori previsti dalla Delibera AGCOM 256/10/CSP?
  - [ ] Tutti i consuntivi numerici di campo recano `[DA VERIFICARE SUL CAMPO]`?
  - [ ] Il margine d'errore statistico teorico al 95% è stato calcolato matematicamente sulla numerosità dichiarata?

---

### 2.6 `analysis-agent` (Analisi Statistica e Post-Rilevazione — Modulo B, In Attesa)

- **Ruolo**: Subagent specialistico per le elaborazioni statistiche descrittive e inferenziali post-rilevazione.
- **Stato Operativo**: **IN ATTESA DI ATTIVAZIONE (MODULO B)**. Non attivo durante la fase di progettazione e revisione dei questionari (Modulo A). Se invocato prima dell'attivazione formale e della consegna di dati empirici autorizzati e anonimizzati, segnala lo stato di attesa e restituisce il controllo ad `ai-coordinator`.
- **Responsabilità Previste all'Attivazione**:
  - Ricezione di dati empirici anonimizzati a consuntivo del campo;
  - Diagnostica statistica della non risposta (*unit nonresponse* vs *item nonresponse*);
  - Controllo qualità delle matrici dati e ponderazione campionaria (IPF / rim weighting) su piano approvato;
  - Elaborazione di tavole descrittive di frequenza e incroci con basi campionarie e intervalli di confidenza.
- **Compiti Ammessi (quando attivato)**:
  - Verificare l'integrità e la qualità dei microdati empirici raccolti sul campo da Noto Sondaggi;
  - Eseguire controlli di coerenza logica interna, tempi di compilazione (*speeders*) e pattern anomali (*straightlining*);
  - Elaborare distribuzioni di frequenza, tabelle di contingenza e indici di sintesi con basi campionarie trasparenti;
  - Condurre la diagnostica avanzata della non risposta distinguendo *unit nonresponse* e *item nonresponse* (con codici `97`, `98`, `99`);
  - Applicare routine di pesatura campionaria complessa (IPF / rim weighting) esclusivamente se previste dal piano approvato.
- **Compiti Vietati e Vincoli Deontologici**:
  - **NON accede a microdati senza autorizzazione esplicita del ricercatore responsabile e del DPO**;
  - **NON opera su dati contenenti identificativi diretti** (nominativi, numeri di telefono, email, IP);
  - **NON sostituisce mai osservazioni mancanti o unit nonresponse con rispondenti sintetici generati da LLM**;
  - **NON elabora tavole ponderate in assenza di metadati ufficiali di disegno e popolazione**;
  - **NON effettua previsioni elettorali non autorizzate, profilazione politica individuale o targeting persuasivo**.
- **Contratto di Input/Output Previsto (Modulo B)**:
  - *Input richiesti all'attivazione*: Questionario definitivo approvato (`runs/<caso>/final.md`), dizionario delle variabili (*codebook*), dataset empirico anonimizzato, metadati del disegno campionario (quote, pesi di post-stratificazione) e piano statistico validato dal ricercatore umano.
  - *Output previsti all'attivazione*: Script riproducibili di controllo qualità e analisi descrittiva in `runs/<caso>/`, tavole statistiche validate (ponderate e non ponderate, con basi campionarie ed errori standard), report diagnostico sulla non risposta.
- **Checklist Operativa / di Autoverifica**:
  - [ ] Il Modulo B è stato formalmente attivato dal ricercatore umano con dati anonimizzati e piano statistico approvato? (In caso negativo, fermarsi immediatamente).
  - [ ] Ho distinto chiaramente *unit nonresponse*, *item nonresponse*, *Autentico Non so*, *Rifiuto* e *Non applicabile*?
  - [ ] Ogni tavola prodotta riporta base campionaria (ponderata e non ponderata), formulazione esatta dell'item, pesi utilizzati e avvertenze statistiche?
  - [ ] Ho evitato qualsiasi inferenza causale impropria o generazione di dati sintetici?

---

### 2.7 `dashboard-agent` (Visualizzazione e Layout — Modulo B, In Attesa)

- **Ruolo**: Subagent specialista nella progettazione di layout visivi, report grafici e dashboard divulgative.
- **Stato Operativo**: **IN ATTESA DI ATTIVAZIONE (MODULO B)**. Non attivo durante il Modulo A. Se invocato prima dell'attivazione formale e dell'approvazione di tavole e report, segnala lo stato di attesa e restituisce il controllo ad `ai-coordinator`.
- **Responsabilità Previste all'Attivazione**:
  - Progettazione di grafici e schede di sintesi basate esclusivamente su tavole validate da `analysis-agent`;
  - Inserimento obbligatorio in ogni grafico dei metadati di trasparenza (denominatore $N$, formulazione domanda, popolazione, periodo, quote di non risposta con codici `98` e `99`);
  - Operatività esclusivamente locale, senza esportazione o pubblicazione automatica su piattaforme cloud esterne.
- **Compiti Ammessi (quando attivato)**:
  - Progettare specifiche grafiche, infografiche e layout di sintesi partendo esclusivamente da dati e tavole validate da `analysis-agent`;
  - Rendere esplicita e visibile la trasparenza metodologica di ogni visualizzazione (indicazione del denominatore $N$, formulazione della domanda, popolazione, periodo, pesatura);
  - Rappresentare in modo chiaro e distinto le quote di *"Non so"* (`98`) e *"Preferisco non rispondere"* (`99`), evitando di occultarle;
  - Operare rigorosamente in locale per la produzione di mockup visivi o codice dichiarativo.
- **Compiti Vietati e Vincoli Deontologici**:
  - **NON modifica o arrotonda arbitrariamente i numeri approvati**;
  - **NON tronca gli assi dei grafici in modo distorsivo o ingannevole**;
  - **NON inventa serie storiche o trend passati non documentati**;
  - **NON esporta né pubblica dati o grafici verso provider cloud, servizi SaaS o piattaforme esterne senza autorizzazione scritta**;
  - **NON diffonde report prima della revisione e validazione formale del ricercatore umano tramite `ai-coordinator`**.
- **Contratto di Input/Output Previsto (Modulo B)**:
  - *Input richiesti all'attivazione*: Tavole statistiche validate e report descrittivo approvato in `runs/<caso>/`, metadati obbligatori dell'indagine (committente, esecutore, periodo di rilevazione, popolazione, metodo di raccolta, numerosità campionaria $N$, criterio di pesatura).
  - *Output previsti all'attivazione*: Specifiche o artefatti di visualizzazione in `runs/<caso>/`, in cui ogni singolo grafico riporta obbligatoriamente titolo neutrale, ID domanda, denominatore esatto, quote di non risposta (`98`/`99`), fonte e avvertenze metodologiche.
- **Checklist Operativa / di Autoverifica**:
  - [ ] Il Modulo B è stato formalmente attivato e dispongo di tavole e report approvati dal ricercatore? (In caso negativo, fermarsi immediatamente).
  - [ ] Ogni grafico/visualizzazione include titolo neutrale, denominatore (`N`), popolazione, periodo, fonte, pesatura e quota di non risposta (*Non so / Rifiuto*)?
  - [ ] Ho operato esclusivamente sui file del workspace senza inviare dati a servizi esterni?
  - [ ] L'output è contrassegnato come bozza interna soggetta ad approvazione umana prima di qualsiasi diffusione?

---

### 2.8 Tabella Sinottica Comparativa dei 7 Agenti

| Agente | Tipo | Modulo | Skill Primaria | Template di Riferimento | Artefatto Prodotto |
| :--- | :---: | :---: | :--- | :--- | :--- |
| **`ai-coordinator`** | Main | A | `noto-survey-pipeline` | `templates/status_template.md` | `runs/<caso>/status.md` |
| **`questionnaire-agent`** | Sub | A | `noto-brief-structuring`<br>`noto-questionnaire-drafting`<br>`noto-questionnaire-consolidation`<br>`noto-survey-extractor` | `templates/brief_template.md`<br>`templates/questionnaire_template.md`<br>`templates/final_template.md`<br>`templates/extracted_survey_template.md` | `runs/<caso>/brief.md`<br>`runs/<caso>/questionnaire.md`<br>`runs/<caso>/final.md`<br>`runs/<caso>/limesurvey_survey.txt`<br>`runs/<caso>/extracted_survey.md` |
| **`methodology-agent`** | Sub | A | `noto-methodology-audit` | `templates/methodology_template.md` | `runs/<caso>/methodology.md` |
| **`compliance-agent`** | Sub | A | `noto-compliance-check` | `templates/compliance_template.md` | `runs/<caso>/compliance.md` |
| **`reporting-agent`** | Sub | A | `noto-agcom-reporting` | `templates/agcom_template.md` | `runs/<caso>/scheda_agcom.md` |
| **`analysis-agent`** | Sub | B | *In attesa di attivazione* | *In attesa di attivazione* | Tavole statistiche e script di validazione dati |
| **`dashboard-agent`** | Sub | B | *In attesa di attivazione* | *In attesa di attivazione* | Specifiche layout e report grafici |

---

## 3. Catalogo delle 8 Skill Speculari

Le skill rappresentano le procedure operative incapsulate richiamabili dagli agenti o direttamente dall'utente umano tramite comandi slash. Ognuna è presente sia in `.agents/skills/<nome>/SKILL.md` sia in `.claude/skills/<nome>/SKILL.md`.

### 3.1 `noto-survey-pipeline`
- **Finalità**: Coordina l'intero ciclo di vita del caso di indagine. Gestisce la creazione delle cartelle in `runs/<caso>/`, la copia del file originale in `runs/<caso>/source/`, la transizione tra le fasi e il registro decisionale in `runs/<caso>/status.md`.
- **Esecutore Primario**: `ai-coordinator`.
- **Input**: Identificativo del caso (`<caso>`), percorso del file sorgente, comando di avvio del workflow.
- **Output**: Cartelle `runs/<caso>/`, `runs/<caso>/source/` e file `runs/<caso>/status.md`.
- **Template Associato**: `templates/status_template.md` (oltre alla supervisione dei contratti di tutti gli altri template).
- **Regole Chiave**: Esecuzione strettamente sequenziale; verifica della conformità di ogni artefatto prima della presentazione all'utente; stop obbligatorio ad ogni gate.

---

### 3.2 `noto-brief-structuring`
- **Finalità**: Trasforma appunti informali, brief di committenti o trascrizioni di riunioni in un documento di brief metodologico strutturato.
- **Esecutore Primario**: `questionnaire-agent`.
- **Input**: File grezzo in `runs/<caso>/source/<file>`.
- **Output**: `runs/<caso>/brief.md` (conforme a `templates/brief_template.md`).
- **Template Associato**: `templates/brief_template.md`.
- **Regole Chiave**: Divieto assoluto di inventare dati campionari (usare `DA DEFINIRE`); censimento dei costrutti; marcatura dei dati contingenti come `[DA VERIFICARE]`; formulazione puntuale delle domande aperte per il ricercatore.

---

### 3.3 `noto-questionnaire-drafting`
- **Finalità**: Redige la bozza iniziale strutturata del questionario a partire dal brief approvato.
- **Esecutore Primario**: `questionnaire-agent`.
- **Input**: `runs/<caso>/brief.md` approvato e relative note in `runs/<caso>/status.md`.
- **Output**: `runs/<caso>/questionnaire.md` (conforme a `templates/questionnaire_template.md`).
- **Template Associato**: `templates/questionnaire_template.md`.
- **Regole Chiave**: Ogni domanda deve essere ancorata a un obiettivo del brief; formulazioni neutrali privi di aggettivi orientanti (*leading*); codici distinti per `97` (Non applicabile), `98` (Non so) e `99` (Rifiuta); note di regia tipografiche standardizzate (`[NON LEGGERE / SPONTANEA / ROTAZIONE / PROBING]`); marcatura `BOZZA NON AUTORIZZATA PER CAMPO`.

---

### 3.4 `noto-methodology-audit`
- **Finalità**: Esegue l'audit metodologico dettagliato domanda per domanda e dell'intero flusso del questionario.
- **Esecutore Primario**: `methodology-agent`.
- **Input**: Questionario (`runs/<caso>/questionnaire.md` o file sorgente in `runs/<caso>/source/`), eventuale brief.
- **Output**: `runs/<caso>/methodology.md` (conforme a `templates/methodology_template.md`).
- **Template Associato**: `templates/methodology_template.md`.
- **Regole Chiave**: Griglia riepilogativa a 11 colonne obbligatorie; schede analitiche a 12 campi per ciascun item; articolazione delle 3 alternative (**Opzione A: Conservare**, **Opzione B: Modifica minima**, **Opzione C: Revisione sostanziale**); categorizzazione rigorosa della non risposta; divieto di previsioni certe (effetti attesi formulati come *ipotesi da testare*); colonna decisionale impostata su `DA CONFERMARE`.

---

### 3.5 `noto-compliance-check`
- **Finalità**: Esegue lo screening preliminare strutturato di conformità privacy (GDPR) e governance dell'intelligenza artificiale (AI Act).
- **Esecutore Primario**: `compliance-agent`.
- **Input**: Questionario in esame, eventuale brief e audit metodologico.
- **Output**: `runs/<caso>/compliance.md` (conforme a `templates/compliance_template.md`).
- **Template Associato**: `templates/compliance_template.md`.
- **Regole Chiave**: Censimento di dati ex Art. 9 GDPR (opinioni politiche, convinzioni, voto); valutazione del rischio di identificazione indiretta (*singling out*); verifica obbligatorietà opzione *"Preferisco non rispondere"* (`99`); checklist AI Act (assenza pratiche manipolative, *human oversight*); evidenziazione blocchi per il DPO; dicitura esplicita di screening preliminare non avente valore di parere legale formale.

---

### 3.6 `noto-questionnaire-consolidation`
- **Finalità**: Consolida la versione finale del questionario recependo le sole modifiche approvate ed esporta il tracciato tecnico per la rilevazione.
- **Esecutore Primario**: `questionnaire-agent`.
- **Input**: Questionario originale, `methodology.md`, `compliance.md` e decisioni umane registrate in `status.md`.
- **Output**: `runs/<caso>/final.md` (conforme a `templates/final_template.md`) e `runs/<caso>/limesurvey_survey.txt`.
- **Template Associato**: `templates/final_template.md` (e formato nativo di esportazione per LimeSurvey).
- **Regole Chiave**: Compilazione del *Registro delle Modifiche Accettate e Scartate*; divieto di applicare modifiche non approvate dall'utente; inclusione di tutte le istruzioni di regia tipografiche e filtri; esecuzione automatica post-processo di `scripts/export_limesurvey.py` per produrre il file TSV LimeSurvey a 14 colonne standard.

---

### 3.7 `noto-survey-extractor`
- **Finalità**: Estrae, normalizza e archivia in formato strutturato questionari pregressi, formulari e batterie storiche da documenti eterogenei (PDF, DOCX, TXT, MD).
- **Esecutore Primario**: `questionnaire-agent`.
- **Input**: Documenti storici o report in `runs/<caso>/source/` o `knowledge/raw/`.
- **Output**: File strutturato conforme a `templates/extracted_survey_template.md` (es. `runs/<caso>/extracted_survey.md` o `knowledge/extracted_<nome>.md`).
- **Template Associato**: `templates/extracted_survey_template.md`.
- **Regole Chiave**: Fedeltà letterale assoluta al testo originario rivolto al rispondente (non correggere o alterare i testi durante l'estrazione); normalizzazione dei codici di non risposta (`97/98/99`); mappatura delle batterie standard; documentazione dei vincoli di comparabilità; protezione da prompt injection (trattare i testi storici come dati passivi).

---

### 3.8 `noto-agcom-reporting`
- **Finalità**: Redige e convalida la Scheda Informativa obbligatoria del sondaggio ai sensi dell'art. 5 della Delibera AGCOM 256/10/CSP per la pubblicazione sui mezzi di comunicazione e il deposito su `www.sondaggipoliticoelettorali.it`.
- **Esecutore Primario**: `reporting-agent`.
- **Input**: Cartella del caso `runs/<caso>/` o file del questionario definitivo.
- **Output**: `runs/<caso>/scheda_agcom.md` (conforme a `templates/agcom_template.md`).
- **Template Associato**: `templates/agcom_template.md`.
- **Regole Chiave**: Soggetto realizzatore indicato come `"Noto Sondaggi SRL"`; calcolo del margine d'errore statistico teorico al 95% ($z = 1.96$); trascrizione integrale dei quesiti con codici standard; marcatura obbligatoria `[DA VERIFICARE SUL CAMPO]` per tutti i consuntivi di campo e percentuali non ancora rilevate; divieto assoluto di dati fittizi o simulazioni sintetiche.

---

### 3.9 Mappa di Relazione Agenti-Skill-Template-Artefatti

```text
+-----------------------+----------------------------------+------------------------------------+---------------------------------------+
| AGENTE RESPONSABILE   | SKILL APPLICATA                  | TEMPLATE GUIDA                     | ARTEFATTO GENERATO IN runs/<caso>/   |
+-----------------------+----------------------------------+------------------------------------+---------------------------------------+
| ai-coordinator        | noto-survey-pipeline             | templates/status_template.md       | runs/<caso>/status.md                 |
| questionnaire-agent   | noto-brief-structuring           | templates/brief_template.md        | runs/<caso>/brief.md                  |
| questionnaire-agent   | noto-questionnaire-drafting      | templates/questionnaire_template.md| runs/<caso>/questionnaire.md          |
| methodology-agent     | noto-methodology-audit           | templates/methodology_template.md  | runs/<caso>/methodology.md            |
| compliance-agent      | noto-compliance-check            | templates/compliance_template.md   | runs/<caso>/compliance.md             |
| questionnaire-agent   | noto-questionnaire-consolidation | templates/final_template.md        | runs/<caso>/final.md                  |
|                       |                                  | (CLI: export_limesurvey.py)        | runs/<caso>/limesurvey_survey.txt     |
| questionnaire-agent   | noto-survey-extractor            | templates/extracted_survey_template| runs/<caso>/extracted_survey.md       |
| reporting-agent       | noto-agcom-reporting             | templates/agcom_template.md        | runs/<caso>/scheda_agcom.md           |
+-----------------------+----------------------------------+------------------------------------+---------------------------------------+
```

---

## 4. Guida ai 3 Workflow Guidati e Comandi Slash

I workflow guidati offrono percorsi standardizzati e riproducibili per le diverse esigenze di ricerca dell'istituto. Possono essere avviati digitando il rispettivo comando slash sia su Google Antigravity sia su Claude Code.

### 4.1 `/nuova-indagine` (Percorso Completo da Brief a Versione Finale)

- **Scopo**: Progettazione completa da zero di una nuova indagine campionaria a partire da un documento grezzo (appunti del cliente, bozza preliminare, trascrizione autorizzata).
- **Sequenza delle Fasi**:
  $$\text{brief} \longrightarrow \text{questionnaire} \longrightarrow \text{methodology} \longrightarrow \text{compliance} \longrightarrow \text{final}$$
- **Sintassi di Avvio**:
  ```text
  /nuova-indagine <id-caso> <percorso-file-input>
  ```
  *Esempio reale*:
  ```text
  /nuova-indagine demo-biblioteca examples/brief_demo.md
  ```
- **Flusso Operativo Dettagliato**:
  1. **Inizializzazione**: `ai-coordinator` crea `runs/demo-biblioteca/`, copia il brief in `source/brief_demo.md` e inizializza `status.md`.
  2. **Fase 1 (`brief`)**: `questionnaire-agent` redige `brief.md`. L'orchestratore presenta le lacune informative e si ferma (**STOP Gate 1**).
  3. **Fase 2 (`questionnaire`)**: L'utente approva e fornisce chiarimenti. `questionnaire-agent` redige la bozza in `questionnaire.md`. L'orchestratore presenta la bozza e si ferma (**STOP Gate 2**).
  4. **Fase 3 (`methodology`)**: L'utente approva la bozza. `methodology-agent` esegue l'audit in `methodology.md`. L'orchestratore presenta la griglia a 11 colonne con le alternative A/B/C e si ferma (**STOP Gate 3**).
  5. **Fase 4 (`compliance`)**: L'utente seleziona le opzioni preferite (es. *"Accetto Opzione B per Q01 e Q03"*). `compliance-agent` esegue lo screening privacy in `compliance.md`. L'orchestratore presenta i punti per il DPO e si ferma (**STOP Gate 4**).
  6. **Fase 5 (`final`)**: L'utente valida le prescrizioni. `questionnaire-agent` redige `final.md` recependo esclusivamente le scelte registrate, ed esegue lo script per generare `limesurvey_survey.txt`. L'orchestratore presenta il questionario consolidato e si ferma (**STOP Gate 5**).
  7. **Chiusura**: L'utente approva definitivamente; `ai-coordinator` imposta lo stato su `COMPLETATO (MODULO A)`.

---

### 4.2 `/revisione-questionario` (Audit e Consolidamento di Questionario Esistente)

- **Scopo**: Revisione formale, audit metodologico e screening privacy di un questionario già redatto dal committente o proveniente da una serie storica.
- **Sequenza delle Fasi**:
  Le fasi `brief` e `questionnaire` vengono saltate (`SALTATA` in `status.md`); il flusso si articola in:
  $$\text{methodology} \longrightarrow \text{compliance} \longrightarrow \text{final}$$
- **Sintassi di Avvio**:
  ```text
  /revisione-questionario <id-caso> <percorso-questionario-esistente>
  ```
  *Esempio reale*:
  ```text
  /revisione-questionario revisione-customer examples/questionario_demo.md
  ```
- **Flusso Operativo Dettagliato**:
  1. **Inizializzazione**: Viene creata la cartella del caso; il questionario originale viene copiato immutato in `source/`; `status.md` imposta le prime due fasi su `SALTATA` e attiva `methodology`.
  2. **Audit Metodologico**: `methodology-agent` esamina il testo sorgente producendo `methodology.md`. L'orchestratore mostra i rischi rilevati (domande leading, problemi di filtro) e si ferma (**STOP Gate 1**).
  3. **Screening Privacy**: Il ricercatore indica in chat quali modifiche accettare. `compliance-agent` audita il questionario evidenziando categorie Art. 9 GDPR e tutele. L'orchestratore si ferma (**STOP Gate 2**).
  4. **Consolidamento Finale**: `questionnaire-agent` redige `final.md` con il registro comparativo tra testo originario e testo approvato, generando anche `limesurvey_survey.txt`. L'orchestratore si ferma (**STOP Gate 3**).
  5. **Chiusura Modulo A**: Con l'approvazione finale, il caso viene archiviato come completato.

---

### 4.3 `/audit-singolo` (Verifica Specialistica Mirata: Metodologia o Compliance)

- **Scopo**: Esecuzione puntuale e isolata di una singola verifica specialistica su un documento senza generare il questionario consolidato finale.
- **Modalità Supportate**:
  - `methodology`: Solo audit metodologico delle domande, griglia a 11 colonne e 3 alternative di revisione;
  - `compliance`: Solo screening privacy, censimento categorie Art. 9 GDPR, rischi identificazione indiretta e checklist AI Act.
- **Sintassi di Avvio**:
  ```text
  /audit-singolo <id-caso> <tipo-audit> <percorso-file>
  ```
  *Esempi reali*:
  ```text
  /audit-singolo test-metodo methodology examples/questionario_demo.md
  /audit-singolo test-privacy compliance examples/questionario_demo.md
  ```
- **Flusso Operativo**:
  1. `ai-coordinator` crea `runs/<id-caso>/`, salva l'input in `source/` e imposta la sola fase richiesta su `IN CORSO`.
  2. L'agente incaricato (`methodology-agent` o `compliance-agent`) produce il relativo artefatto (`methodology.md` o `compliance.md`).
  3. L'orchestratore presenta la sintesi in chat e **si ferma**.
  4. Il ricercatore decide se archiviare il caso o se evolvere il workflow verso una revisione completa.

---

### 4.4 Protocollo dei Gate di Stop (STOP Gate) e Scelte Decisionali

Ad ogni STOP Gate, `ai-coordinator` sospende tassativamente l'esecuzione ed attende una risposta esplicita del ricercatore umano in chat. Le modalità di risposta ammesse sono:

1. **`APPROVATO`**:
   - Significato: L'artefatto è conforme alle attese; si passa alla fase successiva.
   - Azione del Coordinatore: Registra in `status.md` data, revisore e transizione di fase.
2. **`APPROVATO CON MODIFICHE / SELEZIONE`**:
   - Significato: Utilizzato tipicamente dopo le fasi `methodology` o `compliance`. Il ricercatore specifica quali raccomandazioni recepire.
   - *Esempio di messaggio dell'utente*:
     ```text
     Approvo l'audit. Per Q01 scelgo Opzione B (modifica minima per tutelare la serie storica).
     Per Q02 accetto Opzione C (sdoppiamento domanda doppia). Per Q03 conservo Opzione A (originale).
     Accetto le prescrizioni privacy su Q04 inserendo il codice 99.
     ```
   - Azione del Coordinatore: Trascrive integralmente le scelte puntuali nel registro di `status.md` e istruisce lo specialista successivo affinché le rispetti rigorosamente.
3. **`RIFIUTATO / DA REVISIONARE`**:
   - Significato: L'artefatto presenta lacune formali, fraintendimenti o richiede modifiche prima di procedere.
   - Azione del Coordinatore: Registra le obiezioni in `status.md` e riassegna la medesima fase allo specialista per la correzione.

---

## 5. Manuale Operativo delle 6 CLI in `scripts/`

La piattaforma include una suite di 6 strumenti da riga di comando (CLI) in Python, utilizzabili sia dagli agenti come passaggi interni di automazione, sia direttamente dal ricercatore dal terminale di sistema (PowerShell, Bash, CMD).

---

### 5.1 `scripts/export_limesurvey.py`

- **Finalità**: Converte un questionario consolidato (`final.md` o `questionnaire.md`) nel formato nativo tab-delimited (TSV a 14 colonne standard) compatibile con l'importazione diretta in **LimeSurvey** (funzione *"Importa struttura indagine / .txt"*).
- **Sintassi**:
  ```bash
  python scripts/export_limesurvey.py <input-file> [-o OUTPUT] [-l LANG]
  ```
- **Argomenti e Flag**:
  - `input` *(posizionale, obbligatorio)*: Percorso del file Markdown del questionario (`final.md` o `questionnaire.md`).
  - `-o, --output` *(opzionale)*: Percorso del file `.txt` di output. Se omesso, genera `limesurvey_survey.txt` nella stessa cartella dell'input.
  - `-l, --lang` *(opzionale, default: `it`)*: Codice ISO della lingua dell'indagine.
- **Struttura del File Prodotto (14 Colonne Standard LimeSurvey)**:
  Le 14 colonne prodotte per ogni riga sono:
  1. `id`: Identificativo numerico del record.
  2. `related_id`: ID del record genitore (es. ID domanda per le opzioni `A`).
  3. `class`: Classe del record (`S`=Indagine, `SL`=Impostazioni Lingua, `G`=Gruppo/Sezione, `Q`=Domanda, `SQ`=Sottodomanda, `A`=Risposta).
  4. `type/scale`: Tipo di domanda LimeSurvey (`L`=Scelta singola lista, `M`=Scelta multipla, `F`=Matrice, `T`=Testo lungo, `S`=Testo breve, `N`=Numerica, `X`=Testo informativo/regia, `1`=Seconda scala).
  5. `name`: Codice mnemonico del record (`G1`, `Q01`, `ans1`, `98`, ecc.).
  6. `relevance`: Condizione logica di visualizzazione basata su ExpressionScript (es. `Q01.NAOK == "1"`).
  7. `text`: Testo rivolto al rispondente o descrizione del gruppo.
  8. `help`: Note di regia, testo di aiuto o istruzioni per l'intervistatore.
  9. `language`: Lingua del testo (`it`).
  10. `validation`: Espressione di convalida regex per input aperti/numerici.
  11. `mandatory`: Obbligatorietà della domanda (`Y` o `N`).
  12. `other`: Presenza dell'opzione *"Altro (specificare)"* (`Y` o `N`).
  13. `default`: Valore predefinito.
  14. `same_default`: Ereditarietà valore predefinito (`0` o `1`).
- **Exit Code**: `0` se l'esportazione ha successo; `1` in caso di errore di parsing o file non trovato.
- **Esempio d'Uso**:
  ```bash
  python scripts/export_limesurvey.py examples/demo_run_biblioteca/final.md -o runs/test/limesurvey_survey.txt
  ```

---

### 5.2 `scripts/extract_survey_knowledge.py`

- **Finalità**: Estrae e normalizza in modo strutturato batterie di domande, costrutti e scale da questionari storici e report di ricerca in formato testuale o documentale (`.md`, `.txt`, `.docx`, `.pdf`), popolando l'archivio conforme a `templates/extracted_survey_template.md` o generando un dizionario JSON strutturato.
- **Sintassi**:
  ```bash
  python scripts/extract_survey_knowledge.py <source> [-o OUTPUT] [-f {md,json}] [--id-studio ID] [--committente COMM] [--anno ANNO] [--target TARGET] [--campione CAMP] [--modalita MOD] [--area AREA] [-v]
  ```
- **Argomenti e Flag**:
  - `source` *(posizionale, obbligatorio)*: Percorso del file sorgente da analizzare (`.md`, `.txt`, `.docx`, `.pdf`).
  - `-o, --output` *(opzionale)*: Percorso del file di destinazione (default: `extracted_survey.md` o `.json`).
  - `-f, --format` *(opzionale, default: `md`)*: Formato di output (`md` per Markdown conforme a `templates/extracted_survey_template.md`; `json` per dizionario strutturato).
  - `--id-studio`: Identificativo mnemonico dello studio storico (es. `POL_BAROMETRO_2023`).
  - `--committente`: Nome del committente originario dell'indagine.
  - `--anno`: Anno o periodo di svolgimento della rilevazione.
  - `--target`: Popolazione di riferimento e universo campionario.
  - `--campione`: Numerosità campionaria (es. `1000 casi`).
  - `--modalita`: Metodo di somministrazione originario (`CATI`, `CAWI`, `CAPI`, `Mista`).
  - `--area`: Area tematica prevalente (es. `Politico-Elettorale`, `Civica`, `Economica`).
  - `-v, --verbose`: Abilita il log dettagliato delle operazioni a terminale.
- **Exit Code**: `0` in caso di successo; `1` se il file di input non esiste, è vuoto o non contiene quesiti interpretabili.
- **Esempi d'Uso**:
  ```bash
  # Estrazione standard in Markdown strutturato
  python scripts/extract_survey_knowledge.py historical_report.txt -o knowledge/extracted_report_2023.md --anno 2023 --modalita CATI

  # Estrazione in formato JSON con metadati completi
  python scripts/extract_survey_knowledge.py historical_survey.md -f json -o knowledge/survey_2024.json --committente "Regione Lombardia" --target "Cittadini 18+"
  ```

---

### 5.3 `scripts/generate_interviewer_guide.py`

- **Finalità**: Genera automaticamente la **Guida Operativa per l'Intervistatore** (CATI/CAPI) a partire da un questionario (`final.md` o `questionnaire.md`). Riconosce e applica convenzioni tipografiche standard per facilitare la lettura a video o cartacea durante la somministrazione e può produrre esportazioni in Markdown, Word (.docx) o HTML.
- **Sintassi**:
  ```bash
  python scripts/generate_interviewer_guide.py <input_file> [-o OUTPUT] [-f {md,docx,both,html}]
  ```
- **Argomenti e Flag**:
  - `input_file` *(posizionale, obbligatorio)*: Percorso del questionario sorgente.
  - `-o, --output` *(opzionale)*: Percorso del file di destinazione. Se omesso, deriva il nome dal file sorgente (es. `guida_intervistatore.md`).
  - `-f, --format` *(opzionale, default: `md`)*: Formato di output desiderato:
    - `md`: Markdown ad alta leggibilità con callout tipografici;
    - `docx`: Documento Microsoft Word professionale con stili visivi distinti per testo da leggere e note di regia (richiede la libreria opzionale `python-docx`; esegue fallback automatico su Markdown se non installata);
    - `both`: Genera simultaneamente sia il file `.md` sia il file `.docx`;
    - `html`: Documento HTML autonomo visualizzabile in qualsiasi browser con foglio di stile CSS integrato.
- **Convenzioni Tipografiche Applicate nella Guida**:
  - **TESTO DA LEGGERE AD ALTA VOCE**: Evidenziato in grassetto, con istruzioni chiare di lettura;
  - *NOTE DI REGIA E SOMMINISTRAZIONE*: Evidenziate in corsivo e racchiuse tra parentesi quadre (`[NON LEGGERE LE OPZIONI]`, `[RUOTARE L'ORDINE]`, `[PROBING NEUTRALE]`);
  - `OPZIONI SPONTANEE`: Codici `98` (*Non so*) e `99` (*Rifiuta*) contrassegnati esplicitamente con l'avviso *"NON SOLLECITARE — REGISTRARE SOLO SE EMERGE SPONTANEAMENTE DALL'INTERVISTATO"*.
- **Exit Code**: `0` su generazione completata; `1` in caso di errore.
- **Esempi d'Uso**:
  ```bash
  # Generazione della guida in formato Markdown
  python scripts/generate_interviewer_guide.py examples/demo_run_biblioteca/final.md -o runs/caso-1/guida.md

  # Generazione in formato HTML per visualizzazione rapida da browser
  python scripts/generate_interviewer_guide.py examples/demo_run_biblioteca/final.md -f html -o runs/caso-1/guida.html
  ```

---

### 5.4 `scripts/generate_agcom_report.py`

- **Finalità**: Genera e valida automaticamente la **Scheda Informativa del Sondaggio** ai sensi dell'art. 5 della Delibera AGCOM n. 256/10/CSP. Esegue il calcolo matematico del margine d'errore statistico teorico al 95% di confidenza, trascrive integralmente i quesiti con opzioni e codici `97/98/99`, e applica rigorosamente la marcatura `[DA VERIFICARE SUL CAMPO]`.
- **Sintassi**:
  ```bash
  python scripts/generate_agcom_report.py [case_dir] [--case-dir DIR] [-o OUTPUT] [-n SAMPLE_SIZE] [--client CLIENT] [--buyer BUYER] [--media MEDIA] [--pub-date PUB_DATE] [--fieldwork-date FIELD_DATE] [--title TITLE] [--check-only]
  ```
- **Argomenti e Flag**:
  - `case_dir` *(posizionale o `--case-dir`, opzionale)*: Percorso della cartella del caso (es. `runs/caso-1` o `examples/demo_run_biblioteca`) o percorso diretto a un questionario `.md`.
  - `-o, --output` *(opzionale)*: Percorso del file Markdown di output (default: `<case_dir>/scheda_agcom.md`).
  - `-n, --sample-size` *(opzionale)*: Numerosità campionaria pianificata $n$ per il calcolo del margine d'errore (default: ricavata dal brief o 1000 casi).
  - `--client`: Nome del committente del sondaggio.
  - `--buyer`: Nome dell'acquirente del sondaggio (default: medesimo committente).
  - `--media`: Mezzo di comunicazione di massa su cui è programmata la diffusione (es. testata giornalistica, TV, portale web).
  - `--pub-date`: Data prevista o effettiva di diffusione editoriale.
  - `--fieldwork-date`: Data o periodo di realizzazione delle interviste.
  - `--title`: Titolo o oggetto del sondaggio.
  - `--check-only`: Flag booleano; esegue unicamente il controllo di conformità su una scheda preesistente senza riscriverla.
- **Formula Statistica Applicata**:
  Il margine d'errore massimo teorico proporzionale al 95% di confidenza ($z = 1.96$, $p = 0.5$) viene calcolato come:
  $$e = \pm z \cdot \sqrt{\frac{p(1-p)}{n}} = \pm \frac{1.96 \cdot 0.5}{\sqrt{n}} = \pm \frac{0.98}{\sqrt{n}}$$
  Per popolazioni finite note di dimensione $N$:
  $$e = \pm z \cdot \sqrt{\frac{p(1-p)}{n}} \cdot \sqrt{\frac{N-n}{N-1}}$$
- **Exit Code**: `0` se generata o validata con conformità totale; `1` se si riscontrano violazioni (es. assenza di codici `99`, omissione del soggetto realizzatore Noto Sondaggi SRL, assenza delle 7 sezioni obbligatorie).
- **Esempi d'Uso**:
  ```bash
  # Generazione automatica estraendo i dati da una cartella di caso
  python scripts/generate_agcom_report.py examples/demo_run_biblioteca -o runs/test/scheda_agcom.md

  # Generazione con specificazione di parametri di diffusione
  python scripts/generate_agcom_report.py runs/politico-1 \
    --client "Quotidiano Nazionale" \
    --media "Edizione Cartacea e Web" \
    --sample-size 1000 \
    --pub-date "2026-11-10"

  # Solo verifica di conformità di una scheda esistente
  python scripts/generate_agcom_report.py examples/demo_run_biblioteca/scheda_agcom.md --check-only
  ```

---

### 5.5 `scripts/validate_runs.py`

- **Finalità**: Linter metodologico e validatore formale integrato. Ispeziona gli artefatti del repository per garantire che rispettino puntualmente le regole scientifiche, i requisiti di privacy, i tracciati standard e la tassonomia della non risposta.
- **Sintassi**:
  ```bash
  python scripts/validate_runs.py [percorso_caso_o_file ...]
  ```
  > **Nota operativa sui parametri**: Lo script processa argomenti posizionali diretti (cartelle o percorsi di singoli file). Non implementa il modulo `argparse` e non dispone di un flag `--help` (passare `--help` viene interpretato come percorso di file non trovato ed esce con codice `1`).
- **Modalità di Esecuzione**:
  1. **Validazione di una cartella di caso**: Esegue la batteria completa di test su tutti gli artefatti presenti nella cartella indicata (`status.md`, `brief.md`, `questionnaire.md`, `methodology.md`, `compliance.md`, `final.md`, `scheda_agcom.md`, `limesurvey_survey.txt`):
     ```bash
     python scripts/validate_runs.py examples/demo_run_biblioteca
     ```
  2. **Validazione di singoli file**: Identifica automaticamente il tipo di documento in base al nome e applica il validatore specifico:
     ```bash
     python scripts/validate_runs.py runs/caso-1/final.md
     python scripts/validate_runs.py runs/caso-1/methodology.md
     ```
  3. **Validazione cumulativa**: Se eseguito senza argomenti, scansiona e valida tutte le cartelle presenti all'interno di `runs/`:
     ```bash
     python scripts/validate_runs.py
     ```
- **Controlli Effettuati**:
  - `status.md`: Presenza delle 3 sezioni obbligatorie e metadati di avanzamento;
  - `brief.md`: Rispetto delle 6 sezioni, assenza di parametri campionari arbitrari, marcatura `[DA VERIFICARE]`;
  - `questionnaire.md`: Presenza delle sezioni, istruzioni di regia tipografiche, inclusione dei codici `97`, `98` e `99`;
  - `methodology.md`: Presenza delle 11 colonne esatte nella griglia riepilogativa, presenza dei 12 campi per ogni scheda analitica, articolazione delle Opzioni A, B e C, colonna decisionale `DA CONFERMARE`, assenza di promesse causali certe;
  - `compliance.md`: Rispetto delle 4 sezioni, screening Art. 9 GDPR, valutazione singling out, stato `Approvazione dell'esperto umano: IN ATTESA`;
  - `final.md`: Presenza del Registro Modifiche comparativo, mappa filtri, piano di pretest/pilot;
  - `limesurvey_survey.txt`: Verifica delle 14 colonne separate da tabulazione su ogni riga, record `S`, `SL`, `G`, `Q`, `A`/`SQ`, conformità ExpressionScript;
  - `scheda_agcom.md`: Presenza delle 7 sezioni e dei 12 campi obbligatori AGCOM, soggetto realizzatore Noto Sondaggi SRL, trascrizione quesiti con codici `97/98/99`, presenza marcatura `[DA VERIFICARE SUL CAMPO]`;
  - `extracted_survey.md`: Presenza delle 5 sezioni, tracciamento codici originari, codici standard `97`, `98`, `99`.
- **Exit Code**: `0` se tutti i file sono pienamente conformi; `1` se vengono riscontrate non-conformità.

---

### 5.6 `scripts/check_mirror_sync.py`

- **Finalità**: Guardiano dell'integrità architetturale. Verifica la perfetta specularità e sincronizzazione dei file tra il ramo Google Antigravity (`.agents/`, `AGENTS.md`) e il ramo Claude Code (`.claude/`, `CLAUDE.md`).
- **Sintassi**:
  ```bash
  python scripts/check_mirror_sync.py
  ```
- **Ambiti Verificati**:
  1. **Regole Globali**: Uguaglianza byte-a-byte tra `AGENTS.md` e `CLAUDE.md` (normalizzando i terminatori di linea CRLF/LF);
  2. **Agenti (7)**: Presenza e perfetta corrispondenza del corpo operativo dei file in `.agents/agents/*.md` e `.claude/agents/*.md`, tollerando solo le differenze di metadati di frontmatter tipiche delle due piattaforme (`mainAgent` vs `type: supervisor`);
  3. **Skill (8)**: Perfetta identità di tutti i file `SKILL.md` e delle cartelle associate in `.agents/skills/` e `.claude/skills/`;
  4. **Workflow / Comandi Slash (3)**: Identità di corpo operativo tra `.agents/workflows/*.md` e `.claude/commands/*.md`;
  5. **Template Standard (8)**: Verifica della presenza e integrità degli 8 file di template in `templates/`.
- **Exit Code**: `0` se l'architettura è speculare al 100%; `1` in caso di asimmetrie o file orfani.

---

## 6. I Moduli della Knowledge Base Canonica

La piattaforma include una base di conoscenza metodologica canonica memorizzata in formato JSON strutturato all'interno della cartella `knowledge/`. Questi moduli consentono di standardizzare i quesiti di profilazione socio-demografica e le serie storiche politico-elettorali, accelerando la redazione delle bozze e garantendo la comparabilità nel tempo.

### 6.1 `knowledge/demographics_standard.json`

- **Titolo Ufficiale**: *Standard Socio-Demografico Canonico Armonizzato — Noto Sondaggi SRL*.
- **Standard di Riferimento**: Classificazioni ufficiali **Istat** (Censimento Permanente della Popolazione, Rilevazione Forze di Lavoro) ed **Eurostat**, con codifica uniforme dei valori di uscita (`97=Non applicabile`, `98=Non so`, `99=Preferisco non rispondere`).
- **Variabili Canoniche Mappate**:
  1. `DEM_GENERE`: Rilevazione genere anagrafico (1=Uomo, 2=Donna, 3=Altra identità; codici 97, 98, 99). Nota di regia per interviste telefoniche CATI.
  2. `DEM_ETA_CLASSI`: Standard Istat in 6 classi di età (18-24, 25-34, 35-44, 45-54, 55-64, 65+). Variabile primaria per le quote di post-stratificazione campionaria.
  3. `DEM_TITOLO_STUDIO`: Classificazione a 5 livelli armonizzata Istat/Eurostat (Nessuno/Elementare, Media inferiore, Media superiore/Diploma, Laurea triennale/magistrale, Post-laurea/Master/Dottorato).
  4. `DEM_CONDIZIONE_PROFESSIONALE`: Classificazione Istat Forze di Lavoro in 8 categorie (Occupato dipendente a tempo indeterminato, Dipendente determinato, Autonomo/Libero professionista/Imprenditore, In cerca di occupazione/Disoccupato, Studente, Casalinga/o, Pensionato/Ritirato dal lavoro, Altra condizione).
  5. `DEM_RIPARTIZIONE_GEO`: Macro-ripartizioni territoriali Istat NUTS-1 (Nord-Ovest, Nord-Est, Centro, Sud, Isole). Variabile obbligatoria di pesatura campionaria.
  6. `DEM_AMPIEZZA_COMUNE`: Fasce demografiche dei comuni di residenza (Fino a 5.000 ab., 5.001-10.000, 10.001-50.000, 50.001-100.000, Oltre 100.000 ab./Capoluogo).
  7. `DEM_STATO_CIVILE`: Stato civile anagrafico (Celibe/Nubile, Coniugato/a o Unione civile, Separato/a o Divorziato/a, Vedovo/a).

Ogni variabile include: `id_item`, `construct`, `question_text`, `question_type`, `scale_type`, flag `weighting_variable`, opzioni con codici numerici, codici missing `97/98/99`, condizioni di filtro e note di regia tipografiche per CATI, CAWI e CAPI.

---

### 6.2 `knowledge/political_batteries_core.json`

- **Titolo Ufficiale**: *Batterie Politico-Elettorali Canoniche e Serie Storiche — Noto Sondaggi SRL*.
- **Standard di Riferimento**: Archivio storico dei Barometri Politici di Noto Sondaggi SRL e requisiti di trasparenza della Delibera AGCOM 256/10/CSP.
- **Batterie Canoniche Mappate**:
  1. `POL_FIDUCIA_PREMIER`: Misurazione longitudinale del gradimento del Presidente del Consiglio in carica. Scala ordinale bilanciata a 4 punti (*Molta, Abbastanza, Poca, Nessuna fiducia*) per il calcolo dell'indice netto, con opzione alternativa numerica su scala 1-10.
  2. `POL_BATTERIA_LEADER`: Matrice canonica di valutazione della fiducia nei leader dei principali schieramenti politici nazionali. Include istruzioni tassative di randomizzazione/rotazione delle righe (`[RUOTARE L'ORDINE DEI LEADER]`) per neutralizzare l'effetto d'ordine (*priming* o *recency*).
  3. `POL_FIDUCIA_GOVERNO`: Giudizio complessivo sull'operato del Governo della Repubblica su scala a 4 punti.
  4. `POL_INTENZIONE_VOTO`: Formulario canonico per la simulazione elettorale alle Elezioni Politiche / Europee. Include domanda preliminare di propensione al voto/astensione (*filtro di turnout*), lista delle principali forze politiche aggiornate, scheda bianca/nulla e tutela rafforzata ex Art. 9 GDPR con opzione `99 = Segreto del voto / Preferisco non rispondere`.
  5. `POL_COLLOCAZIONE_SX_DX`: Auto-collocazione del rispondente sull'asse politico unidimensionale Sinistra-Destra (scala a 10 punti con estremi ancorati 1=Sinistra, 10=Destra), con codici `98` (Nessuna collocazione / Non si riconosce) e `99` (Rifiuta).
  6. `POL_PROBLEMI_PRIORITARI`: Batteria semi-aperta o a risposta multipla limitata (massimo 2 o 3 risposte) per rilevare le priorità percepite per il Paese (lavoro/occupazione, sanità, inflazione/carovita, sicurezza, immigrazione, ambiente/clima, fisco/tasse).
  7. `POL_GIUDIZIO_ECONOMIA`: Trend di percezione sulla situazione economica generale del Paese rispetto all'anno precedente (Migliorata, Invariata, Peggiorata) e previsione a 12 mesi.

---

### 6.3 Integrazione della Knowledge Base nella Pipeline Redazionale

Durante la redazione del questionario (`noto-questionnaire-drafting`), l'agente `questionnaire-agent` consulta i file JSON canonici:
- **Eredità fedele dei codici**: Le domande socio-demografiche e le batterie politiche riprendono letteralmente i testi, l'ordine delle opzioni e i codici mnemonici della Knowledge Base.
- **Preservazione delle metriche**: Non vengono modificate le scale verbali a 4 passi o le scale 1-10 senza esplicita richiesta del ricercatore, prevenendo rotture nelle serie storiche decennali dell'istituto.
- **Popolamento automatico LimeSurvey**: Lo script `export_limesurvey.py` riconosce gli ID canonici (`DEM_*`, `POL_*`) e associa automaticamente i codici scala e le classi di domanda ottimali per LimeSurvey.

---

## 7. Casi d'Uso Pratici End-to-End

Di seguito vengono illustrati due scenari operativi tipici completi, rappresentativi dell'utilizzo quotidiano della piattaforma all'interno di Noto Sondaggi SRL.

---

### 7.1 Scenario A: Dalla Richiesta Grezza alla Somministrazione e Diffusione (Caso Biblioteca)

**Scenario**: Il Comune committente richiede un'indagine campionaria sui cittadini residenti per valutare l'ampliamento degli orari e dei servizi della Biblioteca Civica. Il ricercatore dispone solo di brevi appunti preliminari (`examples/brief_demo.md`).

#### Passo 1: Avvio del Workflow
Il ricercatore avvia la procedura da chat o terminale:
```text
/nuova-indagine demo-biblioteca examples/brief_demo.md
```
`ai-coordinator` crea la cartella `runs/demo-biblioteca/`, copia gli appunti in `source/brief_demo.md` e incarica `questionnaire-agent`.

#### Passo 2: Strutturazione del Brief e Chiarimento Lacune
`questionnaire-agent` genera `runs/demo-biblioteca/brief.md`. Rileva che il target è *"Cittadini maggiorenni residenti"*, ma la modalità di somministrazione e il campione non sono specificati. Imposta:
- Modalità di somministrazione: `DA DEFINIRE [Proposta: CATI/CAMI per rappresentatività anagrafica]`
- Campione: `DA DEFINIRE [Proposta: n=800 casi, margine errore ±3.46%]`
- Marca come `[DA VERIFICARE]` il dato citato di 50.000 prestiti annui.

L'orchestratore si ferma al **Gate 1**. Il ricercatore risponde in chat:
```text
Approvo il brief. Modalità confermata mista CATI/CAWI. Campione n=800 casi. Confermo il dato dei 50.000 prestiti.
```

#### Passo 3: Stesura della Bozza di Questionario
`questionnaire-agent` riceve le istruzioni e redige `runs/demo-biblioteca/questionnaire.md`. Il formulario include:
- `Q01`: Frequenza di fruizione della biblioteca nell'ultimo anno (scala ordinale a 4 classi);
- `Q02`: Giudizio sugli orari attuali e sulla disponibilità dei volumi (formulazione preliminare);
- `Q03`: Interesse verso l'apertura serale e domenicale (filtro su fruitori);
- Domande socio-demografiche di coda (`DEM_GENERE`, `DEM_ETA_CLASSI`).
Tutti gli item includono codici `97`, `98`, `99` e note di regia. L'orchestratore si ferma al **Gate 2**. Il ricercatore approva la bozza.

#### Passo 4: Audit Metodologico Item-per-Item
`methodology-agent` esamina `questionnaire.md` e produce `runs/demo-biblioteca/methodology.md`:
- Rileva su `Q02` una criticità di **doppia domanda (*double-barreled*)**: l'item chiedeva contemporaneamente una valutazione sugli *orari* e sui *libri disponibili*, impedendo a chi è soddisfatto dei volumi ma scontento degli orari di esprimersi accuratamente.
- Propone le 3 alternative:
  - *Opzione A*: Conservare l'originale;
  - *Opzione B*: Modifica minima con chiarimento verbale dell'intervistatore;
  - *Opzione C*: Sdoppiamento in due item distinti (`Q02A: Soddisfazione orari`, `Q02B: Disponibilità volumi`).
L'orchestratore si ferma al **Gate 3**. Il ricercatore risponde:
```text
Approvo l'audit. Scelgo Opzione C per Q02: separiamo orari e disponibilità libri in due quesiti distinti.
```

#### Passo 5: Screening Privacy e AI Act
`compliance-agent` audita il questionario producendo `runs/demo-biblioteca/compliance.md`. Rileva che l'indagine non tocca categorie particolari ex Art. 9 GDPR, ma raccomanda di non raccogliere l'indirizzo esatto di residenza per evitare il *singling out*, mantenendo solo la circoscrizione/quartiere. L'orchestratore si ferma al **Gate 4**. Il ricercatore approva la raccomandazione.

#### Passo 6: Consolidamento Finale ed Esportazione LimeSurvey
`questionnaire-agent` redige `runs/demo-biblioteca/final.md`:
- Sdoppia `Q02` in `Q02A` e `Q02B`;
- Aggiorna il Registro Modifiche;
- Esegue in automatico `scripts/export_limesurvey.py`, generando `runs/demo-biblioteca/limesurvey_survey.txt` pronto per il caricamento su piattaforma.
L'orchestratore si ferma al **Gate 5**. Il ricercatore approva definitivamente chiudendo il Modulo A.

#### Passo 7: Generazione Guida Intervistatore e Scheda AGCOM
Per completare i preparativi alla rilevazione e alla diffusione:
1. Il responsabile del campo genera la guida per gli operatori telefonici:
   ```bash
   python scripts/generate_interviewer_guide.py examples/demo_run_biblioteca/final.md -o examples/demo_run_biblioteca/guida_intervistatore.md
   ```
2. Il ricercatore genera la bozza di Scheda Informativa AGCOM con il calcolo del margine d'errore ($n = 800 \to e = \pm 3.46\%$):
   ```bash
   python scripts/generate_agcom_report.py examples/demo_run_biblioteca -n 800 --client "Comune di Pavia" --media "Sito Istituzionale e Stampa Locale"
   ```
3. Il validatore certifica la perfetta conformità dell'intero pacchetto documentale:
   ```bash
   python scripts/validate_runs.py examples/demo_run_biblioteca
   # Output: [PASS] Tutti i file presenti risultano conformi agli standard metodologici.
   ```

---

### 7.2 Scenario B: Ingestione di Questionari Storici e Salvaguardia di Serie Elettorali

**Scenario**: L'istituto deve predisporre il questionario per il nuovo Barometro Politico periodico e intende recuperare la formulazione storica della batteria sulla fiducia nei leader e sull'intenzione di voto utilizzata nel 2022, conservata in un report di sintesi (`historical_survey_2022.txt`).

#### Passo 1: Ingestione ed Estrazione Strutturata
Il ricercatore richiama la CLI di estrazione:
```bash
python scripts/extract_survey_knowledge.py source/historical_survey_2022.txt \
  -o runs/barometro-nov2026/extracted_survey.md \
  --committente "Editoriale Nazionale" \
  --anno 2022 \
  --modalita CATI \
  --area "Politico-Elettorale"
```
Lo script estrae i singoli item storici, preservando il testo originario rivolto al rispondente, classificando le domande e associando i codici standard di non risposta (`97`, `98`, `99`).

#### Passo 2: Avvio della Revisione del Questionario
Il ricercatore avvia la pipeline di revisione basata sul questionario estratto:
```text
/revisione-questionario barometro-nov2026 runs/barometro-nov2026/extracted_survey.md
```

#### Passo 3: Audit con Tutela di Serie Storica
Durante la fase di audit, `methodology-agent` individua che la batteria dei leader politici (`POL_BATTERIA_LEADER`) presenta una scala verbale a 4 punti (*Molta, Abbastanza, Poca, Nessuna*).
- Segnala che la letteratura accademica recente suggerisce scale numeriche a 10 passi, ma avverte che **modificare la scala comprometterebbe 8 anni di serie storiche mensili** di Noto Sondaggi;
- Raccomanda espressamente l'**Opzione A (Conservare l'originale)** per tutelare l'indice longitudinale di gradimento, suggerendo al massimo un pretest su un sub-campione (*split ballot*) per valutare un eventuale passaggio futuro.
Il ricercatore approva l'Opzione A in chat.

#### Passo 4: Screening Privacy Rafforzato (GDPR Art. 9)
`compliance-agent` esamina le intenzioni di voto e l'auto-collocazione politica:
- Qualifica tali informazioni come categorie particolari ex Art. 9 GDPR;
- Verifica la presenza obbligatoria dell'informativa privacy prima del quesito;
- Accerta che l'opzione *"Preferisco non rispondere / Segreto del voto"* con codice `99` sia chiaramente gestita dal software CATI senza sollecitazione forzante.

#### Passo 5: Consolidamento e Deposito AGCOM
Completato il consolidamento in `final.md` ed esportato il file LimeSurvey, viene generata la Scheda Informativa AGCOM:
```bash
python scripts/generate_agcom_report.py runs/barometro-nov2026 \
  -n 1000 \
  --client "Testata Giornalistica" \
  --media "Quotidiano Nazionale e Canale TV"
```
La scheda riporta:
- Soggetto realizzatore: `Noto Sondaggi SRL`;
- Margine d'errore teorico: $\pm 3.10\%$ ($n=1000$ al 95% di confidenza);
- Marcatura `[DA VERIFICARE SUL CAMPO]` sui contatti e percentuali di voto;
- Prescrizione per il deposito contestuale sul sito `www.sondaggipoliticoelettorali.it`.

---

## 8. Mappa Sinottica dei File e Sintassi Rapida

Per una consultazione immediata durante le sessioni operative, la tabella seguente riepiloga le collocazioni dei file, i comandi di avvio e le CLI della piattaforma:

| Funzione Operativa | Percorso File Google Antigravity | Percorso File Claude Code | Comando / Invocazione CLI |
| :--- | :--- | :--- | :--- |
| **Regole di Progetto** | `AGENTS.md` | `CLAUDE.md` | *(Caricate automaticamente dal sistema)* |
| **Workflow Nuova Indagine** | `.agents/workflows/nuova-indagine.md` | `.claude/commands/nuova-indagine.md` | `/nuova-indagine <caso> <file_input>` |
| **Workflow Revisione** | `.agents/workflows/revisione-questionario.md` | `.claude/commands/revisione-questionario.md` | `/revisione-questionario <caso> <file_quest>` |
| **Workflow Audit Singolo** | `.agents/workflows/audit-singolo.md` | `.claude/commands/audit-singolo.md` | `/audit-singolo <caso> <tipo> <file>` |
| **Orchestratore Pipeline** | `.agents/skills/noto-survey-pipeline/` | `.claude/skills/noto-survey-pipeline/` | `ai-coordinator` |
| **Strutturazione Brief** | `.agents/skills/noto-brief-structuring/` | `.claude/skills/noto-brief-structuring/` | `questionnaire-agent` |
| **Bozza Questionario** | `.agents/skills/noto-questionnaire-drafting/`| `.claude/skills/noto-questionnaire-drafting/`| `questionnaire-agent` |
| **Audit Metodologico** | `.agents/skills/noto-methodology-audit/` | `.claude/skills/noto-methodology-audit/` | `methodology-agent` |
| **Screening Privacy & AI**| `.agents/skills/noto-compliance-check/` | `.claude/skills/noto-compliance-check/` | `compliance-agent` |
| **Consolidamento Finale** | `.agents/skills/noto-questionnaire-consolidation/`| `.claude/skills/noto-questionnaire-consolidation/`| `questionnaire-agent` |
| **Estrazione Questionari**| `.agents/skills/noto-survey-extractor/` | `.claude/skills/noto-survey-extractor/` | `python scripts/extract_survey_knowledge.py` |
| **Reporting AGCOM** | `.agents/skills/noto-agcom-reporting/` | `.claude/skills/noto-agcom-reporting/` | `python scripts/generate_agcom_report.py` |
| **Export LimeSurvey TSV** | `scripts/export_limesurvey.py` | `scripts/export_limesurvey.py` | `python scripts/export_limesurvey.py <final.md>` |
| **Guida Intervistatore** | `scripts/generate_interviewer_guide.py`| `scripts/generate_interviewer_guide.py`| `python scripts/generate_interviewer_guide.py <final.md>`|
| **Validatore di Conformità**| `scripts/validate_runs.py` | `scripts/validate_runs.py` | `python scripts/validate_runs.py <caso_o_file>` |
| **Verifica Sincronizzazione**| `scripts/check_mirror_sync.py` | `scripts/check_mirror_sync.py` | `python scripts/check_mirror_sync.py` |
| **Standard Socio-Demo** | `knowledge/demographics_standard.json` | `knowledge/demographics_standard.json` | *(Modulo canonico Istat/Eurostat)* |
| **Batterie Politiche Core**| `knowledge/political_batteries_core.json`| `knowledge/political_batteries_core.json`| *(Libreria Barometri Noto Sondaggi)* |
| **Stato Progetto & 35 Task** | `docs/statoprogetto.md` | `docs/statoprogetto.md` | Rendicontazione accademica e censimento 35 task (v3.1) |
| **Piano Operativo Roadmap** | `docs/piano_operativo.md` | `docs/piano_operativo.md` | Roadmap incrementale M0–M12 e tracciabilità commit |
| **Piano Test Umani (H1-H10)**| `docs/piano_test_umani.md` | `docs/piano_test_umani.md` | Protocolli di collaudo metodologico e deontologico umano |
| **Manuale Installazione** | `docs/manuale_installazione.md` | `docs/manuale_installazione.md` | Guida completa dal setup dell'ambiente all'avvio operativo |
