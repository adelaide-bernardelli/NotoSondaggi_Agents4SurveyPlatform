import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts.export_limesurvey import (
    TSV_COLUMNS,
    export_to_limesurvey_tsv,
    generate_tsv_records,
    parse_questionnaire_markdown,
    translate_relevance,
    validate_tsv_records,
)


class TestExportLimeSurvey(unittest.TestCase):
    """Test unitari per l'esportatore nativo LimeSurvey TSV (14 colonne standard)."""

    def setUp(self):
        self.demo_final_path = ROOT_DIR / "examples" / "demo_run_biblioteca" / "final.md"
        self.script_path = ROOT_DIR / "scripts" / "export_limesurvey.py"

    def test_demo_questionnaire_tsv_export(self):
        """Verifica l'esportazione del questionario demo reale di biblioteca."""
        with tempfile.TemporaryDirectory() as tmpdir:
            out_path = Path(tmpdir) / "demo_limesurvey.txt"
            success = export_to_limesurvey_tsv(self.demo_final_path, out_path, lang="it")
            self.assertTrue(success, "L'esportazione del questionario demo dovrebbe riuscire")
            self.assertTrue(out_path.exists(), "Il file di output TSV deve essere creato")

            lines = out_path.read_text(encoding="utf-8").splitlines()
            self.assertGreater(len(lines), 10, "Il file TSV deve contenere header e righe di dati")

            # 1. Verifica header
            header = lines[0].split("\t")
            self.assertEqual(header, TSV_COLUMNS, "L'header deve coincidere con le 14 colonne standard")

            # 2. Verifica che ogni riga abbia esattamente 14 colonne
            classes_found = set()
            q_names_found = []
            a_codes_found = set()
            q_ids = set()

            for idx, line in enumerate(lines):
                cols = line.split("\t")
                self.assertEqual(
                    len(cols),
                    14,
                    f"La riga {idx} non ha 14 colonne: {line}",
                )
                if idx > 0:
                    r_id, related_id, r_class, r_type, name, rel, text, help_t, lang, val, mand, other, dflt, same_dflt = cols
                    classes_found.add(r_class)
                    if r_class == "Q":
                        q_ids.add(r_id)
                        q_names_found.append(name)
                        self.assertEqual(r_type, "L", "Il questionario demo usa domande a lista radio (L)")
                        self.assertEqual(mand, "Y", "Le domande a scelta devono essere obbligatorie")
                    elif r_class == "A":
                        a_codes_found.add(name)
                        self.assertIn(
                            related_id,
                            q_ids,
                            f"L'opzione di risposta {name} ha un related_id {related_id} non associato a un Q",
                        )

            # 3. Verifica classi attese nel questionario lineare
            self.assertIn("S", classes_found, "Classe S (impostazioni indagine) obbligatoria")
            self.assertIn("SL", classes_found, "Classe SL (lingua indagine) obbligatoria")
            self.assertIn("G", classes_found, "Classe G (gruppi) obbligatoria")
            self.assertIn("Q", classes_found, "Classe Q (domande) obbligatoria")
            self.assertIn("A", classes_found, "Classe A (risposte) obbligatoria")

            # 4. Verifica domande e codici di non risposta nel demo
            self.assertEqual(q_names_found, ["Q1", "Q2a", "Q2b"])
            self.assertIn("98", a_codes_found, "Codice 98 (Non so) deve essere presente nelle risposte")
            self.assertIn("99", a_codes_found, "Codice 99 (Rifiuto/Preferisco non rispondere) presente")

    def test_structured_questionnaire_with_filters_and_code_97(self):
        """Verifica questionario strutturato a sezioni con filtri, codice 97, matrice (F) e multipla (M)."""
        structured_md = """# Indagine Civica e Mobilità Urbana Sostenibile

## 1. Metadati di Consolidamento
- Caso: mobilita-urbana
- Modalita: CAWI

## 4. Testo Definitivo del Questionario Candidato

### Sezione A — Profilo di Mobilità

#### Q01 — Frequenza di utilizzo del trasporto pubblico
- **Testo per il rispondente**: Con quale frequenza utilizza i mezzi pubblici nella sua città?
- **Tipo di domanda**: Chiusa singola
- **Opzioni e codici di risposta**:
  - 1 = Tutti i giorni o quasi
  - 2 = Qualche volta a settimana
  - 3 = Meno spesso o mai
- **Codici distinti di uscita**:
  - `97` = Non applicabile (non risiede nel bacino servito)
  - `98` = Non so / Non ricordo
  - `99` = Preferisco non rispondere
- **Regola di filtro / skip**: Nessuno (tutti i rispondenti)
- **Istruzioni per intervistatore / programmazione CATI-CAWI-CAPI**: Mostrare a tutto il campione

#### Q02 — Motivi di mancato utilizzo
- **Testo per il rispondente**: Quali sono i motivi principali per cui non utilizza i mezzi pubblici?
- **Tipo di domanda**: Chiusa multipla
- **Opzioni e codici di risposta**:
  - 1 = Fermate troppo distanti
  - 2 = Orari inadeguati o corse poco frequenti
  - 3 = Costo del biglietto elevato
- **Codici distinti di uscita**:
  - `97` = Non applicabile
  - `98` = Non so
  - `99` = Preferisco non rispondere
- **Regola di filtro / skip**: Solo se Q01 == 3
- **Istruzioni per intervistatore / programmazione CATI-CAWI-CAPI**: Scelta multipla, max 3 risposte

### Sezione B — Valutazione della Qualità

#### Q03 — Valutazione aspetti del servizio
- **Testo per il rispondente**: Quanto è soddisfatto dei seguenti aspetti del servizio di trasporto?
- **Tipo di domanda**: Batteria
- **Item della batteria**:
  - SQ01 = Pulizia dei mezzi
  - SQ02 = Puntualità delle corse
  - SQ03 = Sicurezza a bordo
- **Opzioni e codici di risposta**:
  - 1 = Molto soddisfatto
  - 2 = Abbastanza soddisfatto
  - 3 = Poco soddisfatto
  - 4 = Per nulla soddisfatto
- **Codici distinti di uscita**:
  - `97` = Non applicabile
  - `98` = Non so
  - `99` = Preferisco non rispondere
- **Regola di filtro / skip**: Se Q01 in (1, 2)
- **Istruzioni per intervistatore / programmazione CATI-CAWI-CAPI**: Scala a 4 punti

#### Q04 — Suggerimenti liberi
- **Testo per il rispondente**: Quali proposte ha per migliorare il servizio di mobilità?
- **Tipo di domanda**: Aperta
- **Regola di filtro / skip**: Nessun filtro
- **Istruzioni per intervistatore / programmazione CATI-CAWI-CAPI**: Testo libero facoltativo
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            md_path = Path(tmpdir) / "structured_final.md"
            out_path = Path(tmpdir) / "structured_limesurvey.txt"
            md_path.write_text(structured_md, encoding="utf-8")

            success = export_to_limesurvey_tsv(md_path, out_path, lang="it")
            self.assertTrue(success, "L'esportazione del questionario strutturato deve riuscire")

            lines = out_path.read_text(encoding="utf-8").splitlines()
            records = [l.split("\t") for l in lines]

            # 1. Verifica 14 colonne su tutti i record
            for idx, r in enumerate(records):
                self.assertEqual(len(r), 14, f"Riga {idx} non ha 14 colonne")

            # 2. Verifica gruppi creati
            groups = [r for r in records if r[2] == "G"]
            self.assertEqual(len(groups), 2, "Devono essere presenti esattamente 2 gruppi (Sezione A e Sezione B)")
            self.assertIn("Profilo di Mobilità", groups[0][6])
            self.assertIn("Valutazione della Qualità", groups[1][6])

            # 3. Verifica domande
            questions = {r[4]: r for r in records if r[2] == "Q"}
            self.assertEqual(set(questions.keys()), {"Q01", "Q02", "Q03", "Q04"})

            # Q01: Singola, codice 97 presente, relevance 1
            q01 = questions["Q01"]
            self.assertEqual(q01[3], "L")
            self.assertEqual(q01[5], "1")
            q01_id = q01[0]

            # Opzioni di Q01 devono contenere 97, 98, 99
            q01_answers = [r for r in records if r[2] == "A" and r[1] == q01_id]
            q01_codes = {r[4] for r in q01_answers}
            self.assertIn("97", q01_codes, "Codice 97 deve essere presente nelle risposte di Q01")
            self.assertIn("98", q01_codes)
            self.assertIn("99", q01_codes)
            opt_97 = next(r for r in q01_answers if r[4] == "97")
            self.assertIn("Non applicabile", opt_97[6])

            # Q02: Multipla (M) con filtri ExpressionScript e subquestions (SQ)
            q02 = questions["Q02"]
            self.assertEqual(q02[3], "M")
            self.assertEqual(q02[5], 'Q01.NAOK == "3"')
            q02_id = q02[0]

            # Le opzioni di scelta multipla devono essere salvate come SQ collegate a Q02
            q02_sq = [r for r in records if r[2] == "SQ" and r[1] == q02_id]
            q02_sq_codes = {r[4] for r in q02_sq}
            self.assertIn("1", q02_sq_codes)
            self.assertIn("97", q02_sq_codes)
            self.assertIn("98", q02_sq_codes)
            self.assertIn("99", q02_sq_codes)

            # Q03: Batteria (F) con SQ (righe) e A (colonne)
            q03 = questions["Q03"]
            self.assertEqual(q03[3], "F")
            self.assertEqual(q03[5], '(Q01.NAOK == "1" || Q01.NAOK == "2")')
            q03_id = q03[0]

            q03_sq = [r for r in records if r[2] == "SQ" and r[1] == q03_id]
            q03_sq_codes = {r[4] for r in q03_sq}
            self.assertEqual(q03_sq_codes, {"SQ01", "SQ02", "SQ03"})

            q03_a = [r for r in records if r[2] == "A" and r[1] == q03_id]
            q03_a_codes = {r[4] for r in q03_a}
            self.assertIn("1", q03_a_codes)
            self.assertIn("4", q03_a_codes)
            self.assertIn("97", q03_a_codes)

            # Q04: Aperta (T), non obbligatoria
            q04 = questions["Q04"]
            self.assertEqual(q04[3], "T")
            self.assertEqual(q04[10], "N")

    def test_translate_relevance(self):
        """Verifica la corretta traduzione dei filtri in ExpressionScript."""
        self.assertEqual(translate_relevance("Solo se Q01 == 1"), 'Q01.NAOK == "1"')
        self.assertEqual(translate_relevance("Solo se Q01 = 1"), 'Q01.NAOK == "1"')
        self.assertEqual(translate_relevance("Se Q1 != 99"), 'Q1.NAOK != "99"')
        self.assertEqual(
            translate_relevance("Se Q01 in (1, 2)"),
            '(Q01.NAOK == "1" || Q01.NAOK == "2")',
        )
        self.assertEqual(translate_relevance("!is_empty(Q02)"), '!is_empty(Q02)')
        self.assertEqual(translate_relevance("Nessuno (tutti i rispondenti)"), "1")
        self.assertEqual(translate_relevance("Nessuno"), "1")
        self.assertEqual(translate_relevance(""), "1")
        self.assertEqual(translate_relevance(None), "1")

        # Verifica preservazione espressioni che contengono già .NAOK (non devono diventare NAOK.NAOK)
        self.assertEqual(translate_relevance('Q01.NAOK == "1"'), 'Q01.NAOK == "1"')
        self.assertEqual(translate_relevance('Q01.NAOK != "99"'), 'Q01.NAOK != "99"')
        self.assertEqual(
            translate_relevance('(Q01.NAOK == "1" || Q01.NAOK == "2")'),
            '(Q01.NAOK == "1" || Q01.NAOK == "2")',
        )

        # Verifica supporto connettivi italiani 'oppure' e 'ed'
        self.assertEqual(
            translate_relevance("Q01 == 1 oppure Q02 == 2"),
            '(Q01.NAOK == "1" || Q02.NAOK == "2")',
        )
        self.assertEqual(
            translate_relevance("Q01 == 1 ed Q02 == 2"),
            '(Q01.NAOK == "1" && Q02.NAOK == "2")',
        )

        # Verifica valori con caratteri accentati (es. "Sì")
        self.assertEqual(translate_relevance("Q01 == Sì"), 'Q01.NAOK == "Sì"')

        # Verifica fallback su linguaggio naturale inverso
        self.assertEqual(translate_relevance("Solo se ha risposto 1 a Q01"), 'Q01.NAOK == "1"')

    def test_multiline_interviewer_instructions(self):
        """Verifica la corretta acquisizione di note e istruzioni per intervistatore su più righe."""
        md = """# Test Istruzioni
### Domande
#### Q01 — Soddisfazione
- **Testo per il rispondente**: Come valuta il servizio?
- **Istruzioni per intervistatore**:
  - Non leggere le opzioni ad alta voce
  - Registrare la prima reazione spontanea
- **Opzioni e codici di risposta**:
  - 1 = Positivo
  - 2 = Negativo
"""
        survey = parse_questionnaire_markdown(md)
        q = survey.groups[0].questions[0]
        self.assertIn("Non leggere le opzioni", q.help_text)
        self.assertIn("Registrare la prima reazione", q.help_text)

    def test_italian_question_prefixes(self):
        """Verifica il supporto di prefissi convenzionali italiani (D per Domanda, P per Principale)."""
        md = """# Questionario Italiano
### Domande
D01. Come valuta i servizi del comune?
1. Ottimo
2. Pessimo
98. Non so
99. Preferisco non rispondere

#### D02 — Frequenza di fruizione
- **Testo per il rispondente**: Con quale frequenza si reca agli sportelli?
- **Opzioni e codici di risposta**:
  - 1 = Settimanale
  - 2 = Mensile
"""
        survey = parse_questionnaire_markdown(md)
        self.assertEqual(len(survey.groups[0].questions), 2)
        q_names = [q.name for q in survey.groups[0].questions]
        self.assertEqual(q_names, ["D01", "D02"])

    def test_welcome_text_and_description_extraction(self):
        """Verifica l'estrazione di welcome_text e descrizione dai metadati/compliance."""
        md = """# Indagine Civica
- **Caso**: test-biblioteca

## 3. Prescrizioni di Compliance
- **Testo introduttivo e informativa breve proposta per il rispondente**: Benvenuti a questa indagine sui servizi civici.

### Domande
Q01. Domanda singola?
1. Sì
2. No
"""
        survey = parse_questionnaire_markdown(md)
        self.assertEqual(survey.welcome_text, "Benvenuti a questa indagine sui servizi civici.")
        self.assertIn("test-biblioteca", survey.description)

        records = generate_tsv_records(survey)
        sl_welcome = next(r for r in records if r[2] == "SL" and r[4] == "surveyls_welcometext")
        self.assertEqual(sl_welcome[6], "Benvenuti a questa indagine sui servizi civici.")

    def test_validation_catches_invalid_question_structure(self):
        """Verifica che validate_tsv_records rilevi anomalie strutturali per tipo domanda."""
        # Creiamo un TSV sintetico con una domanda L priva di opzioni A
        records = [
            list(TSV_COLUMNS),
            ["", "", "S", "", "language", "", "it", "", "", "", "", "", "", ""],
            ["", "", "SL", "", "surveyls_title", "", "Titolo", "", "it", "", "", "", "", ""],
            ["1", "0", "G", "", "G01", "1", "Gruppo", "", "it", "", "", "", "", ""],
            ["2", "0", "Q", "L", "Q01", "1", "Testo domanda", "", "it", "", "Y", "N", "", ""],
            # Nessuna riga A associata a Q01
        ]
        errors = validate_tsv_records(records)
        self.assertTrue(any("priva di opzioni di risposta" in e for e in errors))

    def test_unnumbered_bullet_options(self):
        """Verifica la corretta gestione di opzioni a bullet non numerate con auto-assegnazione codici."""
        md = """# Test Unnumbered
### Domande
#### Q01 — Valutazione sintetica
- **Tipo di domanda**: Chiusa singola
- **Testo per il rispondente**: Quale opinione esprime?
- **Opzioni e codici di risposta**:
  - Molto positiva
  - Abbastanza positiva
  - Negativa
- **Codici distinti di uscita**:
  - Non so / non conosco
  - Preferisco non rispondere
"""
        survey = parse_questionnaire_markdown(md)
        q = survey.groups[0].questions[0]
        codes = [o.code for o in q.options]
        self.assertIn("1", codes)
        self.assertIn("2", codes)
        self.assertIn("3", codes)
        self.assertIn("98", codes, "Non so non numerato deve ricevere codice 98")
        self.assertIn("99", codes, "Preferisco non rispondere non numerato deve ricevere codice 99")

    def test_cli_execution(self):
        """Verifica l'esecuzione della CLI autonoma via subprocess."""
        with tempfile.TemporaryDirectory() as tmpdir:
            out_file = Path(tmpdir) / "cli_output.txt"
            cmd = [
                sys.executable,
                str(self.script_path),
                str(self.demo_final_path),
                "--output",
                str(out_file),
                "--lang",
                "it",
            ]
            res = subprocess.run(cmd, capture_output=True, text=True)
            self.assertEqual(res.returncode, 0, f"CLI fallita: {res.stderr}")
            self.assertTrue(out_file.exists(), "Il file esportato via CLI deve esistere")
            self.assertIn("[OK] File LimeSurvey TSV esportato con successo", res.stdout)

    def test_empty_or_invalid_file(self):
        """Verifica il comportamento in presenza di file inesistenti o privi di domande."""
        with tempfile.TemporaryDirectory() as tmpdir:
            fake_path = Path(tmpdir) / "non_existent.md"
            out_path = Path(tmpdir) / "out.txt"
            # File non esistente
            self.assertFalse(export_to_limesurvey_tsv(fake_path, out_path))

            # File privo di domande
            empty_file = Path(tmpdir) / "empty.md"
            empty_file.write_text("# Documento senza domande\nTesto generico.", encoding="utf-8")
            self.assertFalse(export_to_limesurvey_tsv(empty_file, out_path))


if __name__ == "__main__":
    unittest.main()
