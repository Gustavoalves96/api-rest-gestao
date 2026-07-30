import { apiFetch } from "@/lib/api/client";
import { type Pedido, pedidoSchema, pedidosSchema } from "@/lib/api/schemas";

export type ItemPedidoInput = { produtoId: number; quantidade: number };

export function criarPedido(token: string, itens: ItemPedidoInput[]): Promise<Pedido> {
  return apiFetch("/pedidos", pedidoSchema, {
    method: "POST",
    token,
    json: { itens: itens.map((i) => ({ produto_id: i.produtoId, quantidade: i.quantidade })) },
  });
}

export function obterPedido(token: string, pedidoId: number): Promise<Pedido> {
  return apiFetch(`/pedidos/${pedidoId}`, pedidoSchema, { token });
}

export function listarPedidos(token: string): Promise<Pedido[]> {
  return apiFetch("/pedidos", pedidosSchema, { token });
}
