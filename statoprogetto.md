# Documento Ufficiale di Avanzamento e Stato del Progetto
## Piattaforma Multi-Agente Human-in-the-Loop per Indagini Demoscopiche — Noto Sondaggi SRL

> **Documento Ufficiale di Avanzamento e Rendicontazione per la Supervisione Accademica e Istituzionale**  
> **Istituzione**: Università degli Studi di Pavia / IUSS Pavia  
> **Supervisione Accademica**: Prof.ssa Alessandra Amendola  
> **Committente / Partner Industriale**: Noto Sondaggi SRL  
> **Versione**: 3.0 (Allineamento Formale e Consolidamento di Stato)  
> **Finalità**: Rendicontare in modo analitico lo stato di avanzamento della piattaforma multi-agente, censire esaustivamente i 35 task di sviluppo, formalizzare la roadmap operativa a 4 sprint, strutturare la checklist operativa per l'allineamento con Noto Sondaggi SRL e documentare l'apparato di validazione tecnica e metodologica implementato nel repository.

---

## 1. Executive Summary per la Supervisione Accademica

### 1.1 Risultati Raggiunti in Piena Autonomia dal Team Universitario
Il team di ricerca ha completato e validato l'intera architettura portante del **Modulo A (Progettazione, Revisione Metodologica, Screening Privacy e Consolidamento del Questionario)**. Il sistema è stato ingegnerizzato secondo il principio della **doppia specularità integrale** per operare indistintamente e con parità funzionale su due ambienti AI di riferimento: **Google Antigravity** (`.agents/`, [AGENTS.md](file:///c:/Users/VincenzoOriti/OneDrive%20-%20Universit%C3%A0%20di%20Pavia/Developing/GitHub/NotoSondaggi_Agents4SurveyPlatform/AGENTS.md)) e **Claude Code** (`.claude/`, [CLAUDE.md](file:///c:/Users/VincenzoOriti/OneDrive%20-%20Universit%C3%A0%20di%20Pavia/Developing/GitHub/NotoSondaggi_Agents4SurveyPlatform/CLAUDE.md)).

Nello specifico, sono stati realizzati, testati e verificati:
1. **Regole Fondamentali di Governance e Deontologia Metodologica**: Perimetro strettamente *human-in-the-loop*, divieto categorico di generare rispondenti sintetici per sostituire dati empirici reali, neutralità scientifica (divieto di profilazione politica o persuasione), tutela rigorosa della tassonomia di non risposta (*unit nonresponse*, *item nonresponse*, rifiuto esplicito `99`, autentico non so `98`, non applicabile `97`, break-off) e salvaguardia della comparabilità delle serie storiche.
2. **Orchestrazione Multi-Agente con Separazione dei Ruoli**: Main Agent supervisore (`ai-coordinator`) e 3 Subagent specialistici (`questionnaire-agent`, `methodology-agent`, `compliance-agent`), con protocollo di stop obbligatorio e approvazione umana in chat ad ogni singolo gate.
3. **6 Template Strutturati Obbligatori**: Contratti di output standardizzati ([`templates/status_template.md`](file:///c:/Users/VincenzoOriti/OneDrive%20-%20Universit%C3%A0%20di%20Pavia/Developing/GitHub/NotoSondaggi_Agents4SurveyPlatform/templates/status_template.md), [`templates/brief_template.md`](file:///c:/Users/VincenzoOriti/OneDrive%20-%20Universit%C3%A0%20di%20Pavia/Developing/GitHub/NotoSondaggi_Agents4SurveyPlatform/templates/brief_template.md), [`templates/questionnaire_template.md`](file:///c:/Users/VincenzoOriti/OneDrive%20-%20Universit%C3%A0%20di%20Pavia/Developing/GitHub/NotoSondaggi_Agents4SurveyPlatform/templates/questionnaire_template.md), [`templates/methodology_template.md`](file:///c:/Users/VincenzoOriti/OneDrive%20-%20Universit%C3%A0%20di%20Pavia/Developing/GitHub/NotoSondaggi_Agents4SurveyPlatform/templates/methodology_template.md) con griglia a 11 colonne e schede a 12 campi, [`templates/compliance_template.md`](file:///c:/Users/VincenzoOriti/OneDrive%20-%20Universit%C3%A0%20di%20Pavia/Developing/GitHub/NotoSondaggi_Agents4SurveyPlatform/templates/compliance_template.md), [`templates/final_template.md`](file:///c:/Users/VincenzoOriti/OneDrive%20-%20Universit%C3%A0%20di%20Pavia/Developing/GitHub/NotoSondaggi_Agents4SurveyPlatform/templates/final_template.md)).
4. **Tooling di Verifica Automatica e QA Interno**:
   - [`scripts/check_mirror_sync.py`](file:///c:/Users/VincenzoOriti/OneDrive%20-%20Universit%C3%A0%20di%20Pavia/Developing/GitHub/NotoSondaggi_Agents4SurveyPlatform/scripts/check_mirror_sync.py): validatore automatico della sincronizzazione speculare tra `.agents/` e `.claude/` (eseguito con successo: 100% allineato);
   - [`scripts/validate_runs.py`](file:///c:/Users/VincenzoOriti/OneDrive%20-%20Universit%C3%A0%20di%20Pavia/Developing/GitHub/NotoSondaggi_Agents4SurveyPlatform/scripts/validate_runs.py): linter formale per la conformità di qualsiasi caso generato in `runs/<caso>/` rispetto a colonne, campi e codici di non risposta;
   - [`examples/demo_run_biblioteca/`](file:///c:/Users/VincenzoOriti/OneDrive%20-%20Universit%C3%A0%20di%20Pavia/Developing/GitHub/NotoSondaggi_Agents4SurveyPlatform/examples/demo_run_biblioteca/): caso completo di riferimento end-to-end con tutte le 5 fasi generate e validate.
5. **Predisposizione dell'Architettura del Modulo B**: Strutture architetturali e schede di definizione per le fasi post-fieldwork (`analysis-agent`, `reporting-agent`, `dashboard-agent`).

---

### 1.2 Quadro Operativo Aggiornato e Ottimizzazione della Strategia di Rilascio
A seguito della disamina analitica condotta elemento per elemento con la direzione scientifica e tecnica, il quadro operativo del progetto si consolida attorno a evidenze chiare e percorsi di sviluppo definiti:

1. **Integrazione della piattaforma di rilevazione (LimeSurvey)**:  
   È stato accertato che Noto Sondaggi impiega ordinariamente **LimeSurvey**. Questa evidenza sblocca lo sviluppo del modulo di esportazione autonoma (`final.md` -> formato nativo per LimeSurvey), trasformando una precedente incertezza tecnica in un percorso di sviluppo a elevato valore aggiunto (*Task #26*). Resta unicamente da verificare se per eventuali interviste telefoniche (CATI) vengano impiegati applicativi complementari (*Task #24*).
2. **Disponibilità interna di analisi e report storici**:  
   Il team dispone già di elaborazioni e analisi relative a indagini precedenti condotte da Noto Sondaggi. Questo patrimonio informativo consente di accelerare la calibrazione dei task metodologici (*Task #22*) e di ancorare la futura generazione di report descrittivi e schede AGCOM (*Task #33*) a strutture concrete e verificate, procedendo in piena autonomia.
3. **Proposta architetturale: Skill di Ingestione Sondaggi Storici (`noto-survey-extractor`)**:  
   Dall'analisi è emerso che i formulari e le scale delle serie storiche di Noto sono desumibili dai questionari di riferimento. Viene formalizzata la proposta di una **skill dedicata** (`noto-survey-extractor`), concepita per elaborare i documenti d'esempio caricati ed estrarre automaticamente formulari, scale e codifiche per alimentare la base di conoscenza permanente degli agenti (*Task #09*).
4. **Focalizzazione strategica del Modulo B (Differimento della Pesatura Complessa IPF)**:  
   La pesatura campionaria multivariata complessa (Iterative Proportional Fitting, trimming dei pesi estremi e convenzioni di post-stratificazione — *Task #30, #31, #32*) è stata giudicata prematura rispetto alla fase corrente di consolidamento del flusso. Viene pertanto differita a rilasci successivi, focalizzando il Modulo B sull'analisi descrittiva (*Task #29*) e sulla generazione automatica della Scheda AGCOM (*Task #33*).
5. **Razionalizzazione delle attività infrastrutturali (CI e Benchmark Multi-Modello)**:  
   La configurazione di pipeline CI automatizzate su GitHub Actions (*Task #18*) e i benchmark sperimentali multi-modello (*Task #21*) vengono classificati come estensioni future, assicurando priorità assoluta ai deliverable applicativi del core metodologico.
6. **Punti aperti per l'allineamento operativo con Noto Sondaggi**:  
   I requisiti che richiedono un riscontro operativo con Noto Sondaggi si sintetizzano in 4 quesiti tecnici essenziali:
   - *Canali di rilevazione*: incidenza e gestione operativa di interviste telefoniche (CATI con operatore) rispetto a rilevazioni web (CAWI su LimeSurvey) (*Task #12, #24*);
   - *Classi anagrafiche e standard socio-demografici*: eventuale presenza di convenzioni proprietarie fisse rispetto allo standard demografico Istat/Eurostat adottato dal team (*Task #08*);
   - *Trasmissione del questionario agli intervistatori*: formato di produzione per il personale di rilevazione (documento Word con indicazioni di regia tipografiche, foglio di calcolo, o fruizione a schermo) (*Task #25*);
   - *Governance privacy*: canale di contatto con il DPO / referente privacy per la validazione delle checklist su categorie particolari di dati ex Art. 9 GDPR (orientamenti di voto) e dell'informativa di somministrazione (*Task #14*).

---

### 1.3 Sintesi Statistica Rigorosa dei 35 Task del Progetto
A seguito delle evidenze operative consolidate, la distribuzione dello stato di sviluppo e della dipendenza esterna delinea un quadro ad elevata autonomia realizzativa: **i requisiti soggetti a vincoli esterni bloccanti si riducono a un singolo elemento (2.9%)**, mentre il volume delle attività già completate o sviluppabili internamente dal team universitario raggiunge il **45.7%** (31.4% ultimati + 14.3% realizzabili in piena autonomia).

| Stato di Sviluppo Attuale | N. Task |  Quota %   | Significato                                                                              |
| :------------------------ | :-----: | :--------: | :--------------------------------------------------------------------------------------- |
| **FATTO**                 |    12   |   34.3%    | Componente completato, verificato nel codice e operativo nel repository                  |
| **ABBOZZATO**             |    11   |   31.4%    | Presente come bozza, linea guida, analisi parziale o struttura architetturale            |
| **IPOTIZZATO**            |    6    |   17.1%    | Previsto a livello architetturale con percorso di realizzazione delineato                |
| **POSSIBILE IN FUTURO**   |    5    |   14.3%    | Funzionalità avanzata posticipata (CI, pacchetto pesatura IPF #30-#32, brand layout #35) |
| **NON PRESENTE**          |    1    |    2.9%    | Elemento non ancora definito (formato consegna intervistatori #25)                       |
| **TOTALE**                |  **35** | **100.0%** |                                                                                          |

| Condizione Operativa & Dipendenza da Noto Sondaggi                   | N. Task |  Quota %   | Implicazione Operativa                                                                                     |
| :------------------------------------------------------------------- | :-----: | :--------: | :--------------------------------------------------------------------------------------------------------- |
| **ULTIMATO**                                                         |    11   |   31.4%    | Componente solido, verificato e conforme agli standard; nessuna azione richiesta                           |
| **Sviluppabile subito internamente**                                 |    5    |   14.3%    | Sviluppo immediato a zero dipendenze esterne (esportatore LimeSurvey, analisi storiche, AGCOM)             |
| **Serve Noto per revisionare ma si può già procedere allo sviluppo** |    8    |   22.9%    | Realizzazione autonoma del prototipo; Noto valida o allinea le preferenze operative                        |
| **Servono prima dati di contesto da Noto altrimenti siamo bloccati** |    1    |    2.9%    | Unico punto subordinato a specifiche di fornitura: formato di consegna materiale agli intervistatori (#25) |
| **È da rivedere più avanti**                                         |    10   |   28.6%    | Attività differite a fasi avanzate o al Modulo B (differita la complessità matematica IPF)                 |
| **TOTALE**                                                           |  **35** | **100.0%** |                                                                                                            |

---

## 2. Master Table dei 35 Task Ordinati per il Completamento del Progetto

La tabella seguente censisce analiticamente tutti i 35 task del progetto, aggiornati con le valutazioni operative, la conferma di LimeSurvey, il differimento della ponderazione IPF, la proposta di skill per l'ingestione dei sondaggi storici e la rigorosa quadratura statistica.

### Legenda delle Colonne:
1. **#**: Progressivo numerico ordinato (da #01 a #35).
2. **Fase / Macro-Area**: Ambito strutturale di appartenenza.
3. **Task / Oggetto Operativo**: Componente tecnico o metodologico specifico.
4. **Stato di Sviluppo**:
   - `FATTO`: Completato, verificato nel codice e operativo.
   - `ABBOZZATO`: Presente come bozza, linea guida, riscontro parziale o struttura architetturale.
   - `IPOTIZZATO`: Previsto concettualmente con percorso di sviluppo delineato.
   - `POSSIBILE IN FUTURO`: Funzionalità posticipata (CI, IPF, layout avanzato).
   - `NON PRESENTE`: Componente ancora da avviare.
5. **Condizione Operativa & Dipendenza da Noto Sondaggi**:
   - `ULTIMATO`: Componente completato, verificato e conforme agli standard tecnici e metodologici.
   - `Sviluppabile subito internamente`: Autonomia totale del team (zero dipendenze esterne).
   - `Serve Noto per revisionare ma si può già procedere allo sviluppo`: Bozza autonoma realizzabile subito, Noto valida.
   - `Servono prima dati di contesto da Noto altrimenti siamo bloccati`: Elemento vincolato a specifiche esterne da chiarire con Noto.
   - `È da rivedere più avanti`: Subordinato a fasi successive o deprioritizzato.
6. **Dettaglio Operativo, Cosa C'è e Cosa Manca**: Diagnosi tecnica puntuale aggiornata.

---

### Tabella Generale dei 35 Task Ordinati

|   #    | Fase / Macro-Area                         | Task / Oggetto Operativo                                                                        |   Stato di Sviluppo   | Condizione Operativa & Dipendenza da Noto Sondaggi                 | Dettaglio Operativo, Cosa C'è e Cosa Manca |
| :----: | :---------------------------------------- | :---------------------------------------------------------------------------------------------- | :-------------------: | :----------------------------------------------------------------- | :----------------------------------------- |
| **01** | **Fase 0 — Governance**                   | Regole deontologiche, divieto rispondenti sintetici, etica GDPR/AI Act                          |        `FATTO`        | `ULTIMATO`                                                         | Codificato esaustivamente in `AGENTS.md` e `CLAUDE.md`. I vincoli scientifici (esclusione rispondenti sintetici, neutralità scientifica, tassonomia della non risposta) sono pienamente consolidati. |
| **02** | **Fase 0 — Architettura**                 | Struttura speculare duale Google Antigravity (`.agents/`) e Claude Code (`.claude/`)            |        `FATTO`        | `ULTIMATO`                                                         | Piena simmetria per agenti, skill, workflow e comandi operativi. Verificata automaticamente con `scripts/check_mirror_sync.py`. |
| **03** | **Fase 0 — Architettura**                 | Separazione dei ruoli tra supervisore (`ai-coordinator`) e subagenti operativi                  |        `FATTO`        | `ULTIMATO`                                                         | Il supervisore coordina il flusso e aggiorna lo stato ma non redige direttamente brief, questionari o audit, prevenendo derive da sovraccarico di contesto. |
| **04** | **Fase 0 — Human-in-the-Loop**            | Protocollo di approvazione umana in chat e tracciamento in `runs/<caso>/status.md`              |        `FATTO`        | `ULTIMATO`                                                         | Definito in `templates/status_template.md` e orchestrato da `noto-survey-pipeline`. Stop obbligatorio dopo ogni fase, gestione nativa in chat senza dipendenze da script esterni. |
| **05** | **Fase 1 — Modulo A (Brief)**             | Skill `noto-brief-structuring` e template `templates/brief_template.md`                         |        `FATTO`        | `Serve Noto per revisionare ma si può già procedere allo sviluppo` | Struttura consolidata (obiettivi, costrutti, target, dati `[DA VERIFICARE]`, domande per il ricercatore). Da rifinire su dati reali e sottoporre a validazione formale con Noto Sondaggi. |
| **06** | **Fase 1 — Modulo A (Brief)**             | Mappatura delle tipologie di committenza abituali di Noto Sondaggi                              |      `ABBOZZATO`      | `Serve Noto per revisionare ma si può già procedere allo sviluppo` | Disponibilità di elementi preliminari raccolti nelle sessioni di avvio. Da consolidare in una tassonomia sistematica delle committenze (media/politica, PA, corporate) per validazione finale. |
| **07** | **Fase 1 — Modulo A (Questionario)**      | Skill `noto-questionnaire-drafting` e template `templates/questionnaire_template.md`            |        `FATTO`        | `ULTIMATO`                                                         | Gestisce codici distinti di non risposta (`97=NA`, `98=Non so`, `99=Rifiuto`), filtri/skip logic e metadati di somministrazione. |
| **08** | **Fase 1 — Modulo A (Questionario)**      | Batterie Socio-Demografiche e Convenzioni Classi d'Età                                          |      `ABBOZZATO`      | `Serve Noto per revisionare ma si può già procedere allo sviluppo` | Da verificare se Noto adotti schemi rigidi per le classi anagrafiche (es. 18-34, 35-54 vs età puntuale). La gestione parametrica e modulare implementata nel sistema garantisce elevata flessibilità; il valore predefinito è allineato agli standard ufficiali Istat/Eurostat. |
| **09** | **Fase 1 — Modulo A (Questionario)**      | Batterie Politico-Elettorali, Serie Storiche & Proposta Skill `noto-survey-extractor`           |      `ABBOZZATO`      | `Sviluppabile subito internamente`                                 | I dati delle serie storiche sono desumibili dai questionari campione. Proposta architetturale: progettazione della skill `noto-survey-extractor` per estrarre in modo strutturato formulari, scale e codifiche da file di questionari storici caricati. |
| **10** | **Fase 1 — Modulo A (Metodologia)**       | Griglia audit a 11 colonne e schede analitiche a 12 campi (`templates/methodology_template.md`) |        `FATTO`        | `ULTIMATO`                                                         | Analisi granulare: distingue 5 tipologie di non risposta (rifiuto, non so autentico, non applicabile, item nonresponse, break-off) e formula 3 opzioni operative (A: Conservare, B: Modifica minima, C: Revisione sostanziale). |
| **11** | **Fase 1 — Modulo A (Metodologia)**       | Calibrazione euristiche metodologiche su vincoli commerciali di Noto                            |      `ABBOZZATO`      | `Serve Noto per revisionare ma si può già procedere allo sviluppo` | Regole euristiche implementate (double-barreled questions, leading questions, priming, recall bias). Da calibrare nel confronto operativo con Noto per contemperare rigore metodologico e tempi di somministrazione. |
| **12** | **Fase 1 — Modulo A (Metodologia)**       | Specificità per modalità di somministrazione (CATI telefonico vs CAWI web)                      |      `ABBOZZATO`      | `Serve Noto per revisionare ma si può già procedere allo sviluppo` | Da verificare con Noto l'effettiva incidenza di interviste telefoniche (CATI con operatore) rispetto a rilevazioni su panel online (CAWI). La checklist tecnica è predisposta per entrambi i canali. |
| **13** | **Fase 1 — Modulo A (Compliance)**        | Checklist screening preliminare GDPR e AI Act (`templates/compliance_template.md`)              |        `FATTO`        | `ULTIMATO`                                                         | Censimento categorie particolari di dati ex Art. 9 GDPR (orientamenti politici), valutazione del rischio di re-identificazione indiretta, esclusione di attestazioni legali automatiche e obbligo di opzione di rifiuto (`99`). |
| **14** | **Fase 1 — Modulo A (Compliance)**        | Interlocuzione DPO / Consulente Privacy su Art. 9 GDPR e informativa tipo                       |      `IPOTIZZATO`     | `Serve Noto per revisionare ma si può già procedere allo sviluppo` | Previsto un canale di raccordo con il DPO o consulente privacy di Noto per validare le procedure di screening del `compliance-agent`, in particolare per le indagini su orientamenti di voto e per l'informativa di somministrazione. |
| **15** | **Fase 1 — Modulo A (Consolidamento)**    | Skill `noto-questionnaire-consolidation` e template `templates/final_template.md`               |        `FATTO`        | `ULTIMATO`                                                         | Recepisce esclusivamente le modifiche approvate dal ricercatore in `status.md`, traccia le opzioni scartate e predispone il piano di validazione empirica. |
| **16** | **Fase 2 — Qualità & QA**                 | Script Python verifica sincronizzazione speculare (`scripts/check_mirror_sync.py`)              |        `FATTO`        | `ULTIMATO`                                                         | Implementato e verificato con successo: valida la corrispondenza integrale tra `.agents/` e `.claude/`, frontmatter, body markdown, skill e template. |
| **17** | **Fase 2 — Qualità & QA**                 | Linter e validatore formale degli artefatti (`scripts/validate_runs.py`)                        |        `FATTO`        | `ULTIMATO`                                                         | Implementato e verificato con successo: verifica la conformità delle 11 colonne metodologiche, dei codici standard 97, 98, 99 e della corretta compilazione di `status.md`. |
| **18** | **Fase 2 — Qualità & QA**                 | Pipeline CI (GitHub Actions) per esecuzione automatica test ad ogni commit                      | `POSSIBILE IN FUTURO` | `È da rivedere più avanti`                                         | Attività differita a una fase successiva dell'infrastruttura; non rappresenta un requisito critico per l'operatività del flusso di lavoro. |
| **19** | **Fase 2 — Test & Validazione**           | Caso demo completo di riferimento end-to-end (`examples/demo_run_biblioteca/`)                  |        `FATTO`        | `ULTIMATO`                                                         | Realizzato e validato con successo: include i 5 artefatti completi di fase (`status.md`, `questionnaire.md`, `methodology.md`, `compliance.md`, `final.md`). |
| **20** | **Fase 2 — Test & Validazione**           | Studio di Caso Reale da Archivio Pubblico AGCOM                                                 |      `IPOTIZZATO`     | `È da rivedere più avanti`                                         | Esercizio metodologico programmato per una fase successiva, per dare priorità all'integrazione dei dati operativi diretti e al raccordo con Noto Sondaggi. |
| **21** | **Fase 2 — Test & Validazione**           | Protocollo di Benchmark Multi-Modello (`examples/confronto_modelli.csv`)                        |      `ABBOZZATO`      | `È da rivedere più avanti`                                         | Matrice di confronto predisposta in formato CSV. Le sessioni comparative multi-modello sono temporaneamente differite per concentrare le risorse sulla stabilizzazione del flusso principale. |
| **22** | **Fase 3 — Sblocco & Dati Reali**         | Integrazione Questionari Storici ed Elaborazione Analisi Pregresse                              |      `ABBOZZATO`      | `Sviluppabile subito internamente`                                 | Integrazione dei dati e delle analisi di indagini pregresse già nella disponibilità interna del team, accelerando la calibrazione dei moduli metodologici senza dipendere da nuovi invii. |
| **23** | **Fase 3 — Sblocco & Dati Reali**         | Richiesta e Integrazione Batterie Anagrafiche e Politiche Ufficiali                             |      `IPOTIZZATO`     | `Serve Noto per revisionare ma si può già procedere allo sviluppo` | Verifica e allineamento con Noto Sondaggi delle formulazioni standard per batterie socio-demografiche e politiche, al fine di consolidare la base di conoscenza permanente degli agenti. |
| **24** | **Fase 4 — Fieldwork & Esportazione**     | Accertamento Piattaforma LimeSurvey e Verifica Applicativi Aggiuntivi                           |      `ABBOZZATO`      | `Serve Noto per revisionare ma si può già procedere allo sviluppo` | Accertato l'impiego ordinario di LimeSurvey da parte di Noto Sondaggi. Da chiarire l'eventuale ricorso ad applicativi dedicati per la gestione di interviste telefoniche CATI (es. predictive dialer) o CAPI. |
| **25** | **Fase 4 — Fieldwork & Esportazione**     | Formato di Consegna del Questionario agli Intervistatori                                        |     `NON PRESENTE`    | `Servono prima dati di contesto da Noto altrimenti siamo bloccati` | Definizione dello standard di trasmissione del testo al personale di rilevazione: documento Word strutturato con note di regia, foglio di calcolo, o fruizione a schermo su piattaforma. |
| **26** | **Fase 4 — Fieldwork & Esportazione**     | Sviluppo Esportatore Automatico per LimeSurvey (`final.md` -> `.txt`/`.lss`)                    |      `ABBOZZATO`      | `Sviluppabile subito internamente`                                 | Sviluppo prioritario del modulo di conversione automatica dal Markdown finale (`final.md`) al formato nativo di importazione per LimeSurvey (file tab-delimited `.txt` per gruppi/domande/risposte o XML `.lss`), sviluppabile in piena autonomia dal team. |
| **27** | **Fase 4 — Fieldwork & Esportazione**     | Generatore Formato Intervistatore (Word `.docx` con stili e istruzioni di regia)                |      `IPOTIZZATO`     | `Sviluppabile subito internamente`                                 | Modulo per la produzione automatica della guida di somministrazione per l'intervistatore in formato Word (`.docx`), con distinzione tipografica tra testo per il rispondente e note di regia. |
| **28** | **Fase 5 — Modulo B (Dati & Statistica)** | Strutturazione contratti di input/output e scheda di `analysis-agent.md`                        |      `ABBOZZATO`      | `È da rivedere più avanti`                                         | Struttura architetturale predisposta (*In attesa di attivazione*). Il completamento avverrà con l'attivazione della seconda fase progettuale (Modulo B). |
| **29** | **Fase 5 — Modulo B (Dati & Statistica)** | Skill e template per analisi descrittiva e controlli di qualità del dato grezzo                 |      `IPOTIZZATO`     | `È da rivedere più avanti`                                         | Implementazione programmata a partire dalle basi dati e dai report storici già disponibili internamente (controlli di coerenza, identificazione speeders, frequenze, tabelle di contingenza). |
| **30** | **Fase 5 — Modulo B (Ponderazione)**      | Routine di pesatura campionaria complessa (IPF / Raking multivariato su celle incrociate)       | `POSSIBILE IN FUTURO` | `È da rivedere più avanti`                                         | Attività deprioritizzata: l'algoritmo di calcolo multivariato (Raking/IPF) è differito a sviluppi successivi per focalizzare le risorse sui deliverable a valore immediato. |
| **31** | **Fase 5 — Modulo B (Ponderazione)**      | Trimming, diagnostica di convergenza ed efficienza campionaria dei pesi                         | `POSSIBILE IN FUTURO` | `È da rivedere più avanti`                                         | Attività deprioritizzata: controlli avanzati sull'efficienza campionaria (Kish design effect) e trimming dei pesi estremi differiti a fase successiva. |
| **32** | **Fase 5 — Modulo B (Ponderazione)**      | Acquisizione convenzioni proprietarie di pesatura e post-stratificazione Noto                   | `POSSIBILE IN FUTURO` | `È da rivedere più avanti`                                         | Attività deprioritizzata: coerentemente con i Task #30 e #31, la formalizzazione di convenzioni complesse di post-stratificazione non rientra nel perimetro immediato di confronto con Noto. |
| **33** | **Fase 5 — Modulo B (Reporting)**         | Creazione skill di reporting con compilazione automatica Scheda AGCOM (`reporting-agent.md`)    |      `IPOTIZZATO`     | `Sviluppabile subito internamente`                                 | Sviluppo autonomo a partire dai dati storici disponibili: generazione automatizzata della Scheda Informativa AGCOM, obbligatoria per legge ai fini della pubblicazione editoriale dei sondaggi. |
| **34** | **Fase 5 — Modulo B (Dashboard)**         | Strutturazione contratti di input/output e scheda di `dashboard-agent.md`                       |      `ABBOZZATO`      | `È da rivedere più avanti`                                         | Struttura architetturale predisposta, coerente con il disegno modulare dell'architettura complessiva. |
| **35** | **Fase 5 — Modulo B (Dashboard)**         | Layout descrittivi, veste grafica e personalizzazione brand Noto Sondaggi                       | `POSSIBILE IN FUTURO` | `È da rivedere più avanti`                                         | Personalizzazione dell'interfaccia visiva e integrazione delle linee guida grafiche di Noto Sondaggi, programmata a completamento della pipeline analitica. |

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

## 6. Appendice Tecnica: Strumenti di Validazione Implementati nel Repository

A riprova del rigore metodologico e ingegneristico del lavoro svolto, nel repository sono pienamente operativi i seguenti strumenti di controllo automatico:

1. **[`scripts/check_mirror_sync.py`](file:///c:/Users/VincenzoOriti/OneDrive%20-%20Universit%C3%A0%20di%20Pavia/Developing/GitHub/NotoSondaggi_Agents4SurveyPlatform/scripts/check_mirror_sync.py)**:
   - Esegue la scansione ricorsiva di `.agents/` e `.claude/`.
   - Verifica la coincidenza integrale delle regole di governance (`AGENTS.md` vs `CLAUDE.md`).
   - Verifica l'integrità del corpo operativo di tutti i 7 agenti.
   - Verifica l'identità delle 6 skill e la corrispondenza dei comandi workflow.
   - *Esito*: **PASSED — Architettura speculare integra al 100%.**
2. **[`scripts/validate_runs.py`](file:///c:/Users/VincenzoOriti/OneDrive%20-%20Universit%C3%A0%20di%20Pavia/Developing/GitHub/NotoSondaggi_Agents4SurveyPlatform/scripts/validate_runs.py)**:
   - Ispeziona ogni cartella in `runs/<caso>/` o `examples/`.
   - Controlla la presenza delle 11 colonne nella griglia metodologica e delle opzioni di intervento A, B, C.
   - Verifica la presenza e la distinzione tassonomica dei codici di non risposta `97` (Non applicabile), `98` (Non so) e `99` (Preferisco non rispondere / Rifiuto).
   - Valida i metadati e il registro cronologico delle decisioni umane in `status.md`.
   - *Esito*: **PASSED — Validazione superata con successo sul caso `demo-biblioteca`.**
3. **[`examples/demo_run_biblioteca/`](file:///c:/Users/VincenzoOriti/OneDrive%20-%20Universit%C3%A0%20di%20Pavia/Developing/GitHub/NotoSondaggi_Agents4SurveyPlatform/examples/demo_run_biblioteca/)**:
   - Caso di riferimento completo archiviato nel repository (tracciato da git) con tutti i 5 artefatti generati e validati end-to-end.

---

## 7. Conclusioni e Quadro di Sintesi Istituzionale

Il consolidamento analitico dello stato di sviluppo delinea un assetto di progetto solido, verificato e altamente operativo:
- **Piena maturità del Modulo A**: L'architettura portante di governance, drafting, audit metodologico e screening privacy è completata, sincronizzata speculare al 100% tra Google Antigravity e Claude Code, e validata da test automatici e casi studio di riferimento.
- **Sviluppo autonomo ad elevato impatto**: La certezza dell'adozione di **LimeSurvey** da parte di Noto Sondaggi e la disponibilità interna di report e dati storici consentono al team universitario di procedere senza interruzioni nello sviluppo dell'esportatore nativo e del generatore della Scheda AGCOM.
- **Focalizzazione metodologica**: La temporanea deprioritizzazione della pesatura campionaria complessa (IPF, Task #30-#32) e degli apparati infrastrutturali differibili salvaguarda le risorse di ricerca, concentrandole sui deliverable di immediato valore d'uso per il committente.
- **Allineamento operativo con il committente**: Con la trasmissione formale della comunicazione di allineamento e la definizione della checklist operativa (Sezione 5), il raccordo con Noto Sondaggi SRL e il rispettivo referente DPO è strutturato per richiedere il minimo impegno temporale, massimizzando l'efficacia del confronto tecnico.
