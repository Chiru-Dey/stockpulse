<script setup>
defineProps({
  movements: { type: Array, required: true }
});

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleString();
};
</script>

<template>
  <div class="mt-8 flow-root">
    <div class="-mx-4 -my-2 overflow-x-auto sm:-mx-6 lg:-mx-8">
      <div class="inline-block min-w-full py-2 align-middle sm:px-6 lg:px-8">
        <div class="overflow-hidden shadow ring-1 ring-black ring-opacity-5 sm:rounded-lg">
          <table class="min-w-full divide-y divide-gray-300">
            <thead class="bg-gray-50">
              <tr>
                <th scope="col" class="py-3.5 pl-4 pr-3 text-left text-sm font-semibold text-gray-900 sm:pl-6">Date</th>
                <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Product</th>
                <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Type</th>
                <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Quantity</th>
                <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Note</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-200 bg-white">
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
                <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                  {{ movement.quantity }}
                </td>
                <td class="px-3 py-4 text-sm text-gray-500 truncate max-w-xs">
                  {{ movement.note || '-' }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>