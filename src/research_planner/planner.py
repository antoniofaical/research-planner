"""Limite de rodadas e proveniência controlados pelo programa, não pelo modelo."""

from copy import deepcopy

from .model import validate_reply
from .validation import text, validate_export


def build_plan(briefing, model, max_rounds=3, ask=None, tell=None):
    ask = input if ask is None else ask
    tell = print if tell is None else tell
    text(briefing, "briefing")
    if type(max_rounds) is not int or max_rounds < 0:
        raise ValueError("max_rounds deve ser inteiro >= 0.")
    context = {"briefing_markdown": briefing, "clarifications": []}
    pending = []
    asked = set()
    rounds = 0
    stopped = False
    while True:
        remaining = 0 if stopped else max_rounds - rounds
        tell("Elaborando plano..." if not rounds else "Atualizando plano com os esclarecimentos...")
        reply = validate_reply(model.generate(deepcopy(context), remaining))
        questions = reply["questions"]
        new_questions = [q for q in questions if q not in asked]
        if remaining == 0 or not new_questions:
            pending.extend(questions)
            break
        rounds += 1
        tell(f"Rodada {rounds}/{max_rounds}. Enter pula; /fim encerra os esclarecimentos.")
        for question in new_questions:
            answer = ""
            if not stopped:
                try:
                    answer = ask(question + "\n> ").strip()
                except EOFError:
                    stopped = True
                if answer == "/fim":
                    answer = ""
                    stopped = True
            context["clarifications"].append(
                {"round": rounds, "question": question, "answer": answer or None})
            asked.add(question)
            if not answer:
                pending.append(question)
    document = deepcopy(reply["plan"])
    for question in dict.fromkeys(pending):
        gap = f"Esclarecimento pendente: {question}"
        if gap not in document["gaps"]:
            document["gaps"].append(gap)
    document["request_context"] = context
    document["review_status"] = "pending"
    validate_export(document)
    return document
