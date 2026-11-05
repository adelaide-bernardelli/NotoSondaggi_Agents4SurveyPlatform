import unittest
import sys
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
from scripts.validate_runs import validate_case


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


if __name__ == "__main__":
    unittest.main()
