"use client";

import { useMutation } from "@tanstack/react-query";
import Link from "next/link";
import { useRouter } from "next/navigation";

import { ApiError } from "@/lib/api/client";
import { criarPedido } from "@/lib/api/pedidos";
import { useCart } from "@/hooks/useCart";
import { useAuth } from "@/lib/auth/context";
import { formatBRL } from "@/lib/money";

export default function CarrinhoPage() {
  const router = useRouter();
  const { token } = useAuth();
  const { itens, total, definirQuantidade, remover, limpar } = useCart();

  const finalizar = useMutation({
    mutationFn: () =>
      criarPedido(
        token as string,
        itens.map((i) => ({ produtoId: i.produtoId, quantidade: i.quantidade })),
      ),
    onSuccess: (pedido) => {
      limpar();
      router.push(`/checkout/${pedido.id}`);
    },
  });

  if (itens.length === 0) {
    return (
      <div>
        <h1 className="mb-4 text-xl font-semibold">Carrinho</h1>
        <p className="text-zinc-600 dark:text-zinc-400">
          Seu carrinho está vazio.{" "}
          <Link href="/produtos" className="text-emerald-600 hover:underline">
            Ver produtos
          </Link>
          .
        </p>
      </div>
    );
  }

  return (
    <div>
      <h1 className="mb-6 text-xl font-semibold">Carrinho</h1>
      <ul className="flex flex-col gap-3">
        {itens.map((item) => (
          <li
            key={item.produtoId}
            className="flex items-center gap-4 rounded-lg border border-black/10 bg-white p-4 dark:border-white/10 dark:bg-zinc-900"
          >
            <div className="flex-1">
              <p className="font-medium">{item.nome}</p>
              <p className="text-xs text-zinc-500">
                {item.sku} · {formatBRL(item.preco)} un.
              </p>
            </div>
            <div className="flex items-center gap-2">
              <button
                type="button"
                aria-label="Diminuir"
                onClick={() => definirQuantidade(item.produtoId, item.quantidade - 1)}
                className="h-8 w-8 rounded-md border border-black/15 hover:bg-black/5 dark:border-white/20 dark:hover:bg-white/10"
              >
                −
              </button>
              <input
                type="number"
                min={1}
                value={item.quantidade}
                onChange={(e) => definirQuantidade(item.produtoId, Number(e.target.value))}
                className="w-14 rounded-md border border-black/15 bg-white px-2 py-1 text-center dark:border-white/20 dark:bg-zinc-900"
              />
              <button
                type="button"
                aria-label="Aumentar"
                onClick={() => definirQuantidade(item.produtoId, item.quantidade + 1)}
                className="h-8 w-8 rounded-md border border-black/15 hover:bg-black/5 dark:border-white/20 dark:hover:bg-white/10"
              >
                +
              </button>
            </div>
            <div className="w-24 text-right font-medium">
              {formatBRL(item.preco * item.quantidade)}
            </div>
            <button
              type="button"
              onClick={() => remover(item.produtoId)}
              className="text-sm text-red-600 hover:underline"
            >
              Remover
            </button>
          </li>
        ))}
      </ul>

      <div className="mt-6 flex items-center justify-between border-t border-black/10 pt-4 dark:border-white/10">
        <span className="text-lg font-semibold">Total: {formatBRL(total)}</span>
        {token === null ? (
          <button
            type="button"
            onClick={() => router.push("/login")}
            className="rounded-md border border-black/15 px-4 py-2 hover:bg-black/5 dark:border-white/20 dark:hover:bg-white/10"
          >
            Entre para finalizar
          </button>
        ) : (
          <button
            type="button"
            disabled={finalizar.isPending}
            onClick={() => finalizar.mutate()}
            className="rounded-md bg-emerald-600 px-5 py-2 text-white hover:bg-emerald-700 disabled:opacity-60"
          >
            {finalizar.isPending ? "Criando pedido…" : "Finalizar pedido"}
          </button>
        )}
      </div>
      {finalizar.isError && (
        <p className="mt-3 text-right text-sm text-red-600">
          {finalizar.error instanceof ApiError
            ? finalizar.error.message
            : "Não foi possível finalizar o pedido."}
        </p>
      )}
    </div>
  );
}
