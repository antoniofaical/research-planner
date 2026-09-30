"""Markdown e JSON validados: arquivo substituível ou diretório novo."""

import json
import os
import tempfile
from pathlib import Path

from .validation import validate_export


def fenced(value):
    # O briefing/expressão pode conter cercas próprias.
    longest = max(
        (len(part) for part in value.splitlines() if part and set(part) == {"`"}),
        default=0,
    )
    fence = "`" * max(3, longest + 1)
    # Também protege cercas seguidas de um identificador de linguagem.
    while fence in value:
        fence += "`"
    return f"{fence}\n{value}\n{fence}"


def markdown(document):
    validate_export(document)
    reviewed = document["review_status"] == "reviewed"
    lines = [
        "# Plano de busca bibliográfica",
        "",
        "Revisão do analista: " + ("concluída." if reviewed else "pendente."),
        "",
        "Este plano contém propostas de investigação, não evidências ou conclusões. "
        "Todas as expressões são propostas ainda não testadas em bases reais. "
        "A revisão humana não altera esse status.",
        "",
        "## Pergunta central",
        "",
        document["central_question"] or "Pendente — consulte as lacunas.",
        "",
    ]

    def section(title, entries, empty="Não definido."):
        lines.extend([f"## {title}", ""])
        lines.extend([f"- {entry}" for entry in entries] or [empty])
        lines.append("")

    section("Inclusão proposta", document["scope"]["inclusion"])
    section("Exclusão proposta", document["scope"]["exclusion"])
    section("Subperguntas", document["subquestions"])
    section(
        "Conceitos e sinônimos candidatos",
        [
            f"{item['concept']}: "
            + ("; ".join(item["synonyms"]) or "sem sinônimos definidos")
            for item in document["concepts"]
        ],
    )
    lines.extend(["## Estratégias candidatas", ""])
    for number, strategy in enumerate(document["strategies"], 1):
        lines.extend(
            [
                f"### Expressão {number}",
                "",
                f"Finalidade: {strategy['purpose']}",
                "",
                f"Destino/tipo de fonte: {strategy['destination'] or 'não definido'}. "
                "Status: proposta não testada.",
                "",
                fenced(strategy["expression"]),
                "",
            ]
        )
    if not document["strategies"]:
        lines.extend(["Nenhuma expressão formulada; consulte as lacunas.", ""])
    section(
        "Lacunas pendentes", document["gaps"], "Nenhuma lacuna registrada nesta versão."
    )
    context = document["request_context"]
    lines.extend(
        [
            "## Contexto do solicitante — não verificado cientificamente",
            "",
            "Briefing original, preservado integralmente:",
            "",
            fenced(context["briefing_markdown"]),
            "",
            "### Esclarecimentos e decisões do analista",
            "",
        ]
    )
    for item in context["clarifications"]:
        lines.extend(
            [
                f"Rodada {item['round']} — {item['question']}",
                "",
                fenced(item["answer"])
                if item["answer"] is not None
                else "Sem resposta; permanece como lacuna.",
                "",
            ]
        )
    if not context["clarifications"]:
        lines.extend(["Nenhum esclarecimento registrado.", ""])
    return "\n".join(lines)


def export_plan(document, output: Path):
    rendered = markdown(document)
    serialized = (
        json.dumps(document, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    )
    # Um diretório novo impede apagar briefing, versões anteriores ou arquivos alheios.
    output.mkdir(parents=True, exist_ok=False)
    created = []
    try:
        for filename, content in (("plan.json", serialized), ("plan.md", rendered)):
            path = output / filename
            with path.open("x", encoding="utf-8", newline="\n") as file:
                created.append(path)
                file.write(content)
    except BaseException:
        for path in created:
            path.unlink(missing_ok=True)
        try:
            output.rmdir()
        except OSError:
            pass
        raise
    return output / "plan.md", output / "plan.json"


def export_files(document, output: Path):
    """Substitui o Markdown escolhido e o JSON de mesmo nome após validar o plano."""
    rendered = markdown(document)
    serialized = (
        json.dumps(document, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    )
    targets = ((output, rendered), (output.with_suffix(".json"), serialized))
    for path, _ in targets:
        if path.exists() and not path.is_file():
            raise ValueError(f"A saída deve ser um arquivo: {path}.")
    output.parent.mkdir(parents=True, exist_ok=True)
    staged = []
    try:
        for target, content in targets:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                newline="\n",
                dir=output.parent,
                prefix=f".{target.name}.",
                suffix=".tmp",
                delete=False,
            ) as file:
                staged.append((Path(file.name), target))
                file.write(content)
        for temporary, target in staged:
            os.replace(temporary, target)
    finally:
        for temporary, _ in staged:
            temporary.unlink(missing_ok=True)
    return output, output.with_suffix(".json")
