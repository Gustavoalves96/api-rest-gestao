const CHAVE = "gestao.token";

type Listener = () => void;
let listeners: Listener[] = [];

function emitir(): void {
  for (const l of listeners) l();
}

/**
 * Store externo do JWT (localStorage), consumido via `useSyncExternalStore`.
 * Evita `setState` dentro de efeito e mantém o SSR consistente (snapshot do
 * servidor é sempre `null`; o valor real entra após a hidratação).
 */
export const tokenStore = {
  subscribe(listener: Listener): () => void {
    listeners.push(listener);
    // Sincroniza entre abas.
    const onStorage = (e: StorageEvent) => {
      if (e.key === CHAVE) listener();
    };
    window.addEventListener("storage", onStorage);
    return () => {
      listeners = listeners.filter((l) => l !== listener);
      window.removeEventListener("storage", onStorage);
    };
  },
  getSnapshot(): string | null {
    return window.localStorage.getItem(CHAVE);
  },
  getServerSnapshot(): string | null {
    return null;
  },
  definir(token: string | null): void {
    if (token === null) {
      window.localStorage.removeItem(CHAVE);
    } else {
      window.localStorage.setItem(CHAVE, token);
    }
    emitir();
  },
};
