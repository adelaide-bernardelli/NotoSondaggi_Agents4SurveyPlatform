# Documento Ufficiale di Avanzamento e Stato del Progetto
## Piattaforma Multi-Agente Human-in-the-Loop per Indagini Demoscopiche — Noto Sondaggi SRL

> **Documento di Avanzamento e Rendicontazione**  
> **Istituzione**: IUSS Pavia  
> **Ph.D Student**: Adelaide Emma Bernardelli  
> **Supervisione Accademica**: Prof.ssa Alessandra Amendola  
> **Committente / Partner Industriale**: Noto Sondaggi SRL  
> **Versione**: 3.1 (Stato Esecuzione Software M0–M8 e Avvio Collaudo Umano H1–H10)  
> **Finalità**: Rendicontare in modo analitico lo stato di avanzamento della piattaforma multi-agente, censire esaustivamente i 35 task di sviluppo, certificare il completamento dell'implementazione software delle prime 9 milestone (M0–M8) e dei 19 task correlati attualmente in fase di collaudo umano (Protocolli H1–H10 di [`docs/piano_test_umani.md`](piano_test_umani.md)), formalizzare la sospensione operativa al Gate di Stop per l'allineamento con Noto Sondaggi SRL e DPO prima delle milestone M9–M12 e documentare l'apparato di validazione tecnica e metodologica implementato nel repository.

---

## 1. Executive Summary per la Supervisione Accademica

### 1.1 Risultati Raggiunti in Piena Autonomia dal Team Universitario
Il team di ricerca ha completato e validato l'intera architettura portante del **Modulo A (Progettazione, Revisione Metodologica, Screening Privacy e Consolidamento del Questionario)** e le componenti a sviluppo autonomo del **Modulo B (Reporting Regolamentare AGCOM)** e del **Fieldwork Bridge (Esportatore LimeSurvey TSV e Guida Intervistatore CATI/CAPI)**. Il sistema è stato ingegnerizzato secondo il principio della **doppia specularità integrale** per operare indistintamente e con parità funzionale su due ambienti AI di riferimento: **Google Antigravity** (`.agents/`, [`AGENTS.md`](../AGENTS.md)) e **Claude Code** (`.claude/`, [`CLAUDE.md`](../CLAUDE.md)).

Nello specifico, sono stati realizzati, testati e verificati nel codice:
1. **Regole Fondamentali di Governance e Deontologia Metodologica (Task #01)**: Perimetro strettamente *human-in-the-loop*, divieto categorico di generare rispondenti sintetici per sostituire dati empirici reali, neutralità scientifica (divieto di profilazione politica o persuasione), tutela rigorosa della tassonomia di non risposta (*unit nonresponse*, *item nonresponse*, rifiuto esplicito `99`, autentico non so `98`, non applicabile `97`, break-off) e salvaguardia della comparabilità delle serie storiche.
2. **Orchestrazione Multi-Agente con Separazione dei Ruoli (Task #02, #03, #04, #16)**: Main Agent supervisore (`ai-coordinator`) e 4 Agenti specialistici attivi (`questionnaire-agent`, `methodology-agent`, `compliance-agent`, `reporting-agent`), con protocollo di stop obbligatorio e approvazione umana in chat ad ogni singolo gate registrato in `runs/<caso>/status.md`.
3. **8 Template Strutturati Obbligatori**: Contratti di output standardizzati ([`templates/status_template.md`], [`templates/brief_template.md`], [`templates/questionnaire_template.md`], [`templates/methodology_template.md`] con griglia a 11 colonne e schede a 12 campi per opzioni A/B/C, [`templates/compliance_template.md`], [`templates/final_template.md`], [`templates/extracted_survey_template.md`], [`templates/agcom_template.md`]).
4. **Tooling di Automazione CLI, Esportazione e QA Interno (6 CLI Operative)**:
   - [`scripts/check_mirror_sync.py`] (Task #16): validatore automatico della sincronizzazione speculare tra `.agents/` e `.claude/` (eseguito con successo: 100% allineato su 7 agenti, 8 skill e 8 template);
   - [`scripts/validate_runs.py`] (Task #17): linter formale per la conformità di qualsiasi caso in `runs/<caso>/` o `examples/` rispetto a colonne, campi, codici 97/98/99 e note di regia;
   - [`scripts/export_limesurvey.py`] (Task #26 — Milestone M1, M2): convertitore nativo TSV a 14 colonne per l'importazione diretta in LimeSurvey CATI/CAWI;
   - [`scripts/extract_survey_knowledge.py`] (Task #09, #22 — Milestone M3, M4): tool CLI di estrazione strutturata di formulari e batterie storiche alimentato dai file di knowledge base (`knowledge/demographics_standard.json` e `knowledge/political_batteries_core.json`);
   - [`scripts/generate_interviewer_guide.py`] (Task #27, #12 — Milestone M5, M6): generatore automatico della guida di somministrazione per intervistatori con formattazione tipografica ad alta leggibilità per le note di regia in Markdown, HTML e Word (`.docx`);
   - [`scripts/generate_agcom_report.py`] (Task #33 — Milestone M7, M8): generatore della Scheda Informativa AGCOM obbligatoria ex art. 5 Delibera AGCOM 256/10/CSP con calcolo automatico del margine d'errore campionario teorico al 95% di confidenza.
5. **Fixture Completa e Validata (Task #19)**: [`examples/demo_run_biblioteca/`] recante tutti i 9 artefatti completi di fase (`status.md`, `brief.md`, `questionnaire.md`, `methodology.md`, `compliance.md`, `final.md`, `limesurvey_survey.txt`, `guida_intervistatore.md`, `scheda_agcom.md`).
6. **Piano di Test Umano e Protocolli di Collaudo**: Redazione completa di [`docs/piano_test_umani.md`](piano_test_umani.md) con 10 protocolli operativi di collaudo metodologico e deontologico umano (Protocolli H1 – H10) a presidio del controllo qualitativo dei ricercatori e del DPO.

---

### 1.2 Quadro Operativo Aggiornato e Transizione alla Fase di Collaudo Umano
A seguito del completamento dell'intero blocco di sviluppo autonomo del codice (Milestone **M0 – M8**), il quadro operativo del progetto registra una svolta fondamentale:

1. **Implementazione Software delle Milestone M0–M8 Completata al 100%**:  
   Tutte le funzionalità autonome previste dalla roadmap esecutiva di [`docs/piano_operativo.md`](piano_operativo.md) sono state codificate, corredate da 130 test unitari automatici passati con successo e integrate nella suite operativa.
2. **Attivazione della Fase di Collaudo Metodologico Umano (Protocolli H1–H10)**:  
   I 19 task coperti dallo sviluppo software (#01, #02, #03, #04, #05, #07, #08, #09, #10, #12, #13, #15, #16, #17, #19, #22, #26, #27, #33) sono ora classificati come **`ESEGUITO (SOFTWARE) — IN FASE DI TEST UMANO`**. I ricercatori metodologi e il referente DPO conducono i collaudi qualitativi secondo le procedure operative di [`docs/piano_test_umani.md`](piano_test_umani.md).
3. **Attivazione Formale del Gate di Stop per le Milestone M9–M12**:  
   Lo sviluppo del codice è formalmente sospeso (**🛑 STOP Gate**) in attesa della sessione di allineamento e riscontro tecnico con **Noto Sondaggi SRL** e il rispettivo referente DPO. I 7 task subordinati a tale allineamento (#06, #08, #11, #12, #14, #23, #24, #25) e le relative milestone post-feedback (M9, M10, M11, M12) rimangono in attesa per evitare derive o assunzioni arbitrarie.
4. **Focalizzazione del Modulo B e Differimento della Pesatura Complessa IPF**:  
   Confermata la scelta strategica di differire a fasi successive la complessità matematica della post-stratificazione IPF/Raking multivariata (Task #30, #31, #32), focalizzando il Modulo B sulla Scheda AGCOM (completata in M7/M8) e sull'analisi descrittiva.

---

### 1.3 Sintesi Statistica Rigorosa dei 35 Task del Progetto
A valle della transizione operativa, la distribuzione dei 35 task del progetto evidenzia che **oltre la metà dei requisiti (54.3%) è già stata implementata nel software e si trova in fase di test umano**, il **20.0%** è subordinato al riscontro del Gate di Stop con Noto Sondaggi & DPO, e il restante **25.7%** è programmato per estensioni avanzate post-v1.0.0 o Modulo B:

| Stato di Sviluppo & Test Attuale | N. Task | Quota % | Significato Operativo |
| :--- | :---: | :---: | :--- |
| **`ESEGUITO — IN TEST UMANO`** | **19** | **54.3%** | Software implementato, test unitari superati; in collaudo metodologico/deontologico umano (Protocolli H1–H10) |
| **`IN ATTESA (GATE DI STOP)`** | **7** | **20.0%** | Requisiti in attesa della sessione di allineamento con Noto Sondaggi SRL e riscontro del DPO |
| **`DIFFERITO (MODULO B / INFRA)`** | **9** | **25.7%** | Funzionalità avanzate posticipate (CI post v1.0.0 #18, benchmark multi-modello #21, pacchetto pesatura IPF #30–#32, layout brand #35, analysis/dashboard avanzati #28, #29, #34) |
| **TOTALE** | **35** | **100.0%** | **Quadratura statistica perfetta su tutti i 35 task di progetto** |

| Condizione Operativa & Dipendenza da Noto Sondaggi | N. Task | Quota % | Implicazione Operativa |
| :--- | :---: | :---: | :--- |
| **`ESEGUITO — IN FASE DI TEST UMANO (H1–H10)`** | **19** | **54.3%** | Autonomia totale del team completata; validazione qualitativa in corso secondo [`docs/piano_test_umani.md`](piano_test_umani.md) |
| **In attesa di incontro/allineamento con Noto Sondaggi SRL** | **4** | **11.4%** | Riscontro canali CATI/CAWI, standard classi anagrafiche, committenze e formato consegna intervistatori (#06, #11, #24, #25) |
| **In attesa di dati/batterie storiche o riscontro DPO da Noto** | **3** | **8.6%** | Prescrizioni DPO su Art. 9 GDPR e questionari storici per test indagine reale M11 (#14, #20, #23) |
| **Differito a fasi successive (Modulo B avanzato / CI)** | **9** | **25.7%** | Attività differite a fasi avanzate del Modulo B o all'infrastruttura post-rilascio (#18, #21, #28, #29, #30, #31, #32, #34, #35) |
| **TOTALE** | **35** | **100.0%** | **Quadratura statistica perfetta su tutti i 35 task di progetto** |

---

## 2. Master Table dei 35 Task Ordinati per il Completamento del Progetto

La tabella seguente censisce analiticamente tutti i 35 task del progetto, aggiornati con lo stato di implementazione software, l'avvio della fase di test umano tramite i protocolli H1–H10 di [`docs/piano_test_umani.md`](piano_test_umani.md), il vincolo del Gate di Stop per l'allineamento con Noto Sondaggi SRL & DPO e la rigorosa quadratura statistica.

### Legenda delle Colonne:
1. **#**: Progressivo numerico ordinato (da #01 a #35).
2. **Fase / Macro-Area**: Ambito strutturale di appartenenza.
3. **Task / Oggetto Operativo**: Componente tecnico o metodologico specifico.
4. **Stato di Sviluppo & Test**:
   - `ESEGUITO — IN TEST UMANO`: Software implementato e testato; in fase di collaudo umano qualitativo (Protocolli H1–H10).
   - `IN ATTESA (GATE DI STOP)`: Subordinato alla sessione di allineamento con Noto Sondaggi SRL o al parere del DPO.
   - `DIFFERITO`: Posticipato a fasi avanzate del Modulo B (pesatura IPF) o all'infrastruttura post-v1.0.0.
5. **Condizione Operativa & Dipendenza da Noto Sondaggi**:
   - `IN FASE DI TEST UMANO`: Autonomia totale completata; verifica qualitativa in corso.
   - `In attesa di allineamento con Noto Sondaggi SRL`: Richiede confronto operativo al Gate di Stop.
   - `In attesa di interlocuzione con DPO Noto`: Richiede validazione legale/DPO su Art. 9 GDPR.
   - `È da rivedere più avanti`: Programmato per rilasci successivi.
6. **Dettaglio Operativo e Protocollo di Collaudo**: Diagnosi tecnica puntuale e protocollo di test umano associato.

---

### Tabella Generale dei 35 Task Ordinati

|   #    | Fase / Macro-Area                         | Task / Oggetto Operativo                                                                        |   Stato di Sviluppo & Test   | Condizione Operativa & Dipendenza da Noto Sondaggi                 | Dettaglio Operativo e Protocollo di Collaudo |
| :----: | :---------------------------------------- | :---------------------------------------------------------------------------------------------- | :-------------------: | :----------------------------------------------------------------- | :----------------------------------------- |
| **01** | **Fase 0 — Governance**                   | Regole deontologiche, divieto rispondenti sintetici, etica GDPR/AI Act                          | `ESEGUITO — IN TEST UMANO` | `IN FASE DI TEST UMANO` | Codificato in `AGENTS.md` e `CLAUDE.md`. Sottoposto a collaudo metodologico e deontologico umano (Protocollo H10). |
| **02** | **Fase 0 — Architettura**                 | Struttura speculare duale Google Antigravity (`.agents/`) e Claude Code (`.claude/`)            | `ESEGUITO — IN TEST UMANO` | `IN FASE DI TEST UMANO` | Sincronizzazione speculare al 100% verificata via `scripts/check_mirror_sync.py`; collaudo operativo continuo (Protocollo H10). |
| **03** | **Fase 0 — Architettura**                 | Separazione dei ruoli tra supervisore (`ai-coordinator`) e subagenti operativi                  | `ESEGUITO — IN TEST UMANO` | `IN FASE DI TEST UMANO` | Il supervisore coordina il flusso ma non redige direttamente i documenti; in collaudo di controllo del flusso (Protocollo H10). |
| **04** | **Fase 0 — Human-in-the-Loop**            | Protocollo di approvazione umana in chat e tracciamento in `runs/<caso>/status.md`              | `ESEGUITO — IN TEST UMANO` | `IN FASE DI TEST UMANO` | Definito in `templates/status_template.md` e orchestrato con STOP Gate tassativo; in collaudo umano (Protocollo H10). |
| **05** | **Fase 1 — Modulo A (Brief)**             | Skill `noto-brief-structuring` e template `templates/brief_template.md`                         | `ESEGUITO — IN TEST UMANO` | `IN FASE DI TEST UMANO` | Struttura consolidata (costrutti, target, `[DA VERIFICARE]`); in collaudo metodologico (Protocollo H1; rifinitura committenze M9). |
| **06** | **Fase 1 — Modulo A (Brief)**             | Mappatura delle tipologie di committenza abituali di Noto Sondaggi                              | `IN ATTESA (GATE DI STOP)` | `In attesa di allineamento con Noto Sondaggi SRL` | Mappatura committenze abituali subordinata all'incontro di allineamento (Milestone M9). |
| **07** | **Fase 1 — Modulo A (Questionario)**      | Skill `noto-questionnaire-drafting` e template `templates/questionnaire_template.md`            | `ESEGUITO — IN TEST UMANO` | `IN FASE DI TEST UMANO` | Gestisce codici standard `97/98/99`, filtri e note di regia per intervistatore; in collaudo umano (Protocollo H2). |
| **08** | **Fase 1 — Modulo A (Questionario)**      | Batterie Socio-Demografiche e Convenzioni Classi d'Età                                          | `ESEGUITO — IN TEST UMANO` | `IN FASE DI TEST UMANO` | Baseline standard Istat/Eurostat implementata in `knowledge/demographics_standard.json` (M4); in collaudo (Protocolli H9, H2; calibrazione Noto M9). |
| **09** | **Fase 1 — Modulo A (Questionario)**      | Batterie Politico-Elettorali, Serie Storiche & Skill `noto-survey-extractor`                     | `ESEGUITO — IN TEST UMANO` | `IN FASE DI TEST UMANO` | Skill speculare `noto-survey-extractor` e libreria elettorale implementate (M3, M4); in collaudo umano (Protocollo H9). |
| **10** | **Fase 1 — Modulo A (Metodologia)**       | Griglia audit a 11 colonne e schede analitiche a 12 campi (`templates/methodology_template.md`) | `ESEGUITO — IN TEST UMANO` | `IN FASE DI TEST UMANO` | Analisi granulare: distingue 5 tipi di non risposta e formula 3 opzioni operative (A, B, C); in collaudo metodologico (Protocollo H3). |
| **11** | **Fase 1 — Modulo A (Metodologia)**       | Calibrazione euristiche metodologiche su vincoli commerciali di Noto                            | `IN ATTESA (GATE DI STOP)` | `In attesa di allineamento con Noto Sondaggi SRL` | Calibrazione euristiche commerciali subordinata al riscontro operativo nella sessione con Noto (Milestone M9). |
| **12** | **Fase 1 — Modulo A (Metodologia)**       | Specificità per modalità di somministrazione (CATI telefonico vs CAWI web)                      | `ESEGUITO — IN TEST UMANO` | `IN FASE DI TEST UMANO` | Specificità CATI/CAWI implementate con sintassi di regia tipografica `[REGIA: ...]`; in collaudo (Protocolli H3, H7; verifica dialer al Gate). |
| **13** | **Fase 1 — Modulo A (Compliance)**        | Checklist screening preliminare GDPR e AI Act (`templates/compliance_template.md`)              | `ESEGUITO — IN TEST UMANO` | `IN FASE DI TEST UMANO` | Censimento dati particolari ex Art. 9 GDPR (voto), re-identificazione e opzione di rifiuto obbligatoria `99`; in collaudo (Protocollo H4). |
| **14** | **Fase 1 — Modulo A (Compliance)**        | Interlocuzione DPO / Consulente Privacy su Art. 9 GDPR e informativa tipo                       | `IN ATTESA (GATE DI STOP)` | `In attesa di interlocuzione con DPO Noto` | Raccordo con DPO Noto Sondaggi per validazione checklist Art. 9 e testo informativa tipo (Milestone M10). |
| **15** | **Fase 1 — Modulo A (Consolidamento)**    | Skill `noto-questionnaire-consolidation` e template `templates/final_template.md`               | `ESEGUITO — IN TEST UMANO` | `IN FASE DI TEST UMANO` | Recepisce sole modifiche approvate, predispone export LimeSurvey e note regia; in collaudo umano (Protocollo H5). |
| **16** | **Fase 2 — Qualità & QA**                 | Script Python verifica sincronizzazione speculare (`scripts/check_mirror_sync.py`)              | `ESEGUITO — IN TEST UMANO` | `IN FASE DI TEST UMANO` | Implementato e operativo al 100%: valida corrispondenza integrale su 7 agenti, 8 skill, 8 template e regole; in collaudo (Protocollo H10). |
| **17** | **Fase 2 — Qualità & QA**                 | Linter e validatore formale degli artefatti (`scripts/validate_runs.py`)                        | `ESEGUITO — IN TEST UMANO` | `IN FASE DI TEST UMANO` | Implementato ed esteso: verifica colonne metodologiche, codici 97/98/99, TSV LimeSurvey e note regia; in collaudo (Protocollo H10). |
| **18** | **Fase 2 — Qualità & QA**                 | Pipeline CI (GitHub Actions) per esecuzione automatica test ad ogni commit                      | `DIFFERITO` | `È da rivedere più avanti` | Attività infrastrutturale differita post v1.0.0; non pregiudica l'operatività locale del flusso. |
| **19** | **Fase 2 — Test & Validazione**           | Caso demo completo di riferimento end-to-end (`examples/demo_run_biblioteca/`)                  | `ESEGUITO — IN TEST UMANO` | `IN FASE DI TEST UMANO` | Realizzato e validato con 9 artefatti completi; fixture ufficiale di riferimento per collaudo (Protocolli H1–H10). |
| **20** | **Fase 2 — Test & Validazione**           | Studio di Caso Reale da Archivio Pubblico AGCOM                                                 | `IN ATTESA (GATE DI STOP)` | `È da rivedere più avanti` | Esercizio programmato in Milestone M11 direttamente sul caso studio reale fornito da Noto Sondaggi. |
| **21** | **Fase 2 — Test & Validazione**           | Protocollo di Benchmark Multi-Modello (`examples/confronto_modelli.csv`)                        | `DIFFERITO` | `È da rivedere più avanti` | Matrice di confronto CSV predisposta; sessioni comparative posticipate per stabilizzare il flusso principale. |
| **22** | **Fase 3 — Sblocco & Dati Reali**         | Integrazione Questionari Storici ed Elaborazione Analisi Pregresse                              | `ESEGUITO — IN TEST UMANO` | `IN FASE DI TEST UMANO` | Dati pregressi utilizzati per tarare le batterie in M4 e la scheda AGCOM in M7; in collaudo (Protocollo H9). |
| **23** | **Fase 3 — Sblocco & Dati Reali**         | Richiesta e Integrazione Batterie Anagrafiche e Politiche Ufficiali                             | `IN ATTESA (GATE DI STOP)` | `In attesa di allineamento con Noto Sondaggi SRL` | Integrazione formulazioni ufficiali Noto programmata in Milestone M9 post-allineamento. |
| **24** | **Fase 4 — Fieldwork & Esportazione**     | Accertamento Piattaforma LimeSurvey e Verifica Applicativi Aggiuntivi                           | `IN ATTESA (GATE DI STOP)` | `In attesa di riscontro Noto su applicativi CATI` | Adozione LimeSurvey accertata (M1/M2); chiarimento eventuale dialer CATI al Gate di Stop con Noto. |
| **25** | **Fase 4 — Fieldwork & Esportazione**     | Formato di Consegna del Questionario agli Intervistatori                                        | `IN ATTESA (GATE DI STOP)` | `In attesa di conferma Noto al Gate di Stop` | Generatore Word sviluppato in M5 (`scripts/generate_interviewer_guide.py`); in attesa di conferma Noto al Gate. |
| **26** | **Fase 4 — Fieldwork & Esportazione**     | Sviluppo Esportatore Automatico per LimeSurvey (`final.md` -> `.txt`/`.lss`)                    | `ESEGUITO — IN TEST UMANO` | `IN FASE DI TEST UMANO` | Priorità tecnica completata in piena autonomia: `scripts/export_limesurvey.py` genera il TSV nativo a 14 colonne; in collaudo (Protocollo H6). |
| **27** | **Fase 4 — Fieldwork & Esportazione**     | Generatore Formato Intervistatore (Word `.docx` con stili e istruzioni di regia)                | `ESEGUITO — IN TEST UMANO` | `IN FASE DI TEST UMANO` | Modulo operativo `scripts/generate_interviewer_guide.py` (MD/HTML/DOCX) con distinzione tipografica note di regia; in collaudo (Protocollo H7). |
| **28** | **Fase 5 — Modulo B (Dati & Statistica)** | Strutturazione contratti di input/output e scheda di `analysis-agent.md`                        | `DIFFERITO` | `È da rivedere più avanti` | Struttura architetturale predisposta; attivazione programmata con il Modulo B avanzato. |
| **29** | **Fase 5 — Modulo B (Dati & Statistica)** | Skill e template per analisi descrittiva e controlli di qualità del dato grezzo                 | `DIFFERITO` | `È da rivedere più avanti` | Differito per dare priorità alla Scheda Informativa AGCOM (Task #33). |
| **30** | **Fase 5 — Modulo B (Ponderazione)**      | Routine di pesatura campionaria complessa (IPF / Raking multivariato su celle incrociate)       | `DIFFERITO` | `È da rivedere più avanti` | Attività deprioritizzata: calcolo multivariato IPF differito a sviluppi successivi. |
| **31** | **Fase 5 — Modulo B (Ponderazione)**      | Trimming, diagnostica di convergenza ed efficienza campionaria dei pesi                         | `DIFFERITO` | `È da rivedere più avanti` | Attività deprioritizzata: controlli su efficienza campionaria e trimming differiti a fase successiva. |
| **32** | **Fase 5 — Modulo B (Ponderazione)**      | Acquisizione convenzioni proprietarie di pesatura e post-stratificazione Noto                   | `DIFFERITO` | `È da rivedere più avanti` | Attività deprioritizzata coerentemente con i Task #30 e #31. |
| **33** | **Fase 5 — Modulo B (Reporting)**         | Creazione skill di reporting con compilazione automatica Scheda AGCOM (`reporting-agent.md`)    | `ESEGUITO — IN TEST UMANO` | `IN FASE DI TEST UMANO` | Sviluppo autonomo completato con `templates/agcom_template.md`, `scripts/generate_agcom_report.py` e `reporting-agent` (Protocollo H8). |
| **34** | **Fase 5 — Modulo B (Dashboard)**         | Strutturazione contratti di input/output e scheda di `dashboard-agent.md`                       | `DIFFERITO` | `È da rivedere più avanti` | Struttura architetturale predisposta; attivazione post-fieldwork. |
| **35** | **Fase 5 — Modulo B (Dashboard)**         | Layout descrittivi, veste grafica e personalizzazione brand Noto Sondaggi                       | `DIFFERITO` | `È da rivedere più avanti` | Personalizzazione visiva e grafica Noto programmata a completamento della pipeline analitica. |

---

## 3. Analisi Tecnica dei Nodi Operativi e dei Punti Aperti con Noto Sondaggi

Con il quadro operativo consolidato, i nodi di sviluppo si articolano in percorsi realizzativi autonomi già avviati e in 4 quesiti tecnici mirati per Noto Sondaggi.

### 3.1 Piattaforma di Fieldwork: Integrazione LimeSurvey ed Esportazione Automatica (Task #24, #25, #26)
- **Quadro consolidato**: Noto Sondaggi impiega ordinariamente **LimeSurvey**.
- **Sviluppo autonomo interno (Task #26 — Priorità Tecnica)**: Realizzazione di un convertitore Python che trasforma il questionario approvato (`runs/<caso>/final.md`) nel formato nativo di importazione di LimeSurvey (file tab-delimited `.txt` per struttura indagine o formato XML `.lss`). Questo componente consente di caricare il questionario validato in piattaforma con procedura automatica, azzerando i tempi di programmazione manuale.
- **Punti di allineamento con Noto Sondaggi**:
  1. *Telefonia CATI*: Accertare se, accanto alle indagini web (CAWI su LimeSurvey), vengano effettuate interviste telefoniche con operatori (CATI). In caso affermativo, verificare se la gestione CATI avvenga tramite LimeSurvey o tramite piattaforme specializzate con predictive dialer (*Task #12, #24*);
  2. *Formato per il personale di rilevazione (Task #25)*: Rilevare le modalità con cui il questionario definitivo viene trasmesso alla sala interviste (documento Word con stili dedicati per le note di regia, foglio di calcolo, o fruizione a schermo).

### 3.2 Batterie Socio-Demografiche e Gestione Parametrica delle Classi d'Età (Task #08)
- **Quadro consolidato**: Da accertare se Noto adotti schemi rigidi per le classi anagrafiche o se li adatti in funzione delle richieste del committente.
- **Soluzione tecnica implementata**: Progettazione modulare e parametrica del generatore di anagrafiche, che rende il sistema di agenti versatile e configurabile:
  - Default metodologico standard allineato alle classificazioni ufficiali Istat/Eurostat (`18-24 / 25-34 / 35-44 / 45-54 / 55-64 / 65+` oppure domanda aperta su anno di nascita ricodificata);
  - Possibilità di applicare configurazioni anagrafiche proprietarie su indicazione di Noto Sondaggi.
- **Punto di allineamento con Noto Sondaggi**: Verifica della presenza di convenzioni storiche proprietarie per età, titolo di studio e condizione occupazionale.

### 3.3 Formulari Politico-Elettorali e Proposta Skill Dedicata (`noto-survey-extractor`) (Task #09, #22)
- **Quadro consolidato**: Il team dispone già di analisi e dati relativi a indagini precedenti; inoltre, le formulazioni politico-elettorali sono desumibili dai questionari di riferimento.
- **Proposta architetturale**: Implementazione della skill specialistica `noto-survey-extractor`:
  - Riceve in ingresso documenti (PDF, Word o testo) di questionari storici caricati nella cartella del caso;
  - Estrae in modo strutturato formulazioni delle serie storiche (fiducia nei leader, voto politico, giudizio sul governo), scale impiegate e codifiche delle liste;
  - Popola la base di conoscenza permanente degli agenti di redazione, assicurando la piena comparabilità storica dei dati.

### 3.4 Governance Privacy e Raccordo con il Referente DPO (Task #14)
- **Quadro consolidato**: I sondaggi politici comportano il trattamento di orientamenti di voto, qualificabili come categorie particolari di dati ex Art. 9 GDPR. Il `compliance-agent` assicura uno screening preliminare rigoroso, ma la convalida formale compete alla funzione DPO/legale.
- **Protocollo operativo**: Attivazione di un canale di raccordo con il **DPO o consulente privacy** di Noto Sondaggi per:
  - Verificare l'aderenza tra la checklist del `compliance-agent` e il Registro dei Trattamenti dell'istituto;
  - Convalidare il testo dell'informativa tipo di somministrazione (formula breve per interviste telefoniche CATI, informativa estesa per somministrazioni CAWI).

### 3.5 Semplificazione Strategica del Modulo B: Differimento della Pesatura Complessa IPF (Task #30, #31, #32) e Sviluppo Scheda AGCOM (Task #33)
- **Decisione metodologica**: Le attività inerenti alla ponderazione campionaria complessa (IPF / Raking multivariato su celle incrociate — Task #30, #31, #32) sono formalmente differite a rilasci successivi. L'applicazione di algoritmi complessi di post-stratificazione multivariata prima della completa stabilizzazione del flusso dati costituirebbe un elemento di sovra-ingegnerizzazione.
- **Focalizzazione del Modulo B**: Valorizzazione delle basi dati storiche disponibili per sviluppare prioritariamente il generatore della **Scheda Informativa AGCOM** (Task #33), deliverable obbligatorio per legge ai fini della pubblicazione dei sondaggi sui mezzi di comunicazione.

---

## 4. Roadmap Cronologica di Esecuzione Riorganizzata a 4 Sprint

L'esecuzione del progetto è strutturata in 4 sprint sequenziali che valorizzano l'autonomia di sviluppo e ottimizzano il raccordo operativo con Noto Sondaggi:

```
┌───────────────────────────────────────────────────────────────────────────────────────┐
│ SPRINT 1 (Immediato - Autonomia Totale Team Universitario - Settimana 1)              │
│ • Sviluppo Esportatore Automatico LimeSurvey (#26) [Priorità Tecnica]                 │
│ • Integrazione analisi storiche già disponibili (#22)                                 │
│ • Progettazione skill di estrazione da sondaggi storici (#09)                         │
│ • Validatori automatici speculari operativi (#16, #17) [ULTIMATO]                     │
│ • [Differiti: CI su GitHub Actions #18 e Benchmark multi-modello #21]                 │
└──────────────────────────────────────────┬────────────────────────────────────────────┘
                                           │
                                           ▼
┌───────────────────────────────────────────────────────────────────────────────────────┐
│ SPRINT 2 (Allineamento Operativo Noto & DPO - Azione Istituzionale - Settimana 1-2)   │
│ • Raccordo operativo con Noto Sondaggi e DPO (comunicazione avviata)                  │
│ • Riscontro canali di rilevazione: CATI telefonico vs CAWI web (#12, #24)             │
│ • Verifica convenzioni classi d'età (#08) e formato note intervistatore (#25)         │
│ • Raccordo con referente privacy per checklist compliance Art. 9 GDPR (#14)           │
│ • Acquisizione di 1-2 questionari storici per test nuova skill (#09)                  │
└──────────────────────────────────────────┬────────────────────────────────────────────┘
                                           │
                                           ▼
┌───────────────────────────────────────────────────────────────────────────────────────┐
│ SPRINT 3 (Calibrazione Modulo A & Esportatori di Consegna - Settimana 2-3)            │
│ • Validazione dell'esportatore LimeSurvey su indagine reale (#26)                     │
│ • Generatore Word per intervistatori (.docx con istruzioni di regia) (#27)            │
│ • Consolidamento convenzioni definitive nelle skill di drafting/audit                 │
│ • Validazione end-to-end Modulo A                                                     │
└──────────────────────────────────────────┬────────────────────────────────────────────┘
                                           │
                                           ▼
┌───────────────────────────────────────────────────────────────────────────────────────┐
│ SPRINT 4 (Modulo B Essenziale: Analisi & Scheda AGCOM - Settimana 3-4)                │
│ • Template di reporting descrittivo su basi dati storiche (#29)                       │
│ • Generatore automatico Scheda Informativa AGCOM (#33)                                │
│ • [Differita: Pesatura campionaria complessa IPF #30-#32 a fase avanzata]             │
│ • Predisposizione layout sintetico dashboard (#34, #35) e documentazione              │
└───────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 5. Checklist Operativa per l'Allineamento Tecnico con Noto Sondaggi SRL

A valle della formalizzazione della comunicazione ufficiale di raccordo già trasmessa a Noto Sondaggi SRL, la presente sezione struttura gli strumenti operativi e la matrice dei quesiti tecnici a supporto della sessione di allineamento e verifica con il committente.

### 5.1 Matrice dei Quesiti Tecnici Essenziali (Quick-Win)
Checklist operativa predisposta per la rilevazione rapida delle specifiche tecniche:

1. **Canali di Rilevazione**:
   - `[ ] Rilevazione esclusiva CAWI web (piattaforma LimeSurvey)`
   - `[ ] Rilevazione mista CAWI + CATI telefonico con operatore (gestione LimeSurvey o applicativo dedicato)`
   - `[ ] Altre modalità (CAPI / rilevazione assistita)`

2. **Formato per gli Intervistatori / Personale di Rilevazione**:
   - `[ ] Documento Word formattato con distinzione grafica per note di regia e istruzioni`
   - `[ ] Caricamento e fruizione diretta a video su piattaforma LimeSurvey`
   - `[ ] Foglio di calcolo strutturato (Excel / CSV)`

3. **Convenzioni Classi d'Età e Standard Demografici**:
   - `[ ] Adozione dello standard ufficiale demografico Istat/Eurostat predisposto dal team (18-24, 25-34, 35-44, 45-54, 55-64, 65+)`
   - `[ ] Applicazione di partizioni anagrafiche proprietarie Noto Sondaggi (da specificare)`

4. **Raccordo Privacy e Governance DPO**:
   - `Referente privacy / DPO designato: _________________________________________`
   - `Canale operativo preferenziale: [ ] Scambio note via email  |  [ ] Breve allineamento tecnico`

---

### 5.2 Fabbisogno Materiali e Documentazione di Supporto
Poiché il team universitario dispone già delle analisi e dei report descrittivi relativi a precedenti indagini di Noto Sondaggi (sufficienti per strutturare il generatore della Scheda AGCOM del Modulo B), il fabbisogno documentale esterno si limita a:
1. **1 o 2 questionari storici di riferimento** (documenti privi di vincoli di riservatezza), necessari per testare e validare l'estrazione automatica di testi e scale tramite la nuova skill `noto-survey-extractor` (fiducia nei leader, orientamenti di voto, batterie socio-demografiche);
2. *(Opzionale)* Un facsimile di Scheda Informativa AGCOM pubblicata o di report esecutivo, al fine di verificare la perfetta aderenza del layout tipografico e dei campi informativi.

---

### 5.3 Schema Operativo della Sessione di Allineamento (Riunione Operativa 20-25 minuti)
1. **Minuti 00-10 — Dimostrazione Operativa Live**: Esecuzione guidata del workflow `/revisione-questionario` e dimostrazione dell'esportatore nativo per LimeSurvey.
2. **Minuti 10-18 — Riscontro sui Quesiti Tecnici**: Definizione delle specifiche per i canali CATI/CAWI, standard classi anagrafiche e modalità di raccordo con il referente privacy.
3. **Minuti 18-25 — Definizione del Calendario di Rilascio**: Programmazione della validazione finale del Modulo A e avvio delle funzionalità del Modulo B (Scheda AGCOM).

---

## 6. Appendice Tecnica: Strumenti di Validazione e Protocolli di Test nel Repository

A riprova del rigore metodologico, ingegneristico e deontologico del lavoro svolto, nel repository sono pienamente operativi e testati i seguenti strumenti di controllo automatico e protocolli di collaudo umano:

1. **[`scripts/check_mirror_sync.py`](../scripts/check_mirror_sync.py)** (Task #16):
   - Esegue la scansione ricorsiva di `.agents/` e `.claude/`.
   - Verifica la coincidenza integrale delle regole di governance ([`AGENTS.md`](../AGENTS.md) vs [`CLAUDE.md`](../CLAUDE.md)).
   - Verifica l'integrità del corpo operativo di tutti i 7 agenti.
   - Verifica l'identità speculare delle 8 skill e la corrispondenza dei 3 comandi workflow.
   - *Esito*: **PASSED — Architettura speculare integra al 100%.**
2. **[`scripts/validate_runs.py`](../scripts/validate_runs.py)** (Task #17):
   - Ispeziona ogni cartella in `runs/<caso>/` o `examples/`.
   - Controlla la presenza delle 11 colonne nella griglia metodologica e delle opzioni di intervento A, B, C.
   - Verifica la presenza e la distinzione tassonomica dei codici di non risposta `97` (Non applicabile), `98` (Non so) e `99` (Preferisco non rispondere / Rifiuto).
   - Verifica la conformità dei file TSV a 14 colonne per LimeSurvey e delle note tipografiche di regia `[REGIA: ...]`.
   - Valida i metadati e il registro cronologico delle decisioni umane in `status.md`.
   - *Esito*: **PASSED — Validazione superata con successo sul caso `demo-biblioteca`.**
3. **[`scripts/export_limesurvey.py`](../scripts/export_limesurvey.py)** (Task #26 — Milestone M1, M2):
   - Parser dal Markdown consolidato (`final.md`) al formato nativo tab-delimited (TSV a 14 colonne) per LimeSurvey CATI/CAWI.
   - Supporta tipi domanda `L` (scelta singola), `M` (scelta multipla), `T`/`S` (testo), `F` (batterie a matrice).
4. **[`scripts/extract_survey_knowledge.py`](../scripts/extract_survey_knowledge.py)** (Task #09, #22 — Milestone M3, M4):
   - Estrattore CLI di formulari, batterie e scale da file `.md`, `.txt`, `.docx` e `.pdf` per la base di conoscenza.
5. **[`scripts/generate_interviewer_guide.py`](../scripts/generate_interviewer_guide.py)** (Task #27, #12 — Milestone M5, M6):
   - Generatore automatico della guida di somministrazione CATI/CAPI con netta distinzione tra enunciato e note di regia.
6. **[`scripts/generate_agcom_report.py`](../scripts/generate_agcom_report.py)** (Task #33 — Milestone M7, M8):
   - Compilatore normativo della Scheda Informativa AGCOM (Delibera 256/10/CSP) con calcolo del margine d'errore campionario teorico al 95% di confidenza.
7. **Suite di Test Unitari e di Regressione (`tests/`)**:
   - 130 test unitari automatizzati eseguiti con successo tramite `python -m unittest discover tests/`.
8. **[`examples/demo_run_biblioteca/`](../examples/demo_run_biblioteca/)** (Task #19):
   - Caso di riferimento completo archiviato nel repository (tracciato da git) con tutti i 9 artefatti generati e validati end-to-end.
9. **Manuale Operativo e Protocolli di Collaudo Umano (`docs/`)**:
   - [`docs/piano_test_umani.md`](piano_test_umani.md): 10 protocolli operativi di collaudo metodologico e privacy (Protocolli H1 – H10);
   - [`docs/piano_operativo.md`](piano_operativo.md): Roadmap operativa a 13 milestone (M0–M12) su 6 track tematiche;
   - [`docs/manuale_installazione.md`](manuale_installazione.md): Manuale di installazione, setup e avvio;
   - [`docs/guida_funzionalita.md`](guida_funzionalita.md): Guida completa enciclopedica alle funzionalità della piattaforma.

---

## 7. Conclusioni e Quadro di Sintesi Istituzionale

Il consolidamento analitico dello stato di sviluppo delinea un assetto di progetto solido, verificato e altamente operativo:
- **Piena maturità del Modulo A e Tooling Autonomo**: L'architettura portante di governance, drafting, audit metodologico, screening privacy, esportazione LimeSurvey, guida intervistatore e Scheda AGCOM è completata (Milestones M0–M8 e 19 task correlati), sincronizzata speculare al 100% tra Google Antigravity e Claude Code, e validata da 130 test automatici.
- **Avvio della Fase di Test Umano (Protocolli H1–H10)**: La transizione operativa pone al centro la validazione qualitativa umana da parte dei ricercatori metodologi e del DPO secondo i protocolli strutturati di [`docs/piano_test_umani.md`](piano_test_umani.md).
- **Presidio Deontologico e Rigore del Gate di Stop**: Prima di procedere alle Milestone M9–M12 (integrazione standard socio-demografici proprietari, parere legale DPO su Art. 9 GDPR e validazione su indagine reale), il sistema si arresta formalmente al Gate di Stop per la sessione di allineamento con Noto Sondaggi SRL.
- **Tracciabilità Accademica Integrale**: La roadmap commit-driven in [`docs/piano_operativo.md`](piano_operativo.md) e la rendicontazione dei 35 task offrono alla Prof.ssa Alessandra Amendola e a Noto Sondaggi SRL una visibilità totale, verificabile e matematicamente quadrata dell'avanzamento scientifico del dottorato.
