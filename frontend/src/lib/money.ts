/**
 * Formata um valor monetário para exibição.
 *
 * O valor trafega em centavos (int) por toda a stack; a divisão por 100 só
 * acontece aqui, na renderização. Como `centavos` é inteiro, a divisão é
 * exata dentro do intervalo seguro de números — não há erro de ponto flutuante.
 */
export function formatBRL(centavos: number): string {
  return new Intl.NumberFormat("pt-BR", {
    style: "currency",
    currency: "BRL",
  }).format(centavos / 100);
}

/**
 * Converte um valor em reais digitado ("199,90" ou "199.90") para centavos (int).
 * Retorna `NaN` se a entrada não for um número válido (o formulário valida).
 */
export function reaisParaCentavos(valor: string): number {
  const normalizado = valor.trim().replace(",", ".");
  const reais = Number(normalizado);
  if (normalizado === "" || !Number.isFinite(reais)) return NaN;
  // Arredonda para o centavo mais próximo para não sobrar resíduo de ponto
  // flutuante (ex.: 19.99 * 100 = 1998.9999…).
  return Math.round(reais * 100);
}
