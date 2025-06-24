import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geist = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "LetterChain | AI Cover Letter Generator",
  description: "Generate personalized cover letters using AI with LetterChain.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${geist.variable} ${geistMono.variable} antialiased bg-white text-navy-blue min-h-screen flex flex-col`}>
        <header className="w-full py-6 px-4 bg-white shadow-sm flex items-center justify-center sticky top-0 z-20">
          <div className="flex items-center gap-3">
            <span className="text-3xl">🔗</span>
            <span className="text-2xl font-bold tracking-tight text-navy-blue">LetterChain</span>
          </div>
          <span className="ml-4 text-base text-slate-gray font-medium hidden sm:inline">AI-powered cover letter generator</span>
        </header>
        <main className="flex-1 flex flex-col">{children}</main>
        <footer className="w-full py-4 px-4 bg-white border-t text-center text-sm text-slate-gray">© 2024 LetterChain</footer>
      </body>
    </html>
  );
}
