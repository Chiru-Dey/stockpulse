<script setup>
import { ref, onMounted } from 'vue';
import movementsApi from '../api/movements';
import productsApi from '../api/products';
import { PlusIcon } from '@heroicons/vue/24/outline';

const movements = ref([]);
const products = ref([]);
const loading = ref(true);
const error = ref('');

const productId = ref('');
const movementType = ref('');
const dateFrom = ref('');
const dateTo = ref('');
const page = ref(1);
const perPage = ref(10);
const total = ref(0);
const pages = ref(0);

const showModal = ref(false);
const form = ref({ product_id: '', movement_type: 'IN', quantity: 1, note: '' });
const formError = ref('');
const saving = ref(false);

async function fetchMovements() {
  loading.value = true;
  error.value = '';
  try {
    const params = { page: page.value, per_page: perPage.value };
    if (productId.value) params.product_id = productId.value;
    if (movementType.value) params.movement_type = movementType.value;
    if (dateFrom.value) params.date_from = dateFrom.value;
    if (dateTo.value) params.date_to = dateTo.value;
    const response = await movementsApi.list(params);
    movements.value = response.data.movements;
    total.value = response.data.total;
    pages.value = response.data.pages;
  } catch (err) {
    error.value = 'Failed to load stock movements.';
  } finally {
    loading.value = false;
  }
}

async function fetchProducts() {
  try {
    const response = await productsApi.list({ per_page: 100 });
    products.value = response.data.products;
  } catch (err) {
    console.error('Failed to load products', err);
  }
}

function applyFilters() {
  page.value = 1;
  fetchMovements();
}

function clearFilters() {
  productId.value = '';
  movementType.value = '';
  dateFrom.value = '';
  dateTo.value = '';
  page.value = 1;
  fetchMovements();
}

function openModal() {
  form.value = { product_id: '', movement_type: 'IN', quantity: 1, note: '' };
  formError.value = '';
  showModal.value = true;
}

function closeModal() {
  showModal.value = false;
}

async function handleSubmit() {
  formError.value = '';

  if (!form.value.product_id) {
    formError.value = 'Please select a product.';
    return;
  }
  const quantity = parseInt(form.value.quantity, 10);
  if (isNaN(quantity) || quantity < 1) {
    formError.value = 'Quantity must be at least 1.';
    return;
  }

  saving.value = true;
  try {
    await movementsApi.create({
      product_id: parseInt(form.value.product_id, 10),
      movement_type: form.value.movement_type,
      quantity: quantity,
      note: form.value.note.trim() || null
    });
    showModal.value = false;
    page.value = 1;
    await fetchMovements();
    await fetchProducts();
  } catch (err) {
    const data = err.response?.data;
    if (data && data.error === 'Insufficient stock') {
      formError.value = `Insufficient stock (current stock: ${data.current_stock}).`;
    } else {
      formError.value = data?.error || 'Failed to record movement.';
    }
  } finally {
    saving.value = false;
  }
}

function prevPage() {
  if (page.value > 1) {
    page.value -= 1;
    fetchMovements();
  }
}

function nextPage() {
  if (page.value < pages.value) {
    page.value += 1;
    fetchMovements();
  }
}

const formatDate = (dateString) => new Date(dateString).toLocaleString();

onMounted(() => {
  fetchProducts();
  fetchMovements();
});
</script>

<template>
  <div class="p-6">
    <div class="mb-6 flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Stock Movements</h1>
        <p class="mt-1 text-sm text-gray-600">Record and review all stock IN / OUT activity.</p>
      </div>
      <button @click="openModal"
              class="inline-flex items-center px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-md hover:bg-indigo-700">
        <PlusIcon class="h-5 w-5 mr-2" />
        Record Movement
      </button>
    </div>

    <!-- Filters -->
    <div class="mb-6 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-5">
      <div>
        <label class="mb-1 block text-sm font-medium text-gray-700">Product</label>
        <select v-model="productId" @change="applyFilters"
                class="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500">
          <option value="">All products</option>
          <option v-for="p in products" :key="p.id" :value="p.id">{{ p.name }}</option>
        </select>
      </div>
      <div>
        <label class="mb-1 block text-sm font-medium text-gray-700">Movement type</label>
        <select v-model="movementType" @change="applyFilters"
                class="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500">
          <option value="">All types</option>
          <option value="IN">Stock IN</option>
          <option value="OUT">Stock OUT</option>
        </select>
      </div>
      <div>
        <label class="mb-1 block text-sm font-medium text-gray-700">From date</label>
        <input v-model="dateFrom" @change="applyFilters" type="date"
               class="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500" />
      </div>
      <div>
        <label class="mb-1 block text-sm font-medium text-gray-700">To date</label>
        <input v-model="dateTo" @change="applyFilters" type="date"
               class="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500" />
      </div>
      <div class="flex items-end">
        <button @click="clearFilters"
                class="w-full px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50">
          Clear filters
        </button>
      </div>
    </div>

    <div v-if="error" class="mb-4 bg-red-50 border border-red-200 text-red-600 text-sm p-3 rounded-md">
      {{ error }}
    </div>

    <!-- Table -->
    <div class="overflow-hidden shadow ring-1 ring-black ring-opacity-5 sm:rounded-lg bg-white">
      <table class="min-w-full divide-y divide-gray-300">
        <thead class="bg-gray-50">
          <tr>
            <th class="py-3.5 pl-4 pr-3 text-left text-sm font-semibold text-gray-900 sm:pl-6">Date</th>
            <th class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Product</th>
            <th class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Type</th>
            <th class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Quantity</th>
            <th class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Note</th>
            <th class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Recorded By</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-200 bg-white">
          <tr v-if="loading">
            <td colspan="6" class="py-8 text-center text-sm text-gray-500">Loading movements...</td>
          </tr>
          <tr v-else-if="movements.length === 0">
            <td colspan="6" class="py-8 text-center text-sm text-gray-500">No movements found.</td>
          </tr>
          <tr v-for="movement in movements" :key="movement.id">
            <td class="whitespace-nowrap py-4 pl-4 pr-3 text-sm text-gray-500 sm:pl-6">
              {{ formatDate(movement.created_at) }}
            </td>
            <td class="whitespace-nowrap px-3 py-4 text-sm font-medium text-gray-900">
              {{ movement.product_name }}
            </td>
            <td class="whitespace-nowrap px-3 py-4 text-sm">
              <span :class="[
                'inline-flex rounded-full px-2 text-xs font-semibold leading-5',
                movement.movement_type === 'IN' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
              ]">
                {{ movement.movement_type }}
              </span>
            </td>
            <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-900">{{ movement.quantity }}</td>
            <td class="px-3 py-4 text-sm text-gray-500 truncate max-w-xs">{{ movement.note || '-' }}</td>
            <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-500">{{ movement.created_by_email || '-' }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Pagination -->
    <div class="mt-4 flex items-center justify-between">
      <span class="text-sm text-gray-600">
        Page {{ page }} of {{ pages || 1 }} ({{ total }} movements)
      </span>
      <div class="flex gap-2">
        <button @click="prevPage" :disabled="page <= 1"
                class="px-3 py-1.5 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50">
          Previous
        </button>
        <button @click="nextPage" :disabled="page >= pages"
                class="px-3 py-1.5 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50">
          Next
        </button>
      </div>
    </div>

    <!-- Record Movement Modal -->
    <div v-if="showModal" class="fixed inset-0 z-50 overflow-y-auto">
      <div class="fixed inset-0 bg-black bg-opacity-50" @click="closeModal"></div>
      <div class="relative flex min-h-full items-center justify-center p-4">
        <div class="relative w-full max-w-md rounded-lg bg-white shadow-xl">
          <div class="flex items-center justify-between border-b border-gray-200 px-6 py-4">
            <h3 class="text-lg font-semibold text-gray-900">Record Movement</h3>
            <button @click="closeModal" class="text-gray-400 hover:text-gray-600 text-2xl leading-none">&times;</button>
          </div>

          <form @submit.prevent="handleSubmit" class="px-6 py-4 space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Product *</label>
              <select v-model="form.product_id" required
                      class="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500">
                <option value="" disabled>Select a product</option>
                <option v-for="p in products" :key="p.id" :value="p.id">
                  {{ p.name }} ({{ p.sku }}) — stock: {{ p.current_stock }}
                </option>
              </select>
            </div>

            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Type *</label>
                <select v-model="form.movement_type"
                        class="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500">
                  <option value="IN">Stock IN</option>
                  <option value="OUT">Stock OUT</option>
                </select>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Quantity *</label>
                <input v-model="form.quantity" type="number" min="1" required
                       class="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500" />
              </div>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Note</label>
              <input v-model="form.note" type="text" placeholder="e.g. Supplier delivery, sale, damage..."
                     class="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500" />
            </div>

            <div v-if="formError" class="bg-red-50 border border-red-200 text-red-600 text-sm p-3 rounded-md">
              {{ formError }}
            </div>

            <div class="flex justify-end gap-3 pt-2">
              <button type="button" @click="closeModal"
                      class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50">
                Cancel
              </button>
              <button type="submit" :disabled="saving"
                      class="px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-md hover:bg-indigo-700 disabled:opacity-50">
                {{ saving ? 'Saving...' : 'Record' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>