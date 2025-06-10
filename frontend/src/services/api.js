import axios from "axios";

const api = axios.create({
  baseURL: process.env.VUE_APP_API_URL || "/api/",
  timeout: 5000,
  withCredentials: true,
  headers: {
    "Content-Type": "application/json",
    Accept: "application/json",
  },
});

// No token injection needed; credentials (cookies) are sent automatically

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
