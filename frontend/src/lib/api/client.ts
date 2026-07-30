import type { z } from "zod";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

/** Erro de uma resposta HTTP não-2xx, com a mensagem de domínio da API. */
export class ApiError extends Error {
  constructor(
    public readonly status: number,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

type FetchOptions = {
  method?: "GET" | "POST" | "PATCH" | "DELETE";
  token?: string | null;
  json?: unknown;
  form?: Record<string, string>;
};

async function extrairDetalhe(res: Response): Promise<string> {
  try {
    const corpo: unknown = await res.json();
    if (
      typeof corpo === "object" &&
      corpo !== null &&
      "detail" in corpo &&
      typeof (corpo as { detail: unknown }).detail === "string"
    ) {
      return (corpo as { detail: string }).detail;
    }
  } catch {
    // sem corpo JSON
  }
  return `Erro ${res.status}`;
}

async function executar(path: string, opts: FetchOptions): Promise<Response> {
  const headers: Record<string, string> = {};
  let body: BodyInit | undefined;

  if (opts.json !== undefined) {
    headers["Content-Type"] = "application/json";
    body = JSON.stringify(opts.json);
  } else if (opts.form) {
    headers["Content-Type"] = "application/x-www-form-urlencoded";
    body = new URLSearchParams(opts.form).toString();
  }
  if (opts.token) {
    headers.Authorization = `Bearer ${opts.token}`;
  }

  const res = await fetch(`${BASE_URL}${path}`, {
    method: opts.method ?? "GET",
    headers,
    body,
  });

  if (!res.ok) {
    throw new ApiError(res.status, await extrairDetalhe(res));
  }
  return res;
}

/**
 * Faz a requisição e valida a resposta com o schema Zod fornecido. O app nunca
 * consome o JSON cru — só o tipo inferido do schema.
 */
export async function apiFetch<T>(
  path: string,
  schema: z.ZodType<T>,
  opts: FetchOptions = {},
): Promise<T> {
  const res = await executar(path, opts);
  const data: unknown = await res.json();
  return schema.parse(data);
}

/** Variante para respostas sem corpo (ex.: 204 No Content). */
export async function apiFetchVoid(path: string, opts: FetchOptions = {}): Promise<void> {
  await executar(path, opts);
}
