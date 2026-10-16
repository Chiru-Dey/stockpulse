<script setup>
import { ref, onMounted } from 'vue';
import categoriesApi from '../api/categories';
import { useAuthStore } from '../stores/auth';
import { PencilSquareIcon, TrashIcon, PlusIcon } from '@heroicons/vue/24/outline';

const authStore = useAuthStore();

const categories = ref([]);
const loading = ref(true);
const error = ref('');

// Modal state
const showModal = ref(false);
const editingCategory = ref(null);
const form = ref({ name: '', description: '' });
const formError = ref('');
const saving = ref(false);

async function fetchCategories() {
  loading.value = true;
  error.value = '';
  try {
    const response = await categoriesApi.list();
    categories.value = response.data.categories;
  } catch (err) {
    error.value = 'Failed to load categories.';
  } finally {
    loading.value = false;
  }
}

function openCreate() {
  editingCategory.value = null;
  form.value = { name: '', description: '' };
  formError.value = '';
  showModal.value = true;
}

function openEdit(cat) {
  editingCategory.value = cat;
  form.value = { name: cat.name, description: cat.description || '' };
  formError.value = '';
  showModal.value = true;
}

function closeModal() {
  showModal.value = false;
}

async function handleSubmit() {
  formError.value = '';
  if (!form.value.name.trim()) {
    formError.value = 'Name is required.';
    return;
  }

  const payload = {
    name: form.value.name.trim(),
    description: form.value.description.trim() || null
  };

  saving.value = true;
  try {
    if (editingCategory.value) {
      await categoriesApi.update(editingCategory.value.id, payload);
    } else {
      await categoriesApi.create(payload);
    }
    showModal.value = false;
    fetchCategories();
  } catch (err) {
    formError.value = err.response?.data?.error || 'Failed to save category.';
  } finally {
    saving.value = false;
  }
}

async function handleDelete(cat) {
  if (!confirm(`Delete category "${cat.name}"?`)) return;
  
  try {
    await categoriesApi.remove(cat.id);
    fetchCategories();
  } catch (err) {
    // The backend will return a 400 error if the category has products.
    // We just display that exact message to the user.
    alert(err.response?.data?.error || 'Failed to delete category.');
  }
}

onMounted(fetchCategories);
</script>

<template>
  <div class="p-6">
    <div class="mb-6 flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Categories</h1>
        <p class="mt-1 text-sm text-gray-600">Organize your products into logical groups.</p>
      </div>
      <button v-if="authStore.isAdmin" @click="openCreate"
              class="inline-flex items-center px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-md hover:bg-indigo-700">
        <PlusIcon class="h-5 w-5 mr-2" />
        New Category
      </button>
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
            <th class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Description</th>
            <th class="py-3.5 pl-3 pr-4 text-right text-sm font-semibold text-gray-900 sm:pr-6">Created</th>
            <th v-if="authStore.isAdmin" class="px-3 py-3.5 text-right text-sm font-semibold text-gray-900">Actions</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-200 bg-white">
          <tr v-if="loading">
            <td :colspan="authStore.isAdmin ? 4 : 3" class="py-8 text-center text-sm text-gray-500">Loading categories...</td>
          </tr>
          <tr v-else-if="categories.length === 0">
            <td :colspan="authStore.isAdmin ? 4 : 3" class="py-8 text-center text-sm text-gray-500">No categories found.</td>
          </tr>
          <tr v-for="cat in categories" :key="cat.id">
            <td class="whitespace-nowrap py-4 pl-4 pr-3 text-sm font-medium text-gray-900 sm:pl-6">{{ cat.name }}</td>
            <td class="px-3 py-4 text-sm text-gray-500">{{ cat.description || '—' }}</td>
            <td class="whitespace-nowrap py-4 pl-3 pr-4 text-right text-sm text-gray-500 sm:pr-6">
              {{ new Date(cat.created_at).toLocaleDateString() }}
            </td>
            <td v-if="authStore.isAdmin" class="whitespace-nowrap px-3 py-4 text-right text-sm">
              <button @click="openEdit(cat)" class="text-indigo-600 hover:text-indigo-800 mr-3" title="Edit">
                <PencilSquareIcon class="h-5 w-5 inline" />
              </button>
              <button @click="handleDelete(cat)" class="text-red-600 hover:text-red-800" title="Delete">
                <TrashIcon class="h-5 w-5 inline" />
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modal -->
    <div v-if="showModal" class="fixed inset-0 z-50 overflow-y-auto">
      <div class="fixed inset-0 bg-black bg-opacity-50" @click="closeModal"></div>
      <div class="relative flex min-h-full items-center justify-center p-4">
        <div class="relative w-full max-w-md rounded-lg bg-white shadow-xl">
          <div class="flex items-center justify-between border-b border-gray-200 px-6 py-4">
            <h3 class="text-lg font-semibold text-gray-900">
              {{ editingCategory ? 'Edit Category' : 'New Category' }}
            </h3>
            <button @click="closeModal" class="text-gray-400 hover:text-gray-600 text-2xl leading-none">&times;</button>
          </div>

          <form @submit.prevent="handleSubmit" class="px-6 py-4 space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Name *</label>
              <input v-model="form.name" type="text" required
                     class="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Description</label>
              <textarea v-model="form.description" rows="3"
                        class="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"></textarea>
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
                {{ saving ? 'Saving...' : (editingCategory ? 'Update' : 'Create') }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>