"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import Link from "next/link";

import { listarProdutos, removerProduto } from "@/lib/api/produtos";
import type { Produto } from "@/lib/api/schemas";
import { useRequireAuth } from "@/hooks/useRequireAuth";
import { formatBRL } from "@/lib/money";

export default function AdminProdutosPage() {
  const { token, pronto } = useRequireAuth();
  const queryClient = useQueryClient();

  const { data, isLoading, isError } = useQuery({
    queryKey: ["produtos"],
    queryFn: listarProdutos,
    enabled: pronto,
  });

  const remover = useMutation({
    mutationFn: (id: number) => removerProduto(token as string, id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["produtos"] }),
  });

  if (!pronto || isLoading) {
    return <p className="text-zinc-600 dark:text-zinc-400">Carregando…</p>;
  }
  if (isError || data === undefined) {
    return <p className="text-red-600">Não foi possível carregar os produtos.</p>;
  }

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-xl font-semibold">Administração de produtos</h1>
        <Link
          href="/admin/produtos/novo"
          className="rounded-md bg-emerald-600 px-4 py-2 text-sm text-white hover:bg-emerald-700"
        >
          Novo produto
        </Link>
      </div>

      {data.length === 0 ? (
        <p className="text-zinc-600 dark:text-zinc-400">Nenhum produto cadastrado.</p>
      ) : (
        <div className="overflow-x-auto rounded-lg border border-black/10 dark:border-white/10">
          <table className="w-full text-left text-sm">
            <thead className="bg-black/5 dark:bg-white/10">
              <tr>
                <th className="px-4 py-2">SKU</th>
                <th className="px-4 py-2">Nome</th>
                <th className="px-4 py-2">Preço</th>
                <th className="px-4 py-2">Estoque</th>
                <th className="px-4 py-2">Ativo</th>
                <th className="px-4 py-2 text-right">Ações</th>
              </tr>
            </thead>
            <tbody>
              {data.map((produto) => (
                <LinhaProduto
                  key={produto.id}
                  produto={produto}
                  removendo={remover.isPending && remover.variables === produto.id}
                  onRemover={() => {
                    if (window.confirm(`Excluir "${produto.nome}"?`)) {
                      remover.mutate(produto.id);
                    }
                  }}
                />
              ))}
            </tbody>
          </table>
        </div>
      )}

      {remover.isError && (
        <p className="mt-3 text-sm text-red-600">Não foi possível excluir o produto.</p>
      )}
    </div>
  );
}

function LinhaProduto({
  produto,
  removendo,
  onRemover,
}: {
  produto: Produto;
  removendo: boolean;
  onRemover: () => void;
}) {
  return (
    <tr className="border-t border-black/10 dark:border-white/10">
      <td className="px-4 py-2 font-mono text-xs">{produto.sku}</td>
      <td className="px-4 py-2">{produto.nome}</td>
      <td className="px-4 py-2">{formatBRL(produto.preco)}</td>
      <td className="px-4 py-2">{produto.quantidadeEstoque}</td>
      <td className="px-4 py-2">{produto.ativo ? "Sim" : "Não"}</td>
      <td className="px-4 py-2">
        <div className="flex justify-end gap-3">
          <Link
            href={`/admin/produtos/${produto.id}/editar`}
            className="text-emerald-600 hover:underline"
          >
            Editar
          </Link>
          <button
            type="button"
            onClick={onRemover}
            disabled={removendo}
            className="text-red-600 hover:underline disabled:opacity-60"
          >
            {removendo ? "Excluindo…" : "Excluir"}
          </button>
        </div>
      </td>
    </tr>
  );
}
