import apiClient from './client';

export default {
  list(params = {}) {
    return apiClient.get('/products', { params });
  },
  get(id) {
    return apiClient.get(`/products/${id}`);
  },
  create(payload) {
    return apiClient.post('/products', payload);
  },
  update(id, payload) {
    return apiClient.patch(`/products/${id}`, payload);
  },
  remove(id) {
    return apiClient.delete(`/products/${id}`);
  }
};