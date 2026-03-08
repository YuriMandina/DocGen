// frontend/src/services/api.js
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://127.0.0.1:8000',
});

// Interceptador de Requisição: Injeta o Token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('@DocGen:token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Interceptador de Resposta: Trata token expirado/inválido
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // Se der 401, limpa os dados e joga pro login
      localStorage.removeItem('@DocGen:token');
      localStorage.removeItem('@DocGen:user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;