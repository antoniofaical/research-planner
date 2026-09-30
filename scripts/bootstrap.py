"""Rotina compartilhada pelos bootstraps Bash e PowerShell."""

import os
import subprocess
import sys
import venv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def ensure_user_files(root):
    user = root / "user"
    user.mkdir(exist_ok=True)
    for name in ("user_prompt.md", "output.md"):
        path = user / name
        try:
            with path.open("x", encoding="utf-8"):
                pass
        except FileExistsError:
            if not path.is_file():
                raise ValueError(f"Era esperado um arquivo em {path}.")


def run(root, python, *args):
    print("[EXEC]", python, *args, flush=True)
    subprocess.run([str(python), "-X", "utf8", *args], cwd=root, check=True)


def bootstrap(root=ROOT):
    if sys.version_info < (3, 11):
        raise ValueError("Python 3.11 ou superior é obrigatório.")
    environment = root / ".venv"
    python = environment / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    if not environment.exists():
        print("[ETAPA] Criar ambiente virtual .venv", flush=True)
        venv.EnvBuilder(with_pip=True).create(environment)
    if not python.is_file():
        raise ValueError(
            ".venv existente não contém Python. Revise essa pasta antes de recriá-la."
        )
    run(
        root,
        python,
        "-c",
        "import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)",
    )
    print(
        "[ETAPA] Preparar arquivos em user/ (preservar conteúdo existente)", flush=True
    )
    ensure_user_files(root)
    run(root, python, "-m", "pip", "install", "-e", ".[dev]")
    run(root, python, "-m", "pip", "check")
    run(
        root,
        python,
        "-m",
        "unittest",
        "discover",
        "-s",
        "tests",
        "-p",
        "test_*.py",
        "-v",
    )
    run(root, python, "-m", "ruff", "check", ".")
    run(root, python, "-m", "ruff", "format", "--check", ".")
    run(root, python, "-m", "research_planner", "--help")
    print("[OK] Ambiente preparado e verificações concluídas.", flush=True)
    print("Preencha user/user_prompt.md e defina OPENAI_API_KEY para gerar o plano.")
    if os.name == "nt":
        print(r"Execute: .\.venv\Scripts\python.exe -m research_planner")
    else:
        print("Execute: ./.venv/bin/python -m research_planner")
    print(
        "Saída: user/output.md e user/output.json (substituídos a cada geração bem-sucedida)."
    )


def main():
    try:
        bootstrap()
        return 0
    except KeyboardInterrupt:
        print("\nBootstrap cancelado.", file=sys.stderr)
        return 130
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        print(f"Erro no bootstrap: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
