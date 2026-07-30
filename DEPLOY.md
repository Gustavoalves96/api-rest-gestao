# Guia de deploy — Vercel + Render + Neon

Arquitetura de produção:

| Camada | Serviço |
| --- | --- |
| Frontend (Next.js) | **Vercel** |
| Backend (FastAPI) | **Render** (Docker) |
| Banco (PostgreSQL) | **Neon** |

> Enquanto não houver gateway de pagamento real, o backend roda com
> `PAYMENT_GATEWAY=fake` e você confirma pagamentos pelo botão "Simular
> pagamento" (dev) no checkout. Nenhum dinheiro real trafega.

A ordem importa: **Neon → Render → Vercel** (o front precisa da URL da API, e o
CORS da API precisa da URL do front).

---

## 0) Antes de começar

- O repositório já está no GitHub.
- Crie contas gratuitas em [Neon](https://neon.tech), [Render](https://render.com)
  e [Vercel](https://vercel.com).
- Gere dois segredos fortes (guarde-os):

  ```bash
  python -c "import secrets; print(secrets.token_urlsafe(48))"   # JWT_SECRET
  python -c "import secrets; print(secrets.token_urlsafe(48))"   # WEBHOOK_SECRET
  ```

---

## 1) Banco de dados — Neon

1. Crie um projeto no Neon (escolha a região mais próxima).
2. Copie a **connection string** (use a do endpoint *pooled*).
   Ela vem parecida com:
   ```
   postgresql://USER:PASSWORD@ep-xxx-pooler.REGIÃO.aws.neon.tech/DBNAME?sslmode=require
   ```
3. Converta para o formato **async** que a API usa (driver `asyncpg` + SSL):
   ```
   postgresql+asyncpg://USER:PASSWORD@ep-xxx-pooler.REGIÃO.aws.neon.tech/DBNAME?ssl=require
   ```
   Mudanças: prefixo `postgresql+asyncpg://` e troque `sslmode=require` por
   `ssl=require`. Remova parâmetros extras como `channel_binding` (o asyncpg não
   os aceita). Guarde essa URL — é o `DATABASE_URL`.

---

## 2) Backend — Render

Há um `render.yaml` na raiz (Blueprint), então o jeito mais simples é:

1. No Render: **New → Blueprint** e selecione este repositório. Ele lê o
   `render.yaml` e cria o web service `api-gestao` (Docker).
2. Preencha as variáveis marcadas como "sync: false":
   | Variável | Valor |
   | --- | --- |
   | `DATABASE_URL` | a URL async da Neon (passo 1) |
   | `JWT_SECRET` | o segredo gerado no passo 0 |
   | `WEBHOOK_SECRET` | o outro segredo gerado no passo 0 |
   | `CORS_ORIGINS` | deixe `http://localhost:3000` por enquanto; ajustamos no passo 4 |

   (`PAYMENT_GATEWAY=fake` já vem do Blueprint.)
3. Clique em **Apply/Deploy** e aguarde o build da imagem Docker.
4. As **migrations rodam automaticamente** no start do container (o `CMD` do
   Dockerfile executa `alembic upgrade head` antes de subir a API). Não é
   preciso Shell — ideal para o free tier.
5. Confirme a saúde: abra `https://SEU-SERVICO.onrender.com/health` → deve
   responder `{"status":"ok"}`. A doc fica em `/docs`.

Anote a URL pública da API (ex.: `https://api-gestao.onrender.com`).

> **Alternativa sem Blueprint:** New → **Web Service** → conecte o repo →
> Runtime **Docker** → defina as mesmas variáveis → Deploy.

> **Free tier:** o serviço "dorme" após inatividade; a primeira requisição
> depois disso demora alguns segundos (cold start). Normal para uso interno.

---

## 3) Frontend — Vercel

1. No Vercel: **Add New → Project** e importe o repositório.
2. Em **Root Directory**, selecione `frontend`. O framework (Next.js) é
   detectado automaticamente.
3. Em **Environment Variables**, adicione:
   | Variável | Valor |
   | --- | --- |
   | `NEXT_PUBLIC_API_URL` | a URL da API na Render (passo 2) |

   Importante: essa variável é embutida no build; se mudar depois, refaça o deploy.
4. **Deploy**. Ao final, anote o domínio (ex.: `https://gestao.vercel.app`).

---

## 4) Ligar os dois — CORS

1. Volte ao serviço na Render → **Environment** → edite `CORS_ORIGINS` para o
   domínio da Vercel (sem barra no final):
   ```
   https://gestao.vercel.app
   ```
   Para liberar mais de uma origem, separe por vírgula:
   ```
   https://gestao.vercel.app,http://localhost:3000
   ```
2. Salve — a Render faz redeploy automático.

> Deploys de *preview* da Vercel têm URLs próprias; se precisar testá-los,
> adicione a URL do preview ao `CORS_ORIGINS` também.

---

## 5) Testar de ponta a ponta

1. Abra o domínio da Vercel.
2. **Cadastre-se** e entre.
3. Em **Admin**, crie um produto (preço em reais; vira centavos na API).
4. **Adicione ao carrinho**, ajuste a quantidade e **finalize o pedido**.
5. No checkout, veja o QR Code e o copia-e-cola; clique em **"Simular
   pagamento confirmado"** (botão de dev) → o pedido vira **pago** e o estoque
   baixa.

Se algo falhar, verifique nesta ordem: `/health` da API, o `NEXT_PUBLIC_API_URL`
no front, e o `CORS_ORIGINS` na API (o navegador acusa erro de CORS no console).

---

## Quando for cobrar de verdade

1. Contrate/cadastre um gateway (ex.: Asaas) e obtenha a chave de API.
2. Na Render, mude as variáveis:
   ```
   PAYMENT_GATEWAY=http
   GATEWAY_BASE_URL=<url do gateway>
   GATEWAY_API_KEY=<sua chave>
   WEBHOOK_SECRET=<token de assinatura do webhook>
   ```
3. Configure a URL do webhook no painel do gateway apontando para
   `https://SUA-API.onrender.com/webhooks/pagamentos`.
4. Se o formato de payload do provedor diferir da convenção genérica, ajuste
   apenas a tradução em `app/services/gateways/http.py`. Nada mais muda.

Ao sair do `fake`, o endpoint de simulação (`/dev/...`) deixa de existir
automaticamente.
