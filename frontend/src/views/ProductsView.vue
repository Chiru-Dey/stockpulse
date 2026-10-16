<script setup>
import { ref, onMounted } from 'vue';
import productsApi from '../api/products';
import categoriesApi from '../api/categories';
import ProductFormModal from '../components/ProductFormModal.vue';
import { useAuthStore } from '../stores/auth';
import { PencilSquareIcon, TrashIcon, PlusIcon } from '@heroicons/vue/24/outline';

const authStore = useAuthStore();

const products = ref([]);
const categories = ref([]);
const loading = ref(true);
const error = ref('');

const search = ref('');
const categoryId = ref('');
const stockStatus = ref('');
const page = ref(1);
const perPage = ref(10);
const total = ref(0);
const pages = ref(0);

const showModal = ref(false);
const editingProduct = ref(null);

async function fetchProducts() {
  loading.value = true;
  error.value = '';
  try {
    const params = { page: page.value, per_page: perPage.value };
    if (search.value) params.search = search.value;
    if (categoryId.value) params.category_id = categoryId.value;
    if (stockStatus.value) params.stock_status = stockStatus.value;
    const response = await productsApi.list(params);
    products.value = response.data.products;
    total.value = response.data.total;
    pages.value = response.data.pages;
  } catch (err) {
    error.value = err.response?.data?.error || 'Failed to load products.';
  } finally {
    loading.value = false;
  }
}

async function fetchCategories() {
  try {
    const response = await categoriesApi.list();
    categories.value = response.data.categories;
  } catch (err) {
    console.error('Failed to load categories', err);
  }
}

let searchTimeout = null;
function onSearchInput() {
  clearTimeout(searchTimeout);
  searchTimeout = setTimeout(() => {
    page.value = 1;
    fetchProducts();
  }, 300);
}

function applyFilters() {
  page.value = 1;
  fetchProducts();
}

function openCreateModal() {
  editingProduct.value = null;
  showModal.value = true;
}

function openEditModal(product) {
  editingProduct.value = product;
  showModal.value = true;
}

async function handleDelete(product) {
  if (!confirm(`Delete product "${product.name}"? Its stock movement history will also be deleted.`)) {
    return;
  }
  try {
    await productsApi.remove(product.id);
    fetchProducts();
  } catch (err) {
    alert(err.response?.data?.error || 'Failed to delete product.');
  }
}

function onSaved() {
  showModal.value = false;
  fetchProducts();
}

function prevPage() {
  if (page.value > 1) {
    page.value -= 1;
    fetchProducts();
  }
}

function nextPage() {
  if (page.value < pages.value) {
    page.value += 1;
    fetchProducts();
  }
}

const statusBadgeClass = (status) => {
  if (status === 'ok') return 'bg-green-100 text-green-800';
  if (status === 'low') return 'bg-yellow-100 text-yellow-800';
  return 'bg-red-100 text-red-800';
};

const categoryName = (id) => {
  const cat = categories.value.find((c) => c.id === id);
  return cat ? cat.name : '—';
};

onMounted(() => {
  fetchCategories();
  fetchProducts();
});
</script>

<template>
  <div class="p-6">
    <div class="mb-6 flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Products</h1>
        <p class="mt-1 text-sm text-gray-600">Manage your inventory items and stock levels.</p>
      </div>
      <button v-if="authStore.isAdmin" @click="openCreateModal"
              class="inline-flex items-center px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-md hover:bg-indigo-700">
        <PlusIcon class="h-5 w-5 mr-2" />
        New Product
      </button>
    </div>

    <!-- Filters -->
    <div class="mb-6 grid grid-cols-1 gap-4 sm:grid-cols-3">
      <input v-model="search" @input="onSearchInput" type="text" placeholder="Search by name or SKU..."
             class="rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500" />
      <select v-model="categoryId" @change="applyFilters"
              class="rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500">
        <option value="">All categories</option>
        <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
      </select>
      <select v-model="stockStatus" @change="applyFilters"
              class="rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500">
        <option value="">All stock statuses</option>
        <option value="ok">In stock</option>
        <option value="low">Low stock</option>
        <option value="out">Out of stock</option>
      </select>
    </div>

    <div v-if="error" class="mb-4 bg-red-50 border border-red-200 text-red-600 text-sm p-3 rounded-md">
      {{ error }}
    </div>

    <!-- Table -->
    <div class="overflow-hidden shadow ring-1 ring-black ring-opacity-5 sm:rounded-lg bg-white">
      <table class="min-w-full divide-y divide-gray-300">
        <thead class="bg-gray-50">
          <tr>
            <th class="py-3.5 pl-4 pr-3 text-left text-sm font-semibold text-gray-900 sm:pl-6">Name</th>
            <th class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">SKU</th>
            <th class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Category</th>
            <th class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Stock</th>
            <th class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Status</th>
            <th v-if="authStore.isAdmin" class="px-3 py-3.5 text-right text-sm font-semibold text-gray-900">Actions</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-200 bg-white">
          <tr v-if="loading">
            <td :colspan="authStore.isAdmin ? 6 : 5" class="py-8 text-center text-sm text-gray-500">Loading products...</td>
          </tr>
          <tr v-else-if="products.length === 0">
            <td :colspan="authStore.isAdmin ? 6 : 5" class="py-8 text-center text-sm text-gray-500">No products found.</td>
          </tr>
          <tr v-for="product in products" :key="product.id">
            <td class="whitespace-nowrap py-4 pl-4 pr-3 text-sm font-medium text-gray-900 sm:pl-6">{{ product.name }}</td>
            <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-500">{{ product.sku }}</td>
            <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-500">{{ categoryName(product.category_id) }}</td>
            <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-900">{{ product.current_stock }}</td>
            <td class="whitespace-nowrap px-3 py-4 text-sm">
              <span :class="['inline-flex rounded-full px-2 text-xs font-semibold leading-5', statusBadgeClass(product.stock_status)]">
                {{ product.stock_status.toUpperCase() }}
              </span>
            </td>
            <td v-if="authStore.isAdmin" class="whitespace-nowrap px-3 py-4 text-right text-sm">
              <button @click="openEditModal(product)" class="text-indigo-600 hover:text-indigo-800 mr-3" title="Edit">
                <PencilSquareIcon class="h-5 w-5 inline" />
              </button>
              <button @click="handleDelete(product)" class="text-red-600 hover:text-red-800" title="Delete">
                <TrashIcon class="h-5 w-5 inline" />
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Pagination -->
    <div class="mt-4 flex items-center justify-between">
      <span class="text-sm text-gray-600">
        Page {{ page }} of {{ pages || 1 }} ({{ total }} products)
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

    <ProductFormModal
      :show="showModal"
      :product="editingProduct"
      :categories="categories"
      @close="showModal = false"
      @saved="onSaved"
    />
  </div>
</template>