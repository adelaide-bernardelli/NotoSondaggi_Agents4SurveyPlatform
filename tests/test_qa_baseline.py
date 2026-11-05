import os
import sys
import tempfile
import unittest
from pathlib import Path

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts.check_mirror_sync import (
    check_global_rules,
    check_agents,
    check_skills,
    check_workflows_commands,
    check_templates,
)
from scripts.validate_runs import (
    validate_case,
    validate_limesurvey_file,
    validate_extracted_survey_file,
)


class TestQABaseline(unittest.TestCase):
    """Test di regressione e QA continuo della baseline architetturale."""

    def test_global_rules_sync(self):
        ok, msg = check_global_rules()
        self.assertTrue(ok, f"Regole globali non sincronizzate: {msg}")

    def test_agents_mirror_sync(self):
        ok, msg = check_agents()
        self.assertTrue(ok, f"Agenti non sincronizzati: {msg}")

    def test_skills_mirror_sync(self):
        ok, msg = check_skills()
        self.assertTrue(ok, f"Skill non sincronizzate: {msg}")
        self.assertEqual(msg, "Tutte le 7 skill sono perfettamente identiche")

    def test_workflows_commands_sync(self):
        ok, msg = check_workflows_commands()
        self.assertTrue(ok, f"Workflow e comandi non sincronizzati: {msg}")

    def test_templates_presence(self):
        ok, msg = check_templates()
        self.assertTrue(ok, f"Template obbligatori non completi: {msg}")
        self.assertEqual(msg, "Tutti i 7 template obbligatori sono presenti")

    def test_extracted_survey_template_content(self):
        """Verifica la completezza dei campi del template extracted_survey_template.md."""
        tpl_path = ROOT_DIR / "templates" / "extracted_survey_template.md"
        self.assertTrue(tpl_path.exists(), "templates/extracted_survey_template.md mancante")
        content = tpl_path.read_text(encoding="utf-8")
        
        required_headers = [
            "## 1. Metadati dello Studio Estratto",
            "## 2. Inquadramento Metodologico e Aree Tematiche",
            "## 3. Inventario Strutturato delle Domande e Batterie Estratte",
            "## 4. Mappa delle Batterie Standard Identificate",
            "## 5. Note di Validazione Umana e Revisione",
        ]
        for header in required_headers:
            self.assertIn(header, content, f"Sezione '{header}' mancante nel template di estrazione")
            
        required_fields = [
            "ID Studio / Nome Archivio:",
            "Committente originario:",
            "Popolazione di riferimento e Target:",
            "Codice originale nella fonte:",
            "Costrutto / Variabile misurata:",
            "Testo originario per rispondente:",
            "97 = Non applicabile",
            "98 = Non so",
            "99 = Preferisco non rispondere",
            "Valutazione comparabilita storica:",
        ]
        for field in required_fields:
            self.assertIn(field, content, f"Campo '{field}' mancante nel template di estrazione")

    def test_noto_survey_extractor_skill_sync(self):
        """Verifica che la skill noto-survey-extractor esista e sia speculare byte-for-byte."""
        ant_file = ROOT_DIR / ".agents" / "skills" / "noto-survey-extractor" / "SKILL.md"
        cld_file = ROOT_DIR / ".claude" / "skills" / "noto-survey-extractor" / "SKILL.md"
        
        self.assertTrue(ant_file.exists(), "noto-survey-extractor SKILL.md mancante in .agents")
        self.assertTrue(cld_file.exists(), "noto-survey-extractor SKILL.md mancante in .claude")
        
        content_ant = ant_file.read_text(encoding="utf-8").replace("\r\n", "\n")
        content_cld = cld_file.read_text(encoding="utf-8").replace("\r\n", "\n")
        
        self.assertEqual(content_ant, content_cld, "I due file SKILL.md di noto-survey-extractor non sono identici")
        self.assertIn("name: noto-survey-extractor", content_ant)
        self.assertIn("templates/extracted_survey_template.md", content_ant)
        self.assertIn("97", content_ant)
        self.assertIn("98", content_ant)
        self.assertIn("99", content_ant)

    def test_demo_run_biblioteca_valid(self):
        demo_dir = ROOT_DIR / "examples" / "demo_run_biblioteca"
        self.assertTrue(demo_dir.exists(), "Cartella demo_run_biblioteca mancante")
        self.assertTrue(validate_case(demo_dir), "Validazione del caso demo_run_biblioteca fallita")

    def test_demo_run_limesurvey_export_valid(self):
        """Verifica che l'artefatto limesurvey_survey.txt nel caso demo sia valido."""
        ls_file = ROOT_DIR / "examples" / "demo_run_biblioteca" / "limesurvey_survey.txt"
        self.assertTrue(ls_file.exists(), "File limesurvey_survey.txt mancante nel caso demo")
        issues = validate_limesurvey_file(ls_file)
        self.assertEqual(issues, [], f"Validazione di limesurvey_survey.txt ha prodotto errori: {issues}")
        # Test polimorfismo Path/str
        issues_str = validate_limesurvey_file(str(ls_file))
        self.assertEqual(issues_str, [], f"Validazione con percorso stringa ha prodotto errori: {issues_str}")

    def test_validate_case_str_path(self):
        """Verifica che validate_case accetti percorsi sia come Path sia come stringhe."""
        demo_dir = ROOT_DIR / "examples" / "demo_run_biblioteca"
        self.assertTrue(validate_case(str(demo_dir)), "Validazione con percorso stringa fallita")

    def test_validate_limesurvey_file_edge_cases(self):
        """Verifica i controlli del validatore LimeSurvey su file malformati ed edge cases."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)

            # 1. File non esistente
            non_existent = tmp_path / "missing.txt"
            errs = validate_limesurvey_file(non_existent)
            self.assertTrue(any("Impossibile leggere" in e for e in errs))

            # 2. File vuoto (test sia con Path sia con str)
            empty_file = tmp_path / "empty.txt"
            empty_file.write_text("", encoding="utf-8")
            errs = validate_limesurvey_file(empty_file)
            self.assertTrue(any("vuoto" in e for e in errs))
            errs_str = validate_limesurvey_file(str(empty_file))
            self.assertTrue(any("vuoto" in e for e in errs_str))

            # 3. Intestazione con colonne errate
            bad_header_file = tmp_path / "bad_header.txt"
            bad_header_file.write_text("col1\tcol2\tcol3\n", encoding="utf-8")
            errs = validate_limesurvey_file(bad_header_file)
            self.assertTrue(any("Intestazione non conforme" in e for e in errs))

            # 4. Riga con numero colonne errato
            bad_row_file = tmp_path / "bad_row.txt"
            header = "\t".join([
                "id", "related_id", "class", "type/scale", "name",
                "relevance", "text", "help", "language", "validation",
                "mandatory", "other", "default", "same_default"
            ])
            bad_row_file.write_text(f"{header}\n1\t0\tS\tshort_row\n", encoding="utf-8")
            errs = validate_limesurvey_file(bad_row_file)
            self.assertTrue(any("anziché 14" in e for e in errs))

            # 5. Classe sconosciuta
            unknown_class_file = tmp_path / "unknown_class.txt"
            row_unknown = "\t".join(["1", "0", "UNKNOWN", "", "name", "1", "txt", "hlp", "it", "", "N", "N", "", ""])
            unknown_class_file.write_text(f"{header}\n{row_unknown}\n", encoding="utf-8")
            errs = validate_limesurvey_file(unknown_class_file)
            self.assertTrue(any("non riconosciuta" in e for e in errs))

            # 6. Riga con classe vuota (es. 13 tab)
            empty_class_file = tmp_path / "empty_class.txt"
            row_empty_class = "\t" * 13
            unknown_class_file.write_text(f"{header}\n{row_unknown}\n", encoding="utf-8")
            empty_class_file.write_text(f"{header}\n{row_empty_class}\n", encoding="utf-8")
            errs = validate_limesurvey_file(empty_class_file)
            self.assertTrue(any("campo 'class' vuoto" in e for e in errs))

            # 7. Riga vuota nel mezzo dei record
            empty_line_file = tmp_path / "empty_line.txt"
            row_s = "\t".join(["", "", "S", "", "language", "", "it", "", "", "", "", "", "", ""])
            empty_line_file.write_text(f"{header}\n\n{row_s}\n", encoding="utf-8")
            errs = validate_limesurvey_file(empty_line_file)
            self.assertTrue(any("riga vuota non ammessa" in e for e in errs))

            # 8. Classi strutturali minime mancanti (manca Q, G, SL)
            missing_classes_file = tmp_path / "missing_classes.txt"
            missing_classes_file.write_text(f"{header}\n{row_s}\n", encoding="utf-8")
            errs = validate_limesurvey_file(missing_classes_file)
            self.assertTrue(any("mancanti" in e for e in errs))

    def test_validate_extracted_survey_file_template(self):
        """Verifica che il template extracted_survey_template.md sia conforme al validatore."""
        tpl_path = ROOT_DIR / "templates" / "extracted_survey_template.md"
        errs = validate_extracted_survey_file(tpl_path)
        self.assertEqual(errs, [], f"Il template extracted_survey presenta errori: {errs}")
        # Test polimorfismo Path/str
        errs_str = validate_extracted_survey_file(str(tpl_path))
        self.assertEqual(errs_str, [], f"Il template con path str presenta errori: {errs_str}")

    def test_validate_extracted_survey_file_edge_cases(self):
        """Verifica i controlli del validatore di estrazione su casi limite ed errori."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)

            # 1. File non esistente
            non_existent = tmp_path / "missing.md"
            errs = validate_extracted_survey_file(non_existent)
            self.assertTrue(any("Impossibile leggere" in e for e in errs))

            # 2. File vuoto
            empty_file = tmp_path / "empty.md"
            empty_file.write_text("   \n", encoding="utf-8")
            errs = validate_extracted_survey_file(empty_file)
            self.assertTrue(any("vuoto" in e for e in errs))

            # 3. Sezioni obbligatorie mancanti
            partial_file = tmp_path / "partial.md"
            partial_file.write_text("## 1. Metadati dello Studio Estratto\nID Studio / Nome Archivio: Test\n", encoding="utf-8")
            errs = validate_extracted_survey_file(partial_file)
            self.assertTrue(any("Sezione mancante" in e for e in errs))

            # 4. Metadati minimi mancanti
            valid_base = (ROOT_DIR / "templates" / "extracted_survey_template.md").read_text(encoding="utf-8")
            missing_meta_file = tmp_path / "no_meta.md"
            missing_meta_file.write_text(valid_base.replace("ID Studio / Nome Archivio:", "Studio:"), encoding="utf-8")
            errs = validate_extracted_survey_file(missing_meta_file)
            self.assertTrue(any("Metadato obbligatorio mancante" in e for e in errs))

            # 5. Codici standard non risposta mancanti (es. tolgo 97)
            missing_97_file = tmp_path / "no_97.md"
            missing_97_file.write_text(valid_base.replace("97", "00"), encoding="utf-8")
            errs = validate_extracted_survey_file(missing_97_file)
            self.assertTrue(any("Codice 97" in e for e in errs))

    def test_validate_case_with_extracted_survey(self):
        """Verifica che validate_case rilevi e convalidi extracted_survey.md se presente in una cartella caso."""
        with tempfile.TemporaryDirectory() as tmpdir:
            case_dir = Path(tmpdir) / "test_case"
            case_dir.mkdir()
            # Status minimo conforme
            status_file = case_dir / "status.md"
            status_file.write_text(
                "# Status\n## Metadati del Caso\n- ID Caso: test\n- Fase attiva corrente: BOZZA\n"
                "## Avanzamento delle Fasi\n## Registro delle Decisioni Umane in Chat\n",
                encoding="utf-8",
            )
            # extracted_survey.md valido
            ext_file = case_dir / "extracted_survey.md"
            valid_content = (ROOT_DIR / "templates" / "extracted_survey_template.md").read_text(encoding="utf-8")
            ext_file.write_text(valid_content, encoding="utf-8")

            self.assertTrue(validate_case(case_dir), "Validazione del caso con extracted_survey valido fallita")

            # Invalida extracted_survey.md rimuovendo codice 99
            ext_file.write_text(valid_content.replace("99", "XX"), encoding="utf-8")
            self.assertFalse(validate_case(case_dir), "Validazione doveva fallire con extracted_survey invalido")

    def test_ai_coordinator_extractor_delegation_sync(self):
        """Verifica che la delega di noto-survey-extractor sia censita e sincronizzata in ai-coordinator."""
        ant_coord = ROOT_DIR / ".agents" / "agents" / "ai-coordinator.md"
        cld_coord = ROOT_DIR / ".claude" / "agents" / "ai-coordinator.md"

        self.assertTrue(ant_coord.exists(), "ai-coordinator.md mancante in .agents")
        self.assertTrue(cld_coord.exists(), "ai-coordinator.md mancante in .claude")

        content_ant = ant_coord.read_text(encoding="utf-8")
        content_cld = cld_coord.read_text(encoding="utf-8")

        for content in [content_ant, content_cld]:
            self.assertIn("noto-survey-extractor", content)
            self.assertIn("templates/extracted_survey_template.md", content)
            self.assertIn("extracted_survey.md", content)


if __name__ == "__main__":
    unittest.main()
