---
name: nuova-indagine
description: Avvia o prosegue il workflow completo per una nuova indagine survey (brief -> questionnaire -> methodology -> compliance -> final) con delega agli specialisti e approvazione umana in chat ad ogni fase.
---

# Workflow: Nuova Indagine (`brief -> questionnaire -> methodology -> compliance -> final`)

Questo workflow guida lo sviluppo end-to-end del Modulo A per una **nuova ricerca** di **Noto Sondaggi SRL**, a partire da un brief grezzo, appunti del cliente o una trascrizione autorizzata.

## Parametri di Avvio
- **Argomenti ricevuti (`$ARGUMENTS` / messaggio utente)**: verifica se il ricercatore ha indicato `<caso>` e il file di input. Se uno dei due parametri manca, **non inventarlo** (non usare il nome di esempio): chiedi al ricercatore umano di specificare `<caso>` e il file di partenza prima di inizializzare `runs/<caso>/`.
- **ID Caso (`<caso>`)**: identificativo alfanumerico della cartella in `runs/<caso>/` (es. `esempio-biblioteca`).
- **File di input**: percorso del documento di partenza (es. `examples/brief_demo.md` o file fornito dal ricercatore).

---

## Sequenza delle Fasi e Gate Human-in-the-Loop

### Fase 0 — Inizializzazione (`ai-coordinator` via `noto-survey-pipeline`)
1. Leggi `AGENTS.md` / `CLAUDE.md`.
2. Se `runs/<caso>/status.md` non esiste:
   - Crea `runs/<caso>/source/` e copia al suo interno il file di input senza modificarlo.
   - Crea `runs/<caso>/status.md` a partire da `templates/status_template.md`, impostando `Workflow attivo: nuova-indagine` e `Fase attiva corrente: brief`.

### Fase 1 — Strutturazione del Brief (`brief`)
- **Agente delegato**: `questionnaire-agent`
- **Skill**: `noto-brief-structuring`
- **Template**: `templates/brief_template.md`
- **Output**: `runs/<caso>/brief.md`
- **Gate Umano 1 (STOP)**: `ai-coordinator` verifica la conformità di `brief.md` al template, aggiorna `runs/<caso>/status.md` su `IN ATTESA DI APPROVAZIONE`, presenta in chat le domande aperte e le lacune informative e **si ferma**. Avanza alla Fase 2 solo dopo l'approvazione esplicita del ricercatore in chat e la registrazione delle sue risposte in `runs/<caso>/status.md`.

### Fase 2 — Stesura Bozza Questionario (`questionnaire`)
- **Agente delegato**: `questionnaire-agent`
- **Skill**: `noto-questionnaire-drafting`
- **Template**: `templates/questionnaire_template.md`
- **Output**: `runs/<caso>/questionnaire.md`
- **Gate Umano 2 (STOP)**: `ai-coordinator` verifica che ogni item sia collegato al brief, abbia codici distinti per *Non so*, *Rifiuto* e *Non applicabile* e tuteli eventuali serie storiche; aggiorna `runs/<caso>/status.md` e **si ferma** in attesa di approvazione umana in chat. Registra decisione, revisore, data e note in `runs/<caso>/status.md` prima di procedere alla Fase 3.

### Fase 3 — Audit Metodologico (`methodology`)
- **Agente delegato**: `methodology-agent`
- **Skill**: `noto-methodology-audit`
- **Template**: `templates/methodology_template.md`
- **Output**: `runs/<caso>/methodology.md`
- **Gate Umano 3 (STOP)**: `ai-coordinator` verifica la presenza della griglia a 11 colonne e delle schede a 12 campi con le 3 alternative (*Opzione A: Conservare*, *Opzione B: Modifica minima*, *Opzione C: Revisione sostanziale*); aggiorna `runs/<caso>/status.md` e **si ferma** chiedendo al ricercatore quali alternative approvare per ciascuna domanda. Registra le scelte puntuali in `runs/<caso>/status.md`.

### Fase 4 — Screening Preliminare Privacy e AI Act (`compliance`)
- **Agente delegato**: `compliance-agent`
- **Skill**: `noto-compliance-check`
- **Template**: `templates/compliance_template.md`
- **Output**: `runs/<caso>/compliance.md`
- **Gate Umano 4 (STOP)**: `ai-coordinator` verifica lo screening Art. 9 GDPR e AI Act, aggiorna `runs/<caso>/status.md` e **si ferma** sottoponendo le cautele e gli eventuali blocchi al ricercatore umano (e al DPO/legale ove richiesto). Registra in `runs/<caso>/status.md` la decisione e le prescrizioni privacy/GDPR approvate da recepire in `final.md`.

### Fase 5 — Consolidamento Versione Finale (`final`)
- **Agente delegato**: `questionnaire-agent`
- **Skill**: `noto-questionnaire-consolidation`
- **Template**: `templates/final_template.md`
- **Output**: `runs/<caso>/final.md`
- **Gate Umano 5 (STOP e Chiusura Modulo A)**: `ai-coordinator` verifica che `final.md` recepisca esclusivamente le modifiche approvate dal ricercatore in `runs/<caso>/status.md`, presenta la versione finale candidata e **si ferma**. Dopo l'approvazione finale, aggiorna `runs/<caso>/status.md` a `COMPLETATO (MODULO A)`.
