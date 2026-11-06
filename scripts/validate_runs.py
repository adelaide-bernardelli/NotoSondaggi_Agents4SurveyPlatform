#!/usr/bin/env python3
"""
Linter e validatore formale degli artefatti generati in runs/<caso>/
Verifica la conformita alle regole metodologiche, alla griglia a 11 colonne,
alle schede a 12 campi, alla presenza dei codici di non risposta (97, 98, 99)
e alla struttura del file LimeSurvey TSV (14 colonne standard).
"""

import os
import sys
import re
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

def validate_status_file(path):
    issues = []
    path = Path(path)
    content = path.read_text(encoding="utf-8")
    
    required_sections = [
        "Metadati del Caso",
        "Avanzamento delle Fasi",
        "Registro delle Decisioni Umane in Chat",
    ]
    for s in required_sections:
        if s not in content:
            issues.append(f"Sezione mancante: '{s}'")
            
    if "ID Caso" not in content:
        issues.append("Campo 'ID Caso' mancante nei metadati")
    if "Fase attiva corrente" not in content:
        issues.append("Campo 'Fase attiva corrente' mancante nei metadati")
        
    return issues

def validate_brief_file(path):
    """
    Valida la conformita formale di un artefatto brief.md rispetto a templates/brief_template.md.
    Verifica sezioni obbligatorie, metadati di base, obiettivi conoscitivi e vincoli privacy/metodologici.
    Supporta polimorficamente sia Path sia stringhe.
    """
    issues = []
    path = Path(path)
    try:
        content = path.read_text(encoding="utf-8")
    except Exception as e:
        return [f"Impossibile leggere il file del brief: {e}"]

    if not content.strip():
        return ["File del brief vuoto o privo di contenuto"]

    # 1. Sezioni obbligatorie (6 sezioni di templates/brief_template.md)
    required_sections = [
        ("Inquadramento", "Sezione 1 (Inquadramento e Fonti) mancante o non riconosciuta"),
        ("Obiettivi", "Sezione 2 (Obiettivi e Costrutti) mancante o non riconosciuta"),
        ("Disegno", "Sezione 3 (Disegno di Rilevazione) mancante o non riconosciuta"),
        ("Vincoli", "Sezione 4 (Vincoli Metodologici e Privacy Preliminari) mancante o non riconosciuta"),
        ("Lacune", "Sezione 5 (Lacune Informative e Domande per il Ricercatore) mancante o non riconosciuta"),
        ("Approvazione", "Sezione 6 (Approvazione Umana) mancante o non riconosciuta"),
    ]
    for kw, msg in required_sections:
        if not re.search(r"^##\s+.*" + re.escape(kw), content, re.MULTILINE | re.IGNORECASE):
            issues.append(msg)

    # 2. Metadati obbligatori
    if not re.search(r"ID\s+(?:caso|studio|indagine)", content, re.IGNORECASE):
        issues.append("Campo 'ID caso' mancante nei metadati del brief")

    # 3. Obiettivi conoscitivi
    if not re.search(r"Obiettivo\s+conoscitivo", content, re.IGNORECASE):
        issues.append("Definizione dell'obiettivo conoscitivo ('Obiettivo conoscitivo') mancante nel brief")

    # 4. Vincoli metodologici e privacy preliminari
    if not re.search(r"non risposta", content, re.IGNORECASE):
        issues.append("Prescrizioni sulla gestione della non risposta mancanti nei vincoli del brief")
    if not re.search(r"privacy|GDPR|Art\.\s*9", content, re.IGNORECASE):
        issues.append("Prescrizioni sui vincoli privacy/GDPR mancanti nei vincoli del brief")

    return issues

def has_regia_instructions(block: str) -> bool:
    """
    Verifica se il blocco di una domanda contiene istruzioni di regia o somministrazione.
    Riconosce la sintassi standardizzata:
      - **Istruzioni di regia e somministrazione**: [NON LEGGERE / SPONTANEA / ROTAZIONE / PROBING]
    e garantisce tolleranza difensiva per varianti equivalenti:
      - Istruzioni per intervistatore / l'intervistatore / di somministrazione
      - Nota / Note di regia / per intervistatore
      - Tag inline [REGIA: ...] o [ISTRUZIONI: ...]
    """
    # 1. Tag inline [REGIA: ...] o [ISTRUZIONI: ...]
    if re.search(r"\[(?:REGIA|ISTRUZIONI)\s*:\s*[^\]]+\]", block, re.IGNORECASE):
        return True

    # 2. Linee strutturate di regia / somministrazione / intervistatore
    patterns = [
        r"^[ \t]*[-*]?[ \t]*(?:\*\*)?(?:Istruzioni(?:\s+di\s+regia(?:\s+e\s+somministrazione)?|\s+per\s+(?:l['’])?intervistatore|\s+di\s+somministrazione|\s+generali|\s+intervistatore)?|Not[ae]\s+(?:di\s+regia|per\s+(?:l['’])?intervistatore|intervistatore))[^*:\r\n]*(?:\*\*)?:[ \t]*([^\r\n]+)?",
    ]
    for pat in patterns:
        m = re.search(pat, block, re.MULTILINE | re.IGNORECASE)
        if m:
            val = m.group(1)
            if val and val.strip():
                clean_val = re.sub(r"^[.\-–—\s]+$", "", val.strip())
                if clean_val and clean_val not in ["[]", "()", "N/A", "None"]:
                    return True
            # Se la riga termina con ':' senza testo, controlla se c'è testo indented sulle righe successive
            sub_lines = block[m.end():].splitlines()
            for sl in sub_lines:
                sls = sl.strip()
                if not sls:
                    continue
                # Se la riga successiva è un'altra intestazione, domanda o opzione numerata, esci
                if sls.startswith("#") or re.match(r"^(?:Domanda\s+)?(?:[QDP]\d+|\d+[.)\-])", sls, re.IGNORECASE):
                    break
                if sls.startswith(("-", "*")):
                    # Se è un altro campo con etichetta chiave: valore, non è continuazione regia
                    if re.match(r"^[-*]\s*(?:\*\*)?[A-Za-z0-9_À-ÿ\s/'-]+(?:\*\*)?:", sls):
                        break
                    if sl.startswith(("  ", "\t")):
                        return True
                    break
                if sl.startswith(("  ", "\t")):
                    return True
                break

    return False

def extract_question_blocks(content: str):
    """
    Estrae le singole domande e i rispettivi blocchi di testo dal contenuto del questionario
    (supportando sia formato strutturato #### Q01 sia formato lineare Q1. / Q2a. / Domanda 1 / **Q1.**).
    """
    lines = content.splitlines()
    start_idx = 0
    end_idx = len(lines)

    for i, line in enumerate(lines):
        sl = line.strip()
        if re.match(r"^(?:#{2,3})\s+(?:\d+\.\s*)?(?:Testo Definitivo|Domande|Testo del Questionario|Quesiti|Questionario\b)", sl, re.IGNORECASE):
            start_idx = i + 1
            break

    search_start = start_idx if start_idx > 0 else 0
    for i in range(search_start, len(lines)):
        sl = lines[i].strip()
        if re.match(
            r"^##\s+(?:\d+\.\s*)?(?:Specifiche Riepilogative|Specifiche dei Filtri|Piano di Validazione|Piano di Monitoraggio|Adempimenti|Registro|Punti aperti|Approvazione Finale|Approvazione Umana|Note Conclusive)",
            sl,
            re.IGNORECASE,
        ):
            end_idx = i
            break

    target_lines = lines[start_idx:end_idx]

    questions = []
    current_qid = None
    current_block_lines = []

    struct_q_re = re.compile(
        r"^(?:#{2,4})\s+(?:\*\*)?(?:(?:Domanda\s+)([QDP]?\d+[a-zA-Z0-9_]*)|([QDP]\d+[a-zA-Z0-9_]*))(?:\*\*)?(?:\s*[-–—:.]\s*(.*))?$",
        re.IGNORECASE,
    )
    linear_q_re = re.compile(
        r"^\s*(?:\*\*)?(?:(?:Domanda\s+)([QDP]?\d+[a-zA-Z0-9_]*)|([QDP]\d+[a-zA-Z0-9_]*))(?:\*\*)?(?:[.:\-–—]\s*(?:\*\*)?|(?:\*\*)?[.:\-–—])\s+(.+)$",
        re.IGNORECASE,
    )

    for line in target_lines:
        sl = line.strip()
        if not sl or sl.startswith(("|", "---", "***", "___")):
            continue

        if re.match(r"^#{2,3}\s+(?:Sezione|Gruppo|Modulo)\b", sl, re.IGNORECASE):
            continue

        m_q = None
        if sl.startswith("#"):
            m_q = struct_q_re.match(sl)
        elif not re.match(r"^[-*]\s", sl):
            m_q = linear_q_re.match(sl)

        if m_q:
            if current_qid:
                questions.append((current_qid, "\n".join(current_block_lines)))
                current_block_lines = []
            raw_qid = (m_q.group(1) or m_q.group(2)).strip()
            current_qid = f"Q{raw_qid}" if raw_qid.isdigit() else raw_qid
            current_block_lines.append(sl)
        elif current_qid:
            current_block_lines.append(sl)

    if current_qid:
        questions.append((current_qid, "\n".join(current_block_lines)))

    return questions

def validate_questionnaire_file(path):
    issues = []
    path = Path(path)
    try:
        content = path.read_text(encoding="utf-8")
    except Exception as e:
        return [f"Impossibile leggere il file del questionario: {e}"]
        
    if not content.strip():
        return ["File del questionario vuoto o privo di contenuto"]
    
    # Check mandatory non-response codes
    if "97" not in content or "Non applicabile" not in content:
        issues.append("Codice 97 (Non applicabile) mancante o non specificato")
    if "98" not in content or "Non so" not in content:
        issues.append("Codice 98 (Non so) mancante o non specificato")
    if "99" not in content or ("Preferisco non rispondere" not in content and "Rifiuto" not in content):
        issues.append("Codice 99 (Rifiuto / Preferisco non rispondere) mancante o non specificato")

    # Verifica presenza delle note di regia / istruzioni di somministrazione per ciascun item
    q_items = extract_question_blocks(content)
    if not q_items:
        issues.append("Nessuna domanda identificata all'interno del questionario")
    else:
        for q_id, block in q_items:
            if not has_regia_instructions(block):
                issues.append(f"Domanda '{q_id}': istruzioni di regia o somministrazione mancanti o non specificate")
        
    return issues

def validate_methodology_file(path):
    issues = []
    path = Path(path)
    content = path.read_text(encoding="utf-8")
    
    # Check 11 columns in summary table
    table_headers = [
        "ID", "Costrutto", "Testo originale", "Modalita", 
        "Criticita e tipo non risposta a rischio", "Severita", 
        "Proposta raccomandata", "Nuove opzioni / filtri", 
        "Impatto durata", "Impatto comparabilita", "Decisione umana"
    ]
    for col in table_headers:
        if col not in content:
            issues.append(f"Colonna mancante nella griglia metodologica: '{col}'")
            
    # Check options A, B, C presence
    if "Opzione A" not in content:
        issues.append("Mancano le specifiche per 'Opzione A — Conservare'")
    if "Opzione B" not in content:
        issues.append("Mancano le specifiche per 'Opzione B — Modifica minima'")
    if "Opzione C" not in content:
        issues.append("Mancano le specifiche per 'Opzione C — Revisione sostanziale'")
        
    return issues

def validate_compliance_file(path):
    issues = []
    path = Path(path)
    content = path.read_text(encoding="utf-8")
    
    required_keywords = [
        "Art. 9", "GDPR", "identificazione", "Preferisco non rispondere"
    ]
    for kw in required_keywords:
        if kw not in content:
            issues.append(f"Parola chiave/controllo compliance mancante: '{kw}'")
            
    return issues

def validate_final_file(path):
    issues = []
    path = Path(path)
    try:
        content = path.read_text(encoding="utf-8")
    except Exception as e:
        return [f"Impossibile leggere il file del questionario finale: {e}"]

    if not content.strip():
        return ["File del questionario finale vuoto o privo di contenuto"]
    
    if "97" not in content:
        issues.append("Codice 97 mancante nel questionario finale")
    if "98" not in content:
        issues.append("Codice 98 mancante nel questionario finale")
    if "99" not in content:
        issues.append("Codice 99 mancante nel questionario finale")

    # Verifica presenza delle note di regia / istruzioni di somministrazione per ciascun item
    q_items = extract_question_blocks(content)
    if not q_items:
        issues.append("Nessuna domanda identificata all'interno del questionario finale")
    else:
        for q_id, block in q_items:
            if not has_regia_instructions(block):
                issues.append(f"Domanda '{q_id}': istruzioni di regia o somministrazione mancanti o non specificate")
        
    return issues

def validate_extracted_survey_file(path):
    """Valida la conformita formale di un artefatto di questionario storico estratto."""
    issues = []
    path = Path(path)
    try:
        content = path.read_text(encoding="utf-8")
    except Exception as e:
        return [f"Impossibile leggere il file di estrazione: {e}"]
        
    if not content.strip():
        return ["File di estrazione vuoto o privo di contenuto"]

    required_sections = [
        "## 1. Metadati dello Studio Estratto",
        "## 2. Inquadramento Metodologico e Aree Tematiche",
        "## 3. Inventario Strutturato delle Domande e Batterie Estratte",
        "## 4. Mappa delle Batterie Standard Identificate",
        "## 5. Note di Validazione Umana e Revisione",
    ]
    for s in required_sections:
        if s not in content:
            issues.append(f"Sezione mancante: '{s}'")

    required_meta = [
        "ID Studio / Nome Archivio:",
        "Committente originario:",
        "Popolazione di riferimento e Target:",
    ]
    for m in required_meta:
        if m not in content:
            issues.append(f"Metadato obbligatorio mancante: '{m}'")

    if "97" not in content or "Non applicabile" not in content:
        issues.append("Codice 97 (Non applicabile) mancante o non specificato")
    if "98" not in content or "Non so" not in content:
        issues.append("Codice 98 (Non so) mancante o non specificato")
    if "99" not in content or ("Preferisco non rispondere" not in content and "Rifiuto" not in content and "Rifiuta" not in content):
        issues.append("Codice 99 (Rifiuto / Preferisco non rispondere) mancante o non specificato")

    return issues

EXPECTED_LIMESURVEY_COLUMNS = [
    "id",
    "related_id",
    "class",
    "type/scale",
    "name",
    "relevance",
    "text",
    "help",
    "language",
    "validation",
    "mandatory",
    "other",
    "default",
    "same_default",
]

VALID_LIMESURVEY_CLASSES = {"S", "SL", "G", "Q", "SQ", "A"}
REQUIRED_LIMESURVEY_CLASSES = {"S", "SL", "G", "Q"}

def validate_limesurvey_file(path):
    """Valida la conformita formale del file LimeSurvey TSV a 14 colonne standard."""
    issues = []
    path = Path(path)
    try:
        content = path.read_text(encoding="utf-8")
    except Exception as e:
        return [f"Impossibile leggere il file LimeSurvey TSV: {e}"]
        
    lines = content.splitlines()
    while lines and lines[-1] == "":
        lines.pop()
        
    if not lines:
        return ["File LimeSurvey TSV vuoto o privo di righe"]
        
    header = lines[0].split("\t")
    if len(header) != 14:
        issues.append(f"Intestazione non conforme: trovate {len(header)} colonne anziché 14")
    elif header != EXPECTED_LIMESURVEY_COLUMNS:
        issues.append(f"Nomi delle colonne di intestazione non conformi allo standard LimeSurvey TSV: {header}")
        
    found_classes = set()
    for idx, line in enumerate(lines[1:], start=2):
        if not line:
            issues.append(f"Riga {idx}: riga vuota non ammessa nel file LimeSurvey TSV")
            continue

        cols = line.split("\t")
        if len(cols) != 14:
            issues.append(f"Riga {idx}: trovate {len(cols)} colonne anziché 14 (record '{cols[2] if len(cols) > 2 else 'sconosciuto'}')")
            continue
            
        rec_class = cols[2].strip()
        if not rec_class:
            issues.append(f"Riga {idx}: campo 'class' vuoto")
        elif rec_class not in VALID_LIMESURVEY_CLASSES:
            issues.append(f"Riga {idx}: classe '{rec_class}' non riconosciuta (classi ammesse: {sorted(VALID_LIMESURVEY_CLASSES)})")
        else:
            found_classes.add(rec_class)
            
    missing_classes = REQUIRED_LIMESURVEY_CLASSES - found_classes
    if missing_classes:
        issues.append(f"Classi strutturali minime mancanti nel tracciato LimeSurvey: {sorted(missing_classes)}")
        
    return issues

def validate_case(case_dir):
    case_dir = Path(case_dir)
    print(f"\n--- Validazione Caso: {case_dir.name} ---")
    case_issues = []
    
    status_file = case_dir / "status.md"
    if not status_file.exists():
        case_issues.append("File status.md mancante nel caso")
    else:
        errs = validate_status_file(status_file)
        if errs:
            case_issues.extend([f"status.md: {e}" for e in errs])

    brief_file = case_dir / "brief.md"
    if brief_file.exists():
        errs = validate_brief_file(brief_file)
        if errs:
            case_issues.extend([f"brief.md: {e}" for e in errs])
            
    q_file = case_dir / "questionnaire.md"
    if q_file.exists():
        errs = validate_questionnaire_file(q_file)
        if errs:
            case_issues.extend([f"questionnaire.md: {e}" for e in errs])
            
    m_file = case_dir / "methodology.md"
    if m_file.exists():
        errs = validate_methodology_file(m_file)
        if errs:
            case_issues.extend([f"methodology.md: {e}" for e in errs])
            
    c_file = case_dir / "compliance.md"
    if c_file.exists():
        errs = validate_compliance_file(c_file)
        if errs:
            case_issues.extend([f"compliance.md: {e}" for e in errs])
            
    f_file = case_dir / "final.md"
    if f_file.exists():
        errs = validate_final_file(f_file)
        if errs:
            case_issues.extend([f"final.md: {e}" for e in errs])

    ls_file = case_dir / "limesurvey_survey.txt"
    if ls_file.exists():
        errs = validate_limesurvey_file(ls_file)
        if errs:
            case_issues.extend([f"limesurvey_survey.txt: {e}" for e in errs])

    ext_file = case_dir / "extracted_survey.md"
    if ext_file.exists():
        errs = validate_extracted_survey_file(ext_file)
        if errs:
            case_issues.extend([f"extracted_survey.md: {e}" for e in errs])
            
    if case_issues:
        for err in case_issues:
            print(f"  [FAIL] {err}")
        return False
    else:
        print("  [PASS] Tutti i file presenti risultano conformi agli standard metodologici.")
        return True

def main():
    cases_to_check = []
    
    all_files_ok = True
    has_files = False

    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            p = Path(arg)
            if not p.is_absolute():
                candidate = (Path.cwd() / arg).resolve()
                if candidate.exists():
                    p = candidate
                else:
                    p = (ROOT_DIR / arg).resolve()
            if not p.exists():
                print(f"[FAIL] Percorso non trovato o non valido: '{arg}'")
                sys.exit(1)
            if p.is_file():
                has_files = True
                if p.name == "limesurvey_survey.txt" or p.suffix == ".txt":
                    errs = validate_limesurvey_file(p)
                    tipo = "LimeSurvey TSV"
                elif "extracted" in p.name:
                    errs = validate_extracted_survey_file(p)
                    tipo = "Estrazione Questionario"
                elif p.name == "brief.md" or "brief" in p.name:
                    errs = validate_brief_file(p)
                    tipo = "Brief di Ricerca"
                elif p.name == "questionnaire.md" or "questionnaire" in p.name:
                    errs = validate_questionnaire_file(p)
                    tipo = "Bozza Questionario"
                elif p.name == "final.md" or "final" in p.name:
                    errs = validate_final_file(p)
                    tipo = "Questionario Finale"
                elif p.name == "methodology.md" or "methodology" in p.name:
                    errs = validate_methodology_file(p)
                    tipo = "Audit Metodologico"
                elif p.name == "compliance.md" or "compliance" in p.name:
                    errs = validate_compliance_file(p)
                    tipo = "Screening Compliance"
                elif p.name == "status.md" or "status" in p.name:
                    errs = validate_status_file(p)
                    tipo = "Stato Avanzamento"
                else:
                    print(f"[FAIL] Tipo di file non riconosciuto per la validazione diretta: '{arg}'")
                    sys.exit(1)
                if errs:
                    for e in errs:
                        print(f"  [FAIL] {p.name}: {e}")
                    all_files_ok = False
                else:
                    print(f"  [PASS] {p.name} conforme allo standard ({tipo}).")
            else:
                cases_to_check.append(p)

        if has_files and not cases_to_check:
            sys.exit(0 if all_files_ok else 1)
    else:
        runs_dir = ROOT_DIR / "runs"
        cases_to_check = [d for d in runs_dir.iterdir() if d.is_dir() and not d.name.startswith(".")]
        
        if not cases_to_check:
            print("Nessun caso presente in runs/ da validare (cartella pulita o solo .gitkeep).")
            print("Per validare un caso specifico o un esempio: python scripts/validate_runs.py examples/demo_run_biblioteca")
            sys.exit(0)
        
    all_ok = True
    for c in cases_to_check:
        ok = validate_case(c)
        if not ok:
            all_ok = False
            
    if all_ok:
        print("\nTutti i casi esaminati sono conformi.")
        sys.exit(0)
    else:
        print("\nAlcuni casi presentano non-conformita formali.")
        sys.exit(1)

if __name__ == "__main__":
    main()
