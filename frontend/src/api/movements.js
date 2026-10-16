import apiClient from './client';

export default {
  list(params = {}) {
    return apiClient.get('/stock-movements', { params });
  },
  get(id) {
    return apiClient.get(`/stock-movements/${id}`);
  },
  create(payload) {
    return apiClient.post('/stock-movements', payload);
  }
};