"""Contrato pequeno, validado sem Pydantic ou JSON Schema."""

import json

PLAN_KEYS = {
    "central_question",
    "scope",
    "subquestions",
    "concepts",
    "strategies",
    "gaps",
}
EXPORT_KEYS = PLAN_KEYS | {"request_context", "review_status"}


def object_keys(value, keys, where):
    if not isinstance(value, dict) or value.keys() != keys:
        raise ValueError(f"{where}: campos esperados: {', '.join(sorted(keys))}.")


def text(value, where):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{where}: texto não vazio obrigatório.")


def texts(value, where):
    if not isinstance(value, list):
        raise ValueError(f"{where}: lista obrigatória.")
    for item in value:
        text(item, where)


def validate_plan(plan):
    object_keys(plan, PLAN_KEYS, "plano")
    if plan["central_question"] is not None:
        text(plan["central_question"], "central_question")
    object_keys(plan["scope"], {"inclusion", "exclusion"}, "scope")
    for key in ("inclusion", "exclusion"):
        texts(plan["scope"][key], f"scope.{key}")
    texts(plan["subquestions"], "subquestions")
    texts(plan["gaps"], "gaps")
    for key in ("concepts", "strategies"):
        if not isinstance(plan[key], list):
            raise ValueError(f"{key}: lista obrigatória.")
    for concept in plan["concepts"]:
        object_keys(concept, {"concept", "synonyms"}, "concepts[]")
        text(concept["concept"], "concept")
        texts(concept["synonyms"], "synonyms")
    for strategy in plan["strategies"]:
        object_keys(
            strategy, {"expression", "purpose", "destination", "status"}, "strategies[]"
        )
        for key in ("expression", "purpose"):
            text(strategy[key], key)
        if strategy["destination"] is not None:
            text(strategy["destination"], "destination")
        if strategy["status"] != "proposed_untested":
            raise ValueError("Toda expressão deve ter status proposed_untested.")
    if (
        plan["central_question"] is None
        or not plan["strategies"]
        or not plan["scope"]["inclusion"]
    ) and not plan["gaps"]:
        raise ValueError("Plano incompleto exige uma lacuna explícita em gaps.")


def validate_export(document):
    object_keys(document, EXPORT_KEYS, "documento")
    validate_plan({key: document[key] for key in PLAN_KEYS})
    if document["review_status"] not in ("pending", "reviewed"):
        raise ValueError("review_status deve ser pending ou reviewed.")
    context = document["request_context"]
    object_keys(context, {"briefing_markdown", "clarifications"}, "request_context")
    text(context["briefing_markdown"], "briefing_markdown")
    if not isinstance(context["clarifications"], list):
        raise ValueError("clarifications: lista obrigatória.")
    previous_round = 0
    for item in context["clarifications"]:
        object_keys(item, {"round", "question", "answer"}, "clarifications[]")
        if (
            type(item["round"]) is not int
            or not 1 <= item["round"] <= previous_round + 1
        ):
            raise ValueError("Rodadas devem ser positivas, consecutivas e ordenadas.")
        if item["round"] < previous_round:
            raise ValueError("Rodadas fora de ordem.")
        previous_round = item["round"]
        text(item["question"], "question")
        if item["answer"] is not None:
            text(item["answer"], "answer")


def load_json(raw):
    def unique_pairs(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"Campo JSON duplicado: {key}.")
            result[key] = value
        return result

    def reject_constant(value):
        raise ValueError(f"Constante JSON inválida: {value}.")

    return json.loads(
        raw, object_pairs_hook=unique_pairs, parse_constant=reject_constant
    )
