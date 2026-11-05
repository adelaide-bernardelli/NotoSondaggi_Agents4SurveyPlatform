import json
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

from scripts.extract_survey_knowledge import (
    ExtractedSurvey,
    extract_survey_knowledge,
    generate_json_output,
    generate_markdown_output,
    harmonize_missing_codes,
    make_construct,
    parse_metadata_from_text,
    parse_survey_text,
    read_input_file,
)
from scripts.validate_runs import validate_extracted_survey_file


class TestKnowledgeDemographicsStandard(unittest.TestCase):
    """Verifica la validità strutturale e metodologica di knowledge/demographics_standard.json."""

    def setUp(self):
        self.json_path = ROOT_DIR / "knowledge" / "demographics_standard.json"

    def test_demographics_standard_json_exists_and_valid(self):
        """Verifica che il file demographics_standard.json esista e sia un JSON valido."""
        self.assertTrue(self.json_path.exists(), "knowledge/demographics_standard.json non esiste")
        content = self.json_path.read_text(encoding="utf-8")
        data = json.loads(content)
        self.assertIsInstance(data, dict)

        # Verifica metadati di vertice
        self.assertIn("metadata", data)
        meta = data["metadata"]
        self.assertEqual(meta["standard_id"], "DEM_STANDARD_ISTAT_EUROSTAT")
        self.assertIn("Istat", meta["source_authority"])
        self.assertIn("default_missing_codes", meta)

        missing = meta["default_missing_codes"]
        self.assertIn("97", missing)
        self.assertIn("98", missing)
        self.assertIn("99", missing)

    def test_demographics_standard_required_variables_presence(self):
        """Verifica che siano presenti tutte le 7 variabili socio-demografiche canoniche."""
        data = json.loads(self.json_path.read_text(encoding="utf-8"))
        self.assertIn("variables", data)
        variables = data["variables"]
        self.assertIsInstance(variables, list)

        var_ids = {v["id_item"] for v in variables}
        expected_ids = {
            "DEM_GENERE",
            "DEM_ETA_CLASSI",
            "DEM_ETA_CONTINUA",
            "DEM_TITOLO_STUDIO",
            "DEM_CONDIZIONE_PROFESSIONALE",
            "DEM_RIPARTIZIONE_GEO",
            "DEM_AMPIEZZA_COMUNE",
        }
        missing_ids = expected_ids - var_ids
        self.assertEqual(missing_ids, set(), f"Variabili demografiche mancanti: {missing_ids}")

    def test_demographics_standard_each_variable_has_required_fields_and_exit_codes(self):
        """Verifica che ogni variabile demografica contenga tutti i campi obbligatori e i codici 97, 98, 99."""
        data = json.loads(self.json_path.read_text(encoding="utf-8"))
        for v in data["variables"]:
            item_id = v.get("id_item", "UNKNOWN")
            self.assertTrue(v.get("construct"), f"{item_id}: costrutto mancante o vuoto")
            self.assertTrue(v.get("question_text"), f"{item_id}: testo domanda mancante")
            self.assertTrue(v.get("question_type"), f"{item_id}: tipo domanda mancante")
            self.assertTrue(v.get("scale_type"), f"{item_id}: tipo scala mancante")
            self.assertIn("missing_codes", v, f"{item_id}: missing_codes mancante")

            missing_codes_map = {m["code"]: m["label"] for m in v["missing_codes"]}
            self.assertIn("97", missing_codes_map, f"{item_id}: codice 97 mancante")
            self.assertIn("98", missing_codes_map, f"{item_id}: codice 98 mancante")
            self.assertIn("99", missing_codes_map, f"{item_id}: codice 99 mancante")

            # Verifica etichette
            self.assertIn("Non applicabile", missing_codes_map["97"])
            self.assertTrue(any(kw in missing_codes_map["98"].lower() for kw in ["non so", "non ricorda"]))
            self.assertTrue(
                any(kw in missing_codes_map["99"].lower() for kw in ["preferisco non rispondere", "rifiut"])
            )

    def test_demographics_age_classes_and_continuous(self):
        """Verifica la coerenza della classe di età a 6 passi Istat e dell'età continua."""
        data = json.loads(self.json_path.read_text(encoding="utf-8"))
        variables_by_id = {v["id_item"]: v for v in data["variables"]}

        # 1. DEM_ETA_CLASSI: 6 classi Istat
        eta_classi = variables_by_id["DEM_ETA_CLASSI"]
        options = {opt["code"]: opt["label"] for opt in eta_classi["response_options"]}
        self.assertEqual(len(options), 6, "DEM_ETA_CLASSI deve contenere esattamente 6 classi Istat")
        self.assertIn("18-24", options["1"])
        self.assertIn("25-34", options["2"])
        self.assertIn("35-44", options["3"])
        self.assertIn("45-54", options["4"])
        self.assertIn("55-64", options["5"])
        self.assertIn("65", options["6"])

        # Verifica schemi di aggregazione (4 classi e 3 classi)
        self.assertIn("aggregations", eta_classi)
        self.assertIn("4_classi", eta_classi["aggregations"])
        self.assertIn("3_classi", eta_classi["aggregations"])

        # 2. DEM_ETA_CONTINUA: tipo numerico
        eta_cont = variables_by_id["DEM_ETA_CONTINUA"]
        self.assertEqual(eta_cont["question_type"], "numeric")
        self.assertEqual(eta_cont["scale_type"], "ratio")
        self.assertIn("validation_rules", eta_cont)
        self.assertEqual(eta_cont["validation_rules"]["min_value"], 1900)

    def test_demographics_education_and_employment(self):
        """Verifica i livelli di istruzione Istat e le condizioni occupazionali."""
        data = json.loads(self.json_path.read_text(encoding="utf-8"))
        variables_by_id = {v["id_item"]: v for v in data["variables"]}

        # Titolo di studio
        edu = variables_by_id["DEM_TITOLO_STUDIO"]
        edu_opts = [opt["label"].lower() for opt in edu["response_options"]]
        self.assertTrue(any("elementare" in o for o in edu_opts))
        self.assertTrue(any("media inferiore" in o for o in edu_opts))
        self.assertTrue(any("maturit" in o or "superiore" in o for o in edu_opts))
        self.assertTrue(any("laurea" in o for o in edu_opts))
        self.assertIn("aggregations", edu)
        self.assertIn("3_livelli", edu["aggregations"])

        # Condizione professionale
        occ = variables_by_id["DEM_CONDIZIONE_PROFESSIONALE"]
        occ_opts = [opt["label"].lower() for opt in occ["response_options"]]
        self.assertTrue(any("imprenditore" in o or "libero professionista" in o for o in occ_opts))
        self.assertTrue(any("impiegato" in o for o in occ_opts))
        self.assertTrue(any("operaio" in o for o in occ_opts))
        self.assertTrue(any("pensionato" in o for o in occ_opts))
        self.assertTrue(any("studente" in o for o in occ_opts))
        self.assertTrue(any("disoccupato" in o for o in occ_opts))

    def test_demographics_nuts1_geography_and_municipality_size(self):
        """Verifica le 5 ripartizioni NUTS-1 e le classi di ampiezza comune."""
        data = json.loads(self.json_path.read_text(encoding="utf-8"))
        variables_by_id = {v["id_item"]: v for v in data["variables"]}

        # NUTS-1: Nord-Ovest, Nord-Est, Centro, Sud, Isole
        geo = variables_by_id["DEM_RIPARTIZIONE_GEO"]
        geo_opts = {opt["code"]: opt["label"] for opt in geo["response_options"]}
        self.assertEqual(len(geo_opts), 5)
        self.assertIn("Nord-Ovest", geo_opts["1"])
        self.assertIn("Nord-Est", geo_opts["2"])
        self.assertIn("Centro", geo_opts["3"])
        self.assertIn("Sud", geo_opts["4"])
        self.assertIn("Isole", geo_opts["5"])

        # Ampiezza comune
        amp = variables_by_id["DEM_AMPIEZZA_COMUNE"]
        amp_opts = [opt["label"].lower() for opt in amp["response_options"]]
        self.assertEqual(len(amp_opts), 5)
        self.assertTrue(any("fino a 5.000" in o for o in amp_opts))
        self.assertTrue(any("oltre 100.000" in o for o in amp_opts))


class TestKnowledgePoliticalBatteriesCore(unittest.TestCase):
    """Verifica la validità strutturale e metodologica di knowledge/political_batteries_core.json."""

    def setUp(self):
        self.json_path = ROOT_DIR / "knowledge" / "political_batteries_core.json"

    def test_political_batteries_json_exists_and_valid(self):
        """Verifica che political_batteries_core.json esista e sia valido."""
        self.assertTrue(self.json_path.exists(), "knowledge/political_batteries_core.json non esiste")
        content = self.json_path.read_text(encoding="utf-8")
        data = json.loads(content)
        self.assertIsInstance(data, dict)

        self.assertIn("metadata", data)
        meta = data["metadata"]
        self.assertEqual(meta["collection_id"], "POL_BATTERIES_CORE_NOTO")
        self.assertIn("AGCOM", meta["source_authority"])
        self.assertIn("default_missing_codes", meta)

    def test_political_batteries_presence(self):
        """Verifica la presenza di tutte le 7 batterie politico-elettorali essenziali."""
        data = json.loads(self.json_path.read_text(encoding="utf-8"))
        self.assertIn("batteries", data)
        batteries = data["batteries"]
        self.assertIsInstance(batteries, list)

        bat_ids = {b["id_battery"] for b in batteries}
        expected_ids = {
            "POL_FIDUCIA_PREMIER",
            "POL_BATTERIA_LEADER",
            "POL_BATTERIA_ISTITUZIONI",
            "POL_GIUDIZIO_GOVERNO",
            "POL_AUTOCOLLOCAZIONE_SINISTRA_DESTRA",
            "POL_INTENZIONE_VOTO_POLITICHE",
            "POL_CLIMA_OPINIONE_DIREZIONE_PAESE",
            "POL_PROBLEMI_PRIORITARI",
        }
        missing_ids = expected_ids - bat_ids
        self.assertEqual(missing_ids, set(), f"Batterie politiche mancanti: {missing_ids}")

    def test_political_batteries_mandatory_fields_and_exit_codes(self):
        """Verifica campi obbligatori e codici standard di uscita per ogni batteria politica."""
        data = json.loads(self.json_path.read_text(encoding="utf-8"))
        for b in data["batteries"]:
            b_id = b.get("id_battery", "UNKNOWN")
            self.assertTrue(b.get("construct"), f"{b_id}: costrutto mancante")
            self.assertTrue(b.get("question_text"), f"{b_id}: testo domanda mancante")
            self.assertTrue(b.get("question_type"), f"{b_id}: tipo domanda mancante")
            self.assertTrue(b.get("scale_type"), f"{b_id}: tipo scala mancante")
            self.assertTrue(b.get("temporal_tracking"), f"{b_id}: temporal_tracking deve essere True")

            missing_codes_map = {m["code"]: m["label"] for m in b["missing_codes"]}
            self.assertIn("97", missing_codes_map, f"{b_id}: codice 97 mancante")
            self.assertIn("98", missing_codes_map, f"{b_id}: codice 98 mancante")
            self.assertIn("99", missing_codes_map, f"{b_id}: codice 99 mancante")

    def test_premier_trust_and_leader_battery(self):
        """Verifica la conformità metodologica delle batterie di fiducia leader e premier."""
        data = json.loads(self.json_path.read_text(encoding="utf-8"))
        bat_by_id = {b["id_battery"]: b for b in data["batteries"]}

        # Fiducia Premier
        premier = bat_by_id["POL_FIDUCIA_PREMIER"]
        self.assertEqual(premier["scale_points"], 4)
        prem_labels = [opt["label"].lower() for opt in premier["response_options"]]
        self.assertIn("molta fiducia", prem_labels)
        self.assertIn("abbastanza fiducia", prem_labels)
        self.assertIn("poca fiducia", prem_labels)
        self.assertIn("nessuna fiducia", prem_labels)
        self.assertIn("alternative_numeric_scale", premier)
        self.assertEqual(premier["alternative_numeric_scale"]["scale_points"], 10)

        # Batteria Leader (Matrice con SQ)
        leaders = bat_by_id["POL_BATTERIA_LEADER"]
        self.assertEqual(leaders["question_type"], "matrix")
        self.assertIn("sub_items", leaders)
        self.assertGreaterEqual(len(leaders["sub_items"]), 5)
        sq_codes = [sq["code"] for sq in leaders["sub_items"]]
        self.assertIn("SQ01", sq_codes)
        self.assertIn("SQ02", sq_codes)
        self.assertIn("regia_notes", leaders)
        self.assertIn("Ruotare", leaders["regia_notes"])

    def test_institutions_trust_battery(self):
        """Verifica la batteria di fiducia nelle istituzioni (POL_BATTERIA_ISTITUZIONI)."""
        data = json.loads(self.json_path.read_text(encoding="utf-8"))
        bat_by_id = {b["id_battery"]: b for b in data["batteries"]}

        self.assertIn("POL_BATTERIA_ISTITUZIONI", bat_by_id)
        inst = bat_by_id["POL_BATTERIA_ISTITUZIONI"]
        self.assertEqual(inst["question_type"], "matrix")
        self.assertEqual(inst["scale_points"], 4)
        self.assertIn("sub_items", inst)
        self.assertGreaterEqual(len(inst["sub_items"]), 6)
        labels = [sq["label"].lower() for sq in inst["sub_items"]]
        self.assertTrue(any("presidente della repubblica" in l for l in labels))
        self.assertTrue(any("parlamento" in l for l in labels))
        self.assertTrue(any("governo" in l for l in labels))
        self.assertTrue(any("forze dell'ordine" in l for l in labels))
        self.assertTrue(any("unione europea" in l for l in labels))
        self.assertIn("regia_notes", inst)

    def test_vote_intentions_and_agcom_regulatory_compliance(self):
        """Verifica i requisiti normativi AGCOM (Delibera 256/10/CSP) su intenzioni di voto."""
        data = json.loads(self.json_path.read_text(encoding="utf-8"))
        bat_by_id = {b["id_battery"]: b for b in data["batteries"]}

        voto = bat_by_id["POL_INTENZIONE_VOTO_POLITICHE"]
        self.assertIn("regulatory_compliance", voto)
        self.assertIn("256/10/CSP", voto["regulatory_compliance"])

        # Deve comprendere sia liste politiche che le opzioni esplicite di astensione e scheda bianca
        opt_labels = [opt["label"].lower() for opt in voto["response_options"]]
        self.assertTrue(any("fratelli d'italia" in o for o in opt_labels))
        self.assertTrue(any("partito democratico" in o for o in opt_labels))
        self.assertTrue(any("scheda bianca" in o for o in opt_labels))
        self.assertTrue(any("astensione" in o or "non andrei a votare" in o for o in opt_labels))

        # I codici di uscita devono contemplare indecisi (98) e segreto del voto (99)
        missing_map = {m["code"]: m["label"].lower() for m in voto["missing_codes"]}
        self.assertTrue("indeciso" in missing_map["98"])
        self.assertTrue("segreto del voto" in missing_map["99"] or "preferisco non rispondere" in missing_map["99"])

    def test_left_right_and_issue_salience(self):
        """Verifica l'auto-collocazione sinistra-destra 1-10 e la batteria problemi prioritari."""
        data = json.loads(self.json_path.read_text(encoding="utf-8"))
        bat_by_id = {b["id_battery"]: b for b in data["batteries"]}

        # Sinistra-Destra
        lr = bat_by_id["POL_AUTOCOLLOCAZIONE_SINISTRA_DESTRA"]
        self.assertEqual(lr["scale_points"], 10)
        self.assertEqual(len(lr["response_options"]), 10)
        self.assertIn("aggregations", lr)
        self.assertIn("5_poli", lr["aggregations"])

        # Problemi prioritari
        issues = bat_by_id["POL_PROBLEMI_PRIORITARI"]
        self.assertEqual(issues["question_type"], "multiple_choice")
        self.assertEqual(issues["max_responses"], 2)
        issue_labels = [opt["label"].lower() for opt in issues["response_options"]]
        self.assertTrue(any("sanit" in o for o in issue_labels))
        self.assertTrue(any("inflazione" in o or "carovita" in o for o in issue_labels))
        self.assertTrue(any("lavoro" in o or "occupazione" in o for o in issue_labels))


class TestSurveyExtractorCLIAndAPI(unittest.TestCase):
    """Test unitari per la CLI e per le funzioni di extract_survey_knowledge.py."""

    def setUp(self):
        self.script_path = ROOT_DIR / "scripts" / "extract_survey_knowledge.py"
        self.demo_q_path = ROOT_DIR / "examples" / "questionario_demo.md"

    def test_cli_help(self):
        """Verifica che l'invocazione di --help ritorni esito 0 e mostri le opzioni."""
        cmd = [sys.executable, str(self.script_path), "--help"]
        res = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(res.returncode, 0)
        self.assertIn("extract_survey_knowledge.py", res.stdout)
        self.assertIn("--format", res.stdout)
        self.assertIn("--id-studio", res.stdout)

    def test_extract_markdown_to_markdown_output_validates_successfully(self):
        """Verifica che l'estrazione da Markdown produca un file conforme al validatore di artefatti."""
        with tempfile.TemporaryDirectory() as tmpdir:
            out_file = Path(tmpdir) / "extracted_survey.md"
            ok = extract_survey_knowledge(
                input_path=self.demo_q_path,
                output_path=out_file,
                output_format="md",
                id_studio="test-demo-biblioteca",
                committente="Comune di Test",
                target="Cittadini maggiorenni",
                anno="2024",
                modalita="CATI",
            )
            self.assertTrue(ok, "extract_survey_knowledge deve ritornare True")
            self.assertTrue(out_file.exists(), "Il file di output deve esistere")

            # Verifica di conformità mediante il linter validate_extracted_survey_file
            issues = validate_extracted_survey_file(out_file)
            self.assertEqual(issues, [], f"Il file estratto non supera il linter: {issues}")

            content = out_file.read_text(encoding="utf-8")
            self.assertIn("ID Studio / Nome Archivio: test-demo-biblioteca", content)
            self.assertIn("Committente originario: Comune di Test", content)
            self.assertIn("Popolazione di riferimento e Target: Cittadini maggiorenni", content)
            self.assertIn("Q01", content)
            self.assertIn("97 = Non applicabile", content)
            self.assertIn("98 = Non so", content)
            self.assertIn("99 = Preferisco non rispondere", content)

    def test_extract_markdown_to_json_output(self):
        """Verifica che l'output in formato JSON sia valido e strutturato correttamente."""
        with tempfile.TemporaryDirectory() as tmpdir:
            out_file = Path(tmpdir) / "extracted_survey.json"
            ok = extract_survey_knowledge(
                input_path=self.demo_q_path,
                output_path=out_file,
                output_format="json",
                id_studio="json-test-case",
                committente="Test Committente",
            )
            self.assertTrue(ok)
            self.assertTrue(out_file.exists())

            data = json.loads(out_file.read_text(encoding="utf-8"))
            self.assertIn("study_metadata", data)
            self.assertEqual(data["study_metadata"]["id_studio"], "json-test-case")
            self.assertEqual(data["study_metadata"]["committente"], "Test Committente")

            self.assertIn("questions", data)
            self.assertEqual(len(data["questions"]), 5)
            q01 = data["questions"][0]
            self.assertEqual(q01["id_item"], "Q01")
            self.assertEqual(q01["original_code"], "Q1")
            self.assertTrue(len(q01["response_options"]) >= 2)
            missing_codes = {m["code"] for m in q01["missing_codes"]}
            self.assertEqual(missing_codes, {"97", "98", "99"})

    def test_extract_plain_text_fixture(self):
        """Verifica l'estrazione da un file di testo grezzo (.txt) con formati misti."""
        txt_content = """# Indagine di Soddisfazione Trasporti
Committente: Agenzia Mobilità
Target: Utenti del servizio ferroviario
Anno: 2023

D01. Con quale frequenza utilizza il treno?
1. Tutti i giorni
2. Qualche volta a settimana
3. Meno spesso
98. Non ricordo
99. Preferisco non rispondere

D02. Come valuta la puntualità dei convogli?
1. Molto soddisfacente
2. Abbastanza soddisfacente
3. Poco soddisfacente
4. Per nulla soddisfacente
98. Non so esprimere un giudizio
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            in_file = Path(tmpdir) / "source_trasporti.txt"
            in_file.write_text(txt_content, encoding="utf-8")

            out_file = Path(tmpdir) / "extracted_trasporti.md"
            ok = extract_survey_knowledge(in_file, out_file, output_format="md")
            self.assertTrue(ok)

            issues = validate_extracted_survey_file(out_file)
            self.assertEqual(issues, [], f"Errori di validazione su testo estratto: {issues}")

            content = out_file.read_text(encoding="utf-8")
            self.assertIn("Agenzia Mobilità", content)
            self.assertIn("D01", content)
            self.assertIn("D02", content)
            self.assertIn("Q01", content)
            self.assertIn("Q02", content)

    def test_extract_structured_battery_matrix(self):
        """Verifica l'estrazione e il riconoscimento automatico di una batteria a matrice con SQ."""
        battery_md = """# Monitoraggio Istituzioni
### Sezione A — Gradimento
#### Q01 — Fiducia nelle Forze dell'Ordine
- **Testo per il rispondente**: Quanto si fida dei seguenti corpi dello Stato?
- **Tipo di domanda**: Batteria
- **Item della batteria**:
  - SQ01 = Carabinieri
  - SQ02 = Polizia di Stato
  - SQ03 = Guardia di Finanza
- **Opzioni e codici di risposta**:
  - 1 = Molta
  - 2 = Abbastanza
  - 3 = Poca
  - 4 = Nessuna
- **Codici distinti di uscita**:
  - 97 = Non applicabile
  - 98 = Non so
  - 99 = Preferisco non rispondere
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            in_file = Path(tmpdir) / "battery.md"
            in_file.write_text(battery_md, encoding="utf-8")

            out_json = Path(tmpdir) / "battery.json"
            ok = extract_survey_knowledge(in_file, out_json, output_format="json")
            self.assertTrue(ok)

            data = json.loads(out_json.read_text(encoding="utf-8"))
            self.assertGreaterEqual(len(data["batteries"]), 1)
            b01 = data["batteries"][0]
            self.assertEqual(b01["id_battery"], "B01")
            self.assertEqual(b01["item_count"], 3)
            self.assertIn("Carabinieri", str(data["questions"][0]["sub_items"]))

    def test_cli_execution_via_subprocess(self):
        """Verifica l'esecuzione reale tramite riga di comando subprocess."""
        with tempfile.TemporaryDirectory() as tmpdir:
            out_file = Path(tmpdir) / "cli_test_out.md"
            cmd = [
                sys.executable,
                str(self.script_path),
                str(self.demo_q_path),
                "-o",
                str(out_file),
                "--format",
                "md",
                "--id-studio",
                "cli-run-123",
                "--committente",
                "Noto Sondaggi Test",
                "-v",
            ]
            res = subprocess.run(cmd, capture_output=True, text=True)
            self.assertEqual(res.returncode, 0, f"CLI execution fallita: {res.stderr}")
            self.assertTrue(out_file.exists())
            self.assertIn("[OK] Artefatto salvato con successo", res.stdout)

            issues = validate_extracted_survey_file(out_file)
            self.assertEqual(issues, [])

    def test_character_encoding_and_accents(self):
        """Verifica la corretta gestione di accenti italiani e caratteri speciali."""
        text_accented = """# Indagine sulla Città
Q1. È soddisfatto della qualità della vita nella Sua città?
1. Molto soddisfatto
2. Poco soddisfatto
98. Non so
99. Non risponde
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            in_file = Path(tmpdir) / "accented.txt"
            # Scrittura sia in UTF-8 che verifica con latin-1
            in_file.write_text(text_accented, encoding="utf-8")

            survey = parse_survey_text(text_accented, default_id="accented-test")
            q = list(survey.sections.values())[0][0]
            self.assertIn("È soddisfatto della qualità", q.question_text)

            # Test fallback decodifica latin-1 in read_input_file
            in_latin = Path(tmpdir) / "latin.txt"
            in_latin.write_bytes(text_accented.encode("latin-1"))
            read_txt, _, err = read_input_file(in_latin)
            self.assertIsNone(err)
            self.assertIn("qualità", read_txt)

    def test_edge_case_empty_or_nonexistent_files(self):
        """Verifica il comportamento difensivo su file mancanti, vuoti o privi di domande."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # 1. File non esistente
            non_existent = Path(tmpdir) / "missing.md"
            out = Path(tmpdir) / "out.md"
            self.assertFalse(extract_survey_knowledge(non_existent, out))

            # 2. File vuoto
            empty_file = Path(tmpdir) / "empty.txt"
            empty_file.write_text("   \n", encoding="utf-8")
            self.assertFalse(extract_survey_knowledge(empty_file, out))

            # 3. File privo di domande
            no_q_file = Path(tmpdir) / "no_questions.txt"
            no_q_file.write_text("Questo è un testo descrittivo senza alcuna domanda di questionario.", encoding="utf-8")
            self.assertFalse(extract_survey_knowledge(no_q_file, out))

    def test_defensive_docx_and_pdf_handling(self):
        """Verifica che la gestione difensiva per DOCX e PDF assenti non causi crash non gestiti."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Creiamo un finto file .docx e un finto .pdf
            fake_docx = Path(tmpdir) / "test.docx"
            fake_docx.write_bytes(b"PK\x03\x04fakewebcontent")

            fake_pdf = Path(tmpdir) / "test.pdf"
            fake_pdf.write_bytes(b"%PDF-1.4fakepdf")

            # Lettura: se python-docx o pypdf non sono installati, ritorna messaggio descrittivo senza crash
            txt, fonte, err = read_input_file(fake_docx)
            if err:
                self.assertIn("python-docx", err)

            txt, fonte, err = read_input_file(fake_pdf)
            if err:
                self.assertTrue("pypdf" in err or "PyPDF2" in err or "PDF" in err)

    def test_make_construct_and_helpers(self):
        """Verifica helper make_construct e armonizzazione missing codes."""
        c = make_construct("Quanto è soddisfatto del servizio di trasporto pubblico locale?")
        self.assertLessEqual(len(c), 60)
        self.assertFalse(c.endswith("?"))

        # Test armonizzazione missing codes
        m_list = []
        harmonize_missing_codes(m_list)
        codes = [m.code for m in m_list]
        self.assertEqual(codes, ["97", "98", "99"])

    def test_extract_demo_run_biblioteca_questionnaire_correct_question_count(self):
        """Verifica che questionnaire.md di demo_run_biblioteca estragga esattamente 3 domande con opzioni corrette."""
        q_path = ROOT_DIR / "examples" / "demo_run_biblioteca" / "questionnaire.md"
        with tempfile.TemporaryDirectory() as tmpdir:
            out_file = Path(tmpdir) / "extracted_q.json"
            ok = extract_survey_knowledge(q_path, out_file, output_format="json")
            self.assertTrue(ok)
            data = json.loads(out_file.read_text(encoding="utf-8"))

            questions = data["questions"]
            # Devono essere estratte ESATTAMENTE 3 domande (Q1, Q2, Q3) e NON 19 frammenti di opzioni
            self.assertEqual(len(questions), 3, f"Attese 3 domande, estratte {len(questions)}")
            self.assertEqual(questions[0]["original_code"], "Q1")
            self.assertEqual(questions[1]["original_code"], "Q2")
            self.assertEqual(questions[2]["original_code"], "Q3")

            # Verifica opzioni della prima domanda
            self.assertEqual(len(questions[0]["response_options"]), 4)
            missing_codes_q1 = {m["code"] for m in questions[0]["missing_codes"]}
            self.assertEqual(missing_codes_q1, {"97", "98", "99"})

    def test_extract_demo_run_biblioteca_final_alphanumeric_codes(self):
        """Verifica che final.md estragga correttamente le domande con codici alfanumerici (Q2a, Q2b)."""
        f_path = ROOT_DIR / "examples" / "demo_run_biblioteca" / "final.md"
        with tempfile.TemporaryDirectory() as tmpdir:
            out_file = Path(tmpdir) / "extracted_final.json"
            ok = extract_survey_knowledge(f_path, out_file, output_format="json")
            self.assertTrue(ok)
            data = json.loads(out_file.read_text(encoding="utf-8"))

            questions = data["questions"]
            self.assertEqual(len(questions), 3)
            codes = [q["original_code"] for q in questions]
            self.assertIn("Q1", codes)
            self.assertIn("Q2a", codes)
            self.assertIn("Q2b", codes)

    def test_extract_questionnaire_template_format(self):
        """Verifica la compatibilità con il template ufficiale templates/questionnaire_template.md."""
        template_chunk = """# Questionario di Prova
### Sezione A — Servizi al Cittadino
#### Q01 — Valutazione Servizi
- Obiettivo del brief: Misurare la soddisfazione generale
- Testo per rispondente: Come valuta i servizi offerti dal Comune?
- Tipo di domanda: Chiusa singola
- Opzioni e codici:
  - 1 = Molto soddisfacente
  - 2 = Abbastanza soddisfacente
  - 3 = Poco soddisfacente
  - 4 = Per nulla soddisfacente
- Non so / rifiuto / non applicabile (codici distinti obbligatori):
  - 97 = Non applicabile (non residente)
  - 98 = Non so
  - 99 = Preferisco non rispondere
- Filtro / skip: Posta a tutti i residenti
- Nota per intervistatore: Non sollecitare i codici di uscita
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            in_file = Path(tmpdir) / "template_test.md"
            in_file.write_text(template_chunk, encoding="utf-8")
            out_file = Path(tmpdir) / "extracted_template.json"
            ok = extract_survey_knowledge(in_file, out_file, output_format="json")
            self.assertTrue(ok)

            data = json.loads(out_file.read_text(encoding="utf-8"))
            self.assertEqual(len(data["questions"]), 1)
            q01 = data["questions"][0]
            self.assertEqual(q01["question_text"], "Come valuta i servizi offerti dal Comune?")
            self.assertEqual(q01["filter_logic"], "Posta a tutti i residenti")
            self.assertEqual(q01["interviewer_notes"], "Non sollecitare i codici di uscita")
            self.assertEqual(len(q01["response_options"]), 4)

            # L'intestazione dei missing codes non deve essere catturata come codice opzione
            missing_labels = [m["label"] for m in q01["missing_codes"]]
            self.assertFalse(any("codici distinti obbligatori" in l.lower() for l in missing_labels))

    def test_extract_various_option_formats(self):
        """Verifica che i vari formati di opzione (1), a), [1], 1 =, 1.) siano riconosciuti uniformemente."""
        mixed_text = """# Questionario Formati Misti
Q1. Come valuta la qualità dei parchi?
1) Ottima
2) Buona
3) Sufficiente
4) Insufficiente
98) Non so
99) Rifiuto

Q2. Con quale mezzo si sposta prevalentemente?
a) Auto privata
b) Mezzi pubblici
c) Bicicletta / monopattino
d) A piedi
98. Non so
99. Rifiuta
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            in_file = Path(tmpdir) / "mixed.txt"
            in_file.write_text(mixed_text, encoding="utf-8")
            out_file = Path(tmpdir) / "mixed.json"
            ok = extract_survey_knowledge(in_file, out_file, output_format="json")
            self.assertTrue(ok)

            data = json.loads(out_file.read_text(encoding="utf-8"))
            self.assertEqual(len(data["questions"]), 2)
            q1 = data["questions"][0]
            self.assertEqual(len(q1["response_options"]), 4)
            self.assertEqual(q1["response_options"][0]["code"], "1")
            self.assertEqual(q1["response_options"][0]["label"], "Ottima")

            q2 = data["questions"][1]
            self.assertEqual(len(q2["response_options"]), 4)
            self.assertEqual(q2["response_options"][0]["code"], "a")
            self.assertEqual(q2["response_options"][0]["label"], "Auto privata")

    def test_utf8_bom_handling(self):
        """Verifica la corretta lettura di file con UTF-8 BOM."""
        bom_text = "\ufeff# Indagine con BOM\nQ1. Domanda di test con BOM? Sì / No / Non so.\n"
        with tempfile.TemporaryDirectory() as tmpdir:
            in_file = Path(tmpdir) / "bom.txt"
            in_file.write_bytes(bom_text.encode("utf-8"))
            out_file = Path(tmpdir) / "bom.json"
            ok = extract_survey_knowledge(in_file, out_file, output_format="json")
            self.assertTrue(ok)
            data = json.loads(out_file.read_text(encoding="utf-8"))
            self.assertEqual(len(data["questions"]), 1)

    def test_cli_campione_argument(self):
        """Verifica che l'argomento CLI --campione popoli correttamente i metadati."""
        with tempfile.TemporaryDirectory() as tmpdir:
            out_file = Path(tmpdir) / "cli_campione.md"
            cmd = [
                sys.executable,
                str(self.script_path),
                str(self.demo_q_path),
                "-o",
                str(out_file),
                "--campione",
                "1000 casi",
            ]
            res = subprocess.run(cmd, capture_output=True, text=True)
            self.assertEqual(res.returncode, 0)
            content = out_file.read_text(encoding="utf-8")
            self.assertIn("Numerosita campionaria originaria: 1000 casi", content)


if __name__ == "__main__":
    unittest.main()
