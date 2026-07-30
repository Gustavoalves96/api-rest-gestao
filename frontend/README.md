# Frontend — Gestão (loja com checkout Pix)

Aplicação **Next.js (App Router)** em TypeScript `strict` que consome a API de gestão:
catálogo de produtos, criação de pedidos e **pagamento Pix** com QR Code, copia-e-cola
e acompanhamento do status em tempo real.

## Stack

Next.js · React 19 · TypeScript (strict) · Tailwind CSS v4 · TanStack Query ·
Zod (validação na borda) · Vitest + Testing Library.

## Como rodar

```bash
npm install
cp .env.local.example .env.local     # aponta para a API (padrão: http://localhost:8000)
npm run dev                          # http://localhost:3000
```

A API (backend na raiz do repositório) precisa estar rodando em paralelo.

## Scripts

```bash
npm run dev         # servidor de desenvolvimento
npm run build       # build de produção
npm run lint        # ESLint
npm run typecheck   # tsc --noEmit
npm run test        # Vitest
```

## Organização

```
src/
├── app/                # rotas do App Router (login, register, produtos, pedidos, checkout)
├── components/         # UI (header, providers, checkout Pix, botão copiar)
├── hooks/              # usePagamento (polling com backoff)
└── lib/
    ├── api/            # client HTTP + schemas Zod + funções por recurso
    ├── auth/           # store do JWT (useSyncExternalStore) + contexto
    ├── money.ts        # formatação de centavos em BRL
    └── pagamento-state.ts  # union discriminada do estado de pagamento
```

## Decisões

- **Validação na borda** — toda resposta da API passa por um schema Zod; o app consome
  apenas os tipos inferidos (camelCase), nunca o JSON cru.
- **Dinheiro em centavos** — valores trafegam como inteiros; a formatação em BRL acontece
  só na renderização (`Intl.NumberFormat`).
- **Estado de pagamento** como union discriminada — impossível renderizar sucesso sem
  `confirmadoEm`, expiração sem tratar, etc.
- **Espera pelo pagamento** com backoff crescente (2s → 4s → 8s … teto de 30s), parando
  em estados terminais — sem polling de intervalo fixo.
- **Sem lógica de negócio** no front: ele apenas exibe o que a API decide.
