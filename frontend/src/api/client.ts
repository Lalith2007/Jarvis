import axios from 'axios';
import { FrontendConfig } from '../../electron/config.cjs';

// Create a generic axios instance for the JARVIS API
export const apiClient = axios.create({
  baseURL: FrontendConfig.API_BASE, // Update this based on where backend runs
  headers: {
    'Content-Type': 'application/json',
  },
});

// Optionally add interceptors here
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);
