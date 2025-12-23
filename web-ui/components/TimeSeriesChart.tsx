'use client';

import { TimeSeriesPoint } from '@/lib/api';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { format, parseISO } from 'date-fns';

interface TimeSeriesChartProps {
  data: TimeSeriesPoint[];
  groupBy?: string | null;
}

export default function TimeSeriesChart({ data, groupBy }: TimeSeriesChartProps) {
  const formatDate = (dateStr: string) => {
    try {
      const date = parseISO(dateStr);
      return format(date, 'dd.MM.yyyy');
    } catch {
      return dateStr;
    }
  };

  // Группируем данные если есть группировка
  const chartData = data.map((point) => ({
    date: formatDate(point.date),
    value: point.value,
    category: point.category || '',
    brand: point.brand || '',
  }));

  return (
    <div className="bg-white shadow rounded-lg p-6">
      <h3 className="text-lg font-medium text-gray-900 mb-4">
        Динамика добавлений в избранное
        {groupBy && ` (по ${groupBy === 'category' ? 'категориям' : 'брендам'})`}
      </h3>
      <ResponsiveContainer width="100%" height={400}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis />
          <Tooltip />
          <Legend />
          {groupBy === 'category' ? (
            <Line type="monotone" dataKey="value" stroke="#3b82f6" name="Добавлений" />
          ) : groupBy === 'brand' ? (
            <Line type="monotone" dataKey="value" stroke="#10b981" name="Добавлений" />
          ) : (
            <Line type="monotone" dataKey="value" stroke="#3b82f6" name="Добавлений" />
          )}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

