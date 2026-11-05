#!/usr/bin/env python3
"""
Script di validazione della specularita e sincronizzazione architetturale
tra Google Antigravity (.agents/) e Claude Code (.claude/), AGENTS.md e CLAUDE.md.
"""

import os
import sys
import re
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

def check_global_rules():
    agents_md = ROOT_DIR / "AGENTS.md"
    claude_md = ROOT_DIR / "CLAUDE.md"
    
    if not agents_md.exists():
        return False, "AGENTS.md mancante"
    if not claude_md.exists():
        return False, "CLAUDE.md mancante"
        
    content_agents = agents_md.read_text(encoding="utf-8").replace("\r\n", "\n")
    content_claude = claude_md.read_text(encoding="utf-8").replace("\r\n", "\n")
    
    if content_agents != content_claude:
        return False, "AGENTS.md e CLAUDE.md non sono identici"
    return True, "AGENTS.md e CLAUDE.md perfettamente sincronizzati"

def parse_frontmatter(content):
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            return parts[1], parts[2].strip()
    return "", content.strip()

def check_agents():
    agents_dir = ROOT_DIR / ".agents" / "agents"
    claude_dir = ROOT_DIR / ".claude" / "agents"
    
    if not agents_dir.exists() or not claude_dir.exists():
        return False, "Cartella agents mancante in .agents o .claude"
        
    agents_files = {f.name for f in agents_dir.glob("*.md")}
    claude_files = {f.name for f in claude_dir.glob("*.md")}
    
    if agents_files != claude_files:
        diff1 = agents_files - claude_files
        diff2 = claude_files - agents_files
        return False, f"Disallineamento file agenti: solo in .agents={diff1}, solo in .claude={diff2}"
        
    mismatches = []
    for fname in sorted(agents_files):
        c_ant = (agents_dir / fname).read_text(encoding="utf-8")
        c_cld = (claude_dir / fname).read_text(encoding="utf-8")
        
        _, body_ant = parse_frontmatter(c_ant)
        _, body_cld = parse_frontmatter(c_cld)
        
        # Normalize newlines
        body_ant = body_ant.replace("\r\n", "\n")
        body_cld = body_cld.replace("\r\n", "\n")
        
        if body_ant != body_cld:
            mismatches.append(fname)
            
    if mismatches:
        return False, f"Corpo testo disallineato negli agenti: {mismatches}"
    return True, f"Tutti i {len(agents_files)} agenti sono allineati nel corpo operativo"

def check_skills():
    agents_skills_dir = ROOT_DIR / ".agents" / "skills"
    claude_skills_dir = ROOT_DIR / ".claude" / "skills"
    
    if not agents_skills_dir.exists() or not claude_skills_dir.exists():
        return False, "Cartella skills mancante in .agents o .claude"
        
    skills_ant = {d.name for d in agents_skills_dir.iterdir() if d.is_dir()}
    skills_cld = {d.name for d in claude_skills_dir.iterdir() if d.is_dir()}
    
    expected_skills = [
        "noto-survey-pipeline",
        "noto-brief-structuring",
        "noto-questionnaire-drafting",
        "noto-methodology-audit",
        "noto-compliance-check",
        "noto-questionnaire-consolidation",
        "noto-survey-extractor",
    ]
    missing_ant = set(expected_skills) - skills_ant
    missing_cld = set(expected_skills) - skills_cld
    if missing_ant or missing_cld:
        return False, f"Skill attese mancanti: .agents={missing_ant}, .claude={missing_cld}"
        
    unexpected_ant = skills_ant - set(expected_skills)
    unexpected_cld = skills_cld - set(expected_skills)
    if unexpected_ant or unexpected_cld:
        return False, f"Skill non censite o inattese: .agents={unexpected_ant}, .claude={unexpected_cld}"
        
    if skills_ant != skills_cld:
        return False, f"Disallineamento cartelle skill: {skills_ant ^ skills_cld}"
        
    mismatches = []
    for skill_name in sorted(skills_ant):
        f_ant = agents_skills_dir / skill_name / "SKILL.md"
        f_cld = claude_skills_dir / skill_name / "SKILL.md"
        
        if not f_ant.exists():
            mismatches.append(f"{skill_name} manca in .agents")
            continue
        if not f_cld.exists():
            mismatches.append(f"{skill_name} manca in .claude")
            continue
            
        c_ant = f_ant.read_text(encoding="utf-8").replace("\r\n", "\n")
        c_cld = f_cld.read_text(encoding="utf-8").replace("\r\n", "\n")
        
        if c_ant != c_cld:
            mismatches.append(f"{skill_name} (contenuto differente)")
            
    if mismatches:
        return False, f"Disallineamento file SKILL.md: {mismatches}"
    return True, f"Tutte le {len(skills_ant)} skill sono perfettamente identiche"

def check_workflows_commands():
    wf_dir = ROOT_DIR / ".agents" / "workflows"
    cmd_dir = ROOT_DIR / ".claude" / "commands"
    
    if not wf_dir.exists() or not cmd_dir.exists():
        return False, "Cartella workflows o commands mancante"
        
    wf_files = {f.name for f in wf_dir.glob("*.md")}
    cmd_files = {f.name for f in cmd_dir.glob("*.md")}
    
    if wf_files != cmd_files:
        return False, f"Disallineamento nomi: workflows={wf_files}, commands={cmd_files}"
        
    mismatches = []
    for fname in sorted(wf_files):
        c_wf = (wf_dir / fname).read_text(encoding="utf-8").replace("\r\n", "\n")
        c_cmd = (cmd_dir / fname).read_text(encoding="utf-8").replace("\r\n", "\n")
        if c_wf != c_cmd:
            mismatches.append(fname)
            
    if mismatches:
        return False, f"Contenuto disallineato tra workflow e comandi: {mismatches}"
        
    return True, f"Tutti i {len(wf_files)} flussi/comandi corrispondono per nome e contenuto"

def check_templates():
    templates_dir = ROOT_DIR / "templates"
    expected = [
        "status_template.md",
        "brief_template.md",
        "questionnaire_template.md",
        "methodology_template.md",
        "compliance_template.md",
        "final_template.md",
        "extracted_survey_template.md",
    ]
    missing = [t for t in expected if not (templates_dir / t).exists()]
    if missing:
        return False, f"Template mancanti: {missing}"
    templates_found = [f.name for f in templates_dir.glob("*.md")]
    unexpected = set(templates_found) - set(expected)
    if unexpected:
        return False, f"Template non previsti in templates/: {unexpected}"
    return True, f"Tutti i {len(expected)} template obbligatori sono presenti"

def main():
    print("=== Verifica Sincronizzazione Architetturale Noto Sondaggi ===")
    checks = [
        ("Regole Globali (AGENTS.md / CLAUDE.md)", check_global_rules),
        ("Agenti (.agents/agents vs .claude/agents)", check_agents),
        ("Skill (.agents/skills vs .claude/skills)", check_skills),
        ("Workflow / Comandi (.agents/workflows vs .claude/commands)", check_workflows_commands),
        ("Template Obbligatori (templates/)", check_templates),
    ]
    
    all_ok = True
    for name, fn in checks:
        ok, msg = fn()
        status = "OK" if ok else "ERRORE"
        print(f"[{status}] {name}: {msg}")
        if not ok:
            all_ok = False
            
    if all_ok:
        print("\nRISULTATO: Architettura speculare integra al 100%.")
        sys.exit(0)
    else:
        print("\nRISULTATO: Trovati disallineamenti o problemi architetturali.")
        sys.exit(1)

if __name__ == "__main__":
    main()
