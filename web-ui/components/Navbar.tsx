'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useQueryClient } from '@tanstack/react-query';
import { queryKeys } from '@/lib/hooks/use-api';
import { api } from '@/lib/api';
import { TrendingUp, Package, BarChart3, DollarSign, Home, Zap, Database } from 'lucide-react';

const navItems = [
  { href: '/', label: 'Главная', icon: Home },
  { href: '/products', label: 'Товары', icon: Package },
  { href: '/analytics', label: 'Аналитика', icon: BarChart3 },
  { href: '/pricing', label: 'Ценообразование', icon: DollarSign },
  { href: '/integrations', label: 'Интеграции', icon: Zap },
  { href: '/cache', label: 'Кэш', icon: Database },
];

export default function Navbar() {
  const pathname = usePathname();
  const queryClient = useQueryClient();

  // Prefetch данных при наведении на ссылку
  const handleMouseEnter = (href: string) => {
    if (href === '/') {
      // Prefetch дашборда
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
    } else if (href === '/products') {
      queryClient.prefetchQuery({
        queryKey: queryKeys.products({ page: 1, page_size: 50 }),
        queryFn: () => api.getProducts({ page: 1, page_size: 50 }),
      });
      queryClient.prefetchQuery({
        queryKey: queryKeys.categories(),
        queryFn: () => api.getCategories(),
      });
    } else if (href === '/analytics') {
      queryClient.prefetchQuery({
        queryKey: queryKeys.topProducts({ limit: 20 }),
        queryFn: () => api.getTopProducts({ limit: 20 }),
      });
      queryClient.prefetchQuery({
        queryKey: queryKeys.demandTrends({ group_by: 'category' }),
        queryFn: () => api.getDemandTrends({ group_by: 'category' }),
      });
    }
  };

  return (
    <nav className="bg-gradient-to-r from-[#005BFF] to-[#00D9FF] shadow-xl border-b-4 border-[#0047CC]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-20">
          <div className="flex">
            <div className="flex-shrink-0 flex items-center">
              <div className="bg-white rounded-xl p-2 shadow-lg">
                <TrendingUp className="h-8 w-8 text-[#005BFF]" />
              </div>
              <span className="ml-3 text-2xl font-bold text-white drop-shadow-lg">Dynamic Pricing 1299$</span>
            </div>
            <div className="hidden sm:ml-8 sm:flex sm:space-x-2">
              {navItems.map((item) => {
                const Icon = item.icon;
                const isActive = pathname === item.href;
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    onMouseEnter={() => handleMouseEnter(item.href)}
                    className={`inline-flex items-center px-4 py-2 rounded-xl text-sm font-semibold transition-all duration-200 ${
                      isActive
                        ? 'bg-white text-[#005BFF] shadow-lg transform scale-105'
                        : 'text-white/90 hover:bg-white/20 hover:text-white'
                    }`}
                  >
                    <Icon className="h-5 w-5 mr-2" />
                    {item.label}
                  </Link>
                );
              })}
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
}
