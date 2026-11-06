# Piano di Test Umano e Manuale Operativo di Verifica della Piattaforma Multi-Agente
## Protocolli di Collaudo Metodologico, Deontologico e Tecnico per Ricercatori e DPO
### Progetto: Survey AI Human-in-the-Loop — Noto Sondaggi SRL & IUSS Pavia

> **Destinatari**: Ricercatori metodologi senior/junior, Responsabili del Fieldwork CATI/CAWI/CAPI, Data Protection Officer (DPO) e consulenti di conformità normativa di **Noto Sondaggi SRL** e **IUSS Pavia**.  
> **Oggetto**: Manuale operativo completo di testing umano per ciascuna funzionalità della piattaforma multi-agente: 10 protocolli di test passo-passo (Protocolli H1 – H10), criteri di accettazione qualitativi insostituibili, master checklist tabellari a crocette esecutive e modulo di tracciamento delle deviazioni metodologiche.  
> **Versione**: 1.0 — Deliverable di Certificazione Qualità e Validazione Empirica  
> **Riferimenti di Roadmap e Avanzamento**: [`docs/statoprogetto.md`](statoprogetto.md) (Censimento dei 35 task) e [`docs/piano_operativo.md`](piano_operativo.md) (Roadmap a 13 milestone M0–M12 e Gate di Stop).  
> **Principio Fondamentale**: *"L'intelligenza artificiale propone, il ricercatore umano dispone, verifica e certifica."*  

---

## Indice Generale

1. [Premessa Metodologica e Obiettivi del Testing Umano](#1-premessa-metodologica-e-obiettivi-del-testing-umano)
   - 1.1 [Perché la Validazione Automatica non basta: Limiti dell'Audit Algoritmico](#11-perché-la-validazione-automatica-non-basta-limiti-dellaudit-algoritmico)
   - 1.2 [La Responsabilità Scientifica, Giuridica ed Editoriale del Ricercatore](#12-la-responsabilità-scientifica-giuridica-ed-editoriale-del-ricercatore)
   - 1.3 [Matrice dei Ruoli dei Tester e Competenze Coinvolte](#13-matrice-dei-ruoli-dei-tester-e-competenze-coinvolte)
   - 1.4 [L'Ambiente di Test e la Gestione dei Dati Fittizi vs Empirici](#14-lambiente-di-test-e-la-gestione-dei-dati-fittizi-vs-empirici)
2. [I 10 Protocolli Operativi di Test Umano Passo-Passo (Protocolli H1 – H10)](#2-i-10-protocolli-operativi-di-test-umano-passo-passo-protocolli-h1--h10)
   - 2.1 [Protocollo H1 — Validazione Strutturazione del Brief (`brief.md`)](#21-protocollo-h1--validazione-strutturazione-del-brief-briefmd)
   - 2.2 [Protocollo H2 — Validazione Bozza di Questionario (`questionnaire.md`)](#22-protocollo-h2--validazione-bozza-di-questionario-questionnairemd)
   - 2.3 [Protocollo H3 — Validazione Audit Metodologico Item-per-Item (`methodology.md`)](#23-protocollo-h3--validazione-audit-metodologico-item-per-item-methodologymd)
   - 2.4 [Protocollo H4 — Validazione Screening Compliance Privacy & AI Act (`compliance.md`)](#24-protocollo-h4--validazione-screening-compliance-privacy--ai-act-compliancemd)
   - 2.5 [Protocollo H5 — Validazione Consolidamento Finale e Skip Logic (`final.md`)](#25-protocollo-h5--validazione-consolidamento-finale-e-skip-logic-finalmd)
   - 2.6 [Protocollo H6 — Validazione Fieldwork Bridge LimeSurvey TSV (`limesurvey_survey.txt`)](#26-protocollo-h6--validazione-fieldwork-bridge-limesurvey-tsv-limesurvey_surveytxt)
   - 2.7 [Protocollo H7 — Validazione Guida Intervistatore CATI/CAPI (`guida_intervistatore.md`/HTML/Word)](#27-protocollo-h7--validazione-guida-intervistatore-caticapi-guida_intervistatormdhtmlword)
   - 2.8 [Protocollo H8 — Validazione Scheda AGCOM Delibera 256/10/CSP (`scheda_agcom.md`)](#28-protocollo-h8--validazione-scheda-agcom-delibera-25610csp-scheda_agcommd)
   - 2.9 [Protocollo H9 — Validazione Ingestione Questionari Storici (`extract_survey_knowledge.py`)](#29-protocollo-h9--validazione-ingestione-questionari-storici-extract_survey_knowledgepy)
   - 2.10 [Protocollo H10 — Validazione Orchestrazione e STOP Gate in Chat (`status.md`)](#210-protocollo-h10--validazione-orchestrazione-e-stop-gate-in-chat-statusmd)
3. [Master Checklist Tabellare Esecutiva a Crocette](#3-master-checklist-tabellare-esecutiva-a-crocette)
   - 3.1 [Tabella di Collaudo Modulo A (Protocolli H1 – H5)](#31-tabella-di-collaudo-modulo-a-protocolli-h1--h5)
   - 3.2 [Tabella di Collaudo Tooling e Bridge Operativi (Protocolli H6 – H9)](#32-tabella-di-collaudo-tooling-e-bridge-operativi-protocolli-h6--h9)
   - 3.3 [Tabella di Collaudo Governance e Interazione Chat (Protocollo H10)](#33-tabella-di-collaudo-governance-e-interazione-chat-protocollo-h10)
4. [Modulo di Registrazione Anomalie e Riconciliazione (Bug & Methodological Deviation Report)](#4-modulo-di-registrazione-anomalie-e-riconciliazione-bug--methodological-deviation-report)
   - 4.1 [Workflow di Gestione dell'Anomalia e Classificazione di Gravità](#41-workflow-di-gestione-dellanomalia-e-classificazione-di-gravità)
   - 4.2 [Modello di Scheda Segnalazione Non Conformità](#42-modello-di-scheda-segnalazione-non-conformità)
5. [Verbale Finale di Omologazione al Fieldwork](#5-verbale-finale-di-omologazione-al-fieldwork)

---

## 1. Premessa Metodologica e Obiettivi del Testing Umano

### 1.1 Perché la Validazione Automatica non basta: Limiti dell'Audit Algoritmico

La piattaforma multi-agente include suite di test automatici rigorose (sintassi Markdown, parsing TSV a 14 colonne, formule statistiche di Gauss, coerenza dei metadati tramite [`scripts/validate_runs.py`](../scripts/validate_runs.py) e [`scripts/check_mirror_sync.py`](../scripts/check_mirror_sync.py)).  
Tuttavia, **l'automazione formale è cieca rispetto alla semantica profonda, al contesto sociale e alla psicologia della risposta**:

```
┌────────────────────────────────────────┐     ┌────────────────────────────────────────┐
│     VALIDAZIONE AUTOMATICA (SCRIPT)    │     │      VALIDAZIONE UMANA (METODOLOGO)    │
├────────────────────────────────────────┤     ├────────────────────────────────────────┤
│ ✓ Sintassi Markdown valida             │     │ 👁 Assenza di presupposizioni ideologiche│
│ ✓ Presenza intestazioni e sezioni      │     │ 👁 Valutazione dell'effetto priming/halo│
│ ✓ Esistenza codici 97, 98, 99          │     │ 👁 Bilanciamento percettivo della scala│
│ ✓ Calcolo matematico margine d'errore  │     │ 👁 Salvaguardia semantica serie storiche│
│ ✓ Rispetto delle 14 colonne TSV        │     │ 👁 Adeguatezza socioculturale del target│
│ ✓ Regex di marcatura [DA VERIFICARE]   │     │ 👁 Legittimità etica e riservatezza    │
└────────────────────────────────────────┘     └────────────────────────────────────────┘
```

I Large Language Models possono generare testi formalmente perfetti ma metodologicamente viziati da:
1. **Bias di acquiescenza (*Acquiescence Bias*)**: Formulazioni che spingono inconsciamente l'intervistato a concordare con l'affermazione proposta;
2. **Presupposizione non dimostrata (*Loaded/Leading Questions*)**: Domande che contengono una premessa implicita negativa o positiva (es. *"Dati i continui ritardi del trasporto pubblico, quanto ritiene urgente..."*);
3. **Quesiti a doppio bersaglio (*Double-Barreled Questions*)**: Quesiti che aggregano due concetti distinti in un unico item (es. *"Ritiene che il servizio sia rapido ed economico?"*), rendendo impossibile interpretare il dato se l'utente trova il servizio rapido ma costoso;
4. **Effetto di ancoraggio e contesto (*Priming / Context Effects*)**: Disposizione sequenziale errata delle sezioni, per cui una domanda su un recente scandalo politico altera la valutazione successiva sull'onestà del candidato;
5. **Asimmetria delle scale di risposta**: Scale Likert sbilanciate su più gradi di positività rispetto a quelli di negatività;
6. **Allucinazione di consuntivi e surrogazione sintetica**: Rischio che il modello inventi percentuali campionarie a consuntivo anziché preservare la dicitura `[DA VERIFICARE SUL CAMPO]`.

Il presente piano di test fornisce il **protocollo operativo e tassonomico per il ricercatore umano**, unico soggetto deontologicamente e scientificamente deputato a convalidare ogni artefatto prima che entri nella catena di produzione e rilevazione.

---

### 1.2 La Responsabilità Scientifica, Giuridica ed Editoriale del Ricercatore

In conformità al Codice di Condotta Internazionale **ESOMAR/ICC**, alle norme **WAPOR**, al Regolamento UE 2016/679 (**GDPR**) e alle delibere **AGCOM** (in particolare la Delibera n. 256/10/CSP e s.m.i.):
- L'utilizzo dell'Intelligenza Artificiale **non esonera in alcun caso** il ricercatore dalla responsabilità metodologica e legale dei quesiti e dei report pubblicati.
- **Divieto categorico di rispondenti sintetici**: Nessuna decisione di ricerca o stima statistica può essere basata su interviste simulate o rispondenti virtuali generati da LLM.
- **Responsabilità editoriale verso l'Autorità**: La Scheda Informativa AGCOM depositata sul portale pubblico `www.sondaggipoliticoelettorali.it` è un atto avente valore giuridico; eventuali discrepanze tra il testo somministrato e quello dichiarato comportano sanzioni amministrative a carico del direttore responsabile e dell'istituto.

---

### 1.3 Matrice dei Ruoli dei Tester e Competenze Coinvolte

I collaudi umani sono ripartiti su quattro figure professionali complementari di **Noto Sondaggi SRL** e **IUSS Pavia**:

| Ruolo Tester | Abbreviazione | Competenze Chiave | Protocolli Assegnati |
| :--- | :---: | :--- | :--- |
| **Ricercatore Metodologo Senior** | `MET-SR` | Metodologia delle scienze sociali, psicologia cognitiva, question-wording, comparabilità serie storiche demoscopiche. | **H1, H2, H3, H5, H10** |
| **Data Protection Officer / Privacy Reviewer** | `DPO-LEG` | Diritto della privacy, GDPR Art. 9 (dati particolari), tutela dell'anonimato, compliance informativa, AI Act. | **H4, H5** |
| **Responsabile Sala Campo CATI/CAWI** | `FLD-DIR` | Usabilità dell'interfaccia, tempi di somministrazione, interazione intervistatore-intervistato, fatica cognitiva. | **H2, H6, H7** |
| **Operatore Tecnico / Data Scientist** | `TEC-OPS` | Piattaforme LimeSurvey, esportazione TSV, parsing ExpressionScript, calcolo margine di Gauss, archiviazione. | **H6, H8, H9** |

---

### 1.4 L'Ambiente di Test e la Gestione dei Dati Fittizi vs Empirici

Tutti i protocolli di test devono essere eseguiti all'interno dell'ambiente di lavoro locale o su cartelle di collaudo isolate in `runs/`:
- **Isolamento dei Casi**: Creare una cartella `runs/test_collaudo_<data>/` per non inquinare i casi di indagine reale;
- **Utilizzo di Dati Fittizi**: Nelle prove di estrazione e verifica non utilizzare recapiti reali (numeri di telefono, indirizzi email, nomi di cittadini) a tutela del GDPR;
- **Marcatura Indefiniti**: Qualsiasi dato empirico non ancora misurato sul campo deve rimanere rigorosamente marcato come `[DA VERIFICARE SUL CAMPO]`.

---

## 2. I 10 Protocolli Operativi di Test Umano Passo-Passo (Protocolli H1 – H10)

---

### 2.1 Protocollo H1 — Validazione Strutturazione del Brief (`brief.md`)

```
Responsabile Primario: MET-SR (Ricercatore Metodologo)
Artefatto da collaudare: runs/<caso>/brief.md
Documento sorgente: runs/<caso>/source/* (appunti, email committente, trascrizione)
Template di riferimento: templates/brief_template.md
Skill di riferimento: noto-brief-structuring
```

#### 2.1.1 Obiettivo del Collaudo Umano
Accertare che l'agente [`questionnaire-agent`](../.agents/agents/questionnaire-agent.md) abbia convertito le richieste discorsive, frammentarie o disorganizzate del committente in un documento programmatico rigoroso, senza introdurre presupposizioni indebite e senza dimenticare vincoli essenziali di campionamento.

#### 2.1.2 Procedura Operativa Passo-Passo
1. **Apertura e Confronto Sinottico**:
   - Aprire a schermo affiancato il testo originario in `runs/<caso>/source/` e il brief generato in `runs/<caso>/brief.md`.
2. **Verifica Traduzione Costrutti Latenti (Sezione 2)**:
   - Verificare che i desiderata colloquiali del committente (es. *"vogliamo capire se l'opinione pubblica è contraria alla nuova opera pubblica"*) siano stati trasformati in costrutti analitici neutri (es. *"Rilevazione del livello di favore/sfavore verso l'infrastruttura X e percezione dell'impatto sul traffico e sull'ambiente"*).
   - Accertare che l'agente non abbia adottato l'eventuale framing tendenzioso suggerito dal cliente.
3. **Verifica della Marcatura delle Fonti e dei Dati Fattuali (Sezione 1)**:
   - Identificare ogni menzione di delibere, decreti, importi economici, date di inaugurazione o percentuali di bilancio.
   - Controllare che ciascun dato fattuale non certificato rechi la marcatura:
     ```text
     [DA VERIFICARE: verificare numero protocollo e importo stanziato da delibera comunale]
     ```
4. **Verifica Completezza del Disegno Campionario Proposto (Sezione 3)**:
   - Controllare la popolazione di riferimento (residenti, elettori, fruitori del servizio).
   - Verificare se l'estensione territoriale (comunale, regionale, nazionale) corrisponde al perimetro dello studio.
   - Verificare la congruità della modalità proposta (CATI, CAWI, CAMI, mista) rispetto agli obiettivi e al budget di tempo.
5. **Verifica delle Lacune Informative e Domande per il Ricercatore (Sezione 5)**:
   - Leggere le domande poste dall'agente al ricercatore. Sono quesiti cruciali (es. *"Esiste una serie storica precedente da preservare?"*, *"Qual è la quota di copertura mobile richiesta?"*) o mere ovvietà?
   - Formulare le risposte in chat da passare all'orchestratore.

#### 2.1.3 Criteri di Accettazione e Decisione
- **SUPERATO**: Tutti i costrutti sono neutri; tutte le date/norme non verificate recano `[DA VERIFICARE]`; le lacune sono pertinenti.
- **CON RISERVA**: Mancano dettagli secondari ma l'impostazione concettuale è solida. Il metodologo integra le note nel verbale.
- **NON SUPERATO**: Presenza di costrutti non neutrali derivati dal cliente; invenzione di dati non presenti nella sorgente; assenza della sezione vincoli metodologici.

---

### 2.2 Protocollo H2 — Validazione Bozza di Questionario (`questionnaire.md`)

```
Responsabile Primario: MET-SR (Ricercatore Metodologo)
Co-Tester: FLD-DIR (Responsabile Campo CATI/CAWI)
Artefatto da collaudare: runs/<caso>/questionnaire.md
Template di riferimento: templates/questionnaire_template.md
Skill di riferimento: noto-questionnaire-drafting
```

#### 2.2.1 Obiettivo del Collaudo Umano
Verificare l'assenza di distorsioni cognitive nel question-wording, il perfetto bilanciamento delle scale di risposta, la completezza della codifica standard per la mancata opinione (`97`, `98`, `99`) e l'efficacia delle note di regia per gli intervistatori.

#### 2.2.2 Procedura Operativa Passo-Passo
1. **Lettura Critica a Voce Alta (*Cognitive Walkthrough*)**:
   - Il metodologo o il responsabile di campo legge l'intero testo a voce alta simulando una telefonata o una lettura su schermo smartphone.
   - Verificare la scorrevolezza lessicale, la chiarezza del registro linguistico e l'assenza di termini burocratici o gergali oscuri.
2. **Audit del Question-Wording (Neutralità e Assenza di Presupposizioni)**:
   - Esaminare ogni singolo item alla ricerca di:
     - **Leading**: la domanda suggerisce la risposta preferibile? (es. *"Non crede che sia giusto ridurre le imposte...?"* $\rightarrow$ **ERRORE GRAVE**);
     - **Double-barreled**: la domanda chiede conto di due temi distinti con un'unica scala? (es. *"Quanto è soddisfatto della pulizia e dell'illuminazione?"* $\rightarrow$ **ERRORE GRAVE**);
     - **Polarità sbilanciata e bilanciamento scale (Likert 4 o 5 punti)**:
       - *Scale a 4 punti (scelta forzata senza punto mediano)*: verificare la perfetta simmetria bipolare dei gradi (es. *Molto d'accordo, Abbastanza d'accordo, Poco d'accordo, Per nulla d'accordo*) e valutare l'adeguatezza metodologica della scelta forzata;
       - *Scale a 5 punti (con categoria neutra/intermedia)*: verificare la neutralità semantica del grado centrale (es. *Né favorevole né contrario / Intermedio*) evitando che funga da rifugio per la mancata opinione (da indirizzare al codice `98. Non so`);
       - Verificare in entrambi i casi che il numero di gradi positivi e negativi sia bilanciato (evitare 3 gradi favorevoli e 1 solo contrario $\rightarrow$ **ERRORE GRAVE**).
3. **Verifica della Tassonomia a 6 Codici e Opzioni Standard di Uscita**:
   - Ispezionare ogni singola domanda a scelta chiusa. Verificare che siano presenti in modo **distinto e non accorpato**:
     ```markdown
     - [ ] 97. Non applicabile (fuori target / filtro)
     - [ ] 98. Non so / Senza opinione
     - [ ] 99. Preferisco non rispondere / Rifiuta
     ```
   - Accertare che non vi siano formulazioni forzanti o eliminazione del "Non so" per abbassare artificialmente la mancata risposta.
4. **Verifica delle Istruzioni di Regia Tipografica per l'Intervistatore**:
   - Controllare che tutte le note operative siano racchiuse tra parentesi quadre e scritte in **MAIUSCOLETTO**:
     - `[NON LEGGERE OPZIONI]` per risposte spontanee;
     - `[ROTAZIONE CASUALE DEGLI ITEM]` per prevenire l'effetto primato/recency;
     - `[RISPOSTA SINGOLA]` / `[POSSIBILI FINO A 3 RISPOSTE]`;
     - `[PROBING NEUTRALE: NON SUGGERIRE OPZIONI]`.
5. **Stima del Carico Cognitivo (*Respondent Burden*)**:
   - Stimare la durata complessiva dell'intervista: massimo 8-10 minuti per indagini telefoniche (CATI), massimo 6-8 minuti per indagini web (CAWI). Se supera i 20 item complessi, richiedere lo sfoltimento.

#### 2.2.3 Criteri di Accettazione e Decisione
- **SUPERATO**: Tutte le scale sono bilanciate; assenza totale di double-barreled; codici `97`, `98`, `99` presenti ovunque; istruzioni di regia complete.
- **CON RISERVA**: Lieve asimmetria lessicale correggibile con piccoli ritocchi prima della fase successiva.
- **NON SUPERATO**: Presenza di domande suggestive o viziate; accorpamento di *"Non so"* e *"Rifiuto"*; assenza di istruzioni di rotazione su batterie sensibili.

---

### 2.3 Protocollo H3 — Validazione Audit Metodologico Item-per-Item (`methodology.md`)

```
Responsabile Primario: MET-SR (Ricercatore Metodologo)
Artefatto da collaudare: runs/<caso>/methodology.md
Template di riferimento: templates/methodology_template.md
Skill di riferimento: noto-methodology-audit
Tabella comparativa: examples/confronto_modelli.csv
```

#### 2.3.1 Obiettivo del Collaudo Umano
Accertare che l'audit metodologico svolto da [`methodology-agent`](../.agents/agents/methodology-agent.md) analizzi scientificamente ogni domanda, applichi la griglia standard a 11 colonne, compili le schede analitiche a 12 campi per i quesiti critici e offra **le 3 alternative d'azione** senza imporre scelte arbitrarie che spezzerebbero le serie storiche.

#### 2.3.2 Procedura Operativa Passo-Passo
1. **Verifica della Griglia Sinottica a 11 Colonne**:
   - Aprire la tabella nella Sezione 2 di `methodology.md`.
   - Verificare la presenza delle 11 intestazioni obbligatorie:
     `Codice Item` | `Testo Sintetico` | `Costrutto Indagato` | `Criticità Rilevata` | `Tipo Distorsione Cognitiva` | `Tassonomia Non Risposta Coinvolta` | `Rischio Serie Storica` | `Opzione A (Conservare)` | `Opzione B (Minima)` | `Opzione C (Sostanziale)` | `Raccomandazione Agente`.
   - Accertare che nessun item del questionario sia stato omesso dalla griglia.
2. **Verifica della Completezza delle Schede Analitiche a 12 Campi (Sezione 3)**:
   - Per ogni domanda marcata con criticità media o alta, verificare che sia redatta la scheda a 12 campi:
     1. *Identificativo domanda e testo originario*;
     2. *Costrutto teorico di riferimento*;
     3. *Diagnosi metodologica del difetto*;
     4. *Effetto cognitivo atteso sul rispondente*;
     5. *Impatto sulla non risposta*;
     6. *Rischio comparabilità serie storica*;
     7. *Opzione A — Conservare originale*;
     8. *Opzione B — Riformulazione minima*;
     9. *Opzione C — Ristrutturazione radicale*;
     10. *Valutazione comparativa rischi/benefici*;
     11. *Proposta operativa raccomandata*;
     12. *Protocollo di validazione empirica (pretest / split-ballot)*.
3. **Controllo Linguistico delle Ipotesi di Non Risposta**:
   - Cercare nel testo espressioni vietate come: *"Questa modifica riduce la non risposta"* o *"Migliora la qualità del dato al 100%"*.
   - Verificare che siano usate **esclusivamente formule cautelative**: *"Potenziale mitigazione del rischio di item nonresponse"*, *"Effetto atteso da validare empiricamente tramite split ballot"*.
4. **Valutazione della Tutela delle Serie Storiche**:
   - Valutare se l'Opzione B o C proposta modifica silenziosamente l'oggetto, la polarità o la scala della domanda. Se la domanda è parte di un barometro politico decennale, l'umano deve poter scegliere l'Opzione A (Conservare) proteggendo la comparabilità.
5. **Selezione delle Decisioni Umane da Registrare**:
   - Il metodologo compila la propria decisione puntuale per ciascun item (es. *"Per Q1 scelgo Opzione B; per Q2 scelgo Opzione A per continuità trend; per Q3 scelgo Opzione C con split-ballot al 50%"*).

#### 2.3.3 Criteri di Accettazione e Decisione
- **SUPERATO**: Griglia a 11 colonne integra; schede a 12 campi complete; le 3 opzioni sono realistiche e ben argomentate; linguaggio metodologicamente cauto.
- **CON RISERVA**: L'analisi di una domanda è superficiale; il metodologo richiede all'agente un approfondimento puntuale.
- **NON SUPERATO**: Mancano colonne nella tabella; assenza delle 3 alternative; affermazioni apodittiche non verificate empiricamente.

---

### 2.4 Protocollo H4 — Validazione Screening Compliance Privacy & AI Act (`compliance.md`)

```
Responsabile Primario: DPO-LEG (Data Protection Officer / Consulente Legale)
Co-Tester: MET-SR (Ricercatore Metodologo)
Artefatto da collaudare: runs/<caso>/compliance.md
Template di riferimento: templates/compliance_template.md
Skill di riferimento: noto-compliance-check
```

#### 2.4.1 Obiettivo del Collaudo Umano
Accertare che lo screening preliminare eseguito da [`compliance-agent`](../.agents/agents/compliance-agent.md) abbia mappato esaustivamente il trattamento dei dati personali, isolato i dati particolari ex **Art. 9 GDPR** (opinioni politiche, convinzioni religiose o filosofiche, appartenenza sindacale, dati biometrici o genetici, salute e orientamento sessuale), verificato i rischi di re-identificazione indiretta e individuato tutti i vincoli dell'**AI Act** e le raccomandazioni del Garante Privacy.

#### 2.4.2 Procedura Operativa Passo-Passo
1. **Screening Tabellare Domanda-per-Domanda (Sezione 2)**:
   - Esaminare la tabella di conformità per ciascun quesito del questionario:
     - Identificare se la domanda tocca categorie particolari ex Art. 9 GDPR (in particolare le intenzioni di voto o l'appartenenza a movimenti politici);
     - Controllare la presenza obbligatoria della modalità di uscita:
       ```markdown
       99. Preferisco non rispondere / Rifiuta
       ```
     - Verificare che il rifiuto sia sempre consentito senza alcuna conseguenza o penalizzazione per l'intervistato.
2. **Valutazione del Rischio di Re-Identificazione Indiretta (*Quasi-Identifiers*)**:
   - Ispezionare la batteria delle variabili socio-demografiche: sesso, classe d'età, titolo di studio, professione, comune di residenza o CAP.
   - Accertare se l'incrocio simultaneo di variabili ad alta granularità in campioni locali ristretti consenta di isolare una persona fisica specifica (es. *"Ingegnere donna tra 60 e 65 anni residente nel comune X di 1.200 abitanti"* $\rightarrow$ **RISCHIO DI RE-IDENTIFICAZIONE**).
   - In caso di rischio, prescrivere l'aggregazione delle classi (es. classi di ampiezza demografica del comune o fasce d'età a 10 anni).
3. **Verifica della Formula di Consenso e dell'Informativa Sintetica (Sezione 3)**:
   - Controllare che sia predisposta la formula di informativa breve per interviste telefoniche (CATI) o il link all'informativa estesa per indagini web (CAWI).
   - Verificare che siano esplicitati: Titolare del Trattamento (Noto Sondaggi SRL), Finalità di ricerca statistica aggregata, Base giuridica (consenso esplicito), Diritto di revoca e contatti del DPO.
4. **Verifica della Checklist Preliminare AI Act**:
   - Accertare che la piattaforma sia classificata come sistema AI a supporto (Human-in-the-Loop) e che sia ribadito il divieto assoluto di profilazione automatizzata, emotion recognition o manipolazione psicologica subliminale.
5. **Verifica della Sezione "Punti Bloccanti per il DPO" (Sezione 5)**:
   - Il DPO esamina i punti segnalati dall'agente come bloccanti. Se ci sono rilievi critici non risolvibili in fase redazionale, il DPO emette parere formale condizionante per il proseguo.

#### 2.4.3 Criteri di Accettazione e Decisione
- **SUPERATO**: Tutti i dati Art. 9 sono protetti con codice 99; nessun rischio di re-identificazione sui quasi-identificatori; informativa conforme; punti DPO risolti.
- **CON RISERVA**: Necessario aggregare una variabile demografica o rettificare una dicitura dell'informativa; il DPO annota la prescrizione vincolante.
- **NON SUPERATO**: Mancanza dell'opzione di rifiuto su domande sensibili o politiche; trattamento illecito non coperto da adeguata base giuridica.

---

### 2.5 Protocollo H5 — Validazione Consolidamento Finale e Skip Logic (`final.md`)

```
Responsabile Primario: MET-SR (Ricercatore Metodologo)
Co-Tester: DPO-LEG (DPO per la verifica recepimento prescrizioni)
Artefatto da collaudare: runs/<caso>/final.md
Documenti di riscontro: runs/<caso>/status.md, methodology.md, compliance.md
Template di riferimento: templates/final_template.md
Skill di riferimento: noto-questionnaire-consolidation
```

#### 2.5.1 Obiettivo del Collaudo Umano
Accertare il riscontro biunivoco e matematico tra le decisioni espresse dal ricercatore umano registrate in `status.md` e il testo definitivo consolidato in `final.md`, assicurando l'assenza totale di modifiche arbitrarie non autorizzate e la perfetta tenuta logica dei percorsi di salto (*skip patterns / routing*).

#### 2.5.2 Procedura Operativa Passo-Passo
1. **Riscontro Incrociato 1-a-1 tra Decisioni in `status.md` e Testo in `final.md`**:
   - Aprire il log decisionale della fase `methodology` e `compliance` in `runs/<caso>/status.md`.
   - Per ciascuna modifica approvata dal ricercatore umano (es. *"Approvata Opzione B su Q1 e Opzione A su Q2"*), confrontare riga per riga il testo in `final.md`.
   - **Verifica negativa fondamentale**: Accertare che l'agente consolidatore NON abbia introdotto modifiche formali, lessicali o strutturali su domande per le quali l'umano aveva deliberato di *"Conservare l'originale (Opzione A)"*.
2. **Recepimento delle Prescrizioni di Compliance**:
   - Verificare che tutte le raccomandazioni del DPO (es. inserimento dell'opzione 99, clausola di apertura informativa) siano state trascritte integralmente.
3. **Audit Manuale dell'Albero dei Salti e Condizioni di Filtro (*Skip Logic Walkthrough*)**:
   - Disegnare o tracciare su carta/schermo il grafo delle dipendenze dei filtri:
     - Esempio: Se `Q1 == 2` (Non utilizza i mezzi pubblici), l'intervistato salta a `Q4` (Motivazioni di non utilizzo).
     - Verificare che il rispondente che ha risposto `Q1 == 1` (Utilizza i mezzi) compili `Q2` e `Q3` e salti poi oltre `Q4`.
   - Verificare che nessun ramo logico generi un vicolo cieco (*dead end*), una domanda orfana o una contraddizione semantica (es. chiedere la soddisfazione su un servizio a chi ha dichiarato di non conoscerlo).
4. **Verifica della Mappa delle Variabili e della Tassonomia**:
   - Verificare che l'identificativo di ciascuna variabile (`Q1`, `Q2_A`, `D1`, ecc.) sia univoco, coerente con il codebook e non contenga spazi o caratteri speciali.
   - Verificare che `97`, `98`, `99` siano presenti su tutte le domande pertinenti.

#### 2.5.3 Criteri di Accettazione e Decisione
- **SUPERATO**: Piena coincidenza tra le decisioni in `status.md` e `final.md`; assenza di riscritture arbitrarie; routing esente da difetti logici.
- **CON RISERVA**: Errore minore di battitura nel testo di una domanda rettificabile istantaneamente.
- **NON SUPERATO**: L'agente ha modificato domande senza autorizzazione; errori logici nella matrice dei salti che porterebbero a interviste errate sul campo.

---

### 2.6 Protocollo H6 — Validazione Fieldwork Bridge LimeSurvey TSV (`limesurvey_survey.txt`)

```
Responsabile Primario: TEC-OPS (Operatore Tecnico / Data Scientist)
Co-Tester: FLD-DIR (Responsabile Campo CATI/CAWI)
Script da eseguire: scripts/export_limesurvey.py
Artefatto generato: runs/<caso>/limesurvey_survey.txt
Linter di controllo: scripts/validate_runs.py
Piattaforma di destinazione: LimeSurvey Community Edition (v5.x o v6.x)
```

#### 2.6.1 Obiettivo del Collaudo Umano
Verificare che la procedura di esportazione da Markdown consolidato a tracciato tabellare tab-delimited LimeSurvey (TSV a 14 colonne standard) generi un file sintatticamente perfetto, privo di corruzioni di codifica UTF-8, correttamente importabile su istanza di produzione LimeSurvey senza produrre warning di parsing, e fedele nelle regole di visualizzazione e salti (*ExpressionScript*).

#### 2.6.2 Procedura Operativa Passo-Passo
1. **Esecuzione da Terminale dello Script di Esportazione**:
   - Aprire PowerShell o Bash nel percorso del workspace ed eseguire:
     ```bash
     python scripts/export_limesurvey.py runs/<caso>/final.md -o runs/<caso>/limesurvey_survey.txt
     ```
   - Verificare che l'output da console certifichi l'avvenuta generazione senza errori o eccezioni:
     ```text
     [OK] File LimeSurvey TSV esportato con successo: ...
          Gruppi (G): X, Domande (Q): Y, Totale righe TSV (14 colonne): Z
     ```
2. **Validazione con il Linter Dedicato**:
   - Eseguire il controllo di conformità strutturale:
     ```bash
     python scripts/validate_runs.py runs/<caso>/
     ```
   - Verificare l'emissione del messaggio `[PASS] limesurvey_survey.txt`.
3. **Ispezione Umana del File Tabellare (Tracciato a 14 Colonne)**:
   - Aprire `runs/<caso>/limesurvey_survey.txt` con un editor di testo avanzato (VS Code, Notepad++) visualizzando i caratteri invisibili (tabulazioni `\t` e ritorni a capo `\n`).
   - Verificare che la prima riga contenga esattamente i 14 header standard:
     `id` | `related_id` | `class` | `type/scale` | `name` | `relevance` | `text` | `help` | `language` | `validation` | `mandatory` | `other` | `default` | `same_default`.
   - Controllare a campione 5 righe: accertare che ogni riga abbia esattamente 13 caratteri tabulatore separatori e nessun punto e virgola improprio.
4. **Verifica della Mappatura dei Tipi di Domanda LimeSurvey**:
   - Verificare che le domande a risposta singola abbiano classe `Q` e tipo `L` (Radio list);
   - Verificare che le domande a risposta multipla abbiano tipo `M` (Multiple choice);
   - Verificare che le matrici abbiano tipo `F` o `1` (Dual scale / Array) con sotto-domande (classe `SQ`);
   - Verificare che i codici di uscita `97`, `98`, `99` siano presenti come risposte (classe `A`).
5. **Test di Importazione su Istanza di Staging LimeSurvey (Collaudo Reale)**:
   - Accedere all'interfaccia amministrativa web di LimeSurvey (`https://survey-test.notosondaggi.it` o ambiente locale sandbox);
   - Cliccare su **Crea indagine** $\rightarrow$ scheda **Importa** $\rightarrow$ Selezionare il file `limesurvey_survey.txt` $\rightarrow$ Cliccare su **Importa indagine**;
   - Verificare la schermata di riepilogo: 0 errori critici, corrispondenza esatta del numero di gruppi, domande e risposte create;
   - Eseguire un'anteprima dell'indagine compilando un questionario di test nel browser: verificare che i filtri condizionali nascondano o mostrino le domande in modo fluido.

#### 2.6.3 Criteri di Accettazione e Decisione
- **SUPERATO**: Script eseguito con esito 0; linter `validate_runs.py` emette PASS; importazione in LimeSurvey completata con successo al primo tentativo; anteprima web funzionante.
- **CON RISERVA**: Lieve difetto nella formattazione del testo di aiuto rettificabile dall'editor di LimeSurvey.
- **NON SUPERATO**: Errore di importazione in LimeSurvey (es. separatori mancanti, colonne disallineate, caratteri speciali corrotti); domande o risposte tagliate.

---

### 2.7 Protocollo H7 — Validazione Guida Intervistatore CATI/CAPI (`guida_intervistatore.md`/HTML/Word)

```
Responsabile Primario: FLD-DIR (Responsabile Campo CATI/CAWI)
Co-Tester: TEC-OPS (Operatore Tecnico)
Script da eseguire: scripts/generate_interviewer_guide.py
Artefatti generati: runs/<caso>/guida_intervistatore.md (e .html / .docx)
```

#### 2.7.1 Obiettivo del Collaudo Umano
Verificare che la Guida Intervistatore generata per la sala rilevazione fornisca agli operatori telefonici o faccia-a-faccia uno strumento visivamente chiaro, operativo, privo di ambiguità tipografiche, arricchito di note di probing neutrale e rigoroso nell'impedire forzature sulle opzioni di non risposta.

#### 2.7.2 Procedura Operativa Passo-Passo
1. **Generazione della Guida nei Formati Richiesti**:
   - Da terminale eseguire il generatore automatico:
     ```bash
     python scripts/generate_interviewer_guide.py runs/<caso>/final.md --format both
     ```
   - (Se presente `python-docx` verrà generato anche il file Word `.docx`; in caso contrario, verificare che il generatore esegua il corretto fallback su Markdown e HTML ad alta leggibilità).
2. **Verifica Visiva delle Istruzioni Tipografiche di Somministrazione**:
   - Aprire il file HTML generato in un browser o il file Word/Markdown.
   - Verificare la netta distinzione visiva tra:
     - **Testo da leggere all'intervistato**: Formattato in carattere tondo normale, chiaro e a contrasto elevato;
     - **Istruzioni di regia per l'intervistatore**: Racchiuse in box evidenziati, etichettate con icone e formattate in **MAIUSCOLETTO** (es. `[NON LEGGERE OPZIONI - ATTENDERE RISPOSTA SPONTANEA]`).
3. **Verifica del Protocollo di Probing Neutrale**:
   - Accertare la presenza del callout operativo:
     > *"Se il rispondente esita, non suggerire alcuna opzione. Rileggere la domanda con tono neutro. Se il rispondente ribadisce incertezza, registrare immediatamente 'Non so / Senza opinione' senza insistere."*
4. **Verifica del Divieto Assoluto di Pressioni Deontologiche**:
   - Controllare che la guida rammenti esplicitamente agli operatori telefonici che l'opzione `99 = Preferisco non rispondere` è un diritto garantito dal GDPR e dalla deontologia professionale, e che non devono in nessun caso sollecitare una risposta forzata.
5. **Simulazione Pilota in Sala Rilevazione (*Mock Interview*)**:
   - Assegnare la guida a un intervistatore junior; il Responsabile di Campo simula le risposte di un cittadino (compresi tentativi di interruzione, dichiarazioni di non conoscenza ed esitazioni).
   - Cronometrare il tempo di lettura e verificare che l'intervistatore non inciampi in frasi ambigue o istruzioni confuse.

#### 2.7.3 Criteri di Accettazione e Decisione
- **SUPERATO**: La guida è chiara; distinzione tipografica perfetta; note di probing presenti su ogni domanda complessa; mock interview superata entro i tempi previsti.
- **CON RISERVA**: Note di regia migliorabili per una singola domanda; rettifica manuale immediata.
- **NON SUPERATO**: Mancanza di distinzione tra testo da leggere e istruzioni interne (rischio che l'intervistatore legga le note di regia al telefono); assenza di cautele sul divieto di probing forzato.

---

### 2.8 Protocollo H8 — Validazione Scheda AGCOM Delibera 256/10/CSP (`scheda_agcom.md`)

```
Responsabile Primario: MET-SR (Ricercatore Metodologo)
Co-Tester: TEC-OPS (Data Scientist)
Script da eseguire: scripts/generate_agcom_report.py
Artefatto generato: runs/<caso>/scheda_agcom.md
Linter di controllo: scripts/validate_runs.py
Riferimento Normativo: Delibera AGCOM n. 256/10/CSP (Allegato A) e s.m.i.
```

#### 2.8.1 Obiettivo del Collaudo Umano
Verificare che la Scheda Informativa obbligatoria del sondaggio redatta da [`reporting-agent`](../.agents/agents/reporting-agent.md) e [`scripts/generate_agcom_report.py`](../scripts/generate_agcom_report.py) contenga tutti e 12 i campi previsti dalla normativa di legge, che il margine d'errore statistico sia calcolato correttamente secondo la formula di Gauss al 95% di confidenza, che tutti i consuntivi rechino rigorosamente la marcatura `[DA VERIFICARE SUL CAMPO]` e che tutti i quesiti siano trascritti nella loro formulazione integrale.

#### 2.8.2 Procedura Operativa Passo-Passo
1. **Generazione e Validazione Formale della Scheda**:
   - Per generare la scheda a partire dagli artefatti consolidati del caso:
     ```bash
     python scripts/generate_agcom_report.py runs/<caso> --client "Comune di Pavia" --media "Quotidiano Nazionale"
     ```
   - Per eseguire la validazione formale e normativa di una scheda esistente (senza riscriverla):
     ```bash
     python scripts/generate_agcom_report.py runs/<caso> --check-only
     ```
   - Verificare che il comando restituisca l'esito di conformità `[PASS] Scheda validata al 100% rispetto ai requisiti della Delibera AGCOM 256/10/CSP`.
2. **Controllo Metodologico e Normativo dei 12 Campi di Legge**:
   - Ispezionare riga per riga `scheda_agcom.md` verificando l'integrità dei 12 campi di legge:
     1. **Soggetto realizzatore**: Noto Sondaggi SRL;
     2. **Committente**: Soggetto pubblico o privato finanziatore dell'indagine;
     3. **Acquirente**: Soggetto che ha commissionato l'indagine (spesso coincidente con il committente);
     4. **Data/Periodo di rilevazione**: Date di esecuzione delle interviste;
     5. **Data di pubblicazione/diffusione**: Data e testata/emittente media prevista;
     6. **Popolazione di riferimento**: Descrizione demografica rigorosa (es. *"Popolazione maggiorenne residente nel comune X"*);
     7. **Estensione territoriale**: Limiti geografici campionati;
     8. **Metodo di campionamento**: Descrizione del disegno (probabilistico, stratificato per sesso/età, a quote);
     9. **Rappresentatività e ponderazione**: Criteri di ponderazione campionaria ex-post (es. *"Ponderazione per genere, classi d'età e voto pregresso"*);
     10. **Metodo di raccolta dati**: CATI, CAWI, CAMI o mista con relative percentuali;
     11. **Consistenza numerica del campione e tassi di non risposta**: Numerosità pianificata $n$, contatti totali, rifiuti e sostituzioni;
     12. **Testo integrale di tutti i quesiti**: Trascrizione letterale di ogni domanda senza riassunti giornalistici, con codici `97`, `98`, `99`.
3. **Verifica Matematica Indipendente del Margine d'Errore**:
   - Il ricercatore esegue manualmente il calcolo del margine d'errore campionario teorico al 95% di confidenza (distribuzione normale standard $z = 1.96$ nel caso di massima varianza $p = q = 0.5$):
     $$e = \pm 1.96 \times \sqrt{\frac{0.5 \times 0.5}{n}} = \pm \frac{0.98}{\sqrt{n}}$$
   - Esempio di riscontro numerico:
     - Per $n = 1.000 \rightarrow e = \pm \frac{0.98}{\sqrt{1000}} = \pm \frac{0.98}{31.62} \approx \pm 3.10\%$
     - Per $n = 800 \rightarrow e = \pm \frac{0.98}{28.28} \approx \pm 3.46\%$
     - Per $n = 500 \rightarrow e = \pm \frac{0.98}{22.36} \approx \pm 4.38\%$
   - Confrontare il valore calcolato con quello riportato nel campo 11 della scheda.
4. **Audit Anti-Allucinazione sui Dati a Consuntivo (Fase Pre-Campo)**:
   - Se la scheda viene predisposta prima o durante il fieldwork, verificare che TUTTI i dati numerici a consuntivo (numero contatti effettuati, tasso di rifiuto, interviste complete realizzate) riportino la formula vincolante:
     ```text
     [DA VERIFICARE SUL CAMPO]
     ```
   - **VIOLAZIONE GRAVE**: Se compaiono valori inventati (es. *"Tasso di risposta: 42.3%"* non misurato empiricamente), bocciare immediatamente la scheda.
5. **Verifica Assenza di Commenti o Spin Politico**:
   - Accertare che la scheda non contenga conclusioni analitiche, giudizi di merito o commenti politici, mantenendo la totale neutralità istituzionale imposta da AGCOM.

#### 2.8.3 Criteri di Accettazione e Decisione
- **SUPERATO**: Tutti i 12 campi presenti e conformi; margine d'errore verificato matematicamente; consuntivi marcati `[DA VERIFICARE SUL CAMPO]`; quesiti integrali con 97, 98, 99.
- **CON RISERVA**: Mancata indicazione del mezzo di diffusione (rettificabile prima dell'invio editoriale).
- **NON SUPERATO**: Valori numerici a consuntivo arbitrari o simulati; errore nel calcolo del margine statistico; omissione del testo integrale delle domande.

---

### 2.9 Protocollo H9 — Validazione Ingestione Questionari Storici (`extract_survey_knowledge.py`)

```
Responsabile Primario: MET-SR (Ricercatore Metodologo)
Co-Tester: TEC-OPS (Operatore Tecnico)
Script da eseguire: scripts/extract_survey_knowledge.py
Documento sorgente: file storico in formato .md, .txt, .docx o .pdf
Artefatto generato: knowledge/extracted_<studio>.md o runs/<caso>/extracted_survey.md
Template di riferimento: templates/extracted_survey_template.md
Skill di riferimento: noto-survey-extractor
```

#### 2.9.1 Obiettivo del Collaudo Umano
Accertare che la CLI di estrazione [`scripts/extract_survey_knowledge.py`](../scripts/extract_survey_knowledge.py) analizzi documenti storici non strutturati o semi-strutturati (vecchi report, questionari in Word o PDF), estraendo correttamente ogni item, preservando fedelmente il testo originale e mappando le scale e i codici di uscita secondo la tassonomia della piattaforma (`97/98/99`), corredando il tutto con note di comparabilità storica per non inquinare i barometri longitudinali.

#### 2.9.2 Procedura Operativa Passo-Passo
1. **Esecuzione dell'Estrattore sul File Storico**:
   - Posizionare il file storico in `source/` ed eseguire:
     ```bash
     python scripts/extract_survey_knowledge.py "runs/<caso>/source/questionario_storico.txt" -o "runs/<caso>/extracted_survey.md" --committente "Regione Lombardia" --anno "2023" --verbose
     ```
   - Controllare i log a terminale per verificare quante domande e sezioni sono state riconosciute.
2. **Validazione con il Linter di Repository**:
   - Eseguire il linter formale:
     ```bash
     python scripts/validate_runs.py runs/<caso>/extracted_survey.md
     ```
   - Verificare che non siano segnalati errori strutturali.
3. **Audit Umano della Fedeltà Testuale (Ispezione Riga-per-Riga)**:
   - Aprire a confronto il documento storico originario e il Markdown generato `extracted_survey.md`.
   - Verificare che il testo della domanda non sia stato "normalizzato" o "riformulato" dall'algoritmo: il question-wording storico deve rimanere **identico al 100% all'originale**, compresi eventuali arcaismi o peculiarità terminologiche storiche.
4. **Verifica della Mappatura dei Codici di Non Risposta**:
   - Controllare come sono state tradotte le opzioni di mancata risposta del vecchio questionario:
     - *"Non so"* / *"Non ho opinione"* $\rightarrow$ Deve essere mappato a `98`;
     - *"Rifiuto"* / *"Non risponde"* $\rightarrow$ Deve essere mappato a `99`;
     - Condizioni di salto $\rightarrow$ Devono essere mappate a `97`.
5. **Verifica della Redazione delle Note di Comparabilità**:
   - Ispezionare la Sezione 3 (*Note Metodologiche di Comparabilità per Serie Storiche*):
   - Verificare se sono state evidenziate eventuali differenze metodologiche tra la vecchia indagine e gli standard odierni (es. differente estensione geografica, cambiamento del canale di raccolta da CATI a CAWI).

#### 2.9.3 Criteri di Accettazione e Decisione
- **SUPERATO**: Tutte le domande storiche estratte senza omissioni; fedeltà testuale totale; corretta mappatura dei codici 97, 98, 99; note di comparabilità redatte.
- **CON RISERVA**: Una scala di risposta è stata suddivisa in modo imperfetto; correzione manuale nel Markdown.
- **NON SUPERATO**: Domande perse o troncate; riscrittura non autorizzata dei testi storici; codici di non risposta invertiti o assenti.

---

### 2.10 Protocollo H10 — Validazione Orchestrazione e STOP Gate in Chat (`status.md`)

```
Responsabile Primario: MET-SR (Ricercatore Metodologo)
Interfaccia di interazione: Chat con ai-coordinator (Google Antigravity o Claude Code)
Artefatto da collaudare: runs/<caso>/status.md
Template di riferimento: templates/status_template.md
Workflow esaminati: /nuova-indagine, /revisione-questionario, /audit-singolo
```

#### 2.10.1 Obiettivo del Collaudo Umano
Verificare l'integrità del principio architetturale cardine della piattaforma: **il rispetto rigoroso degli STOP Gate decisionali**. Accertare che l'agente orchestratore [`ai-coordinator`](../.agents/agents/ai-coordinator.md) non proceda mai autonomamente tra una fase e l'altra, presenti al ricercatore sintesi chiare e quesiti aperti, gestisca correttamente le 3 opzioni decisionali umane (APPROVATO, APPROVATO CON MODIFICHE, RIFIUTATO) e registri fedelmente ogni transizione nel file `runs/<caso>/status.md` (basato su [`templates/status_template.md`](../templates/status_template.md)).

#### 2.10.2 Procedura Operativa Passo-Passo
1. **Avvio di un Caso di Collaudo**:
   - Avviare il workflow invocando `/nuova-indagine` o impartendo il prompt iniziale al coordinatore:
     ```text
     Avvia una nuova indagine per il caso 'test-collaudo' basandoti sui materiali in runs/test-collaudo/source/
     ```
   - Verificare che il coordinatore generi immediatamente `runs/test-collaudo/status.md` con stato iniziale `IN CORSO`.
2. **Verifica dello STOP Gate Obbligatorio al Termine della Fase**:
   - Quando lo specialista incaricato (es. `questionnaire-agent`) conclude la stesura dell'artefatto (es. `brief.md` o `questionnaire.md`), verificare che `ai-coordinator`:
     1. Verifichi internamente la conformità formale al template;
     2. Aggiorni lo stato in `status.md` a `IN ATTESA DI APPROVAZIONE`;
     3. Presenti una sintesi chiara in chat con le questioni aperte per il ricercatore;
     4. **SI FERMI TASSATIVAMENTE**, attendendo la replica dell'utente senza avviare la fase successiva.
   - **ERRORE GRAVE**: Se il coordinatore procede autonomamente alla fase successiva senza stop, il test è **FALLITO**.
3. **Collaudo dei 3 Scenari Decisionali Umani**:
   - **Scenario A — Approvazione Piena (`APPROVATO`)**:
     - Il tester risponde in chat: `"Approvato senza modifiche, procedi alla fase successiva"`.
     - Verificare che `status.md` registri lo stato `APPROVATO`, annoti data e revisore e passi alla fase successiva.
   - **Scenario B — Approvazione con Selezione (`APPROVATO CON MODIFICHE / SELEZIONE`)**:
     - Nella fase `methodology`, il tester risponde: `"Approvo Opzione B su Q1, Opzione A su Q2, Opzione C su Q3"`.
     - Verificare che `status.md` memorizzi esattamente tali selezioni nella sezione cronologica prima che il coordinatore incarichi `compliance-agent` o `questionnaire-agent`.
   - **Scenario C — Rifiuto con Richiesta di Riscrittura (`RIFIUTATO / DA REVISIONARE`)**:
     - Il tester risponde: `"Bozza rifiutata: il questionario non include la sezione sui trasporti. Riscrivere la sezione 2"`.
     - Verificare che il coordinatore NON avanzi alla fase successiva, mantenga la fase corrente impostando lo stato su `DA REVISIONARE` in `status.md` e riassegni il compito allo specialista per recepire le correzioni.
4. **Verifica della Coerenza del File `status.md`**:
   - Al termine dell'indagine, aprire `runs/<caso>/status.md` ed eseguire il linter:
     ```bash
     python scripts/validate_runs.py runs/<caso>/status.md
     ```
   - Verificare che la tabella di avanzamento riporti tutte le 5 fasi concluse, che lo stato complessivo sia `COMPLETATO (MODULO A)` e che il registro cronologico contenga traccia inalterabile di ogni decisione presa in chat.

#### 2.10.3 Criteri di Accettazione e Decisione
- **SUPERATO**: L'orchestratore si ferma a ogni singolo gate; registra fedelmente in `status.md` ogni decisione umana; gestisce correttamente approvazione, selezione puntuale e rifiuto; non avanza mai autonomamente.
- **CON RISERVA**: Sintesi in chat prolissa ma comportamento di stop perfettamente rispettato.
- **NON SUPERATO**: Mancato arresto allo STOP Gate; perdita di decisioni umane non trascritte in `status.md`; transizione indebita tra fasi non validate.

---

## 3. Master Checklist Tabellare Esecutiva a Crocette

Le seguenti tabelle operative devono essere stampate o compilate digitalmente dal team di ricerca per ciascuna indagine condotta sulla piattaforma. Ogni punto di verifica deve recare la spunta esplicita dell'esito:
- **`[ ] SUPERATO`**: Requisito metodologico o tecnico pienamente soddisfatto;
- **`[ ] CON RISERVA`**: Requisito soddisfatto con rilievi minori documentati nelle note (non bloccanti);
- **`[ ] NON SUPERATO`**: Non conformità critica o bloccante che impedisce il passaggio al fieldwork.

---

### 3.1 Tabella di Collaudo Modulo A (Protocolli H1 – H5)

```
ID Caso: ____________________________________    Data Sessione: ____________________
Ricercatore Responsabile (MET-SR): _________    DPO / Legal Reviewer (DPO-LEG): ____
```

| ID Check | Protocollo | Ruolo | Oggetto del Controllo di Qualità | Esito Verifica | Firma & Data | Note di Non Conformità / Rilievi |
| :---: | :---: | :---: | :--- | :---: | :---: | :--- |
| **H1.1** | H1 - Brief | `MET-SR` | Costrutti latenti tradotti in modo scientifico e privi di framing del committente | `[ ] SUPERATO`<br>`[ ] CON RISERVA`<br>`[ ] NON SUPERATO` | | |
| **H1.2** | H1 - Brief | `MET-SR` | Date, delibere, fondi e norme non accertati marcati con `[DA VERIFICARE]` | `[ ] SUPERATO`<br>`[ ] CON RISERVA`<br>`[ ] NON SUPERATO` | | |
| **H1.3** | H1 - Brief | `MET-SR` | Popolazione target, estensione geografica e canali di contatto definiti chiaramente | `[ ] SUPERATO`<br>`[ ] CON RISERVA`<br>`[ ] NON SUPERATO` | | |
| **H1.4** | H1 - Brief | `MET-SR` | Domande per il committente formulate per colmare lacune metodologiche reali | `[ ] SUPERATO`<br>`[ ] CON RISERVA`<br>`[ ] NON SUPERATO` | | |
| **H2.1** | H2 - Quest | `MET-SR` | Assenza assoluta di domande tendenziose (*leading*) o allusive | `[ ] SUPERATO`<br>`[ ] CON RISERVA`<br>`[ ] NON SUPERATO` | | |
| **H2.2** | H2 - Quest | `MET-SR` | Assenza di item a doppio bersaglio (*double-barreled*) | `[ ] SUPERATO`<br>`[ ] CON RISERVA`<br>`[ ] NON SUPERATO` | | |
| **H2.3** | H2 - Quest | `MET-SR` | Scale di valutazione bilanciate (Likert 4 o 5 punti con perfetta simmetria) | `[ ] SUPERATO`<br>`[ ] CON RISERVA`<br>`[ ] NON SUPERATO` | | |
| **H2.4** | H2 - Quest | `MET-SR` | Presenza distinta e non accorpata dei codici `97` (N/A), `98` (Non so), `99` (Rifiuto) | `[ ] SUPERATO`<br>`[ ] CON RISERVA`<br>`[ ] NON SUPERATO` | | |
| **H2.5** | H2 - Quest | `FLD-DIR` | Istruzioni tipografiche di regia presenti in **MAIUSCOLETTO** (`[NON LEGGERE]`, ecc.) | `[ ] SUPERATO`<br>`[ ] CON RISERVA`<br>`[ ] NON SUPERATO` | | |
| **H2.6** | H2 - Quest | `FLD-DIR` | Carico cognitivo stimato compatibile con i tempi massimi di indagine (CATI/CAWI) | `[ ] SUPERATO`<br>`[ ] CON RISERVA`<br>`[ ] NON SUPERATO` | | |
| **H3.1** | H3 - Method | `MET-SR` | Griglia sinottica a 11 colonne presente, completa e priva di omissioni | `[ ] SUPERATO`<br>`[ ] CON RISERVA`<br>`[ ] NON SUPERATO` | | |
| **H3.2** | H3 - Method | `MET-SR` | Schede analitiche a 12 campi compilate per ogni quesito critico | `[ ] SUPERATO`<br>`[ ] CON RISERVA`<br>`[ ] NON SUPERATO` | | |
| **H3.3** | H3 - Method | `MET-SR` | Presenza rigorosa delle 3 alternative d'azione per item (Opzioni A, B, C) | `[ ] SUPERATO`<br>`[ ] CON RISERVA`<br>`[ ] NON SUPERATO` | | |
| **H3.4** | H3 - Method | `MET-SR` | Tutela esplicita della comparabilità delle serie storiche e trend | `[ ] SUPERATO`<br>`[ ] CON RISERVA`<br>`[ ] NON SUPERATO` | | |
| **H3.5** | H3 - Method | `MET-SR` | Assenza di affermazioni apodittiche non verificate empiricamente | `[ ] SUPERATO`<br>`[ ] CON RISERVA`<br>`[ ] NON SUPERATO` | | |
| **H4.1** | H4 - Compl | `DPO-LEG` | Isolamento e protezione rigorosa dei dati particolari ex Art. 9 GDPR (es. voto) | `[ ] SUPERATO`<br>`[ ] CON RISERVA`<br>`[ ] NON SUPERATO` | | |
| **H4.2** | H4 - Compl | `DPO-LEG` | Garanzia assoluta dell'opzione `99=Preferisco non rispondere` sui dati particolari | `[ ] SUPERATO`<br>`[ ] CON RISERVA`<br>`[ ] NON SUPERATO` | | |
| **H4.3** | H4 - Compl | `DPO-LEG` | Assenza di rischio di re-identificazione indiretta (*quasi-identifiers*) | `[ ] SUPERATO`<br>`[ ] CON RISERVA`<br>`[ ] NON SUPERATO` | | |
| **H4.4** | H4 - Compl | `DPO-LEG` | Testo dell'informativa privacy conforme e approvato dal DPO | `[ ] SUPERATO`<br>`[ ] CON RISERVA`<br>`[ ] NON SUPERATO` | | |
| **H4.5** | H4 - Compl | `DPO-LEG` | Risoluzione formale di tutti i punti bloccanti segnalati per il DPO | `[ ] SUPERATO`<br>`[ ] CON RISERVA`<br>`[ ] NON SUPERATO` | | |
| **H5.1** | H5 - Final | `MET-SR` | Riscontro 1-a-1 perfetto tra decisioni registrate in `status.md` e testo in `final.md` | `[ ] SUPERATO`<br>`[ ] CON RISERVA`<br>`[ ] NON SUPERATO` | | |
| **H5.2** | H5 - Final | `MET-SR` | Assenza totale di modifiche arbitrarie sulle domande con delibera di "Conservare" | `[ ] SUPERATO`<br>`[ ] CON RISERVA`<br>`[ ] NON SUPERATO` | | |
| **H5.3** | H5 - Final | `MET-SR` | Verifica logica completa dell'albero dei salti (*routing / skip logic*) | `[ ] SUPERATO`<br>`[ ] CON RISERVA`<br>`[ ] NON SUPERATO` | | |
| **H5.4** | H5 - Final | `MET-SR` | Univocità delle etichette delle variabili e presenza codici `97`, `98`, `99` | `[ ] SUPERATO`<br>`[ ] CON RISERVA`<br>`[ ] NON SUPERATO` | | |

---

### 3.2 Tabella di Collaudo Tooling e Bridge Operativi (Protocolli H6 – H9)

```
ID Caso: ____________________________________    Data Sessione: ____________________
Responsabile Sala Fieldwork (FLD-DIR): _____    Operatore Tecnico (TEC-OPS): _______
```

| ID Check | Protocollo | Ruolo | Oggetto del Controllo di Qualità | Esito Verifica | Firma & Data | Note di Non Conformità / Rilievi |
| :---: | :---: | :---: | :--- | :---: | :---: | :--- |
| **H6.1** | H6 - Lime | `TEC-OPS` | Esecuzione CLI `export_limesurvey.py` conclusa con esito 0 e senza errori | `[ ] SUPERATO`<br>`[ ] CON RISERVA`<br>`[ ] NON SUPERATO` | | |
| **H6.2** | H6 - Lime | `TEC-OPS` | File `limesurvey_survey.txt` conforme a 14 colonne standard validate da linter | `[ ] SUPERATO`<br>`[ ] CON RISERVA`<br>`[ ] NON SUPERATO` | | |
| **H6.3** | H6 - Lime | `TEC-OPS` | Tipologie di domanda LimeSurvey (L, M, F, 1) e codici 97, 98, 99 corretti | `[ ] SUPERATO`<br>`[ ] CON RISERVA`<br>`[ ] NON SUPERATO` | | |
| **H6.4** | H6 - Lime | `TEC-OPS` | Test di importazione reale su LimeSurvey CE riuscito senza avvisi o crash | `[ ] SUPERATO`<br>`[ ] CON RISERVA`<br>`[ ] NON SUPERATO` | | |
| **H6.5** | H6 - Lime | `FLD-DIR` | Anteprima web dell'indagine funzionante con routing reattivo | `[ ] SUPERATO`<br>`[ ] CON RISERVA`<br>`[ ] NON SUPERATO` | | |
| **H7.1** | H7 - Guida | `TEC-OPS` | Esecuzione CLI `generate_interviewer_guide.py` conclusa con successo | `[ ] SUPERATO`<br>`[ ] CON RISERVA`<br>`[ ] NON SUPERATO` | | |
| **H7.2** | H7 - Guida | `FLD-DIR` | Netta distinzione tipografica tra testo da leggere e note di regia [MAIUSCOLETTO] | `[ ] SUPERATO`<br>`[ ] CON RISERVA`<br>`[ ] NON SUPERATO` | | |
| **H7.3** | H7 - Guida | `FLD-DIR` | Presenza del box sul probing neutrale e divieto di forzatura non risposte | `[ ] SUPERATO`<br>`[ ] CON RISERVA`<br>`[ ] NON SUPERATO` | | |
| **H7.4** | H7 - Guida | `FLD-DIR` | Simulazione d'intervista pilota (*mock interview*) completata con esito positivo | `[ ] SUPERATO`<br>`[ ] CON RISERVA`<br>`[ ] NON SUPERATO` | | |
| **H8.1** | H8 - AGCOM | `MET-SR` | Presenza di tutti i 12 campi obbligatori di legge ex Delibera 256/10/CSP | `[ ] SUPERATO`<br>`[ ] CON RISERVA`<br>`[ ] NON SUPERATO` | | |
| **H8.2** | H8 - AGCOM | `TEC-OPS` | Margine d'errore teorico al 95% verificato indipendentemente con formula di Gauss | `[ ] SUPERATO`<br>`[ ] CON RISERVA`<br>`[ ] NON SUPERATO` | | |
| **H8.3** | H8 - AGCOM | `MET-SR` | Consuntivi pre-campo recanti categoricamente `[DA VERIFICARE SUL CAMPO]` | `[ ] SUPERATO`<br>`[ ] CON RISERVA`<br>`[ ] NON SUPERATO` | | |
| **H8.4** | H8 - AGCOM | `MET-SR` | Trascrizione integrale di tutti i quesiti con codici standard `97`, `98`, `99` | `[ ] SUPERATO`<br>`[ ] CON RISERVA`<br>`[ ] NON SUPERATO` | | |
| **H8.5** | H8 - AGCOM | `MET-SR` | Assenza totale di commenti editoriali o interpretazioni politiche | `[ ] SUPERATO`<br>`[ ] CON RISERVA`<br>`[ ] NON SUPERATO` | | |
| **H9.1** | H9 - Estratt | `TEC-OPS` | Esecuzione CLI `extract_survey_knowledge.py` su file sorgente storico (.txt/.md/.docx/.pdf) | `[ ] SUPERATO`<br>`[ ] CON RISERVA`<br>`[ ] NON SUPERATO` | | |
| **H9.2** | H9 - Estratt | `MET-SR` | Rispetto integrale del template `templates/extracted_survey_template.md` | `[ ] SUPERATO`<br>`[ ] CON RISERVA`<br>`[ ] NON SUPERATO` | | |
| **H9.3** | H9 - Estratt | `MET-SR` | Fedeltà testuale al 100% rispetto al questionario storico originario | `[ ] SUPERATO`<br>`[ ] CON RISERVA`<br>`[ ] NON SUPERATO` | | |
| **H9.4** | H9 - Estratt | `MET-SR` | Mappatura coerente delle vecchie modalità verso `97`, `98`, `99` | `[ ] SUPERATO`<br>`[ ] CON RISERVA`<br>`[ ] NON SUPERATO` | | |
| **H9.5** | H9 - Estratt | `MET-SR` | Redazione delle note di comparabilità metodologica per serie storiche | `[ ] SUPERATO`<br>`[ ] CON RISERVA`<br>`[ ] NON SUPERATO` | | |

---

### 3.3 Tabella di Collaudo Governance e Interazione Chat (Protocollo H10)

```
ID Caso: ____________________________________    Data Sessione: ____________________
Supervisore del Workflow (MET-SR): _________    Piattaforma: [ ] Antigravity  [ ] Claude Code
```

| ID Check | Protocollo | Ruolo | Oggetto del Controllo di Qualità | Esito Verifica | Firma & Data | Note di Non Conformità / Rilievi |
| :---: | :---: | :---: | :--- | :---: | :---: | :--- |
| **H10.1** | H10 - Orch | `MET-SR` | Inizializzazione corretta del caso con creazione cartelle e `status.md` | `[ ] SUPERATO`<br>`[ ] CON RISERVA`<br>`[ ] NON SUPERATO` | | |
| **H10.2** | H10 - Orch | `MET-SR` | Rispetto tassativo dello STOP Gate al termine di ogni fase senza scavalcamento | `[ ] SUPERATO`<br>`[ ] CON RISERVA`<br>`[ ] NON SUPERATO` | | |
| **H10.3** | H10 - Orch | `MET-SR` | Gestione impeccabile dello scenario `APPROVATO` con transizione ordinata | `[ ] SUPERATO`<br>`[ ] CON RISERVA`<br>`[ ] NON SUPERATO` | | |
| **H10.4** | H10 - Orch | `MET-SR` | Gestione corretta dello scenario `APPROVATO CON MODIFICHE` (selezioni registrate) | `[ ] SUPERATO`<br>`[ ] CON RISERVA`<br>`[ ] NON SUPERATO` | | |
| **H10.5** | H10 - Orch | `MET-SR` | Gestione corretta dello scenario `RIFIUTATO` con riassegnazione allo specialista | `[ ] SUPERATO`<br>`[ ] CON RISERVA`<br>`[ ] NON SUPERATO` | | |
| **H10.6** | H10 - Orch | `MET-SR` | Registro cronologico delle decisioni in `status.md` costantemente allineato | `[ ] SUPERATO`<br>`[ ] CON RISERVA`<br>`[ ] NON SUPERATO` | | |

---

## 4. Modulo di Registrazione Anomalie e Riconciliazione (Bug & Methodological Deviation Report)

### 4.1 Workflow di Gestione dell'Anomalia e Classificazione di Gravità

Nel caso in cui uno dei controlli umani evidenzi una non conformità, il tester **deve bloccare l'avanzamento della pipeline** e aprire una scheda formale di anomalia.  
Le anomalie sono classificate su tre livelli di gravità:

```
┌───────────────────────────┐
│ LIVELLO 1 — BLOCCANTE     │ ➔ Viola legge (GDPR, AGCOM), dati fittizi, alterazione serie storiche.
├───────────────────────────┤    BLOCCA IL CAMPO IMMEDIATAMENTE.
│ LIVELLO 2 — CRITICA       │ ➔ Bias di formulazione, salto logico difettoso, formato TSV errato.
├───────────────────────────┤    RICHIEDE RE-INTERVENTO DELL'AGENTE SPECIALISTA.
│ LIVELLO 3 — MINORE        │ ➔ Refuso lessicale, imperfezione grafica, nota di regia da rifinire.
└───────────────────────────┘    CORREGGIBILE IN LINEA DAL RICERCATORE.
```

---

### 4.2 Modello di Scheda Segnalazione Non Conformità

Compilare una scheda per ciascuna anomalia riscontrata:

```markdown
================================================================================
SCHEDA DI SEGNALAZIONE NON CONFORMITÀ METODOLOGICA / TECNICA
Numero Progressivo Anomalia: NC-______-2026
================================================================================

1. METADATI DI SEGNALAZIONE
- ID Caso di Studio: ___________________________________________________________
- Protocollo Coinvolto: [ ] H1  [ ] H2  [ ] H3  [ ] H4  [ ] H5  [ ] H6  [ ] H7  [ ] H8  [ ] H9  [ ] H10
- ID Check Fallito: (es. H2.4, H4.1, H8.3) ___________________________________
- Data e Ora Rilevazione: _____________________________________________________
- Segnalatore (Nome e Ruolo): __________________________________________________

2. CLASSIFICAZIONE DELLA NON CONFORMITÀ
- Tipologia:
  [ ] Bias Cognitivo / Suggestione di Risposta
  [ ] Violazione Privacy / Mancanza Codice 99 su Dato Art. 9 GDPR
  [ ] Generazione Fittizia di Dati / Assenza marcatura [DA VERIFICARE SUL CAMPO]
  [ ] Difetto Logico nei Salti di Routing / Dead End
  [ ] Errore Formale Tracciato LimeSurvey / Corruzione TSV
  [ ] Difetto Istruzioni di Regia Guida Intervistatore
  [ ] Discrepanza Rispetto alle Decisioni Umane in status.md
  [ ] Altro (specificare): _____________________________________________________
- Livello di Gravità:
  [ ] LIVELLO 1 — BLOCCANTE (Fieldwork congelato)
  [ ] LIVELLO 2 — CRITICA (Rilavorazione agente richiesta)
  [ ] LIVELLO 3 — MINORE (Correzione editoriale semplice)

3. DESCRIZIONE DETTAGLIATA DEL RILIEVO
- Quesito o File Coinvolto: ____________________________________________________
- Testo / Comportamento Errato Rilevato:
  "____________________________________________________________________________
   ____________________________________________________________________________"
- Motivazione Metodologica / Normativa della Non Conformità:
  "____________________________________________________________________________
   ____________________________________________________________________________"

4. AZIONE CORRETTIVA PRESCRITTA DAL RICERCATORE
- Indicazioni impartite all'agente o all'operatore per la risoluzione:
  "____________________________________________________________________________
   ____________________________________________________________________________"

5. VERIFICA DI CHIUSURA E RICONCILIAZIONE
- Data di Riesame: ____________________________________________________________
- Esito Post-Correzione: [ ] CONFORME (Chiusa)   [ ] NON RISOLTA (Riassegnata)
- Firma del Ricercatore / DPO per Chiusura: ____________________________________
================================================================================
```

---

## 5. Verbale Finale di Omologazione al Fieldwork

Al termine dell'esecuzione dei 10 protocolli di test umano e dopo aver verificato che tutte le anomalie di Livello 1 e 2 siano state completamente risolte e chiuse, il Comitato di Ricerca redige e sottoscrive il **Verbale Finale di Omologazione al Fieldwork**.

```markdown
================================================================================
NOTO SONDAGGI SRL — ATTO DI OMOLOGAZIONE METODOLOGICA AL FIELDWORK
Riferimento Indagine: runs/<caso>/ 
Titolo Studio: _________________________________________________________________
Committente: ___________________________________________________________________
Data di Chiusura Modulo A: _____________________________________________________
================================================================================

I sottoscritti, nelle rispettive qualità professionali e scientifiche:

1. IL RICERCATORE METODOLOGO SENIOR (MET-SR)
   Attesta che il questionario consolidato in 'runs/<caso>/final.md' rispetta
   integralmente i principi di neutralità scientifica, assenza di direzionalità,
   bilanciamento delle scale e tutela delle serie storiche, e che tutte le opzioni
   di mancata risposta (97, 98, 99) sono presenti e conformi alla deontologia di ricerca.

   Firma: ____________________________________    Data: ________________________

2. IL DATA PROTECTION OFFICER / CONSULENTE PRIVACY (DPO-LEG)
   Attesta che il trattamento dei dati personali connesso all'indagine è conforme
   al Regolamento UE 2016/679 (GDPR), che i dati particolari ex Art. 9 sono
   adeguatamente protetti dal diritto di rifiuto (codice 99) e che l'informativa
   pre-intervista è idonea alla somministrazione.

   Firma: ____________________________________    Data: ________________________

3. IL RESPONSABILE DI SALA FIELDWORK CATI/CAWI (FLD-DIR)
   Attesta che la Guida Intervistatore è idonea alla somministrazione in sala,
   che il tempo medio previsto non eccede i limiti di tollerabilità del rispondente
   e che gli operatori sono istruiti sul divieto di probing forzato.

   Firma: ____________________________________    Data: ________________________

4. L'OPERATORE TECNICO / DATA SCIENTIST (TEC-OPS)
   Attesta che il file 'limesurvey_survey.txt' è stato validato e testato su
   LimeSurvey senza errori di parsing e che la bozza della Scheda AGCOM è pronta
   per il consuntivo e il deposito istituzionale ex Delibera 256/10/CSP.

   Firma: ____________________________________    Data: ________________________

AUTORIZZAZIONE DEFINITIVA ALLA SOMMINISTRAZIONE EMPIRICA SUL CAMPO:
[  ] CONCESSA     [  ] SOSPESA     [  ] NEGATA

Note della Direzione di Ricerca:
________________________________________________________________________________
________________________________________________________________________________
================================================================================
```
