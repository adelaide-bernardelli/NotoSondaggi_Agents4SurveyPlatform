---
name: noto-questionnaire-consolidation
description: Consolida la versione finale del questionario in runs/<caso>/final.md usando templates/final_template.md, integrando esclusivamente le modifiche metodologiche e di compliance approvate dal ricercatore umano in runs/<caso>/status.md.
---

# Skill: `noto-questionnaire-consolidation` — Consolidamento Versione Finale (`final.md`)

## Scopo e Chi la Utilizza
- **Agente esecutore**: `questionnaire-agent` (su delega di `ai-coordinator` nella fase `final`).
- **Invocazione diretta**: richiamabile dal ricercatore umano tramite `/noto-questionnaire-consolidation` dopo aver completato e approvato l'audit metodologico e lo screening di compliance.
- **Template obbligatorio**: `templates/final_template.md` -> `runs/<caso>/final.md`.

---

## Input Richiesti
1. Questionario di origine (`runs/<caso>/questionnaire.md` per nuove indagini oppure il documento originale in `runs/<caso>/source/<file>` per le revisioni).
2. Audit metodologico `runs/<caso>/methodology.md`.
3. Screening preliminare privacy `runs/<caso>/compliance.md`.
4. Stato del caso e **decisioni puntuali del ricercatore umano** registrate in `runs/<caso>/status.md`.

---

## Procedura Operativa Step-by-Step

### 1. Verifica delle Decisioni Umane in `runs/<caso>/status.md`
- Leggi la sezione *"Registro delle Decisioni Umane in Chat"* di `runs/<caso>/status.md` (se la skill è invocata direttamente dal ricercatore umano senza che `<caso>` sia specificato o senza che le scelte su `methodology.md` e `compliance.md` siano state registrate, chiedi conferma esplicita prima di procedere).
- Accerta quali alternative metodologiche (**Opzione A: Conservare**, **Opzione B: Modifica minima**, **Opzione C: Revisione sostanziale**, o formulazioni specifiche dettate dal ricercatore) sono state approvate per ciascun item e quali prescrizioni di compliance sono state validate.
- **Divieto di iniziativa autonoma**: non applicare mai una modifica proposta in `methodology.md` se il ricercatore umano ha deciso di conservare la formulazione originale (es. per continuità di serie storica).

### 2. Compilazione del Registro delle Modifiche Accettate e Scartate (Sezione 2 del Template)
- Costruisci la tabella comparativa che affianca, per ogni domanda:
  - `ID Domanda`;
  - `Testo Originale / Bozza Precedente`;
  - `Versione Finale Consolidata`;
  - `Scelta del Ricercatore (Origine modifica)`: indica se *Conservata (Opzione A)*, *Modifica minima (Opzione B)*, *Revisione sostanziale (Opzione C)* o *Prescrizione compliance*;
  - `Motivazione Metodologica / Compliance`;
  - `Effetto su Comparabilità Serie Storiche`.

### 3. Recepimento delle Prescrizioni di Compliance (Sezione 3 del Template)
- Inserisci la bozza di testo introduttivo e informativa breve da sottoporre al DPO.
- Verifica che tutte le tutele ex Art. 9 GDPR e di minimizzazione demografica approvate siano effettivamente applicate nel testo delle domande.
- Riporta in evidenza gli adempimenti bloccanti ancora aperti prima della messa in campo.

### 4. Stesura del Testo Definitivo del Questionario Candidato (Sezione 4 del Template)
- Redigi il testo completo e ordinato per sezioni di tutte le domande consolidate, includendo per ciascuna:
  - obiettivo conoscitivo;
  - testo definitivo per il rispondente;
  - tipo di domanda, opzioni e codici definitivi;
  - codici distinti per `97 = Non applicabile`, `98 = Non so`, `99 = Preferisco non rispondere`;
  - regola esatta di filtro / *skip*;
  - istruzioni per intervistatore / programmazione CATI-CAWI-CAPI;
  - nota sulla comparabilità storica.

### 5. Specifiche dei Filtri e Piano di Validazione Empirica (Sezioni 5, 6 e 7 del Template)
- Riepiloga l'albero logico dei filtri (*routing / skip logic*), le regole di rotazione e i controlli di coerenza.
- Indica il piano di validazione empirica sul campo (*pretest*, *cognitive interview*, *split ballot*) per testare le ipotesi metodologiche e raccordare eventuali serie storiche.
- Elenca gli eventuali elementi fattuali ancora marcati `[DA VERIFICARE]` e imposta `Esito revisione finale: IN ATTESA`.
