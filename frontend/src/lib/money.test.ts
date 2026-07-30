import { describe, expect, it } from "vitest";

import { formatBRL, reaisParaCentavos } from "@/lib/money";

describe("formatBRL", () => {
  // Não fixamos o caractere de espaço (varia com a versão do ICU); checamos o conteúdo.
  it("formata centavos como reais", () => {
    expect(formatBRL(19990)).toContain("199,90");
    expect(formatBRL(19990).startsWith("R$")).toBe(true);
  });

  it("formata zero", () => {
    expect(formatBRL(0)).toContain("0,00");
  });

  it("trata valores altos com separador de milhar", () => {
    expect(formatBRL(1234567)).toContain("12.345,67");
  });
});

describe("reaisParaCentavos", () => {
  it("converte usando vírgula ou ponto", () => {
    expect(reaisParaCentavos("199,90")).toBe(19990);
    expect(reaisParaCentavos("199.90")).toBe(19990);
  });

  it("arredonda sem resíduo de ponto flutuante", () => {
    expect(reaisParaCentavos("19,99")).toBe(1999);
    expect(reaisParaCentavos("0,10")).toBe(10);
  });

  it("retorna NaN para entrada inválida ou vazia", () => {
    expect(Number.isNaN(reaisParaCentavos(""))).toBe(true);
    expect(Number.isNaN(reaisParaCentavos("abc"))).toBe(true);
  });
});
