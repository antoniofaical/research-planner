"""CLI interativo de planejamento e renderização local após edição do JSON."""

import argparse
from pathlib import Path
import sys

from .config import load_config
from .export import export_plan, markdown
from .model import ModelError, OpenAIModel
from .planner import build_plan
from .validation import load_json, text, validate_export


def parser():
    result = argparse.ArgumentParser(prog="research-planner",
                                     description="Planeje buscas; não execute coleta bibliográfica.")
    commands = result.add_subparsers(dest="command", required=True)
    plan = commands.add_parser("plan", help="Gerar e revisar um plano interativamente")
    plan.add_argument("briefing", type=Path, help="Arquivo Markdown UTF-8")
    plan.add_argument("--config", type=Path, default=Path("configs.toml"))
    render = commands.add_parser("render", help="Validar JSON editado e gerar Markdown, sem modelo")
    render.add_argument("plan_json", type=Path)
    for command in (plan, render):
        command.add_argument("--output", type=Path, required=True, help="Diretório NOVO para plan.md e plan.json")
    return result


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        if args.output.exists():
            raise ValueError("O diretório de saída já existe. Escolha outro para preservar seus arquivos.")
        if args.command == "render":
            document = load_json(args.plan_json.read_text(encoding="utf-8-sig"))
            validate_export(document)
        else:
            config = load_config(args.config)
            if args.briefing.suffix.lower() != ".md":
                raise ValueError("O briefing deve ser um arquivo .md.")
            briefing = args.briefing.read_text(encoding="utf-8-sig")
            text(briefing, "briefing")
            model = OpenAIModel(config)
            print(f"Modelo: {config.model}. Briefing e respostas serão enviados à OpenAI.")
            document = build_plan(briefing, model, config.max_clarification_rounds)
            print("\n" + markdown(document))
            try:
                reviewed = input("Revisão do plano concluída? [s/N] ").strip().lower()
            except EOFError:
                reviewed = ""
            if reviewed in ("s", "sim"):
                document["review_status"] = "reviewed"
        md_path, json_path = export_plan(document, args.output)
        print(f"Arquivos: {md_path} e {json_path}")
        if document["review_status"] == "pending":
            print("Revisão pendente: edite o JSON e use render para gerar uma nova versão.")
        return 0
    except KeyboardInterrupt:
        print("\nCancelado pelo analista.", file=sys.stderr)
        return 130
    except (OSError, ValueError, ModelError) as error:
        print(f"Erro: {error}", file=sys.stderr)
        return 2
