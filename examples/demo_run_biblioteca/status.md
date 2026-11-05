# Stato di Avanzamento del Caso — Tracciamento Human-in-the-Loop

> **Nota operativa**: questo file è gestito da `ai-coordinator` per tracciare le fasi del workflow e registrare le decisioni espresse dal ricercatore umano in chat.

## 1. Metadati del Caso
- **ID Caso**: `demo-biblioteca`
- **Workflow attivo**: `nuova-indagine`
- **Documento di input in `source/`**: `runs/demo-biblioteca/source/brief_demo.md`
- **Data di apertura**: `2026-11-04`
- **Fase attiva corrente**: `COMPLETATO (MODULO A)`
- **Stato fase corrente**: `APPROVATO`

---

## 2. Avanzamento delle Fasi (Modulo A)

| Fase | Agente Esecutore | Skill Utilizzata | Artefatto Prodotto | Stato | Revisore Umano | Data Decisione | Note Sintetiche |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **1. `brief`** | `questionnaire-agent` | `noto-brief-structuring` | `runs/demo-biblioteca/brief.md` | `APPROVATO` | Ricercatore Senior | 2026-11-04 | Approvato brief strutturato con focus su fruitori residenti |
| **2. `questionnaire`** | `questionnaire-agent` | `noto-questionnaire-drafting` | `runs/demo-biblioteca/questionnaire.md` | `APPROVATO` | Ricercatore Senior | 2026-11-04 | Approvata bozza 5 item con codici standard 97, 98, 99 |
| **3. `methodology`** | `methodology-agent` | `noto-methodology-audit` | `runs/demo-biblioteca/methodology.md` | `APPROVATO CON SELEZIONE` | Ricercatore Senior | 2026-11-04 | Scelta Opzione B per Q1, Q3, Q4; Opzione C per Q2 (sdoppiamento) |
| **4. `compliance`** | `compliance-agent` | `noto-compliance-check` | `runs/demo-biblioteca/compliance.md` | `APPROVATO` | DPO / Consulente Legale | 2026-11-04 | Nessun dato Art. 9; inserita opzione rifiuto su socio-demografiche |
| **5. `final`** | `questionnaire-agent` | `noto-questionnaire-consolidation` | `runs/demo-biblioteca/final.md` | `APPROVATO` | Ricercatore Senior | 2026-11-04 | Consolidato testo finale pronto per programmazione CAWI/CATI |

---

## 3. Registro delle Decisioni Umane in Chat (Log Cronologico)

### Fase `brief`
- **Stato**: `APPROVATO`
- **Revisore**: Ricercatore Senior
- **Data**: 2026-11-04
- **Risposte alle domande aperte e vincoli confermati dal ricercatore**: Modalità mista CAWI/CATI, target residenti maggiorenni.

### Fase `questionnaire`
- **Stato**: `APPROVATO`
- **Revisore**: Ricercatore Senior
- **Data**: 2026-11-04
- **Indicazioni e modifiche richieste dal ricercatore**: Inseriti codici 97, 98, 99 su tutte le domande.

### Fase `methodology`
- **Stato**: `APPROVATO CON SELEZIONE`
- **Revisore**: Ricercatore Senior
- **Data**: 2026-11-04
- **Scelte puntuali del ricercatore per domanda**: Approvate opzioni conservative con sdoppiamento orari/libri.

### Fase `compliance`
- **Stato**: `APPROVATO`
- **Revisore**: DPO
- **Data**: 2026-11-04
- **Prescrizioni privacy/GDPR e cautele approvate da recepire in `final.md`**: Informativa sintetica allineata.

### Fase `final`
- **Stato**: `APPROVATO`
- **Revisore**: Ricercatore Senior
- **Data**: 2026-11-04
- **Note conclusive del ricercatore (Fine Modulo A)**: Validazione Modulo A completata con successo.
