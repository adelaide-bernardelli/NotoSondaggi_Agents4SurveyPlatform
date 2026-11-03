---
name: noto-compliance-check
description: Esegue la checklist preliminare di privacy (GDPR Art. 9) e governance AI Act in runs/<caso>/compliance.md usando templates/compliance_template.md, segnalando cautele e punti bloccanti per DPO o consulente legale.
---

# Skill: `noto-compliance-check` — Checklist Preliminare Privacy (GDPR Art. 9) e AI Act

## Scopo e Chi la Utilizza
- **Agente esecutore**: `compliance-agent` (su delega di `ai-coordinator` nella fase `compliance`).
- **Invocazione diretta**: richiamabile dal ricercatore umano tramite `/noto-compliance-check` per eseguire uno screening preliminare privacy e AI Act su un questionario o brief.
- **Template obbligatorio**: `templates/compliance_template.md` -> `runs/<caso>/compliance.md`.

> **Avvertenza fondamentale**: questa skill produce una **checklist tecnica preliminare**, NON un parere legale né una certificazione di conformità GDPR o AI Act. Ogni punto critico deve essere rimesso alla valutazione del DPO o del consulente legale di **Noto Sondaggi SRL**.

---

## Input Richiesti
1. Questionario o documento in esame (`runs/<caso>/questionnaire.md` oppure `runs/<caso>/source/<file>`). Se la skill è invocata direttamente dal ricercatore umano su un file esterno non ancora copiato in `runs/<caso>/source/`, richiedere (se mancante) l'ID `<caso>`, creare `runs/<caso>/source/` copiandovi il file immutato e inizializzare `runs/<caso>/status.md` tramite `templates/status_template.md`.
2. Eventuali `runs/<caso>/brief.md`, `runs/<caso>/methodology.md` e scelte del ricercatore registrate in `runs/<caso>/status.md`.

---

## Procedura Operativa Step-by-Step

### 1. Analisi del Perimetro e della Natura dei Dati (Sezione 1 del Template)
- Verifica se i file nel caso contengono **soli testi di questionario**, **dati aggregati** o **microdati**. (Se venissero rilevati dati personali identificativi reali nei file di input, segnala immediatamente l'anomalia come **bloccante**).
- Individua se l'indagine prevede la raccolta sul campo di:
  - **Dati personali comuni** (età, genere, comune/CAP, professione, titolo di studio, metadati di contatto telefonico/IP/panel ID);
  - **Categorie particolari di dati ex Art. 9 GDPR**:
    - opinioni politiche, intenzioni di voto, collocazione politica, fiducia in leader o partiti;
    - convinzioni religiose o filosofiche;
    - appartenenza sindacale;
    - dati relativi alla salute o alla vita/orientamento sessuale;
    - origine razziale o etnica.

### 2. Screening Analitico Domanda per Domanda (Sezione 2 del Template)
Compila la tabella di `templates/compliance_template.md` per tutti gli item del questionario (`Q01`, `Q02`, ...):
- **Natura del Dato**: `Nessuno (opinione su servizi generali)` / `Dato Comune` / `Art. 9 GDPR`.
- **Rischio Identificazione Indiretta**: valuta se la combinazione di variabili socio-demografiche o territoriali (es. piccolo comune + età puntuale + professione specifica) può rendere identificabile il rispondente (*singling out*). Prescrivi l'aggregazione in classi (es. fasce d'età) ove necessario.
- **Presenza "Preferisco non rispondere"**: verifica che ogni domanda, e in modo **tassativo** quelle ex Art. 9 GDPR o socio-demografiche sensibili, preveda l'opzione esplicita *"Preferisco non rispondere / Rifiuta"* con codice distinto da *"Non so"*.
- **Cautela o Modifica Richiesta**: indica eventuali modifiche al testo o alle istruzioni per garantire la libertà di non risposta e la minimizzazione.

### 3. Checklist Adempimenti GDPR e Governance AI Act (Sezione 3 del Template)
Valuta e documenta ciascuna voce della checklist:
- **Base giuridica e informativa (Artt. 6, 9, 13-14 GDPR)**: necessità di informativa chiara prima dell'inizio dell'intervista e verifica con il DPO della base giuridica applicabile (consenso esplicito per Art. 9 GDPR ove non già anonimizzato all'origine).
- **Minimizzazione (Art. 5 GDPR)**: raccogliere solo le variabili strettamente necessarie agli obiettivi conoscitivi del brief approvato.
- **Fornitori esterni e Sub-responsabili (Art. 28 GDPR)**: piattaforme CATI/CAWI/CAPI, gestori di panel, servizi di trascrizione.
- **Trasferimenti e Conservazione (*Data Retention*)**: separazione immediata tra anagrafiche di contatto e risposte al questionario; tempi di cancellazione dei contatti.
- **DPIA (Art. 35 GDPR)**: segnala la necessità di verificare con il DPO l'obbligatorietà di una Valutazione d'Impatto in presenza di monitoraggio su larga scala o trattamento sistematico di dati ex Art. 9 GDPR.
- **Profili AI Act**:
  - verifica l'assenza di tecniche subliminali, manipolative o di sfruttamento di vulnerabilità (Art. 5 AI Act);
  - documenta lo scopo previsto (*intended purpose*: mero supporto redazionale e metodologico interno con *human-in-the-loop*);
  - ribadisci che l'esecuzione locale del sistema non sostituisce gli obblighi GDPR e di governance.
- **Human Oversight**: conferma il tracciamento delle approvazioni umane in `runs/<caso>/status.md`.

### 4. Elenco dei Punti Bloccanti e Validazione Umana (Sezione 4 del Template)
- Elenca in modo chiaro i **Bloccanti prima della somministrazione** (es. approvazione informativa privacy da parte del DPO, inserimento opzione *"Preferisco non rispondere"* sugli item segnalati).
- Indica le figure umane da coinvolgere (`Ricercatore responsabile`, `DPO`, `Consulente legale`) e lascia `Approvazione dell'esperto umano: IN ATTESA`.
