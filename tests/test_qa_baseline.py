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
from scripts.validate_runs import validate_case, validate_limesurvey_file


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

    def test_workflows_commands_sync(self):
        ok, msg = check_workflows_commands()
        self.assertTrue(ok, f"Workflow e comandi non sincronizzati: {msg}")

    def test_templates_presence(self):
        ok, msg = check_templates()
        self.assertTrue(ok, f"Template obbligatori non completi: {msg}")

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


if __name__ == "__main__":
    unittest.main()
