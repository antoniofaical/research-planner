# research-planner

CLI Python independente para transformar um briefing Markdown em um **rascunho
revisável de plano de busca bibliográfica**. A única integração de rede é uma
chamada de geração à OpenAI. Não consulta bases, lê artigos, coleta evidências,
conclui causas ou recomenda empresas. Nenhum dos outros módulos é necessário.

## Instalação

Python **3.11 ou superior**; recomenda-se Python 3.12 nesta entrega, verificada
localmente em **3.12.14**. Não há dependências de execução externas à biblioteca
padrão. `setuptools>=68` é usado apenas para instalar o pacote.

Na raiz do repositório, Linux/macOS:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
export OPENAI_API_KEY='sua-chave'
research-planner plan examples/estoque.md --output runs/estoque
```

Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
$env:OPENAI_API_KEY = 'sua-chave'
research-planner plan .\examples\estoque.md --output .\runs\estoque
```

`python -m research_planner` é equivalente ao comando `research-planner` quando
o diretório dos scripts instalados não estiver no PATH. Use Python 3.11 nos
comandos de criação do ambiente se essa for sua versão instalada.

Para seu briefing real:

```bash
research-planner plan minha_demanda.md --config configs.toml --output runs/minha-pesquisa
```

Os caminhos são relativos ao diretório atual. A configuração deve existir; o
programa não ignora silenciosamente um caminho incorreto. A saída deve ser uma
pasta **nova**. Para outra versão, escolha outro nome.

## Esclarecimentos e revisão

1. O modelo recebe o briefing integral e propõe um plano provisório. Só deve
   perguntar se a ambiguidade impede uma formulação honesta.
2. Cada rodada contém até três perguntas. **Enter** deixa uma resposta pendente;
   **`/fim`** encerra esclarecimentos e solicita o plano com as lacunas restantes.
   EOF também encerra esclarecimentos. **Ctrl+C** cancela a execução.
3. O programa aplica o limite configurado; o modelo não consegue aumentá-lo.
   São no máximo `max_clarification_rounds + 1` chamadas. A última chamada recebe
   zero rodadas disponíveis. Perguntas que ainda aparecerem viram lacunas, sem
   novas solicitações humanas. Perguntas idênticas já feitas não são repetidas.
4. O plano completo aparece no terminal. Responder `s` à pergunta de revisão
   registra `review_status = "reviewed"`; Enter ou EOF mantém `pending`.
5. São exportados **`plan.md` e `plan.json`**. Ambos contêm as mesmas informações.
   Revisão concluída não significa evidência validada nem expressão testada.

Para alterar o conteúdo, edite o JSON em seu editor e reexporte:

```bash
research-planner render runs/minha-pesquisa/plan.json --output runs/minha-pesquisa-revisada
```

`render` valida todos os campos e gera os dois arquivos **sem modelo, chave ou
acesso de rede**. Após revisar, você pode mudar `review_status` para `reviewed`
no próprio JSON. Alterações posteriores exigem nova revisão; não há detecção
automática de edições. Markdown também é editável, mas suas alterações **não
retornam automaticamente ao JSON**. Para manter as duas versões sincronizadas,
edite o JSON e use `render`.

O briefing e os esclarecimentos são contexto declarado pelo solicitante, não
evidências científicas. Perguntas puladas permanecem em `gaps` mesmo se o modelo
as omitir. Ao editar manualmente, preserve esse histórico e documente como
resolveu qualquer lacuna; uma resposta textual não prova um fato científico.

## Configuração

```toml
[planner]
max_clarification_rounds = 3

[model]
name = "gpt-6-sol"
api_key_env = "OPENAI_API_KEY"
timeout_seconds = 180
max_output_tokens = 12000
```

Todos esses campos têm os padrões acima quando omitidos. Rodadas aceitam inteiro
>= 0; zero gera um rascunho com lacunas sem esclarecimentos, mantendo a revisão
interativa. Timeout e tokens devem ser inteiros positivos. Campos desconhecidos,
tipos incorretos e TOML malformado geram erro. A chave fica apenas na variável de
ambiente, nunca no arquivo de configuração. Não há carregamento automático de `.env`.

`name` aceita um identificador de modelo disponível **na API Responses da OpenAI**;
não há adaptadores para outros provedores. O padrão solicitado é `gpt-6-sol`,
sem troca silenciosa de modelo. A disponibilidade depende da conta. O briefing e
as respostas são enviados ao provedor, com `store=false` e sem ferramentas de
busca. Uma chamada pode ter custo. Erros de API, recusa, JSON inválido e resposta
incompleta encerram a execução com uma mensagem; não há retries automáticos.
Se houver truncamento, ajuste `max_output_tokens`. Respostas da sessão ainda não
exportada não são salvas em caso de falha ou cancelamento.

## Campos mínimos e justificativa

| Campo | Finalidade |
| --- | --- |
| `request_context.briefing_markdown` | Preservar integralmente a demanda e a origem das alegações. |
| `request_context.clarifications` | Registrar rodada, pergunta e resposta humana; `null` indica ausência de resposta. |
| `review_status` | Distinguir rascunho de uma versão que o analista declarou revisada. |
| `central_question` | Explicitar o objetivo; `null` quando não for possível formulá-lo honestamente. |
| `scope.inclusion` / `scope.exclusion` | Tornar o recorte proposto visível e editável. |
| `subquestions` | Dividir a pergunta central em questões investigáveis. |
| `concepts` | Relacionar cada conceito a uma lista de sinônimos candidatos. |
| `strategies` | Associar expressão, finalidade, destino e status. |
| `gaps` | Registrar decisões e informações pendentes sem preenchê-las por suposição. |

Cada estratégia exige `expression`, `purpose`, `destination` (texto ou `null` se
indefinido) e `status`, sempre **`proposed_untested`**. Todos os campos da tabela
são obrigatórios no JSON, inclusive listas vazias quando justificadas. Um plano
sem pergunta central, inclusão ou expressões exige lacuna explícita. O contrato
rejeita campos desconhecidos, chaves duplicadas, tipos inválidos e status de
busca testada. Não inclui timestamps, IDs universais ou JSON Schema.

Validação estrutural não prova adequação científica, completude dos sinônimos,
ausência de alucinação ou compatibilidade de sintaxe com uma base. O analista
precisa revisar o conteúdo e depois adaptar/testar as buscas no destino escolhido.
O programa não executa essa etapa.

## Exemplo demonstrável sem credencial

`examples/estoque.md` contém uma demanda operacional genérica. `examples/plan.json`
e `examples/plan.md` são um **exemplo didático redigido manualmente**, não uma
execução real do modelo ou resultado de busca. Para demonstrar validação/exportação:

```bash
research-planner render examples/plan.json --output runs/demo
```

Para gerar outro plano com o modelo, use `plan examples/estoque.md` como mostrado
na instalação. O resultado real é variável e requer revisão.

## Testes

Sem credenciais ou rede:

```bash
python -m unittest discover -s tests -p 'test_*.py' -v
```

Testam briefing suficiente, lacuna persistente, limites de rodadas, respostas
humanas enviadas ao modelo, `/fim`, EOF, entradas/configurações inválidas, contrato
JSON, revisão e reexportação, preservação de arquivos e transporte HTTP simulado.

Teste real separado e opt-in, sujeito a custo, usando `configs.toml`:

```bash
RUN_LIVE_MODEL_TEST=1 python -m unittest tests.live -v
```

No PowerShell:

```powershell
$env:RUN_LIVE_MODEL_TEST = '1'
python -m unittest tests.live -v
```

Esse teste só chama o modelo com a chave configurada presente. Verifica o contrato
em uma chamada sem esclarecimentos; não avalia a qualidade científica do plano nem
testa buscas. Veja **`registro.md`** para a execução efetivamente realizada.

## Organização e escolhas

`src/research_planner/` separa configuração, cliente HTTP, planejamento, validação,
exportação e CLI. `tests/` contém a suíte local e o teste real opcional; `examples/`
contém o briefing e o plano didático.

A biblioteca padrão (`argparse`, `tomllib`, `urllib`, `json`, `unittest`) basta
para esta entrega. Isso reduz instalação e dependências, ao custo de manter um
pequeno cliente HTTP e validadores explícitos. O JSON é solicitado no prompt e
validado localmente; o programa falha claramente se o modelo descumprir o contrato,
em vez de tentar reparar a resposta ou depender de geração de JSON Schema.

Referências da integração consultadas na implementação:

- [GPT-6 Sol — identificador e endpoint](https://developers.openai.com/api/docs/models/gpt-6-sol)
- [Text generation — entrada e leitura de output da API Responses](https://developers.openai.com/api/docs/guides/text)

Não há modo `list`, `--mode list`, `questions.md`, banco de dados, coleta,
arquitetura herdada do Research Engine ou componentes dos módulos futuros.
