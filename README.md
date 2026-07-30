<h1 align="center">API REST — Gestão de Estoque, Pedidos e Pagamentos</h1>

<p align="center">
  API REST (domínio ERP / marketplace) para gestão de <strong>estoque</strong>,
  <strong>pedidos</strong> e <strong>pagamentos Pix</strong>, com autenticação JWT,
  integração com gateway abstraído, webhooks idempotentes e testes automatizados.
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

O domínio: usuários autenticados cadastram **produtos** (com controle de estoque),
criam **pedidos** e pagam via **Pix**. O estoque só é abatido quando o pagamento é
**confirmado pelo gateway** (via webhook), na mesma transação — nunca na criação do
pedido.

### Fluxo do pagamento

```
pedido criado (PENDENTE)
      │
      ▼
cobrança Pix gerada no gateway  ──►  QR Code + copia-e-cola
      │
      ▼
webhook do gateway  ──►  assinatura validada  ──►  evento registrado (idempotente)
      │
      ▼
pagamento CONFIRMADO + baixa de estoque, na MESMA transação
```

## Funcionalidades

- 🔐 **Autenticação JWT** — registro e login, com senhas protegidas por hash bcrypt.
- 📦 **Produtos** — CRUD com SKU único, preço (em centavos) e controle de estoque.
- 🧾 **Pedidos** — preço congelado no momento da compra; criação **não** mexe no estoque.
- 💸 **Pagamentos Pix** — cobrança com QR Code e copia-e-cola, gateway **abstraído**
  por trás de um `Protocol` (implementação `fake` em memória; Asaas fica plugável).
- 🔁 **Máquina de estados** de pagamento (`PENDENTE → CONFIRMADO/FALHOU/EXPIRADO`,
  `CONFIRMADO → ESTORNADO`) com transições validadas explicitamente.
- 📥 **Webhooks** com validação de assinatura, idempotência (`external_event_id` único),
  registro do payload cru e baixa de estoque **atômica** na confirmação.
- 💰 **Dinheiro em centavos** (`int`) em toda a stack — nunca `float`.
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
| Gateway de pagamento | Abstraído por `Protocol` (impl. `fake`; Asaas plugável) |
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
- **service** — regra de negócio (ex.: confirmar pagamento e dar baixa no estoque).
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
| `POST`   | `/pedidos`                  |      🔒      | Cria um pedido (não mexe no estoque)   |
| `POST`   | `/pedidos/{id}/pagamento`   |      🔒      | Gera a cobrança Pix (QR + copia-e-cola) |
| `GET`    | `/pedidos/{id}/pagamento`   |      🔒      | Consulta o status da cobrança          |
| `POST`   | `/pedidos/{id}/cancelar`    |      🔒      | Cancela/estorna e devolve o estoque    |
| `POST`   | `/webhooks/pagamentos`      |   assinatura | Recebido **pelo gateway** (não pelo cliente) |
| `GET`    | `/health`                   |      —       | Health check                           |

> Valores monetários trafegam sempre como inteiros em **centavos** (ex.: `19990` = R$ 199,90).

### Exemplo rápido

```bash
# 1. Registrar e autenticar
curl -X POST localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","nome":"Fulana","senha":"senha-forte-123"}'

TOKEN=$(curl -s -X POST localhost:8000/auth/login \
  -d "username=user@example.com&password=senha-forte-123" | jq -r .access_token)

# 2. Criar um produto (preço em centavos)
curl -X POST localhost:8000/produtos \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"sku":"SKU-001","nome":"Teclado","preco":19990,"quantidade_estoque":10}'

# 3. Criar um pedido (ainda não baixa o estoque)
curl -X POST localhost:8000/pedidos \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"itens":[{"produto_id":1,"quantidade":3}]}'

# 4. Gerar a cobrança Pix — retorna QR Code e copia-e-cola
curl -X POST localhost:8000/pedidos/1/pagamento -H "Authorization: Bearer $TOKEN"

# O estoque só é baixado quando o gateway confirma o pagamento via webhook.
```

## Testes e qualidade

```bash
uv run ruff check .    # lint
uv run pytest          # testes
```

Os testes usam um banco **SQLite isolado** e um **gateway fake em memória**, criados
a cada teste — nunca tocam no banco de desenvolvimento nem em um gateway real. A suíte
cobre autenticação, produtos, pedidos e pagamentos: webhook com assinatura inválida
(`401`), webhook duplicado (processado uma única vez), confirmação com estoque
insuficiente (transação revertida) e estorno que devolve o estoque.

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
│   ├── payment_service.py   # cobrança, confirmação, estorno, estados
│   ├── webhook_service.py   # assinatura, idempotência, registro do evento
│   └── gateways/            # abstração do gateway (base Protocol + fake)
├── routers/           # endpoints agrupados por recurso
│   └── webhooks.py    # rotas chamadas PELO gateway
└── auth/              # JWT, hashing e dependências de segurança
tests/                 # testes de integração + fixtures (gateway fake)
alembic/               # configuração e migrations
```

## Decisões de projeto

- **Async de ponta a ponta** — endpoints, acesso a banco e chamadas ao gateway são `async`.
- **Baixa de estoque na confirmação** — o estoque só é abatido quando o pagamento é
  confirmado pelo gateway, na mesma transação (com `SELECT ... FOR UPDATE` no pedido
  para evitar baixa dupla por webhooks concorrentes). Criar o pedido não reserva estoque.
- **Dinheiro em centavos** — todos os valores monetários são `int` em centavos, em toda
  a stack; nunca `float`.
- **Gateway abstraído** — a aplicação depende apenas do `Protocol PaymentGateway`. A
  implementação concreta (ex.: Asaas) é resolvida por config e injetada por `Depends`;
  os testes injetam um fake em memória.
- **Webhooks defensivos** — assinatura validada antes de qualquer processamento, evento
  cru registrado antes de processar, idempotência por `external_event_id` único e o
  status/valor reais reconsultados no gateway (nunca confia no corpo do webhook).
- **Preço histórico** — o item do pedido guarda o preço praticado no momento da compra.
- **Banco de teste em SQLite** — suíte rápida e sem dependência externa; alvo de produção
  é PostgreSQL, e os modelos são neutros de dialeto (`JSONB` no Postgres, `JSON` no SQLite).
- **Segredos por ambiente** — chaves de API, segredo do webhook e JWT vêm do ambiente;
  o `.env` nunca é versionado.

## Frontend

O repositório inclui um frontend **Next.js** (App Router, TypeScript `strict`) em
[`frontend/`](frontend/) que consome esta API: catálogo de produtos, criação de pedidos
e **checkout Pix** com QR Code, copia-e-cola e acompanhamento do status em tempo real
(polling com backoff). Detalhes e comandos no [README do frontend](frontend/README.md).

```bash
cd frontend
npm install
cp .env.local.example .env.local     # aponta para a API
npm run dev                          # http://localhost:3000
```

## Licença

Distribuído sob a licença [MIT](LICENSE).
