import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../api/client';
import { mapDashboardResponse } from '../api/dto';
import type { MappedDashboardSnapshot, RawDashboardResponse } from '../api/dto';

export type { MappedDashboardSnapshot };

export function useDashboardSnapshot() {
  return useQuery<MappedDashboardSnapshot>({
    queryKey: ['dashboard'],
    queryFn: async () => {
      const response = await apiClient.get<RawDashboardResponse>('/dashboard');
      // Map once at the boundary; all consumers receive camelCase
      return mapDashboardResponse(response.data);
    },
    staleTime: Infinity,
    refetchOnWindowFocus: false,
  });
}
