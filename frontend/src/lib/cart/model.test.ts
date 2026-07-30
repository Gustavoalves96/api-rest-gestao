import { describe, expect, it } from "vitest";

import {
  type ItemCarrinho,
  adicionarItem,
  calcularQuantidade,
  calcularTotal,
  definirQuantidade,
  removerItem,
} from "@/lib/cart/model";

function item(overrides: Partial<ItemCarrinho>): ItemCarrinho {
  return { produtoId: 1, sku: "SKU-1", nome: "Item", preco: 1000, quantidade: 1, ...overrides };
}

describe("adicionarItem", () => {
  it("acrescenta um item novo", () => {
    const itens = adicionarItem([], item({ produtoId: 1 }));
    expect(itens).toHaveLength(1);
  });

  it("soma a quantidade quando o produto já está no carrinho", () => {
    const inicial = [item({ produtoId: 1, quantidade: 2 })];
    const itens = adicionarItem(inicial, item({ produtoId: 1, quantidade: 3 }));
    expect(itens).toHaveLength(1);
    expect(itens[0].quantidade).toBe(5);
  });
});

describe("definirQuantidade", () => {
  it("atualiza a quantidade", () => {
    const itens = definirQuantidade([item({ produtoId: 1, quantidade: 1 })], 1, 4);
    expect(itens[0].quantidade).toBe(4);
  });

  it("remove o item quando a quantidade é zero ou menos", () => {
    const itens = definirQuantidade([item({ produtoId: 1 })], 1, 0);
    expect(itens).toHaveLength(0);
  });
});

describe("removerItem", () => {
  it("remove pelo produtoId", () => {
    const inicial = [item({ produtoId: 1 }), item({ produtoId: 2 })];
    expect(removerItem(inicial, 1)).toHaveLength(1);
  });
});

describe("totais", () => {
  const itens = [
    item({ produtoId: 1, preco: 5000, quantidade: 2 }),
    item({ produtoId: 2, preco: 1500, quantidade: 3 }),
  ];

  it("calcula o total em centavos", () => {
    expect(calcularTotal(itens)).toBe(14500);
  });

  it("calcula a quantidade de unidades", () => {
    expect(calcularQuantidade(itens)).toBe(5);
  });
});
