<script setup>
import { ref } from 'vue'
import { api } from '../services/api'

const title = ref('')
const content = ref('')
const saving = ref(false)
const saved = ref(false)
const emit = defineEmits(['saved'])

const handleSave = async () => {
  if (!title.value.trim() || !content.value.trim()) return
  
  saving.value = true
  saved.value = false
  
  try {
    // If content starts with "EOF", remove it? No, user won't type EOF here.
    await api.saveDocument(title.value, content.value)
    saved.value = true
    emit('saved')
    
    // Reset after success
    // title.value = ''
    // content.value = ''
    
    // Emit event to refresh list? (TODO)
  } catch (err) {
    console.error(err)
    alert('Error saving document: ' + err.message)
  } finally {
    saving.value = false
    setTimeout(() => saved.value = false, 3000)
  }
}
</script>

<template>
  <div class="bg-gray-800 p-6 rounded-xl shadow-lg border border-gray-700 h-full flex flex-col">
    <h2 class="text-2xl font-bold mb-4 bg-gradient-to-r from-purple-400 to-pink-300 bg-clip-text text-transparent">
      2. Capture Knowledge
    </h2>
    
    <div class="space-y-4 flex-1 flex flex-col">
      <div>
        <label class="block text-sm text-gray-400 mb-1">Topic Title</label>
        <input 
          v-model="title"
          type="text"
          class="w-full bg-gray-900 border border-gray-700 rounded-lg p-3 text-white focus:ring-2 focus:ring-purple-500 outline-none transition"
          placeholder="e.g. First Principles Thinking"
        />
      </div>

      <div class="flex-1 flex flex-col">
        <label class="block text-sm text-gray-400 mb-1">Paste Markdown Answer</label>
        <textarea 
          v-model="content"
          class="w-full flex-1 bg-gray-900 border border-gray-700 rounded-lg p-3 text-sm font-mono text-gray-300 focus:ring-2 focus:ring-purple-500 outline-none resize-none transition"
          placeholder="# Paste the expert answer here..."
        ></textarea>
      </div>

      <button 
        @click="handleSave"
        :disabled="saving || !title || !content"
        class="w-full bg-purple-600 hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed text-white font-medium py-3 px-4 rounded-lg transition-colors flex justify-center items-center gap-2"
      >
        <span v-if="saving" class="animate-spin">⏳</span>
        {{ saving ? 'Archiving...' : (saved ? '✅ Saved Successfully!' : 'Save to Library') }}
      </button>
    </div>
  </div>
</template>
