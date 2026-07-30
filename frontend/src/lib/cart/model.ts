/** Item do carrinho. `preco` é o preço unitário em centavos (snapshot para exibição). */
export type ItemCarrinho = {
  produtoId: number;
  sku: string;
  nome: string;
  preco: number;
  quantidade: number;
};

/** Adiciona um item; se o produto já está no carrinho, soma a quantidade. */
export function adicionarItem(itens: ItemCarrinho[], novo: ItemCarrinho): ItemCarrinho[] {
  const existente = itens.find((i) => i.produtoId === novo.produtoId);
  if (existente === undefined) {
    return [...itens, novo];
  }
  return itens.map((i) =>
    i.produtoId === novo.produtoId ? { ...i, quantidade: i.quantidade + novo.quantidade } : i,
  );
}

/** Define a quantidade de um item; quantidade <= 0 remove o item. */
export function definirQuantidade(
  itens: ItemCarrinho[],
  produtoId: number,
  quantidade: number,
): ItemCarrinho[] {
  if (quantidade <= 0) {
    return removerItem(itens, produtoId);
  }
  return itens.map((i) => (i.produtoId === produtoId ? { ...i, quantidade } : i));
}

export function removerItem(itens: ItemCarrinho[], produtoId: number): ItemCarrinho[] {
  return itens.filter((i) => i.produtoId !== produtoId);
}

/** Total do carrinho, em centavos. */
export function calcularTotal(itens: ItemCarrinho[]): number {
  return itens.reduce((soma, i) => soma + i.preco * i.quantidade, 0);
}

/** Quantidade total de unidades no carrinho. */
export function calcularQuantidade(itens: ItemCarrinho[]): number {
  return itens.reduce((soma, i) => soma + i.quantidade, 0);
}
