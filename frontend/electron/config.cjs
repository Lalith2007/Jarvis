const API_BASE_URL = "http://127.0.0.1:8000";

const FrontendConfig = {
  API_BASE: `${API_BASE_URL}/api`,
  API_DASHBOARD: `${API_BASE_URL}/api/dashboard`,
  WS_PLATFORM: `ws://127.0.0.1:8000/ws/platform`,
  WS_RUNTIME: `ws://127.0.0.1:8000/ws/runtime`,
  FRONTEND_DEV_URL: "http://127.0.0.1:5173",
  FRONTEND_DEV_DASHBOARD: "http://127.0.0.1:5173/dashboard",
  VITE_DEV_SERVER: "http://127.0.0.1:5173"
};

module.exports = { FrontendConfig };
