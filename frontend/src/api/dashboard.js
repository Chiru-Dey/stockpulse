import apiClient from './client';

export default {
  getSummary() {
    return apiClient.get('/dashboard/summary');
  }
};