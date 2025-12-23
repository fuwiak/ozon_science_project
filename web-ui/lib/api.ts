import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 15000, // 15 секунд таймаут
});

// Перехватчик для обработки ошибок
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const errorMessage = error?.message || error?.response?.data?.detail || 'Unknown error';
    console.error('API Error:', errorMessage);
    if (error?.code === 'ECONNABORTED' || error?.message?.includes('timeout')) {
      console.error('Request timeout');
    }
    return Promise.reject(error);
  }
);

// Типы данных
export interface Product {
  id: string;
  name: string;
  brand: string | null;
  link: string | null;
  category_level_1: string | null;
  category_level_2: string | null;
  category_level_3: string | null;
  category_level_4: string | null;
  favorites_count: number;
  last_in_stock: string | null;
  period_start: string | null;
  period_end: string | null;
  days_out_of_stock: number | null;
}

export interface ProductListResponse {
  products: Product[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface DemandMetrics {
  product_id: string;
  product_name: string;
  brand: string | null;
  category_level_1: string | null;
  favorites_count: number;
  period_start: string | null;
  period_end: string | null;
  rank: number | null;
}

export interface OutOfStockProduct {
  product_id: string;
  product_name: string;
  brand: string | null;
  category_level_1: string | null;
  last_in_stock: string;
  days_out_of_stock: number;
  favorites_count: number;
  priority_score: number;
}

export interface PricingMetric {
  product_id: string;
  product_name: string;
  brand: string | null;
  category_level_1: string | null;
  demand_level: 'high' | 'medium' | 'low';
  favorites_count: number;
  days_out_of_stock: number;
  priority_score: number;
  recommendation: string;
}

export interface PricingMetricsResponse {
  metrics: PricingMetric[];
  total: number;
}

export interface TimeSeriesPoint {
  date: string;
  value: number;
  category?: string | null;
  brand?: string | null;
}

export interface TimeSeriesResponse {
  data: TimeSeriesPoint[];
  group_by: string | null;
}

export interface TrendData {
  period: string;
  category: string | null;
  brand: string | null;
  total_favorites: number;
  unique_products: number;
  avg_favorites_per_product: number;
}

// API функции
export const api = {
  // Товары
  getProducts: async (params?: {
    category_level_1?: string;
    category_level_2?: string;
    category_level_3?: string;
    category_level_4?: string;
    brand?: string;
    min_favorites_count?: number;
    period_start?: string;
    period_end?: string;
    out_of_stock_days?: number;
    page?: number;
    page_size?: number;
  }): Promise<ProductListResponse> => {
    const response = await apiClient.get<ProductListResponse>('/api/products', { params });
    return response.data;
  },

  getProduct: async (id: string): Promise<Product> => {
    const response = await apiClient.get<Product>(`/api/products/${id}`);
    return response.data;
  },

  getCategories: async (): Promise<string[]> => {
    const response = await apiClient.get<string[]>('/api/products/categories/list');
    return response.data;
  },

  getBrands: async (category?: string): Promise<string[]> => {
    const response = await apiClient.get<string[]>('/api/products/brands/list', {
      params: { category },
    });
    return response.data;
  },

  // Аналитика
  getTopProducts: async (params?: {
    limit?: number;
    category?: string;
    brand?: string;
    period_start?: string;
    period_end?: string;
  }): Promise<DemandMetrics[]> => {
    const response = await apiClient.get<DemandMetrics[]>('/api/analytics/demand/top', { params });
    return response.data;
  },

  getDemandTrends: async (params?: {
    category?: string;
    brand?: string;
    group_by?: 'category' | 'brand' | 'period';
  }): Promise<TrendData[]> => {
    const response = await apiClient.get<TrendData[]>('/api/analytics/demand/trends', { params });
    return response.data;
  },

  getOutOfStockProducts: async (params?: {
    min_days?: number;
    category?: string;
    brand?: string;
    period_start?: string;
    period_end?: string;
  }): Promise<OutOfStockProduct[]> => {
    const response = await apiClient.get<OutOfStockProduct[]>('/api/analytics/stock/out-of-stock', { params });
    return response.data;
  },

  getTimeSeries: async (params?: {
    category?: string;
    brand?: string;
    group_by?: 'category' | 'brand';
    period?: 'day' | 'week' | 'month';
  }): Promise<TimeSeriesResponse> => {
    const response = await apiClient.get<TimeSeriesResponse>('/api/analytics/timeseries', { params });
    return response.data;
  },

  getPricingMetrics: async (params?: {
    category?: string;
    brand?: string;
    min_days_out_of_stock?: number;
  }): Promise<PricingMetricsResponse> => {
    const response = await apiClient.get<PricingMetricsResponse>('/api/analytics/pricing-metrics', { params });
    return response.data;
  },

  // Статус загрузки данных
  getStatus: async (): Promise<{
    cache_ready: boolean;
    loading: boolean;
    files_loaded: number;
    total_products: number;
    using_mock_data?: boolean;
    message?: string;
  }> => {
    const response = await apiClient.get('/api/status');
    return response.data;
  },

  // n8n интеграция
  getN8NWorkflows: async (url?: string, apiKey?: string): Promise<{
    workflows: Array<{
      id: string;
      name: string;
      active: boolean;
      nodes: number;
      lastExecuted?: string;
    }>;
    total: number;
  }> => {
    const params: any = {};
    if (url) params.url = url;
    if (apiKey) params.api_key = apiKey;
    const response = await apiClient.get('/api/n8n/workflows', { params });
    return response.data;
  },

  toggleN8NWorkflow: async (workflowId: string, active: boolean, url?: string, apiKey?: string): Promise<{
    success: boolean;
    message: string;
  }> => {
    const params: any = { active };
    if (url) params.url = url;
    if (apiKey) params.api_key = apiKey;
    const response = await apiClient.post(`/api/n8n/workflows/${workflowId}/toggle`, null, { params });
    return response.data;
  },

  testN8NConnection: async (url: string, apiKey: string): Promise<{
    success: boolean;
    message: string;
  }> => {
    const response = await apiClient.post('/api/n8n/test-connection', {
      url,
      api_key: apiKey,
    });
    return response.data;
  },

  // Telegram интеграция
  saveTelegramBotSettings: async (botToken: string, webhookUrl?: string): Promise<{
    success: boolean;
    message: string;
    bot_username?: string;
    webhook_set?: boolean;
  }> => {
    const response = await apiClient.post('/api/telegram/bot/settings', {
      bot_token: botToken,
      webhook_url: webhookUrl,
    });
    return response.data;
  },

  getTelegramBotStatus: async (): Promise<{
    configured: boolean;
    bot_username?: string;
    webhook_url?: string;
    message: string;
  }> => {
    const response = await apiClient.get('/api/telegram/bot/status');
    return response.data;
  },

  sendTelegramMessage: async (chatId: string, message: string): Promise<{
    success: boolean;
    message: string;
  }> => {
    const response = await apiClient.post('/api/telegram/bot/send-message', {
      chat_id: chatId,
      message: message,
    });
    return response.data;
  },

  setTelegramMenu: async (): Promise<{
    success: boolean;
    message: string;
  }> => {
    const response = await apiClient.post('/api/telegram/bot/set-menu');
    return response.data;
  },
};

