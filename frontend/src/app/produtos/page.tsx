"use client";

import { useMutation, useQuery } from "@tanstack/react-query";
import { useRouter } from "next/navigation";

import { criarPedido } from "@/lib/api/pedidos";
import { listarProdutos } from "@/lib/api/produtos";
import type { Produto } from "@/lib/api/schemas";
import { useAuth } from "@/lib/auth/context";
import { formatBRL } from "@/lib/money";

export default function ProdutosPage() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ["produtos"],
    queryFn: listarProdutos,
  });

  if (isLoading) {
    return <p className="text-zinc-600 dark:text-zinc-400">Carregando produtos…</p>;
  }
  if (isError || data === undefined) {
    return <p className="text-red-600">Não foi possível carregar os produtos.</p>;
  }
  if (data.length === 0) {
    return <p className="text-zinc-600 dark:text-zinc-400">Nenhum produto cadastrado ainda.</p>;
  }

  return (
    <div>
      <h1 className="mb-6 text-xl font-semibold">Produtos</h1>
      <ul className="grid gap-4 sm:grid-cols-2">
        {data.map((produto) => (
          <ProdutoCard key={produto.id} produto={produto} />
        ))}
      </ul>
    </div>
  );
}

function ProdutoCard({ produto }: { produto: Produto }) {
  const router = useRouter();
  const { token } = useAuth();

  const comprar = useMutation({
    mutationFn: () => criarPedido(token as string, [{ produtoId: produto.id, quantidade: 1 }]),
    onSuccess: (pedido) => router.push(`/checkout/${pedido.id}`),
  });

  const semEstoque = produto.quantidadeEstoque <= 0;

  return (
    <li className="flex flex-col rounded-xl border border-black/10 bg-white p-5 dark:border-white/10 dark:bg-zinc-900">
      <div className="flex-1">
        <p className="text-xs uppercase tracking-wide text-zinc-500">{produto.sku}</p>
        <h2 className="mt-1 font-medium">{produto.nome}</h2>
        {produto.descricao !== null && (
          <p className="mt-1 text-sm text-zinc-600 dark:text-zinc-400">{produto.descricao}</p>
        )}
      </div>
      <div className="mt-4 flex items-center justify-between">
        <span className="text-lg font-semibold">{formatBRL(produto.preco)}</span>
        <span className="text-xs text-zinc-500">{produto.quantidadeEstoque} em estoque</span>
      </div>
      {token === null ? (
        <button
          type="button"
          onClick={() => router.push("/login")}
          className="mt-4 rounded-md border border-black/15 px-4 py-2 text-sm hover:bg-black/5 dark:border-white/20 dark:hover:bg-white/10"
        >
          Entre para comprar
        </button>
      ) : (
        <button
          type="button"
          disabled={semEstoque || comprar.isPending}
          onClick={() => comprar.mutate()}
          className="mt-4 rounded-md bg-emerald-600 px-4 py-2 text-sm text-white hover:bg-emerald-700 disabled:opacity-60"
        >
          {semEstoque ? "Sem estoque" : comprar.isPending ? "Criando pedido…" : "Comprar"}
        </button>
      )}
      {comprar.isError && (
        <p className="mt-2 text-sm text-red-600">Não foi possível criar o pedido.</p>
      )}
    </li>
  );
}
