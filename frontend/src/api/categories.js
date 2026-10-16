import apiClient from './client';

export default {
  list(params = {}) {
    return apiClient.get('/categories', { params });
  },
  create(payload) {
    return apiClient.post('/categories', payload);
  },
  update(id, payload) {
    return apiClient.patch(`/categories/${id}`, payload);
  },
  remove(id) {
    return apiClient.delete(`/categories/${id}`);
  }
};