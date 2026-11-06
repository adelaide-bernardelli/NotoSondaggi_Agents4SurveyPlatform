---
name: noto-agcom-reporting
description: Genera e convalida la Scheda Informativa obbligatoria del sondaggio ex art. 5 Delibera AGCOM 256/10/CSP per la diffusione sui media e il deposito istituzionale su sondaggipoliticoelettorali.it, con calcolo del margine d'errore teorico al 95%, trascrizione integrale dei quesiti con codici standard (97, 98, 99) e marcatura rigorosa di [DA VERIFICARE SUL CAMPO].
---

# Skill: `noto-agcom-reporting` — Scheda Informativa AGCOM (Delibera 256/10/CSP)

## Scopo e Chi la Utilizza
- **Agente esecutore**: `reporting-agent` (attivato per reporting regolamentare AGCOM e rendicontazione descrittiva trasparente, oppure su richiesta di `ai-coordinator` a valle del questionario consolidato).
- **Invocazione diretta**: richiamabile dal ricercatore umano tramite il comando `/noto-agcom-reporting` o via CLI per produrre, aggiornare o validare la Scheda Informativa di pubblicazione di un sondaggio demoscopico o elettorale.
- **Template obbligatorio**: `templates/agcom_template.md` -> salvato come `runs/<caso>/scheda_agcom.md`.
- **Script associato**: `scripts/generate_agcom_report.py`.
- **Riferimento normativo vincolante**: Delibera AGCOM n. 256/10/CSP ("Regolamento in materia di pubblicazione e diffusione dei sondaggi sui mezzi di comunicazione di massa", art. 5 Allegato A) e deposito obbligatorio presso la Presidenza del Consiglio dei Ministri sul sito istituzionale `www.sondaggipoliticoelettorali.it`.

---

## Input Supportati
1. Cartella del caso `runs/<caso>/` contenente:
   - Questionario consolidato definitivo `runs/<caso>/final.md` (o in subordine la bozza `questionnaire.md`);
   - Metadati del caso e registro approvazioni in `runs/<caso>/status.md`;
   - Brief di inquadramento metodologico e campionario in `runs/<caso>/brief.md` (se disponibile).
2. In alternativa: percorso diretto a un singolo file di questionario (`.md`).
3. Eventuali parametri campionari e di diffusione forniti dal ricercatore umano in chat o tramite argomenti CLI (es. `--sample-size`, `--client`, `--buyer`, `--media`, `--pub-date`, `--fieldwork-date`, `--title`).

---

## Procedura Operativa Step-by-Step

### 1. Acquisizione Metadati e Domande
- Ispeziona `runs/<caso>/status.md` e `runs/<caso>/brief.md` per estrarre:
  - Titolo dell'indagine e ID del caso;
  - Committente e Acquirente della ricerca;
  - Popolazione di riferimento (universo di indagine) ed estensione territoriale (nazionale, regionale, provinciale, comunale);
  - Metodo di campionamento (stratificato per quote o probabilistico) e rappresentatività;
  - Numerosità campionaria pianificata ($n$), estraendo il valore intero anche con separatore delle migliaia (es. $n = 1.000$ -> 1000);
  - Metodo di raccolta dati (`CATI`, `CAWI`, `CAMI`, `CAPI` o mista integrata) e piattaforma di somministrazione (LimeSurvey / operatore telefonico);
  - Metodo di ponderazione statistica e variabili di post-stratificazione.
- Ispeziona il questionario consolidato (`runs/<caso>/final.md` o `questionnaire.md`) ed estrai tutte le domande, incluse batterie/matrici, opzioni di risposta e istruzioni di regia.

### 2. Calcolo Statistico del Margine d'Errore Teorico
- Calcola il margine d'errore statistico teorico al livello di confidenza del 95% ($z = 1.96$) assumendo la massima dispersione proporzionale binaria prudenziale ($p = 0.5$, $1-p = 0.5$):
  $$e = \pm z \cdot \sqrt{\frac{p(1-p)}{n}} = \pm \frac{1.96 \cdot 0.5}{\sqrt{n}} = \pm \frac{0.98}{\sqrt{n}}$$
  (es. per $n = 800 \to e = \pm 3.46\%$; per $n = 1000 \to e = \pm 3.10\%$; per $n = 1500 \to e = \pm 2.53\%$).
- Se la popolazione di riferimento $N$ è finita e nota, applica il fattore di correzione per popolazioni finite (*finite population correction*):
  $$e = \pm z \cdot \sqrt{\frac{p(1-p)}{n}} \cdot \sqrt{\frac{N-n}{N-1}}$$
- Inserisci sempre l'avvertenza metodologica che per i sottocampioni o segmenti socio-demografici di consistenza inferiore a $n$ il margine d'errore teorico risulta proporzionalmente più elevato.

### 3. Gestione Rigorosa dei Parametri di Fieldwork e Marcatura `[DA VERIFICARE SUL CAMPO]`
- **Prescrizione fondamentale di pre-campo**: tutti i dati numerici a consuntivo non disponibili prima dell'avvio o della conclusione del fieldwork DEVONO essere contrassegnati rigorosamente con il marcatore `[DA VERIFICARE SUL CAMPO]`:
  - Numerosità campionaria effettiva realizzata;
  - Date esatte di inizio e fine fieldwork;
  - Data di diffusione e testata/mezzo di comunicazione di pubblicazione;
  - Indicatori di contatto a consuntivo:
    * Contatti totali tentati ($T$);
    * Interviste complete valide ($C$);
    * Rifiuti all'intervista / *unit nonresponse* ($R$);
    * Mancati contatti / irreperibili ($M$);
    * Interviste parziali / abbandoni / *break-off* ($B$);
    * Fuori target / ineleggibili ($F$);
    * Tasso di Risposta ($RR = C/T$);
    * Tasso di Rifiuto ($RefR = R/T$);
  - Percentuali di risposta registrate per ciascuna opzione di ciascun quesito (`[DA VERIFICARE SUL CAMPO %]`).
- **Divieto deontologico inderogabile**:
  - Non inserire MAI numeri fittizi, stime inventate o tassi di contatto presunti.
  - Divieto assoluto di utilizzare rispondenti sintetici, simulazioni LLM o dati sintetici per popolare i risultati del sondaggio.

### 4. Trascrizione Fedele e Integrale dei Quesiti (Art. 5, comma 1, lett. m)
- Trascrivi ciascuna domanda somministrata con fedeltà letterale, specificando:
  - Codice identificativo del quesito (`Q01`, `Q02`, ecc.);
  - Formulazione testuale esatta rivolta al rispondente;
  - Istruzioni di regia e somministrazione per l'intervistatore o la piattaforma (`[NON LEGGERE / LEGGERE LE OPZIONI / RISPOSTA SINGOLA / ROTAZIONE]`);
  - Elenco completo e sequenziale di tutte le opzioni di risposta;
  - Inclusione obbligatoria dei codici standard di non risposta secondo il protocollo Noto Sondaggi:
    * `97`: Non applicabile (fuori sub-target);
    * `98`: Non so / Nessuna opinione;
    * `99`: Preferisco non rispondere / Rifiuta.

### 5. Compilazione Automatica della Scheda AGCOM via CLI
- Esegui lo script generatore richiamando:
  ```bash
  python scripts/generate_agcom_report.py runs/<caso> --output runs/<caso>/scheda_agcom.md
  ```
- In caso di parametri specifici di diffusione comunicati dal committente o dal ricercatore:
  ```bash
  python scripts/generate_agcom_report.py runs/<caso> \
    --output runs/<caso>/scheda_agcom.md \
    --client "Committente SpA" \
    --media "Quotidiano Nazionale" \
    --sample-size 1000
  ```
- Per eseguire solo il controllo di conformità su un file esistente senza riscriverlo:
  ```bash
  python scripts/generate_agcom_report.py runs/<caso> --check-only
  ```

### 6. Convalida Formale di Conformità alla Delibera AGCOM 256/10/CSP
- Verifica che `runs/<caso>/scheda_agcom.md` superi la validazione automatica (`validate_agcom_report` e `scripts/validate_runs.py`).
- Accerta che tutte le 7 sezioni obbligatorie siano compilate:
  1. *Dati Identificativi e di Diffusione* (Titolo, Soggetto realizzatore "Noto Sondaggi SRL", Committente, Acquirente, Date fieldwork, Pubblicazione, Mezzo);
  2. *Popolazione di Riferimento e Disegno Campionario* (Universo, Estensione territoriale, Metodo di campionamento, Rappresentatività, Numerosità pianificata ed effettiva);
  3. *Metodo di Rilevazione e Somministrazione* (Metodo CATI/CAWI/misto, Piattaforma LimeSurvey/operatore, Durata, Trattamento non risposte);
  4. *Consistenza Numerica del Campione e Indicatori di Contatto* (Tabella contatti, $T, C, R, M, B, F$, tassi $RR$ e $RefR$, marcati `[DA VERIFICARE SUL CAMPO]`);
  5. *Ponderazione Statistica e Margine d'Errore Teorico* (Metodo di ponderazione, Variabili post-stratificazione, Livello confidenza 95%, Margine calcolato $\pm e\%$, avvertenza sottocampioni);
  6. *Testo Integrale delle Domande e Opzioni di Risposta* (Tutti i quesiti integrali con opzioni, codici `97`, `98`, `99` e `[DA VERIFICARE SUL CAMPO %]`);
  7. *Archivio e Deposito Istituzionale* (Autorità AGCOM, Delibera 256/10/CSP, deposito obbligatorio su `www.sondaggipoliticoelettorali.it`, dichiarazione di conformità Noto Sondaggi SRL).

---

## Controlli di Qualità e Presidi Deontologici
- **Soggetto realizzatore**: deve essere indicato inderogabilmente come `Noto Sondaggi SRL`.
- **Riferimento normativo esatto**: deve essere citata esplicitamente la `Delibera AGCOM n. 256/10/CSP`.
- **Deposito ministeriale**: deve essere esplicitato il link istituzionale `www.sondaggipoliticoelettorali.it` per il deposito obbligatorio contestuale alla diffusione.
- **Integrità dei codici di uscita**: ogni domanda deve includere i codici `97`, `98` e `99` con etichette chiare.
- **Trasparenza statistica**: il margine d'errore teorico deve corrispondere esattamente alla formula gaussiana al 95% applicata alla numerosità campionaria dichiarata.
- **Natura di proposta**: la Scheda AGCOM generata costituisce una proposta tecnica di adempimento regolamentare. La pubblicazione editoriale e il caricamento sul portale della Presidenza del Consiglio dei Ministri richiedono la formale approvazione del ricercatore responsabile di Noto Sondaggi SRL.
