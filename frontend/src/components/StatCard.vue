<script setup>
defineProps({
  title: { type: String, required: true },
  value: { type: [String, Number], required: true },
  icon: { type: Object, required: true },
  colorClass: { type: String, default: 'text-indigo-600 bg-indigo-100' }
});
</script>

<template>
  <div class="bg-white overflow-hidden shadow rounded-lg border border-gray-200">
    <div class="p-5">
      <div class="flex items-center">
        <div :class="['flex-shrink-0 rounded-md p-3', colorClass]">
          <component :is="icon" class="h-6 w-6" aria-hidden="true" />
        </div>
        <div class="ml-5 w-0 flex-1">
          <dl>
            <dt class="text-sm font-medium text-gray-500 truncate">{{ title }}</dt>
            <dd class="text-3xl font-semibold text-gray-900">{{ value }}</dd>
          </dl>
        </div>
      </div>
    </div>
  </div>
</template>