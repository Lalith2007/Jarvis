import { apiClient } from './client';

export const getAthenaStatus = async () => {
  const { data } = await apiClient.get('/athena/status');
  return data;
};

export const getPlannerStatus = async () => {
  const { data } = await apiClient.get('/planner/status');
  return data;
};

export const getExecutorStatus = async () => {
  const { data } = await apiClient.get('/executor/status');
  return data;
};

export const getMemoryStatus = async () => {
  const { data } = await apiClient.get('/memory/status');
  return data;
};
