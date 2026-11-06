import os
import re
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
    extract_question_blocks,
    has_regia_instructions,
    validate_brief_file,
    validate_case,
    validate_extracted_survey_file,
    validate_final_file,
    validate_limesurvey_file,
    validate_questionnaire_file,
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
        self.assertEqual(msg, "Tutti gli 8 template obbligatori sono presenti")

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

    def test_demo_run_brief_valid(self):
        """Verifica che brief.md in demo_run_biblioteca sia presente e conforme a validate_brief_file."""
        brief_path = ROOT_DIR / "examples" / "demo_run_biblioteca" / "brief.md"
        self.assertTrue(brief_path.exists(), "brief.md mancante in examples/demo_run_biblioteca/")
        issues = validate_brief_file(brief_path)
        self.assertEqual(issues, [], f"Validazione di brief.md fallita: {issues}")
        # Test polimorfismo str/Path
        issues_str = validate_brief_file(str(brief_path))
        self.assertEqual(issues_str, [], f"Validazione con percorso stringa fallita: {issues_str}")

    def test_brief_template_valid(self):
        """Verifica che templates/brief_template.md sia conforme a validate_brief_file."""
        tpl_path = ROOT_DIR / "templates" / "brief_template.md"
        self.assertTrue(tpl_path.exists(), "templates/brief_template.md mancante")
        issues = validate_brief_file(tpl_path)
        self.assertEqual(issues, [], f"templates/brief_template.md presenta non conformità: {issues}")

    def test_validate_brief_file_edge_cases(self):
        """Verifica la robustezza di validate_brief_file su casi limite e anomalie."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)

            # 1. File non esistente
            non_existent = tmp_path / "missing_brief.md"
            errs = validate_brief_file(non_existent)
            self.assertTrue(any("Impossibile leggere" in e for e in errs))

            # 2. File vuoto
            empty_file = tmp_path / "empty_brief.md"
            empty_file.write_text("   \n", encoding="utf-8")
            errs = validate_brief_file(empty_file)
            self.assertTrue(any("vuoto" in e for e in errs))
            errs_str = validate_brief_file(str(empty_file))
            self.assertTrue(any("vuoto" in e for e in errs_str))

            # 3. Base valida per test mutazionali
            valid_base = (ROOT_DIR / "templates" / "brief_template.md").read_text(encoding="utf-8")

            # 4. Sezione mancante (es. tolgo Sezione 1 Inquadramento)
            no_sec1 = tmp_path / "no_sec1.md"
            no_sec1.write_text(valid_base.replace("Inquadramento e Fonti", "Background"), encoding="utf-8")
            errs = validate_brief_file(no_sec1)
            self.assertTrue(any("Inquadramento" in e for e in errs))

            # 5. ID caso mancante
            no_id = tmp_path / "no_id.md"
            no_id.write_text(valid_base.replace("ID caso:", "Codice:"), encoding="utf-8")
            errs = validate_brief_file(no_id)
            self.assertTrue(any("ID caso" in e for e in errs))

            # 6. Obiettivo conoscitivo mancante
            no_obj = tmp_path / "no_obj.md"
            no_obj.write_text(valid_base.replace("Obiettivo conoscitivo", "Scopo"), encoding="utf-8")
            errs = validate_brief_file(no_obj)
            self.assertTrue(any("Obiettivo conoscitivo" in e for e in errs))

            # 7. Non risposta mancante nella sezione vincoli
            no_nonresp = tmp_path / "no_nonresp.md"
            no_nonresp.write_text(valid_base.replace("non risposta", "omissioni"), encoding="utf-8")
            errs = validate_brief_file(no_nonresp)
            self.assertTrue(any("non risposta" in e for e in errs))

            # 8. Privacy mancante nella sezione vincoli
            no_priv = tmp_path / "no_priv.md"
            no_priv.write_text(re.sub(r"privacy|GDPR|Art\.\s*9", "riservatezza", valid_base, flags=re.IGNORECASE), encoding="utf-8")
            errs = validate_brief_file(no_priv)
            self.assertTrue(any("privacy" in e.lower() for e in errs))

    def test_validate_case_with_brief_lifecycle(self):
        """Verifica che validate_case controlli brief.md se presente nel caso."""
        with tempfile.TemporaryDirectory() as tmpdir:
            case_dir = Path(tmpdir) / "test_brief_case"
            case_dir.mkdir()
            status_file = case_dir / "status.md"
            status_file.write_text(
                "# Status\n## Metadati del Caso\n- ID Caso: brief-test\n- Fase attiva corrente: BRIEF\n"
                "## Avanzamento delle Fasi\n## Registro delle Decisioni Umane in Chat\n",
                encoding="utf-8",
            )
            # brief.md valido
            brief_file = case_dir / "brief.md"
            valid_brief = (ROOT_DIR / "templates" / "brief_template.md").read_text(encoding="utf-8")
            brief_file.write_text(valid_brief, encoding="utf-8")

            self.assertTrue(validate_case(case_dir), "Validazione del caso con brief valido fallita")

            # Rende brief non conforme rimuovendo ID caso
            brief_file.write_text(valid_brief.replace("ID caso", "Codice Progetto"), encoding="utf-8")
            self.assertFalse(validate_case(case_dir), "Validazione doveva fallire con brief non conforme")

    def test_templates_regia_syntax_valid(self):
        """Verifica che i template ufficiali questionnaire_template.md e final_template.md validino con note di regia."""
        q_tpl = ROOT_DIR / "templates" / "questionnaire_template.md"
        f_tpl = ROOT_DIR / "templates" / "final_template.md"

        errs_q = validate_questionnaire_file(q_tpl)
        self.assertEqual(errs_q, [], f"templates/questionnaire_template.md non valida: {errs_q}")

        errs_f = validate_final_file(f_tpl)
        self.assertEqual(errs_f, [], f"templates/final_template.md non valida: {errs_f}")

    def test_has_regia_instructions_detection_patterns(self):
        """Verifica la funzione has_regia_instructions con sintassi standard, varianti e casi limite."""
        # Standard M6: - **Istruzioni di regia e somministrazione**: [NON LEGGERE / SPONTANEA / ROTAZIONE / PROBING]
        block_std = (
            "#### Q01 — Costrutto\n"
            "- **Testo per il rispondente**: Domanda di prova?\n"
            "- **Istruzioni di regia e somministrazione**: [NON LEGGERE / SPONTANEA / ROTAZIONE / PROBING]\n"
        )
        self.assertTrue(has_regia_instructions(block_std))

        # Tolleranza difensiva: Istruzioni per intervistatore
        block_interv = (
            "#### Q02 — Costrutto\n"
            "- **Istruzioni per intervistatore**: Non leggere le opzioni, attendere risposta spontanea\n"
        )
        self.assertTrue(has_regia_instructions(block_interv))

        # Tolleranza difensiva: Nota per intervistatore
        block_nota = (
            "Q1. Testo?\n"
            "- Nota per intervistatore: leggere opzioni lentamente\n"
        )
        self.assertTrue(has_regia_instructions(block_nota))

        # Tolleranza difensiva: Note di regia
        block_note_regia = (
            "Q2. Testo?\n"
            "- Note di regia: ruotare le opzioni da 1 a 4\n"
        )
        self.assertTrue(has_regia_instructions(block_note_regia))

        # Tag inline [REGIA: ...]
        block_inline_regia = "Q3. Quanto è soddisfatto? [REGIA: NON LEGGERE OPZIONI]\n1. Molto\n2. Poco\n"
        self.assertTrue(has_regia_instructions(block_inline_regia))

        # Tag inline [ISTRUZIONI: ...]
        block_inline_istr = "Q4. Quanto è soddisfatto? [ISTRUZIONI: SCELTA SINGOLA SPONTANEA]\n1. Molto\n"
        self.assertTrue(has_regia_instructions(block_inline_istr))

        # Istruzioni multiriga indentate valide
        block_multiline = (
            "#### Q05 — Costrutto\n"
            "- **Istruzioni di regia e somministrazione**:\n"
            "  - Non leggere le opzioni ad alta voce\n"
            "  - Ruotare l'ordine delle alternative\n"
            "1. Opzione A\n"
        )
        self.assertTrue(has_regia_instructions(block_multiline))

        # Caso negativo: voce presente ma vuota
        block_empty_note = (
            "#### Q05 — Costrutto\n"
            "- **Testo per il rispondente**: Domanda di prova?\n"
            "- **Istruzioni di regia e somministrazione**:\n"
            "- **Nota sulla comparabilita storica**: Alta\n"
        )
        self.assertFalse(has_regia_instructions(block_empty_note))

        # Caso negativo: campo regia vuoto seguito immediatamente da opzioni numerate
        block_empty_before_options = (
            "Q1. Testo?\n"
            "- **Istruzioni di regia e somministrazione**:\n"
            "1. Prima opzione\n"
            "2. Seconda opzione\n"
            "98. Non so\n"
            "99. Rifiuto\n"
        )
        self.assertFalse(has_regia_instructions(block_empty_before_options))

        # Caso negativo: campo regia vuoto seguito da domanda successiva
        block_empty_before_next_q = (
            "Q1. Testo?\n"
            "- **Istruzioni di regia e somministrazione**:\n"
            "Q2. Domanda successiva?\n"
        )
        self.assertFalse(has_regia_instructions(block_empty_before_next_q))

        # Caso negativo: solo puntini di sospensione o trattino come segnaposto
        self.assertFalse(has_regia_instructions("Q1. Testo?\n- **Istruzioni di regia e somministrazione**: ...\n1. A\n"))
        self.assertFalse(has_regia_instructions("Q1. Testo?\n- **Istruzioni di regia e somministrazione**: -\n1. A\n"))

        # Caso negativo: domanda completamente priva di note di regia
        block_no_regia = (
            "#### Q06 — Costrutto\n"
            "- **Testo per il rispondente**: Domanda senza regia?\n"
            "- **Tipo di domanda**: Chiusa singola\n"
        )
        self.assertFalse(has_regia_instructions(block_no_regia))

    def test_extract_question_blocks_complex_formats(self):
        """Verifica l'estrazione di domande con numerazioni articolate, intestazioni Markdown H2/H3/H4 e grassetto."""
        content = (
            "# Questionario Articolato\n"
            "## 3. Domande del Questionario\n"
            "### Sezione 1 — Generale\n"
            "## Q01 — Soddisfazione complessiva\n"
            "- **Istruzioni di regia e somministrazione**: [LEGGERE]\n"
            "1. Molto\n2. Poco\n"
            "### Domanda 2: Servizi erogati\n"
            "- **Istruzioni per intervistatore**: Spontanea\n"
            "1. Sì\n2. No\n"
            "#### Q12_A — Sotto-item di valutazione orari\n"
            "- **Istruzioni di regia e somministrazione**: [ROTAZIONE]\n"
            "1. Positivo\n2. Negativo\n"
            "**Q12_B.** Sotto-item di valutazione tariffe?\n"
            "- **Istruzioni di regia e somministrazione**: [ROTAZIONE]\n"
            "1. Adeguate\n2. Elevate\n"
            "Domanda 13: Suggerimenti aperti\n"
            "- **Istruzioni di regia e somministrazione**: [APERTA]\n"
            "## 4. Specifiche Riepilogative dei Filtri\n"
            "Filtro: nessuno\n"
        )
        q_blocks = extract_question_blocks(content)
        q_ids = [q[0] for q in q_blocks]
        self.assertEqual(q_ids, ["Q01", "Q2", "Q12_A", "Q12_B", "Q13"])
        for qid, block in q_blocks:
            self.assertTrue(has_regia_instructions(block), f"Domanda {qid} doveva contenere note di regia")

    def test_validate_questionnaire_and_final_file_regia_edge_cases(self):
        """Verifica i controlli del validatore su questionari con e senza istruzioni di regia."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)

            # 1. Questionario bozza valido con sintassi standard M6
            valid_q = (
                "# Questionario Bozza\n"
                "- Codici: 97=Non applicabile, 98=Non so, 99=Preferisco non rispondere\n"
                "## 3. Domande\n"
                "#### Q01 — Soddisfazione\n"
                "- Testo: Come valuta il servizio?\n"
                "- **Istruzioni di regia e somministrazione**: [LEGGERE LE OPZIONI — RISPOSTA SINGOLA]\n"
                "1. Soddisfatto\n2. Non soddisfatto\n97. Non applicabile\n98. Non so\n99. Preferisco non rispondere\n"
            )
            q_file = tmp_path / "valid_q.md"
            q_file.write_text(valid_q, encoding="utf-8")
            self.assertEqual(validate_questionnaire_file(q_file), [])

            # 2. Questionario bozza privo di regia su Q02
            invalid_q = valid_q + (
                "\n#### Q02 — Utilizzo\n"
                "- Testo: Utilizza il servizio regolarmente?\n"
                "1. Sì\n2. No\n98. Non so\n99. Preferisco non rispondere\n"
            )
            q_file_err = tmp_path / "invalid_q.md"
            q_file_err.write_text(invalid_q, encoding="utf-8")
            errs = validate_questionnaire_file(q_file_err)
            self.assertTrue(any("Q02" in e and "regia" in e for e in errs))

            # 3. Questionario finale valido con tolleranza difensiva 'Istruzioni per intervistatore'
            valid_f = (
                "# Questionario Finale\n"
                "Codici garantiti: 97, 98, 99\n"
                "### Testo Definitivo\n"
                "Q1. Quanto è soddisfatto?\n"
                "- **Istruzioni per intervistatore**: Attendere risposta spontanea\n"
                "1. Molto\n2. Poco\n98. Non so\n99. Rifiuto\n"
            )
            f_file = tmp_path / "valid_f.md"
            f_file.write_text(valid_f, encoding="utf-8")
            self.assertEqual(validate_final_file(f_file), [])

            # 4. Questionario finale con domanda priva di regia
            invalid_f = valid_f + "\nQ2. Come giudica il trasporto?\n1. Buono\n2. Scarso\n98. Non so\n99. Rifiuto\n"
            f_file_err = tmp_path / "invalid_f.md"
            f_file_err.write_text(invalid_f, encoding="utf-8")
            errs_f = validate_final_file(f_file_err)
            self.assertTrue(any("Q2" in e and "regia" in e for e in errs_f))


if __name__ == "__main__":
    unittest.main()
