'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { getCars, type Car } from '@/lib/api';

function formatPrice(n: number | null): string {
  if (n == null) return '—';
  if (n >= 10_000) return `${(n / 10_000).toFixed(1)}万`;
  return n.toLocaleString();
}

export default function HomePage() {
  const { token, logout, isReady } = useAuth();
  const router = useRouter();
  const [cars, setCars] = useState<Car[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!isReady) return;
    if (!token) {
      router.replace('/login');
      return;
    }
    let cancelled = false;
    getCars(token)
      .then((data) => {
        if (!cancelled) setCars(data);
      })
      .catch((e) => {
        if (!cancelled) {
          setError(e.message);
          if (e.message === 'Unauthorized') router.replace('/login');
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => { cancelled = true; };
  }, [token, isReady, router]);

  if (!isReady || !token) return null;

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-900">
      <header className="sticky top-0 z-10 border-b border-slate-200 dark:border-slate-700 bg-white/95 dark:bg-slate-800/95 backdrop-blur">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-4 flex items-center justify-between">
          <h1 className="text-xl font-semibold text-slate-800 dark:text-slate-100">
            Car ads
          </h1>
          <button
            onClick={() => { logout(); router.replace('/login'); }}
            className="text-sm text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white"
          >
            Sign out
          </button>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 py-6">
        {error && (
          <div className="rounded-lg bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 text-sm px-4 py-3 mb-4">
            {error}
          </div>
        )}
        {loading ? (
          <div className="flex items-center justify-center py-20">
            <div className="animate-spin rounded-full h-10 w-10 border-2 border-brand-500 border-t-transparent" />
          </div>
        ) : (
          <div className="rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 overflow-hidden shadow-sm">
            <div className="overflow-x-auto">
              <table className="w-full text-left">
                <thead>
                  <tr className="border-b border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/80">
                    <th className="px-4 py-3 text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                      Make
                    </th>
                    <th className="px-4 py-3 text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                      Model
                    </th>
                    <th className="px-4 py-3 text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                      Year
                    </th>
                    <th className="px-4 py-3 text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                      Price
                    </th>
                    <th className="px-4 py-3 text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider hidden sm:table-cell">
                      Color
                    </th>
                    <th className="px-4 py-3 text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                      Link
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {cars.length === 0 ? (
                    <tr>
                      <td colSpan={6} className="px-4 py-12 text-center text-slate-500 dark:text-slate-400">
                        No cars yet. The scraper will fill the database periodically.
                      </td>
                    </tr>
                  ) : (
                    cars.map((c) => (
                      <tr
                        key={c.id}
                        className="border-b border-slate-100 dark:border-slate-700/50 hover:bg-slate-50/50 dark:hover:bg-slate-800/50 transition"
                      >
                        <td className="px-4 py-3 text-slate-800 dark:text-slate-200">
                          {c.make ?? '—'}
                        </td>
                        <td className="px-4 py-3 text-slate-800 dark:text-slate-200 max-w-[200px] truncate">
                          {c.model ?? '—'}
                        </td>
                        <td className="px-4 py-3 text-slate-600 dark:text-slate-300">
                          {c.year ?? '—'}
                        </td>
                        <td className="px-4 py-3 text-slate-800 dark:text-slate-200 whitespace-nowrap">
                          {formatPrice(c.price)}
                        </td>
                        <td className="px-4 py-3 text-slate-600 dark:text-slate-300 hidden sm:table-cell">
                          {c.color ?? '—'}
                        </td>
                        <td className="px-4 py-3">
                          <a
                            href={c.link}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-brand-600 dark:text-brand-400 hover:underline text-sm truncate block max-w-[180px] sm:max-w-none"
                          >
                            View ad
                          </a>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
