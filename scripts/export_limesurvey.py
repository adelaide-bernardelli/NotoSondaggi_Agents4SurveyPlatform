#!/usr/bin/env python3
"""
export_limesurvey.py — Generatore di struttura questionario per LimeSurvey (TSV a 14 colonne)

Legge un file markdown di questionario consolidato (formato lineare come in examples/demo_run_biblioteca/final.md
oppure formato strutturato a sezioni/skip logic come in templates/final_template.md) e produce un file .txt
tab-delimited conforme alle specifiche ufficiali di LimeSurvey a 14 colonne standard:
id, related_id, class, type/scale, name, relevance, text, help, language, validation, mandatory, other, default, same_default.

Classi gestite:
- S: parametri globali dell'indagine
- SL: parametri di localizzazione e testi (titolo, descrizione, benvenuto, chiusura)
- G: gruppi/sezioni
- Q: domande (L, M, T, S, N, F, 5)
- SQ: sotto-domande (per batterie a matrice e scelte multiple)
- A: opzioni di risposta per liste radio e scale di batterie

Codici standard di non risposta:
- 97: Non applicabile
- 98: Non so / Non conosco
- 99: Preferisco non rispondere / Rifiuto
"""

import argparse
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

TSV_COLUMNS = [
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

STANDARD_NONRESPONSE_CODES = {
    "97": "Non applicabile",
    "98": "Non so",
    "99": "Preferisco non rispondere",
}


@dataclass
class AnswerOption:
    code: str
    text: str


@dataclass
class SubQuestion:
    code: str
    text: str


@dataclass
class Question:
    name: str
    text: str
    q_type: str = "L"
    help_text: str = ""
    relevance: str = "1"
    mandatory: str = "Y"
    other: str = "N"
    validation: str = ""
    default: str = ""
    same_default: str = ""
    options: List[AnswerOption] = field(default_factory=list)
    subquestions: List[SubQuestion] = field(default_factory=list)


@dataclass
class Group:
    name: str
    text: str
    help_text: str = ""
    relevance: str = "1"
    questions: List[Question] = field(default_factory=list)


@dataclass
class Survey:
    title: str = "Indagine Noto Sondaggi"
    description: str = ""
    welcome_text: str = ""
    end_text: str = "Grazie per aver completato il questionario per Noto Sondaggi."
    language: str = "it"
    groups: List[Group] = field(default_factory=list)


def clean_markdown_text(raw_text: str) -> str:
    """Rimuove formattazione markdown superficiale e normalizza per TSV."""
    if not raw_text:
        return ""
    text = raw_text.strip()
    # Rimuove apici o virgolette avvolgenti
    if (text.startswith('"') and text.endswith('"')) or (text.startswith("'") and text.endswith("'")):
        text = text[1:-1].strip()
    # Rimuove grassetti/corsivi di apertura/chiusura se avvolgenti
    text = re.sub(r'^\*{1,2}(.*?)\*{1,2}$', r'\1', text).strip()
    # Rimuove backticks
    text = text.replace("`", "")
    # Sostituisce tab interni con spazi per preservare integrità TSV
    text = text.replace("\t", " ")
    # Sostituisce ritorni a capo con tag HTML <br /> se testo lungo
    text = re.sub(r'[\r\n]+', '<br />', text)
    # Collassa spazi multipli
    text = re.sub(r'\s{2,}', ' ', text)
    return text.strip()


def translate_relevance(rule_text: str) -> str:
    """
    Traduce condizioni condizionali e filtri in ExpressionScript LimeSurvey.
    Preserva rigorosamente espressioni ExpressionScript preesistenti o già dotate di .NAOK.

    Esempi:
    - 'Solo se Q01 == 1'         -> 'Q01.NAOK == "1"'
    - 'Solo se Q01 = 1'          -> 'Q01.NAOK == "1"'
    - 'Se Q01 in (1, 2)'         -> '(Q01.NAOK == "1" || Q01.NAOK == "2")'
    - 'Se Q01 != 99'             -> 'Q01.NAOK != "99"'
    - 'Q01 == 1 oppure Q02 == 2' -> '(Q01.NAOK == "1" || Q02.NAOK == "2")'
    - 'Q01.NAOK == "1"'          -> 'Q01.NAOK == "1"' (preserva ExpressionScript valido)
    - '!is_empty(Q02)'           -> '!is_empty(Q02)'
    - 'Nessuno' / ''             -> '1'
    """
    if not rule_text:
        return "1"

    clean = rule_text.strip()
    clean_lower = clean.lower()

    # Casi di nessun filtro / mostra a tutti
    if any(clean_lower.startswith(x) for x in ["nessun", "tutti", "tutto", "-", "none", "no"]):
        return "1"
    if clean_lower in [
        "nessuno",
        "nessuno (tutti i rispondenti)",
        "tutti i rispondenti",
        "tutti",
        "nessun filtro",
        "mostrare a tutto il campione",
    ]:
        return "1"

    # Se l'espressione contiene già .NAOK, non alterarla né rimapparla (evita NAOK.NAOK)
    if ".naok" in clean_lower:
        return clean

    # Se è già ExpressionScript avanzato con funzioni di sistema
    if any(fn in clean_lower for fn in ["is_empty(", "count(", "that.", "regexmatch(", "sum("]):
        return clean

    # Pattern: Qxx / Dxx / Pxx in (1, 2, 3) oppure tra (1, 2)
    in_match = re.search(r'([A-Za-z0-9_]+)\s+(?:in|tra)\s*\(([^)]+)\)', clean, re.IGNORECASE)
    if in_match:
        q_code = in_match.group(1)
        vals = [v.strip().strip("'\"") for v in in_match.group(2).split(",")]
        sub_exprs = [f'{q_code}.NAOK == "{v}"' for v in vals if v]
        if sub_exprs:
            return "(" + " || ".join(sub_exprs) + ")"

    # Pattern: confronti multipli o singoli (es. Q01 = 1, Q01 == 2, Q01 != 99, D01 == "Sì")
    # Supporta caratteri accentati e valori testuali
    comp_matches = list(
        re.finditer(
            r'([A-Za-z0-9_]+)\s*(==|=|!=|<>|<=|>=|<|>)\s*([0-9a-zA-Z_\u00C0-\u017F"\']+)',
            clean,
        )
    )
    if comp_matches:
        # Rileva disgiunzioni (o, oppure, or, ||) vs congiunzioni (e, ed, and, &&)
        is_or = bool(re.search(r'\b(?:o|oppure|or)\b|\|\|', clean_lower))
        op = " || " if is_or else " && "

        parts = []
        for m in comp_matches:
            q_code = m.group(1)
            cmp_op = m.group(2)
            val = m.group(3).strip("'\"")
            if cmp_op == "=":
                cmp_op = "=="
            elif cmp_op == "<>":
                cmp_op = "!="
            parts.append(f'{q_code}.NAOK {cmp_op} "{val}"')

        if len(parts) == 1:
            return parts[0]
        else:
            return f"({op.join(parts)})"

    # Fallback su menzione di un codice domanda (Qxx/Dxx/Pxx) e un valore numerico
    fallback = re.search(r'\b([QDP]\d+[a-zA-Z0-9_]*)\b[^0-9]*([0-9]+)', clean, re.IGNORECASE)
    if fallback:
        return f'{fallback.group(1)}.NAOK == "{fallback.group(2)}"'

    fallback_rev = re.search(r'([0-9]+)[^0-9]*?\b([QDP]\d+[a-zA-Z0-9_]*)\b', clean, re.IGNORECASE)
    if fallback_rev:
        return f'{fallback_rev.group(2)}.NAOK == "{fallback_rev.group(1)}"'

    return "1"


def map_question_type(type_str: str, has_subquestions: bool = False, has_options: bool = True) -> str:
    """Mappa la descrizione del tipo domanda al codice LimeSurvey corrispondente."""
    if not type_str:
        if has_subquestions:
            return "F"
        return "L" if has_options else "T"

    t = type_str.lower()
    if "multipl" in t or t == "m":
        return "M"
    if any(k in t for k in ["batteria", "matrice", "array", "griglia"]) or t == "f":
        return "F"
    if any(k in t for k in ["aperta", "long", "esteso", "parere", "commento", "testo libero"]) or t == "t":
        return "T"
    if any(k in t for k in ["breve", "short"]) or t == "s":
        return "S"
    if any(k in t for k in ["numeric", "numero", "quantitativ"]) or t == "n":
        return "N"
    if "5 punt" in t or t == "5":
        return "5"
    if any(k in t for k in ["singol", "radio", "ordinale", "likert", "scelta singola"]) or t == "l":
        return "L"
    if "dropdown" in t or "tendina" in t or t == "!":
        return "!"

    if has_subquestions:
        return "F"
    return "L" if has_options else "T"


def parse_option_line(line: str) -> Optional[Tuple[str, str]]:
    """
    Riconosce una linea come opzione di risposta numerata o codificata.
    Supporta:
    - 1. Molto soddisfatto
    - - 1 = Molto soddisfatto
    - - 1. Molto soddisfatto
    - - `97` = Non applicabile
    - 98. Non so
    - - [99] Preferisco non rispondere
    - SQ01 = Item 1
    """
    stripped = line.strip()
    if not stripped or stripped.startswith("#"):
        return None

    # Regex per catturare (codice, etichetta)
    pattern = r'^(?:[-*]\s*)?(?:[`"\'\[\(]?([0-9a-zA-Z_]+)[`"\'\]\)]?\s*(?:[=.:)\-–—]|\s*=\s*)\s*)(.+)$'
    m = re.match(pattern, stripped)
    if m:
        code = m.group(1).strip()
        text = clean_markdown_text(m.group(2))
        if code and text:
            return code, text

    return None


def parse_inline_options(line: str) -> List[Tuple[str, str]]:
    """Estrae opzioni multiple separate da virgola su singola riga (es. '1=Sì, 2=No, 98=Non so')."""
    results = []
    parts = [p.strip() for p in line.split(",") if p.strip()]
    for p in parts:
        opt = parse_option_line(p)
        if opt:
            results.append(opt)
    return results


def parse_questionnaire_markdown(content: str, default_lang: str = "it") -> Survey:
    """
    Parser robusto per questionari consolidati e bozze:
    - Formato lineare (demo_run_biblioteca/final.md)
    - Formato strutturato a sezioni tematiche e skip logic (templates/final_template.md)
    - Gestione codici standard 97, 98, 99
    - Istruzioni di regia / help text multi-riga
    - Prefissi domanda standard italiani (Q, D, P)
    """
    lines = content.splitlines()
    survey = Survey(language=default_lang)

    # 1. Estrazione metadati globali (titolo, welcome text, descrizione)
    for line in lines:
        sl = line.strip()
        if not survey.title or survey.title == "Indagine Noto Sondaggi":
            m_title = re.match(r'^#\s+(.+)$', sl)
            if m_title:
                survey.title = clean_markdown_text(m_title.group(1).strip())

        # Estrazione welcome text dall'informativa o introduzione
        if not survey.welcome_text:
            m_welcome = re.match(
                r'^[-*]\s*(?:\*\*)?(?:Testo introduttivo.*|Testo di presentazione.*|Informativa.*)(?:\*\*)?:\s*(.+)$',
                sl,
                re.IGNORECASE,
            )
            if m_welcome:
                survey.welcome_text = clean_markdown_text(m_welcome.group(1))

        # Estrazione caso / descrizione
        if not survey.description:
            m_case = re.match(r'^[-*]\s*(?:\*\*)?(?:ID Caso|Caso)(?:\*\*)?:\s*(.+)$', sl, re.IGNORECASE)
            if m_case:
                case_name = clean_markdown_text(m_case.group(1))
                survey.description = f"Indagine Noto Sondaggi — Caso: {case_name}"

    # 2. Individuazione della sezione contenente le domande
    start_idx = 0
    end_idx = len(lines)

    for i, line in enumerate(lines):
        sl = line.strip()
        if re.search(r'^(?:#{2,3})\s+(?:\d+\.\s*)?(?:Testo Definitivo|Domande)', sl, re.IGNORECASE):
            start_idx = i + 1
            break

    # Ricerca di una successiva intestazione H2 che chiuda la sezione domande
    # (es. "## 5. Specifiche...", "## Specifiche Riepilogative...", "## Note...")
    if start_idx > 0:
        for i in range(start_idx, len(lines)):
            sl = lines[i].strip()
            if re.match(
                r'^(?:##\s+(?:\d+\.\s*)?(?:Specifiche|Piano|Adempimenti|Registro|Punti|Approvazione|Note)|##\s+[0-9]+\.(?!\s*(?:Sezione|Gruppo|Modulo)))',
                sl,
                re.IGNORECASE,
            ):
                end_idx = i
                break

    target_lines = lines[start_idx:end_idx]

    # 3. Parsing a stati di gruppi, domande, opzioni e attributi
    current_group: Optional[Group] = None
    current_question: Optional[Question] = None
    current_section_mode: Optional[str] = None  # "options", "exit_codes", "subquestions", "help"
    group_counter = 1

    def ensure_group():
        nonlocal current_group, group_counter
        if current_group is None:
            g_name = f"G{group_counter:02d}"
            current_group = Group(name=g_name, text="Domande Principali")
            survey.groups.append(current_group)
            group_counter += 1
        return current_group

    for line in target_lines:
        stripped = line.strip()
        if not stripped:
            continue

        # Separatore markdown orizzontale
        if stripped in ["---", "***", "___"]:
            continue

        # A. Rilevazione di un nuovo Gruppo / Sezione
        m_grp = re.match(
            r'^(?:#{2,3})\s+(?:(?:\d+\.\s*)?(?:Sezione|Gruppo|Modulo)\s*([A-Za-z0-9_]*)\s*[-–—:]\s*(.+)|(?:Sezione|Gruppo|Modulo)\s+([A-Za-z0-9_]+.*))$',
            stripped,
            re.IGNORECASE,
        )
        if m_grp:
            g_code = f"G{group_counter:02d}"
            g_title = clean_markdown_text(stripped.lstrip("#").strip())
            current_group = Group(name=g_code, text=g_title)
            survey.groups.append(current_group)
            group_counter += 1
            current_question = None
            current_section_mode = None
            continue

        # B. Rilevazione di una Domanda Strutturata (#### Q01 ..., ### D01 ..., #### P01 ...)
        m_q_struct = re.match(
            r'^(?:#{2,4})\s+(?:\*\*)?(?:(?:Domanda\s+)([QDP]?\d+[a-zA-Z0-9_]*)|([QDP]\d+[a-zA-Z0-9_]*))(?:\*\*)?(?:\s*[-–—:.]\s*(.*))?$',
            stripped,
            re.IGNORECASE,
        )
        if m_q_struct:
            grp = ensure_group()
            raw_q_code = (m_q_struct.group(1) or m_q_struct.group(2)).strip()
            q_code = f"Q{raw_q_code}" if raw_q_code.isdigit() else raw_q_code
            q_label = (m_q_struct.group(3) or "").strip()
            clean_label = re.sub(r'^\s*\[.*?\]\s*', '', q_label).strip()
            initial_text = clean_markdown_text(clean_label if clean_label else q_label)
            current_question = Question(name=q_code, text=initial_text)
            grp.questions.append(current_question)
            current_section_mode = None
            continue

        # C. Rilevazione di una Domanda Lineare (es. Q1. Come valuta..., D2a: ...)
        m_q_linear = re.match(
            r'^\s*(?:\*\*)?(?:(?:Domanda\s+)([QDP]?\d+[a-zA-Z0-9_]*)|([QDP]\d+[a-zA-Z0-9_]*))(?:\*\*)?(?:[.:\-–—]\s*(?:\*\*)?|(?:\*\*)?[.:\-–—])\s+(.+)$',
            stripped,
            re.IGNORECASE,
        )
        if m_q_linear and not re.match(r"^[-*]\s", stripped):
            grp = ensure_group()
            raw_q_code = (m_q_linear.group(1) or m_q_linear.group(2)).strip()
            q_code = f"Q{raw_q_code}" if raw_q_code.isdigit() else raw_q_code
            q_text = clean_markdown_text(m_q_linear.group(3))
            current_question = Question(name=q_code, text=q_text, q_type="L")
            grp.questions.append(current_question)
            current_section_mode = "options"
            continue

        # D. Se siamo all'interno di una domanda, parsing degli attributi strutturati
        if current_question:
            # Testo per il rispondente
            m_text = re.match(
                r'^[-*]\s*(?:\*\*)?Testo per (?:il )?rispondente(?:\*\*)?:\s*(.*)$',
                stripped,
                re.IGNORECASE,
            )
            if m_text:
                explicit_text = clean_markdown_text(m_text.group(1))
                if explicit_text:
                    current_question.text = explicit_text
                current_section_mode = None
                continue

            # Tipo di domanda
            m_type = re.match(
                r'^[-*]\s*(?:\*\*)?Tipo di domanda(?:\*\*)?:\s*(.*)$',
                stripped,
                re.IGNORECASE,
            )
            if m_type:
                raw_type = clean_markdown_text(m_type.group(1))
                current_question.q_type = map_question_type(raw_type)
                if current_question.q_type in ["T", "S"]:
                    current_question.mandatory = "N"
                current_section_mode = None
                continue

            # Indicazione di obbligatorietà esplicita
            m_mand = re.match(
                r'^[-*]\s*(?:\*\*)?(?:Obbligatorietà|Obbligatoria|Mandatory)(?:\*\*)?:\s*(.*)$',
                stripped,
                re.IGNORECASE,
            )
            if m_mand:
                raw_m = clean_markdown_text(m_mand.group(1)).lower()
                current_question.mandatory = "N" if any(w in raw_m for w in ["no", "facoltativ", "n"]) else "Y"
                current_section_mode = None
                continue

            # Regola di filtro / skip
            m_skip = re.match(
                r'^[-*]\s*(?:\*\*)?(?:Regola di filtro\s*/\s*skip|Filtro\s*/\s*skip|Filtro)(?:\*\*)?:\s*(.*)$',
                stripped,
                re.IGNORECASE,
            )
            if m_skip:
                raw_rule = clean_markdown_text(m_skip.group(1))
                current_question.relevance = translate_relevance(raw_rule)
                current_section_mode = None
                continue

            # Istruzioni per intervistatore / help text
            m_help = re.match(
                r'^[-*]\s*(?:\*\*)?(?:Istruzioni(?:\s+di\s+regia(?:\s+e\s+somministrazione)?|\s+per\s+(?:l[\'’])?intervistatore|\s+di\s+somministrazione|\s+generali|\s+intervistatore)?|Not[ae]\s+(?:di\s+regia|per\s+(?:l[\'’])?intervistatore|intervistatore))[^*:]*(?:\*\*)?:?\s*(.*)$',
                stripped,
                re.IGNORECASE,
            )
            if m_help:
                inline_help = clean_markdown_text(m_help.group(1))
                if inline_help:
                    current_question.help_text = inline_help
                current_section_mode = "help"
                continue

            # Sezione opzioni e codici di risposta
            m_opts_hdr = re.match(
                r'^[-*]\s*(?:\*\*)?Opzioni e codici(?: di risposta)?(?:\*\*)?:?\s*(.*)$',
                stripped,
                re.IGNORECASE,
            )
            if m_opts_hdr:
                current_section_mode = "options"
                inline_part = m_opts_hdr.group(1).strip()
                if inline_part:
                    inline_opts = parse_inline_options(inline_part)
                    for c, t in inline_opts:
                        current_question.options.append(AnswerOption(code=c, text=t))
                continue

            # Sezione codici distinti di uscita
            m_exit_hdr = re.match(
                r'^[-*]\s*(?:\*\*)?(?:Codici distinti di uscita|Non so\s*/\s*rifiuto.*)(?:\*\*)?:?\s*(.*)$',
                stripped,
                re.IGNORECASE,
            )
            if m_exit_hdr:
                current_section_mode = "exit_codes"
                inline_part = m_exit_hdr.group(1).strip()
                if inline_part:
                    inline_opts = parse_inline_options(inline_part)
                    for c, t in inline_opts:
                        current_question.options.append(AnswerOption(code=c, text=t))
                continue

            # Sezione item batteria / sotto-domande
            if re.match(
                r'^[-*]\s*(?:\*\*)?(?:Item della batteria|Item|Sotto-domande|Sottodomande|Affermazioni)(?:\*\*)?:?',
                stripped,
                re.IGNORECASE,
            ):
                current_section_mode = "subquestions"
                if current_question.q_type == "L":
                    current_question.q_type = "F"
                continue

            # Parsing di una riga opzione o sotto-domanda codificata
            opt_data = parse_option_line(stripped)
            if opt_data:
                code, label = opt_data
                if code in STANDARD_NONRESPONSE_CODES and (not label or label.lower() in ["standard", "default"]):
                    label = STANDARD_NONRESPONSE_CODES[code]

                if current_section_mode == "subquestions" or (
                    current_question.q_type == "F"
                    and current_section_mode not in ["options", "exit_codes"]
                ):
                    current_question.subquestions.append(SubQuestion(code=code, text=label))
                else:
                    existing_codes = {o.code for o in current_question.options}
                    if code not in existing_codes:
                        current_question.options.append(AnswerOption(code=code, text=label))
                continue

            # Bullet aggiuntivo per istruzioni intervistatore multi-linea
            if current_section_mode == "help" and stripped.startswith(("-", "*")):
                if re.match(r"^[-*]\s*(?:\*\*)?[A-Za-z0-9_À-ÿ\s/'-]+(?:\*\*)?:", stripped):
                    current_section_mode = None
                else:
                    help_line = clean_markdown_text(re.sub(r'^[-*]\s*', '', stripped))
                    if help_line:
                        current_question.help_text = (current_question.help_text + " " + help_line).strip()
                    continue

            # Opzione non numerata sotto sezione opzioni/uscite (auto-assegnazione codice)
            if current_section_mode in ["options", "exit_codes"] and stripped.startswith(("-", "*")):
                opt_label = clean_markdown_text(re.sub(r'^[-*]\s*', '', stripped))
                if opt_label:
                    lbl_lower = opt_label.lower()
                    if "non applicabile" in lbl_lower:
                        auto_code = "97"
                    elif any(w in lbl_lower for w in ["non so", "non ricordo", "non conosce"]):
                        auto_code = "98"
                    elif any(w in lbl_lower for w in ["rifiut", "preferisco non"]):
                        auto_code = "99"
                    else:
                        num_codes = [int(o.code) for o in current_question.options if o.code.isdigit() and int(o.code) < 90]
                        auto_code = str(max(num_codes) + 1 if num_codes else len(current_question.options) + 1)

                    existing_codes = {o.code for o in current_question.options}
                    if auto_code not in existing_codes:
                        current_question.options.append(AnswerOption(code=auto_code, text=opt_label))
                continue

            # Note di regia inline tra parentesi quadre
            if stripped.startswith("[") and stripped.endswith("]"):
                note = clean_markdown_text(stripped[1:-1])
                current_question.help_text = (current_question.help_text + " " + note).strip()
                continue

            # Continuazione testo domanda se prima delle opzioni
            if (
                not current_question.options
                and not current_question.subquestions
                and not stripped.startswith(("-", "#"))
            ):
                extra = clean_markdown_text(stripped)
                if extra:
                    current_question.text = (current_question.text + " " + extra).strip()

    # Normalizzazione finale delle domande (coerenza tipo/opzioni)
    for g in survey.groups:
        for q in g.questions:
            # Se è marcata come lista radio ma ha solo sotto-domande e nessuna risposta, è una batteria
            if q.q_type == "L" and not q.options and q.subquestions:
                q.q_type = "F"
            # Se è marcata come lista radio ma non ha alcuna opzione di risposta, ricade su testo aperto
            elif q.q_type in ["L", "!"] and not q.options and not q.subquestions:
                q.q_type = "T"
                q.mandatory = "N"

    # Rimuove gruppi vuoti se presenti
    survey.groups = [g for g in survey.groups if g.questions]

    return survey


def generate_tsv_records(survey: Survey) -> List[List[str]]:
    """
    Produce la lista ordinata di record a 14 colonne conforme al formato LimeSurvey.
    Colonne:
    id, related_id, class, type/scale, name, relevance, text, help, language, validation, mandatory, other, default, same_default
    """
    records: List[List[str]] = []
    lang = survey.language or "it"

    # Intestazione TSV ufficiale obbligatoria
    records.append(list(TSV_COLUMNS))

    def make_row(
        r_id="",
        r_related_id="",
        r_class="",
        r_type_scale="",
        r_name="",
        r_relevance="",
        r_text="",
        r_help="",
        r_language="",
        r_validation="",
        r_mandatory="",
        r_other="",
        r_default="",
        r_same_default="",
    ) -> List[str]:
        return [
            str(r_id),
            str(r_related_id),
            str(r_class),
            str(r_type_scale),
            str(r_name),
            str(r_relevance),
            str(r_text),
            str(r_help),
            str(r_language),
            str(r_validation),
            str(r_mandatory),
            str(r_other),
            str(r_default),
            str(r_same_default),
        ]

    # 1. Parametri Globali Indagine (class = S)
    records.append(make_row(r_class="S", r_name="language", r_text=lang))
    records.append(make_row(r_class="S", r_name="format", r_text="G"))  # Group-by-group
    records.append(make_row(r_class="S", r_name="template", r_text="fruity"))
    records.append(make_row(r_class="S", r_name="anonymized", r_text="N"))
    records.append(make_row(r_class="S", r_name="savetimings", r_text="Y"))
    records.append(make_row(r_class="S", r_name="datestamp", r_text="Y"))
    records.append(make_row(r_class="S", r_name="ipaddr", r_text="N"))  # GDPR minimizzazione
    records.append(make_row(r_class="S", r_name="refurl", r_text="N"))
    records.append(make_row(r_class="S", r_name="active", r_text="N"))

    # 2. Parametri Lingua Indagine (class = SL)
    survey_desc = survey.description or f"Questionario di ricerca conforme agli standard Noto Sondaggi ({survey.title})"
    welcome = survey.welcome_text or f"Gentile partecipante, la invitiamo a compilare la seguente indagine: {survey.title}."
    records.append(make_row(r_class="SL", r_name="surveyls_title", r_text=survey.title, r_language=lang))
    records.append(make_row(r_class="SL", r_name="surveyls_description", r_text=survey_desc, r_language=lang))
    records.append(make_row(r_class="SL", r_name="surveyls_welcometext", r_text=welcome, r_language=lang))
    records.append(make_row(r_class="SL", r_name="surveyls_endtext", r_text=survey.end_text, r_language=lang))

    # 3. Gerarchia Gruppi (G) -> Domande (Q) -> Sotto-domande (SQ) / Risposte (A)
    entity_id_counter = 1

    for group in survey.groups:
        group_id = entity_id_counter
        entity_id_counter += 1

        records.append(
            make_row(
                r_id=group_id,
                r_related_id="0",
                r_class="G",
                r_name=group.name,
                r_relevance=group.relevance or "1",
                r_text=group.text,
                r_help=group.help_text,
                r_language=lang,
            )
        )

        for q in group.questions:
            q_id = entity_id_counter
            entity_id_counter += 1

            records.append(
                make_row(
                    r_id=q_id,
                    r_related_id="0",
                    r_class="Q",
                    r_type_scale=q.q_type,
                    r_name=q.name,
                    r_relevance=q.relevance or "1",
                    r_text=q.text,
                    r_help=q.help_text,
                    r_language=lang,
                    r_validation=q.validation,
                    r_mandatory=q.mandatory or "Y",
                    r_other=q.other or "N",
                    r_default=q.default,
                    r_same_default=q.same_default,
                )
            )

            # Gestione opzioni e sotto-domande a seconda del tipo
            if q.q_type == "M":
                # Scelta multipla: in LimeSurvey le scelte sono subquestions (class = SQ)
                seen_sq_codes = set()
                all_sub_items = []
                for sq in q.subquestions:
                    if sq.code not in seen_sq_codes:
                        seen_sq_codes.add(sq.code)
                        all_sub_items.append((sq.code, sq.text))
                for opt in q.options:
                    if opt.code not in seen_sq_codes:
                        seen_sq_codes.add(opt.code)
                        all_sub_items.append((opt.code, opt.text))

                for code, text in all_sub_items:
                    sq_id = entity_id_counter
                    entity_id_counter += 1
                    records.append(
                        make_row(
                            r_id=sq_id,
                            r_related_id=q_id,
                            r_class="SQ",
                            r_type_scale="0",
                            r_name=code,
                            r_relevance="1",
                            r_text=text,
                            r_language=lang,
                        )
                    )
            elif q.q_type == "F":
                # Batteria/Matrice:
                # 1. SQ per gli item/righe
                for sq in q.subquestions:
                    sq_id = entity_id_counter
                    entity_id_counter += 1
                    records.append(
                        make_row(
                            r_id=sq_id,
                            r_related_id=q_id,
                            r_class="SQ",
                            r_type_scale="0",
                            r_name=sq.code,
                            r_relevance="1",
                            r_text=sq.text,
                            r_language=lang,
                        )
                    )
                # 2. A per la scala di risposta comune (colonne)
                for opt in q.options:
                    records.append(
                        make_row(
                            r_id=q_id,
                            r_related_id=q_id,
                            r_class="A",
                            r_type_scale="0",
                            r_name=opt.code,
                            r_text=opt.text,
                            r_language=lang,
                        )
                    )
            elif q.q_type in ["L", "!", "5"]:
                # Lista radio, dropdown o scala 5 punti
                for opt in q.options:
                    records.append(
                        make_row(
                            r_id=q_id,
                            r_related_id=q_id,
                            r_class="A",
                            r_type_scale="0",
                            r_name=opt.code,
                            r_text=opt.text,
                            r_language=lang,
                        )
                    )
            else:
                # Per tipi T, S, N (aperti/numerici), se presenti opzioni le emettiamo come A
                if q.options:
                    for opt in q.options:
                        records.append(
                            make_row(
                                r_id=q_id,
                                r_related_id=q_id,
                                r_class="A",
                                r_type_scale="0",
                                r_name=opt.code,
                                r_text=opt.text,
                                r_language=lang,
                            )
                        )

    return records


def validate_tsv_records(records: List[List[str]]) -> List[str]:
    """Valida la consistenza sintattica e relazionale dei record generati prima del salvataggio."""
    errors = []
    if not records:
        return ["Nessun record generato."]

    # Verifica header
    header = records[0]
    if header != TSV_COLUMNS:
        errors.append(f"Header errato. Atteso: {TSV_COLUMNS}, trovato: {header}")

    # Verifica numero colonne per ogni riga
    for idx, row in enumerate(records):
        if len(row) != 14:
            errors.append(f"Riga {idx} contiene {len(row)} colonne anziché 14.")

    # Verifica classi obbligatorie presenti
    classes_present = {row[2] for row in records[1:]}
    for c in ["S", "SL", "G", "Q"]:
        if c not in classes_present:
            errors.append(f"Classe obbligatoria mancante nei record: '{c}'")

    # Verifica integrità relazionale di SQ e A (related_id deve puntare a una Q valida)
    q_rows = {row[0]: row for row in records if row[2] == "Q"}
    q_ids = set(q_rows.keys())

    sq_by_q = {qid: [] for qid in q_ids}
    a_by_q = {qid: [] for qid in q_ids}

    for idx, row in enumerate(records[1:], start=1):
        row_class = row[2]
        related_id = row[1]
        if row_class in ["SQ", "A"]:
            if not related_id or related_id not in q_ids:
                errors.append(
                    f"Riga {idx} ({row_class} {row[4]}): related_id '{related_id}' orfano (non corrisponde ad alcun Q id)."
                )
            elif row_class == "SQ":
                sq_by_q[related_id].append(row)
            elif row_class == "A":
                a_by_q[related_id].append(row)

    # Verifica requisiti strutturali specifici per tipo domanda
    for qid, q_row in q_rows.items():
        q_type = q_row[3]
        q_name = q_row[4]
        if q_type in ["L", "!", "5"] and not a_by_q[qid]:
            errors.append(f"Domanda '{q_name}' (tipo {q_type}) priva di opzioni di risposta (class A).")
        elif q_type == "M" and not sq_by_q[qid]:
            errors.append(f"Domanda a scelta multipla '{q_name}' (tipo M) priva di subquestions (class SQ).")
        elif q_type == "F":
            if not sq_by_q[qid]:
                errors.append(f"Batteria a matrice '{q_name}' (tipo F) priva di item/subquestions (class SQ).")
            if not a_by_q[qid]:
                errors.append(f"Batteria a matrice '{q_name}' (tipo F) priva di opzioni di scala (class A).")

    return errors


def export_to_limesurvey_tsv(input_path: Path, output_path: Path, lang: str = "it") -> bool:
    """Esegue il ciclo completo: lettura markdown, parsing, generazione TSV, validazione e scrittura."""
    if not input_path.exists():
        print(f"[ERRORE] File di input non trovato: {input_path}", file=sys.stderr)
        return False

    content = input_path.read_text(encoding="utf-8")
    survey = parse_questionnaire_markdown(content, default_lang=lang)

    # Verifica che ci siano domande
    total_questions = sum(len(g.questions) for g in survey.groups)
    if total_questions == 0:
        print(f"[ERRORE] Nessuna domanda estratta dal file '{input_path}'.", file=sys.stderr)
        return False

    records = generate_tsv_records(survey)
    validation_errors = validate_tsv_records(records)
    if validation_errors:
        print(f"[ERRORE] Validazione TSV LimeSurvey fallita ({len(validation_errors)} errori):", file=sys.stderr)
        for err in validation_errors:
            print(f"  - {err}", file=sys.stderr)
        return False

    # Scrittura del file TSV
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="\n") as f:
        for row in records:
            f.write("\t".join(row) + "\n")

    # Statistiche riepilogative
    total_groups = len(survey.groups)
    print(f"[OK] File LimeSurvey TSV esportato con successo:")
    print(f"     Destinazione: {output_path}")
    print(f"     Titolo: '{survey.title}'")
    print(f"     Gruppi (G): {total_groups}")
    print(f"     Domande (Q): {total_questions}")
    print(f"     Totale righe TSV (14 colonne): {len(records)}")
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Esportatore di questionari consolidati in formato LimeSurvey TSV (14 colonne standard)."
    )
    parser.add_argument("input", help="Percorso del file markdown (final.md o questionnaire.md)")
    parser.add_argument(
        "-o",
        "--output",
        help="Percorso del file .txt di destinazione (default: limesurvey_survey.txt nella cartella dell'input)",
    )
    parser.add_argument(
        "-l",
        "--lang",
        default="it",
        help="Codice lingua dell'indagine (default: it)",
    )

    args = parser.parse_args()
    input_path = Path(args.input).resolve()

    if args.output:
        output_path = Path(args.output).resolve()
    else:
        output_path = input_path.parent / "limesurvey_survey.txt"

    success = export_to_limesurvey_tsv(input_path, output_path, lang=args.lang)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
