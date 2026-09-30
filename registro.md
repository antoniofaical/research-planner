# Registro de implementação e verificação

## Inspeção anterior às edições

- Repositório autorizado: `antoniofaical/research-planner`. Acesso confirmado
  pelo conector GitHub; branch padrão `main`, repositório público e vazio.
- `git ls-remote https://github.com/antoniofaical/research-planner.git` não
  retornou referências. O clone informou repositório vazio.
- `git status --short --branch`: nenhum commit em `main`, sem arquivos de
  trabalho preexistentes. `rg --files --hidden -g '!\.git/**'`: nenhum arquivo.
- Nenhum `AGENTS.md` encontrado no repositório nem nos diretórios ancestrais
  aplicáveis (`/`, `/workspace`, `/workspace/scratch`, diretório da tarefa).
- Não havia instruções locais adicionais, alterações ou artefatos a preservar.
  Não foi necessário consultar ou portar o `pilot-research-engine`.
- Escritas restritas a este repositório. Outros repositórios não foram alterados.

## Ambiente e decisões

- `python --version`: **Python 3.12.14**, disponível no ambiente Linux.
- Compatibilidade declarada: Python >= 3.11. Python 3.11 não estava instalado
  neste ambiente e não foi executado; a implementação utiliza APIs presentes em 3.11.
- `setuptools`: **84.0.0** no ambiente; projeto exige >= 68 apenas no build.
- Nenhuma dependência externa de execução. Validação explícita de dicionários,
  listas, tipos e campos obrigatórios, sem Pydantic ou JSON Schema.
- Padrão `gpt-6-sol`; integração HTTP com a API Responses, conforme documentação
  oficial vinculada no README. Sem ferramentas de busca e sem fallback de modelo.
- Não havia `OPENAI_API_KEY`. Nenhuma chamada real ao modelo foi realizada.
- Layout `src/research_planner`, comando `research-planner`, configuração em
  `configs.toml`, padrão de três rodadas. Sem timestamps no plano.
- Briefing e respostas humanas preservados integralmente em `request_context`;
  planos e expressões identificados como propostas, com revisão humana pendente.

## Arquivos entregues

- `pyproject.toml`, `.gitignore`, `configs.toml`: instalação e configuração.
- `src/research_planner/`: CLI, configuração, cliente do modelo, controle de
  rodadas, validação local e exportação Markdown/JSON.
- `examples/estoque.md`: briefing operacional genérico.
- `examples/plan.json`, `examples/plan.md`: plano didático manual, não gerado
  por chamada real nem validado em base bibliográfica.
- `tests/test_planner.py`: testes sem credencial e sem rede.
- `tests/live.py`: teste real opt-in, separado da descoberta automática padrão.
- `README.md`: instalação Linux/Windows, uso, contrato mínimo justificado,
  configuração, revisão, edição/reexportação, testes e limitações.
- `registro.md`: este registro.

## Comandos executados e resultados

Comandos executados na raiz do clone, salvo a inspeção inicial:

| Comando | Resultado observado |
| --- | --- |
| `python -m pip install --no-build-isolation -e .` | Instalado `research-planner 0.1.0`; build editável bem-sucedido. |
| `python -m unittest discover -s tests -p 'test_*.py' -v` | **15 testes passaram**, 0 falhas, 0 erros, 0 skips. |
| `/root/.local/bin/research-planner --help` | Comandos `plan` e `render` disponíveis. |
| `/root/.local/bin/research-planner render examples/plan.json --output runs/demo` | Exportou `runs/demo/plan.md` e `runs/demo/plan.json`. |
| `python -m unittest tests.live -v` | **1 teste pulado**: opt-in não habilitado; também não havia chave. Não conta como validação real do modelo. |
| `python -m compileall -q src tests` | Compilação sem erros. |
| `python -m pip wheel --no-deps --no-build-isolation . -w /tmp/research-planner-wheel` | Wheel construída com sucesso. |
| `python -m research_planner plan examples/estoque.md --output runs/no-key` | Saída 2 com orientação para definir `OPENAI_API_KEY`; nenhuma saída de plano criada. |
| `git diff --cached --check` | Sem erros de whitespace nos 19 arquivos preparados. |

O commit local foi criado. `git push -u origin main` falhou porque o terminal
não dispõe de credencial HTTPS para GitHub (`could not read Username`). A
publicação usa o conector GitHub autenticado: inicialização com o README,
seguida da árvore completa dos arquivos locais testados, commit e atualização
de `main` sem force. O commit local original é preservado em uma branch local.

O script instalou em `/root/.local/bin`, fora do PATH deste ambiente; por isso a
verificação usou o caminho absoluto. Em ambiente virtual, o comando fica disponível
após ativação; `python -m research_planner` também funciona.

`runs/demo/` e a wheel são artefatos de verificação local. Não são versionados;
os exemplos reproduzíveis ficam em `examples/`.

## O que a suíte verifica

1. Briefing suficiente: plano válido sem esclarecimentos, contexto integral e
   status de revisão pendente.
2. Lacuna persistente: resposta pulada permanece como lacuna mesmo quando a
   resposta simulada do modelo omite essa lacuna.
3. Limites lidos de TOML: **0, 1, 2, 3 e 5 rodadas**, com no máximo limite + 1
   chamadas e perguntas finais convertidas em lacunas.
4. Três perguntas contam como uma rodada; respostas exatas chegam ao modelo.
5. `/fim`, EOF e pergunta pulada repetida; nenhuma repetição literal ao usuário.
6. Plano completamente indefinido exige lacuna e não precisa inventar pergunta
   central, inclusão ou expressões.
7. Campos obrigatórios no JSON exportado e nas estratégias; status de busca
   testada, tipos inválidos, campos duplicados e constantes não JSON são rejeitados.
8. Briefing vazio, inexistente, TOML malformado, limites negativos/fracionários/
   booleanos, chaves desconhecidas, modelo vazio e limites de tokens/timeout inválidos.
9. Exportação dos dois formatos e recusa de sobrescrever diretório existente.
10. CLI completo com modelo simulado, esclarecimento, revisão, edição do JSON e
    reexportação sem instanciar o cliente de rede.
11. Transporte Responses simulado: seleção do modelo, extração do texto entre
    itens de raciocínio, nenhuma ferramenta de busca e `store=false`.
12. Recusa, resposta incompleta, JSON inválido, contrato inválido, chave ausente,
    erros HTTP/conexão/timeout e bloqueio de redirecionamento de credencial.

## Limites da verificação

Os testes locais comprovam comportamento do programa com respostas controladas,
não qualidade semântica de saídas reais. A primeira execução real depende da chave,
do acesso da conta a `gpt-6-sol` e da rede. O teste opt-in cobre contrato de uma
chamada, não avaliação científica nem conversação real de múltiplas rodadas.

Nenhuma busca foi executada em uma base real; sintaxe, sensibilidade e cobertura
das expressões permanecem não testadas. Alegações científicas ou especificidades
indevidas produzidas pelo modelo exigem revisão humana: o validador estrutural
não é um verificador factual. Markdown não é importado de volta para JSON.

Não há salvamento parcial da sessão antes da exportação nem retry automático;
falha de API/cancelamento exige reiniciar e repetir esclarecimentos. Isso mantém
o incremento pequeno, sem histórico de sessões ou infraestrutura adicional.

## Incremento: bootstraps e arquivos padrão

Inspeção inicial deste incremento: checkout limpo em `3446009`, `main` alinhada
ao remoto após `git fetch origin`, sem novas instruções locais. Os arquivos e
exemplos anteriores foram preservados; mudanças mecânicas nos fontes existentes
adequam imports e formatação às verificações Ruff agora exigidas.

Implementado:

- `bootstrap.sh` e `bootstrap.ps1` com comportamento equivalente, delegando a
  `scripts/bootstrap.py` para evitar divergência entre plataformas.
- Localização de Python >= 3.11, criação/reuso de `.venv`, instalação editável
  com `.[dev]`, `pip check`, testes locais, Ruff lint/formatação e CLI `--help`.
- Criação de `user/user_prompt.md` e `user/output.md` vazios se ausentes, sem
  alterar conteúdo preexistente ao executar novamente o bootstrap.
- Comando sem argumentos equivalente a `plan`, lendo `user/user_prompt.md` e
  substituindo `user/output.md` e `user/output.json` após geração válida. Na
  instalação editável, os padrões são resolvidos na raiz do checkout.
- Escritas preparadas em temporários antes de substituir cada arquivo de saída;
  conteúdo anterior inválido não impede overwrite. Briefing preservado.
- `--output arquivo.md` também sobrescreve seu par `.md`/`.json`; a opção anterior
  de diretório novo continua disponível. `user/` e cache Ruff ignorados pelo Git.
- Ruff fixado em **0.16.9** como dependência de desenvolvimento, sem nova
  dependência de execução. README atualizado com os dois fluxos de uso.

Verificações efetivamente executadas em Python 3.12.14 / Linux:

| Comando/cenário | Resultado |
| --- | --- |
| `python -m venv .venv` e `.venv/bin/python -m pip install -e '.[dev]'` | Ambiente e Ruff instalados. |
| `.venv/bin/python -m ruff check --fix .` e `ruff format .` | Imports e formatação ajustados durante desenvolvimento. O bootstrap apenas verifica. |
| `bash -n bootstrap.sh` | Sintaxe Bash válida. |
| `bash bootstrap.sh` com `.venv` já existente | Fluxo completo aprovado; arquivos de usuário criados. |
| `python -m unittest discover -s tests -p 'test_*.py' -v` via bootstrap | **22 testes passaram**, sem falhas/erros/skips. |
| `python -m pip check`, `python -m ruff check .`, `python -m ruff format --check .` via bootstrap | Todas as verificações passaram. |
| Bootstrap em cópia limpa, sem `.venv`, caminho com espaços e CWD externo | Ambiente criado e fluxo completo aprovado, incluindo os 22 testes. |
| `python -m research_planner render <exemplo>` nessa cópia, a partir de outro diretório | Exportou os padrões dentro de `user/` da cópia, substituindo o Markdown vazio. |
| `git diff --cached --check` | Sem erros de whitespace. |

Os sete novos testes cobrem defaults, overwrite de conteúdo arbitrário (incluindo
JSON inválido), preservação em falha do modelo/validação, recusa de usar o briefing
como saída, render sem API, criação repetível de arquivos e interrupção do bootstrap
quando uma etapa falha. Os testes existentes seguem passando.

**Limites:** não há PowerShell neste ambiente, portanto `bootstrap.ps1` não foi
executado nativamente. A rotina Python compartilhada foi executada integralmente;
isso não equivale a um teste do launcher no Windows. Não houve chamada real ao
modelo nem consultas bibliográficas neste incremento. Os bootstraps não fazem
chamadas ao modelo nem executam o teste opt-in pago.
