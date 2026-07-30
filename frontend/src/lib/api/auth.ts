import { apiFetch } from "@/lib/api/client";
import { type Token, type Usuario, tokenSchema, usuarioSchema } from "@/lib/api/schemas";

export function registrar(email: string, nome: string, senha: string): Promise<Usuario> {
  return apiFetch("/auth/register", usuarioSchema, {
    method: "POST",
    json: { email, nome, senha },
  });
}

export function login(email: string, senha: string): Promise<Token> {
  // O padrão OAuth2 do backend espera os campos `username`/`password` via form.
  return apiFetch("/auth/login", tokenSchema, {
    method: "POST",
    form: { username: email, password: senha },
  });
}

export function obterUsuarioAtual(token: string): Promise<Usuario> {
  return apiFetch("/auth/me", usuarioSchema, { token });
}
