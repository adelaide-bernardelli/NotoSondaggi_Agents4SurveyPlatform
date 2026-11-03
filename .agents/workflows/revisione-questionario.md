---
name: revisione-questionario
description: Avvia o prosegue la revisione di un questionario gia esistente (methodology -> compliance -> final) preservando la fonte originale in runs/<caso>/source/ e richiedendo approvazione umana in chat ad ogni fase.
---

# Workflow: Revisione Questionario Esistente (`methodology -> compliance -> final`)

Questo workflow guida la revisione metodologica, la verifica preliminare di compliance e il consolidamento finale a partire da un **questionario già redatto o storico** di **Noto Sondaggi SRL**.
Le fasi `brief` e `questionnaire` vengono contrassegnate come `SALTATA` in `runs/<caso>/status.md` e il processo parte direttamente da `methodology`.

## Parametri di Avvio
- **Argomenti ricevuti (`$ARGUMENTS` / messaggio utente)**: verifica se il ricercatore ha indicato `<caso>` e il questionario in input. Se uno dei due parametri manca, **non inventarlo**: chiedi al ricercatore umano di specificare `<caso>` e il file da revisionare prima di inizializzare `runs/<caso>/`.
- **ID Caso (`<caso>`)**: identificativo alfanumerico della cartella in `runs/<caso>/` (es. `revisione-demo`).
- **Questionario in input**: percorso del questionario da revisionare (es. `examples/questionario_demo.md` o file fornito dal ricercatore).

---

## Sequenza delle Fasi e Gate Human-in-the-Loop

### Fase 0 — Inizializzazione (`ai-coordinator` via `noto-survey-pipeline`)
1. Leggi `AGENTS.md` / `CLAUDE.md`.
2. Se `runs/<caso>/status.md` non esiste:
   - Crea `runs/<caso>/source/` e copia al suo interno il questionario di partenza **senza mai alterarlo**.
   - Crea `runs/<caso>/status.md` usando `templates/status_template.md`, impostando `Workflow attivo: revisione-questionario`, le fasi `brief` e `questionnaire` su `SALTATA` e `Fase attiva corrente: methodology`.

### Fase 1 — Audit Metodologico (`methodology`)
- **Agente delegato**: `methodology-agent`
- **Skill**: `noto-methodology-audit`
- **Template**: `templates/methodology_template.md`
- **Input**: questionario originale in `runs/<caso>/source/<file>`
- **Output**: `runs/<caso>/methodology.md`
- **Gate Umano 1 (STOP)**: `ai-coordinator` verifica l'allineamento della griglia a 11 colonne e delle schede analitiche a 12 campi con le 3 alternative (*Opzione A: Conservare*, *Opzione B: Modifica minima*, *Opzione C: Revisione sostanziale*), aggiorna `runs/<caso>/status.md` e **si ferma**. Chiede al ricercatore umano in chat quali proposte accettare o scartare per ciascun item (valutando l'impatto sulle serie storiche) e registra le decisioni in `runs/<caso>/status.md`.

### Fase 2 — Screening Preliminare Privacy e AI Act (`compliance`)
- **Agente delegato**: `compliance-agent`
- **Skill**: `noto-compliance-check`
- **Template**: `templates/compliance_template.md`
- **Input**: questionario in `runs/<caso>/source/<file>`, `runs/<caso>/methodology.md` e scelte in `runs/<caso>/status.md`
- **Output**: `runs/<caso>/compliance.md`
- **Gate Umano 2 (STOP)**: `ai-coordinator` verifica la completezza dello screening Art. 9 GDPR e AI Act, aggiorna `runs/<caso>/status.md` e **si ferma** chiedendo l'approvazione umana in chat delle cautele privacy da recepire. Registra la decisione e le prescrizioni approvate in `runs/<caso>/status.md` prima di passare alla Fase 3.

### Fase 3 — Consolidamento Versione Finale (`final`)
- **Agente delegato**: `questionnaire-agent`
- **Skill**: `noto-questionnaire-consolidation`
- **Template**: `templates/final_template.md`
- **Input**: `runs/<caso>/source/<file>`, `runs/<caso>/methodology.md`, `runs/<caso>/compliance.md` e decisioni umane in `runs/<caso>/status.md`
- **Output**: `runs/<caso>/final.md`
- **Gate Umano 3 (STOP e Chiusura Modulo A)**: `ai-coordinator` verifica che in `runs/<caso>/final.md` siano state recepite solo le modifiche approvate dal ricercatore, presenta il documento consolidato in chat e **si ferma**. Dopo l'approvazione finale, aggiorna `runs/<caso>/status.md` a `COMPLETATO (MODULO A)`.
