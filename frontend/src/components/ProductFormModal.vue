<script setup>
import { ref, watch } from 'vue';
import productsApi from '../api/products';

const props = defineProps({
  show: { type: Boolean, default: false },
  product: { type: Object, default: null },
  categories: { type: Array, default: () => [] }
});

const emit = defineEmits(['close', 'saved']);

const form = ref({
  name: '',
  sku: '',
  description: '',
  category_id: '',
  low_stock_threshold: 10
});
const error = ref('');
const saving = ref(false);

watch(() => props.show, (visible) => {
  if (visible) {
    error.value = '';
    if (props.product) {
      form.value = {
        name: props.product.name,
        sku: props.product.sku,
        description: props.product.description || '',
        category_id: props.product.category_id ?? '',
        low_stock_threshold: props.product.low_stock_threshold
      };
    } else {
      form.value = {
        name: '',
        sku: '',
        description: '',
        category_id: '',
        low_stock_threshold: 10
      };
    }
  }
});

async function handleSubmit() {
  error.value = '';

  if (!form.value.name.trim() || !form.value.sku.trim()) {
    error.value = 'Name and SKU are required.';
    return;
  }

  const threshold = parseInt(form.value.low_stock_threshold, 10);
  if (isNaN(threshold) || threshold < 0) {
    error.value = 'Low stock threshold must be a non-negative number.';
    return;
  }

  const payload = {
    name: form.value.name.trim(),
    sku: form.value.sku.trim(),
    description: form.value.description.trim() || null,
    category_id: form.value.category_id === '' ? null : parseInt(form.value.category_id, 10),
    low_stock_threshold: threshold
  };

  saving.value = true;
  try {
    if (props.product) {
      await productsApi.update(props.product.id, payload);
    } else {
      await productsApi.create(payload);
    }
    emit('saved');
  } catch (err) {
    error.value = err.response?.data?.error || 'Failed to save product.';
  } finally {
    saving.value = false;
  }
}
</script>

<template>
  <div v-if="show" class="fixed inset-0 z-50 overflow-y-auto">
    <div class="fixed inset-0 bg-black bg-opacity-50" @click="$emit('close')"></div>
    <div class="relative flex min-h-full items-center justify-center p-4">
      <div class="relative w-full max-w-lg rounded-lg bg-white shadow-xl">
        <div class="flex items-center justify-between border-b border-gray-200 px-6 py-4">
          <h3 class="text-lg font-semibold text-gray-900">
            {{ product ? 'Edit Product' : 'New Product' }}
          </h3>
          <button @click="$emit('close')" class="text-gray-400 hover:text-gray-600 text-2xl leading-none">&times;</button>
        </div>

        <form @submit.prevent="handleSubmit" class="px-6 py-4 space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Name *</label>
            <input v-model="form.name" type="text" required
                   class="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500" />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">SKU *</label>
            <input v-model="form.sku" type="text" required
                   class="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500" />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Description</label>
            <textarea v-model="form.description" rows="3"
                      class="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"></textarea>
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Category</label>
              <select v-model="form.category_id"
                      class="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500">
                <option value="">No category</option>
                <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Low Stock Threshold</label>
              <input v-model="form.low_stock_threshold" type="number" min="0"
                     class="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500" />
            </div>
          </div>

          <div v-if="error" class="bg-red-50 border border-red-200 text-red-600 text-sm p-3 rounded-md">
            {{ error }}
          </div>

          <div class="flex justify-end gap-3 pt-2">
            <button type="button" @click="$emit('close')"
                    class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50">
              Cancel
            </button>
            <button type="submit" :disabled="saving"
                    class="px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-md hover:bg-indigo-700 disabled:opacity-50">
              {{ saving ? 'Saving...' : (product ? 'Update Product' : 'Create Product') }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>