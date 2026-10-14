"use client";
import { useEffect, useState } from 'react';
import CallListTable from '../components/CallListTable';
import StatCards from '../components/StatCards';
import type { CallAnalysis } from '../lib/types';

export default function Dashboard() {
  const [calls, setCalls] = useState<CallAnalysis[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const controller = new AbortController();
    const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';

    fetch(`${apiUrl}/api/calls/recent`, { signal: controller.signal })
      .then((res) => {
        if (!res.ok) {
          throw new Error(`Request failed with status ${res.status}`);
        }
        return res.json() as Promise<CallAnalysis[]>;
      })
      .then((data) => {
        setCalls(data);
      })
      .catch((err) => {
        if (err instanceof DOMException && err.name === 'AbortError') {
          return;
        }
        console.error('خطا در دریافت اطلاعات از بک‌اند', err);
        setError('ارتباط با سرویس تحلیل برقرار نشد. لطفاً دوباره تلاش کنید.');
      })
      .finally(() => {
        setLoading(false);
      });

    return () => controller.abort();
  }, []);

  return (
    <main className="min-h-screen bg-gray-50 p-8 font-sans">
      <div className="max-w-7xl mx-auto">
        <header className="mb-10 text-right" dir="rtl">
          <h1 className="text-3xl font-black text-gray-900">سامانه هوشمند تحلیل فروش</h1>
          <p className="text-gray-500 mt-2">نظارت لحظه‌ای بر عملکرد کارشناسان و کیفیت لیدها</p>
        </header>

        <StatCards calls={calls} />

        <div className="mt-8">
          <h2 className="text-xl font-bold text-gray-800 mb-4 text-right" dir="rtl">آخرین مکالمات پردازش شده</h2>
          {loading ? (
            <div className="text-center py-10 text-gray-500">در حال دریافت داده‌ها از هوش مصنوعی...</div>
          ) : error ? (
            <div className="rounded-lg border border-red-200 bg-red-50 p-6 text-center text-red-700" dir="rtl">
              {error}
            </div>
          ) : (
            <CallListTable calls={calls} />
          )}
        </div>
      </div>
    </main>
  );
}
