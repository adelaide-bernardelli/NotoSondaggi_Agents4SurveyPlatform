#!/usr/bin/env python3
"""
generate_interviewer_guide.py — Generatore di Guida Esecutiva per l'Intervistatore (CATI / CAPI)

Trasforma un questionario consolidato o bozza (in formato lineare come examples/demo_run_biblioteca/final.md
oppure strutturato a sezioni tematiche e skip logic come templates/final_template.md) in un documento operativo
formattato per la sala interviste (CATI con operatore telefonico o CAPI per somministrazione faccia a faccia).

Caratteristiche principali:
1. Separazione tipografica netta tra testo da pronunciare a voce alta e note di regia riservate all'operatore.
2. Box di regia dedicati:
   - Istruzioni di somministrazione ("NON LEGGERE LE OPZIONI", "SPONTANEA", "ROTAZIONE CASUALE", "FILTRO ATTIVO");
   - Note di probing neutrale (chiarimenti ammessi senza influenzare la risposta);
   - Trattamento delle non risposte (quando insistere con probing moderato e quando registrare subito "Non so" 98,
     "Rifiuta" 99 o "Non applicabile" 97, evitando forzature).
3. Supporto multi-formato con CLI autonoma:
   - Markdown con callout ricchi (GitHub alerts: `> [!NOTE]`, `> [!IMPORTANT]`, `> [!TIP]`) e tabelle;
   - HTML renderizzato standalone con stile tipografico moderno e responsivo;
   - Esportazione Microsoft Word (.docx) opzionale: rilevamento difensivo con fallback pulito su Markdown
     se `python-docx` non è installato nell'ambiente Python.
"""

import argparse
import html
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Tuple, Union

# Configurazione encoding standard per la console su Windows
if sys.platform == "win32":
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
    if hasattr(sys.stderr, "reconfigure"):
        try:
            sys.stderr.reconfigure(encoding="utf-8")
        except Exception:
            pass

# Rilevamento difensivo opzionale della libreria python-docx
try:
    import docx
    from docx import Document
    from docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.oxml import OxmlElement, parse_xml
    from docx.oxml.ns import nsdecls, qn
    from docx.shared import Inches, Pt, RGBColor

    HAS_DOCX = True
except ImportError:
    HAS_DOCX = False
    Document = None
    WD_ALIGN_VERTICAL = None
    WD_TABLE_ALIGNMENT = None
    WD_ALIGN_PARAGRAPH = None
    OxmlElement = None
    parse_xml = None
    nsdecls = None
    qn = None
    Inches = None
    Pt = None
    RGBColor = None


STANDARD_EXIT_CODES = {
    "97": "Non applicabile",
    "98": "Non so",
    "99": "Preferisco non rispondere",
}


@dataclass
class AnswerOption:
    code: str
    label: str
    is_exit_code: bool = False


@dataclass
class SubQuestionItem:
    code: str
    label: str


@dataclass
class SurveyQuestion:
    id: str
    title: str = ""
    text: str = ""
    q_type: str = "singola"  # singola, multipla, batteria, aperta, numerica, scala
    filter_rule: str = ""
    interviewer_notes: str = ""
    options: List[AnswerOption] = field(default_factory=list)
    subquestions: List[SubQuestionItem] = field(default_factory=list)
    section_name: str = ""

    @property
    def has_filter(self) -> bool:
        if not self.filter_rule:
            return False
        clean = self.filter_rule.lower().strip()
        return not any(clean.startswith(x) for x in ["nessun", "tutti", "tutto", "-", "none", "no"])

    @property
    def exit_codes(self) -> List[AnswerOption]:
        return [opt for opt in self.options if opt.code in ("97", "98", "99") or opt.is_exit_code]

    @property
    def substantive_options(self) -> List[AnswerOption]:
        return [opt for opt in self.options if opt.code not in ("97", "98", "99") and not opt.is_exit_code]


@dataclass
class SurveyMetadata:
    title: str = "Indagine Noto Sondaggi"
    case_id: str = "non-specificato"
    date: str = ""
    mode: str = "CATI (Telefonico assistito da operatore) / CAPI (Intervista personale assistita)"
    welcome_intro: str = ""
    target: str = "Cittadini / Popolazione di riferimento"


def _clean_text(raw_text: str) -> str:
    """Rimuove formattazione markdown superficiale e normalizza spazi."""
    if not raw_text:
        return ""
    text = raw_text.strip()
    if (text.startswith('"') and text.endswith('"')) or (text.startswith("'") and text.endswith("'")):
        text = text[1:-1].strip()
    # Rimuove backticks
    text = text.replace("`", "")
    # Rimuove delimitatori bold/italic avvolgenti
    text = re.sub(r"^\*{1,2}(.*?)\*{1,2}$", r"\1", text).strip()
    # Normalizza ritorni a capo interni e spazi multipli
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _format_markdown_inline_to_html(text: str) -> str:
    """Converte formattazione inline markdown (grassetto, codice) in tag HTML sicuri."""
    escaped = html.escape(text)
    # Converte **grassetto** in <strong>grassetto</strong>
    escaped = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", escaped)
    # Converte `codice` in <code>codice</code>
    escaped = re.sub(r"`(.+?)`", r"<code>\1</code>", escaped)
    return escaped


def _is_exit_code(code: str, label: str) -> bool:
    """Verifica se il codice o l'etichetta rappresentano un codice di uscita/non-risposta."""
    code_clean = code.strip()
    if code_clean in ("97", "98", "99"):
        return True
    lbl_lower = label.lower()
    if any(k in lbl_lower for k in [
        "non applicabile", "non so", "non ricordo", "non conosce",
        "preferisco non rispondere", "rifiuto", "rifiuta"
    ]):
        return True
    return False


def _parse_option_line(line: str) -> Optional[Tuple[str, str, bool]]:
    """
    Riconosce una linea come opzione di risposta numerata o codificata.
    Esempi supportati:
    - 1. Molto soddisfacente
    - - 1 = Molto soddisfacente
    - - `97` = Non applicabile (fuori target)
    - 98. Non so
    - - [99] Preferisco non rispondere
    - SQ01 = Item 1
    """
    stripped = line.strip()
    if not stripped or stripped.startswith("#"):
        return None

    pattern = r"^(?:[-*]\s*)?(?:[`\"'\[\(]?([0-9a-zA-Z_]+)[`\"'\]\)]?\s*(?:[=.:)\-–—]|\s*=\s*)\s*)(.+)$"
    m = re.match(pattern, stripped)
    if m:
        code = m.group(1).strip()
        label = _clean_text(m.group(2))
        is_exit = _is_exit_code(code, label)
        return code, label, is_exit

    return None


def _parse_inline_options(line: str) -> List[Tuple[str, str, bool]]:
    """Estrae opzioni multiple separate da virgola su singola riga."""
    results = []
    parts = [p.strip() for p in line.split(",") if p.strip()]
    for p in parts:
        opt = _parse_option_line(p)
        if opt:
            results.append(opt)
    return results


def parse_questionnaire(content: str) -> Tuple[SurveyMetadata, List[SurveyQuestion]]:
    """
    Parser polimorfo che analizza questionari finali o bozze:
    - Formato lineare (demo_run_biblioteca/final.md)
    - Formato strutturato a sezioni tematiche e skip logic (templates/final_template.md)
    - Gestione testo multi-linea per il rispondente e per le istruzioni di regia
    - Supporto per opzioni a punto elenco non numerate con auto-codifica ordinata
    - Isolamento rigoroso degli attributi per impedire a campi estranei di finire nelle note di regia
    - Gestione codici standard 97, 98, 99 e codici personalizzati
    """
    lines = content.splitlines()
    metadata = SurveyMetadata()
    questions: List[SurveyQuestion] = []

    # 1. Estrazione metadati globali
    for line in lines:
        sl = line.strip()
        if not sl:
            continue
        # Titolo indagine
        if metadata.title == "Indagine Noto Sondaggi":
            m_title = re.match(r"^#\s+(.+)$", sl)
            if m_title:
                metadata.title = _clean_text(m_title.group(1))

        # Caso ID
        m_case = re.match(r"^[-*]?\s*(?:\*\*)?(?:ID Caso|Caso)(?:\*\*)?:\s*(.+)$", sl, re.IGNORECASE)
        if m_case:
            metadata.case_id = _clean_text(m_case.group(1))

        # Data
        m_date = re.match(r"^[-*]?\s*(?:\*\*)?Data[^*:]*(?:\*\*)?:\s*(.+)$", sl, re.IGNORECASE)
        if m_date:
            metadata.date = _clean_text(m_date.group(1))

        # Modalita
        m_mode = re.match(r"^[-*]?\s*(?:\*\*)?Modalit[aà][^*:]*(?:\*\*)?:\s*(.+)$", sl, re.IGNORECASE)
        if m_mode:
            metadata.mode = _clean_text(m_mode.group(1))

        # Popolazione / Target
        m_target = re.match(r"^[-*]?\s*(?:\*\*)?(?:Popolazione|Target)[^*:]*(?:\*\*)?:\s*(.+)$", sl, re.IGNORECASE)
        if m_target:
            metadata.target = _clean_text(m_target.group(1))

        # Testo introduttivo / Informativa
        m_intro = re.match(r"^[-*]?\s*(?:\*\*)?(?:Testo introduttivo|Informativa)[^*:]*(?:\*\*)?:\s*(.+)$", sl, re.IGNORECASE)
        if m_intro:
            metadata.welcome_intro = _clean_text(m_intro.group(1))

    # 2. Individuazione sezione domande
    start_idx = 0
    end_idx = len(lines)
    for i, line in enumerate(lines):
        sl = line.strip()
        if re.search(r"^(?:#{2,3})\s+(?:\d+\.\s*)?(?:Testo Definitivo|Domande|Testo del Questionario)", sl, re.IGNORECASE):
            start_idx = i + 1
            break

    if start_idx > 0:
        for i in range(start_idx, len(lines)):
            sl = lines[i].strip()
            # Interrompe solo se incontra una specifica sezione conclusiva di secondo livello del documento
            if re.match(
                r"^##\s+(?:\d+\.\s*)?(?:Specifiche Riepilogative|Specifiche dei Filtri|Piano di Validazione|Piano di Monitoraggio|Adempimenti|Registro|Punti da Sottoporre|Approvazione Finale|Note Conclusive)",
                sl,
                re.IGNORECASE,
            ):
                end_idx = i
                break

    target_lines = lines[start_idx:end_idx]

    # 3. Parsing a stati di domande, opzioni e attributi
    current_section = "Domande Generali"
    current_q: Optional[SurveyQuestion] = None
    parsing_mode: Optional[str] = None  # "text", "options", "exit_codes", "subquestions", "help"

    for line in target_lines:
        stripped = line.strip()
        if not stripped or stripped in ["---", "***", "___"]:
            continue

        # A. Rilevazione Sezione / Gruppo
        m_sec = re.match(
            r"^(?:#{2,3})\s+(?:(?:\d+\.\s*)?(?:Sezione|Gruppo|Modulo)\s*[A-Za-z0-9_]*\s*[-–—:]\s*(.+)|(?:Sezione|Gruppo|Modulo)\s+([A-Za-z0-9_]+.*))$",
            stripped,
            re.IGNORECASE,
        )
        if m_sec:
            current_section = _clean_text(stripped.lstrip("#").strip())
            current_q = None
            parsing_mode = None
            continue

        # B. Rilevazione Domanda Strutturata (#### Q01 — Costrutto, ### D01: ...)
        m_q_struct = re.match(
            r"^(?:#{2,4})\s+(?:\*\*)?(?:(?:Domanda\s+)([QDP]?\d+[a-zA-Z0-9_]*)|([QDP]\d+[a-zA-Z0-9_]*))(?:\*\*)?(?:\s*[-–—:.]\s*(.*))?$",
            stripped,
            re.IGNORECASE,
        )
        if m_q_struct:
            raw_id = (m_q_struct.group(1) or m_q_struct.group(2)).strip()
            q_id = f"Q{raw_id}" if raw_id.isdigit() else raw_id
            raw_title = _clean_text(m_q_struct.group(3)) if m_q_struct.group(3) else ""
            clean_title = re.sub(r"^\s*\[.*?\]\s*", "", raw_title).strip()
            q_title = clean_title if clean_title else raw_title
            current_q = SurveyQuestion(id=q_id, title=q_title, text=q_title, section_name=current_section)
            questions.append(current_q)
            parsing_mode = None
            continue

        # C. Rilevazione Domanda Lineare (es. Q1. Come valuta..., D2a: ...)
        m_q_linear = re.match(
            r"^\s*(?:\*\*)?(?:(?:Domanda\s+)([QDP]?\d+[a-zA-Z0-9_]*)|([QDP]\d+[a-zA-Z0-9_]*))(?:\*\*)?(?:[.:\-–—]\s*(?:\*\*)?|(?:\*\*)?[.:\-–—])\s+(.+)$",
            stripped,
            re.IGNORECASE,
        )
        if m_q_linear and not re.match(r"^[-*]\s", stripped):
            raw_id = (m_q_linear.group(1) or m_q_linear.group(2)).strip()
            q_id = f"Q{raw_id}" if raw_id.isdigit() else raw_id
            full_text = m_q_linear.group(3).strip()

            # Estrazione di eventuali tag inline [REGIA: ...] o [FILTRO: ...]
            q_regia = ""
            m_reg = re.search(r"\[(?:REGIA|ISTRUZIONI)\s*:\s*([^\]]+)\]", full_text, re.IGNORECASE)
            if m_reg:
                q_regia = m_reg.group(1).strip()
                full_text = full_text.replace(m_reg.group(0), "").strip()

            q_filtro = ""
            m_flt = re.search(r"\[FILTRO\s*:\s*([^\]]+)\]", full_text, re.IGNORECASE)
            if m_flt:
                q_filtro = m_flt.group(1).strip()
                full_text = full_text.replace(m_flt.group(0), "").strip()

            clean_q_text = _clean_text(full_text)
            current_q = SurveyQuestion(
                id=q_id,
                title="",
                text=clean_q_text,
                interviewer_notes=q_regia,
                filter_rule=q_filtro,
                section_name=current_section,
            )
            questions.append(current_q)
            parsing_mode = "options"
            continue

        # D. Parsing attributi all'interno di una domanda
        if current_q:
            # 1. Testo per il rispondente
            m_text = re.match(
                r"^[-*]\s*(?:\*\*)?Testo per (?:il )?rispondente(?:\*\*)?:\s*(.*)$",
                stripped,
                re.IGNORECASE,
            )
            if m_text:
                explicit_text = _clean_text(m_text.group(1))
                if explicit_text:
                    current_q.text = explicit_text
                else:
                    # Inizia acquisizione multi-linea se il testo è su righe successive
                    current_q.text = ""
                parsing_mode = "text"
                continue

            # 2. Obiettivo conoscitivo
            m_obj = re.match(
                r"^[-*]\s*(?:\*\*)?Obiettivo conoscitivo(?:\*\*)?:\s*(.*)$",
                stripped,
                re.IGNORECASE,
            )
            if m_obj:
                obj_text = _clean_text(m_obj.group(1))
                if not current_q.title and obj_text:
                    current_q.title = obj_text
                parsing_mode = None
                continue

            # 3. Tipo di domanda
            m_type = re.match(
                r"^[-*]\s*(?:\*\*)?Tipo di domanda(?:\*\*)?:\s*(.*)$",
                stripped,
                re.IGNORECASE,
            )
            if m_type:
                raw_type = _clean_text(m_type.group(1)).lower()
                if "multipl" in raw_type:
                    current_q.q_type = "multipla"
                elif any(k in raw_type for k in ["batteria", "matrice", "array", "griglia"]):
                    current_q.q_type = "batteria"
                elif any(k in raw_type for k in ["aperta", "long", "esteso", "testo libero"]):
                    current_q.q_type = "aperta"
                elif any(k in raw_type for k in ["numeric", "numero", "quantitativ"]):
                    current_q.q_type = "numerica"
                elif any(k in raw_type for k in ["scala", "likert", "ordinale"]):
                    current_q.q_type = "scala"
                else:
                    current_q.q_type = "singola"
                parsing_mode = None
                continue

            # 4. Regola di filtro / skip
            m_filter = re.match(
                r"^[-*]\s*(?:\*\*)?(?:Regola di filtro\s*/\s*skip|Filtro\s*/\s*skip|Filtro)(?:\*\*)?:\s*(.*)$",
                stripped,
                re.IGNORECASE,
            )
            if m_filter:
                current_q.filter_rule = _clean_text(m_filter.group(1))
                parsing_mode = None
                continue

            # 5. Istruzioni per intervistatore / note di regia
            m_help = re.match(
                r"^[-*]\s*(?:\*\*)?(?:Istruzioni(?:\s+di\s+regia(?:\s+e\s+somministrazione)?|\s+per\s+(?:l['’])?intervistatore|\s+di\s+somministrazione|\s+generali|\s+intervistatore)?|Not[ae]\s+(?:di\s+regia|per\s+(?:l['’])?intervistatore|intervistatore))[^*:]*(?:\*\*)?:?\s*(.*)$",
                stripped,
                re.IGNORECASE,
            )
            if m_help:
                inline_note = _clean_text(m_help.group(1))
                if inline_note:
                    current_q.interviewer_notes = (current_q.interviewer_notes + " " + inline_note).strip()
                parsing_mode = "help"
                continue

            # 6. Intestazione opzioni di risposta
            m_opts_hdr = re.match(
                r"^[-*]\s*(?:\*\*)?Opzioni e codici(?: di risposta)?[^*:]*(?:\*\*)?:?\s*(.*)$",
                stripped,
                re.IGNORECASE,
            )
            if m_opts_hdr:
                parsing_mode = "options"
                inline_part = m_opts_hdr.group(1).strip()
                if inline_part:
                    for c, l, is_ex in _parse_inline_options(inline_part):
                        current_q.options.append(AnswerOption(code=c, label=l, is_exit_code=is_ex))
                continue

            # 7. Intestazione codici distinti di uscita
            m_exit_hdr = re.match(
                r"^[-*]\s*(?:\*\*)?(?:Codici distinti di uscita|Non so\s*/\s*rifiuto)[^*:]*(?:\*\*)?:?\s*(.*)$",
                stripped,
                re.IGNORECASE,
            )
            if m_exit_hdr:
                parsing_mode = "exit_codes"
                inline_part = m_exit_hdr.group(1).strip()
                if inline_part:
                    for c, l, _ in _parse_inline_options(inline_part):
                        current_q.options.append(AnswerOption(code=c, label=l, is_exit_code=True))
                continue

            # 8. Intestazione sotto-domande o item batteria
            m_sub_hdr = re.match(
                r"^[-*]\s*(?:\*\*)?(?:Item della batteria|Item|Sotto-domande|Sottodomande|Affermazioni)(?:\*\*)?:?\s*(.*)$",
                stripped,
                re.IGNORECASE,
            )
            if m_sub_hdr:
                current_q.q_type = "batteria"
                parsing_mode = "subquestions"
                inline_part = m_sub_hdr.group(1).strip()
                if inline_part:
                    for c, l, _ in _parse_inline_options(inline_part):
                        current_q.subquestions.append(SubQuestionItem(code=c, label=l))
                continue

            # 9. Rilevazione di qualsiasi altro attributo con etichetta chiave (es. Nota comparabilità, Prescrizioni)
            # Questo garantisce che attributi successivi NON vengano ingeriti nelle note di regia o nel testo domanda
            m_other_attr = re.match(r"^[-*]\s*(?:\*\*)?[A-Za-z0-9_À-ÿ\s/'-]+(?:\*\*)?:\s*.*", stripped)
            if m_other_attr:
                parsing_mode = None
                continue

            # 10. Continuazione testo domanda multi-linea
            if parsing_mode == "text":
                if stripped.startswith(("-", "*", "#")):
                    parsing_mode = None
                else:
                    opt_test = _parse_option_line(stripped)
                    if opt_test:
                        parsing_mode = None
                    else:
                        current_q.text = (current_q.text + " " + _clean_text(stripped)).strip()
                        continue

            # 11. Continuazione testo note intervistatore multi-linea
            if parsing_mode == "help":
                opt_test = _parse_option_line(stripped)
                if opt_test or stripped.startswith("#"):
                    parsing_mode = None
                elif stripped.startswith(("-", "*", ">")):
                    if re.match(r"^[-*]\s*(?:\*\*)?[A-Za-z0-9_À-ÿ\s/'-]+(?:\*\*)?:", stripped):
                        parsing_mode = None
                    else:
                        sub_line = re.sub(r"^[-*>]\s*", "", stripped).strip()
                        current_q.interviewer_notes = (current_q.interviewer_notes + " " + _clean_text(sub_line)).strip()
                        continue
                else:
                    current_q.interviewer_notes = (current_q.interviewer_notes + " " + _clean_text(stripped)).strip()
                    continue

            # 12. Gestione opzioni codificate o sotto-domande
            opt_parsed = _parse_option_line(stripped)
            if opt_parsed:
                c, l, is_ex = opt_parsed
                if c.upper().startswith("SQ") or parsing_mode == "subquestions":
                    current_q.subquestions.append(SubQuestionItem(code=c, label=l))
                    current_q.q_type = "batteria"
                elif parsing_mode == "exit_codes" or is_ex:
                    current_q.options.append(AnswerOption(code=c, label=l, is_exit_code=True))
                else:
                    current_q.options.append(AnswerOption(code=c, label=l, is_exit_code=False))
                continue

            # 13. Gestione opzioni non numerate sotto sezione opzioni o codici uscita
            if parsing_mode in ["options", "exit_codes"] and stripped.startswith(("-", "*")):
                opt_label = _clean_text(re.sub(r"^[-*]\s*", "", stripped))
                if opt_label:
                    is_ex = _is_exit_code("", opt_label)
                    if is_ex or parsing_mode == "exit_codes":
                        lbl_lower = opt_label.lower()
                        if "non applicabile" in lbl_lower:
                            auto_code = "97"
                        elif any(w in lbl_lower for w in ["non so", "non ricordo", "non conosce"]):
                            auto_code = "98"
                        elif any(w in lbl_lower for w in ["rifiut", "preferisco non"]):
                            auto_code = "99"
                        else:
                            auto_code = "99"
                        current_q.options.append(AnswerOption(code=auto_code, label=opt_label, is_exit_code=True))
                    else:
                        num_codes = [int(o.code) for o in current_q.options if o.code.isdigit() and int(o.code) < 90]
                        auto_code = str(max(num_codes) + 1 if num_codes else len(current_q.options) + 1)
                        current_q.options.append(AnswerOption(code=auto_code, label=opt_label, is_exit_code=False))
                continue

            # 14. Testo diretto della domanda posto immediatamente dopo l'intestazione (senza bullet Testo:)
            if parsing_mode is None and not stripped.startswith(("-", "*", "#")):
                if not current_q.options and not current_q.subquestions:
                    # Se il testo è ancora uguale al titolo grezzo o vuoto, questa riga è il testo effettivo della domanda
                    if not current_q.text or current_q.text == current_q.title:
                        current_q.text = _clean_text(stripped)
                        parsing_mode = "text"
                        continue

    # Post-elaborazione di rifinitura: assicurare correttezza tipi e testo
    for q in questions:
        if q.subquestions and q.q_type == "singola":
            q.q_type = "batteria"

        if not q.options and not q.subquestions and q.q_type == "singola":
            q.q_type = "aperta"

        # Se il testo è rimasto vuoto, imposta fallback esplicito
        if not q.text.strip():
            q.text = q.title if q.title else f"[Testo della domanda {q.id} non specificato]"

    return metadata, questions


def _build_administration_instructions(q: SurveyQuestion) -> List[str]:
    """Costruisce le istruzioni di regia tipografiche per la somministrazione della domanda."""
    instructions = []
    notes_lower = q.interviewer_notes.lower()

    # 1. Istruzione di somministrazione e modalità di lettura
    if q.q_type == "aperta":
        instructions.append("[REGIA: DOMANDA APERTA — NON LEGGERE ALCUNA OPZIONE — TRASCRIVERE FEDELMENTE LA RISPOSTA SPONTANEA]")
    elif q.q_type == "multipla":
        max_ans_match = re.search(r"max\s*(\d+)|fino\s*a\s*(\d+)", notes_lower)
        if max_ans_match:
            n = max_ans_match.group(1) or max_ans_match.group(2)
            instructions.append(f"[REGIA: SCELTA MULTIPLA — LEGGERE LE OPZIONI DI SEGUITO — AMMESSE FINO A {n} RISPOSTE]")
        else:
            instructions.append("[REGIA: SCELTA MULTIPLA — LEGGERE LE OPZIONI DI SEGUITO RALLENTANDO SULLE ALTERNATIVE — AMMESSE PIÙ RISPOSTE]")
    elif q.q_type == "batteria":
        instructions.append("[REGIA: BATTERIA DI ITEM — LEGGERE CIASCUN ITEM SEPARATAMENTE E APPLICARE LA SCALA DI VALUTAZIONE]")
    else:
        # Domanda singola / scala
        if any(w in notes_lower for w in ["spontanea", "non leggere"]):
            instructions.append("[REGIA: NON LEGGERE LE OPZIONI — ATTENDERE RISPOSTA SPONTANEA]")
        else:
            instructions.append("[REGIA: LEGGERE LE OPZIONI DI SEGUITO RALLENTANDO SULLE ALTERNATIVE — AMMESSA UNA SOLA RISPOSTA]")

    # 2. Rotazione casuale
    if any(w in notes_lower for w in ["ruota", "random", "rotazione"]):
        instructions.append("[REGIA: ROTAZIONE CASUALE DEGLI ITEM / DELLE OPZIONI ATTIVA]")
    elif q.q_type == "batteria":
        instructions.append("[REGIA: ROTAZIONE CASUALE RACCOMANDATA — SE PREVISTO DALLA SALA, INVERTIRE L'ORDINE DI LETTURA DEGLI ITEM]")
    elif q.q_type in ("singola", "multipla") and len(q.substantive_options) >= 5:
        # Non consigliare rotazione su scale ordinali o Likert
        labels_concat = " ".join(o.label.lower() for o in q.substantive_options)
        is_ordinal_scale = any(k in labels_concat for k in [
            "molto", "abbastanza", "poco", "per nulla", "completamente", "accordo", "disaccordo", "insoddisfatto"
        ])
        if not is_ordinal_scale:
            instructions.append("[REGIA: ROTAZIONE CASUALE RACCOMANDATA — SE PREVISTO DALLA SALA, INVERTIRE L'ORDINE DI LETTURA]")

    # 3. Filtro attivo
    if q.has_filter:
        instructions.append(f"[FILTRO ATTIVO: Somministrare SOLO se verificata la condizione: «{q.filter_rule}». Se non verificata, codificare 97 (Non applicabile) e saltare]")

    # 4. Note specifiche da questionario originale (se contengono chiarimenti operativi effettivi)
    if q.interviewer_notes:
        clean_notes = q.interviewer_notes.strip()
        # Evita duplicazione se la nota conteneva solo direttive già formattate nei punti precedenti
        standard_triggers = ["spontanea", "non leggere", "max 3", "ruotare", "fino a", "una sola risposta"]
        is_trivial = len(clean_notes.split()) <= 4 and any(t in clean_notes.lower() for t in standard_triggers)
        if not is_trivial:
            instructions.append(f"[NOTE ORIGINALI DI QUESTIONARIO: {clean_notes}]")

    return instructions


def _build_neutral_probing_notes(q: SurveyQuestion) -> List[str]:
    """Genera le note operative di probing neutrale (chiarimenti ammessi senza influenzare la risposta)."""
    notes = [
        "In caso di silenzio o richiesta di chiarimento da parte del cittadino, rileggere la domanda esattamente come formulata, mantenendo tono calmo e neutrale.",
        "Chiarimenti ammessi: è consentito spiegare il significato letterale di un termine solo se esplicitamente richiesto dal rispondente, senza fornire esempi concreti che possano orientare o polarizzare la risposta.",
        "Neutralità dell'operatore: non manifestare mai assenso, approvazione («Ottimo», «Bene») o disappunto rispetto all'opinione espressa.",
    ]

    if q.q_type in ("singola", "scala"):
        notes.append("Risposte vaghe o intermedie: se il rispondente risponde in modo impreciso (es. «così così», «abbastanza ma non del tutto»), chiedere cortesemente: «Rispetto alle opzioni previste, a quale si sente più vicino?» senza spingere verso un polo.")
    elif q.q_type == "multipla":
        notes.append("Rilancio neutrale dopo prima risposta: dopo la prima indicazione spontanea, chiedere una sola volta: «Ci sono altri aspetti tra quelli indicati che desidera segnalare?». Non insistere se il rispondente chiude.")
    elif q.q_type == "aperta":
        notes.append("Probing su risposta aperta: rilanciare esclusivamente con domande aperte neutre standard: «In che senso? Può spiegare meglio?». Non completare mai la frase del rispondente.")

    return notes


def _build_nonresponse_guidelines(q: SurveyQuestion) -> List[str]:
    """Definisce il protocollo rigoroso di gestione dei codici di non risposta (97, 98, 99)."""
    guidelines = []

    # Codice 97
    if q.has_filter or any(opt.code == "97" for opt in q.options):
        filter_desc = q.filter_rule if q.filter_rule else "fuori target"
        guidelines.append(
            f"**Codice 97 — Non applicabile**: Attribuire d'ufficio se il rispondente non è in target o è escluso dalla condizione di filtro («{filter_desc}»). NON proporre mai a voce alta come alternativa."
        )
    else:
        guidelines.append(
            "**Codice 97 — Non applicabile**: Non applicabile per questa domanda a somministrazione universale (riservato esclusivamente a casi di esclusione tecnica autorizzata)."
        )

    # Codice 98
    guidelines.append(
        "**Codice 98 — Non so / Non ricorda / Non ha un'opinione**: **NON LEGGERE NÉ SOLLECITARE MAI AD ALTA VOCE**. Se il cittadino esita, effettuare un probing moderato e neutro («Non ha maturato un'opinione in merito o preferisce non esprimersi?»). Registrare 98 SOLO se l'assenza di opinione o conoscenza è autentica e confermata. **MAI forzare una risposta di comodo**."
    )

    # Codice 99
    guidelines.append(
        "**Codice 99 — Rifiuto / Preferisco non rispondere**: **NON LEGGERE AD ALTA VOCE**. Registrare immediatamente e senza alcuna insistenza il codice 99 qualora il rispondente manifesti disagio o rifiuti esplicitamente di rispondere. **Divieto assoluto di insistere o esercitare probing forzante** (a garanzia della conformità GDPR Art. 9 e della deontologia Noto Sondaggi)."
    )

    return guidelines


def generate_interviewer_guide_md(metadata: SurveyMetadata, questions: List[SurveyQuestion]) -> str:
    """Genera la guida per l'intervistatore in formato Markdown con GitHub alert boxes e tabelle."""
    lines: List[str] = []

    # Intestazione principale
    lines.append("# GUIDA OPERATIVA PER LA SALA INTERVISTE (CATI / CAPI)")
    lines.append(f"## Indagine: {metadata.title}")
    lines.append("")

    # Metadati generali
    lines.append("### Informazioni Operative di Somministrazione")
    lines.append(f"- **ID Caso / Studio**: `{metadata.case_id}`")
    lines.append(f"- **Canale di somministrazione**: {metadata.mode}")
    if metadata.date:
        lines.append(f"- **Data consolidamento / versione**: {metadata.date}")
    lines.append(f"- **Target di riferimento**: {metadata.target}")
    lines.append(f"- **Numero totale domande**: {len(questions)}")
    lines.append("- **Codici standard riservati alla regia**: `97=Non applicabile`, `98=Non so / Non ha un'opinione`, `99=Rifiuto esplicito`")
    lines.append("")

    # Protocollo deontologico generale
    lines.append("> [!NOTE] **PROTOCOLLO GENERALE DI CONDUZIONE INTERVISTA (SALA CATI / CAPI)**")
    lines.append("> 1. **Accoglienza e Tono di Voce**: Adottare un tono chiaro, professionale, calmo e rassicurante. Evitare inflessioni che lascino presagire risposte giuste o gradite.")
    lines.append("> 2. **Fedeltà Letterale al Testo**: Leggere la domanda esattamente come formulata, senza semplificazioni, parafrasi o interpretazioni soggettive.")
    lines.append("> 3. **Gestione Opzioni di Risposta**: Leggere le opzioni di risposta solo se espressamente previsto dalla regia. Non leggere mai i codici `98` e `99`.")
    lines.append("> 4. **Neutralità Assoluta nel Probing**: Aiutare il rispondente solo a comprendere il quesito, senza mai orientare verso una specifica categoria.")
    lines.append("> 5. **Tutela delle Opzioni di Uscita**: Rispettare sempre il diritto al silenzio (`99`) e l'autentica non conoscenza (`98`). Vietata ogni forma di insistenza indebita.")
    lines.append("")

    if metadata.welcome_intro:
        lines.append("### Formula di Avvio Intervista (da pronunciare a voce alta):")
        lines.append(f"> **«{metadata.welcome_intro}»**")
        lines.append("")

    lines.append("---")
    lines.append("")

    # Ciclo domande
    current_sec = ""
    for idx, q in enumerate(questions, start=1):
        if q.section_name and q.section_name != current_sec:
            current_sec = q.section_name
            lines.append(f"## {current_sec}")
            lines.append("")

        q_heading_title = f"{q.id}" + (f" — {q.title}" if q.title else "")
        lines.append(f"### {q_heading_title}")
        lines.append("")

        # 1. Box Regia & Istruzioni Somministrazione
        regia_items = _build_administration_instructions(q)
        lines.append("> [!IMPORTANT] **ISTRUZIONI DI SOMMINISTRAZIONE & REGIA INTERVISTATORE**")
        for item in regia_items:
            lines.append(f"> - {item}")
        lines.append("")

        # 2. Testo da pronunciare a voce alta
        lines.append("#### TESTO DA PRONUNCIARE A VOCE ALTA:")
        lines.append(f"> **«{q.text}»**")
        lines.append("")

        # Se batteria, mostra tabella sotto-domande
        if q.subquestions:
            lines.append("#### ITEM DELLA BATTERIA DA SOMMINISTRARE IN SEQUENZA:")
            lines.append("| Codice Item | Formulazione da Leggere al Rispondente | Note di Lettura |")
            lines.append("| :---: | :--- | :--- |")
            for sub in q.subquestions:
                lines.append(f"| `{sub.code}` | {sub.label} | Leggere con chiarezza e attendere valutazione |")
            lines.append("")

        # 3. Tabella opzioni di risposta e codici operatore
        if q.options:
            lines.append("#### OPZIONI DI RISPOSTA E CODICI OPERATORE:")
            lines.append("| Codice | Opzione di Risposta | Istruzione Operativa per l'Intervistatore |")
            lines.append("| :---: | :--- | :--- |")

            # Opzioni sostanziali
            for opt in q.substantive_options:
                action = "Leggere ad alta voce rallentando sulle alternative"
                if "non leggere" in q.interviewer_notes.lower() or "spontanea" in q.interviewer_notes.lower():
                    action = "**NON LEGGERE** — Attendere risposta spontanea del cittadino"
                lines.append(f"| **{opt.code}** | {opt.label} | {action} |")

            # Codici di uscita (tutti quelli definiti per la domanda)
            exit_codes = q.exit_codes
            existing_exit_codes = {opt.code for opt in exit_codes}

            for opt in exit_codes:
                if opt.code == "97":
                    action = "**NON LEGGERE** — Assegnare solo se escluso da filtro logico"
                elif opt.code == "98":
                    action = "**NON LEGGERE** — Registrare solo se opinione assente dopo probing moderato"
                elif opt.code == "99":
                    action = "**NON LEGGERE** — Registrare immediatamente su rifiuto (senza insistere)"
                else:
                    action = "**NON LEGGERE** — Codice riservato operatore"
                lines.append(f"| `{opt.code}` | {opt.label} | {action} |")

            # Se 98 o 99 non sono ancora presenti nella domanda, aggiungili a tutela della standardizzazione
            if "98" not in existing_exit_codes:
                lines.append("| `98` | Non so / Non ha un'opinione | **NON LEGGERE** — Registrare se il cittadino dichiara spontaneamente di non sapere |")
            if "99" not in existing_exit_codes:
                lines.append("| `99` | Rifiuto / Preferisco non rispondere | **NON LEGGERE** — Registrare se il cittadino rifiuta di rispondere al quesito |")

            lines.append("")

        # 4. Box Probing Neutrale
        probing_items = _build_neutral_probing_notes(q)
        lines.append("> [!NOTE] **NOTE DI PROBING NEUTRALE (CHIARIMENTI AMMESSI)**")
        for item in probing_items:
            lines.append(f"> - {item}")
        lines.append("")

        # 5. Box Trattamento Non Risposte
        nr_items = _build_nonresponse_guidelines(q)
        lines.append("> [!TIP] **TRATTAMENTO DELLE NON RISPOSTE (CODICI 97 / 98 / 99)**")
        for item in nr_items:
            lines.append(f"> - {item}")
        lines.append("")

        lines.append("---")
        lines.append("")

    return "\n".join(lines)


def generate_interviewer_guide_html(metadata: SurveyMetadata, questions: List[SurveyQuestion]) -> str:
    """Genera la guida per l'intervistatore in un file HTML autonomo ed elegante per la visualizzazione a video."""
    esc = html.escape

    doc_parts = [
        "<!DOCTYPE html>",
        '<html lang="it">',
        "<head>",
        '  <meta charset="utf-8">',
        '  <meta name="viewport" content="width=device-width, initial-scale=1.0">',
        f"  <title>Guida Intervistatore — {esc(metadata.title)}</title>",
        "  <style>",
        "    :root {",
        "      --primary: #1e3a8a;",
        "      --primary-light: #eff6ff;",
        "      --warning-border: #f59e0b;",
        "      --warning-bg: #fffbeb;",
        "      --info-border: #0284c7;",
        "      --info-bg: #f0f9ff;",
        "      --tip-border: #8b5cf6;",
        "      --tip-bg: #f5f3ff;",
        "      --text-main: #0f172a;",
        "      --text-muted: #475569;",
        "      --card-bg: #ffffff;",
        "      --border-color: #cbd5e1;",
        "    }",
        "    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f8fafc; color: var(--text-main); margin: 0; padding: 24px; line-height: 1.5; }",
        "    .container { max-width: 960px; margin: 0 auto; background: var(--card-bg); padding: 32px; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -2px rgba(0,0,0,0.1); }",
        "    .header { border-bottom: 2px solid var(--primary); padding-bottom: 16px; margin-bottom: 24px; }",
        "    h1 { color: var(--primary); margin: 0 0 8px 0; font-size: 26px; }",
        "    h2 { color: var(--primary); margin: 24px 0 12px 0; font-size: 20px; border-bottom: 1px solid var(--border-color); padding-bottom: 6px; }",
        "    h3 { color: var(--text-main); margin: 16px 0 8px 0; font-size: 18px; }",
        "    h4 { color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em; font-size: 13px; margin: 16px 0 6px 0; }",
        "    .metadata-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 12px; background: var(--primary-light); padding: 16px; border-radius: 8px; margin-bottom: 24px; }",
        "    .metadata-item { font-size: 14px; }",
        "    .metadata-label { font-weight: 600; color: var(--primary); }",
        "    .speech-box { background: #f1f5f9; border-left: 5px solid var(--primary); padding: 16px 20px; border-radius: 0 8px 8px 0; margin: 12px 0 20px 0; font-size: 18px; font-weight: 600; color: var(--text-main); }",
        "    .callout { padding: 14px 18px; border-radius: 6px; margin: 14px 0; font-size: 14px; }",
        "    .callout-regia { background: var(--warning-bg); border-left: 4px solid var(--warning-border); }",
        "    .callout-regia .callout-title { color: #b45309; font-weight: 700; margin-bottom: 6px; text-transform: uppercase; font-size: 12px; }",
        "    .callout-probing { background: var(--info-bg); border-left: 4px solid var(--info-border); }",
        "    .callout-probing .callout-title { color: #0369a1; font-weight: 700; margin-bottom: 6px; text-transform: uppercase; font-size: 12px; }",
        "    .callout-nr { background: var(--tip-bg); border-left: 4px solid var(--tip-border); }",
        "    .callout-nr .callout-title { color: #6d28d9; font-weight: 700; margin-bottom: 6px; text-transform: uppercase; font-size: 12px; }",
        "    table { width: 100%; border-collapse: collapse; margin: 12px 0 20px 0; font-size: 14px; }",
        "    th, td { padding: 10px 12px; text-align: left; border: 1px solid var(--border-color); }",
        "    th { background: #f8fafc; font-weight: 600; color: var(--text-muted); }",
        "    .code-col { width: 70px; text-align: center; font-weight: bold; }",
        "    .exit-code { background: #fff1f2; color: #9f1239; }",
        "    .question-block { border: 1px solid var(--border-color); border-radius: 8px; padding: 20px; margin-bottom: 28px; background: #ffffff; }",
        "    @media print { body { background: #fff; padding: 0; } .container { box-shadow: none; padding: 0; max-width: 100%; } .question-block { page-break-inside: avoid; } }",
        "  </style>",
        "</head>",
        "<body>",
        '  <div class="container">',
        '    <div class="header">',
        "      <h1>GUIDA OPERATIVA PER LA SALA INTERVISTE (CATI / CAPI)</h1>",
        f"      <div><strong>Indagine:</strong> {esc(metadata.title)}</div>",
        "    </div>",
        '    <div class="metadata-grid">',
        f'      <div class="metadata-item"><span class="metadata-label">Caso:</span> {esc(metadata.case_id)}</div>',
        f'      <div class="metadata-item"><span class="metadata-label">Modalità:</span> {esc(metadata.mode)}</div>',
        f'      <div class="metadata-item"><span class="metadata-label">Data:</span> {esc(metadata.date or "N/D")}</div>',
        f'      <div class="metadata-item"><span class="metadata-label">Target:</span> {esc(metadata.target)}</div>',
        "    </div>",
    ]

    for q in questions:
        doc_parts.append('    <div class="question-block">')
        q_label = f"{esc(q.id)}" + (f" — {esc(q.title)}" if q.title else "")
        doc_parts.append(f"      <h3>{q_label}</h3>")

        # Regia box
        doc_parts.append('      <div class="callout callout-regia">')
        doc_parts.append('        <div class="callout-title">Istruzioni di Somministrazione & Regia</div>')
        doc_parts.append("        <ul>")
        for r in _build_administration_instructions(q):
            doc_parts.append(f"          <li>{esc(r)}</li>")
        doc_parts.append("        </ul>")
        doc_parts.append("      </div>")

        # Speech box
        doc_parts.append("      <h4>Testo da pronunciare a voce alta:</h4>")
        doc_parts.append(f'      <div class="speech-box">«{esc(q.text)}»</div>')

        # Subquestions if any
        if q.subquestions:
            doc_parts.append("      <h4>Item della batteria:</h4>")
            doc_parts.append("      <table><thead><tr><th class='code-col'>Item</th><th>Formulazione</th></tr></thead><tbody>")
            for sub in q.subquestions:
                doc_parts.append(f"        <tr><td class='code-col'>{esc(sub.code)}</td><td>{esc(sub.label)}</td></tr>")
            doc_parts.append("      </tbody></table>")

        # Options table
        if q.options:
            doc_parts.append("      <h4>Opzioni di risposta e codici operatore:</h4>")
            doc_parts.append("      <table><thead><tr><th class='code-col'>Codice</th><th>Opzione</th><th>Istruzione per Intervistatore</th></tr></thead><tbody>")
            for opt in q.substantive_options:
                action = "Leggere ad alta voce"
                if "non leggere" in q.interviewer_notes.lower() or "spontanea" in q.interviewer_notes.lower():
                    action = "<strong>NON LEGGERE</strong> (Spontanea)"
                doc_parts.append(f"        <tr><td class='code-col'><strong>{esc(opt.code)}</strong></td><td>{esc(opt.label)}</td><td>{action}</td></tr>")
            for opt in q.exit_codes:
                doc_parts.append(f"        <tr class='exit-code'><td class='code-col'>{esc(opt.code)}</td><td>{esc(opt.label)}</td><td><strong>NON LEGGERE</strong> (Codice di uscita)</td></tr>")
            doc_parts.append("      </tbody></table>")

        # Probing box
        doc_parts.append('      <div class="callout callout-probing">')
        doc_parts.append('        <div class="callout-title">Note di Probing Neutrale</div>')
        doc_parts.append("        <ul>")
        for p in _build_neutral_probing_notes(q):
            doc_parts.append(f"          <li>{esc(p)}</li>")
        doc_parts.append("        </ul>")
        doc_parts.append("      </div>")

        # Non-response box (con conversione sicura dei grassetti)
        doc_parts.append('      <div class="callout callout-nr">')
        doc_parts.append('        <div class="callout-title">Trattamento Non Risposte (Codici 97 / 98 / 99)</div>')
        doc_parts.append("        <ul>")
        for nr in _build_nonresponse_guidelines(q):
            doc_parts.append(f"          <li>{_format_markdown_inline_to_html(nr)}</li>")
        doc_parts.append("        </ul>")
        doc_parts.append("      </div>")

        doc_parts.append("    </div>")

    doc_parts.extend(["  </div>", "</body>", "</html>"])
    return "\n".join(doc_parts)


def _add_markdown_run(paragraph, text: str, font_size_pt: float = 9.0, default_color=None):
    """Aggiunge segmenti di testo a un paragrafo Word gestendo correttamente i blocchi **grassetto**."""
    parts = re.split(r"(\*\*.*?\*\*)", text)
    for part in parts:
        if not part:
            continue
        if part.startswith("**") and part.endswith("**") and len(part) >= 4:
            run = paragraph.add_run(part[2:-2])
            run.bold = True
        else:
            run = paragraph.add_run(part)
        run.font.size = Pt(font_size_pt)
        if default_color:
            run.font.color.rgb = default_color


def generate_interviewer_guide_docx(
    metadata: SurveyMetadata,
    questions: List[SurveyQuestion],
    output_path: Union[str, Path],
) -> bool:
    """
    Genera il file Microsoft Word (.docx) della guida per l'intervistatore.
    Se python-docx è installato, crea un documento formattato con stili tipografici dedicati:
    - Intestazioni e metadati;
    - Testo domanda in nero grassetto (font prominente);
    - Note di regia operatore in corsivo ambra;
    - Box di probing e non-risposta;
    - Tabelle opzioni strutturate.
    Restituisce True in caso di successo, False se python-docx non è disponibile.
    """
    if not HAS_DOCX or Document is None:
        return False

    out_p = Path(output_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)

    doc = Document()

    # Impostazione margini (2 cm per lato)
    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)

    # Titolo documento
    title_p = doc.add_paragraph()
    title_run = title_p.add_run("GUIDA OPERATIVA PER LA SALA INTERVISTE (CATI / CAPI)\n")
    title_run.bold = True
    title_run.font.size = Pt(18)
    title_run.font.color.rgb = RGBColor(30, 58, 138)  # Blu Notte

    sub_run = title_p.add_run(f"Indagine: {metadata.title}\n")
    sub_run.bold = True
    sub_run.font.size = Pt(13)
    sub_run.font.color.rgb = RGBColor(71, 85, 105)

    meta_run = title_p.add_run(
        f"Caso: {metadata.case_id}  |  Modalità: {metadata.mode}  |  Data: {metadata.date or 'N/D'}\n"
        f"Target: {metadata.target}  |  Domande totali: {len(questions)}\n"
    )
    meta_run.font.size = Pt(10)
    meta_run.font.color.rgb = RGBColor(100, 116, 139)

    doc.add_paragraph("―" * 45)

    # Deontologia e sala interviste
    p_proto = doc.add_paragraph()
    p_proto.add_run("PROTOCOLLO GENERALE DI CONDUZIONE INTERVISTA (CATI / CAPI)\n").bold = True
    p_proto.add_run(
        "• Tono di voce: chiaro, professionale, neutrale e privo di inflessioni orientative.\n"
        "• Fedeltà testuale: leggere le domande esattamente come scritte, senza parafrasi.\n"
        "• Regia opzioni: non leggere le opzioni se indicato [SPONTANEA]. Non leggere mai codici 98 e 99.\n"
        "• Probing: chiarire solo se richiesto, senza influenzare né suggerire esempi.\n"
        "• Rispetto non risposte: registrare 98 per mancata opinione e 99 per rifiuto senza forzature.\n"
    ).font.size = Pt(9.5)

    doc.add_paragraph("―" * 45)

    # Elenco domande
    for q in questions:
        # Intestazione domanda
        q_label = f"{q.id}" + (f" — {q.title}" if q.title else "")
        h_q = doc.add_heading(level=2)
        h_q_run = h_q.add_run(q_label)
        h_q_run.font.color.rgb = RGBColor(30, 58, 138)
        h_q_run.font.size = Pt(13)

        # 1. Regia Somministrazione
        p_reg = doc.add_paragraph()
        reg_title = p_reg.add_run("[ISTRUZIONI DI SOMMINISTRAZIONE & REGIA INTERVISTATORE]\n")
        reg_title.bold = True
        reg_title.font.size = Pt(10)
        reg_title.font.color.rgb = RGBColor(180, 83, 9)  # Ambra

        for item in _build_administration_instructions(q):
            r_run = p_reg.add_run(f"• {item}\n")
            r_run.italic = True
            r_run.font.size = Pt(9.5)
            r_run.font.color.rgb = RGBColor(75, 85, 99)

        # 2. Testo da leggere ad alta voce
        p_speech_lbl = doc.add_paragraph()
        p_speech_lbl.add_run("TESTO DA PRONUNCIARE A VOCE ALTA:").bold = True
        p_speech_lbl.runs[0].font.size = Pt(9)
        p_speech_lbl.runs[0].font.color.rgb = RGBColor(100, 116, 139)

        p_speech = doc.add_paragraph()
        speech_run = p_speech.add_run(f"«{q.text}»")
        speech_run.bold = True
        speech_run.font.size = Pt(12)
        speech_run.font.color.rgb = RGBColor(15, 23, 42)

        # 3. Item batteria se presenti
        if q.subquestions:
            doc.add_paragraph("Item della batteria da sottoporre in sequenza:").bold = True
            table_sub = doc.add_table(rows=1, cols=2)
            table_sub.alignment = WD_TABLE_ALIGNMENT.CENTER
            hdr_cells = table_sub.rows[0].cells
            hdr_cells[0].text = "Codice"
            hdr_cells[1].text = "Formulazione Item"
            for sub in q.subquestions:
                row_cells = table_sub.add_row().cells
                row_cells[0].text = sub.code
                row_cells[1].text = sub.label

        # 4. Tabella opzioni
        if q.options:
            doc.add_paragraph("Opzioni di risposta e codici operatore:").bold = True
            table_opt = doc.add_table(rows=1, cols=3)
            table_opt.alignment = WD_TABLE_ALIGNMENT.CENTER
            hdr = table_opt.rows[0].cells
            hdr[0].text = "Codice"
            hdr[1].text = "Opzione di Risposta"
            hdr[2].text = "Istruzione Operativa"

            for opt in q.substantive_options:
                row = table_opt.add_row().cells
                row[0].text = opt.code
                row[1].text = opt.label
                action = "Leggere ad alta voce"
                if "non leggere" in q.interviewer_notes.lower() or "spontanea" in q.interviewer_notes.lower():
                    action = "NON LEGGERE — Spontanea"
                row[2].text = action

            for opt in q.exit_codes:
                row = table_opt.add_row().cells
                row[0].text = opt.code
                row[1].text = opt.label
                row[2].text = "NON LEGGERE — Riservato operatore"

        # 5. Probing neutrale
        p_prob = doc.add_paragraph()
        p_prob_lbl = p_prob.add_run("[NOTE DI PROBING NEUTRALE]\n")
        p_prob_lbl.bold = True
        p_prob_lbl.font.size = Pt(9.5)
        p_prob_lbl.font.color.rgb = RGBColor(3, 105, 161)  # Azzurro
        for note in _build_neutral_probing_notes(q):
            p_run = p_prob.add_run(f"• {note}\n")
            p_run.font.size = Pt(9)

        # 6. Trattamento non risposte (con gestione formattata dei grassetti)
        p_nr = doc.add_paragraph()
        p_nr_lbl = p_nr.add_run("[TRATTAMENTO NON RISPOSTE (97 / 98 / 99)]\n")
        p_nr_lbl.bold = True
        p_nr_lbl.font.size = Pt(9.5)
        p_nr_lbl.font.color.rgb = RGBColor(109, 40, 217)  # Viola
        for nr in _build_nonresponse_guidelines(q):
            p_nr_item = doc.add_paragraph()
            p_nr_item.add_run("• ").font.size = Pt(9)
            _add_markdown_run(p_nr_item, nr, font_size_pt=9.0)

        doc.add_paragraph("―" * 45)

    doc.save(str(out_p))
    return True


def generate_guide(
    input_file: Union[str, Path],
    output_file: Optional[Union[str, Path]] = None,
    output_format: str = "md",
) -> int:
    """
    Funzione principale per la generazione della guida operatore.
    Supporta formati: 'md', 'html', 'docx', 'both'.
    Gestisce in modo difensivo l'assenza di python-docx senza interrompere il flusso.
    """
    in_path = Path(input_file)
    if not in_path.exists():
        print(f"[ERRORE] File di input non trovato: {in_path}", file=sys.stderr)
        return 1

    try:
        content = in_path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"[ERRORE] Impossibile leggere il file di input '{in_path}': {e}", file=sys.stderr)
        return 1

    metadata, questions = parse_questionnaire(content)
    if not questions:
        print(f"[ERRORE] Nessuna domanda estratta dal questionario '{in_path}'.", file=sys.stderr)
        return 1

    fmt = output_format.lower().strip()
    if fmt not in ("md", "html", "docx", "both", "all"):
        print(f"[ERRORE] Formato '{output_format}' non supportato. Formati validi: md, html, docx, both, all", file=sys.stderr)
        return 1

    # Calcolo percorsi di output
    if output_file:
        out_base = Path(output_file)
    else:
        out_base = in_path.parent / f"{in_path.stem}_guida_intervistatore"

    # Generazione Markdown
    if fmt in ("md", "both", "all"):
        md_path = out_base if str(out_base).endswith(".md") else out_base.with_suffix(".md")
        md_path.parent.mkdir(parents=True, exist_ok=True)
        md_text = generate_interviewer_guide_md(metadata, questions)
        md_path.write_text(md_text, encoding="utf-8")
        print(f"[OK] Guida intervistatore Markdown generata con successo: {md_path}")
        print(f"     Domande elaborate: {len(questions)}")

    # Generazione HTML
    if fmt in ("html", "all"):
        html_path = out_base if str(out_base).endswith(".html") else out_base.with_suffix(".html")
        html_path.parent.mkdir(parents=True, exist_ok=True)
        html_text = generate_interviewer_guide_html(metadata, questions)
        html_path.write_text(html_text, encoding="utf-8")
        print(f"[OK] Guida intervistatore HTML renderizzata con successo: {html_path}")
        print(f"     Domande elaborate: {len(questions)}")

    # Generazione Word (.docx) con gestione difensiva
    if fmt in ("docx", "both", "all"):
        docx_path = out_base if str(out_base).endswith(".docx") else out_base.with_suffix(".docx")
        if HAS_DOCX:
            success = generate_interviewer_guide_docx(metadata, questions, docx_path)
            if success:
                print(f"[OK] Guida intervistatore Word (.docx) generata con successo: {docx_path}")
            else:
                print("[ERRORE] Fallimento imprevisto nella generazione del documento Word.", file=sys.stderr)
                return 1
        else:
            # Fallback difensivo su Markdown
            print("[AVVISO] La libreria opzionale 'python-docx' non è installata nell'ambiente Python.")
            print("[AVVISO] Impossibile generare il file binario Word (.docx).")
            if fmt == "docx":
                fallback_md = docx_path.with_suffix(".md")
                fallback_md.parent.mkdir(parents=True, exist_ok=True)
                md_text = generate_interviewer_guide_md(metadata, questions)
                fallback_md.write_text(md_text, encoding="utf-8")
                print(f"[INFO] Eseguito fallback automatico su Markdown ad alta leggibilità: {fallback_md}")

    return 0


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generatore Guida Intervistatore CATI/CAPI con note di regia e istruzioni tipografiche (Noto Sondaggi SRL)."
    )
    parser.add_argument(
        "input_file",
        type=str,
        help="Percorso del questionario markdown di input (es. final.md o questionnaire.md)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default=None,
        help="Percorso del file di destinazione (se omesso viene derivato dal nome dell'input)",
    )
    parser.add_argument(
        "-f",
        "--format",
        type=str.lower,
        choices=["md", "docx", "both", "html", "all"],
        default="md",
        help="Formato della guida da generare: md (default), docx, both, html, all",
    )

    args = parser.parse_args(argv)
    return generate_guide(input_file=args.input_file, output_file=args.output, output_format=args.format)


if __name__ == "__main__":
    sys.exit(main())
