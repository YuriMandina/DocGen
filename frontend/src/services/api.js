// frontend/src/services/api.js
import axios from 'axios';

// Cria uma instância do Axios apontando para o nosso backend Python
const api = axios.create({
  baseURL: 'http://127.0.0.1:8000',
});

export default api;