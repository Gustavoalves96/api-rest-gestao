<h1 align="center">API REST — Gestão de Estoque e Pedidos</h1>

<p align="center">
  API REST de domínio ERP para gestão de <strong>estoque</strong> e <strong>pedidos</strong>,
  com autenticação JWT, arquitetura em camadas e testes automatizados.
</p>

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white">
  <img alt="FastAPI" src="https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white">
  <img alt="SQLAlchemy" src="https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?logo=sqlalchemy&logoColor=white">
  <img alt="PostgreSQL" src="https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white">
  <a href="https://github.com/Gustavoalves96/api-rest-gestao/actions/workflows/ci.yml"><img alt="CI" src="https://github.com/Gustavoalves96/api-rest-gestao/actions/workflows/ci.yml/badge.svg"></a>
  <img alt="License" src="https://img.shields.io/badge/license-MIT-blue">
</p>

---

## Sumário

- [Sobre](#sobre)
- [Funcionalidades](#funcionalidades)
- [Stack](#stack)
- [Arquitetura](#arquitetura)
- [Como rodar](#como-rodar)
  - [Com Docker (recomendado)](#com-docker-recomendado)
  - [Localmente com uv](#localmente-com-uv)
- [Endpoints](#endpoints)
- [Testes e qualidade](#testes-e-qualidade)
- [Estrutura do projeto](#estrutura-do-projeto)
- [Decisões de projeto](#decisões-de-projeto)
- [Licença](#licença)

## Sobre

Projeto de portfólio que demonstra o design de uma API REST tratada como se fosse
para produção: camadas bem separadas, autenticação, validação de entrada, regras de
negócio isoladas em uma camada de serviço, migrations versionadas e testes cobrindo
caminho feliz e cenários de erro.

O domínio é um mini-ERP: usuários autenticados cadastram **produtos** (com controle
de estoque) e criam **pedidos**, que dão baixa no estoque de forma atômica.

## Funcionalidades

- 🔐 **Autenticação JWT** — registro e login, com senhas protegidas por hash bcrypt.
- 📦 **Produtos** — CRUD com SKU único, preço e controle de estoque.
- 🧾 **Pedidos** — criação com **baixa de estoque transacional**, preço registrado no
  momento da compra e cancelamento que devolve o estoque.
- 🧱 **Arquitetura em camadas** — `router → service → repository → model`.
- ⚠️ **Erros de domínio** convertidos em respostas HTTP consistentes.
- 🗃️ **Migrations** versionadas com Alembic.
- ✅ **Testes** de integração ponta a ponta com banco isolado.
- 🐳 **Docker Compose** para subir API + PostgreSQL com um comando.
- 🤖 **CI** no GitHub Actions rodando lint e testes.

## Stack

| Camada             | Tecnologia                                             |
| ------------------ | ------------------------------------------------------ |
| Linguagem          | Python 3.12+                                           |
| Framework web      | FastAPI                                                |
| Validação/Schemas  | Pydantic v2                                            |
| ORM                | SQLAlchemy 2.0 (async, `Mapped`/`mapped_column`)       |
| Banco de dados     | PostgreSQL (asyncpg)                                   |
| Migrations         | Alembic                                                |
| Autenticação       | JWT (PyJWT) + bcrypt                                    |
| Testes             | pytest + httpx                                          |
| Lint/Formatação    | ruff                                                   |
| Dependências/Env   | uv                                                     |

## Arquitetura

O fluxo de uma requisição percorre camadas com responsabilidades bem definidas:

```
  HTTP
   │
   ▼
┌─────────┐   valida entrada,     ┌─────────┐   regra de       ┌────────────┐   queries    ┌───────┐
│ router  │──  status, resposta ──│ service │── negócio ───────│ repository │── isoladas ──│ model │
└─────────┘                       └─────────┘                  └────────────┘              └───────┘
                                       │
                                 levanta erros de domínio
                                 (traduzidos em HTTP no main.py)
```

- **router** — só HTTP: validação de entrada, código de status e serialização da resposta.
- **service** — regra de negócio (ex.: validar estoque e dar baixa ao criar um pedido).
- **repository** — acesso a dados; todas as queries ficam isoladas aqui.
- **model** — mapeamento SQLAlchemy das tabelas.

Os schemas de entrada e saída são separados (`Create` / `Update` / `Read`) e o modelo
do ORM nunca é exposto diretamente na resposta.

## Como rodar

### Com Docker (recomendado)

Sobe a API já conectada a um PostgreSQL, aplicando as migrations automaticamente:

```bash
docker compose up --build
```

A API fica disponível em `http://localhost:8000` e a documentação interativa em
`http://localhost:8000/docs`.

### Localmente com uv

Pré-requisitos: [uv](https://docs.astral.sh/uv/) e um PostgreSQL acessível.

```bash
uv sync                                # instala as dependências
cp .env.example .env                   # configure DATABASE_URL e JWT_SECRET
uv run alembic upgrade head            # aplica as migrations
uv run uvicorn app.main:app --reload   # sobe a API em http://localhost:8000
```

> Os comandos mais usados também estão no `Makefile`: `make install`, `make run`,
> `make test`, `make migrate`.

## Endpoints

| Método   | Rota                        | Autenticação | Descrição                              |
| -------- | --------------------------- | :----------: | -------------------------------------- |
| `POST`   | `/auth/register`            |      —       | Cadastra um novo usuário               |
| `POST`   | `/auth/login`               |      —       | Autentica e retorna o token JWT        |
| `GET`    | `/auth/me`                  |      🔒      | Dados do usuário autenticado           |
| `GET`    | `/produtos`                 |      —       | Lista produtos (paginado)              |
| `GET`    | `/produtos/{id}`            |      —       | Detalha um produto                     |
| `POST`   | `/produtos`                 |      🔒      | Cadastra um produto                    |
| `PATCH`  | `/produtos/{id}`            |      🔒      | Atualiza um produto                    |
| `DELETE` | `/produtos/{id}`            |      🔒      | Remove um produto                      |
| `GET`    | `/pedidos`                  |      🔒      | Lista os pedidos do usuário            |
| `GET`    | `/pedidos/{id}`             |      🔒      | Detalha um pedido                      |
| `POST`   | `/pedidos`                  |      🔒      | Cria um pedido (dá baixa no estoque)   |
| `POST`   | `/pedidos/{id}/cancelar`    |      🔒      | Cancela o pedido e devolve o estoque   |
| `GET`    | `/health`                   |      —       | Health check                           |

### Exemplo rápido

```bash
# 1. Registrar e autenticar
curl -X POST localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","nome":"Fulana","senha":"senha-forte-123"}'

TOKEN=$(curl -s -X POST localhost:8000/auth/login \
  -d "username=user@example.com&password=senha-forte-123" | jq -r .access_token)

# 2. Criar um produto
curl -X POST localhost:8000/produtos \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"sku":"SKU-001","nome":"Teclado","preco":"199.90","quantidade_estoque":10}'

# 3. Criar um pedido (baixa o estoque)
curl -X POST localhost:8000/pedidos \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"itens":[{"produto_id":1,"quantidade":3}]}'
```

## Testes e qualidade

```bash
uv run ruff check .    # lint
uv run pytest          # testes
```

Os testes usam um banco **SQLite isolado**, criado e destruído a cada teste — não
tocam no banco de desenvolvimento. A suíte cobre autenticação, CRUD de produtos e o
fluxo de pedidos (baixa de estoque, estoque insuficiente, cancelamento).

## Estrutura do projeto

```
app/
├── main.py            # instancia o FastAPI, registra routers e handlers
├── config.py          # settings via pydantic-settings (lê do .env)
├── database.py        # engine, session e dependência de sessão async
├── dependencies.py    # fábricas de injeção de services/repositories
├── exceptions.py      # exceções de domínio e seus handlers HTTP
├── models/            # modelos SQLAlchemy (uma tabela por arquivo)
├── schemas/           # schemas Pydantic (Create / Update / Read)
├── repositories/      # acesso a dados (queries isoladas)
├── services/          # regra de negócio
├── routers/           # endpoints agrupados por recurso
└── auth/              # JWT, hashing e dependências de segurança
tests/                 # testes de integração + fixtures
alembic/               # configuração e migrations
```

## Decisões de projeto

- **Async de ponta a ponta** — endpoints e acesso a banco usam `async`/`AsyncSession`.
- **Baixa de estoque atômica** — a criação do pedido e o abatimento do estoque ocorrem
  na mesma transação; se o estoque for insuficiente, nada é alterado.
- **Preço histórico** — o item do pedido guarda o preço praticado no momento da compra,
  então reajustes futuros no produto não afetam pedidos passados.
- **Banco de teste em SQLite** — mantém a suíte rápida e sem dependência externa,
  enquanto o alvo de produção é PostgreSQL; os modelos são neutros de dialeto.
- **Segredos por ambiente** — credenciais e chave JWT vêm de variáveis de ambiente;
  o `.env` nunca é versionado.

## Licença

Distribuído sob a licença [MIT](LICENSE).
