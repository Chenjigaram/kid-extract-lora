from __future__ import annotations

import json

from ..schema import KidRecord

SYSTEM_PROMPT = (
    "You extract structured data from European fund disclosure documents "
    "(PRIIPs KID and UCITS KIID). Reply with one JSON object and nothing else. "
    "Copy values from the document; never infer, translate or calculate them. "
    "Use null for any field the document does not state."
)

FIELD_SPEC = """fund_name: string
isin: string
currency: 3-letter code
sri: integer 1-7, PRIIPs KID only
srri: integer 1-7, UCITS KIID only
ongoing_charges_pct: number, percent
entry_charge_pct: number, percent
exit_charge_pct: number, percent
transaction_costs_pct: number, percent
performance_fee_pct: number, percent
recommended_holding_period_years: number
investment_objective: string, copied verbatim
benchmark: string
domicile: string
management_company: string
scenarios: object with stress, unfavourable, moderate, favourable, each {value, return_pct}"""

USER_TEMPLATE = """Fields:
{fields}

Document:
{document}

JSON:"""


def build_messages(document: str, examples: list[tuple[str, str]] | None = None) -> list[dict[str, str]]:
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for example_document, example_target in examples or []:
        messages.append({"role": "user", "content": USER_TEMPLATE.format(fields=FIELD_SPEC, document=example_document)})
        messages.append({"role": "assistant", "content": example_target})
    messages.append({"role": "user", "content": USER_TEMPLATE.format(fields=FIELD_SPEC, document=document)})
    return messages


def target_json(record: KidRecord) -> str:
    return json.dumps(record.model_dump(mode="json"), ensure_ascii=False, separators=(",", ":"))


def parse_prediction(raw: str) -> dict | None:
    text = raw.strip()
    if text.startswith("```"):
        text = text.split("```")[1] if "```" in text[3:] else text[3:]
        text = text.removeprefix("json").strip()
    start = text.find("{")
    if start == -1:
        return None
    depth = 0
    for index in range(start, len(text)):
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
            if depth == 0:
                try:
                    return json.loads(text[start : index + 1])
                except json.JSONDecodeError:
                    return None
    return None
