---
name: noto-questionnaire-drafting
description: Redige la bozza strutturata del questionario in runs/<caso>/questionnaire.md a partire da un brief approvato usando templates/questionnaire_template.md, con codici distinti di non risposta, filtri e tutela delle serie storiche.
---

# Skill: `noto-questionnaire-drafting` — Stesura Bozza del Questionario

## Scopo e Chi la Utilizza
- **Agente esecutore**: `questionnaire-agent` (su delega di `ai-coordinator` nella fase `questionnaire`).
- **Invocazione diretta**: richiamabile dal ricercatore umano tramite `/noto-questionnaire-drafting` per generare una bozza di questionario a partire da un brief approvato.
- **Template obbligatorio**: `templates/questionnaire_template.md` -> `runs/<caso>/questionnaire.md`.

---

## Input Richiesti
1. Brief approvato `runs/<caso>/brief.md` (con le risposte e le decisioni del ricercatore umano registrate in `runs/<caso>/status.md`).
2. Eventuali questionari storici o fonti documentali presenti in `runs/<caso>/source/`.

---

## Procedura Operativa Step-by-Step

1. **Verifica Prerequisiti**:
   - Controlla che `runs/<caso>/brief.md` sia presente e che le scelte fondamentali (target, metodo o opzioni da testare, aree tematiche) siano state chiarite dal ricercatore in `runs/<caso>/status.md` (se invocata direttamente dal ricercatore umano senza `runs/<caso>/`, chiedi l'ID `<caso>` e il brief approvato prima di procedere).
2. **Architettura delle Sezioni e Sequenza Cognitiva**:
   - Organizza il questionario in sezioni logiche (es. *Screening/Filtri iniziali*, *Conoscenza/Notorietà*, *Fruizione/Comportamenti*, *Valutazione/Atteggiamenti*, *Profilo socio-demografico in coda*) evitando effetti di *priming* o contaminazione tra domande consecutive.
3. **Redazione Analitica di Ciascun Item (`Q01`, `Q02`, ...)**:
   Per ogni singola domanda compila tutti i campi previsti da `templates/questionnaire_template.md`:
   - **Obiettivo del brief**: indica a quale obiettivo o sotto-obiettivo di `brief.md` risponde la domanda.
   - **Testo per rispondente**: formula il testo in modo chiaro, neutrale, privo di doppie domande (*double-barreled*), privo di presupposizioni o aggettivi orientanti (*leading*).
   - **Tipo di domanda**: specifica se chiusa singola, chiusa multipla (con limite massimo di risposte), scala ordinale bilanciata, batteria, numerica o aperta.
   - **Opzioni e codici**: elenca opzioni mutuamente esclusive ed esaustive con codici numerici coerenti; nelle scale di atteggiamento assicura il perfetto bilanciamento tra poli positivi e negativi.
   - **Non so / rifiuto / non applicabile (codici distinti obbligatori)**:
     - assegna sempre codici separati (es. `97 = Non applicabile`, `98 = Non so / Non conosce`, `99 = Preferisco non rispondere / Rifiuta`);
     - non fondere mai il *"Non so"* con il *"Rifiuto"*.
   - **Filtro / skip**: specifica a chi va posta la domanda (es. *"A tutti"* oppure *"Solo se Q02 = 1 o 2; altrimenti salta a Q05 e codifica 97"*).
   - **Istruzioni di regia e somministrazione**: definisci in modo esplicito le istruzioni operative per l'intervistatore o per la piattaforma di rilevazione, adottando la sintassi standardizzata obbligatoria: `- **Istruzioni di regia e somministrazione**: [NON LEGGERE / SPONTANEA / ROTAZIONE / PROBING]`. Specifica prescrizioni puntuali quali *"[NON LEGGERE LE OPZIONI — ATTENDERE RISPOSTA SPONTANEA]"*, *"[LEGGERE LE OPZIONI DI SEGUITO]"*, *"[RUOTARE L'ORDINE DELLE OPZIONI]"*, *"[PROBING NEUTRALE: SE INCERTO CHIARIRE SENZA ORIENTARE]"*, *"[NON SOLLECITARE 'Non so' / 'Preferisco non rispondere', registrare solo se spontaneo]"* in somministrazioni CATI/CAPI, oppure regole di visualizzazione/randomizzazione a schermo in indagini CAWI.
   - **Fonte/precedente e Rischio comparabilità**: indica se l'item proviene da una serie storica (preservandone testo, scala e riferimento temporale) oppure se è `[NUOVO ITEM]`. Segnala con `[DA VERIFICARE]` ogni dato fattuale citato nelle premesse.
4. **Punti Aperti per il Ricercatore**:
   - Se per un costrutto esistono due formulazioni alternative meritevoli di valutazione (es. scala a 4 passi vs scala a 5 passi con punto neutro), presentale nella sezione *"Punti aperti per il ricercatore"*.
5. **Scrittura dell'Output**:
   - Salva il file in `runs/<caso>/questionnaire.md` rispettando `templates/questionnaire_template.md`, mantenendo l'avvertenza `BOZZA NON AUTORIZZATA PER CAMPO` e `Decisione del ricercatore: IN ATTESA`.

---

## Controlli di Qualità Obbligatori
- Ogni item di `runs/<caso>/questionnaire.md` è mappato su un obiettivo del brief approvato.
- Tutte le domande dispongono di codici distinti per *Non so*, *Rifiuto* e *Non applicabile*.
- Tutte le domande includono la voce standardizzata per le istruzioni di regia e somministrazione (`- **Istruzioni di regia e somministrazione**: [NON LEGGERE / SPONTANEA / ROTAZIONE / PROBING]`).
- Le scale sono bilanciate e prive di formulazioni *leading* o *double-barreled*.
