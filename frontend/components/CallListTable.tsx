import type { CallAnalysis } from '../lib/types';

export default function CallListTable({ calls }: { calls: CallAnalysis[] }) {
  if (calls.length === 0) {
    return (
      <div className="rounded-lg bg-white p-10 text-center text-gray-500 shadow" dir="rtl">
        هنوز مکالمه‌ای تحلیل نشده است.
      </div>
    );
  }

  return (
    <div className="bg-white shadow-md rounded-lg overflow-x-auto">
      <table className="min-w-full text-right" dir="rtl">
        <thead className="bg-gray-100 border-b">
          <tr>
            <th className="px-6 py-4 text-sm font-bold text-gray-700">شماره مشتری</th>
            <th className="px-6 py-4 text-sm font-bold text-gray-700">تاریخ تماس</th>
            <th className="px-6 py-4 text-sm font-bold text-gray-700">امتیاز لید (AI)</th>
            <th className="px-6 py-4 text-sm font-bold text-gray-700">عملکرد کارشناس</th>
            <th className="px-6 py-4 text-sm font-bold text-gray-700">نقاط ضعف اصلی</th>
          </tr>
        </thead>
        <tbody>
          {calls.map((call) => (
            <tr key={call.id} className="border-b hover:bg-gray-50 transition">
              <td className="px-6 py-4 font-mono text-gray-600">
                {call.customer_phone ?? 'نامشخص'}
              </td>
              <td className="px-6 py-4 text-gray-600">
                {new Intl.DateTimeFormat('fa-IR', {
                  dateStyle: 'medium',
                  timeStyle: 'short',
                }).format(new Date(call.date))}
              </td>
              <td className="px-6 py-4">
                <span className={`px-3 py-1 rounded-full text-sm font-bold ${
                  call.lead_score >= 70 ? 'bg-green-100 text-green-700' : 
                  call.lead_score >= 50 ? 'bg-yellow-100 text-yellow-700' : 
                  'bg-red-100 text-red-700'
                }`}>
                  {call.lead_score} / 100
                </span>
              </td>
              <td className="px-6 py-4 font-semibold text-gray-800">
                {call.agent_performance ?? 'نامشخص'}
              </td>
              <td className="px-6 py-4 text-red-500 text-sm">
                {(call.weaknesses ?? []).join('، ') || 'موردی ثبت نشده'}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
