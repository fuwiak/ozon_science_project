'use client';

import { useState } from 'react';
import { useTopProducts, useDemandTrends, useTimeSeries, useCategories } from '@/lib/hooks/use-api';
import TimeSeriesChart from '@/components/TimeSeriesChart';
import { BarChart3, TrendingUp } from 'lucide-react';

export default function AnalyticsPage() {
  const [selectedCategory, setSelectedCategory] = useState<string>('');
  const [groupBy, setGroupBy] = useState<'category' | 'brand' | 'period'>('category');
  const [period, setPeriod] = useState<'day' | 'week' | 'month'>('month');

  // Используем кэшированные данные
  const { data: topProducts = [], isLoading: topProductsLoading } = useTopProducts({ limit: 20, category: selectedCategory || undefined });
  const { data: trends = [], isLoading: trendsLoading } = useDemandTrends({ 
    category: selectedCategory || undefined, 
    group_by: groupBy 
  });
  const { data: timeSeries, isLoading: timeSeriesLoading } = useTimeSeries({ 
    category: selectedCategory || undefined, 
    period, 
    group_by: groupBy === 'period' ? undefined : groupBy 
  });
  const { data: categories = [] } = useCategories();

  const loading = topProductsLoading || trendsLoading || timeSeriesLoading;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8 fade-in">
        <h1 className="text-4xl font-bold bg-gradient-to-r from-[#005BFF] to-[#00D9FF] bg-clip-text text-transparent">
          Аналитика спроса
        </h1>
        <p className="mt-3 text-lg text-gray-600">
          Анализ трендов, топ товаров и динамики добавлений в избранное
        </p>
      </div>

      {/* Фильтры */}
      <div className="card p-6 mb-6 bg-gradient-to-br from-white to-cyan-50/30">
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Категория
            </label>
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="w-full rounded-xl border-2 border-gray-200 shadow-sm focus:border-[#005BFF] focus:ring-2 focus:ring-[#005BFF]/20 transition-all"
            >
              <option value="">Все категории</option>
              {categories.map((cat) => (
                <option key={cat} value={cat}>
                  {cat}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Группировка
            </label>
            <select
              value={groupBy}
              onChange={(e) => setGroupBy(e.target.value as 'category' | 'brand' | 'period')}
              className="w-full rounded-xl border-2 border-gray-200 shadow-sm focus:border-[#005BFF] focus:ring-2 focus:ring-[#005BFF]/20 transition-all"
            >
              <option value="category">По категориям</option>
              <option value="brand">По брендам</option>
              <option value="period">По периодам</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Период агрегации
            </label>
            <select
              value={period}
              onChange={(e) => setPeriod(e.target.value as 'day' | 'week' | 'month')}
              className="w-full rounded-xl border-2 border-gray-200 shadow-sm focus:border-[#005BFF] focus:ring-2 focus:ring-[#005BFF]/20 transition-all"
            >
              <option value="day">День</option>
              <option value="week">Неделя</option>
              <option value="month">Месяц</option>
            </select>
          </div>
        </div>
      </div>

      {/* Временной ряд */}
      {timeSeries && timeSeries.data && timeSeries.data.length > 0 && (
        <div className="mb-8">
          <TimeSeriesChart data={timeSeries.data} groupBy={timeSeries.group_by} />
        </div>
      )}

      {/* Топ товаров */}
      <div className="mb-8">
        <div className="card overflow-hidden">
          <div className="px-6 py-5 border-b border-gray-200 bg-gradient-to-r from-[#00D9FF]/10 to-[#005BFF]/10">
            <div className="flex items-center">
              <div className="bg-gradient-to-r from-[#005BFF] to-[#00D9FF] p-2 rounded-lg mr-3">
                <TrendingUp className="h-5 w-5 text-white" />
              </div>
              <h2 className="text-xl font-bold text-gray-900">Топ товаров по спросу</h2>
            </div>
          </div>
          <div className="p-6">
            {loading ? (
              <div className="animate-pulse space-y-4">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="h-16 bg-gray-200 rounded" />
                ))}
              </div>
            ) : topProducts.length === 0 ? (
              <p className="text-gray-500 text-center py-8">Нет данных</p>
            ) : (
              <div className="space-y-3">
                {topProducts.map((product, index) => (
                  <div key={product.product_id} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50">
                    <div className="flex items-center space-x-4">
                      <div className="flex-shrink-0 w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                        <span className="text-sm font-bold text-blue-600">{index + 1}</span>
                      </div>
                      <div>
                        <h3 className="text-sm font-medium text-gray-900">{product.product_name}</h3>
                        <p className="text-sm text-gray-500">
                          {product.category_level_1 || 'Без категории'} • {product.brand || 'Без бренда'}
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-lg font-semibold text-gray-900">
                        {product.favorites_count.toLocaleString()}
                      </div>
                      <div className="text-xs text-gray-500">добавлений</div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Тренды */}
      <div>
        <div className="card overflow-hidden">
          <div className="px-6 py-5 border-b border-gray-200 bg-gradient-to-r from-[#005BFF]/10 to-[#00D9FF]/10">
            <div className="flex items-center">
              <div className="bg-gradient-to-r from-[#005BFF] to-[#00D9FF] p-2 rounded-lg mr-3">
                <BarChart3 className="h-5 w-5 text-white" />
              </div>
              <h2 className="text-xl font-bold text-gray-900">Тренды спроса</h2>
            </div>
          </div>
          <div className="p-6">
            {loading ? (
              <div className="animate-pulse space-y-4">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="h-16 bg-gray-200 rounded" />
                ))}
              </div>
            ) : trends.length === 0 ? (
              <p className="text-gray-500 text-center py-8">Нет данных</p>
            ) : (
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Период
                      </th>
                      {groupBy === 'category' && (
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Категория
                        </th>
                      )}
                      {groupBy === 'brand' && (
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Бренд
                        </th>
                      )}
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Всего добавлений
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Уникальных товаров
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Среднее на товар
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {trends.map((trend, index) => (
                      <tr key={index} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {trend.period}
                        </td>
                        {groupBy === 'category' && (
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {trend.category || '-'}
                          </td>
                        )}
                        {groupBy === 'brand' && (
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {trend.brand || '-'}
                          </td>
                        )}
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-semibold text-gray-900">
                          {trend.total_favorites.toLocaleString()}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {trend.unique_products}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {trend.avg_favorites_per_product.toFixed(1)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

