"use client";

import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useSyncExternalStore,
} from "react";

import { tokenStore } from "@/lib/auth/storage";

type AuthContextValue = {
  token: string | null;
  carregando: boolean;
  entrar: (token: string) => void;
  sair: () => void;
};

const AuthContext = createContext<AuthContextValue | null>(null);

// `hydrated` fica falso no SSR/primeiro render e vira true após a hidratação,
// sem precisar de setState em efeito.
const noop = () => () => {};

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const token = useSyncExternalStore(
    tokenStore.subscribe,
    tokenStore.getSnapshot,
    tokenStore.getServerSnapshot,
  );
  const hydrated = useSyncExternalStore(
    noop,
    () => true,
    () => false,
  );

  const entrar = useCallback((novo: string) => tokenStore.definir(novo), []);
  const sair = useCallback(() => tokenStore.definir(null), []);

  const value = useMemo(
    () => ({ token, carregando: !hydrated, entrar, sair }),
    [token, hydrated, entrar, sair],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (ctx === null) {
    throw new Error("useAuth precisa estar dentro de <AuthProvider>.");
  }
  return ctx;
}
