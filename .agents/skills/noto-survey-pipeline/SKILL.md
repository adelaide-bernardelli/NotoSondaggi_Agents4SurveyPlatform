---
name: noto-survey-pipeline
description: Coordina uno studio survey dal brief o questionario esistente fino alla versione finale consolidata con agenti specializzati, approvazioni umane in chat, tracciabilita in runs/<caso>/status.md e protezione dei dati.
---

# Skill: `noto-survey-pipeline` — Orchestrazione del Caso e Gestione Stato (Modulo A)

## Scopo e Chi la Utilizza
- **Agente primario**: `ai-coordinator`
- **Invocazione diretta**: utilizzabile anche dal ricercatore umano tramite `/noto-survey-pipeline` per avviare o riprendere un caso in `runs/<caso>/`.
- **Template di riferimento**: `templates/status_template.md` -> `runs/<caso>/status.md`.

---

## Principi Fondamentali di Orchestrazione
1. **Separazione netta dei ruoli**: `ai-coordinator` governa il processo e gestisce `runs/<caso>/status.md`, ma **non redige mai in prima persona** `brief.md`, `questionnaire.md`, `methodology.md`, `compliance.md` o `final.md`. Ogni artefatto è delegato allo specialista competente.
2. **Approvazione umana in chat (senza script esterni)**: ogni passaggio di fase richiede una decisione esplicita del ricercatore umano in chat (`APPROVATO`, `APPROVATO CON MODIFICHE / SELEZIONE`, `RIFIUTATO / DA REVISIONARE`). Tutte le decisioni vengono registrate da `ai-coordinator` in `runs/<caso>/status.md`.
3. **Esecuzione a singola fase (Gate-by-Gate)**: viene eseguita una sola fase alla volta; al termine della fase l'orchestratore presenta il riepilogo al ricercatore e **si ferma**.

---

## Procedura Operativa Step-by-Step (Modulo A)

### Passo 0 — Lettura Regole e Inizializzazione del Caso
1. Leggi `AGENTS.md` (o `CLAUDE.md`) e verifica se esiste già `runs/<caso>/status.md`.
2. Se il caso è nuovo:
   - Crea le cartelle `runs/<caso>/` e `runs/<caso>/source/`.
   - Copia il documento di input (es. `examples/brief_demo.md`, `examples/questionario_demo.md` o file indicato dall'utente) dentro `runs/<caso>/source/` senza mai modificarlo.
   - Crea `runs/<caso>/status.md` copiando la struttura di `templates/status_template.md` e compilando i metadati iniziali (`ID Caso`, `Workflow attivo`, `Documento di input`, `Data di apertura`, `Fase attiva corrente`).
3. Se il caso è già avviato:
   - Leggi `runs/<caso>/status.md` per identificare la fase corrente e verificare che la fase precedente risulti `APPROVATO` o `APPROVATO CON SELEZIONE`.

### Passo 1 — Fase `brief` (Solo per workflow `nuova-indagine`)
- **Delega**: incarica `questionnaire-agent` di eseguire la skill `noto-brief-structuring` a partire da `runs/<caso>/source/<file>` per produrre `runs/<caso>/brief.md` (usando `templates/brief_template.md`).
- **Verifica del Coordinatore**: controlla che `runs/<caso>/brief.md` non contenga dati inventati su campione, metodo o obiettivi e che i fatti esterni siano marcati `[DA VERIFICARE]`.
- **Gate Umano**: aggiorna `runs/<caso>/status.md` (`Stato fase corrente: IN ATTESA DI APPROVAZIONE`), mostra al ricercatore le domande aperte del brief e **FERMATI** in attesa di approvazione in chat.
- **Registrazione**: ricevuta la risposta del ricercatore, annota decisione, revisore, data e risposte alle domande aperte in `runs/<caso>/status.md`.

### Passo 2 — Fase `questionnaire` (Solo per workflow `nuova-indagine`)
- **Delega**: incarica `questionnaire-agent` di eseguire la skill `noto-questionnaire-drafting` usando `runs/<caso>/brief.md` approvato e le note in `runs/<caso>/status.md`, producendo `runs/<caso>/questionnaire.md` (secondo `templates/questionnaire_template.md`).
- **Verifica del Coordinatore**: controlla che ogni domanda sia legata a un obiettivo del brief, abbia codici distinti per *Non so*, *Rifiuto* e *Non applicabile* e tuteli eventuali serie storiche.
- **Gate Umano**: aggiorna `runs/<caso>/status.md`, presenta la bozza al ricercatore e **FERMATI** in attesa di approvazione in chat.
- **Registrazione**: ricevuta la risposta del ricercatore, annota decisione, revisore, data ed eventuali indicazioni o modifiche richieste in `runs/<caso>/status.md`.

### Passo 3 — Fase `methodology` (Per tutti i workflow; prima fase per `revisione-questionario`)
- **Delega**: incarica `methodology-agent` di eseguire la skill `noto-methodology-audit` sul questionario (`runs/<caso>/questionnaire.md` oppure `runs/<caso>/source/<file>` se in modalità revisione), producendo `runs/<caso>/methodology.md` (secondo `templates/methodology_template.md`).
- **Verifica del Coordinatore**: controlla l'allineamento delle 11 colonne della griglia e dei 12 campi delle schede analitiche, la presenza delle 3 alternative (*Opzione A: Conservare*, *Opzione B: Modifica minima*, *Opzione C: Revisione sostanziale*), la distinzione dei tipi di non risposta e la formulazione degli effetti attesi come *ipotesi da testare*.
- **Gate Umano**: aggiorna `runs/<caso>/status.md`, presenta le criticità e chiedi al ricercatore umano di indicare quali opzioni (A, B o C) approvare per ciascuna domanda. **FERMATI**.
- **Registrazione**: trascrivi fedelmente le scelte domanda-per-domanda del ricercatore in `runs/<caso>/status.md`.

### Passo 4 — Fase `compliance`
- **Delega**: incarica `compliance-agent` di eseguire la skill `noto-compliance-check` producendo `runs/<caso>/compliance.md` (secondo `templates/compliance_template.md`).
- **Verifica del Coordinatore**: controlla che siano censiti i potenziali dati ex Art. 9 GDPR (es. opinioni politiche), i rischi di identificazione indiretta e i punti bloccanti da sottoporre a DPO/legale, senza alcuna falsa attestazione di conformità legale.
- **Gate Umano**: aggiorna `runs/<caso>/status.md`, sottoponi i punti aperti al ricercatore umano e **FERMATI** in attesa di decisione.
- **Registrazione**: ricevuta la risposta del ricercatore (e/o le indicazioni del DPO), annota decisione, revisore, data e le prescrizioni privacy/GDPR approvate da recepire in `final.md` all'interno di `runs/<caso>/status.md`.

### Passo 5 — Fase `final`
- **Delega**: incarica `questionnaire-agent` di eseguire la skill `noto-questionnaire-consolidation` per produrre `runs/<caso>/final.md` (usando `templates/final_template.md`) e generare la struttura indagine per LimeSurvey `runs/<caso>/limesurvey_survey.txt` (tramite `scripts/export_limesurvey.py`), integrando **esclusivamente** le modifiche metodologiche e di compliance approvate e registrate in `runs/<caso>/status.md`.
- **Verifica del Coordinatore**: controlla la completezza della tabella di tracciabilità delle modifiche, dei filtri/*skip*, dei codici *Non so / Rifiuto / Non applicabile*, del piano di *pretest / pilot* e la corretta generazione del tracciato TSV a 14 colonne `runs/<caso>/limesurvey_survey.txt` (validato tramite `scripts/validate_runs.py`).
- **Gate Umano Finale**: aggiorna `runs/<caso>/status.md`, presenta `runs/<caso>/final.md` e l'avvenuta esportazione LimeSurvey al ricercatore per l'approvazione conclusiva del Modulo A e **FERMATI**.
- **Chiusura Modulo A**: dopo l'approvazione finale in chat, imposta `Fase attiva corrente: COMPLETATO (MODULO A)` in `runs/<caso>/status.md`. Ricorda sempre che il caricamento su LimeSurvey e l'avvio del fieldwork restano esterni a questa procedura.
