import { z } from "zod";

/**
 * Schemas Zod para validar TODA resposta da API na borda. A API fala snake_case;
 * aqui traduzimos para camelCase e o resto do app consome só os tipos inferidos.
 */

export const usuarioSchema = z
  .object({
    id: z.number(),
    email: z.string(),
    nome: z.string(),
    ativo: z.boolean(),
  })
  .transform((u) => ({ id: u.id, email: u.email, nome: u.nome, ativo: u.ativo }));
export type Usuario = z.infer<typeof usuarioSchema>;

export const tokenSchema = z
  .object({
    access_token: z.string(),
    token_type: z.string(),
  })
  .transform((t) => ({ accessToken: t.access_token, tokenType: t.token_type }));
export type Token = z.infer<typeof tokenSchema>;

export const produtoSchema = z
  .object({
    id: z.number(),
    sku: z.string(),
    nome: z.string(),
    descricao: z.string().nullable(),
    preco: z.number().int(),
    quantidade_estoque: z.number().int(),
    ativo: z.boolean(),
  })
  .transform((p) => ({
    id: p.id,
    sku: p.sku,
    nome: p.nome,
    descricao: p.descricao,
    preco: p.preco,
    quantidadeEstoque: p.quantidade_estoque,
    ativo: p.ativo,
  }));
export type Produto = z.infer<typeof produtoSchema>;
export const produtosSchema = z.array(produtoSchema);

export const statusPedidoSchema = z.enum(["pendente", "pago", "cancelado"]);
export type StatusPedido = z.infer<typeof statusPedidoSchema>;

export const itemPedidoSchema = z
  .object({
    id: z.number(),
    produto_id: z.number(),
    quantidade: z.number().int(),
    preco_unitario: z.number().int(),
    subtotal: z.number().int(),
  })
  .transform((i) => ({
    id: i.id,
    produtoId: i.produto_id,
    quantidade: i.quantidade,
    precoUnitario: i.preco_unitario,
    subtotal: i.subtotal,
  }));
export type ItemPedido = z.infer<typeof itemPedidoSchema>;

export const pedidoSchema = z
  .object({
    id: z.number(),
    usuario_id: z.number(),
    status: statusPedidoSchema,
    total: z.number().int(),
    itens: z.array(itemPedidoSchema),
  })
  .transform((p) => ({
    id: p.id,
    usuarioId: p.usuario_id,
    status: p.status,
    total: p.total,
    itens: p.itens,
  }));
export type Pedido = z.infer<typeof pedidoSchema>;
export const pedidosSchema = z.array(pedidoSchema);

export const statusPagamentoSchema = z.enum([
  "pendente",
  "confirmado",
  "falhou",
  "expirado",
  "estornado",
]);
export type StatusPagamento = z.infer<typeof statusPagamentoSchema>;

export const pagamentoSchema = z
  .object({
    id: z.number(),
    pedido_id: z.number(),
    external_id: z.string(),
    status: statusPagamentoSchema,
    valor: z.number().int(),
    metodo: z.string(),
    qr_code: z.string().nullable(),
    copia_e_cola: z.string().nullable(),
    expira_em: z.string().nullable(),
    confirmado_em: z.string().nullable(),
  })
  .transform((p) => ({
    id: p.id,
    pedidoId: p.pedido_id,
    externalId: p.external_id,
    status: p.status,
    valor: p.valor,
    metodo: p.metodo,
    qrCode: p.qr_code,
    copiaECola: p.copia_e_cola,
    expiraEm: p.expira_em,
    confirmadoEm: p.confirmado_em,
  }));
export type Pagamento = z.infer<typeof pagamentoSchema>;
