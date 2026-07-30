"use client";

import { useQuery } from "@tanstack/react-query";
import { useState } from "react";

import { listarProdutos } from "@/lib/api/produtos";
import type { Produto } from "@/lib/api/schemas";
import { useCart } from "@/hooks/useCart";
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
  const { adicionar } = useCart();
  const [adicionado, setAdicionado] = useState(false);

  const semEstoque = produto.quantidadeEstoque <= 0;

  function aoAdicionar() {
    adicionar({
      produtoId: produto.id,
      sku: produto.sku,
      nome: produto.nome,
      preco: produto.preco,
      quantidade: 1,
    });
    setAdicionado(true);
    setTimeout(() => setAdicionado(false), 1500);
  }

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
      <button
        type="button"
        disabled={semEstoque}
        onClick={aoAdicionar}
        className="mt-4 rounded-md bg-emerald-600 px-4 py-2 text-sm text-white hover:bg-emerald-700 disabled:opacity-60"
      >
        {semEstoque ? "Sem estoque" : adicionado ? "Adicionado ✓" : "Adicionar ao carrinho"}
      </button>
    </li>
  );
}
