import type { Pagamento } from "@/lib/api/schemas";

/**
 * Estado de pagamento como union discriminada: torna impossível, por exemplo,
 * renderizar a tela de sucesso sem `confirmadoEm`. Não usar booleanos soltos.
 */
export type PagamentoState =
  | { status: "pendente"; qrCode: string; copiaECola: string; expiraEm: string }
  | { status: "confirmado"; confirmadoEm: string }
  | { status: "expirado" }
  | { status: "falhou"; motivo: string };

export function toPagamentoState(p: Pagamento): PagamentoState {
  switch (p.status) {
    case "pendente":
      return {
        status: "pendente",
        qrCode: p.qrCode ?? "",
        copiaECola: p.copiaECola ?? "",
        expiraEm: p.expiraEm ?? "",
      };
    case "confirmado":
      return { status: "confirmado", confirmadoEm: p.confirmadoEm ?? "" };
    case "expirado":
      return { status: "expirado" };
    case "falhou":
      return { status: "falhou", motivo: "O pagamento não foi aprovado." };
    case "estornado":
      return { status: "falhou", motivo: "O pagamento foi estornado." };
  }
}

export const STATUS_TERMINAIS: ReadonlySet<Pagamento["status"]> = new Set([
  "confirmado",
  "falhou",
  "expirado",
  "estornado",
]);
