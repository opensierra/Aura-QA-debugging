# -*- coding: utf-8 -*-
"""
DeepBlue.core_bluecode

Client for BlueCode server (HTTP REST).
"""

import json
import os
import shutil
import subprocess
import time
import requests

from .config import BC_PORT, BC_HOST, BC_TIMEOUT, LANGUAGE_TAG, LANGUAGE_REPORT, LANGUAGE_RULES

_QA_PROMPT = r"""You are a STRICT, ZERO-TOLERANCE localization QA auditor for smartphone screenshots. The text is UI copy captured directly from an Android phone screen (Vivo / Android device). Every region is on-screen interface text destined for the target market ({LANGUAGE_TAG}). Be MAXIMALLY AGGRESSIVE and PRECISE. Audit the ENTIRE interface in EVERY pass; do not self-limit to one dimension.

## MISSION
Find EVERY localization defect in the screenshot. A defect is any on-screen string that is wrong, missing, inconsistent, or non-compliant for the {LANGUAGE_TAG} market. Miss nothing. But every issue you report MUST be a real, verifiable defect with a precise fix — never a guess, never a rewrite, never a style opinion.

## AUDIT PROCEDURE (execute in order; do not skip any step)
1. ENUMERATE: List every region id present in the input. You must account for every region — audited, or explicitly dismissed as correct.
2. PER-REGION SWEEP: For each region, check it against EVERY category below. A single region can yield multiple issues (e.g. a spelling error AND a capitalization error).
3. CROSS-REGION CONSISTENCY: Compare regions against each other. Flag the same concept rendered differently (e.g. "Ajustes" vs "Configuración" for the same menu), inconsistent date/number/currency formats, or inconsistent terminology.
4. RULE COMPLIANCE: Check every region against the MANDATORY rules below. Any violation is a defect.
5. SELF-VERIFY: Before emitting each issue, run the SELF-VERIFICATION checklist. Drop any issue that fails it.

## CATEGORIES (define the defect precisely; pick the single best-fitting category)
- Spelling: misspelled word, wrong character, typo.
- Grammar: wrong agreement, conjugation, case, word order, missing/extra word.
- Punctuation: wrong/missing/extra punctuation, wrong spacing around it.
- Capitalization: wrong casing that violates the rules (NOT product names).
- Untranslated text: a string left in the source language that must be in {LANGUAGE_TAG}.
- Mistranslation: translated but wrong meaning, awkward, or incorrect.
- Improvement: correct but clearly suboptimal for the target market (only if a better standard form exists).
- Inconsistency: same concept rendered differently across regions.
- Format error: date/number/currency/phone format violates the rules.
- Tone: register/tone inappropriate for UI (too formal, too casual, imperative where not expected).
- Language mixture: source-language words leaking into {LANGUAGE_TAG} text (NOT product names).
- UI issues: truncation, overflow, overlap, or layout that breaks the text.
- OCR: (use ONLY in ocr_warnings, never in issues) recognition noise.
- Context: text that is wrong or misleading in its UI context.
- Typography: wrong characters, ligatures, non-breaking spaces, wrong quotes/dashes.
- Date format: date representation violates the rules.
- Currency: currency symbol/position/format violates the rules.
- Abbreviation: wrong or non-standard abbreviation.
- Gender: wrong grammatical gender agreement.
- Register: formality level wrong for the context.
- Terminology: non-standard or wrong term for the concept.

## SEVERITY CALIBRATION
- high: user-facing meaning is wrong, misleading, or the string is unusable (mistranslation, untranslated, wrong value).
- medium: clearly wrong but meaning is still recoverable (spelling, grammar, format, inconsistency).
- low: minor polish (capitalization, punctuation, tone, improvement).

## CONFIDENCE CALIBRATION
- high: the defect is unambiguous and the fix is certain.
- medium: the defect is clear but the best fix has a reasonable alternative.
- low: the defect is likely but depends on context you cannot fully see.

## MANDATORY ({LANGUAGE_TAG}) localization rules:
{LOCALIZATION_RULES}

## DO NOT FLAG (these are NOT localization defects — report them in ocr_warnings or not at all)
- Product names, feature names, brand names (e.g. "BOOST", "Game Mode", "Hub Pencari") — even if they look like English or unusual words. Intentional; keep as-is.
- OCR misreads or low-confidence text (regions with ctx=true or low score) — put in "ocr_warnings", NOT "issues".
- Minor capitalization of category labels or section headers.
- Any text already correct in {LANGUAGE_TAG} — do not "improve" correct text.
- Numbers, dates, currency that FOLLOW the rules — only flag if they VIOLATE them.

## SUGGESTION RULES
- The suggestion must be the SAME SCOPE as text_excerpt. One word in -> one word out. Short phrase in -> short phrase out.
- NEVER rewrite a full sentence to fix one word. The suggestion is a drop-in replacement, not a rewrite.
- The suggestion must be in {LANGUAGE_TAG} and must be a real, existing form (not a coinage).
- If you cannot produce a precise, same-scope drop-in replacement, do NOT flag the issue.

## SELF-VERIFICATION (every issue MUST pass all four, or drop it)
1. VERBATIM: Is text_excerpt copied EXACTLY from a region in the input? (If not, drop it.)
2. REAL: Is this a genuine defect that violates a rule or is objectively wrong — not a style preference? (If not, drop it.)
3. SAME-SCOPE: Is the suggestion the same scope as text_excerpt and a valid drop-in? (If not, drop it.)
4. LOCATABLE: Does the bbox match the affected region? (If not, fix the bbox or drop it.)

## OUTPUT
Reply ONLY with valid JSON, no markdown, no prose outside the JSON:
{
  "summary": "<specific summary in {LANGUAGE_REPORT} of ALL problems found in the screenshot>",
  "overall_quality": "excellent|good|acceptable|poor|critical",
  "issues": [{
    "text_excerpt": "<verbatim OCR text, EXACTLY as recognized>",
    "category": "Spelling|Grammar|Punctuation|Capitalization|Untranslated text|Mistranslation|Improvement|Inconsistency|Format error|Tone|Language mixture|UI issues|OCR|Context|Typography|Date format|Currency|Abbreviation|Gender|Register|Terminology",
    "severity": "high|medium|low",
    "suggestion": "<corrected text in {LANGUAGE_TAG}, precise drop-in replacement>",
    "explanation": "<1-2 short sentences in {LANGUAGE_REPORT}: what is wrong and the rule violated>",
    "bbox": {"x": 0, "y": 0, "width": 0, "height": 0},
    "region_ids": [0],
    "confidence": "high|medium|low"
  }],
  "ocr_warnings": []
}

## GENERAL RULES (all passes)
- ALL report text (summary, explanations, ocr_warnings) MUST be in {LANGUAGE_REPORT}.
- The "suggestion" field MUST be in {LANGUAGE_TAG} (it is a drop-in replacement of the on-screen UI text).
- Audit the WHOLE screenshot every time; do not restrict to a single category.
- ALWAYS populate "bbox" with the exact pixel coordinates {x,y,width,height} of the affected region (copy from the OCR input). Empty bbox = cannot be located.
- For each issue give a concrete drop-in correction, never vague advice.
- If a string is ambiguous, assume the worst-case and flag it.
- If nothing wrong at all, return empty issues and a positive note.
- Output ONLY the JSON, no extra prose.
"""



def _extract_json(text: str) -> dict:
    start = text.find("{")
    end = text.rfind("}") + 1
    if start != -1 and end > start:
        try:
            return json.loads(text[start:end])
        except json.JSONDecodeError:
            pass
    return {"error": "Could not parse response", "raw": text[:500]}


_QUALITY_ORDER = {
    "excellent": 0,
    "good": 1,
    "acceptable": 2,
    "poor": 3,
    "critical": 4,
}


def _build_prompt(ocr_regions: list, prior: dict | None = None) -> str:
    if isinstance(LANGUAGE_RULES, dict):
        rules = LANGUAGE_RULES.get(LANGUAGE_TAG, LANGUAGE_RULES.get("DEFAULT", ""))
    else:
        rules = LANGUAGE_RULES
    prompt = _QA_PROMPT.replace("{LANGUAGE_TAG}", LANGUAGE_TAG) \
        .replace("{LANGUAGE_REPORT}", LANGUAGE_REPORT) \
        .replace("{LOCALIZATION_RULES}", rules)
    prompt += (
        "\n\nREGIONES A AUDITAR (cada una trae 'score' de confianza del OCR y "
        "'ctx'=true si el score es bajo, lo que indica posible ruido de "
        "reconocimiento, no necesariamente un defecto de la interfaz):\n"
        + json.dumps(ocr_regions, ensure_ascii=False)
    )
    if prior:
        ctx = {
            "previous_quality": prior.get("overall_quality", ""),
            "previous_issues": prior.get("issues", []) or [],
            "previous_ocr_warnings": prior.get("ocr_warnings", []) or [],
        }
        prompt += (
            "\n\nHALLAZGOS DE PASADAS ANTERIORES (contexto de consistencia; el "
            "sistema ya los tiene en cuenta). Audita la captura COMPLETA de "
            "nuevo y reporta TODOS los defectos que veas con independencia; no "
            "trates de evitar repetir lo anterior. El sistema hace la union):\n"
            + json.dumps(ctx, ensure_ascii=False)
        )
    return prompt


def _issue_key(iss: dict) -> tuple:
    """Dedup key: same recognized text + same category = same defect, even if
    two passes phrased the suggestion differently. Tolerant of casing/space."""
    return (
        str(iss.get("text_excerpt", "")).strip().lower(),
        str(iss.get("category", "")).strip().lower(),
    )


def _merge_results(prev: dict | None, new: dict) -> dict:
    """UNION of findings across passes: any defect reported by ANY pass is kept
    (compensates for per-pass model inconsistency). Re-reported defects are
    enriched with refined fields from the later pass; nothing is ever dropped.
    Quality is the worst seen; OCR warnings accumulate."""
    if prev is None:
        merged = dict(new)
        merged["issues"] = list(new.get("issues", []) or [])
        return merged

    seen = {}
    issues = []
    for iss in prev.get("issues", []) or []:
        key = _issue_key(iss)
        seen[key] = iss
        issues.append(iss)
    for iss in new.get("issues", []) or []:
        key = _issue_key(iss)
        if key in seen:
            # Same defect re-reported: ENRICH (never delete). Prefer newer
            # non-empty values for the actionable fields.
            old = seen[key]
            for fld in ("suggestion", "explanation", "severity", "confidence"):
                nv = iss.get(fld)
                if nv not in (None, "", "N/A"):
                    old[fld] = nv
            if iss.get("bbox"):
                old["bbox"] = iss["bbox"]
            if iss.get("region_ids"):
                old["region_ids"] = iss["region_ids"]
        else:
            seen[key] = iss
            issues.append(iss)

    q_prev = _QUALITY_ORDER.get(str(prev.get("overall_quality", "")).lower(), 2)
    q_new = _QUALITY_ORDER.get(str(new.get("overall_quality", "")).lower(), 2)
    quality = new.get("overall_quality", prev.get("overall_quality", "N/A")) \
        if q_new >= q_prev else prev.get("overall_quality", "N/A")

    seen_w = set()
    ocr_warnings = []
    for w in (prev.get("ocr_warnings", []) or []) + (new.get("ocr_warnings", []) or []):
        key = str(w).strip().lower()
        if key and key not in seen_w:
            seen_w.add(key)
            ocr_warnings.append(w)

    return {
        "summary": new.get("summary", prev.get("summary", "N/A")),
        "overall_quality": quality,
        "issues": issues,
        "ocr_warnings": ocr_warnings,
    }


class BlueCodeACP:

    def __init__(self, port: int = BC_PORT, host: str = BC_HOST, timeout: int = BC_TIMEOUT):
        self.port = port
        self.host = host
        self.timeout = timeout
        self.url = None
        self._proc = None

    def start(self):
        if self.port == 0:
            import socket
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind((self.host, 0))
            self.port = s.getsockname()[1]
            s.close()

        self.url = f"http://{self.host}:{self.port}"

        exe = shutil.which("bluecode.cmd") or shutil.which("bluecode")
        if not exe:
            raise FileNotFoundError("bluecode is not found in PATH.")

        args = [exe, "serve", "--port", str(self.port), "--hostname", self.host]
        if exe.lower().endswith((".cmd", ".bat")):
            args = [os.environ.get("COMSPEC", "cmd.exe"), "/c", *args]

        self._proc = subprocess.Popen(args)
        self._wait_ready()

    def stop(self):
        if not self._proc:
            return
        if os.name == "nt":
            subprocess.run(["taskkill", "/F", "/T", "/PID", str(self._proc.pid)], capture_output=True)
        else:
            self._proc.terminate()
        self._proc = None

    def _wait_ready(self, timeout: int = 30):
        t0 = time.time()
        while time.time() - t0 < timeout:
            if self._proc.poll() is not None:
                raise RuntimeError(f"bluecode terminated with code {self._proc.returncode}")
            try:
                r = requests.get(f"{self.url}/global/health", timeout=1)
                if r.status_code == 200:
                    return
            except requests.RequestException:
                pass
            time.sleep(0.5)
        raise TimeoutError("The server did not respond at /global/health")

    def session_create(self) -> str:
        permissions = [
            {"permission": "read",  "pattern": "*", "action": "allow"},
            {"permission": "glob",  "pattern": "*", "action": "allow"},
            {"permission": "grep",  "pattern": "*", "action": "allow"},
            {"permission": "bash",  "pattern": "*", "action": "allow"},
            {"permission": "edit",  "pattern": "*", "action": "allow"},
        ]
        r = requests.post(f"{self.url}/session",
                          json={"title": "DeepBlue QA", "permission": permissions},
                          timeout=30)
        r.raise_for_status()
        return r.json()["id"]

    def send(self, session_id: str, prompt: str) -> dict:
        body = {"parts": [{"type": "text", "text": prompt}]}
        r = requests.post(f"{self.url}/session/{session_id}/message",
                          json=body,
                          timeout=self.timeout)
        if not r.ok:
            raise RuntimeError(f"POST /message devolvió {r.status_code}: {r.text[:1500]}")
        return r.json()

    def analyze(self, session_id: str, ocr_regions: list,
                 prior: dict | None = None) -> dict:
        prompt = _build_prompt(ocr_regions, prior)
        resp = self.send(session_id, prompt)
        parts = resp.get("parts", [])
        text = "".join(p.get("text", "") for p in parts if p.get("type") == "text")
        if not text:
            return {"error": "No text in the response", "raw": json.dumps(resp)[:1000]}
        return _extract_json(text)

    def analyze_multi_pass(self, session_id: str, ocr_regions: list,
                           passes: int = 3) -> dict:
        """Run the QA analysis several times. Each pass audits the WHOLE
        screenshot independently; the results are UNIONed (any defect caught by
        any pass is kept), which compensates for the model's inconsistency
        between runs. Nothing is ever deleted. Per-pass issue counts are tracked
        to surface coverage gain in the report."""
        merged = None
        pass_counts = []
        for i in range(passes):
            try:
                result = self.analyze(session_id, ocr_regions, prior=merged)
            except Exception as e:
                if merged is None:
                    return {
                        "error": f"QA pass 1 failed: {e}",
                        "summary": "N/A",
                        "overall_quality": "N/A",
                        "issues": [],
                    }
                break
            if isinstance(result, dict) and "error" not in result:
                pass_counts.append(len(result.get("issues", []) or []))
                merged = _merge_results(merged, result)
            elif merged is None:
                merged = result
        merged = merged or {
            "summary": "N/A",
            "overall_quality": "N/A",
            "issues": [],
        }
        merged["qa_passes"] = passes
        merged["qa_pass_counts"] = pass_counts
        return merged