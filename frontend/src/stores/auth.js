// frontend/src/stores/auth.js
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import apiClient from '../api/client';

export const useAuthStore = defineStore('auth', () => {
  const user = ref(JSON.parse(localStorage.getItem('user')) || null);
  const accessToken = ref(localStorage.getItem('access_token') || null);
  const refreshToken = ref(localStorage.getItem('refresh_token') || null);

  const isAuthenticated = computed(() => !!accessToken.value);
  const isAdmin = computed(() => user.value?.is_admin || false);

  async function login(email, password) {
    const { data } = await apiClient.post('/auth/login', { email, password });
    setSession(data);
  }

  async function register(email, password, is_admin = false) {
    const { data } = await apiClient.post('/auth/register', { email, password, is_admin });
    setSession(data);
  }

  function setSession(data) {
    user.value = data.user;
    accessToken.value = data.access_token;
    refreshToken.value = data.refresh_token;
    
    localStorage.setItem('user', JSON.stringify(data.user));
    localStorage.setItem('access_token', data.access_token);
    localStorage.setItem('refresh_token', data.refresh_token);
  }

  function logout() {
    user.value = null;
    accessToken.value = null;
    refreshToken.value = null;
    localStorage.removeItem('user');
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  }

  return { user, accessToken, refreshToken, isAuthenticated, isAdmin, login, register, logout };
});