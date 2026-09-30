"""CLI interativo de planejamento e renderização local após edição do JSON."""

import argparse
import sys
from pathlib import Path

from .config import load_config
from .export import export_files, export_plan, markdown
from .model import ModelError, OpenAIModel
from .planner import build_plan
from .validation import load_json, text, validate_export


def project_root():
    """Usa a raiz do checkout na instalação editável; fora dela, o diretório atual."""
    root = Path(__file__).resolve().parents[2]
    return root if (root / "src/research_planner/cli.py").is_file() else Path.cwd()


def parser():
    root = project_root()
    result = argparse.ArgumentParser(
        prog="research-planner",
        description="Planeje buscas; não execute coleta bibliográfica.",
    )
    commands = result.add_subparsers(dest="command", required=True)
    plan = commands.add_parser("plan", help="Gerar e revisar um plano interativamente")
    plan.add_argument(
        "briefing",
        nargs="?",
        type=Path,
        default=root / "user/user_prompt.md",
        help="Markdown UTF-8 (padrão: user/user_prompt.md)",
    )
    plan.add_argument("--config", type=Path, default=root / "configs.toml")
    render = commands.add_parser(
        "render", help="Validar JSON editado e gerar Markdown, sem modelo"
    )
    render.add_argument("plan_json", type=Path)
    for command in (plan, render):
        command.add_argument(
            "--output",
            type=Path,
            default=root / "user/output.md",
            help="Arquivo .md a sobrescrever (padrão: user/output.md), ou diretório NOVO",
        )
    return result


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    args = parser().parse_args(argv or ["plan"])
    try:
        file_output = args.output.suffix.lower() == ".md"
        if not file_output and args.output.exists():
            raise ValueError(
                "O diretório de saída já existe. Escolha outro para preservar seus arquivos."
            )
        if (
            args.command == "plan"
            and file_output
            and args.output.resolve() == args.briefing.resolve()
        ):
            raise ValueError("O briefing e a saída não podem ser o mesmo arquivo.")
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
            print(
                f"Modelo: {config.model}. Briefing e respostas serão enviados à OpenAI."
            )
            document = build_plan(briefing, model, config.max_clarification_rounds)
            print("\n" + markdown(document))
            try:
                reviewed = input("Revisão do plano concluída? [s/N] ").strip().lower()
            except EOFError:
                reviewed = ""
            if reviewed in ("s", "sim"):
                document["review_status"] = "reviewed"
        export = export_files if file_output else export_plan
        md_path, json_path = export(document, args.output)
        print(f"Arquivos: {md_path} e {json_path}")
        if document["review_status"] == "pending":
            print(
                "Revisão pendente: edite o JSON e use render para gerar uma nova versão."
            )
        return 0
    except KeyboardInterrupt:
        print("\nCancelado pelo analista.", file=sys.stderr)
        return 130
    except (OSError, ValueError, ModelError) as error:
        print(f"Erro: {error}", file=sys.stderr)
        return 2
