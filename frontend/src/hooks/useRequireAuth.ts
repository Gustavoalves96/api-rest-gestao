"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";

import { useAuth } from "@/lib/auth/context";

/**
 * Garante que a página exige autenticação: redireciona para /login quando não
 * há token. Retorna o token (ou null enquanto redireciona/hidrata).
 */
export function useRequireAuth(): { token: string | null; pronto: boolean } {
  const router = useRouter();
  const { token, carregando } = useAuth();

  useEffect(() => {
    if (!carregando && token === null) {
      router.replace("/login");
    }
  }, [carregando, token, router]);

  return { token, pronto: !carregando && token !== null };
}
