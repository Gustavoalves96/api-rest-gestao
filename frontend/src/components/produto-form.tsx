"use client";

import { type FormEvent, useState } from "react";

import { reaisParaCentavos } from "@/lib/money";

export type ProdutoFormValues = {
  sku: string;
  nome: string;
  descricao: string | null;
  preco: number; // centavos
  quantidadeEstoque: number;
  ativo: boolean;
};

type ProdutoFormProps = {
  modo: "criar" | "editar";
  inicial?: {
    sku: string;
    nome: string;
    descricao: string | null;
    precoCentavos: number;
    quantidadeEstoque: number;
    ativo: boolean;
  };
  enviando: boolean;
  erro: string | null;
  onSubmit: (values: ProdutoFormValues) => void;
};

const inputClasse =
  "rounded-md border border-black/15 bg-white px-3 py-2 dark:border-white/20 dark:bg-zinc-900";

export function ProdutoForm({ modo, inicial, enviando, erro, onSubmit }: ProdutoFormProps) {
  const [sku, setSku] = useState(inicial?.sku ?? "");
  const [nome, setNome] = useState(inicial?.nome ?? "");
  const [descricao, setDescricao] = useState(inicial?.descricao ?? "");
  const [precoReais, setPrecoReais] = useState(
    inicial ? (inicial.precoCentavos / 100).toFixed(2) : "",
  );
  const [quantidade, setQuantidade] = useState(String(inicial?.quantidadeEstoque ?? 0));
  const [ativo, setAtivo] = useState(inicial?.ativo ?? true);
  const [erroLocal, setErroLocal] = useState<string | null>(null);

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setErroLocal(null);

    const centavos = reaisParaCentavos(precoReais);
    if (Number.isNaN(centavos) || centavos <= 0) {
      setErroLocal("Informe um preço válido, maior que zero.");
      return;
    }
    const estoque = Number(quantidade);
    if (!Number.isInteger(estoque) || estoque < 0) {
      setErroLocal("A quantidade em estoque deve ser um inteiro não negativo.");
      return;
    }

    onSubmit({
      sku: sku.trim(),
      nome: nome.trim(),
      descricao: descricao.trim() === "" ? null : descricao.trim(),
      preco: centavos,
      quantidadeEstoque: estoque,
      ativo,
    });
  }

  return (
    <form onSubmit={handleSubmit} className="flex max-w-md flex-col gap-4">
      <label className="flex flex-col gap-1 text-sm">
        SKU
        <input
          required
          value={sku}
          disabled={modo === "editar"}
          onChange={(e) => setSku(e.target.value)}
          className={`${inputClasse} disabled:opacity-60`}
        />
      </label>
      <label className="flex flex-col gap-1 text-sm">
        Nome
        <input
          required
          value={nome}
          onChange={(e) => setNome(e.target.value)}
          className={inputClasse}
        />
      </label>
      <label className="flex flex-col gap-1 text-sm">
        Descrição <span className="text-zinc-500">(opcional)</span>
        <textarea
          value={descricao}
          onChange={(e) => setDescricao(e.target.value)}
          rows={2}
          className={inputClasse}
        />
      </label>
      <div className="flex gap-4">
        <label className="flex flex-1 flex-col gap-1 text-sm">
          Preço (R$)
          <input
            required
            inputMode="decimal"
            placeholder="199,90"
            value={precoReais}
            onChange={(e) => setPrecoReais(e.target.value)}
            className={inputClasse}
          />
        </label>
        <label className="flex flex-1 flex-col gap-1 text-sm">
          Estoque
          <input
            required
            type="number"
            min={0}
            value={quantidade}
            onChange={(e) => setQuantidade(e.target.value)}
            className={inputClasse}
          />
        </label>
      </div>
      {modo === "editar" && (
        <label className="flex items-center gap-2 text-sm">
          <input type="checkbox" checked={ativo} onChange={(e) => setAtivo(e.target.checked)} />
          Produto ativo
        </label>
      )}
      {(erroLocal ?? erro) !== null && (
        <p className="text-sm text-red-600">{erroLocal ?? erro}</p>
      )}
      <button
        type="submit"
        disabled={enviando}
        className="rounded-md bg-emerald-600 px-4 py-2 text-white hover:bg-emerald-700 disabled:opacity-60"
      >
        {enviando ? "Salvando…" : modo === "criar" ? "Criar produto" : "Salvar alterações"}
      </button>
    </form>
  );
}
