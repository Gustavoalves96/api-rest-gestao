"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import Link from "next/link";
import { useRouter } from "next/navigation";

import { ProdutoForm, type ProdutoFormValues } from "@/components/produto-form";
import { ApiError } from "@/lib/api/client";
import { criarProduto } from "@/lib/api/produtos";
import { useRequireAuth } from "@/hooks/useRequireAuth";

export default function NovoProdutoPage() {
  const { token, pronto } = useRequireAuth();
  const router = useRouter();
  const queryClient = useQueryClient();

  const criar = useMutation({
    mutationFn: (values: ProdutoFormValues) =>
      criarProduto(token as string, {
        sku: values.sku,
        nome: values.nome,
        descricao: values.descricao,
        preco: values.preco,
        quantidadeEstoque: values.quantidadeEstoque,
      }),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["produtos"] });
      router.push("/admin/produtos");
    },
  });

  if (!pronto) {
    return <p className="text-zinc-600 dark:text-zinc-400">Carregando…</p>;
  }

  return (
    <div>
      <div className="mb-6 flex items-center gap-3">
        <Link href="/admin/produtos" className="text-sm text-emerald-600 hover:underline">
          ← Voltar
        </Link>
        <h1 className="text-xl font-semibold">Novo produto</h1>
      </div>
      <ProdutoForm
        modo="criar"
        enviando={criar.isPending}
        erro={criar.error instanceof ApiError ? criar.error.message : null}
        onSubmit={(values) => criar.mutate(values)}
      />
    </div>
  );
}
