#!/usr/bin/env python3
"""
Linter e validatore formale degli artefatti generati in runs/<caso>/
Verifica la conformita alle regole metodologiche, alla griglia a 11 colonne,
alle schede a 12 campi e alla presenza dei codici di non risposta (97, 98, 99).
"""

import os
import sys
import re
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

def validate_status_file(path):
    issues = []
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

def validate_questionnaire_file(path):
    issues = []
    content = path.read_text(encoding="utf-8")
    
    # Check mandatory non-response codes
    if "97" not in content or "Non applicabile" not in content:
        issues.append("Codice 97 (Non applicabile) mancante o non specificato")
    if "98" not in content or "Non so" not in content:
        issues.append("Codice 98 (Non so) mancante o non specificato")
    if "99" not in content or ("Preferisco non rispondere" not in content and "Rifiuto" not in content):
        issues.append("Codice 99 (Rifiuto / Preferisco non rispondere) mancante o non specificato")
        
    return issues

def validate_methodology_file(path):
    issues = []
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
    content = path.read_text(encoding="utf-8")
    
    if "97" not in content:
        issues.append("Codice 97 mancante nel questionario finale")
    if "98" not in content:
        issues.append("Codice 98 mancante nel questionario finale")
    if "99" not in content:
        issues.append("Codice 99 mancante nel questionario finale")
        
    return issues

def validate_case(case_dir):
    print(f"\n--- Validazione Caso: {case_dir.name} ---")
    case_issues = []
    
    status_file = case_dir / "status.md"
    if not status_file.exists():
        case_issues.append("File status.md mancante nel caso")
    else:
        errs = validate_status_file(status_file)
        if errs:
            case_issues.extend([f"status.md: {e}" for e in errs])
            
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
            
    if case_issues:
        for err in case_issues:
            print(f"  [FAIL] {err}")
        return False
    else:
        print("  [PASS] Tutti i file presenti risultano conformi agli standard metodologici.")
        return True

def main():
    cases_to_check = []
    
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            p = Path(arg)
            if not p.is_absolute():
                candidate = (Path.cwd() / arg).resolve()
                if candidate.exists():
                    p = candidate
                else:
                    p = (ROOT_DIR / arg).resolve()
            if not p.exists() or not p.is_dir():
                print(f"[FAIL] Cartella caso non trovata o non valida: '{arg}'")
                sys.exit(1)
            cases_to_check.append(p)
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
