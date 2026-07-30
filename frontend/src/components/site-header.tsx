"use client";

import Link from "next/link";

import { useCart } from "@/hooks/useCart";
import { useAuth } from "@/lib/auth/context";

export function SiteHeader() {
  const { token, carregando, sair } = useAuth();
  const { quantidade } = useCart();

  return (
    <header className="border-b border-black/10 bg-white/60 dark:border-white/10 dark:bg-black/30">
      <div className="mx-auto flex w-full max-w-4xl items-center justify-between px-4 py-3">
        <Link href="/" className="font-semibold">
          Gestão<span className="text-emerald-600">.</span>
        </Link>
        <nav className="flex items-center gap-4 text-sm">
          <Link href="/produtos" className="hover:underline">
            Produtos
          </Link>
          <Link href="/carrinho" className="hover:underline">
            Carrinho
            {quantidade > 0 && (
              <span className="ml-1 rounded-full bg-emerald-600 px-1.5 py-0.5 text-xs text-white">
                {quantidade}
              </span>
            )}
          </Link>
          {!carregando &&
            (token !== null ? (
              <>
                <Link href="/pedidos" className="hover:underline">
                  Meus pedidos
                </Link>
                <Link href="/admin/produtos" className="hover:underline">
                  Admin
                </Link>
                <button
                  type="button"
                  onClick={sair}
                  className="rounded-md border border-black/15 px-3 py-1 hover:bg-black/5 dark:border-white/20 dark:hover:bg-white/10"
                >
                  Sair
                </button>
              </>
            ) : (
              <Link
                href="/login"
                className="rounded-md bg-emerald-600 px-3 py-1 text-white hover:bg-emerald-700"
              >
                Entrar
              </Link>
            ))}
        </nav>
      </div>
    </header>
  );
}
