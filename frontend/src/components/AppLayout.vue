<script setup>
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';

const router = useRouter();
const authStore = useAuthStore();

function handleLogout() {
  authStore.logout();
  router.push('/login');
}
</script>

<template>
  <div class="min-h-screen bg-gray-100">
    <nav class="bg-white shadow-sm">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
          <div class="flex items-center space-x-8">
            <router-link to="/" class="text-xl font-bold text-indigo-600">StockPulse</router-link>
            <div class="flex items-center space-x-4">
              <router-link to="/" exact-active-class="text-indigo-600 font-semibold"
                           class="text-sm font-medium text-gray-700 hover:text-indigo-600">
                Dashboard
              </router-link>
              <router-link to="/products" active-class="text-indigo-600 font-semibold"
                           class="text-sm font-medium text-gray-700 hover:text-indigo-600">
                Products
              </router-link>
              <router-link to="/categories" active-class="text-indigo-600 font-semibold"
                           class="text-sm font-medium text-gray-700 hover:text-indigo-600">
                Categories
              </router-link>
              <router-link to="/movements" active-class="text-indigo-600 font-semibold"
                           class="text-sm font-medium text-gray-700 hover:text-indigo-600">
                Movements
              </router-link>
            </div>
          </div>
          <div class="flex items-center space-x-4">
            <span class="text-gray-700 text-sm">{{ authStore.user?.email }}</span>
            <button @click="handleLogout" class="text-gray-500 hover:text-red-600 text-sm font-medium">
              Logout
            </button>
          </div>
        </div>
      </div>
    </nav>
    <main class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
      <router-view />
    </main>
  </div>
</template>