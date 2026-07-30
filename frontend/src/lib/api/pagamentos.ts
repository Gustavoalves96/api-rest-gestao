import { apiFetch } from "@/lib/api/client";
import { type Pagamento, pagamentoSchema } from "@/lib/api/schemas";

export function criarCobranca(token: string, pedidoId: number): Promise<Pagamento> {
  return apiFetch(`/pedidos/${pedidoId}/pagamento`, pagamentoSchema, {
    method: "POST",
    token,
  });
}

export function obterCobranca(token: string, pedidoId: number): Promise<Pagamento> {
  return apiFetch(`/pedidos/${pedidoId}/pagamento`, pagamentoSchema, { token });
}
