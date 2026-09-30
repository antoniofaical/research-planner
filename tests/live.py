"""Opt-in: RUN_LIVE_MODEL_TEST=1 e a chave configurada; implica uso pago da API."""

import os
import unittest
from pathlib import Path

from research_planner.config import load_config
from research_planner.model import OpenAIModel
from research_planner.planner import build_plan
from research_planner.validation import validate_export

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(
    os.environ.get("RUN_LIVE_MODEL_TEST") == "1", "Teste real não habilitado"
)
class LiveModelTest(unittest.TestCase):
    def test_real_model_contract(self):
        config = load_config(ROOT / "configs.toml")
        if not os.environ.get(config.api_key_env):
            self.skipTest("Chave de API ausente")
        document = build_plan(
            (ROOT / "examples/estoque.md").read_text(encoding="utf-8"),
            OpenAIModel(config),
            max_rounds=0,
        )
        validate_export(document)
        self.assertTrue(document["strategies"])


if __name__ == "__main__":
    unittest.main()
