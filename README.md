# Noto Sondaggi SRL — Survey AI Platform (Architettura Speculare Antigravity + Claude)

> **Inquadramento Istituzionale e Scientifico**  
> **Istituzione di Ricerca**: IUSS Pavia  
> **Ph.D Candidate / Author**: Adelaide Emma Bernardelli  
> **Supervisione Accademica**: Prof.ssa Alessandra Amendola  

> **Partner Industriale / Committente**: Noto Sondaggi SRL  
> **Paradigma**: Survey AI Human-in-the-Loop per la Ricerca Demoscopica, Sociale e Politica  

---

> 📚 **Documentazione Ufficiale e Guide Operative in Evidenza**
>
> Per la consultazione approfondita e l'avvio operativo della piattaforma, fare riferimento ai 3 documenti cardine in [`docs/`](docs/):
> - 📘 [**Manuale di Installazione e Avvio**](docs/manuale_installazione.md) (`docs/manuale_installazione.md`) — Guida operativa completa dal `git clone` alla configurazione dell'ambiente Python (>= 3.10) e Node.js (>= 18 LTS), avvio su Google Antigravity e Claude Code, gestione percorsi Windows/OneDrive con spazi, uso dei comandi slash e risoluzione problemi.
> - 📗 [**Guida Completa alle Funzionalità**](docs/guida_funzionalita.md) (`docs/guida_funzionalita.md`) — Manuale di riferimento enciclopedico: principi metodologici, tassonomia a 6 codici della non risposta, catalogo dei 7 agenti, 8 skill, 3 workflow guidati, manuale operativo delle 6 CLI in `scripts/`, knowledge base canonica e scenari d'uso pratici.
> - 📕 [**Piano di Test Umano e Protocolli di Collaudo**](docs/piano_test_umani.md) (`docs/piano_test_umani.md`) — Manuale operativo di collaudo metodologico e deontologico: 10 protocolli operativi passo-passo (Protocolli H1 – H10), criteri qualitativi insostituibili per ricercatori e DPO, master checklist tabellari a crocette e modello di tracciamento non conformità.
>
> 📌 **Avanzamento del Progetto e Roadmap di Sviluppo**:
> - 📊 [**Stato del Progetto e Censimento dei 35 Task**](docs/statoprogetto.md) (`docs/statoprogetto.md`) — Documento ufficiale di rendicontazione accademica e aziendale con il censimento analitico e lo stato dei 35 task di sviluppo (Versione 3.1 — Fase di Test Umano).
> - 🗺️ [**Piano Operativo e Roadmap a Milestones**](docs/piano_operativo.md) (`docs/piano_operativo.md`) — Roadmap operativa di implementazione incrementale a 13 milestone (M0 – M12) su 6 track tematiche ancorate al version control.

---

## 1. A cosa serve questo repository

Questo repository ospita la piattaforma multi-agente **human-in-the-loop** in lingua italiana progettata per **Noto Sondaggi SRL**, ingegnerizzata secondo il principio della **doppia specularità integrale** per operare indistintamente e con parità funzionale sia su **Google Antigravity** sia su **Claude Code**.

Il sistema assiste i ricercatori demoscopici nell'intero ciclo di progettazione, revisione metodologica, verifica di conformità normativa e preparazione alla rilevazione (**Modulo A e Reporting Regolamentare**):
1. **Strutturazione del Brief** (`runs/<caso>/brief.md`): formalizzazione di obiettivi conoscitivi, disegno campionario proposto, target, modalità di somministrazione e quesiti aperti da input grezzi, appunti cliente o trascrizioni;
2. **Stesura della Bozza del Questionario** (`runs/<caso>/questionnaire.md`): articolazione strutturata dei quesiti con codici distinti di non risposta (`97=Non applicabile`, `98=Non so`, `99=Preferisco non rispondere`), istruzioni di regia tipografiche standardizzate e salvaguardia delle serie storiche;
3. **Audit Metodologico Item-per-Item** (`runs/<caso>/methodology.md`): diagnosi analitica dei rischi di distorsione cognitiva (doppia formulazione, desiderabilità sociale, polarità sbilanciata, effetto acquiescenza) con griglia a 11 colonne e schede a 12 campi recanti tre alternative operative per ciascun quesito (*Opzione A: Conservare*, *Opzione B: Modifica minima*, *Opzione C: Revisione sostanziale*);
4. **Screening Preliminare Privacy (GDPR Art. 9) e AI Act** (`runs/<caso>/compliance.md`): verifica dei rischi di re-identificazione indiretta, trattamento di categorie particolari di dati (orientamento politico e voto), adeguatezza dell'informativa e trasparenza ex AI Act;
5. **Consolidamento della Versione Finale** (`runs/<caso>/final.md`): recepimento selettivo e tracciabile delle sole modifiche approvate dal ricercatore umano al gate decisionale in chat;
6. **Fieldwork Bridge per LimeSurvey** (`runs/<caso>/limesurvey_survey.txt`): generazione automatica della struttura indagine tab-delimited a 14 colonne conforme allo standard di importazione di LimeSurvey (CATI/CAWI);
7. **Generazione Guida Intervistatore CATI/CAPI** (`runs/<caso>/guida_intervistatore.md` / HTML / Word): produzione automatica della guida di somministrazione con formattazione tipografica ad alta leggibilità per le istruzioni di regia (`[NON LEGGERE]`, `[ROTAZIONE OPZIONI]`, `[PROBING]`);
8. **Reporting Regolamentare AGCOM** (`runs/<caso>/scheda_agcom.md`): redazione della Scheda Informativa obbligatoria del sondaggio ex art. 5 Delibera AGCOM 256/10/CSP per la pubblicazione sui media e il deposito su www.sondaggipoliticoelettorali.it, con calcolo automatico del margine d'errore campionario teorico al 95% di confidenza.

Include inoltre le schede architetturali per i 2 agenti del **Modulo B** (*In attesa di attivazione post-fieldwork*: pesatura campionaria complessa IPF e dashboarding avanzato).  
Il sistema non effettua interviste automatiche con rispondenti sintetici, non carica questionari in piattaforma senza validazione umana e non formula pareri legali definitivi al posto del DPO.

---

## 2. Struttura del Progetto e Mappa dei File

L'albero dei file del repository riflette la rigorosa specularità tra i due ambienti AI e censisce tutti i deliverable realizzati:

```text
NotoSondaggi_Agents4SurveyPlatform/
├── AGENTS.md                                      # Regole globali e governance architettura (Google Antigravity)
├── CLAUDE.md                                      # Regole globali e governance architettura (Claude Code)
├── README.md                                      # Documento vetrina e guida operativa della piattaforma
├── .agents/                                       # Architettura Google Antigravity
│   ├── agents/
│   │   ├── ai-coordinator.md                      # Supervisore e orchestratore (Main Agent, Modulo A)
│   │   ├── questionnaire-agent.md                 # Redattore brief, questionario e consolidamento (Modulo A)
│   │   ├── methodology-agent.md                   # Revisore metodologico item-per-item (Modulo A)
│   │   ├── compliance-agent.md                    # Revisore preliminare GDPR Art. 9 / AI Act (Modulo A)
│   │   ├── reporting-agent.md                     # Specialista reporting regolamentare AGCOM (Attivo)
│   │   ├── analysis-agent.md                      # Analisi statistica e pesatura [In attesa - Modulo B]
│   │   └── dashboard-agent.md                     # Visualizzazione dati e layout [In attesa - Modulo B]
│   ├── skills/
│   │   ├── noto-survey-pipeline/SKILL.md          # Orchestrazione del caso e gestione runs/<caso>/status.md
│   │   ├── noto-brief-structuring/SKILL.md        # Strutturazione del brief da materiali grezzi
│   │   ├── noto-questionnaire-drafting/SKILL.md   # Progettazione e stesura bozza del questionario
│   │   ├── noto-methodology-audit/SKILL.md        # Audit metodologico item-per-item e diagnosi cognitiva
│   │   ├── noto-compliance-check/SKILL.md         # Screening preliminare privacy (GDPR Art. 9) e AI Act
│   │   ├── noto-questionnaire-consolidation/SKILL.md # Consolidamento finale ed export LimeSurvey TSV
│   │   ├── noto-survey-extractor/SKILL.md         # Estrazione e normalizzazione questionari storici
│   │   └── noto-agcom-reporting/SKILL.md          # Scheda Informativa AGCOM (Delibera 256/10/CSP)
│   └── workflows/
│       ├── nuova-indagine.md                      # Flusso completo: brief -> questionnaire -> methodology -> compliance -> final
│       ├── revisione-questionario.md              # Flusso di revisione: methodology -> compliance -> final
│       └── audit-singolo.md                       # Flusso mirato per singola revisione (metodologia o compliance)
├── .claude/                                       # Architettura Claude Code (perfettamente speculare a .agents/)
│   ├── agents/*.md                                # 7 Agenti con frontmatter Claude Code
│   ├── skills/*/SKILL.md                          # 8 Skill speculari
│   └── commands/*.md                              # 3 Comandi slash (/nuova-indagine, /revisione-questionario, /audit-singolo)
├── templates/                                     # 8 Template strutturati obbligatori per gli artefatti
│   ├── status_template.md                         # Modello per runs/<caso>/status.md
│   ├── brief_template.md                          # Modello per runs/<caso>/brief.md
│   ├── questionnaire_template.md                  # Modello per runs/<caso>/questionnaire.md
│   ├── methodology_template.md                    # Modello per runs/<caso>/methodology.md
│   ├── compliance_template.md                     # Modello per runs/<caso>/compliance.md
│   ├── final_template.md                          # Modello per runs/<caso>/final.md
│   ├── extracted_survey_template.md               # Modello per questionari estratti e normalizzati
│   └── agcom_template.md                          # Modello per Scheda Informativa AGCOM (Delibera 256/10/CSP)
├── scripts/                                       # Suite delle 6 CLI di automazione, export, estrazione e QA
│   ├── check_mirror_sync.py                       # Validatore automatico della sincronizzazione speculare
│   ├── validate_runs.py                           # Linter metodologico e strutturale per i casi in runs/
│   ├── export_limesurvey.py                       # Generatore file TSV 14 colonne per LimeSurvey CATI/CAWI
│   ├── extract_survey_knowledge.py                # Estrattore automatico di formulari e batterie da testi storici
│   ├── generate_interviewer_guide.py              # Generatore guida per intervistatore con note di regia (MD/HTML/DOCX)
│   └── generate_agcom_report.py                   # Generatore automatico Scheda AGCOM con calcolo margine d'errore
├── knowledge/                                     # Base di conoscenza canonica e batterie standard
│   ├── demographics_standard.json                 # Batterie socio-demografiche canoniche Istat/Eurostat
│   └── political_batteries_core.json              # Batterie elettorali standard (fiducia leader, voto, posizionamento)
├── docs/                                          # Documentazione operativa, manuali, roadmap e protocolli di test
│   ├── manuale_installazione.md                   # Guida completa dal git clone all'avvio operativo
│   ├── guida_funzionalita.md                      # Manuale di riferimento per agenti, skill, CLI, workflow e metodi
│   ├── piano_test_umani.md                        # Protocolli di collaudo umano (H1-H10), checklist e verbali
│   ├── statoprogetto.md                           # Documento ufficiale di avanzamento e censimento dei 35 task (v3.1)
│   └── piano_operativo.md                         # Roadmap operativa di sviluppo a milestones (M0-M12) e track tematiche
├── tests/                                         # Suite di test automatizzati (130 test unitari e di regressione)
│   ├── __init__.py
│   ├── test_qa_baseline.py                        # Test di regressione baseline, specularità e validazione casi
│   ├── test_export_limesurvey.py                  # Test del parser ed esportatore LimeSurvey TSV a 14 colonne
│   ├── test_survey_knowledge.py                   # Test dei moduli knowledge base ed estrattore storico
│   ├── test_interviewer_guide.py                  # Test del generatore guida intervistatore e note di regia
│   └── test_agcom_report.py                       # Test del calcolo statistico e generatore Scheda AGCOM
├── examples/                                      # Fixture di test, benchmark e caso di studio end-to-end
│   ├── brief_demo.md                              # Brief fittizio sintetico di prova
│   ├── questionario_demo.md                       # Questionario fittizio grezzo di prova
│   ├── confronto_modelli.csv                      # Tracciato tabellare per benchmark sperimentale tra LLM
│   └── demo_run_biblioteca/                       # Caso end-to-end completo e validato di riferimento
│       ├── brief.md                               # Brief strutturato del caso biblioteca
│       ├── questionnaire.md                       # Bozza di questionario con codici 97/98/99
│       ├── methodology.md                         # Audit metodologico item-per-item con 3 opzioni
│       ├── compliance.md                          # Screening preliminare privacy e AI Act
│       ├── final.md                               # Questionario consolidato definitivo
│       ├── status.md                              # Registro decisioni umane e avanzamento fasi
│       ├── limesurvey_survey.txt                  # Struttura TSV a 14 colonne per LimeSurvey
│       ├── guida_intervistatore.md                # Guida di somministrazione con note di regia
│       └── scheda_agcom.md                        # Scheda Informativa AGCOM con calcolo margine d'errore
└── runs/                                          # Cartelle dei singoli casi operativi (escluse dal controllo di versione)
```

---

## 3. Architettura Multi-Agente, Competenze e Tooling

Il sistema adotta la separazione netta tra **supervisione/orchestrazione** (`ai-coordinator`) ed **esecuzione specialistica** (subagent specializzati per dominio). A ogni passaggio critico, il supervisore si arresta e interroga il ricercatore umano in chat (**STOP Gate**), registrando puntualmente la decisione in `runs/<caso>/status.md`.

### 3.1 I 7 Agenti Speculari (`.agents/agents/` e `.claude/agents/`)

Ciascun agente dispone di un contratto operativo formalizzato (Ruolo, Competenze, Contratto I/O, Procedura passo-passo e Checklist di autoverifica):

| Agente | Google Antigravity | Claude Code | Stato | Ruolo, Responsabilità e Artefatti Gestiti |
| :--- | :--- | :--- | :---: | :--- |
| **`ai-coordinator`** | [`.agents/agents/ai-coordinator.md`](.agents/agents/ai-coordinator.md) | [`.claude/agents/ai-coordinator.md`](.claude/agents/ai-coordinator.md) | **Attivo** | **Supervisore e Orchestratore (Main Agent)**: inizializza il caso, aggiorna `runs/<caso>/status.md`, delega una fase alla volta, verifica la conformità ai template e gestisce i gate decisionali in chat. Non redige direttamente gli artefatti specialistici. |
| **`questionnaire-agent`** | [`.agents/agents/questionnaire-agent.md`](.agents/agents/questionnaire-agent.md) | [`.claude/agents/questionnaire-agent.md`](.claude/agents/questionnaire-agent.md) | **Attivo** | **Specialista Questionario ed Estrazione**: redige `brief.md`, `questionnaire.md`, consolida `final.md` ed estrae formulari storici (`extracted_survey.md`). Garantisce codici standard `97/98/99`, istruzioni di regia e continuità delle serie storiche. |
| **`methodology-agent`** | [`.agents/agents/methodology-agent.md`](.agents/agents/methodology-agent.md) | [`.claude/agents/methodology-agent.md`](.claude/agents/methodology-agent.md) | **Attivo** | **Revisore Metodologico**: esegue l'audit metodologico item-per-item in `methodology.md` con griglia a 11 colonne e schede analitiche a 12 campi, fornendo per ciascun quesito tre alternative (*Opzione A: Conservare*, *Opzione B: Modifica minima*, *Opzione C: Revisione sostanziale*). |
| **`compliance-agent`** | [`.agents/agents/compliance-agent.md`](.agents/agents/compliance-agent.md) | [`.claude/agents/compliance-agent.md`](.claude/agents/compliance-agent.md) | **Attivo** | **Revisore Preliminare Privacy & AI Act**: esegue lo screening preliminare GDPR (Art. 9 per orientamento politico) e governance AI Act in `compliance.md`, segnalando cautele e punti bloccanti da sottoporre a DPO o legale umano. |
| **`reporting-agent`** | [`.agents/agents/reporting-agent.md`](.agents/agents/reporting-agent.md) | [`.claude/agents/reporting-agent.md`](.claude/agents/reporting-agent.md) | **Attivo** | **Specialista Reporting Regolamentare e Scheda AGCOM**: redige e convalida la Scheda Informativa obbligatoria ex art. 5 Delibera AGCOM 256/10/CSP in `scheda_agcom.md`, calcola il margine d'errore teorico al 95% di confidenza e assicura la marcatura di `[DA VERIFICARE SUL CAMPO]`. |
| **`analysis-agent`** | [`.agents/agents/analysis-agent.md`](.agents/agents/analysis-agent.md) | [`.claude/agents/analysis-agent.md`](.claude/agents/analysis-agent.md) | *In attesa* | *In attesa di attivazione (Modulo B post-fieldwork)*: verifica dati grezzi raccolti, pesatura campionaria complessa (IPF / rim weighting) e statistiche descrittive riproducibili su piano approvato. |
| **`dashboard-agent`** | [`.agents/agents/dashboard-agent.md`](.agents/agents/dashboard-agent.md) | [`.claude/agents/dashboard-agent.md`](.claude/agents/dashboard-agent.md) | *In attesa* | *In attesa di attivazione (Modulo B post-fieldwork)*: progettazione di layout descrittivi e specifiche per grafici con metadati completi (base, denominatore, note metodologiche). |

---

### 3.2 Le 8 Skill Speculari (`.agents/skills/` e `.claude/skills/`)

Le skill rappresentano procedure operative invocabili sia dagli agenti durante i workflow sia direttamente dal ricercatore:

| Skill | Google Antigravity | Claude Code | Agente Associato | Template / Artefatti Generati | Funzione Operativa |
| :--- | :--- | :--- | :---: | :--- | :--- |
| **`noto-survey-pipeline`** | [`.agents/skills/noto-survey-pipeline/SKILL.md`](.agents/skills/noto-survey-pipeline/SKILL.md) | [`.claude/skills/noto-survey-pipeline/SKILL.md`](.claude/skills/noto-survey-pipeline/SKILL.md) | `ai-coordinator` | [`templates/status_template.md`](templates/status_template.md)<br>-> `runs/<caso>/status.md` | Inizializzazione della cartella del caso, coordinamento delle fasi e gestione dei gate decisionali in chat. |
| **`noto-brief-structuring`** | [`.agents/skills/noto-brief-structuring/SKILL.md`](.agents/skills/noto-brief-structuring/SKILL.md) | [`.claude/skills/noto-brief-structuring/SKILL.md`](.claude/skills/noto-brief-structuring/SKILL.md) | `questionnaire-agent` | [`templates/brief_template.md`](templates/brief_template.md)<br>-> `runs/<caso>/brief.md` | Analisi dei documenti di partenza in `runs/<caso>/source/`, rilevazione delle lacune e stesura del brief strutturato. |
| **`noto-questionnaire-drafting`** | [`.agents/skills/noto-questionnaire-drafting/SKILL.md`](.agents/skills/noto-questionnaire-drafting/SKILL.md) | [`.claude/skills/noto-questionnaire-drafting/SKILL.md`](.claude/skills/noto-questionnaire-drafting/SKILL.md) | `questionnaire-agent` | [`templates/questionnaire_template.md`](templates/questionnaire_template.md)<br>-> `runs/<caso>/questionnaire.md` | Progettazione della bozza del questionario con codici `97/98/99`, sezioni, filtri di salto e note di regia. |
| **`noto-methodology-audit`** | [`.agents/skills/noto-methodology-audit/SKILL.md`](.agents/skills/noto-methodology-audit/SKILL.md) | [`.claude/skills/noto-methodology-audit/SKILL.md`](.claude/skills/noto-methodology-audit/SKILL.md) | `methodology-agent` | [`templates/methodology_template.md`](templates/methodology_template.md)<br>-> `runs/<caso>/methodology.md` | Audit metodologico item-per-item, diagnosi cognitiva dei rischi e proposta delle 3 alternative operative per quesito. |
| **`noto-compliance-check`** | [`.agents/skills/noto-compliance-check/SKILL.md`](.agents/skills/noto-compliance-check/SKILL.md) | [`.claude/skills/noto-compliance-check/SKILL.md`](.claude/skills/noto-compliance-check/SKILL.md) | `compliance-agent` | [`templates/compliance_template.md`](templates/compliance_template.md)<br>-> `runs/<caso>/compliance.md` | Screening preliminare privacy (GDPR Art. 9, identificazione indiretta) e governance AI Act con tabella quesito per quesito. |
| **`noto-questionnaire-consolidation`** | [`.agents/skills/noto-questionnaire-consolidation/SKILL.md`](.agents/skills/noto-questionnaire-consolidation/SKILL.md) | [`.claude/skills/noto-questionnaire-consolidation/SKILL.md`](.claude/skills/noto-questionnaire-consolidation/SKILL.md) | `questionnaire-agent` | [`templates/final_template.md`](templates/final_template.md)<br>-> `runs/<caso>/final.md`<br>`runs/<caso>/limesurvey_survey.txt` | Consolidamento finale delle sole modifiche approvate ed esportazione automatica della struttura LimeSurvey TSV a 14 colonne. |
| **`noto-survey-extractor`** | [`.agents/skills/noto-survey-extractor/SKILL.md`](.agents/skills/noto-survey-extractor/SKILL.md) | [`.claude/skills/noto-survey-extractor/SKILL.md`](.claude/skills/noto-survey-extractor/SKILL.md) | `questionnaire-agent` | [`templates/extracted_survey_template.md`](templates/extracted_survey_template.md)<br>-> `knowledge/extracted_*.md` | Estrazione e normalizzazione di formulari, batterie e scale da questionari e report storici (PDF/DOCX/TXT/MD). |
| **`noto-agcom-reporting`** | [`.agents/skills/noto-agcom-reporting/SKILL.md`](.agents/skills/noto-agcom-reporting/SKILL.md) | [`.claude/skills/noto-agcom-reporting/SKILL.md`](.claude/skills/noto-agcom-reporting/SKILL.md) | `reporting-agent` | [`templates/agcom_template.md`](templates/agcom_template.md)<br>-> `runs/<caso>/scheda_agcom.md` | Redazione e validazione della Scheda Informativa obbligatoria del sondaggio ex art. 5 Delibera AGCOM 256/10/CSP con calcolo margine d'errore. |

---

### 3.3 I 3 Workflow e Comandi Slash Speculari

I flussi multi-fase sono attivabili tramite comando `/` in Claude Code o guidati da `ai-coordinator` in Google Antigravity:

| Workflow / Comando | Percorso Antigravity | Percorso Claude Code | Sequenza Operativa delle Fasi | Scenario di Utilizzo |
| :--- | :--- | :--- | :--- | :--- |
| **`/nuova-indagine`** | [`.agents/workflows/nuova-indagine.md`](.agents/workflows/nuova-indagine.md) | [`.claude/commands/nuova-indagine.md`](.claude/commands/nuova-indagine.md) | `brief -> questionnaire -> methodology -> compliance -> final` | Avvio di una nuova indagine a partire da appunti cliente, brief sintetico o trascrizione di riunione. |
| **`/revisione-questionario`** | [`.agents/workflows/revisione-questionario.md`](.agents/workflows/revisione-questionario.md) | [`.claude/commands/revisione-questionario.md`](.claude/commands/revisione-questionario.md) | `methodology -> compliance -> final` | Audit metodologico e screening normativo di un questionario già redatto o pregresso caricato in `source/`. |
| **`/audit-singolo`** | [`.agents/workflows/audit-singolo.md`](.agents/workflows/audit-singolo.md) | [`.claude/commands/audit-singolo.md`](.claude/commands/audit-singolo.md) | `methodology` *oppure* `compliance` | Esecuzione mirata e rapida del solo audit metodologico o del solo screening di conformità su un documento. |

---

### 3.4 Gli 8 Template Strutturati Obbligatori (`templates/`)

Ogni documento prodotto nella cartella `runs/<caso>/` o nella base di conoscenza deve seguire rigorosamente la struttura del relativo template:

| Template | Artefatto Target Generato | Agente Responsabile | Skill Associata | Sezioni Obbligatorie del Template |
| :--- | :--- | :--- | :--- | :--- |
| [`templates/status_template.md`](templates/status_template.md) | `runs/<caso>/status.md` | `ai-coordinator` | `noto-survey-pipeline` | Metadati del caso, tabella avanzamento delle 5 fasi del Modulo A, registro cronologico delle decisioni umane in chat, blocchi pre-campo. |
| [`templates/brief_template.md`](templates/brief_template.md) | `runs/<caso>/brief.md` | `questionnaire-agent` | `noto-brief-structuring` | Inquadramento e fonti (`[DA VERIFICARE]`), obiettivi cognitivi, disegno di campionamento proposto o `DA DEFINIRE`, vincoli e quesiti per il committente. |
| [`templates/questionnaire_template.md`](templates/questionnaire_template.md) | `runs/<caso>/questionnaire.md` | `questionnaire-agent` | `noto-questionnaire-drafting` | Metadati indagine, testo introduttivo, articolazione quesiti con codici `97/98/99`, istruzioni di regia (`[NON LEGGERE / ROTAZIONE]`), filtri di salto condizionale. |
| [`templates/methodology_template.md`](templates/methodology_template.md) | `runs/<caso>/methodology.md` | `methodology-agent` | `noto-methodology-audit` | Metodo e limiti, griglia sintetica a 11 colonne, schede analitiche a 12 campi con 3 alternative operative (*Opzione A, B, C*), piano *pretest/pilot*. |
| [`templates/compliance_template.md`](templates/compliance_template.md) | `runs/<caso>/compliance.md` | `compliance-agent` | `noto-compliance-check` | Perimetro dati personali, griglia screening quesito per quesito (Art. 9 GDPR, re-identificazione, opzione rifiuto), checklist AI Act, prescrizioni DPO. |
| [`templates/final_template.md`](templates/final_template.md) | `runs/<caso>/final.md` | `questionnaire-agent` | `noto-questionnaire-consolidation` | Metadati di consolidamento, registro delle modifiche approvate/scartate, prescrizioni compliance recepite, testo definitivo dei quesiti con note di regia e mappa filtri. |
| [`templates/extracted_survey_template.md`](templates/extracted_survey_template.md) | `knowledge/extracted_*.md`<br>`runs/<caso>/extracted_survey.md` | `questionnaire-agent` | `noto-survey-extractor` | Metadati studio storico, inventario strutturato delle domande con codici originali, costrutti, formulazioni esatte, scale e opzioni con codici standard `97/98/99`, note serie storiche. |
| [`templates/agcom_template.md`](templates/agcom_template.md) | `runs/<caso>/scheda_agcom.md` | `reporting-agent` | `noto-agcom-reporting` | Scheda informativa obbligatoria ex art. 5 Delibera AGCOM 256/10/CSP: soggetto realizzatore, committente, popolazione, campione e tassi con `[DA VERIFICARE SUL CAMPO]`, margine d'errore al 95%, testo integrale quesiti. |

---

### 3.5 Tooling CLI e Script di Automazione (`scripts/`)

La piattaforma mette a disposizione 6 strumenti a riga di comando per validazione, esportazione e calcolo statistico:

| CLI Tool | Descrizione Funzionale | Argomenti Principali | Esempio Rapido d'Uso |
| :--- | :--- | :--- | :--- |
| [`scripts/check_mirror_sync.py`](scripts/check_mirror_sync.py) | Validatore di specularità tra Antigravity (`.agents/`) e Claude (`.claude/`) | Nessuno | `python scripts/check_mirror_sync.py` |
| [`scripts/validate_runs.py`](scripts/validate_runs.py) | Linter metodologico e strutturale per i casi in `runs/` o `examples/` | `[<cartella_o_file>] [-h/--help]` | `python scripts/validate_runs.py examples/demo_run_biblioteca` |
| [`scripts/export_limesurvey.py`](scripts/export_limesurvey.py) | Parser ed esportatore del questionario consolidato in formato LimeSurvey TSV (14 colonne standard) | `<questionario_md> [-o out.txt] [-l/--lang it]` | `python scripts/export_limesurvey.py examples/demo_run_biblioteca/final.md` |
| [`scripts/extract_survey_knowledge.py`](scripts/extract_survey_knowledge.py) | Estrattore automatico di formulari storici e batterie da file di testo/markdown/docx/pdf | `<input_file> [-o out.md] [--title/--id-studio Titolo] [-f md\|json]` | `python scripts/extract_survey_knowledge.py input_storico.md -o knowledge/estratto.md` |
| [`scripts/generate_interviewer_guide.py`](scripts/generate_interviewer_guide.py) | Generatore guida per intervistatori CATI/CAPI con note di regia tipografiche | `<questionario_md> [-o out] [-f/--format md\|html\|docx\|both\|all]` | `python scripts/generate_interviewer_guide.py examples/demo_run_biblioteca/final.md --format all` |
| [`scripts/generate_agcom_report.py`](scripts/generate_agcom_report.py) | Generatore Scheda Informativa AGCOM con calcolo margine d'errore (Delibera 256/10/CSP) | `[case_dir] [-n/--campione N] [--popolazione N] [--check-only]` | `python scripts/generate_agcom_report.py examples/demo_run_biblioteca --campione 1000 --popolazione 50000000` |

#### Esempi di Invocazione da Terminale

```bash
# 1. Verifica sincronizzazione architetturale
python scripts/check_mirror_sync.py

# 2. Validazione di conformità metodologica di un caso
python scripts/validate_runs.py examples/demo_run_biblioteca

# 3. Esportazione struttura LimeSurvey TSV a 14 colonne
python scripts/export_limesurvey.py examples/demo_run_biblioteca/final.md -o runs/mio_caso/limesurvey_survey.txt

# 4. Generazione guida per intervistatore in Markdown, HTML e Word (.docx)
python scripts/generate_interviewer_guide.py examples/demo_run_biblioteca/final.md --format all

# 5. Generazione automatica Scheda AGCOM con calcolo del margine d'errore teorico al 95%
python scripts/generate_agcom_report.py examples/demo_run_biblioteca --campione 1000 --popolazione 50000000
```

> 💡 **Nota tecnica su Windows**: in presenza di percorsi con spazi o caratteri accentati (es. cartelle istituzionali OneDrive), racchiudere sempre i percorsi tra virgolette doppie (`"..."`).

---

### 3.6 Moduli della Knowledge Base Canonica (`knowledge/`)

Per garantire uniformità campionaria e comparabilità temporale, la piattaforma include standard demografici ed elettorali di riferimento:
- [`knowledge/demographics_standard.json`](knowledge/demographics_standard.json): batterie socio-demografiche conformi agli standard Istat ed Eurostat (Genere, Fasce d'età con aggregazioni a 4 e 6 classi, Titolo di studio Isced, Condizione professionale a 9 voci, Ampiezza demografica del comune di residenza e Ripartizione geografica Istat a 5 macro-aree);
- [`knowledge/political_batteries_core.json`](knowledge/political_batteries_core.json): formulazioni e scale canoniche per indagini demoscopiche e politiche (Fiducia nelle istituzioni e nei leader su scala 1-10 o a 4 livelli, Indice di gradimento del Governo, Intenzione di voto con lista partiti e codici `98=Indeciso / Non so` e `99=Scheda bianca / Rifiuta`, e Scala di auto-collocazione politica sinistra-destra a 10 punti).

---

### 3.7 Suite di Test Unitari e Regressione (`tests/`)

La piattaforma dispone di una suite di test automatici articolata su 5 moduli specialistici:
- [`tests/test_qa_baseline.py`](tests/test_qa_baseline.py): verifica della sincronizzazione architetturale, presenza dei file chiave e conformità della fixture demo;
- [`tests/test_export_limesurvey.py`](tests/test_export_limesurvey.py): collaudo del parser TSV a 14 colonne, gestione codici opzione (`A`), domande (`Q`) e sottodomande (`SQ`);
- [`tests/test_survey_knowledge.py`](tests/test_survey_knowledge.py): validazione della consistenza JSON dei moduli demografici ed elettorali e testing dell'estrattore storico;
- [`tests/test_interviewer_guide.py`](tests/test_interviewer_guide.py): collaudo del rendering delle note di regia, intro/outro, filtri e fallback HTML/Markdown;
- [`tests/test_agcom_report.py`](tests/test_agcom_report.py): collaudo del calcolo statistico del margine d'errore gaussiano al 95% di confidenza e della conformità alla Delibera AGCOM 256/10/CSP.

```bash
# Esecuzione dell'intera suite di test (130 test unitari)
python -m unittest discover tests/
```

---

## 4. Guida Rapida all'Uso e Scenari Operativi

Per le istruzioni dettagliate di installazione passo-passo, consultare il [**Manuale di Installazione e Avvio**](docs/manuale_installazione.md).

### Apertura dell'Ambiente
- **Google Antigravity**: aprire la cartella principale del repository come Workspace. Antigravity caricherà automaticamente le regole di [AGENTS.md](AGENTS.md), gli agenti in `.agents/agents/`, le skill in `.agents/skills/` e i flussi in `.agents/workflows/`.
- **Claude Code**: aprire il terminale o il plugin IDE nella root del repository. Claude Code caricherà automaticamente [CLAUDE.md](CLAUDE.md), i subagent in `.claude/agents/`, le skill in `.claude/skills/` e i comandi slash in `.claude/commands/`.

---

### Scenario A — Avvio di una Nuova Indagine (`/nuova-indagine`)

Sequenza guidata: `brief -> questionnaire -> methodology -> compliance -> final`

1. Copiare i documenti di partenza (appunti cliente, note, trascrizioni autorizzate) in `examples/` o direttamente in `runs/<nome_caso>/source/`;
2. Scrivere in chat al supervisore `ai-coordinator`:
   > `Avvia il workflow /nuova-indagine per il caso "comunali-milano" usando come input source/appunti_brief.md. Esegui la prima fase (brief) e fermati per la mia approvazione.`
3. `ai-coordinator` crea `runs/comunali-milano/`, inizializza `runs/comunali-milano/status.md` e incarica `questionnaire-agent` di redigere `runs/comunali-milano/brief.md` secondo `templates/brief_template.md`;
4. **STOP Gate (Approvazione Umana)**: esaminare `brief.md` e rispondere direttamente in chat:
   > `Approvo il brief (revisore: Adelaide). Per la somministrazione confermo modalità mista CATI/CAWI, 12 quesiti totali, target popolazione maggiorenne residente. Procedi con la fase questionnaire.`
5. `ai-coordinator` registra la decisione in `status.md` e passa alla fase successiva (`questionnaire`), ripetendo il ciclo di verifica e approvazione fino alla generazione del questionario consolidato `final.md`.

---

### Scenario B — Revisione di un Questionario Esistente (`/revisione-questionario`)

Sequenza guidata: `methodology -> compliance -> final`

1. Inserire il questionario già predisposto in `runs/<nome_caso>/source/questionario_grezzo.md`;
2. Richiedere l'avvio della revisione in chat:
   > `Avvia il workflow /revisione-questionario per il caso "revisione-trasporti" a partire da source/questionario_grezzo.md.`
3. Il coordinatore salta le fasi di brief e bozza, incaricando direttamente `methodology-agent` di redigere l'audit in `runs/revisione-trasporti/methodology.md`;
4. **STOP Gate**: esaminare la griglia a 11 colonne e indicare in chat le decisioni sui singoli quesiti:
   > `Approvo l'audit metodologico. Su Q1 accetto l'Opzione B (modifica minima della polarità); su Q2 confermo l'Opzione A (mantenimento formulazione originale per serie storica); su Q3 accetto l'Opzione C (scorporo della doppia domanda). Procedi con compliance.`
5. Proseguire con lo screening normativo in `compliance.md` e con il consolidamento finale in `final.md`.

---

### Scenario C — Audit Singolo o Esecuzione Mirata di una Skill (`/audit-singolo`)

È possibile invocare controlli specifici o singole skill specialistiche:
- `/audit-singolo` — per eseguire unicamente la revisione metodologica oppure lo screening privacy su un testo;
- `/noto-survey-extractor` — per normalizzare un documento pregresso e alimentare la knowledge base;
- `/noto-agcom-reporting` — per redigere o convalidare la Scheda Informativa AGCOM per un'indagine pronta alla diffusione.

---

### Scenario D — Bridge Operativi di Fieldwork (LimeSurvey, Intervistatore, AGCOM)

Al termine del consolidamento di un'indagine in `final.md`, è possibile generare tutti i supporti tecnici:
1. **Esportazione LimeSurvey**: eseguire `python scripts/export_limesurvey.py runs/<caso>/final.md` per produrre `runs/<caso>/limesurvey_survey.txt` pronto per l'importazione diretta come indagine CATI/CAWI;
2. **Guida per Intervistatore**: eseguire `python scripts/generate_interviewer_guide.py runs/<caso>/final.md --format all` per generare la guida di somministrazione con istruzioni di regia evidenziate per gli operatori di call center;
3. **Scheda AGCOM**: eseguire `python scripts/generate_agcom_report.py runs/<caso>` per generare la Scheda Informativa conforme alla Delibera 256/10/CSP con il calcolo del margine d'errore statistico teorico al 95%.

---

## 5. Casi di Studio ed Esempi di Riferimento (`examples/`)

La cartella [`examples/`](examples/) fornisce fixture di prova e casi completi per sperimentazione, addestramento e validazione:

- [`examples/demo_run_biblioteca/`](examples/demo_run_biblioteca/): **Caso completo end-to-end certificato e validato** relativo a un'indagine sui servizi bibliotecari civici e culturali. Contiene tutti gli artefatti previsti dal ciclo di ricerca:
  - [`status.md`](examples/demo_run_biblioteca/status.md): registro completo dell'avanzamento delle 5 fasi e delle approvazioni umane;
  - [`brief.md`](examples/demo_run_biblioteca/brief.md): brief strutturato con inquadramento, target e quesiti aperti;
  - [`questionnaire.md`](examples/demo_run_biblioteca/questionnaire.md): prima bozza strutturata con codici `97/98/99` e note di regia;
  - [`methodology.md`](examples/demo_run_biblioteca/methodology.md): audit metodologico completo con griglia a 11 colonne e schede analitiche a 12 campi (opzioni A, B, C);
  - [`compliance.md`](examples/demo_run_biblioteca/compliance.md): screening privacy preliminare GDPR Art. 9 e governance AI Act;
  - [`final.md`](examples/demo_run_biblioteca/final.md): questionario consolidato definitivo conforme alle scelte del ricercatore;
  - [`limesurvey_survey.txt`](examples/demo_run_biblioteca/limesurvey_survey.txt): file TSV nativo a 14 colonne per LimeSurvey;
  - [`guida_intervistatore.md`](examples/demo_run_biblioteca/guida_intervistatore.md): guida per rilevatori telefonici e sul campo;
  - [`scheda_agcom.md`](examples/demo_run_biblioteca/scheda_agcom.md): scheda di diffusione conforme alla Delibera AGCOM 256/10/CSP.
- [`examples/confronto_modelli.csv`](examples/confronto_modelli.csv): tracciato standard per benchmark comparativi tra diversi modelli LLM a parità di prompt e caso di test;
- [`examples/brief_demo.md`](examples/brief_demo.md) e [`examples/questionario_demo.md`](examples/questionario_demo.md): materiali sintetici di test per l'avvio immediato di prove pilota.

---

## 6. Deontologia Scientifica, Tassonomia della Non Risposta e Vincoli Metodologici

La piattaforma è progettata secondo rigorosi canoni epistemologici e deontologici:

### 6.1 Principio Human-in-the-Loop Tassativo
Gli agenti operano esclusivamente come assistenti tecnici per la formulazione di bozze e audit preliminari. Nessuna proposta generata dall'AI costituisce decisione finale di ricerca, autorizzazione alla somministrazione o perizia legale asseverata.

### 6.2 Divieto Assoluto di Rispondenti Sintetici
È fatto divieto categorico di simulare rispondenti sintetici o generare risposte artificiali con LLM per sostituire o integrare campioni empirici reali. Le stime demoscopiche devono basarsi esclusivamente su rilevazioni empiriche validate sul campo.

### 6.3 Tassonomia Rigorosa a 6 Codici della Non Risposta
Il sistema applica sistematicamente la distinzione metodologica tra le differenti nature della non risposta:
1. **Mancato contatto / Rifiuto totale** (*Unit nonresponse*);
2. **Mancata risposta al singolo quesito** (*Item nonresponse*);
3. **Rifiuto esplicito alla risposta** (`Codice 99: Preferisco non rispondere / Rifiuta`);
4. **Autentica non conoscenza o assenza di opinione** (`Codice 98: Non so / Senza opinione`);
5. **Non applicabilità per filtro di eleggibilità** (`Codice 97: Non applicabile`);
6. **Abbandono nel corso dell'intervista** (*Break-off*).

È severamente vietato eliminare arbitrariamente le opzioni di uscita per ridurre fittiziamente la quota di mancata risposta.

### 6.4 Tutela delle Serie Storiche e Comparabilità Longitudinale
Qualsiasi proposta di riformulazione testuale deve documentare l'impatto potenziale sulla comparabilità longitudinale. Le domande storiche calibrate non devono essere alterate tacitamente nell'oggetto, nella polarità o nella scala di risposta.

### 6.5 Screening di Conformità Normativa (GDPR Art. 9 e AI Act)
Il `compliance-agent` opera un vaglio cautelativo preliminare:
- Rileva la presenza di dati ex Art. 9 GDPR (in particolare orientamenti politici, sindacali, filosofici o religiosi) che richiedono base giuridica specifica e consenso informato rafforzato;
- Evidenzia combinazioni di quesiti socio-demografici suscettibili di determinare re-identificazione indiretta in campioni ristretti;
- Segnala obbligatoriamente ogni criticità al Data Protection Officer (DPO) aziendale prima della messa in campo.
