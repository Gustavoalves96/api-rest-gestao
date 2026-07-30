import { describe, expect, it } from "vitest";

import type { Pagamento } from "@/lib/api/schemas";
import { STATUS_TERMINAIS, toPagamentoState } from "@/lib/pagamento-state";

function pagamento(overrides: Partial<Pagamento>): Pagamento {
  return {
    id: 1,
    pedidoId: 1,
    externalId: "fake_1",
    status: "pendente",
    valor: 10000,
    metodo: "pix",
    qrCode: "qr",
    copiaECola: "000201",
    expiraEm: "2026-01-01T00:00:00Z",
    confirmadoEm: null,
    ...overrides,
  };
}

describe("toPagamentoState", () => {
  it("pendente carrega qrCode e copia-e-cola", () => {
    const estado = toPagamentoState(pagamento({ status: "pendente" }));
    expect(estado.status).toBe("pendente");
    if (estado.status === "pendente") {
      expect(estado.copiaECola).toBe("000201");
    }
  });

  it("confirmado carrega confirmadoEm", () => {
    const estado = toPagamentoState(
      pagamento({ status: "confirmado", confirmadoEm: "2026-01-02T10:00:00Z" }),
    );
    expect(estado).toEqual({ status: "confirmado", confirmadoEm: "2026-01-02T10:00:00Z" });
  });

  it("estornado vira falhou com motivo", () => {
    const estado = toPagamentoState(pagamento({ status: "estornado" }));
    expect(estado.status).toBe("falhou");
  });

  it("expirado não expõe dados de cobrança", () => {
    expect(toPagamentoState(pagamento({ status: "expirado" }))).toEqual({ status: "expirado" });
  });
});

describe("STATUS_TERMINAIS", () => {
  it("pendente não é terminal; confirmado é", () => {
    expect(STATUS_TERMINAIS.has("pendente")).toBe(false);
    expect(STATUS_TERMINAIS.has("confirmado")).toBe(true);
  });
});
