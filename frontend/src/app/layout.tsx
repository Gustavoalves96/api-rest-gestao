import type { Metadata } from "next";

import { SiteHeader } from "@/components/site-header";
import { Providers } from "@/components/providers";
import "./globals.css";

export const metadata: Metadata = {
  title: "Gestão — Estoque, Pedidos e Pagamentos",
  description: "Loja de exemplo com checkout Pix, consumindo a API de gestão.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="pt-BR" className="h-full antialiased">
      <body className="min-h-full flex flex-col">
        <Providers>
          <SiteHeader />
          <main className="mx-auto w-full max-w-4xl flex-1 px-4 py-8">{children}</main>
        </Providers>
      </body>
    </html>
  );
}
