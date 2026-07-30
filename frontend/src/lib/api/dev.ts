import { apiFetch } from "@/lib/api/client";
import { type Pagamento, pagamentoSchema } from "@/lib/api/schemas";

export type ResultadoSimulado = "confirmar" | "expirar" | "falhar";

/**
 * Simula a resposta do gateway (só existe no backend quando PAYMENT_GATEWAY=fake).
 * Usado apenas em desenvolvimento para exercitar o fluxo de ponta a ponta.
 */
export function simularPagamento(
  token: string,
  pedidoId: number,
  resultado: ResultadoSimulado = "confirmar",
): Promise<Pagamento> {
  return apiFetch(`/dev/pagamentos/${pedidoId}/simular`, pagamentoSchema, {
    method: "POST",
    token,
    json: { resultado },
  });
}
