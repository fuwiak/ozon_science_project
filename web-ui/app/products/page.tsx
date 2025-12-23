'use client';

import { useState } from 'react';
import { useProducts, useCategories, useBrands } from '@/lib/hooks/use-api';
import ProductTable from '@/components/ProductTable';
import { Search, Filter } from 'lucide-react';

export default function ProductsPage() {
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(50);
  
  // Фильтры
  const [selectedCategory, setSelectedCategory] = useState<string>('');
  const [selectedBrand, setSelectedBrand] = useState<string>('');
  const [minFavorites, setMinFavorites] = useState<string>('');

  // Используем кэшированные данные
  const { data: productsData, isLoading: productsLoading } = useProducts({
    page,
    page_size: pageSize,
    category_level_1: selectedCategory || undefined,
    brand: selectedBrand || undefined,
    min_favorites_count: minFavorites ? parseInt(minFavorites) : undefined,
  });

  const { data: categories = [] } = useCategories();
  const { data: brands = [] } = useBrands(selectedCategory || undefined);

  const products = productsData?.products || [];
  const total = productsData?.total || 0;
  const loading = productsLoading;

  const totalPages = Math.ceil(total / pageSize);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8 fade-in">
        <h1 className="text-4xl font-bold bg-gradient-to-r from-[#005BFF] to-[#00D9FF] bg-clip-text text-transparent">
          Товары
        </h1>
        <p className="mt-3 text-lg text-gray-600">
          Поиск и фильтрация товаров по различным критериям
        </p>
      </div>

      {/* Фильтры */}
      <div className="bg-white shadow rounded-lg p-6 mb-6">
        <div className="flex items-center mb-4">
          <Filter className="h-5 w-5 text-gray-400 mr-2" />
          <h2 className="text-lg font-medium text-gray-900">Фильтры</h2>
        </div>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Категория
            </label>
            <select
              value={selectedCategory}
              onChange={(e) => {
                setSelectedCategory(e.target.value);
                setSelectedBrand('');
                setPage(1);
              }}
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
              Бренд
            </label>
            <select
              value={selectedBrand}
              onChange={(e) => {
                setSelectedBrand(e.target.value);
                setPage(1);
              }}
              className="w-full rounded-xl border-2 border-gray-200 shadow-sm focus:border-[#005BFF] focus:ring-2 focus:ring-[#005BFF]/20 transition-all"
              disabled={!selectedCategory}
            >
              <option value="">Все бренды</option>
              {brands.map((brand) => (
                <option key={brand} value={brand}>
                  {brand}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Мин. добавлений в избранное
            </label>
            <input
              type="number"
              value={minFavorites}
              onChange={(e) => {
                setMinFavorites(e.target.value);
                setPage(1);
              }}
              placeholder="0"
              className="w-full rounded-xl border-2 border-gray-200 shadow-sm focus:border-[#005BFF] focus:ring-2 focus:ring-[#005BFF]/20 transition-all"
            />
          </div>
        </div>
      </div>

      {/* Таблица товаров */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-4">
          <p className="text-sm text-gray-600">
            Найдено товаров: <span className="font-semibold">{total}</span>
          </p>
          <div className="flex items-center space-x-2">
            <label className="text-sm text-gray-600">Размер страницы:</label>
            <select
              value={pageSize}
              onChange={(e) => {
                setPageSize(parseInt(e.target.value));
                setPage(1);
              }}
              className="rounded-xl border-2 border-gray-200 shadow-sm focus:border-[#005BFF] focus:ring-2 focus:ring-[#005BFF]/20 transition-all"
            >
              <option value="25">25</option>
              <option value="50">50</option>
              <option value="100">100</option>
            </select>
          </div>
        </div>
        <ProductTable products={products} isLoading={loading} />
      </div>

      {/* Пагинация */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between bg-white px-4 py-3 border border-gray-200 rounded-lg">
          <div className="flex-1 flex justify-between sm:hidden">
            <button
              onClick={() => setPage(Math.max(1, page - 1))}
              disabled={page === 1}
              className="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
            >
              Назад
            </button>
            <button
              onClick={() => setPage(Math.min(totalPages, page + 1))}
              disabled={page === totalPages}
              className="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
            >
              Вперед
            </button>
          </div>
          <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
            <div>
              <p className="text-sm text-gray-700">
                Страница <span className="font-medium">{page}</span> из{' '}
                <span className="font-medium">{totalPages}</span>
              </p>
            </div>
            <div>
              <nav className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px" aria-label="Pagination">
                <button
                  onClick={() => setPage(Math.max(1, page - 1))}
                  disabled={page === 1}
                  className="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50"
                >
                  Назад
                </button>
                {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                  let pageNum;
                  if (totalPages <= 5) {
                    pageNum = i + 1;
                  } else if (page <= 3) {
                    pageNum = i + 1;
                  } else if (page >= totalPages - 2) {
                    pageNum = totalPages - 4 + i;
                  } else {
                    pageNum = page - 2 + i;
                  }
                  return (
                    <button
                      key={pageNum}
                      onClick={() => setPage(pageNum)}
                      className={`relative inline-flex items-center px-4 py-2 border text-sm font-medium ${
                        page === pageNum
                          ? 'z-10 bg-blue-50 border-blue-500 text-blue-600'
                          : 'bg-white border-gray-300 text-gray-500 hover:bg-gray-50'
                      }`}
                    >
                      {pageNum}
                    </button>
                  );
                })}
                <button
                  onClick={() => setPage(Math.min(totalPages, page + 1))}
                  disabled={page === totalPages}
                  className="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50"
                >
                  Вперед
                </button>
              </nav>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

