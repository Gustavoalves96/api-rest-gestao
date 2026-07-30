"use client";

import { useSyncExternalStore } from "react";

import { type ItemCarrinho, calcularQuantidade, calcularTotal } from "@/lib/cart/model";
import { cartStore } from "@/lib/cart/store";

export function useCart() {
  const itens = useSyncExternalStore(
    cartStore.subscribe,
    cartStore.getSnapshot,
    cartStore.getServerSnapshot,
  );

  return {
    itens,
    quantidade: calcularQuantidade(itens),
    total: calcularTotal(itens),
    adicionar: (item: ItemCarrinho) => cartStore.adicionar(item),
    definirQuantidade: (produtoId: number, quantidade: number) =>
      cartStore.definirQuantidade(produtoId, quantidade),
    remover: (produtoId: number) => cartStore.remover(produtoId),
    limpar: () => cartStore.limpar(),
  };
}
