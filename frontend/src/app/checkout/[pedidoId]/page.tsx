"use client";

import { useParams, useRouter } from "next/navigation";
import { useEffect } from "react";

import { PixCheckout } from "@/components/pix-checkout";
import { useAuth } from "@/lib/auth/context";

export default function CheckoutPage() {
  const params = useParams<{ pedidoId: string }>();
  const router = useRouter();
  const { token, carregando } = useAuth();

  useEffect(() => {
    if (!carregando && token === null) {
      router.replace("/login");
    }
  }, [carregando, token, router]);

  const pedidoId = Number(params.pedidoId);

  if (carregando || token === null) {
    return <p className="text-zinc-600 dark:text-zinc-400">Carregando…</p>;
  }
  if (!Number.isInteger(pedidoId)) {
    return <p className="text-red-600">Pedido inválido.</p>;
  }

  return <PixCheckout token={token} pedidoId={pedidoId} />;
}
