import { apiFetch } from "@/lib/api/client";
import { type Produto, produtosSchema } from "@/lib/api/schemas";

export function listarProdutos(): Promise<Produto[]> {
  return apiFetch("/produtos", produtosSchema);
}
