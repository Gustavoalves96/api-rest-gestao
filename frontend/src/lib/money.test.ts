import { describe, expect, it } from "vitest";

import { formatBRL } from "@/lib/money";

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
