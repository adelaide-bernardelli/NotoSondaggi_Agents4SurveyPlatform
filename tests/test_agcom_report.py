#!/usr/bin/env python3
"""
test_agcom_report.py — Suite di test unitari per la Scheda Informativa AGCOM (Delibera 256/10/CSP)

Verifica:
1. Completezza del template ufficiale `templates/agcom_template.md`.
2. Accuratezza del calcolo statistico del margine d'errore teorico (Gauss, confidenza 95%, finite population correction).
3. Estrazione dei metadati e trascrizione fedele delle domande da casi reali/demo (demo_run_biblioteca).
4. Presenza obbligatoria della marcatura `[DA VERIFICARE SUL CAMPO]` sui parametri ex-post.
5. Inclusione e codifica rigorosa dei codici standard di non risposta (97, 98, 99).
6. Robustezza ed edge case (fallback con solo questionnaire.md, questionario strutturato, assenza di brief).
7. Esecuzione da interfaccia a riga di comando (CLI) e flag di validazione (--check-only).
8. Validatore di conformità `validate_agcom_file` e `validate_agcom_report`.
"""

import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

# Aggiunge la radice del repository al path per gli import
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts.generate_agcom_report import (
    DELIBERA_REF,
    SITO_DEPOSITO,
    SOGGETTO_REALIZZATORE,
    DA_VERIFICARE_CAMPO,
    calculate_margin_of_error,
    format_agcom_report,
    generate_agcom_report,
    parse_case_metadata,
    parse_questions_from_survey,
    validate_agcom_report,
)
from scripts.validate_runs import validate_agcom_file, validate_case


class TestAGCOMTemplate(unittest.TestCase):
    """Verifica l'integrità e la conformità di templates/agcom_template.md."""

    def setUp(self):
        self.template_path = ROOT_DIR / "templates" / "agcom_template.md"

    def test_template_exists(self):
        self.assertTrue(self.template_path.exists(), "templates/agcom_template.md non trovato")

    def test_template_required_sections(self):
        content = self.template_path.read_text(encoding="utf-8")
        required_headers = [
            "## 1. Dati Identificativi e di Diffusione",
            "## 2. Popolazione di Riferimento e Disegno Campionario",
            "## 3. Metodo di Rilevazione e Somministrazione",
            "## 4. Consistenza Numerica del Campione e Indicatori di Contatto (Fieldwork)",
            "## 5. Ponderazione Statistica e Margine d'Errore Teorico",
            "## 6. Testo Integrale delle Domande e Opzioni di Risposta",
            "## 7. Archivio e Deposito Istituzionale",
        ]
        for header in required_headers:
            self.assertIn(header, content, f"Sezione obbligatoria mancante nel template: {header}")

    def test_template_mandatory_fields(self):
        content = self.template_path.read_text(encoding="utf-8")
        mandatory_terms = [
            DELIBERA_REF,
            SOGGETTO_REALIZZATORE,
            "Committente",
            "Acquirente",
            "Popolazione di riferimento",
            "Estensione territoriale",
            "Metodo di campionamento",
            "Metodo di raccolta dei dati",
            DA_VERIFICARE_CAMPO,
            "Margine d'errore",
            "95%",
            "97",
            "98",
            "99",
            SITO_DEPOSITO,
        ]
        for term in mandatory_terms:
            self.assertIn(term, content, f"Termine obbligatorio mancante nel template: '{term}'")

    def test_template_validation_clean(self):
        errs = validate_agcom_file(self.template_path)
        self.assertEqual(errs, [], f"Il template ufficiale presenta errori di validazione: {errs}")


class TestMarginOfErrorCalculation(unittest.TestCase):
    """Verifica il calcolo matematico del margine d'errore teorico al 95% di confidenza."""

    def test_standard_sample_sizes(self):
        # n = 800: e = 1.96 * 0.5 / sqrt(800) = 0.034648... -> 3.46%
        moe_800 = calculate_margin_of_error(800)
        self.assertEqual(moe_800, 3.46)

        # n = 1000: e = 1.96 * 0.5 / sqrt(1000) = 0.030989... -> 3.10%
        moe_1000 = calculate_margin_of_error(1000)
        self.assertEqual(moe_1000, 3.10)

        # n = 1500: e = 1.96 * 0.5 / sqrt(1500) = 0.025303... -> 2.53%
        moe_1500 = calculate_margin_of_error(1500)
        self.assertEqual(moe_1500, 2.53)

        # n = 400: e = 1.96 * 0.5 / sqrt(400) = 0.049000... -> 4.90%
        moe_400 = calculate_margin_of_error(400)
        self.assertEqual(moe_400, 4.90)

        # n = 2000: e = 1.96 * 0.5 / sqrt(2000) = 0.021913... -> 2.19%
        moe_2000 = calculate_margin_of_error(2000)
        self.assertEqual(moe_2000, 2.19)

    def test_confidence_levels(self):
        # 90% (z = 1.645): e = 1.645 * 0.5 / sqrt(1000) = 0.026010... -> 2.60%
        moe_90 = calculate_margin_of_error(1000, confidence=0.90)
        self.assertEqual(moe_90, 2.60)

        # 99% (z = 2.576): e = 2.576 * 0.5 / sqrt(1000) = 0.040730... -> 4.07%
        moe_99 = calculate_margin_of_error(1000, confidence=0.99)
        self.assertEqual(moe_99, 4.07)

    def test_finite_population_correction(self):
        # N = 1000, n = 800: fpc = sqrt(200 / 999) = 0.4474...
        # Senza fpc: 3.46%, con fpc: 3.46 * 0.4474 = 1.55%
        moe_fpc = calculate_margin_of_error(800, population_size=1000)
        self.assertEqual(moe_fpc, 1.55)
        self.assertLess(moe_fpc, 3.46)

    def test_invalid_sample_size(self):
        with self.assertRaises(ValueError):
            calculate_margin_of_error(0)
        with self.assertRaises(ValueError):
            calculate_margin_of_error(-500)


class TestAGCOMReportGenerationDemoBiblioteca(unittest.TestCase):
    """Verifica l'estrazione e generazione della Scheda AGCOM sul caso demo_run_biblioteca."""

    @classmethod
    def setUpClass(cls):
        cls.demo_dir = ROOT_DIR / "examples" / "demo_run_biblioteca"
        cls.out_file = cls.demo_dir / "scheda_agcom.md"
        # Esegui la generazione
        generate_agcom_report(case_dir=cls.demo_dir, output_path=cls.out_file)
        cls.content = cls.out_file.read_text(encoding="utf-8")

    def test_file_generated(self):
        self.assertTrue(self.out_file.exists(), "examples/demo_run_biblioteca/scheda_agcom.md non generato")
        self.assertGreater(len(self.content), 1000)

    def test_metadata_extracted(self):
        self.assertIn("demo-biblioteca", self.content)
        self.assertIn(SOGGETTO_REALIZZATORE, self.content)
        self.assertIn("n = 800", self.content)
        self.assertIn("± 3.46%", self.content)
        self.assertIn("CATI / CAWI", self.content)
        self.assertIn("Cittadini maggiorenni residenti", self.content)
        self.assertIn("Comunale", self.content)

    def test_questions_faithfully_included(self):
        # Q1, Q2a, Q2b
        self.assertIn("### Q1", self.content)
        self.assertIn("Come valuta complessivamente i servizi offerti dalla biblioteca comunale?", self.content)
        self.assertIn("[LEGGERE LE OPZIONI — RISPOSTA SINGOLA]", self.content)
        self.assertIn("Molto soddisfacente", self.content)
        self.assertIn("Abbastanza soddisfacente", self.content)
        self.assertIn("Poco soddisfacente", self.content)
        self.assertIn("Per nulla soddisfacente", self.content)

        self.assertIn("### Q2a", self.content)
        self.assertIn("Quanto è soddisfatto degli orari di apertura della biblioteca?", self.content)

        self.assertIn("### Q2b", self.content)
        self.assertIn("Quanto è soddisfatto della disponibilità e scelta dei libri?", self.content)

    def test_standard_exit_codes_presence(self):
        # Codici 97, 98, 99
        self.assertIn("`97`", self.content)
        self.assertIn("`98`", self.content)
        self.assertIn("`99`", self.content)
        self.assertIn("Non so", self.content)
        self.assertIn("Preferisco non rispondere", self.content)

    def test_unverified_fieldwork_placeholders(self):
        # Verifica la presenza sistematica di [DA VERIFICARE SUL CAMPO]
        self.assertIn(DA_VERIFICARE_CAMPO, self.content)
        # Deve comparire nelle tabelle dei contatti e nei tassi di risposta
        self.assertIn(f"Contatti totali tentati** | $T$ | {DA_VERIFICARE_CAMPO}", self.content)
        self.assertIn(f"Rifiuti all'intervista (*unit nonresponse*)** | $R$ | {DA_VERIFICARE_CAMPO}", self.content)
        self.assertIn(f"Tasso di Risposta ($RR$)", self.content)

    def test_institutional_repository(self):
        self.assertIn(SITO_DEPOSITO, self.content)
        self.assertIn("Presidenza del Consiglio dei Ministri", self.content)

    def test_validation_passes(self):
        issues = validate_agcom_report(self.content)
        self.assertEqual(issues, [], f"La Scheda AGCOM di demo-biblioteca non è conforme: {issues}")

        errs_linter = validate_agcom_file(self.out_file)
        self.assertEqual(errs_linter, [], f"Il linter rileva errori: {errs_linter}")

    def test_case_directory_validates_with_agcom(self):
        # Verifica che scripts/validate_runs.py validi l'intero caso inclusa la scheda AGCOM
        ok = validate_case(self.demo_dir)
        self.assertTrue(ok, "validate_case ha fallito sul caso con scheda AGCOM")


class TestAGCOMReportEdgeCases(unittest.TestCase):
    """Verifica comportamenti su formati alternativi, casi parziali ed errori."""

    def test_structured_questionnaire_format(self):
        """Verifica estrazione corretta da questionario strutturato a sezioni (#### Q01 — Costrutto)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            case_dir = Path(tmpdir) / "structured_case"
            case_dir.mkdir()

            (case_dir / "brief.md").write_text(
                "# Brief\n- ID caso: struct-test\n- Obiettivo conoscitivo principale: Test strutturato\n"
                "- Popolazione di riferimento: Cittadini\n- Area geografica: Regionale\n"
                "- Modalita di somministrazione: CATI\n- Numerosita campionaria e quote: n = 1000 interviste\n",
                encoding="utf-8",
            )
            (case_dir / "final.md").write_text(
                "# Questionario Strutturato\n## 4. Testo Definitivo del Questionario Candidato\n"
                "### Sezione A — Generale\n"
                "#### Q01 — Valutazione\n"
                "- **Testo per il rispondente**: Come valuta la gestione?\n"
                "- **Istruzioni di regia e somministrazione**: [NON LEGGERE — RISPOSTA SPONTANEA]\n"
                "- **Opzioni e codici di risposta**:\n"
                "  1. Positiva\n  2. Negativa\n"
                "- **Codici distinti di uscita**:\n"
                "  - `97` = Non applicabile\n  - `98` = Non so\n  - `99` = Preferisco non rispondere\n",
                encoding="utf-8",
            )

            out_file, content, issues = generate_agcom_report(case_dir)
            self.assertEqual(issues, [])
            self.assertIn("struct-test", content)
            self.assertIn("± 3.10%", content)
            self.assertIn("Come valuta la gestione?", content)
            self.assertIn("[NON LEGGERE — RISPOSTA SPONTANEA]", content)
            self.assertIn("1. Positiva", content)
            self.assertIn("`97`", content)
            self.assertIn("`98`", content)
            self.assertIn("`99`", content)

    def test_fallback_to_questionnaire_md_when_no_final(self):
        """Verifica fallback su questionnaire.md se final.md non è presente."""
        with tempfile.TemporaryDirectory() as tmpdir:
            case_dir = Path(tmpdir) / "draft_case"
            case_dir.mkdir()

            (case_dir / "questionnaire.md").write_text(
                "# Questionario Bozza\n## 3. Domande\n"
                "Q1. Domanda in bozza?\n- **Istruzioni di regia e somministrazione**: [SPONTANEA]\n"
                "1. Sì\n2. No\n98. Non so\n99. Rifiuta\n",
                encoding="utf-8",
            )

            out_file, content, issues = generate_agcom_report(case_dir)
            self.assertEqual(issues, [])
            self.assertIn("Domanda in bozza?", content)
            self.assertIn("1. Sì", content)

    def test_explicit_overrides(self):
        """Verifica il funzionamento degli override espliciti (client, sample size, media, ecc.)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            case_dir = Path(tmpdir) / "override_case"
            case_dir.mkdir()

            (case_dir / "final.md").write_text(
                "# Questionario\n### Domande\nQ1. Testo?\n1. A\n2. B\n98. Non so\n99. Rifiuto\n",
                encoding="utf-8",
            )

            out_file, content, issues = generate_agcom_report(
                case_dir=case_dir,
                sample_size=1500,
                client="Gruppo Editoriale Espresso",
                buyer="La Repubblica",
                media="Quotidiano La Repubblica e sito web",
                pub_date="15/11/2026",
                fieldwork_date="10-12/11/2026",
                title="Sondaggio Nazionale Politico-Elettorale",
            )
            self.assertEqual(issues, [])
            self.assertIn("n = 1500", content)
            self.assertIn("± 2.53%", content)
            self.assertIn("Gruppo Editoriale Espresso", content)
            self.assertIn("La Repubblica", content)
            self.assertIn("Quotidiano La Repubblica e sito web", content)
            self.assertIn("15/11/2026", content)
            self.assertIn("10-12/11/2026", content)
            self.assertIn("Sondaggio Nazionale Politico-Elettorale", content)

    def test_missing_case_dir_error(self):
        with self.assertRaises(FileNotFoundError):
            generate_agcom_report("percorso_inesistente_12345")

    def test_missing_questionnaire_file_error(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            case_dir = Path(tmpdir) / "empty_case"
            case_dir.mkdir()
            with self.assertRaises(FileNotFoundError):
                generate_agcom_report(case_dir)

    def test_empty_questionnaire_error(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            case_dir = Path(tmpdir) / "no_q_case"
            case_dir.mkdir()
            (case_dir / "final.md").write_text("# Questionario vuoto\nNessuna domanda presente.\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                generate_agcom_report(case_dir)


class TestAGCOMReportValidator(unittest.TestCase):
    """Verifica le regole di validazione formale e contenutistica."""

    def test_validator_detects_empty(self):
        issues = validate_agcom_report("")
        self.assertTrue(any("vuoto" in e for e in issues))

    def test_validator_detects_missing_delibera(self):
        valid = (ROOT_DIR / "templates" / "agcom_template.md").read_text(encoding="utf-8")
        corrupted = valid.replace("256/10/CSP", "999/99/XXX")
        issues = validate_agcom_report(corrupted)
        self.assertTrue(any("256/10/CSP" in e for e in issues))

    def test_validator_detects_missing_company(self):
        valid = (ROOT_DIR / "templates" / "agcom_template.md").read_text(encoding="utf-8")
        corrupted = valid.replace("Noto Sondaggi", "Altro Istituto")
        issues = validate_agcom_report(corrupted)
        self.assertTrue(any("Noto Sondaggi" in e for e in issues))

    def test_validator_detects_missing_exit_code(self):
        valid = (ROOT_DIR / "templates" / "agcom_template.md").read_text(encoding="utf-8")
        corrupted = valid.replace("97", "00")
        issues = validate_agcom_report(corrupted)
        self.assertTrue(any("97" in e for e in issues))

    def test_validator_detects_missing_unverified_tag(self):
        valid = (ROOT_DIR / "templates" / "agcom_template.md").read_text(encoding="utf-8")
        corrupted = valid.replace(DA_VERIFICARE_CAMPO, "Valore Definitivo")
        issues = validate_agcom_report(corrupted)
        self.assertTrue(any(DA_VERIFICARE_CAMPO in e for e in issues))

    def test_validate_agcom_file_str_path(self):
        tpl_path = ROOT_DIR / "templates" / "agcom_template.md"
        errs = validate_agcom_file(str(tpl_path))
        self.assertEqual(errs, [])


class TestAGCOMCLI(unittest.TestCase):
    """Verifica il comportamento del comando scripts/generate_agcom_report.py da riga di comando."""

    def test_cli_execution_demo(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            out_file = Path(tmpdir) / "cli_scheda.md"
            cmd = [
                sys.executable,
                str(ROOT_DIR / "scripts" / "generate_agcom_report.py"),
                str(ROOT_DIR / "examples" / "demo_run_biblioteca"),
                "--output",
                str(out_file),
            ]
            res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(res.returncode, 0, f"CLI fallita con stdout: {res.stdout}\nstderr: {res.stderr}")
            self.assertTrue(out_file.exists())
            self.assertIn("Scheda AGCOM generata con successo", res.stdout)
            self.assertIn("PASS", res.stdout)

    def test_cli_check_only_flag(self):
        demo_scheda = ROOT_DIR / "examples" / "demo_run_biblioteca" / "scheda_agcom.md"
    def test_cli_execution_with_file_path(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            out_file = Path(tmpdir) / "cli_scheda_from_file.md"
            final_file = ROOT_DIR / "examples" / "demo_run_biblioteca" / "final.md"
            cmd = [
                sys.executable,
                str(ROOT_DIR / "scripts" / "generate_agcom_report.py"),
                str(final_file),
                "--output",
                str(out_file),
            ]
            res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(res.returncode, 0, f"Invocazione con file path fallita: {res.stdout}\n{res.stderr}")
            self.assertTrue(out_file.exists())
            self.assertIn("Scheda AGCOM generata con successo", res.stdout)


class TestAGCOMAdvancedFeatures(unittest.TestCase):
    """Verifica le funzionalità avanzate: opzioni '=', batterie, notazione italiana, fallback metadata ed edge cases."""

    def test_options_with_equal_sign_and_custom_exit_labels(self):
        """Verifica estrazione opzioni con '=' e personalizzazione etichette codici 97, 98, 99."""
        survey_text = """
### Domande
#### Q01 — Valutazione Servizio
- **Testo per il rispondente**: Come valuta il servizio di anagrafe?
- **Istruzioni di regia e somministrazione**: [RISPOSTA SINGOLA]
- **Opzioni e codici di risposta**:
  - 1 = Molto efficiente
  - 2 = Abbastanza efficiente
  - 3 = Poco efficiente
  - 4 = Per nulla efficiente
- **Codici distinti di uscita**:
  - `97` = Fuori target (non residente)
  - `98` = Non ricorda / Nessuna opinione
  - `99` = Rifiuta di rispondere
"""
        qs = parse_questions_from_survey(survey_text)
        self.assertEqual(len(qs), 1)
        q = qs[0]
        self.assertEqual(len(q.options), 4)
        self.assertEqual(q.options[0].code, "1")
        self.assertEqual(q.options[0].label, "Molto efficiente")

        self.assertEqual(len(q.exit_codes), 3)
        self.assertEqual(q.exit_codes[0].code, "97")
        self.assertEqual(q.exit_codes[0].label, "Fuori target (non residente)")
        self.assertEqual(q.exit_codes[1].code, "98")
        self.assertEqual(q.exit_codes[1].label, "Non ricorda / Nessuna opinione")
        self.assertEqual(q.exit_codes[2].code, "99")
        self.assertEqual(q.exit_codes[2].label, "Rifiuta di rispondere")

    def test_inline_options_and_inline_exit_codes(self):
        """Verifica parsing di opzioni inline su singola riga separate da virgola."""
        survey_text = """
### Domande
#### Q02 — Uso del Servizio
- **Testo per il rispondente**: Ha utilizzato il servizio nell'ultimo anno?
- **Opzioni e codici di risposta**: 1. Sì, 2. No
- **Codici distinti di uscita**: 97 = Non applicabile, 98 = Non so, 99 = Rifiuto
"""
        qs = parse_questions_from_survey(survey_text)
        self.assertEqual(len(qs), 1)
        q = qs[0]
        self.assertEqual(len(q.options), 2)
        self.assertEqual(q.options[0].code, "1")
        self.assertEqual(q.options[0].label, "Sì")
        self.assertEqual(q.options[1].code, "2")
        self.assertEqual(q.options[1].label, "No")
        self.assertEqual(len(q.exit_codes), 3)
        self.assertEqual(q.exit_codes[0].code, "97")
        self.assertEqual(q.exit_codes[1].code, "98")
        self.assertEqual(q.exit_codes[2].code, "99")

    def test_battery_matrix_items_subquestions(self):
        """Verifica estrazione e formattazione di batterie a matrice con item (SQ01, SQ02)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            case_dir = Path(tmpdir) / "battery_case"
            case_dir.mkdir()
            (case_dir / "final.md").write_text("""# Questionario Batteria
### Domande
#### Q03 — Valutazione Aspetti
- **Testo per il rispondente**: Quanto è soddisfatto dei seguenti aspetti della città?
- **Item della batteria**:
  - SQ01 = Raccolta differenziata
  - SQ02 = Manutenzione stradale
  - SQ03 = Aree verdi e parchi
- **Opzioni e codici di risposta**:
  1. Molto
  2. Poco
- **Codici distinti di uscita**:
  - 98 = Non so
  - 99 = Rifiuto
""", encoding="utf-8")

            out_file, content, issues = generate_agcom_report(case_dir)
            self.assertEqual(issues, [])
            self.assertIn("Item / Sotto-quesiti valutati", content)
            self.assertIn("SQ01", content)
            self.assertIn("Raccolta differenziata", content)
            self.assertIn("SQ02", content)
            self.assertIn("Manutenzione stradale", content)
            self.assertIn("SQ03", content)
            self.assertIn("Aree verdi e parchi", content)

    def test_italian_thousands_sample_size_parsing(self):
        """Verifica la corretta interpretazione di 'n = 1.000' e 'n = 1 500' senza troncamenti."""
        with tempfile.TemporaryDirectory() as tmpdir:
            case_dir = Path(tmpdir) / "italian_num_case"
            case_dir.mkdir()
            (case_dir / "brief.md").write_text(
                "# Brief\n- ID caso: it-num\n- Numerosita campionaria e quote: n = 1.000 interviste complete\n",
                encoding="utf-8",
            )
            (case_dir / "final.md").write_text(
                "# Questionario\n### Domande\nQ1. Test?\n1. A\n2. B\n",
                encoding="utf-8",
            )
            meta = parse_case_metadata(case_dir)
            self.assertEqual(meta.planned_sample_size, 1000)
            self.assertEqual(meta.margin_of_error_pct, 3.10)

    def test_metadata_extraction_from_final_without_brief(self):
        """Verifica estrazione completa dei metadati da final.md in assenza di brief.md."""
        with tempfile.TemporaryDirectory() as tmpdir:
            case_dir = Path(tmpdir) / "no_brief_case"
            case_dir.mkdir()
            (case_dir / "final.md").write_text("""# Questionario Consolidato
## 1. Metadati di Consolidamento
- ID Caso: rev-2026
- Committente: Comune di Milano
- Modalita di somministrazione: CAWI via web panel
- Popolazione di riferimento e campione previsto: Residenti maggiorenni a Milano (n = 1200)
- Durata complessiva stimata: 12 minuti
### Domande
Q1. Test?\n1. A\n2. B\n""", encoding="utf-8")

            meta = parse_case_metadata(case_dir)
            self.assertEqual(meta.case_id, "rev-2026")
            self.assertEqual(meta.client, "Comune di Milano")
            self.assertEqual(meta.planned_sample_size, 1200)
            self.assertEqual(meta.data_collection_method, "CAWI via web panel")
            self.assertEqual(meta.interview_duration, "12 minuti")
            self.assertEqual(meta.margin_of_error_pct, 2.83)

    def test_census_population_zero_margin_of_error(self):
        """Verifica che un censimento completo (N == n) produca margine d'errore 0.0%."""
        moe_census = calculate_margin_of_error(800, population_size=800)
        self.assertEqual(moe_census, 0.0)

    def test_invalid_population_and_confidence_bounds(self):
        """Verifica la gestione degli errori per parametri statistici fuori range."""
        with self.assertRaises(ValueError):
            calculate_margin_of_error(800, population_size=500)
        with self.assertRaises(ValueError):
            calculate_margin_of_error(800, confidence=1.5)
        with self.assertRaises(ValueError):
            calculate_margin_of_error(800, p=1.0)
        with self.assertRaises(ValueError):
            calculate_margin_of_error(800, p=0.0)

    def test_heading_with_standalone_number(self):
        """Verifica che un'intestazione con numero autonomo (### 1. Titolo) sia riconosciuta come quesito."""
        survey_text = """
### Domande
### 1. Come valuta l'operato della giunta?
- **Istruzioni di regia e somministrazione**: [LEGGERE LE OPZIONI]
1. Positivo
2. Negativo
"""
        qs = parse_questions_from_survey(survey_text)
        self.assertEqual(len(qs), 1)
        self.assertEqual(qs[0].id, "Q1")
        self.assertIn("Come valuta l'operato della giunta?", qs[0].text)

    def test_unnumbered_bullet_options(self):
        """Verifica l'auto-assegnazione ordinata di codici a punti elenco non numerati."""
        survey_text = """
### Domande
#### Q01 — Preferenze
- **Testo per il rispondente**: Quale mezzo usa preferibilmente?
- **Opzioni e codici di risposta**:
  - Metropolitana
  - Autobus
  - Bicicletta
"""
        qs = parse_questions_from_survey(survey_text)
        self.assertEqual(len(qs), 1)
        self.assertEqual(len(qs[0].options), 3)
        self.assertEqual(qs[0].options[0].code, "1")
        self.assertEqual(qs[0].options[0].label, "Metropolitana")
        self.assertEqual(qs[0].options[1].code, "2")
        self.assertEqual(qs[0].options[1].label, "Autobus")
        self.assertEqual(qs[0].options[2].code, "3")
        self.assertEqual(qs[0].options[2].label, "Bicicletta")


if __name__ == "__main__":
    unittest.main()

