---
name: audit-singolo
description: Esegue in modo mirato il solo audit metodologico (methodology) oppure la sola verifica preliminare privacy/AI Act (compliance) su un documento fornito dal ricercatore.
---

# Workflow: Audit Singolo Mirato (`methodology` oppure `compliance`)

Questo workflow consente al ricercatore umano di eseguire **una singola verifica specialistica puntuale** su un questionario o documento di ricerca senza dover percorrere l'intera pipeline multi-fase:
- **Modalità A — Solo Audit Metodologico (`methodology`)**: tramite `methodology-agent` e la skill `noto-methodology-audit`.
- **Modalità B — Solo Screening Compliance (`compliance`)**: tramite `compliance-agent` e la skill `noto-compliance-check`.

## Parametri di Avvio
- **Argomenti ricevuti (`$ARGUMENTS` / messaggio utente)**: verifica se il ricercatore ha indicato `<caso>`, il tipo di audit (`methodology` o `compliance`) e il documento in input. Se uno o più parametri mancano, **non inventarli**: chiedili al ricercatore prima di inizializzare `runs/<caso>/`.
- **ID Caso (`<caso>`)**: identificativo alfanumerico della cartella in `runs/<caso>/` (es. `audit-test`).
- **Tipo di audit richiesto**: `methodology` oppure `compliance` (se non specificato dall'utente, `ai-coordinator` chiede quale dei due eseguire prima di procedere).
- **Documento in input**: percorso del file da analizzare (es. `examples/questionario_demo.md`).

---

## Procedura Operativa

### Passo 1 — Inizializzazione (`ai-coordinator`)
1. Leggi `AGENTS.md` / `CLAUDE.md`.
2. Crea `runs/<caso>/source/` e copia il documento fornito in `runs/<caso>/source/` senza modificarlo.
3. Crea `runs/<caso>/status.md` usando `templates/status_template.md`, impostando:
   - `Workflow attivo: audit-singolo`
   - `Fase attiva corrente`: `methodology` oppure `compliance` (contrassegnando le altre fasi non richieste come `SALTATA`).

### Passo 2 — Esecuzione dell'Audit Mirato
- **Se richiesto Audit Metodologico (`methodology`)**:
  - `ai-coordinator` delega a `methodology-agent` l'esecuzione della skill `noto-methodology-audit` sul file in `runs/<caso>/source/`.
  - `methodology-agent` produce `runs/<caso>/methodology.md` conforme a `templates/methodology_template.md` (con la griglia a 11 colonne, le schede a 12 campi e le 3 alternative A/B/C per ciascun item).
- **Se richiesto Screening Compliance (`compliance`)**:
  - `ai-coordinator` delega a `compliance-agent` l'esecuzione della skill `noto-compliance-check` sul file in `runs/<caso>/source/`.
  - `compliance-agent` produce `runs/<caso>/compliance.md` conforme a `templates/compliance_template.md` (con screening Art. 9 GDPR, rischi di identificazione indiretta, checklist AI Act e blocchi per DPO/legale).

### Passo 3 — Verifica Qualità e Consegna al Ricercatore (STOP)
1. `ai-coordinator` verifica che l'artefatto prodotto (`runs/<caso>/methodology.md` o `runs/<caso>/compliance.md`) rispetti integralmente il template e le regole di `AGENTS.md` / `CLAUDE.md`.
2. Aggiorna `runs/<caso>/status.md` impostando la fase su `IN ATTESA DI APPROVAZIONE`.
3. Presenta al ricercatore umano in chat la sintesi dei risultati e chiede se desidera:
   - registrare l'approvazione e chiudere l'audit singolo; oppure
   - proseguire attivando anche il secondo controllo (`compliance` o `methodology`) e il consolidamento finale (`final.md`).
