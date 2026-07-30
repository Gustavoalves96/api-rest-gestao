import { apiFetch, apiFetchVoid } from "@/lib/api/client";
import { type Produto, produtoSchema, produtosSchema } from "@/lib/api/schemas";

export type ProdutoCreateInput = {
  sku: string;
  nome: string;
  descricao: string | null;
  preco: number; // centavos
  quantidadeEstoque: number;
};

export type ProdutoUpdateInput = {
  nome: string;
  descricao: string | null;
  preco: number; // centavos
  quantidadeEstoque: number;
  ativo: boolean;
};

export function listarProdutos(): Promise<Produto[]> {
  return apiFetch("/produtos", produtosSchema);
}

export function obterProduto(id: number): Promise<Produto> {
  return apiFetch(`/produtos/${id}`, produtoSchema);
}

export function criarProduto(token: string, dados: ProdutoCreateInput): Promise<Produto> {
  return apiFetch("/produtos", produtoSchema, {
    method: "POST",
    token,
    json: {
      sku: dados.sku,
      nome: dados.nome,
      descricao: dados.descricao,
      preco: dados.preco,
      quantidade_estoque: dados.quantidadeEstoque,
    },
  });
}

export function atualizarProduto(
  token: string,
  id: number,
  dados: ProdutoUpdateInput,
): Promise<Produto> {
  return apiFetch(`/produtos/${id}`, produtoSchema, {
    method: "PATCH",
    token,
    json: {
      nome: dados.nome,
      descricao: dados.descricao,
      preco: dados.preco,
      quantidade_estoque: dados.quantidadeEstoque,
      ativo: dados.ativo,
    },
  });
}

export function removerProduto(token: string, id: number): Promise<void> {
  return apiFetchVoid(`/produtos/${id}`, { method: "DELETE", token });
}
