import axios from "axios";
import store from "@/store";

const api = axios.create({
  baseURL: process.env.VUE_APP_API_URL || "/api/",
  timeout: 5000,
  withCredentials: true,
  headers: {
    "Content-Type": "application/json",
    Accept: "application/json",
  },
});

// Include access token-ul in toate requesturile
api.interceptors.request.use((config) => {
  const token = store.state.auth.token;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Interceptor pentru gestionarea raspunsurilor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

export default api;
