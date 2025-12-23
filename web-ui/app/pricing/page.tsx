'use client';

import { useEffect, useState } from 'react';
import { api, PricingMetric } from '@/lib/api';
import PriorityBadge from '@/components/PriorityBadge';
import { DollarSign, AlertTriangle, TrendingUp, Package } from 'lucide-react';

export default function PricingPage() {
  const [metrics, setMetrics] = useState<PricingMetric[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState<string>('');
  const [categories, setCategories] = useState<string[]>([]);
  const [minDays, setMinDays] = useState<string>('15');
  const [sortBy, setSortBy] = useState<'priority' | 'demand' | 'days'>('priority');

  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const cats = await api.getCategories();
        setCategories(cats);
      } catch (error) {
        console.error('Ошибка загрузки категорий:', error);
      }
    };
    fetchCategories();
  }, []);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        setLoading(true);
        const params: any = {
          category: selectedCategory || undefined,
          min_days_out_of_stock: parseInt(minDays) || 15,
        };

        const response = await api.getPricingMetrics(params).catch(() => ({
          metrics: [
            {
              product_id: '1',
              product_name: 'Пример товара',
              brand: 'Пример бренд',
              category_level_1: 'Красота и здоровье',
              demand_level: 'high' as const,
              favorites_count: 15000,
              days_out_of_stock: 25,
              priority_score: 85,
              recommendation: 'Высокий приоритет: высокий спрос, рекомендуется пополнить в ближайшее время.',
            },
          ],
          total: 1,
        }));
        let sorted = [...response.metrics];

        // Сортировка
        if (sortBy === 'priority') {
          sorted.sort((a, b) => b.priority_score - a.priority_score);
        } else if (sortBy === 'demand') {
          sorted.sort((a, b) => {
            const demandOrder = { high: 3, medium: 2, low: 1 };
            return demandOrder[b.demand_level] - demandOrder[a.demand_level];
          });
        } else if (sortBy === 'days') {
          sorted.sort((a, b) => b.days_out_of_stock - a.days_out_of_stock);
        }

        setMetrics(sorted);
      } catch (error) {
        console.error('Ошибка загрузки метрик:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchMetrics();
  }, [selectedCategory, minDays, sortBy]);

  const highPriorityCount = metrics.filter(m => m.priority_score >= 70).length;
  const highDemandCount = metrics.filter(m => m.demand_level === 'high').length;
  const criticalCount = metrics.filter(m => m.days_out_of_stock > 30).length;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8 fade-in">
        <h1 className="text-4xl font-bold bg-gradient-to-r from-[#005BFF] to-[#00D9FF] bg-clip-text text-transparent">
          Динамическое ценообразование
        </h1>
        <p className="mt-3 text-lg text-gray-600">
          Метрики для принятия решений по ценообразованию на основе спроса и остатков
        </p>
      </div>

      {/* Статистика */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-3 mb-8">
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <AlertTriangle className="h-6 w-6 text-red-400" />
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Высокий приоритет</dt>
                  <dd className="text-2xl font-semibold text-gray-900">{highPriorityCount}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <TrendingUp className="h-6 w-6 text-blue-400" />
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Высокий спрос</dt>
                  <dd className="text-2xl font-semibold text-gray-900">{highDemandCount}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <Package className="h-6 w-6 text-yellow-400" />
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Критичные остатки</dt>
                  <dd className="text-2xl font-semibold text-gray-900">{criticalCount}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Фильтры */}
      <div className="card p-6 mb-6 bg-gradient-to-br from-white to-purple-50/30">
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
              Мин. дней без остатка
            </label>
            <input
              type="number"
              value={minDays}
              onChange={(e) => setMinDays(e.target.value)}
              min="0"
              className="w-full rounded-xl border-2 border-gray-200 shadow-sm focus:border-[#005BFF] focus:ring-2 focus:ring-[#005BFF]/20 transition-all"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Сортировка
            </label>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as any)}
              className="w-full rounded-xl border-2 border-gray-200 shadow-sm focus:border-[#005BFF] focus:ring-2 focus:ring-[#005BFF]/20 transition-all"
            >
              <option value="priority">По приоритетности</option>
              <option value="demand">По уровню спроса</option>
              <option value="days">По дням без остатка</option>
            </select>
          </div>
        </div>
      </div>

      {/* Метрики */}
      <div className="card overflow-hidden">
        <div className="px-6 py-5 border-b border-gray-200 bg-gradient-to-r from-[#005BFF]/10 to-[#00D9FF]/10">
          <div className="flex items-center">
            <div className="bg-gradient-to-r from-[#005BFF] to-[#00D9FF] p-2 rounded-lg mr-3">
              <DollarSign className="h-5 w-5 text-white" />
            </div>
            <h2 className="text-xl font-bold text-gray-900">Метрики ценообразования</h2>
            <span className="ml-3 px-3 py-1 bg-white rounded-full text-sm font-semibold text-[#005BFF]">
              {metrics.length} товаров
            </span>
          </div>
        </div>
        <div className="p-6">
          {loading ? (
            <div className="animate-pulse space-y-4">
              {[1, 2, 3, 4, 5].map((i) => (
                <div key={i} className="h-32 bg-gray-200 rounded" />
              ))}
            </div>
          ) : metrics.length === 0 ? (
            <p className="text-gray-500 text-center py-8">Нет данных для отображения</p>
          ) : (
            <div className="space-y-4">
              {metrics.map((metric) => (
                <div
                  key={metric.product_id}
                  className={`border rounded-lg p-5 hover:shadow-md transition-shadow ${
                    metric.priority_score >= 70
                      ? 'border-red-200 bg-red-50'
                      : metric.priority_score >= 40
                      ? 'border-yellow-200 bg-yellow-50'
                      : 'border-gray-200 bg-white'
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h3 className="text-base font-medium text-gray-900 mb-2">
                        {metric.product_name}
                      </h3>
                      <div className="grid grid-cols-2 gap-4 text-sm text-gray-600 mb-3">
                        <div>
                          <span className="font-medium">Категория:</span> {metric.category_level_1 || 'Не указана'}
                        </div>
                        <div>
                          <span className="font-medium">Бренд:</span> {metric.brand || 'Не указан'}
                        </div>
                        <div>
                          <span className="font-medium">Добавлений в избранное:</span>{' '}
                          {metric.favorites_count.toLocaleString()}
                        </div>
                        <div>
                          <span className="font-medium">Дней без остатка:</span> {metric.days_out_of_stock}
                        </div>
                      </div>
                      <div className="mt-3 p-3 bg-white rounded border border-gray-200">
                        <p className="text-sm text-gray-700">
                          <span className="font-medium">Рекомендация:</span> {metric.recommendation}
                        </p>
                      </div>
                    </div>
                    <div className="ml-4">
                      <PriorityBadge score={metric.priority_score} demandLevel={metric.demand_level} />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

