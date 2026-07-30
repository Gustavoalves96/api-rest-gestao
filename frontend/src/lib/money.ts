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
