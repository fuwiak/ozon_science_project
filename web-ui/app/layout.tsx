'use client';

import { QueryClientProvider } from '@tanstack/react-query';
import { queryClient } from '@/lib/query-client';
import "./globals.css";
import Navbar from "@/components/Navbar";

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ru">
      <head>
        <title>Dynamic Pricing 1299$ - Система динамического ценообразования</title>
        <meta name="description" content="Мониторинг цен конкурентов, уровня спроса, остатков на складе и корректировки стоимости товаров" />
      </head>
      <body className="antialiased" style={{ background: 'linear-gradient(135deg, #F5F7FA 0%, #E8F0F8 100%)' }}>
        <QueryClientProvider client={queryClient}>
          <Navbar />
          <main className="min-h-screen">
            {children}
          </main>
        </QueryClientProvider>
      </body>
    </html>
  );
}
