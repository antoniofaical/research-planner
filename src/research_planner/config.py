"""Configuração explícita; nenhum segredo é lido do TOML."""

import tomllib
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Config:
    max_clarification_rounds: int = 3
    model: str = "gpt-6-sol"
    api_key_env: str = "OPENAI_API_KEY"
    timeout_seconds: int = 180
    max_output_tokens: int = 12000

    def __post_init__(self):
        for name, minimum in (
            ("max_clarification_rounds", 0),
            ("timeout_seconds", 1),
            ("max_output_tokens", 1),
        ):
            value = getattr(self, name)
            if type(value) is not int or value < minimum:
                raise ValueError(f"{name} deve ser inteiro >= {minimum}.")
        for name in ("model", "api_key_env"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} deve ser texto não vazio.")


def load_config(path: Path) -> Config:
    with path.open("rb") as file:
        data = tomllib.load(file)
    allowed = {
        "planner": {"max_clarification_rounds"},
        "model": {"name", "api_key_env", "timeout_seconds", "max_output_tokens"},
    }
    if data.keys() - allowed.keys():
        raise ValueError("Seção desconhecida em configs.toml.")
    values = {}
    for section, keys in allowed.items():
        table = data.get(section, {})
        if not isinstance(table, dict) or table.keys() - keys:
            raise ValueError(f"Configuração inválida na seção {section}.")
        values.update(
            {("model" if key == "name" else key): value for key, value in table.items()}
        )
    return Config(**values)
