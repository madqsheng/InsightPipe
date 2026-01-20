<script setup>
import { ref, onMounted, watch } from 'vue'
import MarkdownIt from 'markdown-it'
import { api } from '../services/api'

const props = defineProps({
  filename: String
})

const emit = defineEmits(['close'])

const content = ref('')
const loading = ref(false)
const error = ref('')

const md = new MarkdownIt({
  html: true,
  linkify: true,
  typographer: true
})

const loadDoc = async () => {
  if (!props.filename) return
  
  loading.value = true
  error.value = ''
  content.value = ''
  
  try {
    const res = await api.getDocument(props.filename)
    content.value = md.render(res.content)
  } catch (err) {
    error.value = 'Failed to load document: ' + err.message
  } finally {
    loading.value = false
  }
}

onMounted(loadDoc)
watch(() => props.filename, loadDoc)
</script>

<template>
  <div class="bg-gray-800 rounded-xl shadow-2xl border border-gray-700 flex flex-col h-full overflow-hidden">
    <!-- Header -->
    <div class="px-6 py-4 border-b border-gray-700 bg-gray-900/50 flex justify-between items-center">
      <h2 class="text-xl font-bold bg-gradient-to-r from-green-400 to-teal-300 bg-clip-text text-transparent truncate flex-1">
        {{ filename?.replace('.md', '') }}
      </h2>
      <button 
        @click="$emit('close')"
        class="text-gray-400 hover:text-white bg-gray-700 hover:bg-gray-600 px-3 py-1 rounded text-sm transition ml-4"
      >
        Esc / Close
      </button>
    </div>

    <!-- Content -->
    <div class="flex-1 overflow-y-auto p-8 custom-scrollbar bg-gray-900">
      <div v-if="loading" class="flex justify-center items-center h-full text-gray-400">
        <span class="animate-pulse">Loading content...</span>
      </div>
      
      <div v-else-if="error" class="text-red-400 text-center mt-10">
        {{ error }}
      </div>

      <div v-else class="prose prose-invert prose-blue max-w-none">
        <div v-html="content"></div>
      </div>
    </div>
  </div>
</template>

<style>
/* Custom Scrollbar */
.custom-scrollbar::-webkit-scrollbar {
  width: 8px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: #111827; 
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #374151; 
  border-radius: 4px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: #4b5563; 
}
</style>
