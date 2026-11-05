#!/usr/bin/env python3
"""
extract_survey_knowledge.py — CLI per l'estrazione e normalizzazione di questionari storici

Estrae formulari, batterie di domande, scale di risposta e metadati da file sorgente
(Markdown, testo semplice, e con gestione difensiva per Word .docx e PDF .pdf)
e produce artefatti strutturati in conformità a templates/extracted_survey_template.md
o in formato JSON per l'alimentazione della base di conoscenza di Noto Sondaggi SRL.

Caratteristiche:
- Supporto nativo (senza dipendenze esterne) per file .md e .txt con gestione codifiche (UTF-8 con/senza BOM, Latin-1);
- Gestione difensiva con try/except per librerie opzionali python-docx e pypdf/PyPDF2 (nessun crash se assenti);
- Normalizzazione progressiva dei codici domanda (Q01, Q02, ...) preservando il codice originale (anche alfanumerico: Q2a, Q2b);
- Mappatura obbligatoria dei codici standard di non risposta (97=Non applicabile, 98=Non so, 99=Rifiuto);
- Identificazione automatica di batterie e matrici di item;
- Generazione output in Markdown conforme ai validatori o in JSON strutturato.
"""

import argparse
import datetime
import json
import os
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


STANDARD_NONRESPONSE = {
    "97": "Non applicabile (fuori target / filtro)",
    "98": "Non so / Non conosce / Nessuna opinione",
    "99": "Preferisco non rispondere / Rifiuta",
}

# Regex unificata per opzioni di risposta e codici item
# Supporta: "1 = ...", "1. ...", "1: ...", "1 - ...", "1) ...", "1) - ...",
#           "a) ...", "A. ...", "[1] ...", "- 1 = ...", "- 1. ...", "- 1) ...",
#           "SQ01 = ...", "SQ1: ...", "- [ ] ...", "- ( ) ..."
OPTION_REGEX = re.compile(
    r"^[-*]?\s*(?:\[\s*\]|\(\s*\))?\s*\[?`?([0-9]{1,3}|SQ[0-9]{1,2}|[a-zA-Z])(?:[)\]]\s*[-–—=:\.]?|[\s]*[=–—:\.-])[ \t]*(.*)",
    re.IGNORECASE,
)


@dataclass
class OptionItem:
    code: str
    label: str


@dataclass
class SubQuestionItem:
    code: str
    label: str


@dataclass
class ExtractedQuestion:
    id_item: str
    original_code: str
    construct: str
    question_text: str
    interviewer_notes: str = ""
    question_type: str = "Chiusa singola"
    scale_type: str = "ordinale"
    options: List[OptionItem] = field(default_factory=list)
    missing_codes: List[OptionItem] = field(default_factory=list)
    sub_items: List[SubQuestionItem] = field(default_factory=list)
    filter_logic: str = "Posta a tutti"
    comparability: str = "Alta"
    reuse_cautions: str = (
        "Mantenere formulazione letterale per preservare la serie storica; non alterare la polarità della scala."
    )


@dataclass
class ExtractedBattery:
    id_battery: str
    construct: str
    scale_type: str
    item_count: int
    missing_codes_summary: str = "97=NA, 98=Non so, 99=Rifiuto"
    comparability: str = "Preservare inalterata"
    reuse_notes: str = "Serie storica canonicamente tracciata per la comparabilità"


@dataclass
class ExtractedSurvey:
    id_studio: str
    committente: str = "[DA VERIFICARE]"
    anno: str = "[DA VERIFICARE]"
    target: str = "[DA VERIFICARE]"
    campione: str = "[DA VERIFICARE]"
    modalita: str = "[DA VERIFICARE]"
    fonte_tipo: str = "File di testo"
    file_sorgente: str = ""
    data_estrazione: str = ""
    stato_validazione: str = "BOZZA ESTRATTA — DA REVISIONARE"
    finalita: str = "Indagine campionaria di opinione pubblica / monitoraggio demoscopico"
    aree_tematiche: List[str] = field(default_factory=list)
    note_qualita: str = (
        "Estrazione automatica da documento storico; verificare formulazioni prima dell'inclusione definitiva in knowledge base."
    )
    elementi_da_verificare: List[str] = field(default_factory=list)
    sections: Dict[str, List[ExtractedQuestion]] = field(default_factory=dict)
    batteries: List[ExtractedBattery] = field(default_factory=list)
    researcher_notes: str = ""


# ---------------------------------------------------------------------------
# Lettura difensiva dei file
# ---------------------------------------------------------------------------

def read_input_file(file_path: Path) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Legge il file di input gestendo formati ed estensioni differenti.
    Ritorna: (testo, tipo_fonte, messaggio_errore)
    """
    file_path = Path(file_path)
    if not file_path.exists():
        return None, None, f"File di input non trovato: '{file_path}'"

    suffix = file_path.suffix.lower()

    # Formati nativi testuali (MD, TXT, CSV, ecc.)
    if suffix in [".md", ".txt", ".markdown", ".csv", ".json", ""]:
        try:
            # utf-8-sig rimuove automaticamente l'eventuale BOM UTF-8 iniziale (\ufeff)
            content = file_path.read_text(encoding="utf-8-sig")
        except UnicodeDecodeError:
            try:
                content = file_path.read_text(encoding="latin-1")
            except Exception as e:
                return None, None, f"Impossibile decodificare il file di testo '{file_path}': {e}"
        except Exception as e:
            return None, None, f"Impossibile leggere il file di testo '{file_path}': {e}"

        if not content.strip():
            return None, None, f"Il file di input '{file_path}' è vuoto o privo di contenuto."

        fonte_tipo = "Documento Markdown (.md)" if suffix in [".md", ".markdown"] else "Testo semplice (.txt)"
        return content, fonte_tipo, None

    # Formato Word DOCX (richiede python-docx se disponibile)
    if suffix == ".docx":
        try:
            import docx  # type: ignore
        except ImportError:
            return None, None, (
                f"Impossibile leggere '{file_path.name}': il pacchetto opzionale 'python-docx' non è installato.\n"
                "Per elaborare file Word (.docx), installalo con: pip install python-docx"
            )

        try:
            doc = docx.Document(str(file_path))
            parts: List[str] = []

            # Tentativo di lettura in ordine di apparizione nel corpo XML
            try:
                for child in doc.element.body:
                    tag = child.tag
                    if tag.endswith("p"):
                        txt = "".join(child.itertext()).strip()
                        if txt:
                            parts.append(txt)
                    elif tag.endswith("tbl"):
                        for row in child.iterchildren():
                            if row.tag.endswith("tr"):
                                row_parts: List[str] = []
                                for cell in row.iterchildren():
                                    if cell.tag.endswith("tc"):
                                        cell_txt = "".join(cell.itertext()).strip()
                                        if cell_txt and (not row_parts or cell_txt != row_parts[-1]):
                                            row_parts.append(cell_txt)
                                if row_parts:
                                    parts.append(" | ".join(row_parts))
            except Exception:
                # Fallback standard basato sulle API documentali docx
                parts = []
                for p in doc.paragraphs:
                    text_clean = p.text.strip()
                    if text_clean:
                        parts.append(text_clean)
                for table in doc.tables:
                    for row in table.rows:
                        row_parts = []
                        for cell in row.cells:
                            ct = cell.text.strip()
                            if ct and (not row_parts or ct != row_parts[-1]):
                                row_parts.append(ct)
                        if row_parts:
                            parts.append(" | ".join(row_parts))

            content = "\n\n".join(parts)
            if not content.strip():
                return None, None, f"Il file Word '{file_path}' non contiene testo estraibile."
            return content, "Documento Word (.docx)", None
        except Exception as e:
            return None, None, f"Errore durante la lettura del documento Word '{file_path}': {e}"

    # Formato PDF (richiede pypdf o PyPDF2 se disponibile)
    if suffix == ".pdf":
        pypdf_mod = None
        try:
            import pypdf  # type: ignore
            pypdf_mod = pypdf
        except ImportError:
            try:
                import PyPDF2 as PyPDF2_mod  # type: ignore
                pypdf_mod = PyPDF2_mod
            except ImportError:
                pass

        if pypdf_mod is None:
            return None, None, (
                f"Impossibile leggere '{file_path.name}': nessun pacchetto PDF ('pypdf' o 'PyPDF2') è installato.\n"
                "Per elaborare file PDF (.pdf), installalo con: pip install pypdf"
            )

        try:
            reader = pypdf_mod.PdfReader(str(file_path))
            parts = []
            for idx, page in enumerate(reader.pages):
                txt = page.extract_text()
                if txt and txt.strip():
                    parts.append(txt.strip())
            content = "\n\n".join(parts)
            if not content.strip():
                return None, None, f"Il file PDF '{file_path}' non contiene testo estraibile (possibile scansione immagine)."
            return content, "Documento PDF (.pdf)", None
        except Exception as e:
            return None, None, f"Errore durante l'estrazione testo dal file PDF '{file_path}': {e}"

    return None, None, f"Estensione file non supportata: '{suffix}'. Formati gestiti: .md, .txt, .docx, .pdf"


# ---------------------------------------------------------------------------
# Parsing euristico e normalizzazione del questionario
# ---------------------------------------------------------------------------

def _clean_text(s: str) -> str:
    """Pulisce markdown bold, spazi extra, backtick e ritorni a capo."""
    if not s:
        return ""
    s = s.strip()
    s = re.sub(r"^\*\*(.*?)\*\*$", r"\1", s)
    s = s.strip("`*\"' ")
    return s.strip()


def parse_metadata_from_text(text: str, default_id: str = "studio-storico") -> Dict[str, str]:
    """Estrae eventuali metadati già presenti nel documento di origine."""
    meta = {
        "id_studio": default_id,
        "committente": "[DA VERIFICARE]",
        "anno": "[DA VERIFICARE]",
        "target": "[DA VERIFICARE]",
        "campione": "[DA VERIFICARE]",
        "modalita": "[DA VERIFICARE]",
        "finalita": "Indagine campionaria demoscopica / monitoraggio opinione pubblica",
    }

    patterns = {
        "id_studio": [
            r"ID Studio\s*(?:/\s*Nome Archivio)?\s*:\s*([^\n]+)",
            r"Caso\s*:\s*([^\n]+)",
        ],
        "committente": [
            r"Committente(?: originario)?\s*:\s*([^\n]+)",
        ],
        "anno": [
            r"Periodo di rilevazione\s*(?:/\s*Anno)?\s*:\s*([^\n]+)",
            r"Anno\s*:\s*([^\n]+)",
            r"Data(?:\s+rilevazione|\s+consolidamento)?\s*:\s*([^\n]+)",
        ],
        "target": [
            r"Popolazione di riferimento e Target\s*:\s*([^\n]+)",
            r"Target\s*:\s*([^\n]+)",
            r"Universo\s*:\s*([^\n]+)",
        ],
        "campione": [
            r"Numerosit[aà] campionaria(?: originaria)?\s*:\s*([^\n]+)",
            r"Campione\s*:\s*([^\n]+)",
        ],
        "modalita": [
            r"Modalit[aà] di somministrazione(?: originaria)?\s*:\s*([^\n]+)",
            r"Modalit[aà]\s*:\s*([^\n]+)",
            r"Metodo\s*:\s*([^\n]+)",
        ],
        "finalita": [
            r"Finalit[aà] conoscitiva(?: originaria)?\s*:\s*([^\n]+)",
            r"Obiettivo\s*:\s*([^\n]+)",
        ],
    }

    for key, regexes in patterns.items():
        for rgx in regexes:
            match = re.search(rgx, text, re.IGNORECASE)
            if match:
                val = _clean_text(match.group(1))
                if val and val != "[DA VERIFICARE]":
                    meta[key] = val
                break

    # Se id_studio è rimasto default o vuoto, prova il titolo markdown di livello 1
    if meta["id_studio"] == default_id:
        title_match = re.search(r"^#\s+([^\n]+)", text, re.MULTILINE)
        if title_match:
            candidate = title_match.group(1).strip()
            candidate = re.sub(
                r"^(Questionario|Indagine|Rilevazione|Report)\s*(?:Storico|Consolidato|Bozza)?\s*[:—\-]\s*",
                "",
                candidate,
                flags=re.IGNORECASE,
            )
            candidate = _clean_text(candidate)
            if candidate:
                meta["id_studio"] = candidate[:50]

    return meta


def _is_section_header(line: str) -> bool:
    """Verifica se una riga Markdown H2 o H3 rappresenta una sezione tematica e NON una domanda."""
    m = re.match(r"^#{2,3}\s+(.*)", line.strip())
    if not m:
        return False
    title = m.group(1).strip()

    # Se inizia con un prefisso di domanda tipico (Q01, D01, Domanda 1), NON è una sezione
    if re.match(r"^(?:Domanda\s+|Item\s+|Quesito\s+)?[QDP][0-9]{1,3}[a-zA-Z]?\b", title, re.IGNORECASE):
        return False
    if re.match(r"^[0-9]{1,3}[\.\:\—\-]\s+", title):
        return False

    # Esclude sezioni di template o metadati di processo
    excluded = [
        r"^\d+\.\s*(?:Metadati|Inquadramento|Mappa|Note|Punti aperti|Approvazione|Introduzione)",
        r"^Metadati\s+di\s+Consolidamento",
        r"^Note\s+di\s+Validazione",
    ]
    for ex in excluded:
        if re.search(ex, title, re.IGNORECASE):
            return False

    # È una sezione se inizia con "Sezione", "Area", "Modulo", "Parte", "Blocco", "Domande", "Testo Definitivo"
    if re.search(r"^(?:Sezione|Area\s+Tematica|Modulo|Parte|Blocco|Domande|Testo\s+Definitivo)\b", title, re.IGNORECASE):
        return True

    # Header H2 generico
    if line.strip().startswith("## "):
        return True

    return False


def _clean_section_title(title: str) -> str:
    """Rimuove cancelletti e pulisce il titolo di sezione."""
    t = re.sub(r"^#{2,3}\s+", "", title).strip()
    return _clean_text(t)


def parse_survey_text(text: str, default_id: str = "studio-storico") -> ExtractedSurvey:
    """
    Esegue il parsing analitico del testo del questionario,
    identificando sezioni, domande, opzioni, codici di uscita e batterie.
    """
    meta = parse_metadata_from_text(text, default_id=default_id)

    survey = ExtractedSurvey(
        id_studio=meta["id_studio"],
        committente=meta["committente"],
        anno=meta["anno"],
        target=meta["target"],
        campione=meta["campione"],
        modalita=meta["modalita"],
        finalita=meta["finalita"],
        data_estrazione=datetime.date.today().isoformat(),
    )

    lines = text.splitlines()

    # Rilevamento sezioni nel testo
    section_chunks: List[Tuple[str, List[str]]] = []
    current_sec_name = "Quesiti del Questionario"
    current_sec_lines: List[str] = []

    for line in lines:
        if _is_section_header(line):
            # Salva la sezione precedente se contiene testo
            if current_sec_lines:
                section_chunks.append((current_sec_name, current_sec_lines))
                current_sec_lines = []
            current_sec_name = _clean_section_title(line)
        else:
            current_sec_lines.append(line)

    if current_sec_lines:
        section_chunks.append((current_sec_name, current_sec_lines))

    global_question_counter = 1
    battery_counter = 1

    for sec_title, sec_line_list in section_chunks:
        sec_block_text = "\n".join(sec_line_list)
        questions_in_sec = parse_questions_from_block(sec_block_text, start_counter=global_question_counter)
        if questions_in_sec:
            # Registra l'area tematica se non generica
            if sec_title not in ["Quesiti del Questionario", "Domande", "Testo Definitivo"]:
                if sec_title not in survey.aree_tematiche:
                    survey.aree_tematiche.append(sec_title)

            survey.sections[sec_title] = questions_in_sec
            global_question_counter += len(questions_in_sec)

            # Rileva eventuali batterie
            for q in questions_in_sec:
                is_battery = False
                if q.sub_items or "batteria" in q.question_type.lower() or "matrice" in q.question_type.lower():
                    is_battery = True
                elif any(
                    kw in q.construct.lower()
                    for kw in ["fiducia nei leader", "fiducia nelle istituzioni", "valutazione aspetti", "batteria", "gradimento"]
                ):
                    is_battery = True

                if is_battery:
                    b_id = f"B{battery_counter:02d}"
                    battery_counter += 1
                    item_count = len(q.sub_items) if q.sub_items else len(q.options)
                    survey.batteries.append(
                        ExtractedBattery(
                            id_battery=b_id,
                            construct=q.construct,
                            scale_type=f"{q.scale_type} ({len(q.options)} passi)",
                            item_count=max(item_count, 1),
                            missing_codes_summary="97=NA, 98=Non so, 99=Rifiuto",
                            comparability=q.comparability,
                            reuse_notes="Preservare inalterata formulazione letterale e scala per serie storiche Noto",
                        )
                    )

    # Se nessuna domanda è stata estratta a livello di sezioni, prova scansione dell'intero testo
    if not any(survey.sections.values()):
        questions_fallback = parse_questions_from_block(text, start_counter=1)
        if questions_fallback:
            survey.aree_tematiche.append("Quesiti Generali")
            survey.sections["Quesiti Generali"] = questions_fallback

    return survey


def parse_questions_from_block(block_text: str, start_counter: int = 1) -> List[ExtractedQuestion]:
    """
    Isola le domande all'interno di un blocco di testo, supportando:
    1. Formato template extracted_survey.md (#### Q01 — ... o Codice originale nella fonte:)
    2. Header Markdown H3/H4 (#### Q01 — Costrutto, ### D01. Testo)
    3. Prefissi espliciti di domanda in riga (Q1., Q2a., D01., Domanda 1:)
    4. Domande numerate semplici (1. Testo? 2. Testo?)
    """
    questions: List[ExtractedQuestion] = []

    # 1. Formato template extracted_survey.md
    if "Codice originale nella fonte:" in block_text or "Codice normalizzato:" in block_text:
        chunks = re.split(r"(?=####\s+Q\d+)", block_text)
        for idx, c in enumerate(chunks):
            if "Codice normalizzato:" in c or "Testo originario" in c:
                header_match = re.search(r"####\s+([^\n]+)", c)
                hdr = header_match.group(1) if header_match else f"Q{start_counter + idx:02d}"
                q = parse_extracted_template_chunk(hdr, c, fallback_number=start_counter + len(questions))
                if q:
                    questions.append(q)
        if questions:
            return questions

    # 2. Header Markdown H3/H4 per singole domande
    q_header_regex = re.compile(
        r"^(?:#{3,4})\s+((?:[QDP][0-9]{1,3}[a-zA-Z]?|[0-9]{1,3}[a-zA-Z]?|Domanda\s+[0-9]{1,3}[a-zA-Z]?)\b[^\n]*)",
        re.MULTILINE | re.IGNORECASE,
    )
    matches = list(q_header_regex.finditer(block_text))

    if len(matches) >= 1:
        for idx, m in enumerate(matches):
            header_line = m.group(1).strip()
            start_p = m.end()
            end_p = matches[idx + 1].start() if idx + 1 < len(matches) else len(block_text)
            chunk = block_text[start_p:end_p]
            q = parse_single_question_chunk(header_line, chunk, fallback_number=start_counter + len(questions))
            if q:
                questions.append(q)
        if questions:
            return questions

    # 3. Formato lineare con prefissi di domanda espliciti (Q1, Q2a, D01, Domanda 1, Item 1)
    lines = block_text.splitlines()

    # Controlla se il testo presenta righe con prefissi Q/D/P/Domanda
    has_explicit_q = any(
        re.match(
            r"^(?:(?:Domanda|Item|Quesito)\s+[0-9]{1,3}[a-zA-Z]?|[QDP][0-9]{1,3}[a-zA-Z]?)[\.\:\—\-]",
            l.strip(),
            re.IGNORECASE,
        )
        for l in lines
    )

    if has_explicit_q:
        current_code: Optional[str] = None
        current_first_line: str = ""
        current_chunk_lines: List[str] = []

        for line in lines:
            ls = line.strip()
            if not ls:
                continue

            q_match = re.match(
                r"^(?:(?:Domanda|Item|Quesito)\s+)?([QDP][0-9]{1,3}[a-zA-Z]?)[\.\:\—\-]\s*(.*)",
                ls,
                re.IGNORECASE,
            )
            if q_match:
                # Salva la domanda precedente
                if current_code is not None:
                    full_chunk = current_first_line + "\n" + "\n".join(current_chunk_lines)
                    q = parse_single_linear_question(
                        current_code, full_chunk, fallback_number=start_counter + len(questions)
                    )
                    if q:
                        questions.append(q)
                    current_chunk_lines = []

                current_code = q_match.group(1).strip()
                current_first_line = q_match.group(2).strip()
            elif current_code is not None:
                current_chunk_lines.append(ls)

        if current_code is not None:
            full_chunk = current_first_line + "\n" + "\n".join(current_chunk_lines)
            q = parse_single_linear_question(
                current_code, full_chunk, fallback_number=start_counter + len(questions)
            )
            if q:
                questions.append(q)

        if questions:
            return questions

    # 4. Formato numerato semplice (1. Testo? 2. Testo?)
    # Attenzione: i codici 97, 98, 99 o numeri di opzioni immediate non sono nuove domande
    numbered_q_regex = re.compile(r"^([0-9]{1,3})[\.\:\—\-]\s+([^\n]+)")
    current_num: Optional[int] = None
    current_orig_code: str = ""
    current_first_line = ""
    current_chunk_lines = []

    for line in lines:
        ls = line.strip()
        if not ls:
            continue

        m = numbered_q_regex.match(ls)
        is_new_q = False

        if m:
            cand_num = int(m.group(1))
            cand_text = m.group(2).strip()

            # 97, 98, 99 sono missing codes canonici di Noto, mai nuove domande se segue q 1 o 2
            if cand_num in [97, 98, 99]:
                is_new_q = False
            elif current_num is None:
                # Prima domanda numerata
                if cand_num in [1, 0]:
                    is_new_q = True
            elif cand_num == current_num + 1:
                # Incremento sequenziale (es. da domanda 1 a domanda 2)
                is_new_q = True
            elif cand_num == 1 and current_num is not None:
                # Opzione 1 che riparte subito dopo la domanda 1: è un'opzione, non una nuova domanda!
                is_new_q = False

        if is_new_q and m:
            if current_num is not None:
                full_chunk = current_first_line + "\n" + "\n".join(current_chunk_lines)
                q = parse_single_linear_question(
                    current_orig_code, full_chunk, fallback_number=start_counter + len(questions)
                )
                if q:
                    questions.append(q)
                current_chunk_lines = []

            current_num = int(m.group(1))
            current_orig_code = str(current_num)
            current_first_line = m.group(2).strip()
        elif current_num is not None:
            current_chunk_lines.append(ls)

    if current_num is not None:
        full_chunk = current_first_line + "\n" + "\n".join(current_chunk_lines)
        q = parse_single_linear_question(
            current_orig_code, full_chunk, fallback_number=start_counter + len(questions)
        )
        if q:
            questions.append(q)

    return questions


def parse_single_question_chunk(header_line: str, chunk: str, fallback_number: int) -> Optional[ExtractedQuestion]:
    """Fa il parsing di un blocco di domanda introdotto da un header H3/H4 o bullet template."""
    orig_code = ""
    construct = ""

    header_parts = re.split(r"[—\-:\.]", header_line, maxsplit=1)
    if len(header_parts) == 2:
        candidate_code = header_parts[0].strip()
        candidate_construct = header_parts[1].strip()
        if re.match(r"^[A-Za-z0-9_]+$", candidate_code):
            orig_code = candidate_code
            construct = candidate_construct
        else:
            construct = header_line
    else:
        construct = header_line

    if not orig_code:
        code_match = re.search(r"\b([QDP][0-9]{1,3}[a-zA-Z]?)\b", header_line)
        orig_code = code_match.group(1) if code_match else f"D{fallback_number:02d}"

    norm_code = f"Q{fallback_number:02d}"

    question_text = ""
    question_type = "Chiusa singola"
    interviewer_notes = ""
    filter_logic = "Posta a tutti"
    options: List[OptionItem] = []
    missing_codes: List[OptionItem] = []
    sub_items: List[SubQuestionItem] = []

    lines = chunk.splitlines()
    in_options = False
    in_missing = False
    in_subitems = False

    for line in lines:
        line_s = line.strip()
        if not line_s:
            continue

        # Testo della domanda (conforme sia a templates/questionnaire_template.md sia a extracted_survey)
        if re.search(
            r"(?:Testo(?:\s+(?:originario|per\s+(?:il\s+)?rispondente))?|Formulazione(?:\s+della\s+domanda)?)\s*:\s*(.*)",
            line_s,
            re.IGNORECASE,
        ):
            m = re.search(
                r"(?:Testo(?:\s+(?:originario|per\s+(?:il\s+)?rispondente))?|Formulazione(?:\s+della\s+domanda)?)\s*:\s*(.*)",
                line_s,
                re.IGNORECASE,
            )
            if m:
                question_text = _clean_text(m.group(1))
            in_options = in_missing = in_subitems = False
            continue

        # Costrutto / Obiettivo
        if re.search(
            r"(?:Costrutto(?:\s*/\s*Variabile(?:\s+misurata|\s+indagata)?)?|Obiettivo(?:\s+del\s+brief)?)\s*:\s*(.*)",
            line_s,
            re.IGNORECASE,
        ):
            m = re.search(
                r"(?:Costrutto(?:\s*/\s*Variabile(?:\s+misurata|\s+indagata)?)?|Obiettivo(?:\s+del\s+brief)?)\s*:\s*(.*)",
                line_s,
                re.IGNORECASE,
            )
            if m and (not construct or construct == header_line):
                construct = _clean_text(m.group(1))
            continue

        # Tipo di domanda
        if re.search(r"(?:Tipo|Tipologia)\s+di\s+domanda\s*:\s*(.*)", line_s, re.IGNORECASE):
            m = re.search(r"(?:Tipo|Tipologia)\s+di\s+domanda\s*:\s*(.*)", line_s, re.IGNORECASE)
            if m:
                question_type = _clean_text(m.group(1))
            in_options = in_missing = in_subitems = False
            continue

        # Istruzioni / Note di regia
        if re.search(
            r"(?:Istruzioni(?:\s+generali|\s+intervistatore)?|Not[ae]\s+(?:di\s+regia|intervistatore|per\s+intervistatore))\s*:\s*(.*)",
            line_s,
            re.IGNORECASE,
        ):
            m = re.search(
                r"(?:Istruzioni(?:\s+generali|\s+intervistatore)?|Not[ae]\s+(?:di\s+regia|intervistatore|per\s+intervistatore))\s*:\s*(.*)",
                line_s,
                re.IGNORECASE,
            )
            if m:
                interviewer_notes = _clean_text(m.group(1))
            in_options = in_missing = in_subitems = False
            continue

        # Filtro / Skip / Routing
        if re.search(
            r"(?:Regol[ae]\s+di\s+filtro|Filtro(?:\s*/\s*skip)?|Routing(?:\s+logic)?|Condizioni?\s+di\s+salto)\s*:\s*(.*)",
            line_s,
            re.IGNORECASE,
        ):
            m = re.search(
                r"(?:Regol[ae]\s+di\s+filtro|Filtro(?:\s*/\s*skip)?|Routing(?:\s+logic)?|Condizioni?\s+di\s+salto)\s*:\s*(.*)",
                line_s,
                re.IGNORECASE,
            )
            if m:
                filter_logic = _clean_text(m.group(1))
            in_options = in_missing = in_subitems = False
            continue

        # Inizio blocchi lista opzioni
        if re.search(
            r"(?:Opzioni\s+e\s+codici|Struttura\s+della\s+scala|Opzioni\s+di\s+risposta|Modalit[aà]\s+di\s+risposta)",
            line_s,
            re.IGNORECASE,
        ):
            in_options = True
            in_missing = False
            in_subitems = False
            continue

        # Inizio blocchi missing codes (ignora la riga header stessa!)
        if re.search(
            r"(?:Codici\s+(?:distinti\s+|standard\s+)?di\s+uscita|Non\s+so\s*/\s*rifiuto\s*/\s*non\s+applicabile)",
            line_s,
            re.IGNORECASE,
        ):
            in_missing = True
            in_options = False
            in_subitems = False
            continue

        # Item matrice / batteria
        if re.search(r"(?:Item\s+della\s+batteria|Sotto-domande|Sub-items)", line_s, re.IGNORECASE):
            in_subitems = True
            in_options = False
            in_missing = False
            continue

        # Parsing opzioni / codici strutturati
        opt_match = OPTION_REGEX.match(line_s)
        if opt_match:
            c = opt_match.group(1).strip()
            lbl = _clean_text(opt_match.group(2))

            if in_subitems or c.upper().startswith("SQ"):
                sub_items.append(SubQuestionItem(code=c.upper(), label=lbl))
            elif c in ["97", "98", "99"] or in_missing:
                missing_codes.append(OptionItem(code=c, label=lbl))
            else:
                options.append(OptionItem(code=c, label=lbl))
            continue

        # Opzione bullet semplice senza codice numerico esplicito
        bullet_match = re.match(r"^[-*]\s+(.*)", line_s)
        if bullet_match and (in_options or in_missing):
            item_lbl = _clean_text(bullet_match.group(1))
            # Salta intestazioni interne finite in bullet
            if item_lbl.endswith(":") and any(kw in item_lbl.lower() for kw in ["opzioni", "codici", "uscita"]):
                continue
            if any(kw in item_lbl.lower() for kw in ["non so", "non ricorda", "nessuna opinione"]):
                missing_codes.append(OptionItem(code="98", label=item_lbl))
            elif any(kw in item_lbl.lower() for kw in ["rifiuto", "preferisco non rispondere", "rifiuta"]):
                missing_codes.append(OptionItem(code="99", label=item_lbl))
            elif any(kw in item_lbl.lower() for kw in ["non applicabile", "salta", "fuori target"]):
                missing_codes.append(OptionItem(code="97", label=item_lbl))
            elif in_options:
                auto_code = str(len(options) + 1)
                options.append(OptionItem(code=auto_code, label=item_lbl))

    # Se non è stato trovato testo esplicito, prova la prima riga non vuota del chunk
    if not question_text:
        for line in lines:
            ls = line.strip()
            if ls and not ls.startswith("-") and not ls.startswith("#"):
                question_text = ls
                break

    if not question_text:
        question_text = construct or f"Quesito {norm_code}"

    if not construct:
        construct = make_construct(question_text)

    harmonize_missing_codes(missing_codes)

    if sub_items and question_type == "Chiusa singola":
        question_type = "Batteria di item a matrice"

    scale_type = deduce_scale_type(options, question_type)

    return ExtractedQuestion(
        id_item=norm_code,
        original_code=orig_code or "NON PRESENTE",
        construct=construct,
        question_text=question_text,
        interviewer_notes=interviewer_notes,
        question_type=question_type,
        scale_type=scale_type,
        options=options,
        missing_codes=missing_codes,
        sub_items=sub_items,
        filter_logic=filter_logic or "Posta a tutti",
    )


def make_construct(text: str, max_len: int = 60) -> str:
    """Crea una descrizione sintetica del costrutto senza tagliare parole a metà."""
    text = text.strip()
    if len(text) <= max_len:
        return text.rstrip("?. ")
    cut = text[:max_len]
    last_space = cut.rfind(" ")
    if last_space > 20:
        return cut[:last_space].rstrip("?. ")
    return cut.rstrip("?. ")


def parse_single_linear_question(orig_code: str, chunk: str, fallback_number: int) -> Optional[ExtractedQuestion]:
    """Fa il parsing di una domanda in formato compatto lineare (es. da file di testo/Word grezzo o final.md)."""
    lines = chunk.strip().splitlines()
    if not lines:
        return None

    question_text = lines[0].strip()
    options: List[OptionItem] = []
    missing_codes: List[OptionItem] = []
    sub_items: List[SubQuestionItem] = []
    interviewer_notes = ""
    filter_logic = "Posta a tutti"

    # Gestione opzioni inline su riga singola (es. "Testo della domanda? Sì / No / Non so.")
    if "?" in question_text:
        q_part, opt_part = question_text.split("?", 1)
        if "/" in opt_part:
            candidates = [p.strip().rstrip(".") for p in opt_part.split("/") if p.strip()]
            if len(candidates) >= 2:
                question_text = q_part.strip() + "?"
                for idx, p in enumerate(candidates, start=1):
                    p_lower = p.lower()
                    if any(kw in p_lower for kw in ["non so", "nessuna opinione", "non ricorda"]):
                        missing_codes.append(OptionItem(code="98", label=p))
                    elif any(kw in p_lower for kw in ["rifiut", "preferisco"]):
                        missing_codes.append(OptionItem(code="99", label=p))
                    elif any(kw in p_lower for kw in ["non applicabile", "fuori target"]):
                        missing_codes.append(OptionItem(code="97", label=p))
                    else:
                        options.append(OptionItem(code=str(len(options) + 1), label=p))

    for line in lines[1:]:
        line_s = line.strip()
        if not line_s:
            continue

        # Riconoscimento note di regia e filtri inline
        regia_match = re.search(r"\[(?:REGIA|ISTRUZIONI)\s*:\s*([^\]]+)\]", line_s, re.IGNORECASE)
        if regia_match:
            interviewer_notes = regia_match.group(1).strip()
            continue

        filtro_match = re.search(r"\[FILTRO\s*:\s*([^\]]+)\]", line_s, re.IGNORECASE)
        if filtro_match:
            filter_logic = filtro_match.group(1).strip()
            continue

        # Codici stile "1 = ...", "1. ...", "- 1 = ...", "a) ...", "1) ..."
        m = OPTION_REGEX.match(line_s)
        if m:
            code = m.group(1).strip()
            lbl = _clean_text(m.group(2))

            if code.upper().startswith("SQ"):
                sub_items.append(SubQuestionItem(code=code.upper(), label=lbl))
            elif code in ["97", "98", "99"]:
                missing_codes.append(OptionItem(code=code, label=lbl))
            else:
                options.append(OptionItem(code=code, label=lbl))
        else:
            # Opzioni separate da slash su riga secondaria (es. "Sì / No / Non so")
            if "/" in line_s and not options:
                parts = [p.strip().rstrip(".") for p in line_s.split("/") if p.strip()]
                for idx, p in enumerate(parts, start=1):
                    p_lower = p.lower()
                    if any(kw in p_lower for kw in ["non so", "nessuna opinione"]):
                        missing_codes.append(OptionItem(code="98", label=p))
                    elif any(kw in p_lower for kw in ["rifiut", "preferisco"]):
                        missing_codes.append(OptionItem(code="99", label=p))
                    elif any(kw in p_lower for kw in ["non applicabile", "fuori target"]):
                        missing_codes.append(OptionItem(code="97", label=p))
                    else:
                        options.append(OptionItem(code=str(len(options) + 1), label=p))
            # Bullet semplice
            elif line_s.startswith("-") or line_s.startswith("*"):
                lbl = _clean_text(line_s.lstrip("-* "))
                if any(kw in lbl.lower() for kw in ["non so", "nessuna opinione"]):
                    missing_codes.append(OptionItem(code="98", label=lbl))
                elif any(kw in lbl.lower() for kw in ["rifiut", "preferisco"]):
                    missing_codes.append(OptionItem(code="99", label=lbl))
                elif any(kw in lbl.lower() for kw in ["non applicabile"]):
                    missing_codes.append(OptionItem(code="97", label=lbl))
                elif lbl:
                    options.append(OptionItem(code=str(len(options) + 1), label=lbl))

    harmonize_missing_codes(missing_codes)

    norm_code = f"Q{fallback_number:02d}"
    construct = make_construct(question_text)
    question_type = "Batteria di item" if sub_items else ("Chiusa singola" if options else "Aperta")
    scale_type = deduce_scale_type(options, question_type)

    return ExtractedQuestion(
        id_item=norm_code,
        original_code=orig_code,
        construct=construct,
        question_text=question_text,
        interviewer_notes=interviewer_notes,
        question_type=question_type,
        scale_type=scale_type,
        options=options,
        missing_codes=missing_codes,
        sub_items=sub_items,
        filter_logic=filter_logic,
    )


def parse_extracted_template_chunk(header_line: str, chunk: str, fallback_number: int) -> Optional[ExtractedQuestion]:
    """Fa il parsing di un blocco conforme esattamente a templates/extracted_survey_template.md."""
    norm_code = f"Q{fallback_number:02d}"

    def extract_field(field_name: str, default: str = "") -> str:
        m = re.search(rf"{re.escape(field_name)}\s*:\s*(.*)", chunk, re.IGNORECASE)
        return _clean_text(m.group(1)) if m else default

    orig_code = extract_field("Codice originale nella fonte", f"D{fallback_number:02d}")
    construct = extract_field("Costrutto / Variabile misurata", f"Costrutto {norm_code}")
    q_text = extract_field("Testo originario per rispondente", f"Testo domanda {norm_code}")
    notes = extract_field("Eventuali note di regia / istruzioni intervistatore originarie", "")
    q_type = extract_field("Tipo di domanda", "Chiusa singola")
    filter_logic = extract_field("Regole di filtro e condizioni di salto (routing logic)", "Posta a tutti")
    comparability = extract_field("Valutazione comparabilita storica", "Alta")
    cautions = extract_field(
        "Vincoli e cautele per il riuso",
        "Mantenere formulazione letterale per preservare la serie storica; non alterare la polarità della scala.",
    )

    options: List[OptionItem] = []
    missing_codes: List[OptionItem] = []
    sub_items: List[SubQuestionItem] = []

    lines = chunk.splitlines()
    in_opts = False
    in_missing = False

    for line in lines:
        ls = line.strip()
        if "Struttura della scala / opzioni e codici originali:" in ls:
            in_opts = True
            in_missing = False
            continue
        if "Codici standard di uscita / non risposta" in ls:
            in_missing = True
            in_opts = False
            continue
        if ls.startswith("- Regole di filtro") or ls.startswith("- Valutazione comparabilita"):
            in_opts = False
            in_missing = False
            continue

        opt_match = OPTION_REGEX.match(ls)
        if opt_match:
            c = opt_match.group(1).strip()
            lbl = _clean_text(opt_match.group(2))
            if in_missing or c in ["97", "98", "99"]:
                missing_codes.append(OptionItem(code=c, label=lbl))
            elif c.upper().startswith("SQ"):
                sub_items.append(SubQuestionItem(code=c.upper(), label=lbl))
            elif in_opts:
                options.append(OptionItem(code=c, label=lbl))

    harmonize_missing_codes(missing_codes)
    scale_type = deduce_scale_type(options, q_type)

    return ExtractedQuestion(
        id_item=norm_code,
        original_code=orig_code,
        construct=construct,
        question_text=q_text,
        interviewer_notes=notes,
        question_type=q_type,
        scale_type=scale_type,
        options=options,
        missing_codes=missing_codes,
        sub_items=sub_items,
        filter_logic=filter_logic,
        comparability=comparability,
        reuse_cautions=cautions,
    )


def harmonize_missing_codes(missing_codes: List[OptionItem]) -> None:
    """Garantisce la presenza uniforme dei codici standard 97, 98 e 99."""
    existing_codes = {item.code for item in missing_codes}
    for code, default_label in STANDARD_NONRESPONSE.items():
        if code not in existing_codes:
            missing_codes.append(OptionItem(code=code, label=default_label))
    # Ordina per codice numerico crescente
    missing_codes.sort(key=lambda x: int(x.code) if x.code.isdigit() else 999)


def deduce_scale_type(options: List[OptionItem], question_type: str) -> str:
    """Inferisce la natura metodologica della scala di risposta."""
    if not options:
        return "aperta / qualitativa"
    labels_lower = " ".join([o.label.lower() for o in options])

    if any(kw in labels_lower for kw in ["molto", "abbastanza", "poco", "per nulla"]):
        return "ordinale (4 o 5 punti con polarità)"
    if any(kw in labels_lower for kw in ["ottimo", "buono", "sufficiente", "insufficiente"]):
        return "ordinale (valutativa)"
    if any(kw in labels_lower for kw in ["sì", "no", "si"]):
        return "nominale dicotomica"
    if all(o.code.isdigit() for o in options) and len(options) >= 7:
        return "intervallo / quasi-cardinale (es. 1-10)"
    if "multipla" in question_type.lower():
        return "nominale a scelta multipla"
    return "nominale polytomica"


# ---------------------------------------------------------------------------
# Generazione Output (Markdown conforme a templates/ & JSON strutturato)
# ---------------------------------------------------------------------------

def generate_markdown_output(survey: ExtractedSurvey) -> str:
    """
    Produce il documento Markdown conforme al 100% con
    templates/extracted_survey_template.md e compatibile con validate_runs.py.
    """
    lines: List[str] = []

    lines.append("# Questionario Storico Estratto — Struttura e Batterie\n")
    lines.append(
        "> ATTENZIONE: DOCUMENTO ESTRATTO DA FONTI STORICHE / ARCHIVIO NOTO SONDAGGI SRL. "
        "DESTINATO ALL'ALIMENTAZIONE DELLA BASE DI CONOSCENZA, ALLA PRESERVAZIONE DELLE SERIE STORICHE E AL RIUSO METODOLOGICO CONTROLLATO. "
        "NON MODIFICARE ARBITRARIAMENTE I TESTI O LE SCALE ORIGINARIE.\n"
    )

    # 1. Metadati dello Studio Estratto
    lines.append("## 1. Metadati dello Studio Estratto")
    lines.append(f"- ID Studio / Nome Archivio: {survey.id_studio}")
    lines.append(f"- Committente originario: {survey.committente}")
    lines.append(f"- Periodo di rilevazione / Anno: {survey.anno}")
    lines.append(f"- Popolazione di riferimento e Target: {survey.target}")
    lines.append(f"- Numerosita campionaria originaria: {survey.campione}")
    lines.append(f"- Modalita di somministrazione originaria: {survey.modalita}")
    lines.append(f"- Fonte documentale: {survey.fonte_tipo}")
    lines.append(f"- Riferimento file sorgente: {survey.file_sorgente or '[NON SPECIFICATO]'}")
    lines.append(f"- Data e metodo di estrazione: {survey.data_estrazione} (CLI extract_survey_knowledge.py)")
    lines.append(f"- Stato validazione: {survey.stato_validazione}\n")
    lines.append("---\n")

    # 2. Inquadramento Metodologico e Aree Tematiche
    lines.append("## 2. Inquadramento Metodologico e Aree Tematiche")
    lines.append(f"- Finalita conoscitiva originaria: {survey.finalita}")
    aree_str = ", ".join(survey.aree_tematiche) if survey.aree_tematiche else "Quadro generale dell'indagine"
    lines.append(f"- Aree tematiche coperte dall'indagine: {aree_str}")
    lines.append(f"- Note sulla qualita e completezza della fonte: {survey.note_qualita}")
    da_verificare_str = (
        ", ".join(survey.elementi_da_verificare)
        if survey.elementi_da_verificare
        else "Nessuna lacuna critica riscontrata; dati mancanti marcati come `[DA VERIFICARE]`."
    )
    lines.append(f"- Elementi informativi mancanti o dubbi (marcati `[DA VERIFICARE]`): {da_verificare_str}\n")
    lines.append("---\n")

    # 3. Inventario Strutturato delle Domande e Batterie Estratte
    lines.append("## 3. Inventario Strutturato delle Domande e Batterie Estratte\n")

    sec_keys = list(survey.sections.keys())
    for sec_idx, sec_name in enumerate(sec_keys, start=1):
        sec_letter = chr(64 + sec_idx) if sec_idx <= 26 else str(sec_idx)
        # Evita duplicazione "Sezione A — Sezione A — ..."
        clean_sec = re.sub(r"^Sezione\s+[A-Z0-9]+\s*[—\-:]\s*", "", sec_name, flags=re.IGNORECASE)
        lines.append(f"### Sezione {sec_letter} — {clean_sec}\n")

        for q in survey.sections[sec_name]:
            lines.append(f"#### {q.id_item} — {q.construct}")
            lines.append(f"- Codice originale nella fonte: {q.original_code}")
            lines.append(f"- Codice normalizzato: {q.id_item}")
            lines.append(f"- Costrutto / Variabile misurata: {q.construct}")
            lines.append(f"- Testo originario per rispondente: {q.question_text}")
            regia = q.interviewer_notes if q.interviewer_notes else "Nessuna istruzione particolare documentata"
            lines.append(f"- Eventuali note di regia / istruzioni intervistatore originarie: {regia}")
            lines.append(f"- Tipo di domanda: {q.question_type}")

            # Sub-items per batterie se presenti
            if q.sub_items:
                lines.append("- Item della batteria a matrice:")
                for sq in q.sub_items:
                    lines.append(f"  - {sq.code} = {sq.label}")

            lines.append("- Struttura della scala / opzioni e codici originali:")
            if q.options:
                for opt in q.options:
                    lines.append(f"  - {opt.code} = {opt.label}")
            else:
                lines.append("  - [Risposta aperta libera o numerica]")

            lines.append("- Codici standard di uscita / non risposta (conformita Noto Sondaggi):")
            for mc in q.missing_codes:
                lines.append(f"  - {mc.code} = {mc.label}")

            lines.append(f"- Regole di filtro e condizioni di salto (routing logic): {q.filter_logic}")
            lines.append(f"- Valutazione comparabilita storica: {q.comparability}")
            lines.append(f"- Vincoli e cautele per il riuso: {q.reuse_cautions}\n")

    lines.append("---\n")

    # 4. Mappa delle Batterie Standard Identificate
    lines.append("## 4. Mappa delle Batterie Standard Identificate\n")
    lines.append(
        "| ID Batteria | Costrutto Principale | Tipo Scala / Formato | N. Item | Codici Standard Uscita | Comparabilita Storica | Note Riuso in Nuovi Questionari |"
    )
    lines.append(
        "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |"
    )

    if survey.batteries:
        for b in survey.batteries:
            lines.append(
                f"| {b.id_battery} | {b.construct} | {b.scale_type} | {b.item_count} | "
                f"{b.missing_codes_summary} | {b.comparability} | {b.reuse_notes} |"
            )
    else:
        lines.append(
            "| B01 | Batteria generale quesiti | Scala standard Noto | N/D | 97=NA, 98=Non so, 99=Rifiuto | Conservare per serie storica | Mantenere formulazione |"
        )

    lines.append("\n---\n")

    # 5. Note di Validazione Umana e Revisione
    lines.append("## 5. Note di Validazione Umana e Revisione")
    lines.append("- Decisione del ricercatore: [IN ATTESA / APPROVATO PER KNOWLEDGE BASE / DA REVISIONARE]")
    lines.append("- Ricercatore revisore: DA ASSEGNARE")
    lines.append("- Data revisione: DA DEFINIRE")
    lines.append(
        "- Note e istruzioni per il drafting: Verificare conformità ai formulari storici prima del consolidamento definitivo nella base di conoscenza permanente.\n"
    )

    return "\n".join(lines)


def generate_json_output(survey: ExtractedSurvey) -> str:
    """Serializza il questionario estratto in JSON strutturato e leggibile."""
    flat_questions = []
    for sec_name, q_list in survey.sections.items():
        clean_sec = re.sub(r"^Sezione\s+[A-Z0-9]+\s*[—\-:]\s*", "", sec_name, flags=re.IGNORECASE)
        for q in q_list:
            q_dict = {
                "section": clean_sec,
                "id_item": q.id_item,
                "original_code": q.original_code,
                "construct": q.construct,
                "question_text": q.question_text,
                "interviewer_notes": q.interviewer_notes,
                "question_type": q.question_type,
                "scale_type": q.scale_type,
                "sub_items": [asdict(sq) for sq in q.sub_items],
                "response_options": [asdict(o) for o in q.options],
                "missing_codes": [asdict(m) for m in q.missing_codes],
                "filter_logic": q.filter_logic,
                "comparability": q.comparability,
                "reuse_cautions": q.reuse_cautions,
            }
            flat_questions.append(q_dict)

    data = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "study_metadata": {
            "id_studio": survey.id_studio,
            "committente": survey.committente,
            "anno": survey.anno,
            "target": survey.target,
            "campione": survey.campione,
            "modalita": survey.modalita,
            "fonte_tipo": survey.fonte_tipo,
            "file_sorgente": survey.file_sorgente,
            "data_estrazione": survey.data_estrazione,
            "stato_validazione": survey.stato_validazione,
        },
        "methodological_overview": {
            "finalita": survey.finalita,
            "aree_tematiche": survey.aree_tematiche,
            "note_qualita": survey.note_qualita,
            "elementi_da_verificare": survey.elementi_da_verificare,
        },
        "questions": flat_questions,
        "batteries": [asdict(b) for b in survey.batteries],
    }

    return json.dumps(data, indent=2, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Funzione Principale di Estrazione (API programmatica e CLI)
# ---------------------------------------------------------------------------

def extract_survey_knowledge(
    input_path: Path,
    output_path: Optional[Path] = None,
    output_format: str = "md",
    id_studio: Optional[str] = None,
    committente: Optional[str] = None,
    anno: Optional[str] = None,
    target: Optional[str] = None,
    campione: Optional[str] = None,
    modalita: Optional[str] = None,
    area: Optional[str] = None,
    verbose: bool = False,
) -> bool:
    """
    Esegue l'estrazione completa da un file sorgente e scrive l'output.
    Ritorna True se l'operazione ha avuto successo, False altrimenti.
    """
    input_path = Path(input_path)
    raw_text, fonte_tipo, err = read_input_file(input_path)
    if err:
        sys.stderr.write(f"[ERRORE] {err}\n")
        return False

    if verbose:
        print(f"[INFO] File letto con successo: '{input_path.name}' ({fonte_tipo})")

    default_id = id_studio if id_studio else input_path.stem
    survey = parse_survey_text(raw_text or "", default_id=default_id)
    survey.fonte_tipo = fonte_tipo or "Testo"
    survey.file_sorgente = str(input_path.name)

    # Override CLI esplicito se specificato
    if id_studio:
        survey.id_studio = id_studio
    if committente:
        survey.committente = committente
    if anno:
        survey.anno = anno
    if target:
        survey.target = target
    if campione:
        survey.campione = campione
    if modalita:
        survey.modalita = modalita
    if area and area not in survey.aree_tematiche:
        survey.aree_tematiche.insert(0, area)

    total_questions = sum(len(q_list) for q_list in survey.sections.values())
    if total_questions == 0:
        sys.stderr.write(
            f"[ERRORE] Nessuna domanda identificata all'interno del documento '{input_path.name}'.\n"
        )
        return False

    # Genera output nel formato richiesto
    fmt = output_format.lower().strip()
    if fmt == "json":
        output_content = generate_json_output(survey)
    else:
        output_content = generate_markdown_output(survey)

    if output_path:
        out_p = Path(output_path)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        out_p.write_text(output_content, encoding="utf-8")
        if verbose:
            print(f"[OK] Artefatto salvato con successo: '{out_p}'")
            print(f"     Domande estratte: {total_questions} | Batterie: {len(survey.batteries)}")
    else:
        print(output_content)

    return True


def main() -> None:
    parser = argparse.ArgumentParser(
        description="CLI per l'estrazione e normalizzazione di questionari storici per Noto Sondaggi SRL.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Esempi di utilizzo:
  python scripts/extract_survey_knowledge.py source_questionnaire.md -o knowledge/extracted_studio.md
  python scripts/extract_survey_knowledge.py source.txt --format json -o knowledge/extracted_studio.json
  python scripts/extract_survey_knowledge.py report.docx --committente "Regione Lombardia" --anno 2023 -o runs/caso-1/extracted_survey.md
""",
    )
    parser.add_argument("source", type=str, help="Percorso del file sorgente (.md, .txt, .docx, .pdf)")
    parser.add_argument("-o", "--output", type=str, default=None, help="Percorso del file di destinazione")
    parser.add_argument(
        "-f",
        "--format",
        type=str,
        choices=["md", "json"],
        default="md",
        help="Formato dell'output generato (md per templates/extracted_survey_template.md, json per dizionario strutturato)",
    )
    parser.add_argument("--id-studio", type=str, default=None, help="Identificativo studio / nome archivio")
    parser.add_argument("--committente", type=str, default=None, help="Committente originario dell'indagine")
    parser.add_argument("--anno", type=str, default=None, help="Anno o periodo di rilevazione")
    parser.add_argument("--target", type=str, default=None, help="Popolazione di riferimento e target")
    parser.add_argument("--campione", type=str, default=None, help="Numerosità campionaria (es. 1000 casi)")
    parser.add_argument("--modalita", type=str, default=None, help="Modalità di somministrazione (CATI, CAWI, CAPI, Mista)")
    parser.add_argument("--area", type=str, default=None, help="Area tematica principale dell'indagine")
    parser.add_argument("-v", "--verbose", action="store_true", help="Abilita log dettagliato delle operazioni")

    args = parser.parse_args()

    success = extract_survey_knowledge(
        input_path=Path(args.source),
        output_path=Path(args.output) if args.output else None,
        output_format=args.format,
        id_studio=args.id_studio,
        committente=args.committente,
        anno=args.anno,
        target=args.target,
        campione=args.campione,
        modalita=args.modalita,
        area=args.area,
        verbose=args.verbose,
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
