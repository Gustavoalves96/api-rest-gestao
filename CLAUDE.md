# CLAUDE.md

Este arquivo orienta o Claude Code ao trabalhar neste repositório. Leia por completo antes de gerar ou alterar código.

## Visão geral do projeto

API REST para **gestão de estoque e pedidos** (domínio ERP). O objetivo é ser um projeto de portfólio que demonstra design de API limpo, camadas bem separadas, autenticação, testes e boas práticas de banco de dados.

Não é um projeto de brinquedo: trate-o como se fosse ir para produção. Prefira clareza e correção a atalhos.

## Stack

- **Python 3.12+**
- **FastAPI** — framework web
- **Pydantic v2** — validação e schemas
- **SQLAlchemy 2.0** (sintaxe nova, com `Mapped` / `mapped_column`) — ORM
- **Alembic** — migrations
- **PostgreSQL** — banco de dados (dev pode usar Docker; prod na Neon)
- **pytest** — testes
- **ruff** — lint + formatação
- **uv** — gerenciamento de dependências e ambiente

## Comandos

Use sempre `uv` para rodar comandos dentro do ambiente:

```bash
uv sync                         # instala dependências
uv run uvicorn app.main:app --reload   # sobe o servidor de dev
uv run pytest                   # roda todos os testes
uv run pytest tests/test_x.py -v   # roda um arquivo específico
uv run ruff check .             # lint
uv run ruff format .            # formata o código
uv run alembic revision --autogenerate -m "descrição"   # cria migration
uv run alembic upgrade head     # aplica migrations
```

Antes de considerar uma tarefa concluída, rode `uv run ruff check .` e `uv run pytest`. Ambos precisam passar.

## Estrutura de pastas

```
app/
  main.py            # instancia o FastAPI, registra routers e middlewares
  config.py          # settings via pydantic-settings (lê do .env)
  database.py        # engine, session, base declarativa
  models/            # modelos SQLAlchemy (uma tabela por arquivo)
  schemas/           # schemas Pydantic (Create, Update, Read separados)
  routers/           # endpoints agrupados por recurso
  services/          # regra de negócio (nada de lógica pesada nos routers)
  repositories/      # acesso a dados (queries isoladas aqui)
  auth/              # JWT, hashing, dependências de segurança
  exceptions.py      # exceções de domínio e handlers
tests/
  conftest.py        # fixtures (client de teste, DB de teste)
  ...
alembic/
```

## Arquitetura e convenções

**Camadas.** O fluxo é `router → service → repository → model`. O router só cuida de HTTP (validação de entrada, status, resposta). A regra de negócio fica no service. O acesso ao banco fica no repository. Não misture essas responsabilidades.

**Schemas.** Para cada recurso, separe schemas de entrada e saída: `ProdutoCreate`, `ProdutoUpdate`, `ProdutoRead`. Nunca exponha o modelo do ORM diretamente na resposta.

**Injeção de dependências.** Use o `Depends` do FastAPI para sessão de banco, usuário autenticado e services. Não instancie sessão manualmente dentro dos endpoints.

**Erros.** Levante exceções de domínio (ex.: `EstoqueInsuficienteError`) nos services e converta para respostas HTTP com handlers registrados em `main.py`. Não deixe `HTTPException` vazar para dentro dos services.

**Async.** Endpoints e acesso a banco são assíncronos (`async def`, `AsyncSession`). Seja consistente — não misture chamadas síncronas bloqueantes em rotas async.

**Tipagem.** Todo o código é tipado. Funções têm anotações de tipo em parâmetros e retorno.

## Banco de dados

- Toda alteração de modelo exige uma **migration via Alembic**. Nunca altere o schema na mão.
- Não use `Base.metadata.create_all()` fora de testes.
- Nomes de tabela no plural e em snake_case (`produtos`, `pedidos`, `itens_pedido`).
- Chaves primárias como `id` inteiro autoincremental, salvo motivo claro para UUID.
- Sempre defina `created_at` / `updated_at` nas tabelas principais.

## Testes

- Todo endpoint novo precisa de teste (caminho feliz + pelo menos um erro esperado).
- Services com regra de negócio relevante precisam de teste unitário.
- Use um banco de teste isolado (fixture em `conftest.py`), nunca o banco de dev.
- Prefira testar comportamento (o que a API responde) a testar implementação interna.

## Segurança

- Autenticação por **JWT**. Senhas com hash (bcrypt/argon2), nunca em texto puro.
- Segredos vêm de variáveis de ambiente via `config.py`. **Nunca** faça commit de `.env` nem hardcode credenciais.
- Valide e sanitize toda entrada via Pydantic. Não confie em dados do cliente.

## Estilo de código

- Siga o ruff (config no `pyproject.toml`). Não brigue com o formatador.
- Nomes descritivos em português ou inglês, mas **consistentes** dentro do projeto — escolha um e mantenha.
- Funções curtas e com responsabilidade única. Se um service passou de ~40 linhas, provavelmente dá pra quebrar.
- Evite comentários óbvios. Comente o "porquê", não o "o quê".

## Git

- Commits pequenos e descritivos, no imperativo (ex.: "adiciona endpoint de baixa de estoque").
- Não faça commit de código que não passa no lint ou nos testes.

## O que evitar

- Não instale dependências novas sem necessidade real — justifique antes.
- Não crie abstrações "para o futuro" que ainda não são usadas.
- Não coloque lógica de negócio em routers.
- Não exponha modelos do ORM nas respostas.

## Instruções para o assistente

- Ao começar uma tarefa, se algo estiver ambíguo, pergunte antes de assumir.
- Ao terminar, rode lint e testes e relate o resultado.
- Se precisar alterar o schema do banco, gere a migration correspondente.
- Ao criar um recurso novo, siga o padrão completo: model, schemas, repository, service, router e testes.
