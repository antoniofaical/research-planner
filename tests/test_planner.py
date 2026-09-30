import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError, URLError

from research_planner.cli import main
from research_planner.config import Config, load_config
from research_planner.export import export_plan, markdown
from research_planner.model import ModelError, NoRedirect, OpenAIModel
from research_planner.planner import build_plan
from research_planner.validation import PLAN_KEYS, load_json, validate_export

ROOT = Path(__file__).resolve().parents[1]


def example():
    return load_json((ROOT / "examples" / "plan.json").read_text(encoding="utf-8"))


def reply(questions=()):
    document = example()
    return {"questions": list(questions), "plan": {k: document[k] for k in PLAN_KEYS}}


class FakeModel:
    def __init__(self, *replies):
        self.replies = iter(replies)
        self.calls = []

    def generate(self, context, remaining_rounds):
        self.calls.append((deepcopy(context), remaining_rounds))
        return deepcopy(next(self.replies))


class PlannerTests(unittest.TestCase):
    def test_sufficient_briefing_preserved_without_questions(self):
        briefing = (ROOT / "examples/estoque.md").read_text(encoding="utf-8")
        model = FakeModel(reply())
        result = build_plan(
            briefing,
            model,
            ask=lambda _: self.fail("Pergunta inesperada"),
            tell=lambda _: None,
        )
        validate_export(result)
        self.assertEqual(result["request_context"]["briefing_markdown"], briefing)
        self.assertEqual(result["request_context"]["clarifications"], [])
        self.assertEqual(result["review_status"], "pending")
        self.assertEqual(len(model.calls), 1)

    def test_unanswered_gap_survives_model_omission(self):
        final = reply()
        final["plan"]["gaps"] = []
        model = FakeModel(reply(["Qual setor?"]), final)
        result = build_plan(
            "Investigar estoque.", model, ask=lambda _: "", tell=lambda _: None
        )
        self.assertTrue(
            any(
                g.startswith("Verificar resolução: Qual setor?") for g in result["gaps"]
            )
        )
        self.assertNotIn("Esclarecimento pendente: Qual setor?", result["gaps"])
        self.assertIsNone(result["request_context"]["clarifications"][0]["answer"])
        self.assertIn("Qual setor?", markdown(result))

    def test_configured_round_limit_including_zero(self):
        for limit in (0, 1, 2, 3, 5):
            with self.subTest(limit=limit), tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / "configs.toml"
                path.write_text(
                    f"[planner]\nmax_clarification_rounds = {limit}\n", encoding="utf-8"
                )
                config = load_config(path)
                model = FakeModel(
                    *(reply([f"Pendência {i}?"]) for i in range(limit + 1))
                )
                answers = []

                def ask(prompt):
                    answers.append(prompt)
                    return "Informação do analista"

                result = build_plan(
                    "Estoque.",
                    model,
                    config.max_clarification_rounds,
                    ask,
                    lambda _: None,
                )
                self.assertEqual(len(answers), limit)
                self.assertEqual(
                    [c[1] for c in model.calls], list(range(limit, -1, -1))
                )
                self.assertEqual(
                    len(result["request_context"]["clarifications"]), limit
                )
                self.assertIn(
                    f"Esclarecimento pendente: Pendência {limit}?", result["gaps"]
                )

    def test_three_questions_are_one_round_and_answers_reach_model(self):
        model = FakeModel(reply(["Setor?", "País?", "Período?"]), reply())
        answers = iter(["Sem restrição", "Brasil", "Sem corte temporal"])
        result = build_plan(
            "Estoque.", model, 1, lambda _: next(answers), lambda _: None
        )
        history = result["request_context"]["clarifications"]
        self.assertEqual([h["round"] for h in history], [1, 1, 1])
        self.assertEqual(model.calls[1][0]["clarifications"], history)

    def test_finish_or_eof_preserves_all_unanswered_questions(self):
        for eof in (False, True):
            with self.subTest(eof=eof):
                model = FakeModel(reply(["Setor?", "País?"]), reply())

                def ask(_):
                    if eof:
                        raise EOFError
                    return "/fim"

                result = build_plan("Estoque.", model, ask=ask, tell=lambda _: None)
                self.assertEqual(model.calls[-1][1], 0)
                self.assertEqual(
                    [h["answer"] for h in result["request_context"]["clarifications"]],
                    [None, None],
                )
                self.assertTrue(
                    all(
                        any(q in g for g in result["gaps"]) for q in ["Setor?", "País?"]
                    )
                )

    def test_repeated_skipped_question_is_not_asked_again(self):
        model = FakeModel(reply(["Setor?"]), reply(["Setor?"]))
        prompts = []
        result = build_plan(
            "Estoque.",
            model,
            ask=lambda q: prompts.append(q) or "",
            tell=lambda _: None,
        )
        self.assertEqual(len(prompts), 1)
        self.assertEqual(
            sum(g.startswith("Verificar resolução: Setor?") for g in result["gaps"]), 1
        )
        self.assertNotIn("Esclarecimento pendente: Setor?", result["gaps"])

    def test_answered_repetition_does_not_create_gap_even_at_round_limit(self):
        for limit in (1, 3):
            with self.subTest(limit=limit):
                final = reply(["Qual país?"])
                final["plan"]["gaps"] = []
                model = FakeModel(reply(["Qual país?"]), final)
                prompts = []
                result = build_plan(
                    "Estoque.",
                    model,
                    limit,
                    lambda q: prompts.append(q) or "Brasil",
                    lambda _: None,
                )
                self.assertEqual(len(prompts), 1)
                self.assertEqual(result["gaps"], [])
                self.assertEqual(
                    result["request_context"]["clarifications"],
                    [{"round": 1, "question": "Qual país?", "answer": "Brasil"}],
                )
                self.assertEqual(len(model.calls), 2)

    def test_answered_repetition_and_new_question_at_limit(self):
        final = reply(["Qual país?", "Qual setor?"])
        final["plan"]["gaps"] = []
        model = FakeModel(reply(["Qual país?"]), final)
        result = build_plan("Estoque.", model, 1, lambda _: "Brasil", lambda _: None)
        self.assertEqual(result["gaps"], ["Esclarecimento pendente: Qual setor?"])
        self.assertEqual(model.calls[-1][1], 0)

    def test_answered_repetition_does_not_prevent_new_question_with_rounds_left(self):
        final = reply()
        final["plan"]["gaps"] = []
        model = FakeModel(
            reply(["Qual país?"]), reply(["Qual país?", "Qual setor?"]), final
        )
        prompts = []
        answers = iter(["Brasil", "Hospitalar"])

        def ask(question):
            prompts.append(question)
            return next(answers)

        result = build_plan("Estoque.", model, 3, ask, lambda _: None)
        self.assertEqual(prompts, ["Qual país?\n> ", "Qual setor?\n> "])
        self.assertEqual(result["gaps"], [])
        self.assertEqual(
            [h["answer"] for h in result["request_context"]["clarifications"]],
            ["Brasil", "Hospitalar"],
        )

    def test_skipped_question_cross_answer_requires_neutral_review(self):
        for later_round in (False, True):
            with self.subTest(later_round=later_round):
                final = reply(["Qual país?"])
                final["plan"]["gaps"] = []
                responses = (
                    [reply(["Qual país?"]), reply(["Qual setor?"]), final]
                    if later_round
                    else [reply(["Qual país?", "Qual setor?"]), final]
                )
                model = FakeModel(*responses)
                answers = iter(["", "Hospitalar, no Brasil."])
                result = build_plan(
                    "Estoque.", model, 2, lambda _: next(answers), lambda _: None
                )
                history = result["request_context"]["clarifications"]
                self.assertIsNone(history[0]["answer"])
                self.assertEqual(history[1]["answer"], "Hospitalar, no Brasil.")
                self.assertEqual(len(result["gaps"]), 1)
                self.assertTrue(
                    result["gaps"][0].startswith("Verificar resolução: Qual país?")
                )
                rendered = markdown(result)
                self.assertIn("verificar eventual resolução", rendered)
                self.assertNotIn("Sem resposta; permanece como lacuna.", rendered)
                self.assertNotIn("Esclarecimento pendente: Qual país?", rendered)
                self.assertEqual(model.calls[-1][0]["clarifications"], history)

    def test_unasked_final_question_and_skipped_question_keep_distinct_notices(self):
        final = reply(["Qual país?", "Qual período?"])
        final["plan"]["gaps"] = []
        result = build_plan(
            "Estoque.",
            FakeModel(reply(["Qual país?"]), final),
            1,
            lambda _: "",
            lambda _: None,
        )
        self.assertIn("Esclarecimento pendente: Qual período?", result["gaps"])
        self.assertTrue(
            any(g.startswith("Verificar resolução: Qual país?") for g in result["gaps"])
        )
        self.assertEqual(len(result["gaps"]), 2)

    def test_fully_undefined_plan_requires_gaps(self):
        minimal = {
            "central_question": None,
            "scope": {"inclusion": [], "exclusion": []},
            "subquestions": [],
            "concepts": [],
            "strategies": [],
            "gaps": ["Tema não definido."],
        }
        result = build_plan(
            "Pesquisar algo.",
            FakeModel({"questions": [], "plan": minimal}),
            tell=lambda _: None,
        )
        validate_export(result)
        result["gaps"] = []
        with self.assertRaises(ValueError):
            validate_export(result)

    def test_required_fields_and_nested_types(self):
        original = example()
        for key in original:
            with self.subTest(missing=key):
                broken = deepcopy(original)
                del broken[key]
                with self.assertRaises(ValueError):
                    validate_export(broken)
        for key in original["strategies"][0]:
            with self.subTest(strategy_missing=key):
                broken = deepcopy(original)
                del broken["strategies"][0][key]
                with self.assertRaises(ValueError):
                    validate_export(broken)
        for key, value in [
            ("status", "tested"),
            ("purpose", ""),
            ("destination", 12),
            ("expression", []),
        ]:
            with self.subTest(key=key):
                broken = deepcopy(original)
                broken["strategies"][0][key] = value
                with self.assertRaises(ValueError):
                    validate_export(broken)

    def test_missing_concepts_requires_gap_even_with_strategies(self):
        document = example()
        document.update(concepts=[], subquestions=[], gaps=[])
        with self.assertRaises(ValueError):
            validate_export(document)
        document["gaps"] = [
            "Decomposição conceitual ainda não definida; revisar os termos das estratégias."
        ]
        validate_export(document)

    def test_simple_question_does_not_require_subquestions_or_extra_synonyms(self):
        document = example()
        document["central_question"] = "Como a literatura define acurácia de estoque?"
        document["subquestions"] = []
        document["scope"]["exclusion"] = []
        document["concepts"] = [{"concept": "Acurácia de estoque", "synonyms": []}]
        document["gaps"] = []
        validate_export(document)

    def test_invalid_config_and_input(self):
        invalid = [
            "[planner]\nmax_clarification_rounds = -1",
            "[planner]\nmax_clarification_rounds = true",
            "[planner]\nmax_clarification_rounds = 1.5",
            "[planner]\nmax_rounds = 3",
            '[model]\nname = ""',
            "[model]\ntimeout_seconds = 0",
            "[model]\nmax_output_tokens = 0",
            "[unknown]\na = 1",
            "planner = 4",
            "invalid toml",
        ]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "configs.toml"
            for raw in invalid:
                with self.subTest(raw=raw):
                    path.write_text(raw, encoding="utf-8")
                    with self.assertRaises(ValueError):
                        load_config(path)
            path.write_text("", encoding="utf-8")
            self.assertEqual(load_config(path), Config())
        for bad in ("", "  ", None):
            with self.subTest(briefing=bad), self.assertRaises(ValueError):
                build_plan(bad, FakeModel())
        for raw in ('{"x": 1, "x": 2}', '{"x": NaN}'):
            with self.assertRaises(ValueError):
                load_json(raw)

    def test_export_pair_and_existing_artifact_preservation(self):
        document = example()
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "result"
            md, data = export_plan(document, output)
            self.assertEqual(load_json(data.read_text(encoding="utf-8")), document)
            self.assertEqual(md.read_text(encoding="utf-8"), markdown(document))
            before = data.read_bytes()
            with self.assertRaises(FileExistsError):
                export_plan(document, output)
            self.assertEqual(data.read_bytes(), before)

    def test_manual_example_matches_briefing_and_rendered_markdown(self):
        document = example()
        briefing = (ROOT / "examples/estoque.md").read_text(encoding="utf-8")
        self.assertEqual(document["request_context"]["briefing_markdown"], briefing)
        self.assertIn("Exemplo didático redigido manualmente", briefing)
        self.assertEqual(
            (ROOT / "examples/plan.md").read_text(encoding="utf-8"), markdown(document)
        )

    def test_cli_interactive_review_and_render_without_credentials(self):
        with (
            tempfile.TemporaryDirectory() as tmp,
            redirect_stdout(io.StringIO()),
            redirect_stderr(io.StringIO()),
        ):
            output = Path(tmp) / "run"
            model = FakeModel(reply(["Setor?"]), reply())
            with (
                patch("research_planner.cli.OpenAIModel", return_value=model),
                patch("builtins.input", side_effect=["Sem restrição", "s"]),
            ):
                code = main(
                    [
                        "plan",
                        str(ROOT / "examples/estoque.md"),
                        "--config",
                        str(ROOT / "configs.toml"),
                        "--output",
                        str(output),
                    ]
                )
            self.assertEqual(code, 0)
            document = load_json((output / "plan.json").read_text(encoding="utf-8"))
            self.assertEqual(document["review_status"], "reviewed")
            document["central_question"] = "Pergunta revista pelo analista?"
            (output / "plan.json").write_text(json.dumps(document), encoding="utf-8")
            with patch(
                "research_planner.cli.OpenAIModel",
                side_effect=AssertionError("Rede proibida"),
            ):
                self.assertEqual(
                    main(
                        [
                            "render",
                            str(output / "plan.json"),
                            "--output",
                            str(Path(tmp) / "edited"),
                        ]
                    ),
                    0,
                )
            self.assertIn(
                "Pergunta revista",
                (Path(tmp) / "edited/plan.md").read_text(encoding="utf-8"),
            )

    def test_cli_invalid_input_fails_before_model(self):
        with (
            tempfile.TemporaryDirectory() as tmp,
            redirect_stdout(io.StringIO()),
            redirect_stderr(io.StringIO()),
        ):
            empty = Path(tmp) / "empty.md"
            empty.write_text("", encoding="utf-8")
            with patch(
                "research_planner.cli.OpenAIModel",
                side_effect=AssertionError("Não chamar modelo"),
            ):
                self.assertEqual(
                    main(
                        [
                            "plan",
                            str(empty),
                            "--config",
                            str(ROOT / "configs.toml"),
                            "--output",
                            str(Path(tmp) / "run"),
                        ]
                    ),
                    2,
                )
                self.assertEqual(
                    main(
                        [
                            "plan",
                            "absent.md",
                            "--config",
                            str(ROOT / "configs.toml"),
                            "--output",
                            str(Path(tmp) / "run"),
                        ]
                    ),
                    2,
                )
            self.assertFalse((Path(tmp) / "run").exists())


class ModelTests(unittest.TestCase):
    def call(self, body):
        with (
            patch.dict("os.environ", {"OPENAI_API_KEY": "test-secret"}),
            patch("research_planner.model.build_opener") as opener,
        ):
            opener.return_value.open.return_value.__enter__.return_value.read.return_value = json.dumps(
                body
            ).encode()
            result = OpenAIModel(Config()).generate(
                {"briefing_markdown": "Estoque", "clarifications": []}, 3
            )
            request = opener.return_value.open.call_args.args[0]
            return result, json.loads(request.data)

    def test_responses_transport_and_no_tools(self):
        body = {
            "status": "completed",
            "output": [
                {"type": "reasoning", "summary": []},
                {
                    "type": "message",
                    "content": [{"type": "output_text", "text": json.dumps(reply())}],
                },
            ],
        }
        result, payload = self.call(body)
        self.assertEqual(result, reply())
        self.assertEqual(payload["model"], "gpt-6-sol")
        self.assertNotIn("tools", payload)
        self.assertNotIn("test-secret", json.dumps(payload))
        self.assertFalse(payload["store"])
        self.assertEqual(json.loads(payload["input"])["remaining_rounds"], 3)

    def test_refusal_incomplete_bad_json_and_bad_contract(self):
        for body in [
            {"status": "incomplete", "output": []},
            {
                "status": "completed",
                "output": [{"type": "message", "content": [{"type": "refusal"}]}],
            },
            {
                "status": "completed",
                "output": [
                    {
                        "type": "message",
                        "content": [{"type": "output_text", "text": "not json"}],
                    }
                ],
            },
            {
                "status": "completed",
                "output": [
                    {
                        "type": "message",
                        "content": [{"type": "output_text", "text": "{}"}],
                    }
                ],
            },
            {"status": "completed", "output": [None]},
        ]:
            with self.subTest(body=body), self.assertRaises(ModelError):
                self.call(body)

    def test_missing_key_and_transport_errors_redacted(self):
        with patch.dict("os.environ", {}, clear=True), self.assertRaises(ModelError):
            OpenAIModel(Config())
        for error in (
            HTTPError("url", 401, "test-secret", {}, None),
            URLError("test-secret"),
            TimeoutError("test-secret"),
        ):
            with (
                patch.dict("os.environ", {"OPENAI_API_KEY": "test-secret"}),
                patch("research_planner.model.build_opener") as opener,
            ):
                opener.return_value.open.side_effect = error
                with self.assertRaises(ModelError) as caught:
                    OpenAIModel(Config()).generate({}, 0)
                self.assertNotIn("test-secret", str(caught.exception))
        self.assertIsNone(
            NoRedirect().redirect_request(None, None, 302, "", {}, "https://elsewhere")
        )


if __name__ == "__main__":
    unittest.main()
