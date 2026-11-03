---
name: noto-brief-structuring
description: Analizza i materiali di input autorizzati (appunti, brief cliente, trascrizioni) e compila runs/<caso>/brief.md usando templates/brief_template.md, evidenziando lacune informative e domande per il ricercatore senza inventare dati.
---

# Skill: `noto-brief-structuring` — Analisi Input e Strutturazione del Brief

## Scopo e Chi la Utilizza
- **Agente esecutore**: `questionnaire-agent` (su delega di `ai-coordinator` nella fase `brief`).
- **Invocazione diretta**: richiamabile anche dal ricercatore umano tramite `/noto-brief-structuring` per trasformare appunti grezzi o una trascrizione autorizzata in un brief metodologico strutturato.
- **Template obbligatorio**: `templates/brief_template.md` -> `runs/<caso>/brief.md`.

---

## Input Richiesti
1. Documento di partenza collocato in `runs/<caso>/source/` (es. brief del committente, appunti di ricerca, trascrizione riunione priva di dati personali). Se la skill è invocata direttamente dal ricercatore umano su un file esterno non ancora copiato in `runs/<caso>/source/`, richiedere (se mancante) l'ID `<caso>`, creare `runs/<caso>/source/` copiandovi il file immutato e inizializzare `runs/<caso>/status.md` tramite `templates/status_template.md`.
2. Eventuali vincoli preliminari indicati dal ricercatore umano e registrati in `runs/<caso>/status.md`.

---

## Procedura Operativa Step-by-Step

1. **Lettura analitica della fonte**:
   - Esamina integralmente il documento in `runs/<caso>/source/`.
   - Separa ciò che è esplicitamente dichiarato nella fonte da ciò che è assente, implicito o ambiguo.
2. **Estrazione di Obiettivi e Costrutti**:
   - Individua l'**obiettivo conoscitivo principale** e i **sotto-obiettivi**.
   - Elenca le **variabili chiave e i costrutti** da misurare (es. notorietà, fruizione, soddisfazione, atteggiamenti, intenzioni, profilo socio-demografico).
   - Verifica se sono citate indagini precedenti o serie storiche di **Noto Sondaggi SRL** con cui mantenere la comparabilità.
3. **Analisi del Disegno di Rilevazione (Divieto di invenzione)**:
   - Riporta popolazione di riferimento e area geografica esattamente come indicate nella fonte.
   - Se **modalità di somministrazione** (`CATI / CAWI / CAPI`), **numerosità campionaria**, **durata in minuti** o **numero di domande** non sono specificati, imposta il campo su `DA DEFINIRE`. Puoi suggerire opzioni tecniche tra parentesi quadre solo marcandole chiaramente come `[PROPOSTA DA CONFERMARE]`.
4. **Censimento Fatti Esterni e Vincoli Privacy/Metodologici**:
   - Marca con `[DA VERIFICARE]` qualsiasi cifra, data, percentuale, opera pubblica, legge o atto amministrativo citato negli appunti di partenza.
   - Evidenzia se i temi trattati toccano categorie particolari di dati ex Art. 9 GDPR (es. opinioni politiche, orientamento di voto, appartenenza sindacale, convinzioni religiose, salute).
   - Ribadisci il vincolo metodologico di prevedere codici distinti per *Non so*, *Rifiuto ("Preferisco non rispondere")* e *Non applicabile*.
5. **Formulazione delle Domande per il Ricercatore**:
   - Compila la sezione *"Lacune Informative e Domande per il Ricercatore"* con domande puntuali e operative che il ricercatore umano dovrà sciogliere prima di passare alla stesura del questionario.
6. **Scrittura dell'Output**:
   - Salva il risultato in `runs/<caso>/brief.md` rispettando tutte le sezioni di `templates/brief_template.md` e lasciando `Decisione del ricercatore: IN ATTESA`.

---

## Controlli di Qualità Obbligatori
- Nessun parametro campionario o metodologico assente nell'input è stato dato per certo.
- Tutti i riferimenti fattuali esterni riportano il tag `[DA VERIFICARE]`.
- Il file `runs/<caso>/brief.md` segue fedelmente `templates/brief_template.md`.
