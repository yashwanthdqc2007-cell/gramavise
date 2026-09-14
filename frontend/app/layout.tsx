import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Header } from "@/components/common/Header";
import { Footer } from "@/components/common/Footer";
import { LanguageProvider } from "@/lib/i18n";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "GramaVise — AI Business Advisory for Rural Micro-Entrepreneurs",
  description: "AI-driven hyper-local business advisory, financial structuring, and government scheme matcher for grassroots micro-enterprises.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.className} min-h-screen flex flex-col bg-[#050E17] text-slate-100 antialiased`}>
        <LanguageProvider>
          <Header />
          <main className="flex-grow bg-[#050E17]">{children}</main>
          <Footer />
        </LanguageProvider>
      </body>
    </html>
  );
}
