# CLAUDE.md

Este arquivo orienta o Claude Code ao trabalhar neste repositório. Leia por completo antes de gerar ou alterar código.

## Visão geral do projeto

Plataforma de **gestão de estoque e pedidos com pagamentos** (domínio ERP / marketplace). Projeto de portfólio que demonstra design de API limpo, camadas bem separadas, autenticação, integração com gateway de pagamento e testes.

Composto por duas partes:

- **Backend** (raiz do repo) — API REST em FastAPI. Contém 100% da regra de negócio.
- **Frontend** (`frontend/`) — aplicação Next.js que consome a API.

Não é um projeto de brinquedo: trate-o como se fosse ir para produção. Prefira clareza e correção a atalhos.

### Fluxo central do domínio

```
pedido criado (PENDENTE)
      │
      ▼
cobrança gerada no gateway (Pix)  ──►  front exibe QR Code + copia-e-cola
      │
      ▼
webhook do gateway  ──►  assinatura validada  ──►  evento registrado
      │
      ▼
pagamento CONFIRMADO + baixa de estoque, na MESMA transação
```

O estoque só é abatido quando o pagamento é confirmado. Cancelamento ou expiração devolve o estoque.

---

## Stack

### Backend

- **Python 3.12+**
- **FastAPI** — framework web
- **Pydantic v2** — validação e schemas
- **SQLAlchemy 2.0** (sintaxe nova, com `Mapped` / `mapped_column`) — ORM
- **Alembic** — migrations
- **PostgreSQL** — banco de dados (dev via Docker; prod na Neon)
- **httpx** — cliente HTTP assíncrono para chamar o gateway
- **pytest** + **respx** — testes (respx para mockar o gateway)
- **ruff** — lint + formatação
- **uv** — gerenciamento de dependências e ambiente

### Frontend

- **TypeScript** em modo `strict` — não negociável
- **Next.js** (App Router)
- **Tailwind CSS**
- **Zod** — validação dos dados vindos da API na borda
- **TanStack Query** — cache e revalidação de estado do servidor
- **Vitest** + **Testing Library** — testes

### Gateway de pagamento

- **Asaas** em ambiente **sandbox** como implementação de referência.
- A aplicação nunca conhece o Asaas diretamente — apenas a interface `PaymentGateway`.

---

## Comandos

### Backend (na raiz)

```bash
uv sync                                    # instala dependências
uv run uvicorn app.main:app --reload       # sobe a API em :8000
uv run pytest                              # roda todos os testes
uv run pytest tests/test_x.py -v           # roda um arquivo específico
uv run ruff check .                        # lint
uv run ruff format .                       # formata
uv run alembic revision --autogenerate -m "descrição"
uv run alembic upgrade head
```

### Frontend (em `frontend/`)

```bash
npm install
npm dev                                   # sobe o front em :3000
npm build                                 # build de produção
npm lint
npm typecheck                             # tsc --noEmit
npm test
```

Antes de considerar uma tarefa concluída: no backend, `uv run ruff check .` e `uv run pytest`; no frontend, `npm typecheck` e `npm lint`. Todos precisam passar.

---

## Estrutura de pastas

```
app/
  main.py                  # instancia o FastAPI, registra routers e handlers
  config.py                # settings via pydantic-settings (lê do .env)
  database.py              # engine, session, base declarativa
  dependencies.py          # fábricas de injeção de services/repositories
  exceptions.py            # exceções de domínio e handlers HTTP
  models/                  # modelos SQLAlchemy (uma tabela por arquivo)
  schemas/                 # schemas Pydantic (Create / Update / Read)
  routers/                 # endpoints agrupados por recurso
    webhooks.py            # rotas chamadas PELO gateway (não pelo cliente)
  services/                # regra de negócio
    payment_service.py     # orquestra cobrança, confirmação, estorno
    gateways/
      base.py              # Protocol PaymentGateway (a abstração)
      asaas.py             # implementação concreta
      fake.py              # implementação em memória, usada nos testes
  repositories/            # acesso a dados (queries isoladas aqui)
  auth/                    # JWT, hashing, dependências de segurança
tests/
  conftest.py              # fixtures (client de teste, DB de teste, gateway fake)
alembic/
frontend/
  src/
    app/                   # rotas do App Router
    components/
    lib/
      api/                 # cliente da API + schemas Zod
    hooks/
```

---

## Arquitetura e convenções — backend

**Camadas.** O fluxo é `router → service → repository → model`. O router só cuida de HTTP (validação de entrada, status, resposta). A regra de negócio fica no service. O acesso ao banco fica no repository. Não misture essas responsabilidades.

**Schemas.** Para cada recurso, separe entrada e saída: `ProdutoCreate`, `ProdutoUpdate`, `ProdutoRead`. Nunca exponha o modelo do ORM diretamente na resposta.

**Injeção de dependências.** Use `Depends` para sessão de banco, usuário autenticado, services e o gateway de pagamento. Não instancie sessão nem cliente HTTP manualmente dentro dos endpoints.

**Erros.** Levante exceções de domínio (ex.: `EstoqueInsuficienteError`, `TransicaoDeStatusInvalidaError`) nos services e converta para HTTP com handlers em `main.py`. Não deixe `HTTPException` vazar para dentro dos services.

**Async.** Endpoints, acesso a banco e chamadas ao gateway são assíncronos. Não misture chamadas síncronas bloqueantes em rotas async.

**Tipagem.** Todo o código é tipado, em parâmetros e retorno.

---

## Pagamentos — regras obrigatórias

Esta seção tem precedência sobre conveniência. Qualquer atalho aqui é bug de produção.

### Abstração do gateway

Defina em `services/gateways/base.py` um `Protocol`:

```python
class PaymentGateway(Protocol):
    async def create_charge(self, req: ChargeRequest) -> ChargeResult: ...
    async def get_charge(self, external_id: str) -> ChargeResult: ...
    async def refund(self, external_id: str) -> RefundResult: ...
    def parse_webhook(self, raw_body: bytes, headers: Mapping[str, str]) -> WebhookEvent: ...
```

Regras:

- Nenhum módulo fora de `services/gateways/` importa `asaas.py` ou menciona "asaas".
- `ChargeRequest` / `ChargeResult` / `WebhookEvent` são tipos **nossos**, não o JSON do gateway. A tradução acontece dentro da implementação concreta.
- A implementação é resolvida por `Depends`, escolhida pela config. Testes injetam `fake.py`.

### Dinheiro

- Valores monetários em **centavos**, como `int`, em toda a stack (banco, API, front).
- Se precisar de decimal no banco, use `Numeric(10, 2)` com `Decimal` no Python. **Nunca** `float`.
- No frontend, o valor trafega como inteiro em centavos e é formatado só na renderização, com `Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' })`.
- Toda operação de arredondamento precisa ser explícita e comentada com o "porquê".

### Máquina de estados

Status de pagamento: `PENDENTE`, `CONFIRMADO`, `FALHOU`, `EXPIRADO`, `ESTORNADO`.

- Transições válidas ficam declaradas em um mapa explícito no service. Transição inválida levanta `TransicaoDeStatusInvalidaError`.
- `CONFIRMADO → PENDENTE` nunca acontece. `ESTORNADO` é terminal.
- Nunca faça `UPDATE` direto de status fora do service.

### Webhooks

A rota de webhook é a superfície mais crítica do sistema. Ela precisa:

1. **Validar a assinatura** antes de qualquer parsing de negócio. Sem assinatura válida, responda `401` e não processe nada. Qualquer pessoa na internet conhece essa URL.
2. **Ser idempotente.** Grave `external_event_id` com constraint `UNIQUE` na tabela de eventos. Evento repetido é normal e deve resultar em no-op, não em erro nem em duplo processamento.
3. **Registrar o payload cru** na tabela `eventos_pagamento` (coluna `JSONB`) *antes* de processar. É o único jeito de depurar produção.
4. **Responder `200` rápido.** O gateway tem timeout curto e reenvia. Se o processamento for pesado, persista o evento, responda, e processe em background.
5. **Nunca confiar no corpo do webhook para valores.** Use o evento como gatilho e consulte o gateway (`get_charge`) para confirmar valor e status reais.

### Concorrência

Dois webhooks do mesmo pedido podem chegar simultaneamente. Isso é a causa raiz de estoque negativo.

- Ao confirmar pagamento, faça `SELECT ... FOR UPDATE` no pedido antes de ler o status.
- Confirmação de pagamento e baixa de estoque acontecem na **mesma transação**. Se qualquer parte falhar, nada é alterado.
- A constraint `UNIQUE` em `external_event_id` é a segunda linha de defesa. Não confie apenas na lógica da aplicação.

### Segurança

- Chaves de API do gateway **apenas** em variáveis de ambiente, via `config.py`. Nunca no repositório, nunca em log, nunca em mensagem de erro.
- Dados de cartão **nunca** passam pelo nosso backend nem pelo nosso front. Se cartão entrar no escopo, use tokenização no cliente ou checkout hospedado. Não existe exceção.
- Ao logar requisições ao gateway, mascare a chave e qualquer dado pessoal.

---

## Arquitetura e convenções — frontend

**TypeScript strict.** Sem `any`, sem `as` para silenciar erro. Se o tipo está incômodo, o modelo está errado.

**Estado de pagamento como union discriminada:**

```ts
type PagamentoState =
  | { status: 'pendente'; qrCode: string; copiaECola: string; expiraEm: string }
  | { status: 'confirmado'; confirmadoEm: string }
  | { status: 'expirado' }
  | { status: 'falhou'; motivo: string };
```

Isso torna impossível renderizar tela de sucesso sem `confirmadoEm`. Não substitua por booleanos soltos.

**Validação na borda.** Toda resposta da API passa por um schema Zod em `lib/api/`. O resto do app consome tipos inferidos, nunca o JSON cru.

**Espera pelo pagamento.** Não faça polling de intervalo fixo. Use backoff crescente (2s → 4s → 8s, teto de 30s) ou SSE via `StreamingResponse` no FastAPI. Sempre trate o caso de expiração.

**Pix.** Exiba QR Code **e** o código copia-e-cola com botão de copiar. A maioria dos usuários está no celular e não tem uma segunda tela.

**Sem lógica de negócio no front.** O front não decide se um pagamento é válido, não calcula split, não confirma nada. Ele exibe o que a API diz.

---

## Banco de dados

- Toda alteração de modelo exige **migration via Alembic**. Nunca altere o schema na mão.
- Não use `Base.metadata.create_all()` fora de testes.
- Tabelas no plural e em snake_case (`produtos`, `pedidos`, `itens_pedido`, `pagamentos`, `eventos_pagamento`).
- PK como `id` inteiro autoincremental, salvo motivo claro para UUID.
- Sempre defina `created_at` / `updated_at` nas tabelas principais.
- Toda referência a ID externo do gateway é indexada e, quando representa um evento, `UNIQUE`.

---

## Testes

- Todo endpoint novo precisa de teste (caminho feliz + pelo menos um erro esperado).
- Services com regra de negócio relevante precisam de teste unitário.
- Use banco de teste isolado (fixture em `conftest.py`), nunca o de dev.
- **Nunca chame o gateway real em teste.** Injete `gateways/fake.py`; para testar a implementação concreta, mocke o HTTP com `respx`.
- Cenários de pagamento que precisam de cobertura explícita:
  - webhook com assinatura inválida → `401`, nada é alterado
  - webhook duplicado → processado uma única vez
  - confirmação com estoque insuficiente → transação revertida por completo
  - transição de status inválida → erro de domínio
  - expiração de cobrança → estoque devolvido
- Prefira testar comportamento (o que a API responde) a testar implementação interna.

---

## Estilo de código

- Backend segue o ruff (config no `pyproject.toml`); frontend segue o ESLint + Prettier. Não brigue com o formatador.
- Nomes de domínio em **português** (`pedido`, `estoque`, `pagamento`); termos técnicos e de biblioteca em inglês. Mantenha consistente.
- Funções curtas e com responsabilidade única. Service acima de ~40 linhas provavelmente dá pra quebrar.
- Evite comentários óbvios. Comente o "porquê", não o "o quê" — especialmente em pagamentos, onde a razão de uma trava não é evidente.

---

## Git

- Commits pequenos e descritivos, no imperativo (ex.: "valida assinatura do webhook do gateway").
- Não faça commit de código que não passa no lint ou nos testes.
- Confira o `.gitignore` antes de qualquer commit que toque em configuração. `.env` nunca é versionado.

---

## O que evitar

- Não instale dependências novas sem necessidade real — justifique antes.
- Não crie abstrações "para o futuro" que ainda não são usadas.
- Não coloque lógica de negócio em routers nem no frontend.
- Não exponha modelos do ORM nas respostas.
- Não implemente split de pagamento antes do fluxo Pix simples estar funcionando e testado ponta a ponta. Split exige cadastro de recebedores e trava o progresso.
- Não use `float` para dinheiro em nenhuma hipótese.
- Não marque um pedido como pago com base apenas na resposta de criação da cobrança.

---

## Instruções para o assistente

- Ao começar uma tarefa, se algo estiver ambíguo, pergunte antes de assumir.
- Ao terminar, rode lint e testes das partes afetadas e relate o resultado.
- Se alterar o schema do banco, gere a migration correspondente.
- Ao criar um recurso novo no backend, siga o padrão completo: model, schemas, repository, service, router e testes.
- Ao tocar em qualquer coisa de pagamento, releia a seção "Pagamentos — regras obrigatórias" antes de escrever código.
- Se uma implementação exigir contornar alguma regra desta seção, **pare e explique o conflito** em vez de contornar.
