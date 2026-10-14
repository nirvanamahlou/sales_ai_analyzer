import type { CallAnalysis } from '../lib/types';

function toPersianNumber(value: number): string {
  return new Intl.NumberFormat('fa-IR').format(value);
}

export default function StatCards({ calls }: { calls: CallAnalysis[] }) {
  const averageLeadScore = calls.length
    ? Math.round(calls.reduce((total, call) => total + call.lead_score, 0) / calls.length)
    : 0;
  const strengthCounts = calls
    .flatMap((call) => call.strengths ?? [])
    .reduce<Record<string, number>>((counts, strength) => {
      counts[strength] = (counts[strength] ?? 0) + 1;
      return counts;
    }, {});
  const topStrength =
    Object.entries(strengthCounts).sort((left, right) => right[1] - left[1])[0]?.[0] ??
    'داده‌ای موجود نیست';

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8" dir="rtl">
      <div className="bg-white p-6 rounded-lg shadow border-r-4 border-blue-500">
        <h3 className="text-gray-500 text-sm font-bold">کل تماس‌های تحلیل شده</h3>
        <p className="text-3xl font-black mt-2 text-gray-800">{toPersianNumber(calls.length)}</p>
      </div>
      <div className="bg-white p-6 rounded-lg shadow border-r-4 border-green-500">
        <h3 className="text-gray-500 text-sm font-bold">میانگین امتیاز لیدها</h3>
        <p className="text-3xl font-black mt-2 text-green-600">
          {toPersianNumber(averageLeadScore)}٪
        </p>
      </div>
      <div className="bg-white p-6 rounded-lg shadow border-r-4 border-purple-500">
        <h3 className="text-gray-500 text-sm font-bold">برترین مهارت کارشناسان</h3>
        <p className="text-xl font-bold mt-3 text-gray-800">{topStrength}</p>
      </div>
    </div>
  );
}
