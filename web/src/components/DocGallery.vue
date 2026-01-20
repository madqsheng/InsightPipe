<script setup>
import { ref, onMounted } from 'vue'
import { api } from '../services/api'

const docs = ref([])
const loading = ref(true)

const fetchDocs = async () => {
  loading.value = true
  try {
    docs.value = await api.listDocuments()
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
}

onMounted(fetchDocs)

defineExpose({ refresh: fetchDocs })
</script>

<template>
  <div class="mt-8">
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-xl font-bold text-gray-200">📚 Knowledge Library</h3>
      <button @click="fetchDocs" class="text-sm text-gray-400 hover:text-white transition">🔄 Refresh</button>
    </div>

    <div v-if="loading" class="text-gray-500 text-center py-4">Loading library...</div>
    
    <div v-else-if="docs.length === 0" class="text-gray-500 text-center py-8 border border-dashed border-gray-700 rounded-lg">
      Library is empty. Start asking!
    </div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div 
        v-for="doc in docs" 
        :key="doc.filename"
        class="bg-gray-800 border border-gray-700 hover:border-gray-500 p-4 rounded-lg cursor-pointer transition group"
      >
        <h4 class="font-bold text-blue-300 truncate mb-1 group-hover:text-blue-200">{{ doc.title }}</h4>
        <div class="flex justify-between text-xs text-gray-500">
          <span>{{ doc.created_at }}</span>
          <span>{{ (doc.size / 1024).toFixed(1) }} KB</span>
        </div>
      </div>
    </div>
  </div>
</template>
