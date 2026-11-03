# Stato di Avanzamento del Caso — Tracciamento Human-in-the-Loop

> **Nota operativa**: questo file è gestito da `ai-coordinator` per tracciare le fasi del workflow e registrare le decisioni espresse dal ricercatore umano in chat. Non sostituisce un sistema di audit immutabile.

## 1. Metadati del Caso
- **ID Caso**: `<caso>`
- **Workflow attivo**: `[nuova-indagine / revisione-questionario / audit-singolo]`
- **Documento di input in `source/`**: `runs/<caso>/source/<file_input>`
- **Data di apertura**: `YYYY-MM-DD`
- **Fase attiva corrente**: `[brief / questionnaire / methodology / compliance / final / COMPLETATO (MODULO A)]`
- **Stato fase corrente**: `[IN LAVORAZIONE / IN ATTESA DI APPROVAZIONE / APPROVATO / APPROVATO CON MODIFICHE / RIFIUTATO - DA REVISIONARE]`

---

## 2. Avanzamento delle Fasi (Modulo A)

| Fase | Agente Esecutore | Skill Utilizzata | Artefatto Prodotto | Stato | Revisore Umano | Data Decisione | Note Sintetiche |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **1. `brief`** | `questionnaire-agent` | `noto-brief-structuring` | `runs/<caso>/brief.md` | `[DA AVVIARE / SALTATA]` | — | — | — |
| **2. `questionnaire`** | `questionnaire-agent` | `noto-questionnaire-drafting` | `runs/<caso>/questionnaire.md` | `[DA AVVIARE / SALTATA]` | — | — | — |
| **3. `methodology`** | `methodology-agent` | `noto-methodology-audit` | `runs/<caso>/methodology.md` | `[DA AVVIARE]` | — | — | — |
| **4. `compliance`** | `compliance-agent` | `noto-compliance-check` | `runs/<caso>/compliance.md` | `[DA AVVIARE]` | — | — | — |
| **5. `final`** | `questionnaire-agent` | `noto-questionnaire-consolidation` | `runs/<caso>/final.md` | `[DA AVVIARE]` | — | — | — |

---

## 3. Registro delle Decisioni Umane in Chat (Log Cronologico)

### Fase `brief`
- **Stato**: `[IN ATTESA / APPROVATO / RIFIUTATO / SALTATA]`
- **Revisore**:
- **Data**:
- **Risposte alle domande aperte e vincoli confermati dal ricercatore**:

### Fase `questionnaire`
- **Stato**: `[IN ATTESA / APPROVATO / RIFIUTATO / SALTATA]`
- **Revisore**:
- **Data**:
- **Indicazioni e modifiche richieste dal ricercatore**:

### Fase `methodology`
- **Stato**: `[IN ATTESA / APPROVATO / APPROVATO CON SELEZIONE / RIFIUTATO]`
- **Revisore**:
- **Data**:
- **Scelte puntuali del ricercatore per domanda (Opzione A: Conservare / Opzione B: Modifica minima / Opzione C: Revisione sostanziale)**:

### Fase `compliance`
- **Stato**: `[IN ATTESA / APPROVATO / RIFIUTATO]`
- **Revisore**:
- **Data**:
- **Prescrizioni privacy/GDPR e cautele approvate da recepire in `final.md`**:

### Fase `final`
- **Stato**: `[IN ATTESA / APPROVATO / RIFIUTATO]`
- **Revisore**:
- **Data**:
- **Note conclusive del ricercatore (Fine Modulo A)**:

---

## 4. Punti Aperti e Bloccanti Prima del Campo
- **Elementi fattuali marcati `[DA VERIFICARE]`**:
- **Verifiche legali / DPO richieste prima della somministrazione**:
- **Test empirici consigliati (pretest / cognitive interview / split ballot)**:
- **Stato autorizzazione messa in campo (esterna al Modulo A)**: `NON AUTORIZZATA`
