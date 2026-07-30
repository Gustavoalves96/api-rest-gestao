"use client";

import { QRCodeSVG } from "qrcode.react";
import Link from "next/link";
import { useEffect } from "react";
import { useMutation } from "@tanstack/react-query";

import { CopyButton } from "@/components/copy-button";
import { criarCobranca } from "@/lib/api/pagamentos";
import { usePagamento } from "@/hooks/usePagamento";
import { type PagamentoState, toPagamentoState } from "@/lib/pagamento-state";
import { formatBRL } from "@/lib/money";

export function PixCheckout({ token, pedidoId }: { token: string; pedidoId: number }) {
  // Garante a cobrança uma vez (o backend é idempotente: reaproveita a vigente).
  const cobranca = useMutation({
    mutationFn: () => criarCobranca(token, pedidoId),
  });

  useEffect(() => {
    cobranca.mutate();
    // Rodar só uma vez ao montar; `mutate` é estável.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const consulta = usePagamento(token, pedidoId, cobranca.isSuccess);
  const pagamento = consulta.data ?? cobranca.data;

  if (cobranca.isError) {
    return <p className="text-red-600">Não foi possível gerar a cobrança deste pedido.</p>;
  }
  if (pagamento === undefined) {
    return <p className="text-zinc-600 dark:text-zinc-400">Gerando cobrança…</p>;
  }

  const estado = toPagamentoState(pagamento);

  return (
    <div className="mx-auto max-w-md rounded-xl border border-black/10 bg-white p-6 dark:border-white/10 dark:bg-zinc-900">
      <div className="mb-4 flex items-baseline justify-between">
        <h1 className="text-lg font-semibold">Pagamento do pedido #{pedidoId}</h1>
        <span className="text-lg font-semibold">{formatBRL(pagamento.valor)}</span>
      </div>
      <EstadoPagamento estado={estado} />
    </div>
  );
}

function EstadoPagamento({ estado }: { estado: PagamentoState }) {
  switch (estado.status) {
    case "pendente":
      return (
        <div className="flex flex-col items-center gap-4">
          <p className="text-sm text-zinc-600 dark:text-zinc-400">
            Escaneie o QR Code no app do seu banco ou use o copia-e-cola.
          </p>
          <div className="rounded-lg bg-white p-3">
            <QRCodeSVG value={estado.copiaECola} size={200} />
          </div>
          <div className="w-full">
            <p className="mb-1 text-xs uppercase tracking-wide text-zinc-500">Pix copia-e-cola</p>
            <div className="flex items-center gap-2">
              <code className="flex-1 truncate rounded-md bg-black/5 px-3 py-2 text-xs dark:bg-white/10">
                {estado.copiaECola}
              </code>
              <CopyButton value={estado.copiaECola} />
            </div>
          </div>
          <p className="flex items-center gap-2 text-sm text-amber-600">
            <span className="inline-block h-2 w-2 animate-pulse rounded-full bg-amber-500" />
            Aguardando confirmação do pagamento…
          </p>
        </div>
      );
    case "confirmado":
      return (
        <div className="flex flex-col items-center gap-3 py-4 text-center">
          <span className="text-4xl">✅</span>
          <p className="font-medium text-emerald-600">Pagamento confirmado!</p>
          <p className="text-sm text-zinc-600 dark:text-zinc-400">
            Confirmado em {formatarData(estado.confirmadoEm)}.
          </p>
          <Link href="/pedidos" className="mt-2 text-sm text-emerald-600 hover:underline">
            Ver meus pedidos
          </Link>
        </div>
      );
    case "expirado":
      return (
        <div className="flex flex-col items-center gap-3 py-4 text-center">
          <span className="text-4xl">⌛</span>
          <p className="font-medium">A cobrança expirou.</p>
          <Link href="/produtos" className="text-sm text-emerald-600 hover:underline">
            Voltar aos produtos
          </Link>
        </div>
      );
    case "falhou":
      return (
        <div className="flex flex-col items-center gap-3 py-4 text-center">
          <span className="text-4xl">⚠️</span>
          <p className="font-medium text-red-600">{estado.motivo}</p>
          <Link href="/produtos" className="text-sm text-emerald-600 hover:underline">
            Voltar aos produtos
          </Link>
        </div>
      );
  }
}

function formatarData(iso: string): string {
  if (iso === "") return "agora";
  const data = new Date(iso);
  return Number.isNaN(data.getTime()) ? "agora" : data.toLocaleString("pt-BR");
}
