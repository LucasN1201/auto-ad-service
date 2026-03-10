import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import { Providers } from './providers';

const inter = Inter({ subsets: ['latin'], variable: '--font-sans' });

export const metadata: Metadata = {
  title: 'Auto-ad Service | Admin',
  description: 'Car ads admin panel',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={inter.variable}>
      <body className="min-h-screen font-sans bg-slate-50 text-slate-900 dark:bg-slate-900 dark:text-slate-100 antialiased">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
