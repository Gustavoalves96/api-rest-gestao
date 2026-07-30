"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect } from "react";

import { listarPedidos } from "@/lib/api/pedidos";
import type { StatusPedido } from "@/lib/api/schemas";
import { useAuth } from "@/lib/auth/context";
import { formatBRL } from "@/lib/money";

const ROTULO_STATUS: Record<StatusPedido, string> = {
  pendente: "Pendente",
  pago: "Pago",
  cancelado: "Cancelado",
};

const COR_STATUS: Record<StatusPedido, string> = {
  pendente: "bg-amber-100 text-amber-800",
  pago: "bg-emerald-100 text-emerald-800",
  cancelado: "bg-zinc-200 text-zinc-700",
};

export default function PedidosPage() {
  const router = useRouter();
  const { token, carregando } = useAuth();

  useEffect(() => {
    if (!carregando && token === null) {
      router.replace("/login");
    }
  }, [carregando, token, router]);

  const { data, isLoading, isError } = useQuery({
    queryKey: ["pedidos"],
    queryFn: () => listarPedidos(token as string),
    enabled: token !== null,
  });

  if (carregando || token === null || isLoading) {
    return <p className="text-zinc-600 dark:text-zinc-400">Carregando…</p>;
  }
  if (isError || data === undefined) {
    return <p className="text-red-600">Não foi possível carregar seus pedidos.</p>;
  }
  if (data.length === 0) {
    return <p className="text-zinc-600 dark:text-zinc-400">Você ainda não fez pedidos.</p>;
  }

  return (
    <div>
      <h1 className="mb-6 text-xl font-semibold">Meus pedidos</h1>
      <ul className="flex flex-col gap-3">
        {data.map((pedido) => (
          <li
            key={pedido.id}
            className="flex items-center justify-between rounded-lg border border-black/10 bg-white p-4 dark:border-white/10 dark:bg-zinc-900"
          >
            <div>
              <p className="font-medium">Pedido #{pedido.id}</p>
              <p className="text-sm text-zinc-600 dark:text-zinc-400">
                {pedido.itens.length} item(ns) · {formatBRL(pedido.total)}
              </p>
            </div>
            <div className="flex items-center gap-3">
              <span
                className={`rounded-full px-3 py-1 text-xs font-medium ${COR_STATUS[pedido.status]}`}
              >
                {ROTULO_STATUS[pedido.status]}
              </span>
              {pedido.status === "pendente" && (
                <Link
                  href={`/checkout/${pedido.id}`}
                  className="text-sm text-emerald-600 hover:underline"
                >
                  Pagar
                </Link>
              )}
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}
