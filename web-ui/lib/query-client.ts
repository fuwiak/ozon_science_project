import { QueryClient } from '@tanstack/react-query';

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 минут - данные считаются свежими
      gcTime: 10 * 60 * 1000, // 10 минут - данные в кэше (было cacheTime)
      refetchOnWindowFocus: false, // Не перезагружать при фокусе окна
      refetchOnMount: false, // Не перезагружать при монтировании, если есть кэш
      retry: 1,
    },
  },
});


