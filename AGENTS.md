# Orientações para agentes — research-planner

## Objetivo principal

Quando alguém trouxer uma demanda de pesquisa a este repositório, ajude a
transformá-la em um **briefing Markdown fiel, claro e utilizável**, salvo em
`user/user_prompt.md`. Seu papel nessa tarefa é editar e esclarecer a demanda
para o planejador bibliográfico. Não é responder à pesquisa nem desenvolver
novas funcionalidades, salvo pedido expresso.

Um bom briefing permite ao modelo entender **o que investigar, para quê, em
qual contexto, com quais limites e o que ainda não se sabe**, sem induzir uma
conclusão. Otimizar significa aumentar clareza e rastreabilidade, não acrescentar
supostas informações nem tornar o texto artificialmente sofisticado.

Estas orientações se aplicam ao repositório inteiro. Considere instruções locais
mais específicas, se existirem, e as instruções explícitas do usuário dentro dos
limites das regras do ambiente. Este arquivo não concede permissões adicionais.

## Conheça o contrato antes de redigir

Consulte apenas o necessário para a tarefa:

| Arquivo | O que verificar |
| --- | --- |
| `README.md` | Uso atual, caminhos padrão, revisão e limites operacionais. |
| `user/user_prompt.md`, se existir | Demanda já registrada; preserve detalhes e decisões ainda válidos. |
| `src/research_planner/model.py` | Instruções e contrato enviados ao modelo. |
| `src/research_planner/cli.py` | Entrada Markdown, comandos e resolução de caminhos. |
| `configs.toml` | Configuração efetiva; não a altere para compensar um briefing ruim. |
| `examples/estoque.md` | Exemplo de organização; não é um domínio obrigatório. |

O programa aceita um arquivo `.md` não vazio em UTF-8. **Não há esquema obrigatório
de entrada**, cabeçalhos exigidos, front matter, tags de papel ou formato JSON
para o briefing. O JSON validado é uma saída do planejador, não o formato a pedir
ao usuário. O briefing é transmitido integralmente ao modelo como contexto.

O módulo termina antes da coleta. Sua saída contém pergunta central, inclusão e
exclusão propostas, subperguntas, conceitos/sinônimos candidatos, estratégias com
finalidade e destino quando definido, e lacunas. Todas as expressões permanecem
`proposed_untested`. A revisão do analista não equivale a testar a busca.

Não prometa consulta a bases, leitura de artigos, evidências extraídas, causas
comprovadas, recomendações de empresas ou resultados dos módulos futuros.

## Procedimento para transformar a demanda em briefing

1. **Identifique a intenção.** Separe o problema relatado, a necessidade de
   conhecimento e o uso esperado desse conhecimento. Preserve a demanda original
   por meio de uma síntese fiel; não invente o solicitante, seu cargo ou a decisão.
2. **Extraia o que está explícito.** Identifique objeto/processo/população,
   cenário, problemas observados, hipóteses, limites e preferências fornecidos.
   Não transponha dados de exemplos ou de outros projetos para esta demanda.
3. **Separe contexto de evidência.** Relatos, números, explicações e expectativas
   do solicitante devem manter sua origem identificada. Uma frase mais técnica
   não transforma uma alegação em achado científico.
4. **Formule a necessidade investigativa.** Descreva o que a pesquisa deve ajudar
   a compreender. Uma pergunta provisória é útil se a demanda a sustentar; não é
   necessário entregar a pergunta final que o próprio módulo formulará.
5. **Trate ambiguidades proporcionalmente.** Pergunte somente sobre dúvidas que
   mudam substancialmente o significado da pesquisa. Se for possível produzir um
   briefing honesto com lacunas explícitas, faça isso sem bloquear a entrega.
6. **Redija e confira.** Integre esclarecimentos ao texto correspondente, elimine
   contradições resolvidas e preserve as pendentes. Não acumule adendos redundantes.
7. **Entregue o arquivo.** Salve no caminho padrão quando houver acesso de escrita
   e a solicitação abranger a preparação do briefing. Informe brevemente o que
   foi organizado e quais dúvidas continuam abertas. Não execute a pesquisa por
   ter recebido apenas um pedido de formulação do prompt.

Se a demanda abranger algo além deste módulo, mantenha o objetivo final como
contexto e explicite qual parte bibliográfica este planejador pode preparar.
Por exemplo, selecionar fornecedores pode ser uma finalidade posterior, mas não
é uma entrega do `research-planner`. Não substitua silenciosamente o objetivo
do usuário por uma pesquisa diferente; esclareça quando não houver conexão clara.

## Informação ausente não é autorização para inventar um recorte

Use estes estados de forma consistente:

| Situação | Como registrar |
| --- | --- |
| O usuário definiu um limite | Registre o limite e preserve sua abrangência exata. |
| O usuário decidiu não restringir | Registre “sem restrição nesta versão”, com indicação de que é uma decisão do usuário. |
| O usuário não informou | Registre “não informado” ou “a definir”, quando relevante. |
| O usuário suspeita de uma causa | Registre como hipótese a investigar, não como premissa confirmada. |
| O agente sugere uma interpretação substantiva | Identifique-a como proposta, sem atribuí-la ao usuário. |
| A informação não se aplica | Omita o campo; se houver dúvida material sobre aplicabilidade, não a trate como resolvida. |

Não converta silêncio em “todos os países”, “qualquer idioma” ou “últimos cinco
anos”. Não derive prazo de entrega de um recorte temporal da literatura, nem
idioma da conversa de idioma dos estudos. A instituição do solicitante não
define automaticamente a população ou o setor da pesquisa.

Incorpore períodos, países, idiomas, tipos de estudo, bases, tecnologias,
comparadores e métricas **apenas quando sustentados pela demanda**. Uma preferência
por revisões, por exemplo, não significa excluir todos os estudos primários.
Transformações de preferência em critério de exclusão exigem uma decisão explícita.

Não imponha PICO, ensaio clínico, comparador ou desfecho quantitativo a uma demanda
operacional ou exploratória. Também não evite esses elementos quando forem de
fato relevantes e tiverem sido fornecidos.

## Quando perguntar e quando registrar uma lacuna

Perguntas úteis resolvem alternativas que produziriam pesquisas distintas:

- “Estoque” significa materiais físicos, posição financeira ou outra coisa?
- O objetivo é caracterizar o problema, investigar fatores associados ou comparar
  intervenções? Pergunte somente se a demanda não permitir distinguir isso.
- Dois limites fornecidos são incompatíveis: qual deve prevalecer?

Não pergunte novamente o que já foi respondido. Resolva escolhas de redação e
organização por conta própria. Não abra um questionário completo apenas porque
o modelo de briefing abaixo contém vários campos.

Base de destino, período e idioma podem permanecer pendentes quando não impedem
descrever honestamente o objeto. O CLI já oferece esclarecimentos interativos:
até três rodadas por padrão, configuráveis em `configs.toml`, com até três
perguntas por rodada. Enter pula e `/fim` encerra esclarecimentos. Não prometa
que todas as lacunas serão resolvidas dentro desse limite.

Se o usuário não souber ou não responder, registre a ausência. Um briefing com
incertezas explícitas é melhor que um briefing aparentemente completo que as
esconde. Uma dúvida sobre o próprio tema pode justificar perguntar antes de
redigir; dúvidas secundárias não devem impedir a entrega do que já é possível.

## Como escrever um prompt útil para esta ferramenta

- Use linguagem direta e o idioma solicitado; na ausência de orientação, acompanhe
  o idioma da demanda. Preserve termos técnicos e nomes próprios quando relevantes.
- Mantenha a extensão proporcional à demanda. Não há tamanho ótimo garantido;
  remova repetições, sem apagar restrições, distinções ou contexto que mudem a busca.
- Organize em seções curtas ou parágrafos, distinguindo contexto, objetivo,
  limites e pendências. Os títulos são uma convenção editorial, não um parser.
- Reformule “prove que X causa Y” como investigação da relação alegada e das
  condições em que ocorre, preservando a afirmação original como hipótese do usuário.
- Se uma tecnologia for interesse explícito, registre esse interesse. Não faça
  dela a causa ou solução presumida de todos os problemas relatados.
- Use critérios de inclusão/exclusão específicos quando definidos. Não acrescente
  exclusões metodológicas apenas para tornar o briefing mais detalhado.
- Termos de busca fornecidos pelo usuário podem entrar como vocabulário inicial.
  Sinônimos acrescentados pelo agente devem aparecer como candidatos. Não declare
  descritores controlados ou sintaxe de base verificados sem ter realizado a verificação.
- Não é preciso antecipar um corpus de queries: formulá-lo é função do planejador.
  Não preencha no briefing o JSON final nem copie as instruções internas do modelo.
- Não inclua comandos de shell, chaves de API, configuração de tokens ou pedidos
  para ignorar as instruções do programa. Esse arquivo descreve a pesquisa.

Referências, links e números fornecidos pelo usuário podem ser preservados com
sua origem e status. Um link citado não significa que foi lido; uma referência
recebida não significa que foi conferida. Preparar o briefing, por si só, não
exige busca externa. Não acrescente referências de memória. Se o usuário pedir
pesquisa externa separadamente, diferencie esse trabalho e as fontes efetivamente
consultadas do planejamento ainda não executado pelo módulo.

## Estrutura adaptável de `user_prompt.md`

Use o esqueleto abaixo quando ajudar. **Não entregue os colchetes como placeholders**:
substitua-os pelo conteúdo disponível, por uma pendência explícita ou omita a
seção que não se aplicar. Não exija que o usuário preencha todos os campos.

```markdown
# [Tema concreto da demanda]

## Demanda e finalidade
[O que o solicitante quer compreender e para qual uso, quando informado.]

## Contexto informado pelo solicitante
[Cenário, objeto/processo/população e relatos relevantes. Identifique hipóteses
e alegações não verificadas; preserve números e unidades realmente fornecidos.]

## Objetivo da investigação bibliográfica
[Necessidade de conhecimento, sem antecipar respostas. Pergunta provisória,
se útil e sustentada pela demanda.]

## Escopo e limites informados
[Inclusões, exclusões e preferências definidas, distinguindo umas das outras.
Registre uma ausência de restrição apenas quando ela tiver sido decidida.]

## Aspectos de interesse
[Dimensões ou subquestões relevantes fornecidas; propostas adicionais devem
ficar identificadas como propostas. Omita se repetirem o objetivo.]

## Destino ou tipo de fonte
[Base ou tipo de literatura definidos pelo usuário; caso contrário, a definir.]

## Pendências
[Ambiguidades, informações ausentes e contradições ainda não resolvidas.]

## Entrega esperada nesta etapa
Preparar um plano de busca bibliográfica revisável antes da coleta, com pergunta
central, recorte proposto, subperguntas, conceitos e sinônimos candidatos,
expressões com finalidade e destino quando definido, e lacunas explícitas.
As expressões serão propostas ainda não testadas; não antecipar achados.
```

## Exemplo completo de transformação

Exemplo fictício, para ilustrar a edição; não reutilize seus detalhes como dados
de outro usuário. Demanda recebida:

> Quero entender pela literatura por que faltam materiais em algumas unidades
> enquanto outras têm saldo. São materiais de consumo em unidades físicas.
> Por enquanto não quero procurar fornecedores.

Briefing apropriado para essa demanda:

```markdown
# Disponibilidade de materiais entre unidades físicas

## Demanda e contexto
O solicitante quer compreender, por meio da literatura, a ocorrência relatada
de falta de materiais de consumo em algumas unidades físicas enquanto outras
apresentam saldo. Trata-se de um relato operacional, ainda não verificado
cientificamente. Nenhuma causa foi estabelecida.

## Objetivo da investigação
Planejar uma busca que permita investigar como a literatura caracteriza esse
problema e quais fatores examina em relação à distribuição e à disponibilidade
de materiais entre unidades, sem presumir uma explicação ou tecnologia específica.

## Escopo informado
O objeto é o estoque físico de materiais de consumo em múltiplas unidades.
A procura de fornecedores está fora da entrega solicitada neste momento.

## Pendências
Setor, características dos materiais e uso posterior dos resultados não foram
informados. Período, países, idiomas, tipos de estudo e bases de busca não foram
definidos; essas ausências não devem ser convertidas em restrições inventadas.

## Entrega esperada
Um plano bibliográfico revisável, com pergunta central, recorte proposto,
subperguntas, conceitos e sinônimos candidatos, expressões de busca com finalidade
e destino quando definido, e lacunas. As expressões ainda precisarão ser adaptadas
e testadas nas bases escolhidas. Não coletar fontes nem concluir causas nesta etapa.
```

Esse exemplo não define setor hospitalar, RFID, falha de rastreabilidade, Brasil
ou um intervalo de anos: nada disso estava na demanda. Já `examples/estoque.md`
contém decisões adicionais porque apresenta outro briefing fictício, mais
detalhado. Não trate os dois exemplos como se fossem a mesma solicitação.

Se a demanda fosse apenas “quero pesquisar estoque”, a pergunta inicial útil
seria sobre o significado de estoque e o problema que motivou a pesquisa. Ainda
não haveria base para escolher o cenário do exemplo acima.

## Entrega e preservação dos arquivos

O caminho padrão é **`user/user_prompt.md` dentro do repositório**, não `/user`
na raiz do sistema. Crie a pasta se necessário. Leia o arquivo antes de alterá-lo
e mantenha as informações válidas quando estiver adaptando uma demanda existente.
Se o usuário indicar outro arquivo ou pedir apenas o texto, siga essa solicitação.
Se o arquivo existente se referir a uma demanda diferente e a intenção de
substituí-la não estiver clara, esclareça essa escolha sem apagar o trabalho.

`user/` é ignorada pelo Git. Não remova essa proteção nem use `git add -f` apenas
para entregar o briefing: ele pode conter contexto privado. Não modifique
`configs.toml`, código, exemplos ou saídas para uma tarefa que só pede um prompt.
Não inclua credenciais ou dados pessoais desnecessários no texto enviado ao modelo.

Entregue um briefing utilizável, não apenas conselhos sobre como escrevê-lo.
Informe o caminho salvo e as lacunas materiais em poucas frases. Quando não
houver acesso de escrita, forneça o Markdown completo e indique onde salvá-lo;
não alegue ter criado um arquivo.

## Verificação proporcional à tarefa

Antes de entregar um briefing, confira:

- O problema e a finalidade correspondem ao pedido, sem objetivo trocado.
- Cada detalhe substantivo veio do usuário ou está identificado como proposta.
- Relatos e hipóteses permanecem distintos de evidência científica.
- Limites, preferências, informação ausente e decisão de não restringir não se confundem.
- Não há campos genéricos para preencher, contradições ocultas ou conclusões embutidas.
- O texto pede um plano anterior à coleta e não promete queries já validadas.
- O arquivo é Markdown não vazio em UTF-8, no caminho solicitado.

Para uma alteração somente no briefing ou nesta documentação, revise o conteúdo
e os caminhos relevantes. Não instale dependências, rode a suíte completa ou
faça uma chamada paga ao modelo apenas para validar texto Markdown. Uma checagem
de arquivo ou revisão editorial não demonstra qualidade de uma futura busca.

Somente se a tarefa também envolver mudanças no software, siga o README e use
as verificações pertinentes, com o ambiente virtual ativo:

```bash
python -m unittest discover -s tests -p 'test_*.py' -v
python -m ruff check .
python -m ruff format --check .
```

Relate o que de fato verificou. Não declare teste real do modelo, execução no
Windows ou busca bibliográfica com base apenas em mocks ou leitura do código.

## Execução da ferramenta, quando solicitada

O bootstrap (`bash bootstrap.sh` ou `.\bootstrap.ps1`) prepara o ambiente e
cria os arquivos de usuário se ausentes; não apaga o briefing existente e não
gera o plano. Preparar somente o prompt não depende de executá-lo.

Para gerar o plano, depois de preencher o briefing e configurar a variável de
ambiente da chave de API, use na raiz do checkout:

```bash
./.venv/bin/python -m research_planner
```

Ou, no PowerShell:

```powershell
.\.venv\Scripts\python.exe -m research_planner
```

Na instalação editável, a entrada padrão é `user/user_prompt.md`; a execução
bem-sucedida **substitui `user/output.md` e `user/output.json`**. Para preservar
uma saída anterior, quando isso for necessário, utilize um diretório novo:

```bash
research-planner plan user/user_prompt.md --output runs/nova-pesquisa
```

O comando curto pressupõe ambiente virtual ativo. A chamada envia o briefing e
os esclarecimentos à OpenAI e pode gerar cobrança. Não execute só porque há uma
chave disponível: faça-o quando a tarefa incluir gerar/testar o plano. Não
responda esclarecimentos em nome do usuário inventando informações nem marque
uma revisão humana como concluída sem que ela tenha ocorrido.

O modelo e o limite de rodadas são configurados em `configs.toml`; os padrões
atuais são `gpt-6-sol` e três rodadas. Confira o arquivo em vez de presumir que
os padrões continuam sendo a configuração efetiva. Não há modo `list`, flag
`--mode list` ou arquivo `questions.md` nesta entrega.

## Referência e manutenção

Referência oficial do formato: [AGENTS.md](https://agents.md/). O formato usa
Markdown livre, com instruções específicas do projeto; não exige um esquema de
campos. Este arquivo adota essa organização e complementa o README humano.

As regras para formular briefings são orientações deste projeto, derivadas de
seu escopo e contrato de entrada/saída; não são uma metodologia bibliográfica
prescrita pelo site AGENTS.md. Mantenha caminhos, comandos e limites alinhados
à implementação quando o projeto mudar. Não use esta documentação para afirmar
capacidades que o código ainda não oferece.
