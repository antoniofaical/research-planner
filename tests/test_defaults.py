import io
import os
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

from research_planner.cli import main
from research_planner.export import export_files, markdown
from research_planner.model import ModelError
from research_planner.validation import load_json
from scripts.bootstrap import bootstrap, ensure_user_files
from tests.test_planner import FakeModel, example, reply


class DefaultFilesTests(unittest.TestCase):
    def test_no_arguments_reads_default_and_replaces_arbitrary_outputs(self):
        with tempfile.TemporaryDirectory() as tmp, redirect_stdout(io.StringIO()):
            root = Path(tmp)
            ensure_user_files(root)
            (root / "configs.toml").write_text("", encoding="utf-8")
            (root / "user/user_prompt.md").write_text(
                "Demanda real do analista.", encoding="utf-8"
            )
            (root / "user/output.md").write_bytes(b"\x00\xffconteudo antigo")
            (root / "user/output.json").write_text(
                "JSON anterior invalido", encoding="utf-8"
            )
            model = FakeModel(reply())
            with (
                patch("research_planner.cli.project_root", return_value=root),
                patch("research_planner.cli.OpenAIModel", return_value=model),
                patch("builtins.input", return_value=""),
            ):
                self.assertEqual(main([]), 0)
            document = load_json(
                (root / "user/output.json").read_text(encoding="utf-8")
            )
            self.assertEqual(
                document["request_context"]["briefing_markdown"],
                "Demanda real do analista.",
            )
            self.assertEqual(
                (root / "user/output.md").read_text(encoding="utf-8"),
                markdown(document),
            )
            self.assertEqual(
                (root / "user/user_prompt.md").read_text(encoding="utf-8"),
                "Demanda real do analista.",
            )

    def test_failed_generation_preserves_previous_output(self):
        with tempfile.TemporaryDirectory() as tmp, redirect_stderr(io.StringIO()):
            root = Path(tmp)
            ensure_user_files(root)
            (root / "configs.toml").write_text("", encoding="utf-8")
            (root / "user/user_prompt.md").write_text("Estoque.", encoding="utf-8")
            (root / "user/output.md").write_text("Anterior", encoding="utf-8")
            with (
                patch("research_planner.cli.project_root", return_value=root),
                patch(
                    "research_planner.cli.OpenAIModel",
                    side_effect=ModelError("Sem chave"),
                ),
            ):
                self.assertEqual(main([]), 2)
            self.assertEqual(
                (root / "user/output.md").read_text(encoding="utf-8"), "Anterior"
            )

    def test_explicit_markdown_overwrites_and_default_render_works(self):
        with tempfile.TemporaryDirectory() as tmp, redirect_stdout(io.StringIO()):
            root = Path(tmp)
            custom = root / "nested/custom.md"
            export_files(example(), custom)
            edited = example()
            edited["central_question"] = "Pergunta alterada?"
            export_files(edited, custom)
            self.assertIn("Pergunta alterada?", custom.read_text(encoding="utf-8"))
            with (
                patch("research_planner.cli.project_root", return_value=root),
                patch(
                    "research_planner.cli.OpenAIModel",
                    side_effect=AssertionError("Não chamar API"),
                ),
            ):
                self.assertEqual(main(["render", str(custom.with_suffix(".json"))]), 0)
            self.assertIn(
                "Pergunta alterada?",
                (root / "user/output.md").read_text(encoding="utf-8"),
            )
            self.assertEqual(list(custom.parent.glob("*.tmp")), [])

    def test_invalid_plan_and_directory_collision_preserve_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "output.md"
            output.write_text("Anterior", encoding="utf-8")
            with self.assertRaises(ValueError):
                export_files({}, output)
            output.with_suffix(".json").mkdir()
            with self.assertRaises(ValueError):
                export_files(example(), output)
            self.assertEqual(output.read_text(encoding="utf-8"), "Anterior")

    def test_input_cannot_be_overwritten_as_output(self):
        with tempfile.TemporaryDirectory() as tmp, redirect_stderr(io.StringIO()):
            path = Path(tmp) / "briefing.md"
            path.write_text("Demanda.", encoding="utf-8")
            with patch(
                "research_planner.cli.OpenAIModel",
                side_effect=AssertionError("Não chamar API"),
            ):
                self.assertEqual(main(["plan", str(path), "--output", str(path)]), 2)
            self.assertEqual(path.read_text(encoding="utf-8"), "Demanda.")


class BootstrapTests(unittest.TestCase):
    def test_repeated_setup_preserves_user_content(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ensure_user_files(root)
            for name in ("user_prompt.md", "output.md"):
                path = root / "user" / name
                self.assertEqual(path.read_bytes(), b"")
                path.write_text(f"Conteúdo em {name}", encoding="utf-8")
            ensure_user_files(root)
            for name in ("user_prompt.md", "output.md"):
                self.assertEqual(
                    (root / "user" / name).read_text(encoding="utf-8"),
                    f"Conteúdo em {name}",
                )

    def test_bootstrap_stops_on_failed_check(self):
        import subprocess

        with tempfile.TemporaryDirectory() as tmp, redirect_stdout(io.StringIO()):
            root = Path(tmp)
            python = (
                root
                / ".venv"
                / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
            )
            python.parent.mkdir(parents=True)
            python.touch()
            with patch("scripts.bootstrap.run") as run:
                run.side_effect = [
                    None,
                    subprocess.CalledProcessError(1, ["pip", "install"]),
                ]
                with self.assertRaises(subprocess.CalledProcessError):
                    bootstrap(root)
                self.assertEqual(run.call_count, 2)


if __name__ == "__main__":
    unittest.main()
