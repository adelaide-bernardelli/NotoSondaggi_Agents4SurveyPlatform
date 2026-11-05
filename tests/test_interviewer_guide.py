#!/usr/bin/env python3
"""
test_interviewer_guide.py — Suite di test unitari per il generatore della guida intervistatore (Milestone M5).

Verifica:
1. Estrazione delle note di regia e istruzioni per l'intervistatore (somministrazione, rotazione, filtri);
2. Presenza dei box di regia dedicati: somministrazione, probing neutrale, gestione codici 97/98/99;
3. Generazione e validità formale dell'output Markdown con GitHub alert syntax;
4. Generazione output HTML completo con corretta formattazione inline dei tag;
5. Gestione difensiva dei formati opzionali (Word .docx, mock completo ed esecuzione fallback in assenza di python-docx);
6. Supporto avanzato per testo multi-linea, opzioni a punto elenco non numerate e isolamento attributi;
7. Tutela delle scale ordinali contro rotazioni casuali inappropriate;
8. Supporto a codici di uscita personalizzati e tolleranza maiuscole/minuscole nella CLI.
"""

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

# Inserimento della root di progetto nel percorso di ricerca moduli
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts.generate_interviewer_guide import (
    HAS_DOCX,
    AnswerOption,
    SubQuestionItem,
    SurveyMetadata,
    SurveyQuestion,
    _add_markdown_run,
    _build_administration_instructions,
    _build_neutral_probing_notes,
    _build_nonresponse_guidelines,
    _format_markdown_inline_to_html,
    generate_guide,
    generate_interviewer_guide_docx,
    generate_interviewer_guide_html,
    generate_interviewer_guide_md,
    main,
    parse_questionnaire,
)


class TestInterviewerGuide(unittest.TestCase):
    """Test unitari approfonditi per la generazione della guida per la sala interviste (CATI / CAPI)."""

    def setUp(self):
        self.script_path = ROOT_DIR / "scripts" / "generate_interviewer_guide.py"
        self.demo_final_path = ROOT_DIR / "examples" / "demo_run_biblioteca" / "final.md"

        self.structured_md_sample = """# Indagine sulla Mobilità Urbana e Servizi Civici
## 1. Metadati di Consolidamento
- **Caso**: mobilita-civica-2026
- **Data consolidamento**: 2026-11-05
- **Modalità**: CATI / CAPI
- **Target**: Residenti maggiorenni
- **Informativa**: Buongiorno, la contatto per conto di Noto Sondaggi per una breve indagine sui trasporti pubblici della sua città.

## 4. Testo Definitivo del Questionario Candidato

### Sezione A — Frequenza e Motivi

#### Q01 — Frequenza di fruizione del servizio
- **Testo per il rispondente**: Con quale frequenza utilizza i mezzi pubblici nella sua città?
- **Tipo di domanda**: Chiusa singola
- **Istruzioni per intervistatore**: Non leggere le opzioni, attendere risposta spontanea
- **Opzioni e codici di risposta**:
  - 1 = Tutti i giorni o quasi
  - 2 = Qualche volta a settimana
  - 3 = Meno spesso o mai
- **Codici distinti di uscita**:
  - `97` = Non applicabile (non risiede nell'area servita)
  - `98` = Non so / Non ricorda
  - `99` = Preferisco non rispondere

#### Q02 — Motivi di mancato utilizzo
- **Testo per il rispondente**: Quali sono le motivazioni principali per cui non utilizza i mezzi pubblici?
- **Tipo di domanda**: Chiusa multipla
- **Regola di filtro / skip**: Solo se Q01 == 3
- **Istruzioni per intervistatore**: Scelta multipla, max 3 risposte. Ruotare casualmente l'ordine di lettura delle opzioni.
- **Opzioni e codici di risposta**:
  - 1 = Fermate troppo lontane
  - 2 = Corse poco frequenti o orari inadeguati
  - 3 = Costo del biglietto troppo alto
  - 4 = Preferenza per il mezzo privato
- **Codici distinti di uscita**:
  - `97` = Non applicabile (utilizzatore regolare)
  - `98` = Non so
  - `99` = Rifiuto esplicito

### Sezione B — Valutazione della Qualità

#### Q03 — Batteria di soddisfazione aspetti del servizio
- **Testo per il rispondente**: Le leggerò ora alcuni aspetti del servizio di trasporto pubblico. Per ciascuno mi indichi il suo livello di gradimento:
- **Tipo di domanda**: Batteria
- **Istruzioni per intervistatore**: Ruotare casualmente l'ordine degli item. Assicurarsi che il rispondente mantenga la scala a 4 punti.
- **Item della batteria**:
  - SQ01 = Pulizia e igiene dei mezzi
  - SQ02 = Puntualità e rispetto degli orari
  - SQ03 = Cortesia del personale di bordo
- **Opzioni e codici di risposta**:
  - 1 = Molto soddisfacente
  - 2 = Abbastanza soddisfacente
  - 3 = Poco soddisfacente
  - 4 = Per nulla soddisfacente
- **Codici distinti di uscita**:
  - `97` = Non applicabile
  - `98` = Non so
  - `99` = Preferisco non rispondere

#### Q04 — Proposte e pareri liberi
- **Testo per il rispondente**: Quale suggerimento si sente di rivolgere all'amministrazione comunale per migliorare la mobilità urbana?
- **Tipo di domanda**: Aperta
- **Istruzioni per intervistatore**: Trascrivere fedelmente la risposta testuale senza riassumere.
"""

    def test_parse_linear_questionnaire(self):
        """Verifica il parsing corretto di un questionario lineare (es. demo biblioteca)."""
        content = self.demo_final_path.read_text(encoding="utf-8")
        metadata, questions = parse_questionnaire(content)

        self.assertEqual(metadata.case_id, "demo-biblioteca")
        self.assertEqual(len(questions), 3)
        self.assertEqual(questions[0].id, "Q1")
        self.assertIn("Come valuta complessivamente i servizi", questions[0].text)
        self.assertEqual(len(questions[0].options), 6)  # 4 sostantive + 98 + 99

        # Verifica codici sostantivi ed exit codes
        codes = [opt.code for opt in questions[0].options]
        self.assertEqual(codes, ["1", "2", "3", "4", "98", "99"])
        substantive = [opt.code for opt in questions[0].substantive_options]
        self.assertEqual(substantive, ["1", "2", "3", "4"])
        exit_codes = [opt.code for opt in questions[0].exit_codes]
        self.assertIn("98", exit_codes)
        self.assertIn("99", exit_codes)

    def test_parse_structured_questionnaire(self):
        """Verifica il parsing di un questionario strutturato con sezioni, filtri, multiline help e batterie."""
        metadata, questions = parse_questionnaire(self.structured_md_sample)

        self.assertEqual(metadata.case_id, "mobilita-civica-2026")
        self.assertEqual(metadata.mode, "CATI / CAPI")
        self.assertIn("Buongiorno, la contatto", metadata.welcome_intro)
        self.assertEqual(len(questions), 4)

        # Q01: Singola spontanea con codice 97
        q1 = questions[0]
        self.assertEqual(q1.id, "Q01")
        self.assertEqual(q1.q_type, "singola")
        self.assertIn("Non leggere le opzioni", q1.interviewer_notes)
        self.assertEqual(len(q1.substantive_options), 3)
        self.assertTrue(any(o.code == "97" for o in q1.exit_codes))

        # Q02: Multipla con filtro attivo e rotazione
        q2 = questions[1]
        self.assertEqual(q2.id, "Q02")
        self.assertEqual(q2.q_type, "multipla")
        self.assertTrue(q2.has_filter)
        self.assertEqual(q2.filter_rule, "Solo se Q01 == 3")
        self.assertIn("max 3 risposte", q2.interviewer_notes)
        self.assertIn("Ruotare casualmente", q2.interviewer_notes)

        # Q03: Batteria di item
        q3 = questions[2]
        self.assertEqual(q3.id, "Q03")
        self.assertEqual(q3.q_type, "batteria")
        self.assertEqual(len(q3.subquestions), 3)
        self.assertEqual(q3.subquestions[0].code, "SQ01")
        self.assertEqual(len(q3.substantive_options), 4)

        # Q04: Aperta
        q4 = questions[3]
        self.assertEqual(q4.id, "Q04")
        self.assertEqual(q4.q_type, "aperta")
        self.assertIn("Trascrivere fedelmente", q4.interviewer_notes)

    def test_build_administration_instructions_keywords(self):
        """Verifica che le istruzioni di regia contengano le etichette chiave richieste dalle specifiche."""
        metadata, questions = parse_questionnaire(self.structured_md_sample)
        q1, q2, q3, q4 = questions

        # Q1: Spontanea / Non leggere
        inst1 = _build_administration_instructions(q1)
        inst1_str = " ".join(inst1)
        self.assertIn("NON LEGGERE LE OPZIONI", inst1_str)
        self.assertIn("SPONTANEA", inst1_str)

        # Q2: Filtro attivo, Scelta multipla, Rotazione casuale
        inst2 = _build_administration_instructions(q2)
        inst2_str = " ".join(inst2)
        self.assertIn("FILTRO ATTIVO", inst2_str)
        self.assertIn("Solo se Q01 == 3", inst2_str)
        self.assertIn("SCELTA MULTIPLA", inst2_str)
        self.assertIn("FINO A 3 RISPOSTE", inst2_str)
        self.assertIn("ROTAZIONE CASUALE", inst2_str)

        # Q3: Batteria e rotazione
        inst3 = _build_administration_instructions(q3)
        inst3_str = " ".join(inst3)
        self.assertIn("BATTERIA DI ITEM", inst3_str)
        self.assertIn("ROTAZIONE CASUALE", inst3_str)

        # Q4: Domanda aperta
        inst4 = _build_administration_instructions(q4)
        inst4_str = " ".join(inst4)
        self.assertIn("DOMANDA APERTA", inst4_str)
        self.assertIn("NON LEGGERE ALCUNA OPZIONE", inst4_str)

    def test_neutral_probing_and_nonresponse_guidelines(self):
        """Verifica la completezza dei contenuti nei box di probing neutrale e gestione codici 97/98/99."""
        metadata, questions = parse_questionnaire(self.structured_md_sample)
        q1 = questions[0]

        # Probing neutrale
        probing = _build_neutral_probing_notes(q1)
        probing_str = " ".join(probing)
        self.assertIn("Chiarimenti ammessi", probing_str)
        self.assertIn("senza fornire esempi concreti che possano orientare", probing_str)
        self.assertIn("tono calmo e neutrale", probing_str)
        self.assertIn("Neutralità dell'operatore", probing_str)

        # Non response guidelines
        nr = _build_nonresponse_guidelines(q1)
        nr_str = " ".join(nr)
        self.assertIn("Codice 97 — Non applicabile", nr_str)
        self.assertIn("Codice 98 — Non so", nr_str)
        self.assertIn("Codice 99 — Rifiuto", nr_str)
        self.assertIn("probing moderato", nr_str)
        self.assertIn("MAI forzare una risposta", nr_str)
        self.assertIn("Divieto assoluto di insistere", nr_str)

    def test_markdown_guide_structure_and_callouts(self):
        """Verifica la generazione formale del Markdown con GitHub alerts (> [!IMPORTANT], > [!NOTE], > [!TIP])."""
        metadata, questions = parse_questionnaire(self.structured_md_sample)
        md_output = generate_interviewer_guide_md(metadata, questions)

        self.assertIn("# GUIDA OPERATIVA PER LA SALA INTERVISTE (CATI / CAPI)", md_output)
        self.assertIn("## Indagine: Indagine sulla Mobilità Urbana e Servizi Civici", md_output)
        self.assertIn("> [!NOTE] **PROTOCOLLO GENERALE DI CONDUZIONE INTERVISTA", md_output)
        self.assertIn("> [!IMPORTANT] **ISTRUZIONI DI SOMMINISTRAZIONE & REGIA INTERVISTATORE**", md_output)
        self.assertIn("#### TESTO DA PRONUNCIARE A VOCE ALTA:", md_output)
        self.assertIn("> [!NOTE] **NOTE DI PROBING NEUTRALE (CHIARIMENTI AMMESSI)**", md_output)
        self.assertIn("> [!TIP] **TRATTAMENTO DELLE NON RISPOSTE (CODICI 97 / 98 / 99)**", md_output)

        # Verifica tabella opzioni e item batteria
        self.assertIn("| Codice | Opzione di Risposta | Istruzione Operativa per l'Intervistatore |", md_output)
        self.assertIn("| Codice Item | Formulazione da Leggere al Rispondente | Note di Lettura |", md_output)
        self.assertIn("`SQ01`", md_output)

    def test_html_guide_generation(self):
        """Verifica la generazione di file HTML valido con styling autonomo."""
        metadata, questions = parse_questionnaire(self.structured_md_sample)
        html_output = generate_interviewer_guide_html(metadata, questions)

        self.assertTrue(html_output.startswith("<!DOCTYPE html>"))
        self.assertIn("<title>Guida Intervistatore — Indagine sulla Mobilità Urbana", html_output)
        self.assertIn("speech-box", html_output)
        self.assertIn("callout-regia", html_output)
        self.assertIn("callout-probing", html_output)
        self.assertIn("callout-nr", html_output)
        self.assertIn("</html>", html_output)

    def test_html_bold_rendering(self):
        """Verifica che nell'output HTML i blocchi in grassetto siano tradotti in <strong> e non rimangano **asterischi**."""
        metadata, questions = parse_questionnaire(self.structured_md_sample)
        html_output = generate_interviewer_guide_html(metadata, questions)

        self.assertIn("<strong>Codice 97 — Non applicabile</strong>", html_output)
        self.assertIn("<strong>Codice 98 — Non so / Non ricorda / Non ha un&#x27;opinione</strong>", html_output)
        self.assertIn("<strong>Codice 99 — Rifiuto / Preferisco non rispondere</strong>", html_output)
        # Non devono essere presenti asterischi non renderizzati nei box di non risposta
        self.assertNotIn("**Codice 97", html_output)
        self.assertNotIn("**Codice 98", html_output)

    def test_generate_guide_format_md_and_html(self):
        """Verifica la generazione su file per formato md e html via funzione Python."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = Path(tmpdir) / "test_questionnaire.md"
            input_file.write_text(self.structured_md_sample, encoding="utf-8")

            # 1. Output MD
            out_md = Path(tmpdir) / "output_guida.md"
            ret_md = generate_guide(input_file, out_md, output_format="md")
            self.assertEqual(ret_md, 0)
            self.assertTrue(out_md.exists())
            self.assertGreater(len(out_md.read_text(encoding="utf-8")), 500)

            # 2. Output HTML
            out_html = Path(tmpdir) / "output_guida.html"
            ret_html = generate_guide(input_file, out_html, output_format="html")
            self.assertEqual(ret_html, 0)
            self.assertTrue(out_html.exists())
            self.assertIn("<!DOCTYPE html>", out_html.read_text(encoding="utf-8"))

    def test_docx_defensive_fallback_when_not_installed(self):
        """Verifica che in assenza di python-docx l'esecuzione non fallisca e venga eseguito fallback automatico su MD."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = Path(tmpdir) / "test_input.md"
            input_file.write_text(self.structured_md_sample, encoding="utf-8")
            out_docx = Path(tmpdir) / "guida.docx"

            # Patch HAS_DOCX to False per simulare ambiente privo di python-docx
            with patch("scripts.generate_interviewer_guide.HAS_DOCX", False):
                ret = generate_guide(input_file, out_docx, output_format="docx")
                self.assertEqual(ret, 0, "Il fallback su MD in assenza di docx non deve fallire con errore")

                fallback_md = Path(tmpdir) / "guida.md"
                self.assertTrue(fallback_md.exists(), "Il file di fallback Markdown deve essere stato creato")
                self.assertIn("GUIDA OPERATIVA", fallback_md.read_text(encoding="utf-8"))

    def test_docx_generation_with_mock(self):
        """Verifica l'intero percorso di generazione Word (.docx) mockando la libreria python-docx."""
        metadata, questions = parse_questionnaire(self.structured_md_sample)

        mock_doc = MagicMock()
        mock_section = MagicMock()
        mock_doc.sections = [mock_section]
        mock_p = MagicMock()
        mock_run = MagicMock()
        mock_p.add_run.return_value = mock_run
        mock_doc.add_paragraph.return_value = mock_p
        mock_doc.add_heading.return_value = mock_p

        mock_table = MagicMock()
        mock_row = MagicMock()
        mock_cell = MagicMock()
        mock_row.cells = [mock_cell, mock_cell, mock_cell]
        mock_table.rows = [mock_row]
        mock_table.add_row.return_value = mock_row
        mock_doc.add_table.return_value = mock_table

        mock_table_align = MagicMock()
        mock_table_align.CENTER = "CENTER"

        with patch("scripts.generate_interviewer_guide.HAS_DOCX", True), \
             patch("scripts.generate_interviewer_guide.Document", return_value=mock_doc), \
             patch("scripts.generate_interviewer_guide.WD_TABLE_ALIGNMENT", mock_table_align), \
             patch("scripts.generate_interviewer_guide.Inches", side_effect=lambda x: x), \
             patch("scripts.generate_interviewer_guide.Pt", side_effect=lambda x: x), \
             patch("scripts.generate_interviewer_guide.RGBColor", side_effect=lambda r, g, b: (r, g, b)):
            with tempfile.TemporaryDirectory() as tmpdir:
                out_path = Path(tmpdir) / "mocked_guide.docx"
                ok = generate_interviewer_guide_docx(metadata, questions, out_path)
                self.assertTrue(ok)
                mock_doc.save.assert_called_once_with(str(out_path))
                self.assertTrue(mock_doc.add_heading.called)
                self.assertTrue(mock_doc.add_table.called)

    def test_both_formats_flag(self):
        """Verifica la generazione simultanea con --format both."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = Path(tmpdir) / "test_both.md"
            input_file.write_text(self.structured_md_sample, encoding="utf-8")
            out_both = Path(tmpdir) / "guida_completa"

            ret = generate_guide(input_file, out_both, output_format="both")
            self.assertEqual(ret, 0)

            md_file = Path(tmpdir) / "guida_completa.md"
            self.assertTrue(md_file.exists())
            self.assertIn("GUIDA OPERATIVA", md_file.read_text(encoding="utf-8"))

    def test_cli_execution_on_demo_biblioteca(self):
        """Verifica l'esecuzione da riga di comando (CLI) sul caso demo reale della biblioteca."""
        with tempfile.TemporaryDirectory() as tmpdir:
            out_path = Path(tmpdir) / "guida_intervistatore_test.md"
            cmd = [
                sys.executable,
                str(self.script_path),
                str(self.demo_final_path),
                "--format",
                "md",
                "--output",
                str(out_path),
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, f"CLI execution failed: {result.stderr}")
            self.assertTrue(out_path.exists(), "Il file di output CLI deve esistere")

            content = out_path.read_text(encoding="utf-8")
            self.assertIn("demo-biblioteca", content)
            self.assertIn("### Q1", content)
            self.assertIn("### Q2a", content)
            self.assertIn("### Q2b", content)
            self.assertIn("ISTRUZIONI DI SOMMINISTRAZIONE & REGIA INTERVISTATORE", content)
            self.assertIn("NOTE DI PROBING NEUTRALE", content)
            self.assertIn("TRATTAMENTO DELLE NON RISPOSTE (CODICI 97 / 98 / 99)", content)

    def test_cli_error_handling(self):
        """Verifica che la CLI gestisca errori di file mancante o vuoto con codice di uscita 1."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # 1. File non esistente
            non_existent = Path(tmpdir) / "ghost.md"
            cmd_missing = [sys.executable, str(self.script_path), str(non_existent)]
            res_missing = subprocess.run(cmd_missing, capture_output=True, text=True)
            self.assertEqual(res_missing.returncode, 1)
            self.assertIn("[ERRORE]", res_missing.stderr)

            # 2. File vuoto privo di domande
            empty_file = Path(tmpdir) / "empty.md"
            empty_file.write_text("# Titolo\nNessuna domanda presente qui.", encoding="utf-8")
            cmd_empty = [sys.executable, str(self.script_path), str(empty_file)]
            res_empty = subprocess.run(cmd_empty, capture_output=True, text=True)
            self.assertEqual(res_empty.returncode, 1)
            self.assertIn("[ERRORE]", res_empty.stderr)

    def test_italian_prefixes_and_inline_tags(self):
        """Verifica il supporto a prefissi convenzionali italiani (D, P) e tag inline [REGIA], [FILTRO]."""
        md_text = """# Indagine Opinione
### Domande
D01. Quanto si sente sicuro a camminare da solo di notte nella sua zona? [REGIA: SPONTANEA]
1. Molto sicuro
2. Abbastanza sicuro
3. Poco sicuro
4. Per nulla sicuro
98. Non so
99. Preferisco non rispondere

P02. Ha mai segnalato problemi di illuminazione al comune? [FILTRO: SE D01 >= 3]
1. Sì
2. No
97. Non applicabile
98. Non so
99. Rifiuto
"""
        metadata, questions = parse_questionnaire(md_text)
        self.assertEqual(len(questions), 2)
        self.assertEqual(questions[0].id, "D01")
        self.assertEqual(questions[0].interviewer_notes, "SPONTANEA")
        self.assertEqual(questions[1].id, "P02")
        self.assertEqual(questions[1].filter_rule, "SE D01 >= 3")
        self.assertTrue(questions[1].has_filter)

        guide_md = generate_interviewer_guide_md(metadata, questions)
        self.assertIn("### D01", guide_md)
        self.assertIn("SPONTANEA", guide_md)
        self.assertIn("### P02", guide_md)
        self.assertIn("SE D01 >= 3", guide_md)

    def test_cli_html_and_default_output(self):
        """Verifica l'esecuzione da CLI con formato HTML e con percorso di output omesso (default)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_q = Path(tmpdir) / "questionario_test.md"
            temp_q.write_text(self.structured_md_sample, encoding="utf-8")

            # Esecuzione con --format html e output specificato
            out_html = Path(tmpdir) / "guida.html"
            cmd_html = [
                sys.executable,
                str(self.script_path),
                str(temp_q),
                "--format",
                "html",
                "--output",
                str(out_html),
            ]
            res_html = subprocess.run(cmd_html, capture_output=True, text=True)
            self.assertEqual(res_html.returncode, 0)
            self.assertTrue(out_html.exists())
            self.assertIn("<!DOCTYPE html>", out_html.read_text(encoding="utf-8"))

            # Esecuzione senza --output (deriva percorso da input)
            cmd_default = [
                sys.executable,
                str(self.script_path),
                str(temp_q),
                "--format",
                "md",
            ]
            res_default = subprocess.run(cmd_default, capture_output=True, text=True)
            self.assertEqual(res_default.returncode, 0)
            expected_auto = Path(tmpdir) / "questionario_test_guida_intervistatore.md"
            self.assertTrue(expected_auto.exists())
            self.assertIn("GUIDA OPERATIVA", expected_auto.read_text(encoding="utf-8"))

    def test_multiline_question_text_and_direct_text(self):
        """Verifica la corretta acquisizione di testi di domanda multi-linea e di testi posti direttamente sotto l'intestazione."""
        sample = """# Indagine Civica
## 4. Testo Definitivo
#### Q01 — Costrutto Mobilità
- **Testo per il rispondente**:
  Questa è la prima riga della domanda.
  E questa è la seconda riga continuata.
- 1 = Si
- 2 = No

#### Q02 — Valutazione Diretta
Quanto ritiene adeguate le piste ciclabili del suo comune?
- 1 = Molto adeguate
- 2 = Poco adeguate
"""
        metadata, questions = parse_questionnaire(sample)
        self.assertEqual(len(questions), 2)

        # Q01: testo multi-linea dopo Testo per il rispondente
        q1 = questions[0]
        self.assertIn("Questa è la prima riga della domanda", q1.text)
        self.assertIn("seconda riga continuata", q1.text)
        self.assertNotIn("Costrutto Mobilità", q1.text)

        # Q02: testo diretto posto subito sotto il titolo senza bullet
        q2 = questions[1]
        self.assertEqual(q2.text, "Quanto ritiene adeguate le piste ciclabili del suo comune?")

    def test_attribute_isolation_prevent_help_bleeding(self):
        """Verifica che attributi successivi come 'Nota sulla comparabilita storica' non vengano ingeriti nelle note di regia."""
        sample = """# Indagine Benchmark
## 4. Testo Definitivo
#### Q01 — Mobilità
- **Testo per il rispondente**: Usa il treno?
- **Istruzioni per intervistatore**:
  - Non leggere le opzioni
  - Attendere risposta spontanea
- **Nota sulla comparabilita storica**: Raccordo perfetto con serie Istat 2024.
- **Opzioni e codici di risposta**:
  - 1 = Si
  - 2 = No
"""
        metadata, questions = parse_questionnaire(sample)
        q1 = questions[0]
        self.assertIn("Non leggere le opzioni", q1.interviewer_notes)
        self.assertIn("Attendere risposta spontanea", q1.interviewer_notes)
        self.assertNotIn("Nota sulla comparabilita", q1.interviewer_notes)
        self.assertNotIn("Raccordo perfetto", q1.interviewer_notes)

    def test_unnumbered_bullet_options(self):
        """Verifica che opzioni a punto elenco non numerate vengano auto-codificate sequenzialmente (1, 2, 3...) ed exit (98, 99)."""
        sample = """# Indagine Unnumbered
## 4. Testo Definitivo
#### Q01 — Grado di accordo
- **Testo per il rispondente**: Quanto è d'accordo con la seguente affermazione?
- **Opzioni e codici di risposta**:
  - Molto d'accordo
  - Abbastanza d'accordo
  - Poco d'accordo
  - Per nulla d'accordo
- **Codici distinti di uscita**:
  - Non so
  - Preferisco non rispondere
"""
        metadata, questions = parse_questionnaire(sample)
        q1 = questions[0]
        self.assertEqual(q1.q_type, "singola")
        self.assertEqual(len(q1.substantive_options), 4)
        self.assertEqual([o.code for o in q1.substantive_options], ["1", "2", "3", "4"])
        self.assertEqual([o.label for o in q1.substantive_options], [
            "Molto d'accordo", "Abbastanza d'accordo", "Poco d'accordo", "Per nulla d'accordo"
        ])
        self.assertTrue(any(o.code == "98" for o in q1.exit_codes))
        self.assertTrue(any(o.code == "99" for o in q1.exit_codes))

    def test_custom_exit_codes_rendering(self):
        """Verifica che codici di uscita personalizzati (es. 95 Fuori regione) vengano inclusi nella tabella operatore."""
        sample = """# Indagine Territoriale
## 4. Testo Definitivo
#### Q01 — Territorio
- **Testo per il rispondente**: In quale comune risiede?
- **Opzioni e codici di risposta**:
  - 1 = Capoluogo
  - 2 = Altro comune
- **Codici distinti di uscita**:
  - 95 = Fuori regione (escluso da rilevazione)
  - 98 = Non so
  - 99 = Rifiuto
"""
        metadata, questions = parse_questionnaire(sample)
        guide_md = generate_interviewer_guide_md(metadata, questions)

        self.assertIn("`95`", guide_md)
        self.assertIn("Fuori regione (escluso da rilevazione)", guide_md)
        self.assertIn("`98`", guide_md)
        self.assertIn("`99`", guide_md)

    def test_ordinal_scale_rotation(self):
        """Verifica che su una scala ordinale a 5 punti non venga raccomandata la rotazione casuale distorsiva."""
        sample = """# Indagine Scala
## 4. Testo Definitivo
#### Q01 — Scala Likert 5 punti
- **Testo per il rispondente**: Quanto è soddisfatto?
- **Tipo di domanda**: Scala ordinale
- **Opzioni e codici di risposta**:
  - 1 = Molto soddisfatto
  - 2 = Abbastanza soddisfatto
  - 3 = Né soddisfatto né insoddisfatto
  - 4 = Poco soddisfatto
  - 5 = Per nulla soddisfatto
- **Codici distinti di uscita**:
  - 98 = Non so
  - 99 = Rifiuto
"""
        metadata, questions = parse_questionnaire(sample)
        q1 = questions[0]
        instructions = _build_administration_instructions(q1)
        inst_str = " ".join(instructions)
        self.assertNotIn("ROTAZIONE CASUALE", inst_str)

    def test_cli_case_insensitive_format(self):
        """Verifica che il parametro CLI --format accetti valori sia minuscoli che maiuscoli (es. MD, BOTH)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_q = Path(tmpdir) / "test_case_q.md"
            temp_q.write_text(self.structured_md_sample, encoding="utf-8")
            out_file = Path(tmpdir) / "out.md"

            cmd = [
                sys.executable,
                str(self.script_path),
                str(temp_q),
                "--format",
                "MD",
                "--output",
                str(out_file),
            ]
            res = subprocess.run(cmd, capture_output=True, text=True)
            self.assertEqual(res.returncode, 0, f"CLI with uppercase format failed: {res.stderr}")
            self.assertTrue(out_file.exists())


if __name__ == "__main__":
    unittest.main()
