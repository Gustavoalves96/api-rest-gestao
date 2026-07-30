"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";

import { ProdutoForm, type ProdutoFormValues } from "@/components/produto-form";
import { ApiError } from "@/lib/api/client";
import { atualizarProduto, obterProduto } from "@/lib/api/produtos";
import { useRequireAuth } from "@/hooks/useRequireAuth";

export default function EditarProdutoPage() {
  const { token, pronto } = useRequireAuth();
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const queryClient = useQueryClient();
  const id = Number(params.id);

  const { data: produto, isLoading } = useQuery({
    queryKey: ["produto", id],
    queryFn: () => obterProduto(id),
    enabled: pronto && Number.isInteger(id),
  });

  const salvar = useMutation({
    mutationFn: (values: ProdutoFormValues) =>
      atualizarProduto(token as string, id, {
        nome: values.nome,
        descricao: values.descricao,
        preco: values.preco,
        quantidadeEstoque: values.quantidadeEstoque,
        ativo: values.ativo,
      }),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["produtos"] });
      await queryClient.invalidateQueries({ queryKey: ["produto", id] });
      router.push("/admin/produtos");
    },
  });

  if (!pronto || isLoading) {
    return <p className="text-zinc-600 dark:text-zinc-400">Carregando…</p>;
  }
  if (produto === undefined) {
    return <p className="text-red-600">Produto não encontrado.</p>;
  }

  return (
    <div>
      <div className="mb-6 flex items-center gap-3">
        <Link href="/admin/produtos" className="text-sm text-emerald-600 hover:underline">
          ← Voltar
        </Link>
        <h1 className="text-xl font-semibold">Editar produto</h1>
      </div>
      <ProdutoForm
        modo="editar"
        inicial={{
          sku: produto.sku,
          nome: produto.nome,
          descricao: produto.descricao,
          precoCentavos: produto.preco,
          quantidadeEstoque: produto.quantidadeEstoque,
          ativo: produto.ativo,
        }}
        enviando={salvar.isPending}
        erro={salvar.error instanceof ApiError ? salvar.error.message : null}
        onSubmit={(values) => salvar.mutate(values)}
      />
    </div>
  );
}
