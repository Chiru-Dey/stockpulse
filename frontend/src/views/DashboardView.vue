<script setup>
import { ref, onMounted } from 'vue';
import dashboardApi from '../api/dashboard';
import StatCard from '../components/StatCard.vue';
import MovementTable from '../components/MovementTable.vue';

// Import Heroicons
import { 
  CubeIcon, 
  ArchiveBoxIcon, 
  ExclamationTriangleIcon, 
  XCircleIcon 
} from '@heroicons/vue/24/outline';

const stats = ref(null);
const loading = ref(true);
const error = ref('');

onMounted(async () => {
  try {
    const response = await dashboardApi.getSummary();
    stats.value = response.data;
  } catch (err) {
    error.value = 'Failed to load dashboard data.';
    console.error(err);
  } finally {
    loading.value = false;
  }
});
</script>

<template>
  <div class="p-6">
    <div class="mb-8">
      <h1 class="text-2xl font-bold text-gray-900">Dashboard</h1>
      <p class="mt-1 text-sm text-gray-600">Overview of your inventory health and recent activity.</p>
    </div>

    <div v-if="loading" class="text-center py-12 text-gray-500">
      Loading dashboard data...
    </div>
    
    <div v-else-if="error" class="bg-red-50 border border-red-200 text-red-600 p-4 rounded-md">
      {{ error }}
    </div>

    <div v-else-if="stats">
      <!-- Stats Grid -->
      <dl class="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard 
          title="Total Products" 
          :value="stats.total_products" 
          :icon="CubeIcon" 
          colorClass="text-blue-600 bg-blue-100" 
        />
        <StatCard 
          title="Total Stock Units" 
          :value="stats.total_stock_units" 
          :icon="ArchiveBoxIcon" 
          colorClass="text-indigo-600 bg-indigo-100" 
        />
        <StatCard 
          title="Low Stock Items" 
          :value="stats.low_stock_count" 
          :icon="ExclamationTriangleIcon" 
          colorClass="text-yellow-600 bg-yellow-100" 
        />
        <StatCard 
          title="Out of Stock" 
          :value="stats.out_of_stock_count" 
          :icon="XCircleIcon" 
          colorClass="text-red-600 bg-red-100" 
        />
      </dl>

      <!-- Recent Movements -->
      <div class="mt-12">
        <h2 class="text-lg font-medium text-gray-900 mb-4">Recent Activity</h2>
        <MovementTable :movements="stats.recent_movements" />
      </div>
    </div>
  </div>
</template>