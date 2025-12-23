import { useQuery, useQueryClient, useInfiniteQuery } from '@tanstack/react-query';
import { api, PricingMetric, OutOfStockProduct, DemandMetrics } from '@/lib/api';

// Ключи для кэша
export const queryKeys = {
  pricingMetrics: (params?: any) => ['pricing-metrics', params],
  outOfStock: (params?: any) => ['out-of-stock', params],
  topProducts: (params?: any) => ['top-products', params],
  products: (params?: any) => ['products', params],
  categories: () => ['categories'],
  brands: (category?: string) => ['brands', category],
  cacheStats: () => ['cache-stats'],
  cacheProducts: (params?: any) => ['cache-products', params],
  status: () => ['status'],
  demandTrends: (params?: any) => ['demand-trends', params],
  timeSeries: (params?: any) => ['time-series', params],
};

// Хуки для дашборда
export function usePricingMetrics(params?: { min_days_out_of_stock?: number }) {
  return useQuery({
    queryKey: queryKeys.pricingMetrics(params),
    queryFn: () => api.getPricingMetrics(params),
    staleTime: 2 * 60 * 1000, // 2 минуты
    placeholderData: { metrics: [], total: 0 }, // Мгновенное отображение
  });
}

export function useOutOfStockProducts(params?: { min_days?: number }) {
  return useQuery({
    queryKey: queryKeys.outOfStock(params),
    queryFn: () => api.getOutOfStockProducts(params),
    staleTime: 2 * 60 * 1000,
    placeholderData: [],
  });
}

export function useTopProducts(params?: { 
  limit?: number;
  category?: string;
  brand?: string;
  period_start?: string;
  period_end?: string;
}) {
  return useQuery({
    queryKey: queryKeys.topProducts(params),
    queryFn: () => api.getTopProducts(params),
    staleTime: 2 * 60 * 1000,
    placeholderData: [],
  });
}

export function useStatus() {
  return useQuery({
    queryKey: queryKeys.status(),
    queryFn: () => api.getStatus(),
    refetchInterval: 5000, // Обновлять каждые 5 секунд
    staleTime: 1000,
  });
}

// Хуки для страницы товаров
export function useProducts(params?: {
  page?: number;
  page_size?: number;
  category_level_1?: string;
  brand?: string;
  min_favorites_count?: number;
}) {
  return useQuery({
    queryKey: queryKeys.products(params),
    queryFn: () => api.getProducts(params),
    staleTime: 3 * 60 * 1000,
    placeholderData: { products: [], total: 0, page: 1, page_size: 50, total_pages: 0 },
  });
}

export function useCategories() {
  return useQuery({
    queryKey: queryKeys.categories(),
    queryFn: () => api.getCategories(),
    staleTime: 10 * 60 * 1000, // Категории редко меняются
  });
}

export function useBrands(category?: string) {
  return useQuery({
    queryKey: queryKeys.brands(category),
    queryFn: () => api.getBrands(category),
    staleTime: 10 * 60 * 1000,
    enabled: true, // Всегда загружать
  });
}

// Хуки для аналитики
export function useDemandTrends(params?: {
  category?: string;
  brand?: string;
  group_by?: 'category' | 'brand' | 'period';
}) {
  return useQuery({
    queryKey: queryKeys.demandTrends(params),
    queryFn: () => api.getDemandTrends(params),
    staleTime: 2 * 60 * 1000,
    placeholderData: [],
  });
}

export function useTimeSeries(params?: {
  category?: string;
  brand?: string;
  group_by?: 'category' | 'brand';
  period?: 'day' | 'week' | 'month';
}) {
  return useQuery({
    queryKey: queryKeys.timeSeries(params),
    queryFn: () => api.getTimeSeries(params),
    staleTime: 2 * 60 * 1000,
    placeholderData: { data: [], group_by: null },
  });
}

// Хуки для кэша
export function useCacheStats() {
  return useQuery({
    queryKey: queryKeys.cacheStats(),
    queryFn: async () => {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/cache/stats`);
      if (!response.ok) throw new Error('Failed to fetch cache stats');
      return response.json();
    },
    staleTime: 1 * 60 * 1000,
  });
}

export function useCacheProducts(params?: { 
  page?: number; 
  page_size?: number;
  search?: string; 
  category?: string; 
  brand?: string;
}) {
  return useQuery({
    queryKey: queryKeys.cacheProducts(params),
    queryFn: async () => {
      const searchParams = new URLSearchParams({
        page: (params?.page || 1).toString(),
        page_size: (params?.page_size || 20).toString(),
      });
      if (params?.search) searchParams.append('search', params.search);
      if (params?.category) searchParams.append('category', params.category);
      if (params?.brand) searchParams.append('brand', params.brand);

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/cache/products?${searchParams}`
      );
      if (!response.ok) throw new Error('Failed to fetch cache products');
      return response.json();
    },
    staleTime: 5 * 60 * 1000,
    placeholderData: { products: [], total: 0, page: 1, page_size: 20, total_pages: 0 },
  });
}

export function useCacheProductsInfinite(params?: { search?: string; category?: string; brand?: string }) {
  return useInfiniteQuery({
    queryKey: queryKeys.cacheProducts(params),
    queryFn: async ({ pageParam = 1 }) => {
      // Первая страница - 20 товаров, остальные - по 5
      const pageSize = pageParam === 1 ? '20' : '5';
      const searchParams = new URLSearchParams({
        page: pageParam.toString(),
        page_size: pageSize,
      });
      if (params?.search) searchParams.append('search', params.search);
      if (params?.category) searchParams.append('category', params.category);
      if (params?.brand) searchParams.append('brand', params.brand);

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/cache/products?${searchParams}`
      );
      if (!response.ok) throw new Error('Failed to fetch cache products');
      return response.json();
    },
    getNextPageParam: (lastPage) => {
      if (lastPage.page < lastPage.total_pages) {
        return lastPage.page + 1;
      }
      return undefined;
    },
    initialPageParam: 1,
    staleTime: 5 * 60 * 1000,
    // Первая страница загружается сразу при монтировании
    refetchOnMount: false,
    refetchOnWindowFocus: false,
    // Не загружать следующую страницу автоматически
    getPreviousPageParam: undefined,
  });
}

// Prefetch функции для предзагрузки
export function usePrefetchDashboard() {
  const queryClient = useQueryClient();
  
  return {
    prefetch: () => {
      queryClient.prefetchQuery({
        queryKey: queryKeys.pricingMetrics({ min_days_out_of_stock: 15 }),
        queryFn: () => api.getPricingMetrics({ min_days_out_of_stock: 15 }),
      });
      queryClient.prefetchQuery({
        queryKey: queryKeys.outOfStock({ min_days: 15 }),
        queryFn: () => api.getOutOfStockProducts({ min_days: 15 }),
      });
      queryClient.prefetchQuery({
        queryKey: queryKeys.topProducts({ limit: 5 }),
        queryFn: () => api.getTopProducts({ limit: 5 }),
      });
    },
  };
}

