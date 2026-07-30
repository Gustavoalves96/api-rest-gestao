"use client";

import { useQuery } from "@tanstack/react-query";

import { obterCobranca } from "@/lib/api/pagamentos";
import { STATUS_TERMINAIS } from "@/lib/pagamento-state";

// Backoff crescente com teto de 30s (evita polling agressivo de intervalo fixo).
const INTERVALOS_MS = [2000, 4000, 8000, 16000, 30000] as const;

export function usePagamento(token: string | null, pedidoId: number, enabled = true) {
  return useQuery({
    queryKey: ["pagamento", pedidoId],
    queryFn: () => obterCobranca(token as string, pedidoId),
    enabled: token !== null && enabled,
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      if (status !== undefined && STATUS_TERMINAIS.has(status)) {
        return false; // estado terminal: para de consultar
      }
      const tentativa = query.state.dataUpdateCount;
      return INTERVALOS_MS[Math.min(tentativa, INTERVALOS_MS.length - 1)];
    },
  });
}
