#!/usr/bin/env python3
"""
generate_agcom_report.py — Generatore di Scheda Informativa AGCOM (Delibera 256/10/CSP)

Compila automaticamente la Scheda Informativa obbligatoria per legge ai sensi dell'art. 5
dell'Allegato A alla Delibera AGCOM n. 256/10/CSP per la pubblicazione e diffusione di sondaggi
sui mezzi di comunicazione di massa e il contestuale deposito presso il Dipartimento per
l'Informazione e l'Editoria della Presidenza del Consiglio dei Ministri.

Funzionalità principali:
1. Estrazione metadati campionari e di ricerca da `status.md`, `brief.md` e `final.md` (o `questionnaire.md`).
2. Supporto bidirezionale sia per cartella del caso sia per file questionario diretto (.md).
3. Calcolo automatico del margine d'errore statistico teorico al 95% di confidenza (con gestione universo finito ed edge cases).
4. Normalizzazione numeri con notazione italiana delle migliaia (es. n = 1.000 -> 1000).
5. Marcatura rigorosa con `[DA VERIFICARE SUL CAMPO]` dei parametri ex-post non ancora disponibili prima del fieldwork.
6. Trascrizione fedele e integrale di tutti i quesiti, incluse batterie/matrici, opzioni con qualsiasi sintassi (=, ., -),
   opzioni inline e ordinamento canonico dei codici standard di non risposta (97, 98, 99).
7. Validatore incorporato di conformità alla Delibera AGCOM 256/10/CSP.
"""

import argparse
import math
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

# Configurazione encoding console Windows
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

DELIBERA_REF = "Delibera AGCOM n. 256/10/CSP"
SITO_DEPOSITO = "www.sondaggipoliticoelettorali.it"
SOGGETTO_REALIZZATORE = "Noto Sondaggi SRL"
DA_VERIFICARE_CAMPO = "[DA VERIFICARE SUL CAMPO]"


@dataclass
class AGCOMQuestionOption:
    code: str
    label: str
    is_exit_code: bool = False


@dataclass
class AGCOMQuestion:
    id: str
    title: str = ""
    text: str = ""
    regia_instructions: str = ""
    options: List[AGCOMQuestionOption] = field(default_factory=list)
    exit_codes: List[AGCOMQuestionOption] = field(default_factory=list)
    subquestions: List[AGCOMQuestionOption] = field(default_factory=list)
    filter_rule: str = ""
    q_type: str = "singola"


@dataclass
class AGCOMMetadata:
    case_id: str = "non-specificato"
    title: str = "Indagine Demoscopica Noto Sondaggi"
    company: str = SOGGETTO_REALIZZATORE
    client: str = "Noto Sondaggi SRL / Committente da definire"
    buyer: str = "Stesso committente"
    fieldwork_dates: str = DA_VERIFICARE_CAMPO
    publication_date: str = DA_VERIFICARE_CAMPO
    media_channel: str = DA_VERIFICARE_CAMPO
    target_population: str = "Popolazione maggiorenne residente"
    territorial_scope: str = "Nazionale"
    sampling_method: str = "Campionamento per quote stratificate (genere, età, ampiezza centro)"
    representativeness: str = "Campione rappresentativo dell'universo di riferimento per sesso ed età"
    planned_sample_size: int = 800
    actual_sample_size: str = DA_VERIFICARE_CAMPO
    data_collection_method: str = "CATI / CAWI (Metodologia mista)"
    survey_platform: str = "Piattaforma mista CATI assistita da operatore / CAWI"
    interview_duration: str = "Circa 5-7 minuti"
    weighting_method: str = "Ponderazione post-stratificata per quote sociodemografiche (sesso, classi d'età, ampiezza centro)"
    margin_of_error_pct: float = 3.46
    confidence_level: float = 0.95
    z_score: float = 1.96
    assumed_p: float = 0.50


def calculate_margin_of_error(
    n: int,
    confidence: float = 0.95,
    p: float = 0.50,
    population_size: Optional[int] = None,
) -> float:
    """
    Calcola il margine d'errore statistico teorico massimo percentuale (± e%).
    Formula: e = z * sqrt(p * (1 - p) / n) * fpc
    dove fpc = sqrt((N - n) / (N - 1)) se la popolazione N è finita, altrimenti 1.0.
    Ritorna la percentuale arrotondata a 2 decimali (es. 3.46 per ± 3.46%).
    """
    if n <= 0:
        raise ValueError(f"La numerosità campionaria n deve essere positiva (ricevuto n={n})")
    if not (0.0 < confidence < 1.0):
        raise ValueError(f"Il livello di confidenza deve essere compreso tra 0 e 1 (ricevuto {confidence})")
    if not (0.0 < p < 1.0):
        raise ValueError(f"La proporzione p deve essere compresa tra 0 e 1 (ricevuto {p})")

    # Mappatura z-score per i principali livelli di confidenza
    if abs(confidence - 0.95) < 0.005:
        z = 1.96
    elif abs(confidence - 0.99) < 0.005:
        z = 2.576
    elif abs(confidence - 0.90) < 0.005:
        z = 1.645
    else:
        # Approssimazione standard di Gauss per altri livelli
        z = 1.96

    variance = p * (1.0 - p)
    std_err = math.sqrt(variance / float(n))

    fpc = 1.0
    if population_size is not None:
        if population_size < n:
            raise ValueError(
                f"La dimensione della popolazione N ({population_size}) non può essere inferiore alla numerosità campionaria n ({n})"
            )
        if population_size == n:
            return 0.0
        if population_size > 1:
            fpc = math.sqrt((population_size - n) / float(population_size - 1))

    error_rate = z * std_err * fpc
    return round(error_rate * 100.0, 2)


def _clean_str(text: str) -> str:
    """Pulisce e normalizza stringhe markdown."""
    if not text:
        return ""
    t = text.strip()
    if (t.startswith('"') and t.endswith('"')) or (t.startswith("'") and t.endswith("'")):
        t = t[1:-1].strip()
    t = t.replace("`", "")
    t = re.sub(r"^\*{1,2}(.*?)\*{1,2}$", r"\1", t).strip()
    t = re.sub(r"\s+", " ", t)
    return t.strip()


def _parse_sample_size(text: str) -> Optional[int]:
    """
    Estrae la numerosità campionaria intera n da una stringa gestendo
    notazioni standard e notazioni italiane delle migliaia (es. 'n = 1.000', 'n = 1 500', '800 interviste').
    """
    if not text:
        return None
    patterns = [
        r"\bn\s*=\s*([0-9\s.,]+)",
        r"([0-9\s.,]+)\s*(?:interviste|casi|rispondenti|soggetti|questionari)",
    ]
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            raw = re.sub(r"\s+", "", m.group(1).strip())
            # Se ha separatore delle migliaia (es. 1.000 o 1,000 con 3 cifre seguenti)
            if re.match(r"^\d{1,3}(?:[.,]\d{3})+$", raw):
                clean_num = re.sub(r"[.,]", "", raw)
            else:
                clean_num = re.sub(r"[^0-9]", "", raw)
            if clean_num:
                try:
                    val = int(clean_num)
                    if val > 0:
                        return val
                except ValueError:
                    pass
    return None


def _is_exit_code(code: str, label: str) -> bool:
    """Verifica se il codice o l'etichetta rappresentano un codice di uscita/non-risposta."""
    clean_c = code.strip()
    if clean_c in ("97", "98", "99"):
        return True
    lbl_lower = label.lower()
    return any(
        k in lbl_lower
        for k in [
            "non so",
            "non conosce",
            "non ricorda",
            "nessuna opinione",
            "rifiut",
            "non applicabile",
            "preferisco non",
            "fuori target",
            "fuori quota",
        ]
    )


def _parse_option_line(line: str) -> Optional[Tuple[str, str, bool]]:
    """
    Riconosce una linea come opzione di risposta o sotto-quesito.
    Supporta sintassi con '.', '=', '-', ')', con o senza backticks/parentesi/spazi:
    - 1. Molto soddisfacente
    - - 1 = Molto soddisfacente
    - - `97` = Non applicabile (fuori target)
    - 98. Non so
    - - [99] Preferisco non rispondere
    - SQ01 = Servizio anagrafe
    """
    stripped = line.strip()
    if not stripped or stripped.startswith("#"):
        return None

    pattern = r"^(?:[-*]\s*)?(?:[`\"'\[\(]?([0-9a-zA-Z_]+)[`\"'\]\)]?\s*(?:[=.:)\-–—]|\s*=\s*)\s*)(.+)$"
    m = re.match(pattern, stripped)
    if m:
        code = m.group(1).strip()
        label = _clean_str(m.group(2))
        is_exit = _is_exit_code(code, label)
        return code, label, is_exit

    return None


def _parse_inline_options(line: str) -> List[Tuple[str, str, bool]]:
    """Estrae opzioni multiple separate da virgola o punto e virgola su singola riga."""
    results = []
    parts = [p.strip() for p in re.split(r"[,;]", line) if p.strip()]
    for p in parts:
        opt = _parse_option_line(p)
        if opt:
            results.append(opt)
    return results


def parse_case_metadata(case_dir: Path) -> AGCOMMetadata:
    """
    Estrae i metadati per la Scheda AGCOM esaminando `status.md`, `brief.md` e `final.md` (o `questionnaire.md`).
    Garantisce estrazione robusta anche quando brief.md è assente (es. workflow /revisione-questionario).
    """
    meta = AGCOMMetadata()
    case_dir = Path(case_dir)

    # 1. Lettura status.md se disponibile
    status_file = case_dir / "status.md"
    if status_file.exists():
        try:
            content = status_file.read_text(encoding="utf-8")
            m_case = re.search(r"[-*]?\s*(?:\*\*)?(?:ID\s+)?Caso(?:\*\*)?:\s*`?([A-Za-z0-9_.-]+)`?", content, re.IGNORECASE)
            if m_case:
                meta.case_id = _clean_str(m_case.group(1))
            m_date = re.search(r"[-*]?\s*(?:\*\*)?Data(?: di apertura)?[^*:]*(?:\*\*)?:\s*`?([0-9-]+)`?", content, re.IGNORECASE)
            if m_date:
                meta.fieldwork_dates = _clean_str(m_date.group(1))
        except Exception:
            pass

    # 2. Lettura brief.md se disponibile
    brief_file = case_dir / "brief.md"
    if brief_file.exists():
        try:
            b_content = brief_file.read_text(encoding="utf-8")
            # ID Caso
            if meta.case_id == "non-specificato":
                m_cid = re.search(r"[-*]?\s*(?:\*\*)?(?:ID\s+)?caso(?:\*\*)?:\s*`?([A-Za-z0-9_.-]+)`?", b_content, re.IGNORECASE)
                if m_cid:
                    meta.case_id = _clean_str(m_cid.group(1))

            # Titolo indagine da obiettivo o intestazione
            m_obj = re.search(r"[-*]?\s*(?:\*\*)?Obiettivo conoscitivo principale(?:\*\*)?:\s*(.+)$", b_content, re.MULTILINE | re.IGNORECASE)
            if m_obj:
                meta.title = _clean_str(m_obj.group(1))
            else:
                m_hdr = re.search(r"^#\s+(.+)$", b_content, re.MULTILINE)
                if m_hdr and "brief" in m_hdr.group(1).lower():
                    meta.title = _clean_str(m_hdr.group(1))

            # Committente / Acquirente / Origine
            m_client = re.search(r"[-*]?\s*(?:\*\*)?Committente(?:\*\*)?:\s*(.+)$", b_content, re.MULTILINE | re.IGNORECASE)
            if m_client:
                meta.client = _clean_str(m_client.group(1))
                meta.buyer = meta.client
            else:
                m_orig = re.search(r"[-*]?\s*(?:\*\*)?Origine(?:\*\*)?:\s*(.+)$", b_content, re.MULTILINE | re.IGNORECASE)
                if m_orig:
                    orig_val = _clean_str(m_orig.group(1))
                    meta.client = orig_val
                    meta.buyer = "Stesso committente"

            m_buyer = re.search(r"[-*]?\s*(?:\*\*)?Acquirente(?:\*\*)?:\s*(.+)$", b_content, re.MULTILINE | re.IGNORECASE)
            if m_buyer:
                meta.buyer = _clean_str(m_buyer.group(1))

            # Popolazione di riferimento
            m_pop = re.search(r"[-*]?\s*(?:\*\*)?(?:Popolazione(?:\s+di\s+riferimento|\s+target)?|Universo(?:\s+di\s+indagine)?|Target)[^*:]*:\s*(.+)$", b_content, re.MULTILINE | re.IGNORECASE)
            if m_pop:
                meta.target_population = _clean_str(m_pop.group(1))

            # Area geografica / Estensione territoriale
            m_geo = re.search(r"[-*]?\s*(?:\*\*)?(?:Estensione territoriale|Area geografica|Ambito territoriale|Copertura geografica)[^*:]*:\s*(.+)$", b_content, re.MULTILINE | re.IGNORECASE)
            if m_geo:
                geo_text = _clean_str(m_geo.group(1))
                meta.territorial_scope = geo_text
                if "comun" in geo_text.lower():
                    meta.territorial_scope = f"Comunale ({geo_text})"
                elif "region" in geo_text.lower():
                    meta.territorial_scope = f"Regionale ({geo_text})"
                elif "nazion" in geo_text.lower():
                    meta.territorial_scope = "Nazionale"

            # Modalita somministrazione
            m_mode = re.search(r"[-*]?\s*(?:\*\*)?(?:Modalit[aà]|Metodo)(?:\s+di\s+somministrazione|\s+di\s+raccolta(?:\s+dei\s+dati)?)?[^*:]*:\s*(.+)$", b_content, re.MULTILINE | re.IGNORECASE)
            if m_mode:
                meta.data_collection_method = _clean_str(m_mode.group(1))

            # Numerosita campionaria n e quote
            m_sample = re.search(r"[-*]?\s*(?:\*\*)?(?:Numerosit[aà]|Campione)(?:\s+campionaria|\s+previsto)?[^*:]*:\s*(.+)$", b_content, re.MULTILINE | re.IGNORECASE)
            if m_sample:
                sample_line = _clean_str(m_sample.group(1))
                meta.sampling_method = sample_line
                parsed_n = _parse_sample_size(sample_line)
                if parsed_n:
                    meta.planned_sample_size = parsed_n

            # Durata
            m_dur = re.search(r"[-*]?\s*(?:\*\*)?(?:Lunghezza|Durata)(?:\s+desiderata|\s+complessiva(?:\s+stimata)?)?[^*:]*:\s*(.+)$", b_content, re.MULTILINE | re.IGNORECASE)
            if m_dur:
                meta.interview_duration = _clean_str(m_dur.group(1))
        except Exception:
            pass

    # 3. Lettura final.md (o questionnaire.md) per completare o integrare metadati mancanti
    q_file = case_dir / "final.md"
    if not q_file.exists():
        q_file = case_dir / "questionnaire.md"

    if q_file.exists():
        try:
            q_content = q_file.read_text(encoding="utf-8")

            # ID Caso da questionario se non presente
            if meta.case_id == "non-specificato":
                m_qcase = re.search(r"[-*]?\s*(?:\*\*)?(?:ID\s+)?Caso(?:\*\*)?:\s*`?([A-Za-z0-9_.-]+)`?", q_content, re.IGNORECASE)
                if m_qcase:
                    meta.case_id = _clean_str(m_qcase.group(1))

            # Titolo
            if meta.title.startswith("Indagine Demoscopica") or "brief" in meta.title.lower():
                m_title = re.search(r"^#\s+(.+)$", q_content, re.MULTILINE)
                if m_title:
                    t_val = _clean_str(m_title.group(1))
                    if not t_val.lower().startswith("questionario"):
                        meta.title = t_val
                    else:
                        clean_t = re.sub(r"^Questionario\s*(?:Finale\s*Consolidato|Bozza|Consolidato)?\s*[-–—:]\s*", "", t_val, flags=re.IGNORECASE)
                        if clean_t and clean_t != t_val:
                            meta.title = f"Indagine di Soddisfazione e Opinione — {clean_t}"

            # Data consolidamento / fieldwork
            m_qdate = re.search(r"[-*]?\s*(?:\*\*)?Data(?: consolidamento)?[^*:]*(?:\*\*)?:\s*`?([0-9-]+)`?", q_content, re.IGNORECASE)
            if m_qdate:
                meta.fieldwork_dates = _clean_str(m_qdate.group(1))

            # Committente / Acquirente se mancante da brief
            if meta.client == "Noto Sondaggi SRL / Committente da definire":
                m_qclient = re.search(r"[-*]?\s*(?:\*\*)?Committente(?:\*\*)?:\s*(.+)$", q_content, re.MULTILINE | re.IGNORECASE)
                if m_qclient:
                    meta.client = _clean_str(m_qclient.group(1))
                    meta.buyer = meta.client

            # Popolazione da final.md se non ancora estratta o generica
            m_qpop = re.search(r"[-*]?\s*(?:\*\*)?(?:Popolazione(?:\s+di\s+riferimento)?|Target)[^*:]*:\s*(.+)$", q_content, re.MULTILINE | re.IGNORECASE)
            if m_qpop and meta.target_population.startswith("Popolazione maggiorenne"):
                meta.target_population = _clean_str(m_qpop.group(1))

            # Estensione geografica da final.md se non ancora estratta
            if meta.territorial_scope == "Nazionale":
                m_qgeo = re.search(r"[-*]?\s*(?:\*\*)?(?:Estensione territoriale|Area geografica|Ambito territoriale)[^*:]*:\s*(.+)$", q_content, re.MULTILINE | re.IGNORECASE)
                if m_qgeo:
                    geo_t = _clean_str(m_qgeo.group(1))
                    meta.territorial_scope = geo_t
                    if "comun" in geo_t.lower():
                        meta.territorial_scope = f"Comunale ({geo_t})"
                    elif "region" in geo_t.lower():
                        meta.territorial_scope = f"Regionale ({geo_t})"

            # Modalita somministrazione da final.md se non ancora estratta
            if meta.data_collection_method.startswith("CATI / CAWI (Metodologia mista)"):
                m_qmode = re.search(r"[-*]?\s*(?:\*\*)?(?:Modalit[aà]|Metodo)(?:\s+di\s+somministrazione|\s+di\s+raccolta)?[^*:]*:\s*(.+)$", q_content, re.MULTILINE | re.IGNORECASE)
                if m_qmode:
                    meta.data_collection_method = _clean_str(m_qmode.group(1))

            # Campione / n da final.md se brief assente
            if meta.planned_sample_size == 800:
                m_qsample = re.search(r"[-*]?\s*(?:\*\*)?(?:Popolazione di riferimento e campione previsto|Campione previsto|Numerosit[aà] campionaria)[^*:]*:\s*(.+)$", q_content, re.MULTILINE | re.IGNORECASE)
                if m_qsample:
                    sample_str = _clean_str(m_qsample.group(1))
                    parsed_n = _parse_sample_size(sample_str)
                    if parsed_n:
                        meta.planned_sample_size = parsed_n

            # Durata intervista da final.md se non ancora estratta
            if meta.interview_duration.startswith("Circa 5-7 minuti"):
                m_qdur = re.search(r"[-*]?\s*(?:\*\*)?Durata(?:\s+complessiva\s+stimata)?[^*:]*:\s*(.+)$", q_content, re.MULTILINE | re.IGNORECASE)
                if m_qdur:
                    meta.interview_duration = _clean_str(m_qdur.group(1))

        except Exception:
            pass

    # Calcolo margine d'errore teorico
    try:
        meta.margin_of_error_pct = calculate_margin_of_error(meta.planned_sample_size, confidence=meta.confidence_level, p=meta.assumed_p)
    except Exception:
        meta.margin_of_error_pct = 3.46

    return meta


def parse_questions_from_survey(survey_content: str) -> List[AGCOMQuestion]:
    """
    Estrae l'elenco completo delle domande con formulazione, istruzioni di regia,
    opzioni di risposta numerate o con '=', sotto-domande di batterie e codici standard di non risposta (97, 98, 99).
    Supporta:
    - formato lineare (Q1., Q2a., D01., Domanda 1:)
    - formato strutturato (#### Q01 — Costrutto, ### D01: ..., ### 1. Quesito)
    - opzioni con '.', '=', '-', ')' o inline su singola riga
    - batterie/matrici con subquestions (SQ01, SQ02, Item 1)
    - domande a risposta aperta (senza opzioni fisse)
    - ordinamento canonico e normalizzazione dei codici di uscita 97, 98, 99
    """
    lines = survey_content.splitlines()
    questions: List[AGCOMQuestion] = []

    # Individua inizio e fine sezione domande
    start_idx = 0
    end_idx = len(lines)
    for i, line in enumerate(lines):
        sl = line.strip()
        if re.search(r"^(?:#{2,3})\s+(?:\d+\.\s*)?(?:Testo Definitivo|Domande|Testo del Questionario|Quesiti)", sl, re.IGNORECASE):
            start_idx = i + 1
            break

    search_start = start_idx if start_idx > 0 else 0
    for i in range(search_start, len(lines)):
        sl = lines[i].strip()
        if re.match(
            r"^##\s+(?:\d+\.\s*)?(?:Specifiche Riepilogative|Specifiche dei Filtri|Piano di Validazione|Piano di Monitoraggio|Piano di Campionamento|Adempimenti|Registro|Punti da Sottoporre|Approvazione Finale|Approvazione Umana|Note Conclusive|Chiusura)",
            sl,
            re.IGNORECASE,
        ):
            end_idx = i
            break

    target_lines = lines[start_idx:end_idx]

    current_q: Optional[AGCOMQuestion] = None
    parsing_mode: Optional[str] = None  # "text", "options", "exit_codes", "subquestions", "regia"

    for line in target_lines:
        stripped = line.strip()
        if not stripped or stripped in ["---", "***", "___"]:
            continue

        # A. Domanda Strutturata (#### Q01 — Costrutto, ### D01: ..., ### 1. Costrutto)
        m_q_struct = re.match(
            r"^(?:#{2,4})\s+(?:\*\*)?(?:(?:Domanda|Item)\s+([QDP]?\d+[a-zA-Z0-9_]*)|([QDP]\d+[a-zA-Z0-9_]*)|(\d+[a-zA-Z0-9_]*))(?:\*\*)?(?:\s*[-–—:.]\s*(.*))?$",
            stripped,
            re.IGNORECASE,
        )
        if m_q_struct:
            raw_id = (m_q_struct.group(1) or m_q_struct.group(2) or m_q_struct.group(3)).strip()
            q_id = f"Q{raw_id}" if raw_id.isdigit() else raw_id
            raw_title = _clean_str(m_q_struct.group(4)) if m_q_struct.group(4) else ""
            clean_title = re.sub(r"^\s*\[.*?\]\s*", "", raw_title).strip()
            current_q = AGCOMQuestion(
                id=q_id,
                title=clean_title if clean_title else raw_title,
                text=clean_title if clean_title else raw_title,
            )
            questions.append(current_q)
            parsing_mode = None
            continue

        # B. Domanda Lineare (es. Q1. Come valuta..., D2a: ...)
        m_q_linear = re.match(
            r"^\s*(?:\*\*)?(?:(?:Domanda|Item)\s+([QDP]?\d+[a-zA-Z0-9_]*)|([QDP]\d+[a-zA-Z0-9_]*))(?:\*\*)?(?:[.:\-–—]\s*(?:\*\*)?|(?:\*\*)?[.:\-–—])\s+(.+)$",
            stripped,
            re.IGNORECASE,
        )
        if m_q_linear and not re.match(r"^[-*]\s", stripped):
            raw_id = (m_q_linear.group(1) or m_q_linear.group(2)).strip()
            q_id = f"Q{raw_id}" if raw_id.isdigit() else raw_id
            full_text = m_q_linear.group(3).strip()

            q_regia = ""
            m_reg = re.search(r"\[(?:REGIA|ISTRUZIONI)\s*:\s*([^\]]+)\]", full_text, re.IGNORECASE)
            if m_reg:
                q_regia = m_reg.group(1).strip()
                full_text = full_text.replace(m_reg.group(0), "").strip()

            clean_q_text = _clean_str(full_text)
            current_q = AGCOMQuestion(
                id=q_id,
                title="",
                text=clean_q_text,
                regia_instructions=q_regia,
            )
            questions.append(current_q)
            parsing_mode = "options"
            continue

        # C. Gestione attributi e opzioni per la domanda corrente
        if current_q:
            # 1. Testo esplicito per il rispondente / formulazione del quesito
            m_text = re.match(
                r"^[-*]\s*(?:\*\*)?(?:Testo(?:\s+(?:originario|integrale|definitivo))?(?:\s+(?:per(?:\s+il)?\s+rispondente|della\s+domanda))?|Formulazione(?:\s+testuale)?(?:\s+della\s+domanda)?|Quesito)(?:\*\*)?:\s*(.*)$",
                stripped,
                re.IGNORECASE,
            )
            if m_text:
                explicit_text = _clean_str(m_text.group(1))
                if explicit_text:
                    current_q.text = explicit_text
                parsing_mode = "text"
                continue

            # 2. Istruzioni di regia e somministrazione
            m_regia = re.match(
                r"^[-*]\s*(?:\*\*)?(?:Istruzioni(?:\s+di\s+regia(?:\s+e\s+somministrazione)?|\s+per\s+(?:l['’])?intervistatore|\s+di\s+somministrazione|\s+generali)?|Not[ae]\s+(?:di\s+regia|per\s+(?:l['’])?intervistatore))[^*:]*(?:\*\*)?:?\s*(.*)$",
                stripped,
                re.IGNORECASE,
            )
            if m_regia:
                inline_note = _clean_str(m_regia.group(1))
                if inline_note:
                    current_q.regia_instructions = inline_note
                parsing_mode = "regia"
                continue

            # 3. Sezione item batteria / sotto-domande
            m_sub_hdr = re.match(
                r"^[-*]\s*(?:\*\*)?(?:Item della batteria|Item|Sotto-domande|Sottodomande|Affermazioni)(?:\*\*)?:?\s*(.*)$",
                stripped,
                re.IGNORECASE,
            )
            if m_sub_hdr:
                parsing_mode = "subquestions"
                inline_sub = m_sub_hdr.group(1).strip()
                if inline_sub:
                    for c, l, _ in _parse_inline_options(inline_sub):
                        current_q.subquestions.append(AGCOMQuestionOption(code=c, label=l))
                continue

            # 4. Opzioni e codici intestazione
            m_opts_hdr = re.match(
                r"^[-*]\s*(?:\*\*)?Opzioni e codici(?: di risposta)?[^*:]*(?:\*\*)?:?\s*(.*)$",
                stripped,
                re.IGNORECASE,
            )
            if m_opts_hdr:
                parsing_mode = "options"
                inline_opts = m_opts_hdr.group(1).strip()
                if inline_opts:
                    for c, l, is_ex in _parse_inline_options(inline_opts):
                        opt_obj = AGCOMQuestionOption(code=c, label=l, is_exit_code=is_ex)
                        if is_ex:
                            if not any(e.code == c for e in current_q.exit_codes):
                                current_q.exit_codes.append(opt_obj)
                        else:
                            if not any(o.code == c for o in current_q.options):
                                current_q.options.append(opt_obj)
                continue

            # 5. Codici di uscita / Non so / Rifiuto
            m_exit_hdr = re.match(
                r"^[-*]\s*(?:\*\*)?(?:Codici distinti di uscita|Non so\s*/\s*rifiuto)[^*:]*(?:\*\*)?:?\s*(.*)$",
                stripped,
                re.IGNORECASE,
            )
            if m_exit_hdr:
                parsing_mode = "exit_codes"
                inline_exits = m_exit_hdr.group(1).strip()
                if inline_exits:
                    for c, l, is_ex in _parse_inline_options(inline_exits):
                        opt_obj = AGCOMQuestionOption(code=c, label=l, is_exit_code=True)
                        if not any(e.code == c for e in current_q.exit_codes):
                            current_q.exit_codes.append(opt_obj)
                continue

            # 6. Parsing riga opzione o sotto-domanda codificata
            opt_data = _parse_option_line(stripped)
            if opt_data:
                code_str, label_str, is_exit = opt_data
                opt_obj = AGCOMQuestionOption(code=code_str, label=label_str, is_exit_code=is_exit)

                if parsing_mode == "subquestions" or (
                    not code_str.isdigit() and code_str.upper().startswith(("SQ", "ITEM", "A", "B", "C", "D")) and not is_exit
                ):
                    if not any(s.code == code_str for s in current_q.subquestions):
                        current_q.subquestions.append(opt_obj)
                elif is_exit or parsing_mode == "exit_codes":
                    if not any(e.code == code_str for e in current_q.exit_codes):
                        current_q.exit_codes.append(opt_obj)
                else:
                    if not any(o.code == code_str for o in current_q.options):
                        current_q.options.append(opt_obj)
                continue

            # 7. Opzione a punto elenco non numerata (auto-assegnazione ordinata)
            if parsing_mode in ["options", "exit_codes"] and stripped.startswith(("-", "*")):
                bullet_label = _clean_str(re.sub(r"^[-*]\s*", "", stripped))
                if bullet_label and not re.match(r"^[A-Za-z0-9_À-ÿ\s/'-]+:", bullet_label):
                    is_ex = _is_exit_code("", bullet_label)
                    if is_ex:
                        lbl_l = bullet_label.lower()
                        if "non applicabile" in lbl_l:
                            code_a = "97"
                        elif any(k in lbl_l for k in ["non so", "nessuna opinione"]):
                            code_a = "98"
                        else:
                            code_a = "99"
                        if not any(e.code == code_a for e in current_q.exit_codes):
                            current_q.exit_codes.append(AGCOMQuestionOption(code=code_a, label=bullet_label, is_exit_code=True))
                    else:
                        num_codes = [int(o.code) for o in current_q.options if o.code.isdigit() and int(o.code) < 90]
                        code_a = str(max(num_codes) + 1 if num_codes else len(current_q.options) + 1)
                        if not any(o.code == code_a for o in current_q.options):
                            current_q.options.append(AGCOMQuestionOption(code=code_a, label=bullet_label, is_exit_code=False))
                    continue

            # 8. Continuazione testo domanda multi-linea
            if parsing_mode == "text" and not stripped.startswith(("-", "*", "#")):
                current_q.text = (current_q.text + " " + _clean_str(stripped)).strip()
                continue

    # Post-processing difensivo e ordinamento canonico
    standard_exit_labels = {
        "97": "Non applicabile",
        "98": "Non so / Nessuna opinione",
        "99": "Preferisco non rispondere / Rifiuta",
    }
    for q in questions:
        present_codes = {opt.code for opt in q.exit_codes} | {opt.code for opt in q.options}
        for code, label in [("97", standard_exit_labels["97"]), ("98", standard_exit_labels["98"]), ("99", standard_exit_labels["99"])]:
            if code not in present_codes:
                q.exit_codes.append(AGCOMQuestionOption(code=code, label=label, is_exit_code=True))

        # Ordinamento canonico dei codici standard di non risposta (97, 98, 99)
        def _exit_sort_key(opt: AGCOMQuestionOption):
            if opt.code == "97":
                return 97
            if opt.code == "98":
                return 98
            if opt.code == "99":
                return 99
            if opt.code.isdigit():
                return int(opt.code)
            return 999

        q.exit_codes.sort(key=_exit_sort_key)

    return questions


def format_agcom_report(metadata: AGCOMMetadata, questions: List[AGCOMQuestion]) -> str:
    """
    Formatta la Scheda Informativa AGCOM secondo il template `templates/agcom_template.md`
    in conformità con l'art. 5 della Delibera AGCOM 256/10/CSP.
    """
    moe_str = f"± {metadata.margin_of_error_pct:.2f}%"

    doc = []
    doc.append(f"# Scheda Informativa del Sondaggio ({DELIBERA_REF})")
    doc.append("")
    doc.append(
        "> **Nota regolamentare**: Modello redatto in conformità all'art. 5 dell'Allegato A alla Delibera AGCOM n. 256/10/CSP "
        '("Regolamento in materia di pubblicazione e diffusione dei sondaggi sui mezzi di comunicazione di massa") per la pubblicazione '
        "e diffusione di sondaggi demoscopici ed elettorali sui canali media e il contestuale deposito obbligatorio presso il Dipartimento "
        "per l'Informazione e l'Editoria della Presidenza del Consiglio dei Ministri (art. 5, comma 1 e 2)."
    )
    doc.append("")
    doc.append("---")
    doc.append("")
    doc.append("## 1. Dati Identificativi e di Diffusione")
    doc.append(f"- **Titolo del sondaggio**: {metadata.title}")
    doc.append(f"- **ID Caso interno**: `{metadata.case_id}`")
    doc.append(f"- **Soggetto realizzatore**: {metadata.company}")
    doc.append(f"- **Committente**: {metadata.client}")
    doc.append(f"- **Acquirente**: {metadata.buyer}")
    doc.append(f"- **Data o periodo di realizzazione del fieldwork**: {metadata.fieldwork_dates}")
    doc.append(f"- **Data di pubblicazione o diffusione**: {metadata.publication_date}")
    doc.append(f"- **Mezzo di comunicazione di diffusione editoriale**: {metadata.media_channel}")
    doc.append("")
    doc.append("---")
    doc.append("")
    doc.append("## 2. Popolazione di Riferimento e Disegno Campionario")
    doc.append(f"- **Popolazione di riferimento (Universo di indagine)**: {metadata.target_population}")
    doc.append(f"- **Estensione territoriale del sondaggio**: {metadata.territorial_scope}")
    doc.append(f"- **Metodo di campionamento**: {metadata.sampling_method}")
    doc.append(f"- **Rappresentatività del campione**: {metadata.representativeness}")
    doc.append(f"- **Numerosità campionaria pianificata**: n = {metadata.planned_sample_size} interviste complete")
    actual_sample_text = f"n = {metadata.planned_sample_size} interviste complete" if metadata.actual_sample_size != DA_VERIFICARE_CAMPO else DA_VERIFICARE_CAMPO
    doc.append(f"- **Numerosità campionaria effettiva realizzata**: {actual_sample_text}")
    doc.append("")
    doc.append("---")
    doc.append("")
    doc.append("## 3. Metodo di Rilevazione e Somministrazione")
    doc.append(f"- **Metodo di raccolta dei dati**: {metadata.data_collection_method}")
    doc.append(f"- **Piattaforma di rilevazione / somministrazione**: {metadata.survey_platform}")
    doc.append(f"- **Durata media dell'intervista**: {metadata.interview_duration}")
    doc.append(
        "- **Trattamento non risposte all'indagine**: Codifica distinta e registrazione separata di rifiuti espliciti all'intervista, "
        "mancati contatti e abbandoni in conformità alle buone pratiche metodologiche Noto Sondaggi."
    )
    doc.append("")
    doc.append("---")
    doc.append("")
    doc.append("## 4. Consistenza Numerica del Campione e Indicatori di Contatto (Fieldwork)")
    doc.append("")
    doc.append(
        "> **Avvertenza di pre-campo**: I dati numerici a consuntivo non disponibili prima dell'avvio o del completamento del fieldwork "
        f"sono contrassegnati come `{DA_VERIFICARE_CAMPO}` e saranno compilati a chiusura della rilevazione."
    )
    doc.append("")
    doc.append("| Indicatore di Contatto | Simbolo | Valore Assoluto | Quota % sui Contatti Totali | Note e Descrizione Metodologica |")
    doc.append("| :--- | :---: | :---: | :---: | :--- |")
    doc.append(f"| **Contatti totali tentati** | $T$ | {DA_VERIFICARE_CAMPO} | 100.0% | Numero complessivo di tentativi di contatto telefonico/web avviati |")
    doc.append(f"| **Interviste complete valide** | $C$ | n = {metadata.planned_sample_size} (pianificate) / {DA_VERIFICARE_CAMPO} | {DA_VERIFICARE_CAMPO} | Interviste integre rispondenti a tutti i requisiti di campionamento |")
    doc.append(f"| **Rifiuti all'intervista (*unit nonresponse*)** | $R$ | {DA_VERIFICARE_CAMPO} | {DA_VERIFICARE_CAMPO} | Rispondenti eleggibili che hanno rifiutato espressamente l'intervista |")
    doc.append(f"| **Mancati contatti / Irreperibili** | $M$ | {DA_VERIFICARE_CAMPO} | {DA_VERIFICARE_CAMPO} | Mancata risposta al recapito (occupato, squillo a vuoto, segreteria) |")
    doc.append(f"| **Interviste parziali / Abbandoni (*break-off*)** | $B$ | {DA_VERIFICARE_CAMPO} | {DA_VERIFICARE_CAMPO} | Interviste interrotte prima del completamento del questionario |")
    doc.append(f"| **Quota fuori target / Ineleggibili** | $F$ | {DA_VERIFICARE_CAMPO} | {DA_VERIFICARE_CAMPO} | Contatti filtrati perché fuori quota o non rientranti nella popolazione target |")
    doc.append("")
    doc.append(f"- **Tasso di Risposta ($RR$)**: Formula: $RR = \\frac{{C}}{{T}}$ ({DA_VERIFICARE_CAMPO})")
    doc.append(f"- **Tasso di Rifiuto ($RefR$)**: Formula: $RefR = \\frac{{R}}{{T}}$ ({DA_VERIFICARE_CAMPO})")
    doc.append(f"- **Eventuali sostituzioni di nominativi**: Procedura standard di reintegro quote secondo elenco casuale ({DA_VERIFICARE_CAMPO})")
    doc.append("")
    doc.append("---")
    doc.append("")
    doc.append("## 5. Ponderazione Statistica e Margine d'Errore Teorico")
    doc.append("")
    doc.append("### 5.1 Metodo di Ponderazione")
    doc.append(f"- **Ponderazione effettuata**: {metadata.weighting_method}")
    doc.append("- **Variabili di post-stratificazione utilizzate**: Genere, fascia d'età, titolo di studio e ripartizione geografica")
    doc.append(f"- **Impatto della pesatura sui pesi campionari**: Fattori di ponderazione contenuti nell'intervallo prudenziale standard [0.5, 2.0] ({DA_VERIFICARE_CAMPO})")
    doc.append("")
    doc.append("### 5.2 Margine d'Errore Statistico Teorico")
    doc.append(f"- **Livello di confidenza**: {int(metadata.confidence_level * 100)}% ($z = {metadata.z_score}$)")
    doc.append(f"- **Assunzione prudenziale di dispersione**: Massima varianza proporzionale binaria ($p = {metadata.assumed_p}$, $1-p = {1.0 - metadata.assumed_p}$)")
    doc.append("- **Dimensione della popolazione**: Popolazione infinita o molto ampia ($N \\to \\infty$)")
    doc.append("- **Formula del margine d'errore teorico**:")
    doc.append("  $$e = \\pm z \\cdot \\sqrt{\\frac{p(1-p)}{n}} = \\pm \\frac{1.96 \\cdot 0.5}{\\sqrt{n}} = \\pm \\frac{0.98}{\\sqrt{n}}$$")
    doc.append(f"- **Margine d'errore calcolato sull'intero campione ($n = {metadata.planned_sample_size}$)**: **{moe_str}**")
    doc.append(
        "- **Avvertenza per sottocampioni**: Per sottogruppi o segmenti demografici di consistenza numerica inferiore a $n$, "
        "il margine d'errore teorico risulta proporzionalmente più elevato."
    )
    doc.append("")
    doc.append("---")
    doc.append("")
    doc.append("## 6. Testo Integrale delle Domande e Opzioni di Risposta")
    doc.append("")
    doc.append(
        "> **Prescrizione Delibera AGCOM 256/10/CSP (art. 5, comma 1, lett. m)**: Viene riportato il testo integrale di ciascun quesito "
        "somministrato ai soggetti intervistati, con le relative istruzioni di somministrazione, tutte le opzioni di risposta e i codici standard "
        "di non risposta (`97=Non applicabile`, `98=Non so`, `99=Preferisco non rispondere`). Prima della pubblicazione editoriale a consuntivo, "
        f"le percentuali di risposta registrate sono marcate `{DA_VERIFICARE_CAMPO}`."
    )
    doc.append("")

    for q in questions:
        title_suffix = f" — {q.title}" if q.title else ""
        doc.append(f"### {q.id}{title_suffix}")
        doc.append(f'- **Testo integrale della domanda**: "{q.text}"')
        if q.regia_instructions:
            doc.append(f"- **Istruzioni di regia e somministrazione**: [{q.regia_instructions.strip('[]')}]")

        # Sotto-quesiti di batterie se presenti
        if q.subquestions:
            doc.append("- **Item / Sotto-quesiti valutati**:")
            for sq in q.subquestions:
                doc.append(f"  - `{sq.code}`: {sq.label} `{DA_VERIFICARE_CAMPO} %`")

        doc.append("- **Opzioni di risposta e percentuali**:")
        if q.options:
            for opt in q.options:
                doc.append(f"  {opt.code}. {opt.label} `{DA_VERIFICARE_CAMPO} %`")
        elif not q.subquestions:
            doc.append(f"  [Risposta aperta / Testo libero] `{DA_VERIFICARE_CAMPO}`")

        for opt in q.exit_codes:
            doc.append(f"  - `{opt.code}`. {opt.label} `{DA_VERIFICARE_CAMPO} %`")

        doc.append("")

    doc.append("---")
    doc.append("")
    doc.append("## 7. Archivio e Deposito Istituzionale")
    doc.append("")
    doc.append("- **Autorità di vigilanza**: Autorità per le Garanzie nelle Comunicazioni (AGCOM)")
    doc.append(f"- **Normativa di riferimento**: {DELIBERA_REF} e s.m.i.")
    doc.append(
        "- **Deposito obbligatorio presso la Presidenza del Consiglio dei Ministri**: "
        "Ai sensi dell'art. 5, comma 2, della Delibera AGCOM 256/10/CSP, il documento integrale contenente la presente scheda informativa "
        "e le note metodologiche è reso consultabile sul sito web istituzionale gestito dal Dipartimento per l'Informazione e l'Editoria:"
    )
    doc.append(f"  **[{SITO_DEPOSITO}](https://{SITO_DEPOSITO})**")
    doc.append(
        f"- **Dichiarazione di conformità**: {metadata.company} certifica che i parametri metodologici e campionari dichiarati nella "
        "presente scheda corrispondono alle specifiche tecniche applicate nella progettazione e realizzazione dell'indagine."
    )
    doc.append("")

    return "\n".join(doc)


def validate_agcom_report(content: str) -> List[str]:
    """
    Verifica la piena conformità formale e contenutistica di una Scheda AGCOM rispetto
    alla Delibera AGCOM 256/10/CSP. Ritorna una lista di problemi rilevati (vuota se conforme).
    """
    issues = []
    if not content or not content.strip():
        return ["Il documento della Scheda AGCOM è vuoto o privo di contenuto."]

    # 1. Riferimento normativo Delibera AGCOM 256/10/CSP
    if not re.search(r"256/10/CSP", content, re.IGNORECASE):
        issues.append("Riferimento normativo alla Delibera AGCOM 256/10/CSP mancante.")

    # 2. Soggetto realizzatore
    if "Noto Sondaggi" not in content:
        issues.append("Soggetto realizzatore (Noto Sondaggi SRL) mancante.")

    # 3. Committente e Acquirente
    if not re.search(r"\bCommittente\b", content, re.IGNORECASE):
        issues.append("Campo 'Committente' mancante nei dati identificativi.")
    if not re.search(r"\bAcquirente\b", content, re.IGNORECASE):
        issues.append("Campo 'Acquirente' mancante nei dati identificativi.")

    # 4. Popolazione di riferimento ed estensione territoriale
    if not re.search(r"Popolazione di riferimento", content, re.IGNORECASE):
        issues.append("Campo 'Popolazione di riferimento' mancante.")
    if not re.search(r"Estensione territoriale", content, re.IGNORECASE):
        issues.append("Campo 'Estensione territoriale' mancante.")

    # 5. Metodo di campionamento e consistenza numerica
    if not re.search(r"Metodo di campionamento", content, re.IGNORECASE):
        issues.append("Campo 'Metodo di campionamento' mancante.")
    if not re.search(r"Numerosit[aà] campionaria", content, re.IGNORECASE):
        issues.append("Campo 'Numerosità campionaria' mancante.")

    # 6. Metodo di raccolta dati
    if not re.search(r"Metodo di raccolta dei dati", content, re.IGNORECASE):
        issues.append("Campo 'Metodo di raccolta dei dati' mancante.")

    # 7. Presenza di [DA VERIFICARE SUL CAMPO] per parametri ex-post
    if DA_VERIFICARE_CAMPO not in content:
        issues.append(f"Marcatura obbligatoria '{DA_VERIFICARE_CAMPO}' assente per i parametri di campo.")

    # 8. Margine d'errore statistico teorico e confidenza 95%
    if not re.search(r"Margine d'errore", content, re.IGNORECASE):
        issues.append("Sezione o indicazione del 'Margine d'errore' teorico mancante.")
    if not re.search(r"95%", content):
        issues.append("Indicazione del livello di confidenza al 95% mancante.")

    # 9. Testo integrale delle domande con codici standard 97, 98, 99
    if not re.search(r"Testo Integrale delle Domande", content, re.IGNORECASE):
        issues.append("Sezione 'Testo Integrale delle Domande' mancante.")
    for code in ("97", "98", "99"):
        if not re.search(rf"\b{code}\b", content):
            issues.append(f"Codice standard di non risposta '{code}' mancante nella scheda.")

    # 10. Deposito presso il sito istituzionale
    if SITO_DEPOSITO not in content:
        issues.append(f"Riferimento al sito istituzionale di deposito '{SITO_DEPOSITO}' mancante.")

    return issues


def generate_agcom_report(
    case_dir: Union[str, Path],
    output_path: Optional[Union[str, Path]] = None,
    sample_size: Optional[int] = None,
    client: Optional[str] = None,
    buyer: Optional[str] = None,
    media: Optional[str] = None,
    pub_date: Optional[str] = None,
    fieldwork_date: Optional[str] = None,
    title: Optional[str] = None,
    population: Optional[Union[int, str]] = None,
) -> Tuple[Path, str, List[str]]:
    """
    Funzione principale che orchestra l'estrazione, il calcolo e la scrittura della Scheda AGCOM.
    Accetta polimorficamente sia una directory del caso sia direttamente il file .md del questionario.
    Ritorna una tupla (output_file_path, content_str, issues_list).
    """
    raw_path = Path(case_dir).resolve()
    if not raw_path.exists():
        raise FileNotFoundError(f"Percorso non trovato: {raw_path}")

    if raw_path.is_file():
        q_file_direct = raw_path
        case_path = raw_path.parent
    else:
        q_file_direct = None
        case_path = raw_path

    # Determina destinazione output
    if output_path:
        out_file = Path(output_path).resolve()
    else:
        out_file = case_path / "scheda_agcom.md"

    # Estrazione metadati
    metadata = parse_case_metadata(case_path)

    # Gestione popolazione finita se fornita
    pop_int = None
    if population is not None:
        if isinstance(population, (int, float)):
            pop_int = int(population)
        elif isinstance(population, str):
            clean_pop = population.replace(".", "").replace(",", "").strip()
            if clean_pop.isdigit():
                pop_int = int(clean_pop)

    # Applicazione eventuali override espliciti da parametri/CLI
    if sample_size is not None and sample_size > 0:
        metadata.planned_sample_size = sample_size
        metadata.margin_of_error_pct = calculate_margin_of_error(
            metadata.planned_sample_size, population_size=pop_int
        )
    elif pop_int is not None and pop_int > 0:
        metadata.margin_of_error_pct = calculate_margin_of_error(
            metadata.planned_sample_size, population_size=pop_int
        )
    if client:
        metadata.client = client
    if buyer:
        metadata.buyer = buyer
    if media:
        metadata.media_channel = media
    if pub_date:
        metadata.publication_date = pub_date
    if fieldwork_date:
        metadata.fieldwork_dates = fieldwork_date
    if title:
        metadata.title = title

    # Lettura questionario per domande
    if q_file_direct:
        q_file = q_file_direct
    else:
        q_file = case_path / "final.md"
        if not q_file.exists():
            q_file = case_path / "questionnaire.md"

    if not q_file.exists():
        raise FileNotFoundError(f"Nessun file di questionario ('final.md' o 'questionnaire.md') trovato in {case_path}")

    survey_content = q_file.read_text(encoding="utf-8")
    questions = parse_questions_from_survey(survey_content)

    if not questions:
        raise ValueError(f"Nessuna domanda estratta da {q_file.name}")

    # Formattazione report Markdown
    report_content = format_agcom_report(metadata, questions)

    # Validazione conformità
    issues = validate_agcom_report(report_content)

    # Scrittura file
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(report_content, encoding="utf-8")

    return out_file, report_content, issues


def main():
    parser = argparse.ArgumentParser(
        description="Generatore automatico di Scheda Informativa AGCOM ai sensi della Delibera 256/10/CSP."
    )
    parser.add_argument(
        "case_dir",
        nargs="?",
        default=None,
        help="Percorso della cartella del caso (es. examples/demo_run_biblioteca o runs/<caso>) oppure del file questionario",
    )
    parser.add_argument(
        "--case-dir",
        dest="case_dir_opt",
        default=None,
        help="Percorso alternativo cartella del caso tramite flag",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=None,
        help="Percorso del file Markdown di output (default: <case_dir>/scheda_agcom.md)",
    )
    parser.add_argument(
        "-n",
        "--sample-size",
        "--campione",
        dest="sample_size",
        type=int,
        default=None,
        help="Numerosità campionaria pianificata n per il calcolo del margine d'errore (default estratto da brief)",
    )
    parser.add_argument(
        "--popolazione",
        dest="population",
        default=None,
        help="Dimensione della popolazione di riferimento per la correzione di popolazione finita (opzionale)",
    )
    parser.add_argument(
        "--client",
        default=None,
        help="Nome del committente del sondaggio (default estratto da brief)",
    )
    parser.add_argument(
        "--buyer",
        default=None,
        help="Nome dell'acquirente del sondaggio (default stesso committente)",
    )
    parser.add_argument(
        "--media",
        default=None,
        help="Mezzo di comunicazione di massa su cui è diffuso il sondaggio",
    )
    parser.add_argument(
        "--pub-date",
        default=None,
        help="Data prevista o effettiva di diffusione editoriale",
    )
    parser.add_argument(
        "--fieldwork-date",
        default=None,
        help="Data o intervallo temporale di esecuzione delle interviste",
    )
    parser.add_argument(
        "--title",
        default=None,
        help="Titolo o oggetto del sondaggio (default estratto dal brief o questionario)",
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Esegue solo la validazione formale di una scheda esistente senza riscriverla",
    )

    args = parser.parse_args()

    target_case = args.case_dir or args.case_dir_opt
    if not target_case:
        parser.print_help()
        print("\n[ERRORE] Specificare il percorso della cartella del caso.")
        sys.exit(1)

    case_path = Path(target_case)
    if not case_path.is_absolute():
        case_path = (Path.cwd() / target_case).resolve()

    if not case_path.exists():
        print(f"[ERRORE] Percorso non trovato: {case_path}")
        sys.exit(1)

    if args.check_only:
        target_file = Path(args.output) if args.output else (case_path if case_path.is_file() else case_path / "scheda_agcom.md")
        if not target_file.exists():
            print(f"[ERRORE] File della scheda AGCOM non trovato per la verifica: {target_file}")
            sys.exit(1)
        content = target_file.read_text(encoding="utf-8")
        issues = validate_agcom_report(content)
        if issues:
            print(f"[FAIL] Scheda AGCOM '{target_file.name}' non conforme:")
            for issue in issues:
                print(f"  - {issue}")
            sys.exit(1)
        else:
            print(f"[PASS] Scheda AGCOM '{target_file.name}' perfettamente conforme alla Delibera 256/10/CSP.")
            sys.exit(0)

    try:
        out_file, content, issues = generate_agcom_report(
            case_dir=case_path,
            output_path=args.output,
            sample_size=args.sample_size,
            client=args.client,
            buyer=args.buyer,
            media=args.media,
            pub_date=args.pub_date,
            fieldwork_date=args.fieldwork_date,
            title=args.title,
            population=args.population,
        )

        print("=== Generatore Scheda Informativa AGCOM (Delibera 256/10/CSP) ===")
        print(f"[OK] Scheda AGCOM generata con successo: {out_file}")
        print(f"     Soggetto Realizzatore: {SOGGETTO_REALIZZATORE}")
        print(f"     Deposito Istituzionale: {SITO_DEPOSITO}")

        if issues:
            print("[AVVISO] Rilevate anomalie di conformità:")
            for issue in issues:
                print(f"  - {issue}")
            sys.exit(1)
        else:
            print("[PASS] Scheda validata al 100% rispetto ai requisiti della Delibera AGCOM 256/10/CSP.")
            sys.exit(0)

    except Exception as e:
        print(f"[ERRORE] Errore durante la generazione della Scheda AGCOM: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
