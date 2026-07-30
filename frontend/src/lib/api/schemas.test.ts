import { describe, expect, it } from "vitest";

import { pagamentoSchema, produtoSchema } from "@/lib/api/schemas";

describe("produtoSchema", () => {
  it("valida e traduz snake_case para camelCase", () => {
    const produto = produtoSchema.parse({
      id: 1,
      sku: "SKU-1",
      nome: "Teclado",
      descricao: null,
      preco: 19990,
      quantidade_estoque: 5,
      ativo: true,
    });
    expect(produto.quantidadeEstoque).toBe(5);
    expect(produto.preco).toBe(19990);
  });

  it("rejeita payload inválido (validação na borda)", () => {
    expect(() => produtoSchema.parse({ id: "x", sku: 1 })).toThrow();
  });
});

describe("pagamentoSchema", () => {
  it("traduz os campos da cobrança", () => {
    const pagamento = pagamentoSchema.parse({
      id: 10,
      pedido_id: 3,
      external_id: "fake_abc",
      status: "pendente",
      valor: 10000,
      metodo: "pix",
      qr_code: "qr",
      copia_e_cola: "000201...",
      expira_em: "2026-01-01T00:00:00Z",
      confirmado_em: null,
    });
    expect(pagamento.pedidoId).toBe(3);
    expect(pagamento.copiaECola).toBe("000201...");
    expect(pagamento.status).toBe("pendente");
  });

  it("rejeita status desconhecido", () => {
    expect(() =>
      pagamentoSchema.parse({
        id: 1,
        pedido_id: 1,
        external_id: "x",
        status: "aprovado",
        valor: 1,
        metodo: "pix",
        qr_code: null,
        copia_e_cola: null,
        expira_em: null,
        confirmado_em: null,
      }),
    ).toThrow();
  });
});
