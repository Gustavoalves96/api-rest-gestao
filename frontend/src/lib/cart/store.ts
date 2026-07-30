import {
  type ItemCarrinho,
  adicionarItem,
  definirQuantidade,
  removerItem,
} from "@/lib/cart/model";

const CHAVE = "gestao.carrinho";
// Referência estável para o snapshot de servidor (evita loop no useSyncExternalStore).
const VAZIO: ItemCarrinho[] = [];

let itens: ItemCarrinho[] = carregarInicial();
let listeners: Array<() => void> = [];

function carregarInicial(): ItemCarrinho[] {
  if (typeof window === "undefined") return VAZIO;
  try {
    const bruto = window.localStorage.getItem(CHAVE);
    if (bruto === null) return [];
    const dados: unknown = JSON.parse(bruto);
    return Array.isArray(dados) ? (dados as ItemCarrinho[]) : [];
  } catch {
    return [];
  }
}

function atualizar(novos: ItemCarrinho[]): void {
  itens = novos;
  if (typeof window !== "undefined") {
    window.localStorage.setItem(CHAVE, JSON.stringify(itens));
  }
  for (const l of listeners) l();
}

export const cartStore = {
  subscribe(listener: () => void): () => void {
    listeners.push(listener);
    return () => {
      listeners = listeners.filter((l) => l !== listener);
    };
  },
  getSnapshot(): ItemCarrinho[] {
    return itens;
  },
  getServerSnapshot(): ItemCarrinho[] {
    return VAZIO;
  },
  adicionar(item: ItemCarrinho): void {
    atualizar(adicionarItem(itens, item));
  },
  definirQuantidade(produtoId: number, quantidade: number): void {
    atualizar(definirQuantidade(itens, produtoId, quantidade));
  },
  remover(produtoId: number): void {
    atualizar(removerItem(itens, produtoId));
  },
  limpar(): void {
    atualizar([]);
  },
};
