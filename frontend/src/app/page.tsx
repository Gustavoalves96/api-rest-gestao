import Link from "next/link";

export default function Home() {
  return (
    <div className="flex flex-col gap-6">
      <section className="rounded-xl border border-black/10 bg-white p-8 dark:border-white/10 dark:bg-zinc-900">
        <h1 className="text-2xl font-semibold tracking-tight">
          Loja de exemplo com checkout Pix
        </h1>
        <p className="mt-3 max-w-2xl text-zinc-600 dark:text-zinc-400">
          Frontend Next.js que consome a API de gestão: catálogo de produtos, criação de
          pedidos e pagamento via Pix com QR Code, copia-e-cola e acompanhamento do status
          em tempo real.
        </p>
        <div className="mt-6 flex gap-3">
          <Link
            href="/produtos"
            className="rounded-md bg-emerald-600 px-4 py-2 text-white hover:bg-emerald-700"
          >
            Ver produtos
          </Link>
          <Link
            href="/login"
            className="rounded-md border border-black/15 px-4 py-2 hover:bg-black/5 dark:border-white/20 dark:hover:bg-white/10"
          >
            Entrar
          </Link>
        </div>
      </section>
    </div>
  );
}
