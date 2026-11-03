---
name: noto-methodology-audit
description: Esegue audit metodologico item per item in runs/<caso>/methodology.md usando templates/methodology_template.md, distingue non risposta evitabile e autentica non conoscenza, e documenta rischi, tre alternative di intervento e comparabilita storica.
---

# Skill: `noto-methodology-audit` — Audit Metodologico Item-per-Item

## Scopo e Chi la Utilizza
- **Agente esecutore**: `methodology-agent` (su delega di `ai-coordinator` nella fase `methodology`).
- **Invocazione diretta**: richiamabile dal ricercatore umano tramite `/noto-methodology-audit` per sottoporre qualsiasi questionario a revisione metodologica strutturata.
- **Template obbligatorio**: `templates/methodology_template.md` -> `runs/<caso>/methodology.md`.
- **Tracciamento modelli (opzionale)**: `examples/confronto_modelli.csv`.

---

## Input Richiesti
1. Questionario da sottoporre ad audit: `runs/<caso>/questionnaire.md` (nel workflow `nuova-indagine`) oppure il documento originale in `runs/<caso>/source/<file>` (nei workflow `revisione-questionario` e `audit-singolo`). Se la skill è invocata direttamente dal ricercatore umano su un file esterno non ancora copiato in `runs/<caso>/source/`, richiedere (se mancante) l'ID `<caso>`, creare `runs/<caso>/source/` copiandovi il file immutato e inizializzare `runs/<caso>/status.md` tramite `templates/status_template.md`.
2. Eventuale `runs/<caso>/brief.md` approvato e vincoli registrati in `runs/<caso>/status.md`.

---

## Checklist dei Controlli Metodologici da Eseguire
Esamina ogni singola domanda e l'intero flusso del questionario verificando:
1. **Formulazioni *leading* o presupponenti**: aggettivi orientanti, domande retoriche (*"non è vero?"*, *"finalmente"*), premesse sbilanciate.
2. **Doppia domanda (*double-barreled*)**: due oggetti o costrutti distinti nella stessa domanda (es. *"orari e disponibilità dei libri"*).
3. **Chiarezza lessicale e *respondent burden***: tecnicismi, doppie negazioni, lunghezza eccessiva, sforzo di memoria irrealistico (*recall bias*).
4. **Riferimenti fattuali non verificati**: cifre, opere pubbliche, date o atti amministrativi presentati nelle premesse (da marcare come `[DA VERIFICARE]`) o descrizioni che contaminano la misurazione della conoscenza pregressa.
5. **Coerenza e bilanciamento delle scale**: etichette positive e negative simmetriche, categorie mutuamente esclusive ed esaustive, quantificatori vaghi (*"alcuni / molti"*) da sostituire con classi numeriche oggettive.
6. **Tassonomia della non risposta**:
   - **Rifiuto esplicito** (*"Preferisco non rispondere"*, cod. distinto);
   - **Autentico "Non so" / non conoscenza** (assenza legittima di informazione o opinione strutturata, cod. distinto);
   - **Non applicabile** (rispondente fuori sub-target per assenza di domanda filtro preliminare, cod. distinto);
   - **Mancata risposta all'item** (*item nonresponse* da ambiguità o fatica);
   - **Abbandono** (*break-off*).
7. **Percorsi di filtro (*skip logic*) e *subgroup accessibility***: verifica che le domande di valutazione specifica siano precedute da un filtro di conoscenza o fruizione.
8. **Effetti di sequenza, *priming* e durata delle batterie**: rischio di *response set* / *straightlining* e fatica cognitiva.

> **Regola metodologica aurea**: non eliminare mai l'opzione *"Non so"* o *"Preferisco non rispondere"* per abbassarne artificialmente la frequenza. Una percentuale più bassa di non risposta ottenuta forzando il rispondente non equivale a maggiore validità e genera *pseudo-opinioni*. Ogni effetto atteso deve essere presentato come **ipotesi da testare** empiricamente, mai come certezza.

---

## Struttura Obbligatoria dell'Output (`runs/<caso>/methodology.md`)

Compila `runs/<caso>/methodology.md` seguendo esattamente le 7 sezioni di `templates/methodology_template.md`:

### 1. Metodo e limiti
Riporta caso, modalità (`CATI / CAWI / CAPI / Ignota`), documento originale di riferimento e l'avvertenza che la valutazione si fonda sulle formulazioni e non su tassi empirici osservati.

### 2. Griglia domanda per domanda (11 colonne allineate)
Compila la tabella riepilogativa usando esattamente queste **11 colonne**:
`| ID | Costrutto | Testo originale | Modalita | Criticita e tipo non risposta a rischio | Severita | Proposta raccomandata | Nuove opzioni / filtri (NS/Rifiuto/NA) | Impatto durata | Impatto comparabilita | Decisione umana |`

### 3. Schede analitiche item per item (12 campi allineati)
Per ciascun item (`Q01`, `Q02`, ...), redigi una scheda contenente esattamente questi **12 campi**:
- **ID stabile e Costrutto**
- **Modalita di somministrazione (CATI/CAWI/CAPI o ignota)**
- **Testo originale, opzioni e filtri attuali**
- **Criticita rilevata ed evidenza del rischio**
- **Distinzione del rischio di risposta** (*Rifiuto vs Autentico Non so vs Mancata risposta item vs Fuori target/Non applicabile vs Abbandono*)
- **Severita qualitativa**: `[Bassa / Media / Alta / Critica]`
- **Alternative di intervento** (presentare sempre tutte e tre quando opportuno):
  1. **Opzione A — Conservare l'originale**: testo invariato e condizioni in cui è preferibile mantenerlo (es. continuità di serie storica).
  2. **Opzione B — Modifica minima**: intervento conservativo con differenze puntuali rispetto all'originale e completamento di opzioni/codici (`Non so`, `Rifiuto`, `Non applicabile`) e filtri.
  3. **Opzione C — Revisione sostanziale**: riscrittura strutturale (es. sdoppiamento di domanda *double-barreled*, introduzione di filtro preliminare, rifacimento scala) con differenze puntuali rispetto all'originale.
- **Effetto atteso** (formulato rigorosamente come *ipotesi da testare*, non certezza)
- **Costo in durata / respondent burden**
- **Impatto sulla comparabilita storica**
- **Verifica empirica richiesta**: `[Nessuna / Cognitive interview / Pilot / Split ballot]`
- **Decisione umana**: `DA CONFERMARE [Scelta del ricercatore: Opzione A / Opzione B / Opzione C / Altro]`

### 4. Bozza finale candidata
Presenta la sequenza completa del questionario con le modifiche raccomandate tracciate (inclusi eventuali sdoppiamenti, es. `Q02a` e `Q02b`).

### 5. Rischi trasversali
Analizza ordine delle sezioni, rischio di *priming*, durata delle batterie, coerenza delle scale e premesse `[DA VERIFICARE]`.

### 6. Piano di pretest/pilot e Confronto Modelli
Indica quali item richiedono *cognitive interview*, *pilot* su piccolo campione o *split ballot* per raccordare serie storiche. Se il ricercatore sta effettuando una valutazione comparativa tra modelli LLM, segnala i parametri da registrare secondo il tracciato `examples/confronto_modelli.csv` (`case_id,ruolo,provider,modello_versione,data_run,prompt_versione,tempo_ricercatore_min,issue_rilevate,issue_verificate,modifiche_accettate,note`).

### 7. Decisioni aperte
Riepiloga le scelte rimesse al ricercatore umano con `Stato approvazione: IN ATTESA`.
